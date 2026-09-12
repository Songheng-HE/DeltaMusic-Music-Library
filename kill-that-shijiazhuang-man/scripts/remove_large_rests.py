"""Create a reviewed private-use MIDI derivative with leading/large rests removed."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import mido


def absolute_messages(track: mido.MidiTrack) -> list[tuple[int, mido.Message | mido.MetaMessage]]:
    tick = 0
    result = []
    for message in track:
        tick += message.time
        result.append((tick, message))
    return result


def note_spans(track: mido.MidiTrack) -> list[tuple[int, int]]:
    active: dict[tuple[int, int], int] = {}
    spans: list[tuple[int, int]] = []
    for tick, message in absolute_messages(track):
        if message.type == "note_on" and message.velocity > 0:
            key = (message.channel, message.note)
            if key in active:
                raise ValueError(f"repeated active note at tick {tick}: {key}")
            active[key] = tick
        elif message.type == "note_off" or (
            message.type == "note_on" and message.velocity == 0
        ):
            key = (message.channel, message.note)
            start = active.pop(key, None)
            if start is None:
                raise ValueError(f"unmatched note-off at tick {tick}: {key}")
            spans.append((start, tick))
    if active:
        raise ValueError("unterminated notes")
    return sorted(spans)


def removed_before(tick: int, cuts: list[tuple[int, int]]) -> int:
    return sum(end - start for start, end in cuts if tick >= end)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--track", type=int, default=1)
    parser.add_argument("--large-gap-ticks", type=int, default=10_000)
    args = parser.parse_args()

    midi = mido.MidiFile(args.input)
    spans = note_spans(midi.tracks[args.track])
    if not spans:
        raise ValueError("selected track has no notes")
    if any(next_start < previous_end for (_, previous_end), (next_start, _) in zip(spans, spans[1:])):
        raise ValueError("selected track is not strictly monophonic")

    cuts = [(0, spans[0][0])]
    for (_, previous_end), (next_start, _) in zip(spans, spans[1:]):
        if next_start - previous_end >= args.large_gap_ticks:
            cuts.append((previous_end, next_start))

    if any(end <= start for start, end in cuts):
        raise ValueError("empty cut interval")

    output = mido.MidiFile(type=midi.type, ticks_per_beat=midi.ticks_per_beat)
    for track in midi.tracks:
        rewritten = mido.MidiTrack()
        previous_tick = 0
        for tick, message in absolute_messages(track):
            new_tick = tick - removed_before(tick, cuts)
            if new_tick < previous_tick:
                raise ValueError("timeline became non-monotonic")
            rewritten.append(message.copy(time=new_tick - previous_tick))
            previous_tick = new_tick
        output.tracks.append(rewritten)

    if args.output.exists():
        raise FileExistsError(args.output)
    output.save(args.output)
    args.report.write_text(
        json.dumps(
            {
                "input": str(args.input.resolve()),
                "output": str(args.output.resolve()),
                "track_index": args.track,
                "leading_rest_removed_ticks": spans[0][0],
                "large_gap_threshold_ticks": args.large_gap_ticks,
                "removed_intervals_ticks": [
                    {"start": start, "end": end, "duration": end - start}
                    for start, end in cuts
                ],
                "total_removed_ticks": sum(end - start for start, end in cuts),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
