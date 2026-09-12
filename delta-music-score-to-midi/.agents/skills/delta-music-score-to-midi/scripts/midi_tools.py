#!/usr/bin/env python3
"""Audit a MIDI file or extract one reviewed melody track.

This utility intentionally does not guess a melody from a whole arrangement.
Extraction accepts one explicit source track and makes any chord/overlap policy
visible in its report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

try:
    import mido
except ModuleNotFoundError as exc:  # pragma: no cover - depends on local setup
    raise SystemExit(
        "This tool needs mido. Install it with: py -m pip install mido"
    ) from exc


NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
CONDUCTOR_TYPES = {"set_tempo", "time_signature", "key_signature"}
STRUCTURE_CLASSES = (
    "isolated-melody",
    "karaoke-guide",
    "independent-melodic-part",
    "mixed-melody-accompaniment",
    "imitative-polyphony",
    "chordal-texture",
    "unknown",
)
EXTRACTION_REPORT_FORMAT = "delta-midi-extract/v2"
SAFE_REDUCTION_STRUCTURE_CLASSES = {
    "isolated-melody",
    "karaoke-guide",
    "independent-melodic-part",
}
TRIMMABLE_STRUCTURE_CLASSES = {"isolated-melody", "karaoke-guide"}


@dataclass(frozen=True)
class Note:
    """A complete note event expressed in absolute MIDI ticks."""

    start: int
    end: int
    pitch: int
    velocity: int
    channel: int


def note_name(pitch: int) -> str:
    """Return an unambiguous scientific-pitch label for a MIDI pitch."""

    return f"{NOTE_NAMES[pitch % 12]}{pitch // 12 - 1}"


def file_sha256(path: Path) -> str:
    """Hash a source file without loading an entire large MIDI into memory."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def absolute_messages(track: mido.MidiTrack) -> Iterable[tuple[int, int, Any]]:
    """Yield absolute tick, order, and message values for one MIDI track."""

    tick = 0
    for order, message in enumerate(track):
        tick += int(message.time)
        yield tick, order, message


def parse_track_notes(track: mido.MidiTrack) -> tuple[list[Note], dict[str, int]]:
    """Pair MIDI note-on/off events without changing the source timing."""

    active: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    notes: list[Note] = []
    unmatched_note_off = 0
    zero_length_notes = 0

    for tick, _, message in absolute_messages(track):
        if message.type == "note_on" and message.velocity > 0:
            active[(message.channel, message.note)].append((tick, message.velocity))
            continue

        is_note_end = message.type == "note_off" or (
            message.type == "note_on" and message.velocity == 0
        )
        if not is_note_end:
            continue

        key = (message.channel, message.note)
        if not active[key]:
            unmatched_note_off += 1
            continue

        start, velocity = active[key].pop(0)
        if tick <= start:
            zero_length_notes += 1
            continue
        notes.append(
            Note(
                start=start,
                end=tick,
                pitch=message.note,
                velocity=velocity,
                channel=message.channel,
            )
        )

    unterminated_notes = sum(len(starts) for starts in active.values())
    notes.sort(key=lambda item: (item.start, item.end, item.pitch, item.channel))
    return notes, {
        "unmatched_note_off": unmatched_note_off,
        "unterminated_notes": unterminated_notes,
        "zero_length_notes": zero_length_notes,
    }


def track_name(track: mido.MidiTrack) -> str:
    """Return the first explicit track name, or a stable fallback."""

    for _, _, message in absolute_messages(track):
        if message.type == "track_name":
            return message.name or ""
    return ""


def overlap_metrics(notes: list[Note]) -> tuple[int, int, int]:
    """Return max simultaneous notes, overlapping starts, and max same onset."""

    events: list[tuple[int, int, int]] = []
    onsets = Counter()
    for note in notes:
        events.append((note.end, 0, -1))  # End before start at the same tick.
        events.append((note.start, 1, 1))
        onsets[note.start] += 1

    current = 0
    maximum = 0
    overlapping_starts = 0
    for _, _, change in sorted(events):
        if change < 0:
            current = max(0, current - 1)
        else:
            if current:
                overlapping_starts += 1
            current += 1
            maximum = max(maximum, current)

    return maximum, overlapping_starts, max(onsets.values(), default=0)


