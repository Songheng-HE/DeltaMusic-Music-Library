"""Create a private-use MIDI edit: halve first-half rests and drop the last note."""

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


def map_tick(tick: int, deletions: list[tuple[int, int]]) -> int:
    removed = 0
    for start, end in deletions:
        if tick >= end:
            removed += end - start
        elif tick > start:
            return start - removed
        else:
            break
    return tick - removed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--track", type=int, default=1)
    args = parser.parse_args()

    midi = mido.MidiFile(args.input)
    spans = note_spans(midi.tracks[args.track])
    if len(spans) < 2:
        raise ValueError("at least two notes are required")
    if any(next_start < previous_end for (_, previous_end), (next_start, _) in zip(spans, spans[1:])):
        raise ValueError("selected track is not strictly monophonic")

    full_end = spans[-1][1]
    first_half_end = full_end / 2
    rests = [
        (previous_end, next_start)
        for (_, previous_end), (next_start, _) in zip(spans, spans[1:])
        if next_start > previous_end and next_start <= first_half_end
    ]
    if any((end - start) % 2 for start, end in rests):
        raise ValueError("a selected rest cannot be halved exactly in ticks")

    # Keep the first half of each selected rest and remove its second half.
    deletions = [(start + (end - start) // 2, end) for start, end in rests]
    source_cutoff = spans[-2][1]
    output_cutoff = map_tick(source_cutoff, deletions)

    output = mido.MidiFile(type=midi.type, ticks_per_beat=midi.ticks_per_beat)
    for track in midi.tracks:
        rewritten = mido.MidiTrack()
        previous_tick = 0
        for tick, message in absolute_messages(track):
            if tick > source_cutoff or message.type == "end_of_track":
                continue
            new_tick = map_tick(tick, deletions)
            if new_tick < previous_tick:
                raise ValueError("timeline became non-monotonic")
            rewritten.append(message.copy(time=new_tick - previous_tick))
            previous_tick = new_tick
        rewritten.append(mido.MetaMessage("end_of_track", time=output_cutoff - previous_tick))
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
                "selection": "positive rests wholly ending in the source time-line first half",
                "source_first_half_end_tick": first_half_end,
                "rests_halved_ticks": [
                    {"start": start, "end": end, "original_duration": end - start,
                     "new_duration": (end - start) // 2}
                    for start, end in rests
                ],
                "total_rest_ticks_removed": sum(end - start for start, end in deletions),
                "removed_final_note_span_ticks": {
                    "start": spans[-1][0], "end": spans[-1][1]
                },
                "timeline_truncated_after_source_tick": source_cutoff,
                "output_end_tick": output_cutoff,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
