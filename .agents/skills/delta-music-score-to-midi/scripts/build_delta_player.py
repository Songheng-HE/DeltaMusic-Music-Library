#!/usr/bin/env python3
"""Generate a Delta three-octave player from a validated melody-only MIDI.

The generated player embeds a tempo-map-aware absolute schedule. It deliberately
refuses polyphony and does not fold individual out-of-range notes into another
octave.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

from midi_tools import (
    canonical_tempo_events,
    note_name,
    overlap_metrics,
    parse_track_notes,
    select_track,
    tick_to_seconds,
    track_name,
)

import mido


PLAYABLE_LOW = 48   # C3
PLAYABLE_HIGH = 83  # B5
EXTRACTION_REPORT_FORMAT = "delta-midi-extract/v2"
SAFE_REDUCTION_STRUCTURE_CLASSES = {
    "isolated-melody",
    "karaoke-guide",
    "independent-melodic-part",
}
TRIMMABLE_STRUCTURE_CLASSES = {"isolated-melody", "karaoke-guide"}


PLAYER_TEMPLATE = r'''#!/usr/bin/env python3
"""Generated Delta three-octave player.

Verify the bindings below in a harmless in-game test before full playback.
Run with --dry-run first. F10 stops playback and releases all held controls.
"""

from __future__ import annotations

import argparse
import time

keyboard = None
pydirectinput = None


SONG_TITLE = __SONG_TITLE__
GLOBAL_OCTAVE_SHIFT = __OCTAVE_SHIFT__
PLAYABLE_RANGE = ("C3", "B5")
EVENTS = __EVENTS__
SKIPPED_EVENTS = __SKIPPED_EVENTS__

# Confirm these values against the current game controls before use.
NATURAL_KEYS = {
    0: "z",   # C
    2: "x",   # D
    4: "c",   # E
    5: "v",   # F
    7: "b",   # G
    9: "n",   # A
    11: "m",  # B
}
ACCIDENTAL_BASE = {1: 0, 3: 2, 6: 5, 8: 7, 10: 9}
LOW_OCTAVE_MODIFIER = "left"
SHARP_MODIFIER = "middle"
HIGH_OCTAVE_MODIFIER = "right"
SPECIAL_HIGH_C_KEY = ","
MODIFIER_LEAD_SECONDS = 0.008
STOP_KEY = "f10"
POLL_SECONDS = 0.005


class StopRequested(Exception):
    pass


def load_runtime_dependencies() -> None:
    """Import input-sending packages only when real playback is requested."""

    global keyboard, pydirectinput
    try:
        import keyboard as keyboard_module
        import pydirectinput as pydirectinput_module
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Install runtime dependencies with: py -m pip install pydirectinput keyboard"
        ) from exc
    keyboard = keyboard_module
    pydirectinput = pydirectinput_module


def wait_until(deadline: float) -> None:
    while True:
        if keyboard.is_pressed(STOP_KEY):
            raise StopRequested
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            return
        time.sleep(min(POLL_SECONDS, remaining))


def controls_for_pitch(pitch: int) -> tuple[list[str], str]:
    if pitch == 72:  # C5 has its own key in the verified default layout.
        return [], SPECIAL_HIGH_C_KEY

    octave = pitch // 12 - 1
    pitch_class = pitch % 12
    modifiers: list[str] = []
    if octave == 3:
        modifiers.append(LOW_OCTAVE_MODIFIER)
    elif octave == 4:
        pass
    elif octave == 5:
        modifiers.append(HIGH_OCTAVE_MODIFIER)
    else:
        raise ValueError(f"MIDI pitch {pitch} is outside the configured game range.")

    if pitch_class in NATURAL_KEYS:
        key = NATURAL_KEYS[pitch_class]
    elif pitch_class in ACCIDENTAL_BASE:
        key = NATURAL_KEYS[ACCIDENTAL_BASE[pitch_class]]
        modifiers.append(SHARP_MODIFIER)
    else:
        raise ValueError(f"No Delta key mapping is configured for MIDI pitch {pitch}.")
    return modifiers, key


def release_all() -> None:
    for key in tuple(NATURAL_KEYS.values()) + (SPECIAL_HIGH_C_KEY,):
        pydirectinput.keyUp(key)
    for button in (LOW_OCTAVE_MODIFIER, SHARP_MODIFIER, HIGH_OCTAVE_MODIFIER):
        pydirectinput.mouseUp(button=button)


def play_events() -> None:
    pydirectinput.PAUSE = 0
    release_all()
    clock = time.perf_counter()
    try:
        for start, end, pitch in EVENTS:
            wait_until(clock + max(0.0, start - MODIFIER_LEAD_SECONDS))
            modifiers, key = controls_for_pitch(pitch)
            for button in modifiers:
                pydirectinput.mouseDown(button=button)
            wait_until(clock + start)
            pydirectinput.keyDown(key)
            wait_until(clock + end)
            pydirectinput.keyUp(key)
            for button in reversed(modifiers):
                pydirectinput.mouseUp(button=button)
    finally:
        release_all()


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Play {SONG_TITLE} in Delta.")
    parser.add_argument("--dry-run", action="store_true", help="inspect without sending input")
    parser.add_argument("--start-delay", type=float, default=10.0)
    args = parser.parse_args()

    print(f"{SONG_TITLE}: {len(EVENTS)} playable events, octave shift {GLOBAL_OCTAVE_SHIFT:+d}.")
    if SKIPPED_EVENTS:
        print(f"Warning: {len(SKIPPED_EVENTS)} events are skipped by explicit build choice.")
    if args.dry_run:
        for start, end, pitch in EVENTS[:12]:
            print(f"{start:8.3f}s to {end:8.3f}s  MIDI {pitch}")
        return 0

    load_runtime_dependencies()
    print(
        f"Focus Delta now. Playback starts in {args.start_delay:.1f}s; "
        f"press {STOP_KEY.upper()} to stop."
    )
    try:
        wait_until(time.perf_counter() + max(0.0, args.start_delay))
        play_events()
    except StopRequested:
        print("Stopped.")
    finally:
        release_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def choose_melody_track(midi: mido.MidiFile, requested: str | None) -> tuple[int, mido.MidiTrack]:
    """Use an explicit track, otherwise require an unambiguous melody-only track."""

    if requested:
        return select_track(midi, requested)

    named = [
        (index, track)
        for index, track in enumerate(midi.tracks)
        if track_name(track).casefold() == "melody_only"
    ]
    if len(named) == 1:
        return named[0]

    musical_tracks = []
    for index, track in enumerate(midi.tracks):
        notes, _ = parse_track_notes(track)
        if notes:
            musical_tracks.append((index, track))
    if len(musical_tracks) == 1:
        return musical_tracks[0]
    available = ", ".join(
        f"{index}:{track_name(track) or '(unnamed)'}"
        for index, track in enumerate(midi.tracks)
    )
    raise ValueError(
        "Cannot infer the melody track. Supply --track with an audit-report index "
        f"or exact name. Available tracks: {available}"
    )


def choose_global_octave_shift(notes: list[Any], requested: str) -> int:
    """Choose a whole-octave placement that maximizes exact playable notes."""

    if requested != "auto":
        try:
            shift = int(requested)
        except ValueError as exc:
            raise ValueError("--global-octave-shift must be auto or an integer.") from exc
        if shift % 12:
            raise ValueError("Global octave shift must be a multiple of 12 semitones.")
        return shift

    candidates = list(range(-48, 49, 12))

    def score(shift: int) -> tuple[int, int, int, int]:
        exact = sum(PLAYABLE_LOW <= note.pitch + shift <= PLAYABLE_HIGH for note in notes)
        distance = sum(
            PLAYABLE_LOW - (note.pitch + shift)
            if note.pitch + shift < PLAYABLE_LOW
            else (note.pitch + shift) - PLAYABLE_HIGH
            if note.pitch + shift > PLAYABLE_HIGH
            else 0
            for note in notes
        )
        return exact, -distance, -abs(shift), shift

    return max(candidates, key=score)


def make_schedule(
    notes: list[Any], midi: mido.MidiFile, octave_shift: int
) -> tuple[list[list[float | int]], list[dict[str, Any]]]:
    """Convert MIDI ticks to absolute seconds and identify every unsupported pitch."""

    tempos = canonical_tempo_events(midi)
    schedule: list[list[float | int]] = []
    unplayable: list[dict[str, Any]] = []
    for index, note in enumerate(notes):
        shifted = note.pitch + octave_shift
        event = [
            round(tick_to_seconds(note.start, tempos, midi.ticks_per_beat), 6),
            round(tick_to_seconds(note.end, tempos, midi.ticks_per_beat), 6),
            shifted,
        ]
        if PLAYABLE_LOW <= shifted <= PLAYABLE_HIGH:
            schedule.append(event)
        else:
            unplayable.append(
                {
                    "event_index": index,
                    "start_seconds": event[0],
                    "source_pitch": note.pitch,
                    "source_note": note_name(note.pitch),
                    "placed_pitch": shifted,
                    "placed_note": note_name(shifted),
                }
            )
    return schedule, unplayable


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json_report(path: Path, label: str) -> dict[str, Any]:
    """Load a report as data, rejecting malformed or missing audit evidence."""

    if not path.is_file():
        raise FileNotFoundError(f"{label} does not exist: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object: {path}")
    return value


def same_path(left: str | Path, right: Path) -> bool:
    """Compare report paths safely, including relative paths."""

    return Path(left).resolve() == right.resolve()


def is_sha256(value: Any) -> bool:
    """Return whether a report value is a normalized SHA-256 hex digest."""

    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def audit_evidence(path: Path, melody_path: Path, track_index: int) -> dict[str, Any]:
    """Require a post-conversion audit that describes this exact MIDI input."""

    report = load_json_report(path, "Audit report")
    source_file = report.get("source_file")
    if not isinstance(source_file, str) or not same_path(source_file, melody_path):
        raise ValueError(
            "Audit report source_file must point to the exact melody MIDI being built."
        )
    current_sha256 = hashlib.sha256(melody_path.read_bytes()).hexdigest()
    if report.get("source_sha256") != current_sha256:
        raise ValueError(
            "Audit report hash does not match the melody MIDI. Re-run audit after any change."
        )
    tracks = report.get("tracks")
    if not isinstance(tracks, list):
        raise ValueError("Audit report does not contain a track list.")
    track = next(
        (
            item
            for item in tracks
            if isinstance(item, dict) and item.get("track_index") == track_index
        ),
        None,
    )
    if not track or not track.get("strictly_monophonic"):
        raise ValueError(
            "Audit report does not verify the selected player track as strictly monophonic."
        )
    return {
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "source_midi_sha256": current_sha256,
        "selected_track_audit": track,
    }


def extraction_evidence(path: Path | None, melody_path: Path) -> dict[str, Any] | None:
    """Optionally preserve the preceding extraction decision in the manifest."""

    if path is None:
        return None
    report = load_json_report(path, "Extraction report")
    if report.get("report_format") != EXTRACTION_REPORT_FORMAT:
        raise ValueError(
            f"Extraction report_format must be {EXTRACTION_REPORT_FORMAT}."
        )
    output_file = report.get("output_file")
    if not isinstance(output_file, str) or not same_path(output_file, melody_path):
        raise ValueError(
            "Extraction report output_file must point to the exact melody MIDI being built."
        )
    current_sha256 = hashlib.sha256(melody_path.read_bytes()).hexdigest()
    reported_sha256 = report.get("output_sha256")
    if not is_sha256(reported_sha256) or reported_sha256 != current_sha256:
        raise ValueError(
            "Extraction report hash does not match the melody MIDI. Re-run extraction or audit."
        )
    source_file = report.get("source_file")
    source_sha256 = report.get("source_sha256")
    if not isinstance(source_file, str) or not source_file:
        raise ValueError("Extraction report source_file is required.")
    if not is_sha256(source_sha256):
        raise ValueError("Extraction report source_sha256 is required.")
    source_file_checked = False
    if Path(source_file).is_file():
        if hashlib.sha256(Path(source_file).read_bytes()).hexdigest() != source_sha256:
            raise ValueError(
                "Extraction report source hash does not match the current source MIDI."
            )
        source_file_checked = True

    settings = report.get("settings")
    if not isinstance(settings, dict):
        raise ValueError("Extraction report settings are required.")
    structure_class = report.get("structure_class")
    reduction_requested = settings.get("same_onset") in {"highest", "lowest"} or (
        settings.get("overlaps") == "truncate"
    )
    if reduction_requested and structure_class not in SAFE_REDUCTION_STRUCTURE_CLASSES:
        raise ValueError(
            "Extraction report contains a lossy pitch/overlap reduction without an "
            "eligible structure_class."
        )
    if settings.get("duration_mode") == "onset" and structure_class != "karaoke-guide":
        raise ValueError(
            "Extraction report uses onset duration reconstruction without karaoke-guide."
        )
    if settings.get("trim_leading_rest") is True and (
        structure_class not in TRIMMABLE_STRUCTURE_CLASSES
    ):
        raise ValueError(
            "Extraction report trims the time origin without an eligible structure_class."
        )
    return {
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "report_format": report["report_format"],
        "output_midi_sha256": current_sha256,
        "source_file": source_file,
        "source_sha256": source_sha256,
        "current_source_verified": source_file_checked,
        "source_track_index": report.get("source_track_index"),
        "source_track_name": report.get("source_track_name"),
        "structure_class": structure_class,
        "settings": settings,
    }


def conversion_evidence(path: Path | None, melody_path: Path) -> dict[str, Any] | None:
    """Optionally preserve a reviewed-score conversion without posing as extraction."""

    if path is None:
        return None
    report = load_json_report(path, "Conversion report")
    if report.get("report_format") != "delta-reviewed-score-compile/v1":
        raise ValueError(
            "Conversion report_format must be delta-reviewed-score-compile/v1."
        )
    output_file = report.get("output_file")
    if not isinstance(output_file, str) or not same_path(output_file, melody_path):
        raise ValueError(
            "Conversion report output_file must point to the exact melody MIDI being built."
        )
    current_sha256 = hashlib.sha256(melody_path.read_bytes()).hexdigest()
    if report.get("output_sha256") != current_sha256:
        raise ValueError(
            "Conversion report hash does not match the melody MIDI. Re-run score compilation."
        )

    score_ir = report.get("score_ir")
    source = report.get("source")
    performance_route = report.get("performance_route")
    validation = report.get("validation")
    if not isinstance(score_ir, dict):
        raise ValueError("Conversion report does not contain score_ir evidence.")
    if not isinstance(source, dict):
        raise ValueError("Conversion report does not contain source evidence.")
    if not isinstance(performance_route, dict):
        raise ValueError("Conversion report does not contain a performance_route.")
    if not isinstance(validation, dict):
        raise ValueError("Conversion report does not contain validation evidence.")

    score_ir_path = score_ir.get("path")
    score_ir_sha256 = score_ir.get("sha256")
    if not isinstance(score_ir_path, str) or not score_ir_path:
        raise ValueError("Conversion report score_ir.path must name the reviewed score IR.")
    if not is_sha256(score_ir_sha256):
        raise ValueError("Conversion report score_ir.sha256 is required.")
    resolved_score_ir = Path(score_ir_path)
    if not resolved_score_ir.is_file():
        raise ValueError(
            "Conversion report score_ir.path is unavailable; retain the reviewed score IR."
        )
    score_ir_bytes = resolved_score_ir.read_bytes()
    current_score_ir_sha256 = hashlib.sha256(score_ir_bytes).hexdigest()
    if score_ir_sha256 != current_score_ir_sha256:
        raise ValueError(
            "Conversion report score_ir hash does not match the current reviewed score IR."
        )
    try:
        score_data = json.loads(score_ir_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Conversion report score_ir.path is not valid UTF-8 JSON.") from exc
    if not isinstance(score_data, dict) or score_data.get("format") != "delta-reviewed-score/v1":
        raise ValueError("Conversion report score IR is not delta-reviewed-score/v1.")

    if source.get("hash_verified") is not True:
        raise ValueError("Conversion report source.hash_verified must be true.")
    expected_source_sha256 = source.get("expected_sha256")
    verified_source_sha256 = source.get("verified_sha256")
    if (
        not is_sha256(expected_source_sha256)
        or not is_sha256(verified_source_sha256)
        or expected_source_sha256 != verified_source_sha256
    ):
        raise ValueError(
            "Conversion report source expected_sha256 and verified_sha256 must match."
        )
    source_path = source.get("path")
    ir_source = score_data.get("source")
    if not isinstance(ir_source, dict):
        raise ValueError("Reviewed score IR does not contain source evidence.")
    ir_source_path = ir_source.get("path")
    ir_source_sha256 = ir_source.get("sha256")
    if not isinstance(ir_source_path, str) or not ir_source_path:
        raise ValueError("Reviewed score IR source.path is required.")
    resolved_ir_source = Path(ir_source_path)
    if not resolved_ir_source.is_absolute():
        resolved_ir_source = resolved_score_ir.parent / resolved_ir_source
    resolved_ir_source = resolved_ir_source.resolve()
    if not isinstance(source_path, str) or not same_path(source_path, resolved_ir_source):
        raise ValueError(
            "Conversion report source.path does not match the reviewed score IR."
        )
    if not is_sha256(str(ir_source_sha256).lower()) or (
        expected_source_sha256 != str(ir_source_sha256).lower()
    ):
        raise ValueError(
            "Conversion report source hash does not match the reviewed score IR."
        )
    if source.get("document_type") != ir_source.get("document_type", "other"):
        raise ValueError(
            "Conversion report source document_type does not match the reviewed score IR."
        )

    settings = report.get("settings")
    if not isinstance(settings, dict):
        raise ValueError("Conversion report does not contain settings evidence.")
    expected_ticks_per_beat = score_data.get("ticks_per_beat", 480)
    expected_bpm = score_data.get("bpm")
    expected_bpm_origin = score_data.get("bpm_origin")
    expected_tempo_text = score_data.get("printed_tempo_text")
    expected_printed_bpm = score_data.get("printed_numeric_bpm")
    expected_time_signature = score_data.get("time_signature")
    if (
        settings.get("ticks_per_beat") != expected_ticks_per_beat
        or settings.get("bpm") != expected_bpm
        or settings.get("playback_bpm") != expected_bpm
        or settings.get("playback_bpm_origin") != expected_bpm_origin
        or settings.get("printed_tempo_text") != expected_tempo_text
        or settings.get("printed_numeric_bpm") != expected_printed_bpm
        or settings.get("time_signature") != expected_time_signature
    ):
        raise ValueError(
            "Conversion report settings do not match the reviewed score IR."
        )

    ir_route = score_data.get("performance_route")
    if not isinstance(ir_route, list) or not ir_route:
        raise ValueError("Reviewed score IR performance_route is invalid.")
    if performance_route.get("steps") != ir_route or (
        performance_route.get("step_count") != len(ir_route)
    ):
        raise ValueError(
            "Conversion report performance_route does not match the reviewed score IR."
        )
    if not isinstance(expected_time_signature, dict):
        raise ValueError("Reviewed score IR time_signature is invalid.")
    numerator = expected_time_signature.get("numerator")
    denominator = expected_time_signature.get("denominator")
    if (
        isinstance(numerator, bool)
        or not isinstance(numerator, int)
        or isinstance(denominator, bool)
        or not isinstance(denominator, int)
        or denominator <= 0
        or isinstance(expected_ticks_per_beat, bool)
        or not isinstance(expected_ticks_per_beat, int)
    ):
        raise ValueError("Reviewed score IR meter/PPQ is invalid.")
    expected_total_beats = Fraction(numerator * 4, denominator) * len(ir_route)
    expected_total_ticks = expected_total_beats * expected_ticks_per_beat
    expected_total_beats_text = (
        str(expected_total_beats.numerator)
        if expected_total_beats.denominator == 1
        else f"{expected_total_beats.numerator}/{expected_total_beats.denominator}"
    )
    if (
        expected_total_ticks.denominator != 1
        or performance_route.get("total_quarter_beats") != expected_total_beats_text
        or performance_route.get("total_ticks") != expected_total_ticks.numerator
    ):
        raise ValueError(
            "Conversion report routed duration does not match the reviewed score IR."
        )

    parts = score_data.get("parts")
    if not isinstance(parts, list) or not parts:
        raise ValueError("Reviewed score IR parts are invalid.")
    measure_references: set[tuple[str, str]] = set()
    for part in parts:
        if not isinstance(part, dict) or not isinstance(part.get("id"), str):
            raise ValueError("Reviewed score IR part is invalid.")
        measures = part.get("measures")
        if not isinstance(measures, list) or not measures:
            raise ValueError("Reviewed score IR measures are invalid.")
        for measure in measures:
            if not isinstance(measure, dict):
                raise ValueError("Reviewed score IR measure is invalid.")
            measure_id = measure.get("id")
            measure_source_ref = measure.get("source_ref")
            if not isinstance(measure_id, str) or not measure_id or (
                not isinstance(measure_source_ref, str) or not measure_source_ref
            ):
                raise ValueError("Reviewed score IR measure id/source_ref is invalid.")
            measure_references.add((part["id"], measure_id))
            events = measure.get("events")
            if not isinstance(events, list) or not events or any(
                not isinstance(event, dict)
                or event.get("review_state") != "visually_checked"
                for event in events
            ):
                raise ValueError(
                    "Reviewed score IR contains an unreviewed or invalid event."
                )
    if any(
        not isinstance(step, dict)
        or (step.get("part_id"), step.get("measure_id")) not in measure_references
        for step in ir_route
    ):
        raise ValueError("Reviewed score IR route references an unknown measure.")

    source_file_checked = False
    if resolved_ir_source.is_file():
        current_source_sha256 = hashlib.sha256(resolved_ir_source.read_bytes()).hexdigest()
        if current_source_sha256 != verified_source_sha256:
            raise ValueError(
                "Conversion report source hash does not match the current source file."
            )
        source_file_checked = True

    if validation.get("all_events_visually_checked") is not True:
        raise ValueError(
            "Conversion report must confirm validation.all_events_visually_checked=true."
        )
    if validation.get("strictly_monophonic") is not True:
        raise ValueError(
            "Conversion report must confirm validation.strictly_monophonic=true."
        )
    if validation.get("roundtrip_verified") is not True:
        raise ValueError(
            "Conversion report must confirm validation.roundtrip_verified=true."
        )

    return {
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "report_format": report["report_format"],
        "output_midi_sha256": current_sha256,
        "score_ir": score_ir,
        "source": source,
        "current_files_verified": {
            "score_ir": True,
            "source": source_file_checked,
        },
        "settings": settings,
        "performance_route": performance_route,
        "validation": validation,
        "pitch_range": report.get("pitch_range"),
    }


def ensure_safe_outputs(
    input_path: Path,
    output_path: Path,
    manifest_path: Path,
    report_paths: list[tuple[str, Path | None]],
    force: bool,
) -> None:
    """Protect the supplied source and avoid implicit replacement of artifacts."""

    labelled_paths = [
        ("melody input", input_path),
        ("player output", output_path),
        ("manifest", manifest_path),
        *((label, path) for label, path in report_paths if path is not None),
    ]
    seen: dict[Path, str] = {}
    for label, path in labelled_paths:
        resolved = path.resolve()
        previous = seen.get(resolved)
        if previous is not None:
            raise ValueError(
                f"Path conflict: {label} and {previous} must be different files ({path})."
            )
        seen[resolved] = label
    existing = [path for path in (output_path, manifest_path) if path.exists()]
    if existing and not force:
        joined = ", ".join(str(path) for path in existing)
        raise FileExistsError(
            f"Refusing to overwrite existing artifact(s): {joined}. "
            "Choose new paths or pass --force after review."
        )


def render_player(
    song_title: str,
    octave_shift: int,
    schedule: list[list[float | int]],
    skipped: list[dict[str, Any]],
) -> str:
    """Fill only explicit literals into the self-contained player template."""

    return (
        PLAYER_TEMPLATE.replace("__OCTAVE_SHIFT__", repr(octave_shift))
        .replace("__EVENTS__", json.dumps(schedule, ensure_ascii=False, indent=2))
        .replace("__SKIPPED_EVENTS__", json.dumps(skipped, ensure_ascii=False, indent=2))
        .replace("__SONG_TITLE__", repr(song_title))
    )


def build_manifest(
    args: argparse.Namespace,
    track_index: int,
    selected_track: mido.MidiTrack,
    notes: list[Any],
    octave_shift: int,
    schedule: list[list[float | int]],
    unplayable: list[dict[str, Any]],
    audit_report: dict[str, Any],
    extraction_report: dict[str, Any] | None,
    conversion_report: dict[str, Any] | None,
) -> dict[str, Any]:
    """Create a provenance and placement record without inventing license facts."""

    return {
        "schema_version": 1,
        "source_midi": str(args.input),
        "source_page": args.source_page,
        "declared_license_or_permission": args.license,
        "intended_use": args.intended_use,
        "selected_track": {
            "index": track_index,
            "name": track_name(selected_track) or None,
        },
        "audit_report": audit_report,
        "extraction_report": extraction_report,
        "conversion_report": conversion_report,
        "validation": {
            "note_count": len(notes),
            "strictly_monophonic": True,
            "source_range": {
                "low_pitch": min(note.pitch for note in notes),
                "low_note": note_name(min(note.pitch for note in notes)),
                "high_pitch": max(note.pitch for note in notes),
                "high_note": note_name(max(note.pitch for note in notes)),
            },
        },
        "placement": {
            "global_octave_shift": octave_shift,
            "playable_range": {
                "low_pitch": PLAYABLE_LOW,
                "low_note": note_name(PLAYABLE_LOW),
                "high_pitch": PLAYABLE_HIGH,
                "high_note": note_name(PLAYABLE_HIGH),
            },
            "exact_playable_count": len(schedule),
            "unplayable_count": len(unplayable),
            "unplayable_events": unplayable,
        },
        "player_file": str(args.output),
        "player_written": not unplayable or args.allow_unplayable,
    }


def run(args: argparse.Namespace) -> int:
    ensure_safe_outputs(
        args.input,
        args.output,
        args.manifest,
        [
            ("audit report", args.audit_report),
            ("extraction report", args.extraction_report),
            ("conversion report", args.conversion_report),
        ],
        args.force,
    )
    midi = mido.MidiFile(str(args.input))
    track_index, selected_track = choose_melody_track(midi, args.track)
    notes, anomalies = parse_track_notes(selected_track)
    if not notes:
        raise ValueError("The selected melody track has no complete note events.")
    maximum, overlapping_starts, same_onset = overlap_metrics(notes)
    if maximum > 1 or overlapping_starts:
        raise ValueError(
            "The selected track is not strictly monophonic "
            f"(max simultaneous={maximum}, overlaps={overlapping_starts}, "
            f"same onset max={same_onset}). Run midi_tools.py extract and validate first."
        )
    if any(anomalies.values()):
        raise ValueError(
            f"The selected track has incomplete note data: {anomalies}. "
            "Repair or choose a clean source before player generation."
        )

    audit_report = audit_evidence(args.audit_report, args.input, track_index)
    extraction_report = extraction_evidence(args.extraction_report, args.input)
    conversion_report = conversion_evidence(args.conversion_report, args.input)
    octave_shift = choose_global_octave_shift(notes, args.global_octave_shift)
    schedule, unplayable = make_schedule(notes, midi, octave_shift)
    manifest = build_manifest(
        args,
        track_index,
        selected_track,
        notes,
        octave_shift,
        schedule,
        unplayable,
        audit_report,
        extraction_report,
        conversion_report,
    )
    if args.manifest:
        write_json(args.manifest, manifest)
    if unplayable and not args.allow_unplayable:
        raise ValueError(
            f"{len(unplayable)} notes remain outside {note_name(PLAYABLE_LOW)} through "
            f"{note_name(PLAYABLE_HIGH)} after shift {octave_shift:+d}. "
            "Review the manifest; do not silently fold them. Re-run with "
            "--allow-unplayable only after explicit user approval to skip them."
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        render_player(args.song_title, octave_shift, schedule, unplayable),
        encoding="utf-8",
    )
    print(
        f"Wrote {args.output}: {len(schedule)} exact playable events, "
        f"shift {octave_shift:+d}, skipped {len(unplayable)}."
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a Delta player from a validated melody-only MIDI."
    )
    parser.add_argument("input", type=Path, help="validated melody MIDI")
    parser.add_argument("output", type=Path, help="generated player Python file")
    parser.add_argument("--song-title", default="Untitled Delta melody")
    parser.add_argument(
        "--track",
        help="exact track name or numeric index; optional for a melody_only file",
    )
    parser.add_argument(
        "--global-octave-shift",
        default="auto",
        help="auto or an explicit whole-octave shift such as -24",
    )
    parser.add_argument(
        "--allow-unplayable",
        action="store_true",
        help="write a player that explicitly skips reported out-of-range events",
    )
    parser.add_argument("--manifest", type=Path, required=True, help="path for the build manifest")
    parser.add_argument(
        "--audit-report",
        type=Path,
        required=True,
        help="post-conversion audit JSON for this exact melody MIDI",
    )
    parser.add_argument(
        "--extraction-report",
        type=Path,
        help="optional extraction JSON that produced this melody MIDI",
    )
    parser.add_argument(
        "--conversion-report",
        type=Path,
        help="optional reviewed-score conversion JSON that produced this melody MIDI",
    )
    parser.add_argument(
        "--source-page",
        required=True,
        help="original source page or a clear source reference supplied by the user",
    )
    parser.add_argument(
        "--license",
        required=True,
        help="license or permission as supplied by the user",
    )
    parser.add_argument(
        "--intended-use",
        choices=("private", "public"),
        required=True,
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace existing reviewed player/manifest artifacts, never the MIDI input",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return run(args)
    except (OSError, ValueError, RuntimeError, EOFError) as exc:
        parser.exit(1, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