def summarize_track(index: int, track: mido.MidiTrack, ticks_per_beat: int) -> dict[str, Any]:
    """Create a report entry for one track."""

    notes, anomalies = parse_track_notes(track)
    maximum, overlapping_starts, same_onset_maximum = overlap_metrics(notes)
    programs = sorted(
        {
            message.program
            for _, _, message in absolute_messages(track)
            if message.type == "program_change"
        }
    )
    durations = [note.end - note.start for note in notes]
    duration_counts = Counter(durations)
    common_duration, common_duration_count = duration_counts.most_common(1)[0] if durations else (None, 0)
    onset_ticks = sorted({note.start for note in notes})
    onset_intervals = [
        later - earlier for earlier, later in zip(onset_ticks, onset_ticks[1:])
    ]
    uniform_ratio = (
        round(common_duration_count / len(durations), 4) if durations else 0.0
    )
    likely_karaoke_guide = bool(
        durations
        and uniform_ratio >= 0.85
        and common_duration is not None
        and common_duration <= max(1, ticks_per_beat // 4)
    )

    return {
        "track_index": index,
        "track_name": track_name(track) or None,
        "programs": programs,
        "channels": sorted({note.channel for note in notes}),
        "note_count": len(notes),
        "unique_onset_count": len(onset_ticks),
        "max_simultaneous_notes": maximum,
        "overlapping_note_count": overlapping_starts,
        "max_same_onset_notes": same_onset_maximum,
        "strictly_monophonic": maximum <= 1 and overlapping_starts == 0,
        "lowest_pitch": min((note.pitch for note in notes), default=None),
        "lowest_note": note_name(min(note.pitch for note in notes)) if notes else None,
        "highest_pitch": max((note.pitch for note in notes), default=None),
        "highest_note": note_name(max(note.pitch for note in notes)) if notes else None,
        "first_onset_tick": min((note.start for note in notes), default=None),
        "last_end_tick": max((note.end for note in notes), default=None),
        "median_duration_ticks": int(statistics.median(durations)) if durations else None,
        "most_common_duration_ticks": common_duration,
        "most_common_duration_ratio": uniform_ratio,
        "median_onset_interval_ticks": (
            int(statistics.median(onset_intervals)) if onset_intervals else None
        ),
        "likely_karaoke_or_guide_track": likely_karaoke_guide,
        "anomalies": anomalies,
    }


def canonical_tempo_events(midi: mido.MidiFile) -> list[tuple[int, int]]:
    """Return one effective tempo at each tick, including a default at tick zero."""

    raw: list[tuple[int, int, int, int]] = []
    for track_index, track in enumerate(midi.tracks):
        for tick, order, message in absolute_messages(track):
            if message.type == "set_tempo":
                raw.append((tick, track_index, order, message.tempo))

    effective: dict[int, int] = {}
    for tick, _, _, tempo in sorted(raw):
        effective[tick] = tempo
    events = sorted(effective.items())
    if not events or events[0][0] != 0:
        events.insert(0, (0, 500000))
    return events


def tick_to_seconds(tick: int, tempo_events: list[tuple[int, int]], ticks_per_beat: int) -> float:
    """Convert an absolute tick through an arbitrary tempo map."""

    elapsed = 0.0
    previous_tick = 0
    current_tempo = 500000
    for event_tick, tempo in tempo_events:
        if event_tick > tick:
            break
        elapsed += (
            (event_tick - previous_tick) * current_tempo / (ticks_per_beat * 1_000_000)
        )
        previous_tick = event_tick
        current_tempo = tempo
    elapsed += (tick - previous_tick) * current_tempo / (ticks_per_beat * 1_000_000)
    return elapsed


def metadata_report(midi: mido.MidiFile) -> dict[str, Any]:
    """Collect conductor information without assuming it only lives on track zero."""

    total_ticks = 0
    time_signatures: list[dict[str, Any]] = []
    key_signatures: list[dict[str, Any]] = []
    for track_index, track in enumerate(midi.tracks):
        for tick, order, message in absolute_messages(track):
            total_ticks = max(total_ticks, tick)
            if message.type == "time_signature":
                time_signatures.append(
                    {
                        "tick": tick,
                        "track_index": track_index,
                        "order": order,
                        "numerator": message.numerator,
                        "denominator": message.denominator,
                        "clocks_per_click": message.clocks_per_click,
                        "notated_32nd_notes_per_beat": message.notated_32nd_notes_per_beat,
                    }
                )
            elif message.type == "key_signature":
                key_signatures.append(
                    {
                        "tick": tick,
                        "track_index": track_index,
                        "order": order,
                        "key": message.key,
                    }
                )

    tempi = canonical_tempo_events(midi)
    return {
        "midi_type": midi.type,
        "ticks_per_beat": midi.ticks_per_beat,
        "total_ticks": total_ticks,
        "duration_seconds": round(
            tick_to_seconds(total_ticks, tempi, midi.ticks_per_beat), 6
        ),
        "tempo_map": [
            {
                "tick": tick,
                "microseconds_per_beat": tempo,
                "bpm": round(60_000_000 / tempo, 6),
            }
            for tick, tempo in tempi
        ],
        "time_signatures": sorted(
            time_signatures, key=lambda item: (item["tick"], item["track_index"], item["order"])
        ),
        "key_signatures": sorted(
            key_signatures, key=lambda item: (item["tick"], item["track_index"], item["order"])
        ),
    }


def audit_midi(path: Path) -> dict[str, Any]:
    """Open a MIDI file and return only reproducible facts about its contents."""

    midi = mido.MidiFile(str(path))
    return {
        "source_file": str(path.resolve()),
        "source_sha256": file_sha256(path),
        "global": metadata_report(midi),
        "tracks": [
            summarize_track(index, track, midi.ticks_per_beat)
            for index, track in enumerate(midi.tracks)
        ],
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_safe_writes(
    input_path: Path, output_paths: list[Path | None], force: bool
) -> None:
    """Protect the input and require an explicit choice before replacement."""

    targets = [path for path in output_paths if path is not None]
    resolved_input = input_path.resolve()
    resolved_targets = [path.resolve() for path in targets]
    if resolved_input in resolved_targets:
        raise ValueError("A report or derived output must not overwrite the input file.")
    if len(set(resolved_targets)) != len(resolved_targets):
        raise ValueError("Each requested output/report path must be different.")
    existing = [path for path in targets if path.exists()]
    if existing and not force:
        joined = ", ".join(str(path) for path in existing)
        raise FileExistsError(
            f"Refusing to overwrite existing artifact(s): {joined}. "
            "Choose new paths or pass --force for reviewed derived artifacts."
        )


def render_audit_markdown(report: dict[str, Any]) -> str:
    """Render a compact, human-readable companion to the JSON report."""

    global_info = report["global"]
    lines = [
        "# MIDI track audit",
        "",
        f"- Source: {report['source_file']}",
        f"- MIDI type / PPQ: {global_info['midi_type']} / {global_info['ticks_per_beat']}",
        f"- Duration: {global_info['duration_seconds']:.3f} seconds",
        f"- Tempo events: {len(global_info['tempo_map'])}",
        "",
        "| # | Track | Notes | Onsets | Polyphony | Overlaps | Range | Karaoke hint |",
        "| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for track in report["tracks"]:
        name = track["track_name"] or "(unnamed)"
        note_range = (
            f"{track['lowest_note']} to {track['highest_note']}"
            if track["note_count"]
            else "-"
        )
        lines.append(
            "| {index} | {name} | {notes} | {onsets} | {polyphony} | {overlaps} | {range_} | {karaoke} |".format(
                index=track["track_index"],
                name=name.replace("|", "\\|"),
                notes=track["note_count"],
                onsets=track["unique_onset_count"],
                polyphony=track["max_simultaneous_notes"],
                overlaps=track["overlapping_note_count"],
                range_=note_range,
                karaoke="yes" if track["likely_karaoke_or_guide_track"] else "no",
            )
        )
    lines.extend(["", "See the JSON report for tempo, meter, key, and anomaly details.", ""])
    return "\n".join(lines)


def select_track(midi: mido.MidiFile, reference: str) -> tuple[int, mido.MidiTrack]:
    """Select a track by exact numeric index or exact case-insensitive name."""

    try:
        index = int(reference)
    except ValueError:
        index = -1
    else:
        if 0 <= index < len(midi.tracks):
            return index, midi.tracks[index]
        raise ValueError(f"Track index {index} is outside 0..{len(midi.tracks) - 1}.")

    requested = reference.casefold()
    matches = [
        (index, track)
        for index, track in enumerate(midi.tracks)
        if track_name(track).casefold() == requested
    ]
    if len(matches) == 1:
        return matches[0]
    names = ", ".join(
        f"{index}:{track_name(track) or '(unnamed)'}"
        for index, track in enumerate(midi.tracks)
    )
    if not matches:
        raise ValueError(
            f'No exact track name matches "{reference}". Available tracks: {names}'
        )
    raise ValueError(
        f'More than one track exactly matches "{reference}". Use an index: {names}'
    )


def reduce_same_onset(
    notes: list[Note], same_onset: str, overlaps: str
) -> list[Note]:
    """Resolve only explicitly requested chord and overlap cases."""

    groups: dict[int, list[Note]] = defaultdict(list)
    for note in notes:
        groups[note.start].append(note)

    reduced: list[Note] = []
    chord_onsets = [tick for tick, group in groups.items() if len(group) > 1]
    if chord_onsets and same_onset == "reject":
        raise ValueError(
            f"Selected track has {len(chord_onsets)} same-onset chord positions. "
            "Review it and choose --same-onset highest or lowest only when justified."
        )

    for tick in sorted(groups):
        group = groups[tick]
        if len(group) == 1:
            reduced.append(group[0])
        elif same_onset == "highest":
            reduced.append(max(group, key=lambda item: (item.pitch, item.velocity, item.end)))
        elif same_onset == "lowest":
            reduced.append(min(group, key=lambda item: (item.pitch, -item.velocity, item.end)))

    reduced.sort(key=lambda item: (item.start, item.end, item.pitch, item.channel))
    resolved: list[Note] = []
    overlap_positions = 0
    for index, note in enumerate(reduced):
        next_start = reduced[index + 1].start if index + 1 < len(reduced) else None
        if next_start is not None and note.end > next_start:
            overlap_positions += 1
            if overlaps == "reject":
                raise ValueError(
                    f"Selected melody still overlaps at tick {note.start}. "
                    "Review it and use --overlaps truncate only when ending at the next onset is valid."
                )
            note = replace(note, end=next_start)
        resolved.append(note)

    if overlap_positions and overlaps != "truncate":
        raise AssertionError("Unexpected overlap policy state.")
    return resolved


def validate_structure_policy(
    structure_class: str | None,
    same_onset: str,
    overlaps: str,
    duration_mode: str = "source",
    trim_leading_rest: bool = False,
) -> None:
    """Gate lossy pitch/timing edits behind an explicit, reviewed structure class.

    Passing the final output's strict-monophony check only proves that no notes
    overlap after processing. It does not prove that the retained notes form the
    intended melody. In particular, an offset bass note can enter between melody
    onsets and survive ``highest + truncate`` as a plausible-looking monophonic
    result. Default reject policies remain available without classification.
    """

    reduction_requested = same_onset in {"highest", "lowest"} or overlaps == "truncate"
    if reduction_requested:
        if structure_class is None:
            raise ValueError(
                "--same-onset highest/lowest and --overlaps truncate are lossy reductions. "
                "Classify the reviewed source with --structure-class before using them."
            )
        if structure_class not in SAFE_REDUCTION_STRUCTURE_CLASSES:
            safe = ", ".join(sorted(SAFE_REDUCTION_STRUCTURE_CLASSES))
            raise ValueError(
                f'--structure-class "{structure_class}" does not permit highest/lowest '
                "selection or overlap truncation. Isolate a genuine melodic part first; "
                f"lossy reduction is allowed only for: {safe}."
            )

    if duration_mode == "onset" and structure_class != "karaoke-guide":
        raise ValueError(
            "--duration-mode onset reconstructs note lengths and is allowed only after "
            "classifying the reviewed track as --structure-class karaoke-guide."
        )

    if trim_leading_rest and structure_class not in TRIMMABLE_STRUCTURE_CLASSES:
        safe = ", ".join(sorted(TRIMMABLE_STRUCTURE_CLASSES))
        raise ValueError(
            "--trim-leading-rest changes the musical time origin and requires an "
            f"explicit reviewed structure class: {safe}. Preserve leading rests for "
            "independent parts and imitative polyphony."
        )


def apply_duration_mode(
    notes: list[Note],
    ticks_per_beat: int,
    mode: str,
    onset_gate: float,
    long_gap_beats: float,
    long_gap_hold_beats: float,
) -> list[Note]:
    """Optionally reconstruct guide-track durations from the following onset."""

    if mode == "source" or len(notes) < 2:
        return notes
    if not 0 < onset_gate <= 1:
        raise ValueError("--onset-gate must be greater than 0 and no more than 1.")
    if long_gap_beats <= 0 or long_gap_hold_beats <= 0:
        raise ValueError("Long-gap values must be positive.")

    long_gap_ticks = round(long_gap_beats * ticks_per_beat)
    long_gap_hold_ticks = round(long_gap_hold_beats * ticks_per_beat)
    rebuilt: list[Note] = []
    for index, note in enumerate(notes):
        if index == len(notes) - 1:
            rebuilt.append(note)
            continue
        interval = notes[index + 1].start - note.start
        if interval <= 0:
            raise ValueError("Onset reconstruction requires strictly increasing note starts.")
        proposed = round(interval * onset_gate)
        if interval > long_gap_ticks:
            proposed = min(proposed, long_gap_hold_ticks)
        rebuilt.append(replace(note, end=note.start + max(1, proposed)))
    return rebuilt


def conductor_events(midi: mido.MidiFile, trim_ticks: int) -> list[tuple[int, int, Any]]:
    """Carry the effective tempo, meter, and key into a newly written MIDI."""

    before: dict[str, tuple[int, int, int, Any]] = {}
    after: list[tuple[int, int, int, Any]] = []
    for track_index, track in enumerate(midi.tracks):
        for tick, order, message in absolute_messages(track):
            if message.type not in CONDUCTOR_TYPES:
                continue
            copied = message.copy(time=0)
            if tick <= trim_ticks:
                candidate = (tick, track_index, order, copied)
                if (
                    message.type not in before
                    or candidate[:3] >= before[message.type][:3]
                ):
                    before[message.type] = candidate
            else:
                after.append((tick - trim_ticks, track_index, order, copied))

    events: list[tuple[int, int, Any]] = []
    tempo = before.get(
        "set_tempo", (0, 0, 0, mido.MetaMessage("set_tempo", tempo=500000))
    )[3]
    events.append((0, 0, tempo.copy(time=0)))
    if "time_signature" in before:
        events.append((0, 1, before["time_signature"][3].copy(time=0)))
    if "key_signature" in before:
        events.append((0, 2, before["key_signature"][3].copy(time=0)))

    priority = {"set_tempo": 0, "time_signature": 1, "key_signature": 2}
    for tick, track_index, order, message in sorted(after):
        events.append((tick, 10 + priority[message.type] + track_index * 1000 + order, message))
    return events


def append_absolute_messages(
    track: mido.MidiTrack, events: list[tuple[int, int, Any]]
) -> None:
    """Append copied MIDI messages while converting absolute ticks to deltas."""

    previous_tick = 0
    for tick, _, message in sorted(events, key=lambda item: (item[0], item[1])):
        if tick < previous_tick:
            raise ValueError("Cannot write events out of tick order.")
        track.append(message.copy(time=tick - previous_tick))
        previous_tick = tick


def write_melody_midi(
    source: mido.MidiFile, notes: list[Note], output: Path, trim_ticks: int
) -> None:
    """Write a clean, one-track melody MIDI plus a conductor track."""

    output.parent.mkdir(parents=True, exist_ok=True)
    result = mido.MidiFile(type=1, ticks_per_beat=source.ticks_per_beat)
    conductor = result.add_track("conductor")
    append_absolute_messages(conductor, conductor_events(source, trim_ticks))

    melody = result.add_track("melody_only")
    channel = notes[0].channel if notes else 0
    melody.append(mido.Message("program_change", channel=channel, program=0, time=0))
    events: list[tuple[int, int, Any]] = []
    for note in notes:
        events.append(
            (
                note.start,
                1,
                mido.Message(
                    "note_on",
                    channel=note.channel,
                    note=note.pitch,
                    velocity=note.velocity,
                    time=0,
                ),
            )
        )
        events.append(
            (
                note.end,
                0,
                mido.Message(
                    "note_off",
                    channel=note.channel,
                    note=note.pitch,
                    velocity=0,
                    time=0,
                ),
            )
        )
    append_absolute_messages(melody, events)
    result.save(str(output))


def run_audit(args: argparse.Namespace) -> int:
    ensure_safe_writes(args.input, [args.json, args.markdown], args.force)
    report = audit_midi(args.input)
    if args.json:
        write_json(args.json, report)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(render_audit_markdown(report), encoding="utf-8")
    if not args.json and not args.markdown:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Audited {args.input}")
    return 0


def run_extract(args: argparse.Namespace) -> int:
    structure_class = getattr(args, "structure_class", None)
    validate_structure_policy(
        structure_class,
        args.same_onset,
        args.overlaps,
        args.duration_mode,
        args.trim_leading_rest,
    )
    ensure_safe_writes(args.input, [args.output, args.report], args.force)
    source = mido.MidiFile(str(args.input))
    track_index, track = select_track(source, args.track)
    notes, anomalies = parse_track_notes(track)
    if not notes:
        raise ValueError(f"Selected track {track_index} contains no complete notes.")
    if any(anomalies.values()):
        raise ValueError(
            f"Selected track has incomplete note data: {anomalies}. "
            "Choose or repair a clean source before extraction."
        )

    selected = reduce_same_onset(notes, args.same_onset, args.overlaps)
    selected = apply_duration_mode(
        selected,
        source.ticks_per_beat,
        args.duration_mode,
        args.onset_gate,
        args.long_gap_beats,
        args.long_gap_hold_beats,
    )
    trim_ticks = selected[0].start if args.trim_leading_rest else 0
    if trim_ticks:
        selected = [
            replace(note, start=note.start - trim_ticks, end=note.end - trim_ticks)
            for note in selected
        ]

    write_melody_midi(source, selected, args.output, trim_ticks)
    output_report = audit_midi(args.output)
    melody_track = next(
        track_report
        for track_report in output_report["tracks"]
        if track_report["track_name"] == "melody_only"
    )
    extraction_report = {
        "report_format": EXTRACTION_REPORT_FORMAT,
        "source_file": str(args.input.resolve()),
        "source_sha256": file_sha256(args.input),
        "output_file": str(args.output.resolve()),
        "output_sha256": output_report["source_sha256"],
        "source_track_index": track_index,
        "source_track_name": track_name(track) or None,
        "structure_class": structure_class,
        "source_anomalies": anomalies,
        "settings": {
            "same_onset": args.same_onset,
            "overlaps": args.overlaps,
            "duration_mode": args.duration_mode,
            "onset_gate": args.onset_gate,
            "long_gap_beats": args.long_gap_beats,
            "long_gap_hold_beats": args.long_gap_hold_beats,
            "trim_leading_rest": args.trim_leading_rest,
            "trimmed_ticks": trim_ticks,
        },
        "output_melody": melody_track,
    }
    if not melody_track["strictly_monophonic"]:
        raise RuntimeError(
            "Internal validation failed: output is not strictly monophonic. "
            "Do not use it to build a player."
        )
    if args.report:
        write_json(args.report, extraction_report)
    print(
        f"Wrote strict melody MIDI: {args.output} "
        f"({melody_track['note_count']} notes, "
        f"{melody_track['lowest_note']} to {melody_track['highest_note']})"
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit a MIDI or extract one explicitly selected melody track."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    audit = commands.add_parser("audit", help="write a factual MIDI track report")
    audit.add_argument("input", type=Path)
    audit.add_argument("--json", type=Path, help="path for the JSON report")
    audit.add_argument("--markdown", type=Path, help="path for the Markdown report")
    audit.add_argument(
        "--force",
        action="store_true",
        help="replace existing reviewed report files, never the input MIDI",
    )
    audit.set_defaults(handler=run_audit)

    extract = commands.add_parser(
        "extract", help="create a strict melody MIDI from one reviewed track"
    )
    extract.add_argument("input", type=Path)
    extract.add_argument("output", type=Path)
    extract.add_argument(
        "--track",
        required=True,
        help="exact track name or numeric track index from the audit report",
    )
    extract.add_argument(
        "--same-onset",
        choices=("reject", "highest", "lowest"),
        default="reject",
        help="policy for simultaneous notes in the chosen source track",
    )
    extract.add_argument(
        "--overlaps",
        choices=("reject", "truncate"),
        default="reject",
        help="policy for notes that run across a later onset",
    )
    extract.add_argument(
        "--structure-class",
        choices=STRUCTURE_CLASSES,
        help=(
            "reviewed musical structure; required by highest/lowest or truncate "
            "because strict monophony alone does not identify a melody"
        ),
    )
    extract.add_argument(
        "--duration-mode",
        choices=("source", "onset"),
        default="source",
        help="preserve note-offs or rebuild durations from following onsets",
    )
    extract.add_argument("--onset-gate", type=float, default=0.88)
    extract.add_argument("--long-gap-beats", type=float, default=2.0)
    extract.add_argument("--long-gap-hold-beats", type=float, default=1.0)
    extract.add_argument(
        "--trim-leading-rest",
        action="store_true",
        help="start the output MIDI at the first melody onset",
    )
    extract.add_argument("--report", type=Path, help="path for extraction JSON")
    extract.add_argument(
        "--force",
        action="store_true",
        help="replace an existing reviewed derived output, never the input source",
    )
    extract.set_defaults(handler=run_extract)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.handler(args)
    except (OSError, ValueError, RuntimeError, EOFError) as exc:
        parser.exit(1, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
