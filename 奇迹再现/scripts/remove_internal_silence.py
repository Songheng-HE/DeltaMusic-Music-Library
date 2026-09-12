"""Create a derived MIDI with one reviewed internal silent interval removed."""

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


def shifted_track(track: mido.MidiTrack, gap_start: int, gap_end: int) -> mido.MidiTrack:
    gap_ticks = gap_end - gap_start
    source_tick = 0
    target_tick = 0
    result = mido.MidiTrack()
    for message in track:
        source_tick += message.time
        if gap_start < source_tick < gap_end:
            raise ValueError(f"MIDI event occurs inside reviewed gap at tick {source_tick}")
        new_tick = source_tick if source_tick <= gap_start else source_tick - gap_ticks
        result.append(message.copy(time=new_tick - target_tick))
        target_tick = new_tick
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--gap-start", type=int, required=True)
    parser.add_argument("--gap-end", type=int, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    if args.gap_start < 0 or args.gap_end <= args.gap_start:
        raise SystemExit("gap bounds must be non-negative and increasing")
    if args.output.exists() or args.report.exists():
        raise SystemExit("refusing to overwrite an existing output or report")

    source_hash = sha256(args.input)
    source = mido.MidiFile(args.input)
    if args.gap_end > source.length * source.ticks_per_beat * 10:
        raise SystemExit("gap end is implausibly beyond the MIDI length")

    derived = mido.MidiFile(type=source.type, ticks_per_beat=source.ticks_per_beat)
    for track in source.tracks:
        derived.tracks.append(shifted_track(track, args.gap_start, args.gap_end))
    derived.save(args.output)

    report = {
        "operation": "remove-reviewed-internal-silence/v1",
        "input_file": str(args.input.resolve()),
        "input_sha256": source_hash,
        "output_file": str(args.output.resolve()),
        "output_sha256": sha256(args.output),
        "gap_start_tick": args.gap_start,
        "gap_end_tick": args.gap_end,
        "removed_ticks": args.gap_end - args.gap_start,
        "ticks_per_beat": source.ticks_per_beat,
    }
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
