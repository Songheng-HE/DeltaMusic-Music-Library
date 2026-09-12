"""Halve reviewed short inter-note rests in a single melody MIDI."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import mido


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def complete_notes(track: mido.MidiTrack) -> list[tuple[int, int]]:
    tick = 0
    active: dict[tuple[int, int], int] = {}
    notes: list[tuple[int, int]] = []
    for message in track:
        tick += message.time
        key = (getattr(message, "channel", -1), getattr(message, "note", -1))
        if message.type == "note_on" and message.velocity > 0:
            active[key] = tick
        elif message.type in {"note_off", "note_on"} and (message.type == "note_off" or message.velocity == 0):
            start = active.pop(key, None)
            if start is not None:
                notes.append((start, tick))
    if active:
        raise ValueError("unterminated note in source")
    return sorted(notes)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--track", type=int, default=1)
    parser.add_argument("--min-gap", type=int, required=True)
    parser.add_argument("--max-gap", type=int, required=True)
    parser.add_argument("--end-tick", type=int, help="only select rests ending at or before this tick")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.min_gap <= 0 or args.max_gap < args.min_gap:
        raise SystemExit("gap bounds must be positive and increasing")
    if args.output.exists() or args.report.exists():
        raise SystemExit("refusing to overwrite an existing output or report")

    source = mido.MidiFile(args.input)
    notes = complete_notes(source.tracks[args.track])
    selections = []
    for (_, end), (start, _) in zip(notes, notes[1:]):
        gap = start - end
        if (
            args.min_gap <= gap <= args.max_gap
            and (args.end_tick is None or start <= args.end_tick)
        ):
            selections.append({"start_tick": end, "end_tick": start, "gap_ticks": gap, "removed_ticks": gap // 2})

    cut_points: list[tuple[int, int]] = []
    cumulative = 0
    for selection in selections:
        cut_start = selection["end_tick"] - selection["removed_ticks"]
        cut_points.append((cut_start, selection["removed_ticks"]))
        cumulative += selection["removed_ticks"]

    output = mido.MidiFile(type=source.type, ticks_per_beat=source.ticks_per_beat)
    for track in source.tracks:
        old_tick = 0
        new_tick = 0
        replacement = mido.MidiTrack()
        for message in track:
            old_tick += message.time
            if any(start < old_tick < start + amount for start, amount in cut_points):
                raise ValueError(f"event occurs inside a selected removed interval at tick {old_tick}")
            shift = sum(amount for start, amount in cut_points if old_tick >= start + amount)
            target_tick = old_tick - shift
            replacement.append(message.copy(time=target_tick - new_tick))
            new_tick = target_tick
        output.tracks.append(replacement)
    output.save(args.output)

    args.report.write_text(
        json.dumps(
            {
                "operation": "halve-reviewed-short-rests/v1",
                "input_file": str(args.input.resolve()),
                "input_sha256": sha256(args.input),
                "output_file": str(args.output.resolve()),
                "output_sha256": sha256(args.output),
                "track_index": args.track,
                "selection_bounds_ticks": {"min": args.min_gap, "max": args.max_gap},
                "selection_end_tick": args.end_tick,
                "selected_rests": selections,
                "total_removed_ticks": cumulative,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
