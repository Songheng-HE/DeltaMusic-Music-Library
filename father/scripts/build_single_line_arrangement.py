"""Build the reviewed B option for 筷子兄弟《父亲》.

This is intentionally song-specific: it keeps the named Voice track intact and
inserts one user-approved, whole nine-note phrase from Piano.  It never chooses
notes by pitch height or attempts general melody extraction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import mido


VOICE_TRACK_NAME = "Voice"
PIANO_TRACK_NAME = "Piano"
HANDOFF_TICKS = (70080, 70320, 70560, 70800, 71760, 72000, 72240, 72480, 72720)
HANDOFF_PITCHES = (64, 68, 63, 64, 63, 64, 68, 63, 64)


@dataclass(frozen=True)
class Note:
    start: int
    end: int
    pitch: int
    velocity: int
    channel: int
    source: str


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def named_track(midi: mido.MidiFile, name: str) -> mido.MidiTrack:
    for track in midi.tracks:
        if next((message.name for message in track if message.type == "track_name"), None) == name:
            return track
    raise ValueError(f"Missing required track: {name}")


def notes(track: mido.MidiTrack, source: str) -> list[Note]:
    tick = 0
    active: dict[tuple[int, int], tuple[int, int]] = {}
    result: list[Note] = []
    for message in track:
        tick += message.time
        if message.type == "note_on" and message.velocity > 0:
            key = (message.channel, message.note)
            if key in active:
                raise ValueError(f"Repeated note-on before note-off at tick {tick}: {key}")
            active[key] = (tick, message.velocity)
        elif message.type in ("note_off", "note_on") and (
            message.type == "note_off" or message.velocity == 0
        ):
            key = (message.channel, message.note)
            if key not in active:
                continue
            start, velocity = active.pop(key)
            if tick <= start:
                raise ValueError(f"Non-positive duration at tick {tick}: {key}")
            result.append(Note(start, tick, message.note, velocity, message.channel, source))
    if active:
        raise ValueError(f"Unterminated notes in {source}: {sorted(active)}")
    return sorted(result, key=lambda value: (value.start, value.end, value.pitch))


def validate_monophonic(values: list[Note]) -> None:
    for previous, current in zip(values, values[1:]):
        if current.start < previous.end:
            raise ValueError(
                f"Arrangement overlap: {previous.source} {previous.pitch} ends {previous.end}; "
                f"{current.source} {current.pitch} begins {current.start}."
            )


def conductor_messages(source: mido.MidiFile) -> list[tuple[int, int, mido.Message]]:
    events: list[tuple[int, int, mido.Message]] = []
    seen: set[tuple[int, str, tuple[tuple[str, object], ...]]] = set()
    allowed = {"set_tempo", "time_signature", "key_signature"}
    for track_index, track in enumerate(source.tracks):
        tick = 0
        for order, message in enumerate(track):
            tick += message.time
            if message.type not in allowed:
                continue
            signature = (tick, message.type, tuple(sorted(message.dict().items())))
            if signature in seen:
                continue
            seen.add(signature)
            events.append((tick, track_index * 1000 + order, message.copy(time=0)))
    return sorted(events, key=lambda item: (item[0], item[1]))


def append_absolute(track: mido.MidiTrack, events: list[tuple[int, int, mido.Message]]) -> None:
    previous_tick = 0
    for tick, _, message in sorted(events, key=lambda item: (item[0], item[1])):
        if tick < previous_tick:
            raise ValueError("Events are not in ascending time order")
        track.append(message.copy(time=tick - previous_tick))
        previous_tick = tick


def scale_tempo(message: mido.Message, multiplier: float) -> mido.Message:
    """Keep all tempo-map shape while applying one global tempo multiplier."""
    if message.type != "set_tempo":
        return message
    return message.copy(tempo=max(1, round(message.tempo / multiplier)), time=0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument(
        "--trim-leading-ticks",
        type=int,
        default=0,
        help="Remove reviewed leading silence by shifting the complete output timeline earlier.",
    )
    parser.add_argument(
        "--tempo-multiplier",
        type=float,
        default=1.0,
        help="Multiply every existing BPM value without flattening the tempo map.",
    )
    parser.add_argument(
        "--drop-final-notes",
        type=int,
        default=0,
        help="Remove this many final reviewed melody notes while preserving the output timeline.",
    )
    args = parser.parse_args()

    if args.output.exists() or args.report.exists():
        raise FileExistsError("Refusing to overwrite an existing derived output or report.")
    if args.trim_leading_ticks < 0:
        raise ValueError("--trim-leading-ticks must be zero or positive.")
    if args.tempo_multiplier <= 0:
        raise ValueError("--tempo-multiplier must be positive.")
    if args.drop_final_notes < 0:
        raise ValueError("--drop-final-notes must be zero or positive.")

    source = mido.MidiFile(args.input)
    voice = notes(named_track(source, VOICE_TRACK_NAME), VOICE_TRACK_NAME)
    piano = notes(named_track(source, PIANO_TRACK_NAME), PIANO_TRACK_NAME)
    validate_monophonic(voice)

    piano_by_start = {note.start: note for note in piano}
    handoff = []
    for tick, pitch in zip(HANDOFF_TICKS, HANDOFF_PITCHES):
        candidate = piano_by_start.get(tick)
        if candidate is None or candidate.pitch != pitch:
            raise ValueError(f"Expected reviewed Piano note {pitch} at tick {tick}, found {candidate!r}")
        handoff.append(Note(candidate.start, candidate.end, candidate.pitch, candidate.velocity, 0, PIANO_TRACK_NAME))

    arrangement = sorted([*voice, *handoff], key=lambda value: (value.start, value.end, value.pitch))
    validate_monophonic(arrangement)
    if len(arrangement) != len(voice) + len(handoff):
        raise ValueError("Unexpected arrangement event count")
    source_total_ticks = max(sum(message.time for message in track) for track in source.tracks)
    if args.trim_leading_ticks > arrangement[0].start:
        raise ValueError("Cannot trim past the first reviewed melody event.")
    if args.trim_leading_ticks > source_total_ticks:
        raise ValueError("Cannot trim past the end of the source timeline.")
    if args.trim_leading_ticks:
        arrangement = [
            Note(
                note.start - args.trim_leading_ticks,
                note.end - args.trim_leading_ticks,
                note.pitch,
                note.velocity,
                note.channel,
                note.source,
            )
            for note in arrangement
        ]
    if args.drop_final_notes >= len(arrangement):
        raise ValueError("--drop-final-notes must leave at least one melody note.")
    omitted_final_notes = arrangement[-args.drop_final_notes :] if args.drop_final_notes else []
    if args.drop_final_notes:
        arrangement = arrangement[: -args.drop_final_notes]
    output_total_ticks = source_total_ticks - args.trim_leading_ticks

    result = mido.MidiFile(type=1, ticks_per_beat=source.ticks_per_beat)
    conductor = result.add_track("conductor")
    conductor.append(mido.MetaMessage("track_name", name="conductor", time=0))
    conductor_events = [
        (max(0, tick - args.trim_leading_ticks), order, scale_tempo(message, args.tempo_multiplier))
        for tick, order, message in conductor_messages(source)
    ]
    append_absolute(conductor, conductor_events)
    conductor_last_tick = conductor_events[-1][0] if conductor_events else 0
    conductor.append(mido.MetaMessage("end_of_track", time=output_total_ticks - conductor_last_tick))

    melody = result.add_track("single_line_arrangement")
    melody.append(mido.MetaMessage("track_name", name="single_line_arrangement", time=0))
    melody.append(mido.Message("program_change", channel=0, program=1, time=0))
    note_events: list[tuple[int, int, mido.Message]] = []
    for index, note in enumerate(arrangement):
        note_events.append((note.start, index * 2 + 1, mido.Message("note_on", channel=0, note=note.pitch, velocity=note.velocity, time=0)))
        note_events.append((note.end, index * 2, mido.Message("note_off", channel=0, note=note.pitch, velocity=0, time=0)))
    append_absolute(melody, note_events)
    melody.append(mido.MetaMessage("end_of_track", time=output_total_ticks - arrangement[-1].end))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output)

    report = {
        "format": "delta-single-line-arrangement/v1",
        "source_file": str(args.input.resolve()),
        "source_sha256": sha256(args.input),
        "intended_use": "private",
        "rights_status": "unknown",
        "classification": "single-line arrangement",
        "baseline": {"track_name": VOICE_TRACK_NAME, "note_count": len(voice)},
        "handoff": {
            "source_track_name": PIANO_TRACK_NAME,
            "reason": "User-confirmed complete phrase during the reviewed Voice gap.",
            "gap_start_tick": 69984,
            "gap_end_tick": 72960,
            "output_gap_start_tick": 69984 - args.trim_leading_ticks,
            "output_gap_end_tick": 72960 - args.trim_leading_ticks,
            "notes": [
                {
                    "source_tick": note.start,
                    "source_end_tick": note.end,
                    "output_tick": note.start - args.trim_leading_ticks,
                    "output_end_tick": note.end - args.trim_leading_ticks,
                    "pitch": note.pitch,
                    "source_track": note.source,
                }
                for note in handoff
            ],
        },
        "output_file": str(args.output.resolve()),
        "output_note_count": len(arrangement),
        "dropped_final_note_count": args.drop_final_notes,
        "dropped_final_notes": [
            {
                "output_tick": note.start,
                "output_end_tick": note.end,
                "source_tick": note.start + args.trim_leading_ticks,
                "source_end_tick": note.end + args.trim_leading_ticks,
                "pitch": note.pitch,
                "source_track": note.source,
            }
            for note in omitted_final_notes
        ],
        "source_total_ticks": source_total_ticks,
        "trim_leading_ticks": args.trim_leading_ticks,
        "output_total_ticks": output_total_ticks,
        "tempo_multiplier": args.tempo_multiplier,
        "tempo_events": [
            {
                "output_tick": tick,
                "bpm": round(mido.tempo2bpm(message.tempo), 6),
            }
            for tick, _, message in conductor_events
            if message.type == "set_tempo"
        ],
        "global_transpose_semitones": 0,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} with {len(arrangement)} notes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
