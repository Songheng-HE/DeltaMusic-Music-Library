#!/usr/bin/env python3
"""Compile a fully reviewed, measure-complete score IR to monophonic MIDI.

This module is deliberately not an OCR engine.  A person must review every
event against the supplied source before the IR can pass validation.  The
compiler then performs only deterministic validation and MIDI serialization.

Version 1 has one global tempo and meter.  It does not represent pickup bars or
meter/tempo changes.  Repeats and other navigation must already be resolved to
a finite sequence of measure references in ``performance_route``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path
from typing import Any

try:
    import mido
except ModuleNotFoundError as exc:  # pragma: no cover - depends on local setup
    raise SystemExit(
        "This tool needs mido. Install it with: py -m pip install mido"
    ) from exc


IR_FORMAT = "delta-reviewed-score/v1"
REPORT_FORMAT = "delta-reviewed-score-compile/v1"
REQUIRED_REVIEW_STATE = "visually_checked"
MAX_ROUTE_STEPS = 10_000


@dataclass(frozen=True)
class ScoreEvent:
    event_type: str
    offset: Fraction
    duration: Fraction
    pitch: int | None
    velocity: int
    tie_in: bool
    tie_out: bool
    slur_start: bool
    slur_end: bool
    locator: str


@dataclass(frozen=True)
class Measure:
    part_id: str
    measure_id: str
    source_ref: str
    events: tuple[ScoreEvent, ...]


@dataclass(frozen=True)
class TimelineEvent:
    event_type: str
    start: Fraction
    end: Fraction
    pitch: int | None
    velocity: int
    tie_in: bool
    tie_out: bool
    slur_start: bool
    slur_end: bool
    locator: str


@dataclass(frozen=True)
class MidiNote:
    start_tick: int
    end_tick: int
    pitch: int
    velocity: int


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _object(
    value: Any,
    location: str,
    *,
    required: set[str],
    allowed: set[str],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{location} must be an object.")
    missing = sorted(required - value.keys())
    if missing:
        raise ValueError(f"{location} is missing required field(s): {', '.join(missing)}.")
    unknown = sorted(value.keys() - allowed)
    if unknown:
        raise ValueError(f"{location} has unknown field(s): {', '.join(unknown)}.")
    return value


def _nonempty_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} must be a non-empty string.")
    return value.strip()


def _optional_string(value: Any, location: str) -> str | None:
    if value is None:
        return None
    return _nonempty_string(value, location)


def _integer(value: Any, location: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{location} must be an integer.")
    if not minimum <= value <= maximum:
        raise ValueError(f"{location} must be between {minimum} and {maximum}.")
    return value


def _boolean(value: Any, location: str, default: bool = False) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ValueError(f"{location} must be true or false.")
    return value


def _fraction(value: Any, location: str, *, allow_zero: bool) -> Fraction:
    if not isinstance(value, str):
        raise ValueError(
            f"{location} must be a rational string such as '0', '1', or '1/2'."
        )
    text = value.strip()
    if not text or text.startswith(("+", "-")):
        raise ValueError(f"{location} is not a non-negative rational beat value.")
    pieces = text.split("/")
    if len(pieces) > 2 or any(not piece.isdigit() for piece in pieces):
        raise ValueError(f"{location} is not a rational beat value.")
    if any(len(piece) > 1 and piece.startswith("0") for piece in pieces):
        raise ValueError(f"{location} must not contain leading zeroes.")
    if len(pieces) == 2 and pieces[0] == "0":
        raise ValueError(f"{location} must use '0', not a zero-valued fraction.")
    if len(pieces) == 2 and int(pieces[1]) == 0:
        raise ValueError(f"{location} has a zero denominator.")
    result = Fraction(int(pieces[0]), int(pieces[1]) if len(pieces) == 2 else 1)
    if result < 0 or (result == 0 and not allow_zero):
        qualifier = "non-negative" if allow_zero else "positive"
        raise ValueError(f"{location} must be {qualifier}.")
    return result


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _ticks(value: Fraction, ticks_per_beat: int, location: str) -> int:
    ticks = value * ticks_per_beat
    if ticks.denominator != 1:
        raise ValueError(
            f"{location}={_fraction_text(value)} cannot be represented exactly at "
            f"{ticks_per_beat} ticks per quarter beat. Choose a compatible ticks_per_beat."
        )
    return ticks.numerator


def _bpm(value: Any) -> tuple[int | float, int]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("bpm must be an explicit JSON number.")
    try:
        decimal_bpm = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("bpm is not a valid number.") from exc
    if not decimal_bpm.is_finite() or decimal_bpm <= 0 or decimal_bpm > 1000:
        raise ValueError("bpm must be finite, greater than 0, and no more than 1000.")
    tempo = int(
        (Decimal(60_000_000) / decimal_bpm).to_integral_value(
            rounding=ROUND_HALF_UP
        )
    )
    return value, tempo


def _resolve_source(ir_path: Path, source_value: dict[str, Any]) -> tuple[Path, str, str]:
    source = _object(
        source_value,
        "source",
        required={"path", "sha256"},
        allowed={"path", "sha256", "document_type"},
    )
    raw_path = _nonempty_string(source["path"], "source.path")
    expected = _nonempty_string(source["sha256"], "source.sha256").lower()
    if len(expected) != 64 or any(character not in "0123456789abcdef" for character in expected):
        raise ValueError("source.sha256 must be exactly 64 hexadecimal characters.")
    document_type = source.get("document_type", "other")
    if document_type not in {"pdf", "image", "musicxml", "midi", "other"}:
        raise ValueError("source.document_type is not supported.")
    source_path = Path(raw_path)
    if not source_path.is_absolute():
        source_path = ir_path.parent / source_path
    source_path = source_path.resolve()
    if not source_path.is_file():
        raise ValueError(f"Source file does not exist: {source_path}")
    verified = file_sha256(source_path)
    if verified != expected:
        raise ValueError(
            "Source SHA-256 mismatch: the reviewed IR does not describe the current source file."
        )
    return source_path, expected, document_type


def _validate_event(
    raw: Any,
    location: str,
    *,
    ticks_per_beat: int,
) -> ScoreEvent:
    common = {
        "type",
        "offset_beats",
        "duration_beats",
        "review_state",
        "source_ref",
        "review_note",
    }
    note_only = {
        "pitch",
        "velocity",
        "tie_in",
        "tie_out",
        "slur_start",
        "slur_end",
    }
    event = _object(
        raw,
        location,
        required={"type", "offset_beats", "duration_beats", "review_state"},
        allowed=common | note_only,
    )
    event_type = event["type"]
    if event_type not in {"note", "rest"}:
        raise ValueError(f"{location}.type must be 'note' or 'rest'.")
    if event["review_state"] != REQUIRED_REVIEW_STATE:
        raise ValueError(
            f"{location}.review_state must be '{REQUIRED_REVIEW_STATE}' before compilation."
        )
    _optional_string(event.get("source_ref"), f"{location}.source_ref")
    _optional_string(event.get("review_note"), f"{location}.review_note")
    offset = _fraction(event["offset_beats"], f"{location}.offset_beats", allow_zero=True)
    duration = _fraction(
        event["duration_beats"], f"{location}.duration_beats", allow_zero=False
    )
    _ticks(offset, ticks_per_beat, f"{location}.offset_beats")
    _ticks(duration, ticks_per_beat, f"{location}.duration_beats")

    if event_type == "rest":
        forbidden = sorted(note_only & event.keys())
        if forbidden:
            raise ValueError(
                f"{location} is a rest and cannot contain: {', '.join(forbidden)}."
            )
        return ScoreEvent(
            event_type="rest",
            offset=offset,
            duration=duration,
            pitch=None,
            velocity=0,
            tie_in=False,
            tie_out=False,
            slur_start=False,
            slur_end=False,
            locator=location,
        )

    if "pitch" not in event:
        raise ValueError(f"{location}.pitch is required for a note.")
    pitch = _integer(event["pitch"], f"{location}.pitch", 0, 127)
    velocity = _integer(event.get("velocity", 80), f"{location}.velocity", 1, 127)
    return ScoreEvent(
        event_type="note",
        offset=offset,
        duration=duration,
        pitch=pitch,
        velocity=velocity,
        tie_in=_boolean(event.get("tie_in"), f"{location}.tie_in"),
        tie_out=_boolean(event.get("tie_out"), f"{location}.tie_out"),
        slur_start=_boolean(event.get("slur_start"), f"{location}.slur_start"),
        slur_end=_boolean(event.get("slur_end"), f"{location}.slur_end"),
        locator=location,
    )


def _validate_score(ir_path: Path, raw: Any) -> dict[str, Any]:
    score = _object(
        raw,
        "score",
        required={
            "format",
            "title",
            "source",
            "bpm",
            "bpm_origin",
            "printed_tempo_text",
            "printed_numeric_bpm",
            "time_signature",
            "parts",
            "performance_route",
        },
        allowed={
            "$schema",
            "format",
            "title",
            "composer",
            "source",
            "bpm",
            "bpm_origin",
            "printed_tempo_text",
            "printed_numeric_bpm",
            "time_signature",
            "ticks_per_beat",
            "parts",
            "performance_route",
        },
    )
    if score["format"] != IR_FORMAT:
        raise ValueError(f"score.format must be '{IR_FORMAT}'.")
    title = _nonempty_string(score["title"], "score.title")
    composer = _optional_string(score.get("composer"), "score.composer")
    bpm, tempo = _bpm(score["bpm"])
    bpm_origin = score["bpm_origin"]
    if bpm_origin not in {"printed_score", "editorial_setting"}:
        raise ValueError(
            "score.bpm_origin must be 'printed_score' or 'editorial_setting'."
        )
    printed_tempo_text = _optional_string(
        score["printed_tempo_text"], "score.printed_tempo_text"
    )
    printed_numeric_value = score["printed_numeric_bpm"]
    if printed_numeric_value is None:
        printed_numeric_bpm = None
    else:
        printed_numeric_bpm, _ = _bpm(printed_numeric_value)
    if bpm_origin == "printed_score":
        if printed_numeric_bpm is None:
            raise ValueError(
                "score.printed_numeric_bpm is required when bpm_origin is printed_score."
            )
        if Decimal(str(printed_numeric_bpm)) != Decimal(str(bpm)):
            raise ValueError(
                "score.bpm must equal printed_numeric_bpm when bpm_origin is printed_score."
            )
    ticks_per_beat = _integer(
        score.get("ticks_per_beat", 480), "score.ticks_per_beat", 24, 9600
    )

    meter = _object(
        score["time_signature"],
        "score.time_signature",
        required={"numerator", "denominator"},
        allowed={"numerator", "denominator"},
    )
    numerator = _integer(meter["numerator"], "time_signature.numerator", 1, 32)
    denominator = _integer(meter["denominator"], "time_signature.denominator", 1, 64)
    if denominator & (denominator - 1):
        raise ValueError("time_signature.denominator must be a power of two.")
    measure_length = Fraction(numerator * 4, denominator)
    _ticks(measure_length, ticks_per_beat, "time signature measure length")

    parts = score["parts"]
    if not isinstance(parts, list) or not parts:
        raise ValueError("score.parts must be a non-empty array.")
    measures: dict[tuple[str, str], Measure] = {}
    part_ids: set[str] = set()
    for part_index, raw_part in enumerate(parts):
        part_location = f"parts[{part_index}]"
        part = _object(
            raw_part,
            part_location,
            required={"id", "measures"},
            allowed={"id", "label", "measures"},
        )
        part_id = _nonempty_string(part["id"], f"{part_location}.id")
        if part_id in part_ids:
            raise ValueError(f"Duplicate part id: {part_id}.")
        part_ids.add(part_id)
        _optional_string(part.get("label"), f"{part_location}.label")
        raw_measures = part["measures"]
        if not isinstance(raw_measures, list) or not raw_measures:
            raise ValueError(f"{part_location}.measures must be a non-empty array.")
        for measure_index, raw_measure in enumerate(raw_measures):
            measure_location = f"{part_location}.measures[{measure_index}]"
            measure = _object(
                raw_measure,
                measure_location,
                required={"id", "source_ref", "events"},
                allowed={"id", "label", "source_ref", "events"},
            )
            measure_id = _nonempty_string(measure["id"], f"{measure_location}.id")
            _optional_string(measure.get("label"), f"{measure_location}.label")
            source_ref = _nonempty_string(
                measure["source_ref"], f"{measure_location}.source_ref"
            )
            key = (part_id, measure_id)
            if key in measures:
                raise ValueError(f"Duplicate measure reference: {part_id}/{measure_id}.")
            raw_events = measure["events"]
            if not isinstance(raw_events, list) or not raw_events:
                raise ValueError(f"{measure_location}.events must be a non-empty array.")
            events = tuple(
                _validate_event(
                    raw_event,
                    f"{measure_location}.events[{event_index}]",
                    ticks_per_beat=ticks_per_beat,
                )
                for event_index, raw_event in enumerate(raw_events)
            )
            cursor = Fraction(0)
            for event in events:
                if event.offset != cursor:
                    relation = "gap" if event.offset > cursor else "overlap or out-of-order event"
                    raise ValueError(
                        f"{event.locator} creates a {relation}: expected offset "
                        f"{_fraction_text(cursor)}, got {_fraction_text(event.offset)}. "
                        "Every silent span must be an explicit rest."
                    )
                cursor += event.duration
            if cursor != measure_length:
                raise ValueError(
                    f"{part_id}/{measure_id} covers {_fraction_text(cursor)} quarter beats; "
                    f"the {numerator}/{denominator} measure requires "
                    f"{_fraction_text(measure_length)}."
                )
            measures[key] = Measure(part_id, measure_id, source_ref, events)

    raw_route = score["performance_route"]
    if not isinstance(raw_route, list) or not raw_route:
        raise ValueError("performance_route must be an explicit, non-empty finite array.")
    if len(raw_route) > MAX_ROUTE_STEPS:
        raise ValueError(f"performance_route cannot exceed {MAX_ROUTE_STEPS} steps.")
    route: list[dict[str, str]] = []
    for route_index, raw_step in enumerate(raw_route):
        location = f"performance_route[{route_index}]"
        step = _object(
            raw_step,
            location,
            required={"part_id", "measure_id"},
            allowed={"part_id", "measure_id"},
        )
        part_id = _nonempty_string(step["part_id"], f"{location}.part_id")
        measure_id = _nonempty_string(step["measure_id"], f"{location}.measure_id")
        if (part_id, measure_id) not in measures:
            raise ValueError(
                f"{location} references unknown measure {part_id}/{measure_id}."
            )
        route.append({"part_id": part_id, "measure_id": measure_id})

    source_path, expected_sha, document_type = _resolve_source(ir_path, score["source"])
    return {
        "title": title,
        "composer": composer,
        "source_path": source_path,
        "source_expected_sha256": expected_sha,
        "source_document_type": document_type,
        "bpm": bpm,
        "bpm_origin": bpm_origin,
        "printed_tempo_text": printed_tempo_text,
        "printed_numeric_bpm": printed_numeric_bpm,
        "tempo": tempo,
        "ticks_per_beat": ticks_per_beat,
        "numerator": numerator,
        "denominator": denominator,
        "measure_length": measure_length,
        "measures": measures,
        "route": route,
    }


def _timeline(score: dict[str, Any]) -> tuple[list[TimelineEvent], Fraction]:
    timeline: list[TimelineEvent] = []
    route_cursor = Fraction(0)
    for step_index, step in enumerate(score["route"]):
        measure = score["measures"][(step["part_id"], step["measure_id"])]
        for event in measure.events:
            timeline.append(
                TimelineEvent(
                    event_type=event.event_type,
                    start=route_cursor + event.offset,
                    end=route_cursor + event.offset + event.duration,
                    pitch=event.pitch,
                    velocity=event.velocity,
                    tie_in=event.tie_in,
                    tie_out=event.tie_out,
                    slur_start=event.slur_start,
                    slur_end=event.slur_end,
                    locator=(
                        f"route[{step_index}] {measure.part_id}/{measure.measure_id} "
                        f"[{measure.source_ref}] ({event.locator})"
                    ),
                )
            )
        route_cursor += score["measure_length"]
    return timeline, route_cursor


def _validate_ties(timeline: list[TimelineEvent]) -> None:
    for index, event in enumerate(timeline):
        if event.event_type != "note":
            continue
        if event.tie_in:
            previous = timeline[index - 1] if index else None
            if not (
                previous is not None
                and previous.event_type == "note"
                and previous.tie_out
                and previous.pitch == event.pitch
                and previous.end == event.start
            ):
                raise ValueError(
                    f"Invalid tie_in at {event.locator}: it must immediately continue a "
                    "same-pitch note with tie_out and no time gap."
                )
        if event.tie_out:
            following = timeline[index + 1] if index + 1 < len(timeline) else None
            if not (
                following is not None
                and following.event_type == "note"
                and following.tie_in
                and following.pitch == event.pitch
                and event.end == following.start
            ):
                raise ValueError(
                    f"Invalid tie_out at {event.locator}: it must immediately lead into a "
                    "same-pitch note with tie_in and no time gap."
                )


def _compile_notes(
    timeline: list[TimelineEvent], ticks_per_beat: int
) -> tuple[list[MidiNote], int, int, int]:
    _validate_ties(timeline)
    notes: list[MidiNote] = []
    source_note_events = 0
    rest_events = 0
    tie_merges = 0
    for event in timeline:
        if event.event_type == "rest":
            rest_events += 1
            continue
        source_note_events += 1
        start_tick = _ticks(event.start, ticks_per_beat, f"{event.locator} start")
        end_tick = _ticks(event.end, ticks_per_beat, f"{event.locator} end")
        assert event.pitch is not None
        if event.tie_in:
            notes[-1] = replace(notes[-1], end_tick=end_tick)
            tie_merges += 1
        else:
            notes.append(MidiNote(start_tick, end_tick, event.pitch, event.velocity))
    if not notes:
        raise ValueError("The routed score contains no notes; refusing to write a melody MIDI.")
    return notes, source_note_events, rest_events, tie_merges


def _build_midi(score: dict[str, Any], notes: list[MidiNote], total_ticks: int) -> Any:
    midi = mido.MidiFile(type=1, ticks_per_beat=score["ticks_per_beat"])
    conductor = mido.MidiTrack()
    midi.tracks.append(conductor)
    conductor.append(mido.MetaMessage("track_name", name="conductor", time=0))
    conductor.append(mido.MetaMessage("set_tempo", tempo=score["tempo"], time=0))
    conductor.append(
        mido.MetaMessage(
            "time_signature",
            numerator=score["numerator"],
            denominator=score["denominator"],
            time=0,
        )
    )
    conductor.append(mido.MetaMessage("end_of_track", time=total_ticks))

    melody = mido.MidiTrack()
    midi.tracks.append(melody)
    melody.append(mido.MetaMessage("track_name", name="melody_only", time=0))
    melody.append(mido.Message("program_change", channel=0, program=0, time=0))
    events: list[tuple[int, int, Any]] = []
    for note in notes:
        events.append(
            (
                note.end_tick,
                0,
                mido.Message(
                    "note_off", channel=0, note=note.pitch, velocity=0, time=0
                ),
            )
        )
        events.append(
            (
                note.start_tick,
                1,
                mido.Message(
                    "note_on",
                    channel=0,
                    note=note.pitch,
                    velocity=note.velocity,
                    time=0,
                ),
            )
        )
    previous_tick = 0
    for tick, _, message in sorted(events, key=lambda item: (item[0], item[1])):
        if tick < previous_tick:
            raise RuntimeError("Internal event ordering failure.")
        melody.append(message.copy(time=tick - previous_tick))
        previous_tick = tick
    melody.append(mido.MetaMessage("end_of_track", time=total_ticks - previous_tick))
    return midi


def _roundtrip_notes(path: Path) -> tuple[Any, list[MidiNote]]:
    midi = mido.MidiFile(str(path))
    melody_tracks = []
    for track in midi.tracks:
        name = next(
            (message.name for message in track if message.type == "track_name"), ""
        )
        if name == "melody_only":
            melody_tracks.append(track)
    if len(melody_tracks) != 1:
        raise RuntimeError("Round-trip validation did not find exactly one melody_only track.")
    active: dict[tuple[int, int], tuple[int, int]] = {}
    notes: list[MidiNote] = []
    tick = 0
    for message in melody_tracks[0]:
        tick += int(message.time)
        if message.type == "note_on" and message.velocity > 0:
            key = (message.channel, message.note)
            if key in active:
                raise RuntimeError("Round-trip MIDI contains overlapping same-pitch notes.")
            active[key] = (tick, message.velocity)
        elif message.type == "note_off" or (
            message.type == "note_on" and message.velocity == 0
        ):
            key = (message.channel, message.note)
            if key not in active:
                raise RuntimeError("Round-trip MIDI contains an unmatched note-off.")
            start, velocity = active.pop(key)
            notes.append(MidiNote(start, tick, message.note, velocity))
    if active:
        raise RuntimeError("Round-trip MIDI contains unterminated notes.")
    notes.sort(key=lambda item: (item.start_tick, item.end_tick, item.pitch))
    return midi, notes


def _ensure_safe_paths(
    ir_path: Path,
    source_path: Path,
    output_path: Path,
    report_path: Path,
    *,
    force: bool,
) -> tuple[Path, Path]:
    ir_resolved = ir_path.resolve()
    source_resolved = source_path.resolve()
    output_resolved = output_path.resolve()
    report_resolved = report_path.resolve()
    if output_resolved.suffix.lower() not in {".mid", ".midi"}:
        raise ValueError("The MIDI output path must end in .mid or .midi.")
    protected = {ir_resolved, source_resolved}
    if output_resolved in protected or report_resolved in protected:
        raise ValueError("Derived artifacts must not overwrite the score IR or source file.")
    if output_resolved == report_resolved:
        raise ValueError("MIDI output and JSON report paths must be different.")
    existing = [path for path in (output_resolved, report_resolved) if path.exists()]
    if existing and not force:
        raise FileExistsError(
            "Refusing to overwrite existing artifact(s): "
            + ", ".join(str(path) for path in existing)
            + ". Choose new paths or pass --force for reviewed derived artifacts."
        )
    return output_resolved, report_resolved


def _temporary_path(target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_path = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent)
    )
    os.close(descriptor)
    return Path(raw_path)


def compile_score(
    ir_path: Path,
    output_path: Path,
    report_path: Path,
    *,
    force: bool = False,
) -> dict[str, Any]:
    ir_path = ir_path.resolve()
    if not ir_path.is_file():
        raise ValueError(f"Reviewed score IR does not exist: {ir_path}")
    try:
        ir_bytes = ir_path.read_bytes()
        raw = json.loads(ir_bytes.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Reviewed score IR is not valid JSON: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ValueError("Reviewed score IR must be UTF-8 JSON.") from exc
    ir_sha256 = hashlib.sha256(ir_bytes).hexdigest()
    score = _validate_score(ir_path, raw)
    output_path, report_path = _ensure_safe_paths(
        ir_path,
        score["source_path"],
        output_path,
        report_path,
        force=force,
    )
    timeline, total_beats = _timeline(score)
    total_ticks = _ticks(total_beats, score["ticks_per_beat"], "routed score length")
    notes, source_note_events, rest_events, tie_merges = _compile_notes(
        timeline, score["ticks_per_beat"]
    )
    midi = _build_midi(score, notes, total_ticks)

    temporary_midi = _temporary_path(output_path)
    temporary_report = _temporary_path(report_path)
    try:
        midi.save(str(temporary_midi))
        roundtrip_midi, roundtrip_notes = _roundtrip_notes(temporary_midi)
        if roundtrip_midi.ticks_per_beat != score["ticks_per_beat"]:
            raise RuntimeError("Round-trip MIDI changed ticks_per_beat.")
        if roundtrip_notes != notes:
            raise RuntimeError("Round-trip MIDI note timing or pitch differs from compilation.")
        if file_sha256(ir_path) != ir_sha256:
            raise RuntimeError(
                "Reviewed score IR changed during compilation; no artifacts were committed."
            )
        if file_sha256(score["source_path"]) != score["source_expected_sha256"]:
            raise RuntimeError(
                "Source file changed during compilation; no artifacts were committed."
            )
        output_sha = file_sha256(temporary_midi)
        route_steps = [dict(step) for step in score["route"]]
        report = {
            "report_format": REPORT_FORMAT,
            "score_ir": {
                "path": str(ir_path),
                "sha256": ir_sha256,
            },
            "source": {
                "path": str(score["source_path"]),
                "document_type": score["source_document_type"],
                "expected_sha256": score["source_expected_sha256"],
                "verified_sha256": score["source_expected_sha256"],
                "hash_verified": True,
            },
            "output_file": str(output_path),
            "output_sha256": output_sha,
            "settings": {
                "ticks_per_beat": score["ticks_per_beat"],
                "bpm": score["bpm"],
                "playback_bpm": score["bpm"],
                "playback_bpm_origin": score["bpm_origin"],
                "printed_tempo_text": score["printed_tempo_text"],
                "printed_numeric_bpm": score["printed_numeric_bpm"],
                "microseconds_per_beat": score["tempo"],
                "time_signature": {
                    "numerator": score["numerator"],
                    "denominator": score["denominator"],
                },
            },
            "performance_route": {
                "step_count": len(route_steps),
                "steps": route_steps,
                "total_quarter_beats": _fraction_text(total_beats),
                "total_ticks": total_ticks,
            },
            "validation": {
                "all_events_visually_checked": True,
                "unique_measures_validated": len(score["measures"]),
                "routed_measure_instances": len(route_steps),
                "strictly_monophonic": True,
                "roundtrip_verified": True,
                "source_note_event_count": source_note_events,
                "note_count": len(notes),
                "rest_count": rest_events,
                "tie_groups_merged": tie_merges,
            },
            "pitch_range": {
                "lowest_pitch": min(note.pitch for note in notes),
                "highest_pitch": max(note.pitch for note in notes),
            },
        }
        temporary_report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(temporary_midi, output_path)
        os.replace(temporary_report, report_path)
        return report
    finally:
        for temporary in (temporary_midi, temporary_report):
            if temporary.exists():
                temporary.unlink()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compile an explicitly routed, measure-complete, visually reviewed score IR "
            "to strict monophonic MIDI. Version 1 requires one global tempo/meter, "
            "has no pickup bars, and requires repeats/navigation to be expanded in "
            "performance_route."
        )
    )
    parser.add_argument("input", type=Path, help="reviewed score IR JSON")
    parser.add_argument("output", type=Path, help="output melody-only .mid/.midi")
    parser.add_argument("--report", type=Path, required=True, help="compile JSON report")
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace existing reviewed derived output/report, never source inputs",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        report = compile_score(args.input, args.output, args.report, force=args.force)
    except (OSError, ValueError, RuntimeError, EOFError) as exc:
        parser.exit(1, f"error: {exc}\n")
    print(
        f"Wrote reviewed melody MIDI: {report['output_file']} "
        f"({report['validation']['note_count']} notes, "
        f"SHA-256 {report['output_sha256']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
