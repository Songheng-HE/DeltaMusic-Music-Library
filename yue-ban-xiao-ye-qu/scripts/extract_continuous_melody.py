"""Create a strict-monophonic hand-off arrangement from a Type 0 MIDI."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from pathlib import Path

import mido


STATE_TYPES = {"control_change", "program_change", "pitchwheel", "aftertouch", "polytouch"}


def state_key(message: mido.Message) -> tuple[object, ...] | None:
    if message.type not in STATE_TYPES:
        return None
    if message.type == "control_change":
        return (message.type, message.control)
    if message.type == "polytouch":
        return (message.type, message.note)
    return (message.type,)


def absolute_events(track: mido.MidiTrack) -> tuple[list[tuple[int, int, mido.Message]], int]:
    tick = 0
    result = []
    for order, message in enumerate(track):
        tick += message.time
        result.append((tick, order, message))
    return result, tick


def matched_notes(events: list[tuple[int, int, mido.Message]]) -> list[tuple[int, int, int, int, int]]:
    active: dict[tuple[int, int], deque[tuple[int, int]]] = defaultdict(deque)
    notes = []
    for tick, _order, message in events:
        if message.type == "note_on" and message.velocity > 0:
            active[(message.channel, message.note)].append((tick, message.velocity))
        elif message.type in {"note_off", "note_on"}:
            key = (message.channel, message.note)
            if active[key]:
                start, velocity = active[key].popleft()
                notes.append((message.channel, message.note, start, tick, velocity))
    return notes


def remap_channel(message: mido.Message) -> mido.Message:
    return message.copy(channel=0, time=0)


def state_before(
    events: list[tuple[int, int, mido.Message]], channel: int, tick_limit: int
) -> list[mido.Message]:
    state: dict[tuple[object, ...], tuple[int, int, mido.Message]] = {}
    for tick, order, message in events:
        if tick >= tick_limit:
            break
        if message.is_meta or not hasattr(message, "channel") or message.channel != channel:
            continue
        key = state_key(message)
        if key is not None:
            state[key] = (tick, order, message)
    return [remap_channel(item[2]) for item in sorted(state.values(), key=lambda item: item[:2])]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--lead-channel", type=int, default=0)
    parser.add_argument("--handoff-channel", type=int, default=1)
    parser.add_argument("--handoff-tick", type=int, required=True)
    parser.add_argument("--insert-channel", type=int)
    parser.add_argument("--insert-start-tick", type=int)
    parser.add_argument("--insert-end-tick", type=int)
    parser.add_argument("--trim-leading", action="store_true")
    parser.add_argument("--interlude-rest-ticks", type=int)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"refusing to overwrite existing output: {args.output}")

    source = mido.MidiFile(args.source)
    if source.type != 0 or len(source.tracks) != 1:
        parser.error("this utility requires a one-track Type 0 input")
    insert_arguments = (args.insert_channel, args.insert_start_tick, args.insert_end_tick)
    if any(value is not None for value in insert_arguments) and any(value is None for value in insert_arguments):
        parser.error("the insert channel, start tick, and end tick must be supplied together")
    if args.insert_start_tick is not None and args.insert_start_tick >= args.insert_end_tick:
        parser.error("the insert range must have a positive duration")
    if args.interlude_rest_ticks is not None and args.insert_channel is None:
        parser.error("an interlude rest can only be shortened when an insert range is selected")
    if args.interlude_rest_ticks is not None and args.interlude_rest_ticks < 0:
        parser.error("the replacement rest cannot be negative")
    events, _total_ticks = absolute_events(source.tracks[0])
    notes = matched_notes(events)

    selected = []
    for channel, pitch, start, end, velocity in notes:
        if channel == args.lead_channel and start < args.handoff_tick:
            selected.append((pitch, start, min(end, args.handoff_tick), velocity))
        elif channel == args.handoff_channel and start >= args.handoff_tick and not (
            args.insert_start_tick is not None and args.insert_start_tick <= start < args.insert_end_tick
        ):
            selected.append((pitch, start, end, velocity))
        elif (
            channel == args.insert_channel
            and args.insert_start_tick is not None
            and args.insert_start_tick <= start < args.insert_end_tick
        ):
            selected.append((pitch, start, end, velocity))
    selected.sort(key=lambda note: (note[1], note[0]))
    if not selected:
        parser.error("no notes matched the requested hand-off")

    normalized = []
    for index, (pitch, start, end, velocity) in enumerate(selected):
        if index + 1 < len(selected):
            end = min(end, selected[index + 1][1])
        if end > start:
            normalized.append((pitch, start, end, velocity))

    emitted: list[tuple[int, int, mido.Message]] = []
    serial = 0

    def emit(tick: int, message: mido.Message) -> None:
        nonlocal serial
        emitted.append((tick, serial, message.copy(time=0)))
        serial += 1

    # Preserve global timing/notation metadata. There are no later tempo changes
    # in this source, but keeping such events makes the output self-describing.
    for tick, _order, message in events:
        if message.type in {"track_name", "set_tempo", "time_signature", "key_signature"}:
            emit(tick, message)

    # Carry the first lead's expressive messages through its phrase.
    for tick, _order, message in events:
        if tick >= args.handoff_tick:
            break
        if not message.is_meta and hasattr(message, "channel") and message.channel == args.lead_channel:
            if message.type not in {"note_on", "note_off"}:
                emit(tick, remap_channel(message))

    # Restore the incoming part's state at the hand-off (not its earlier timing),
    # then carry later expression and program changes on one output channel.
    for message in state_before(events, args.handoff_channel, args.handoff_tick):
        emit(args.handoff_tick, message)
    for tick, _order, message in events:
        if tick < args.handoff_tick:
            continue
        if not message.is_meta and hasattr(message, "channel") and message.channel == args.handoff_channel:
            if message.type not in {"note_on", "note_off"}:
                emit(tick, remap_channel(message))

    if args.insert_channel is not None:
        for message in state_before(events, args.insert_channel, args.insert_start_tick):
            emit(args.insert_start_tick, message)
        for tick, _order, message in events:
            if tick < args.insert_start_tick:
                continue
            if tick >= args.insert_end_tick:
                break
            if not message.is_meta and hasattr(message, "channel") and message.channel == args.insert_channel:
                if message.type not in {"note_on", "note_off"}:
                    emit(tick, remap_channel(message))

        resumed = [start for pitch, start, end, velocity in selected if start >= args.insert_end_tick]
        if resumed:
            for message in state_before(events, args.handoff_channel, min(resumed)):
                emit(min(resumed), message)

    for pitch, start, end, velocity in normalized:
        emit(start, mido.Message("note_on", channel=0, note=pitch, velocity=velocity))
        emit(end, mido.Message("note_off", channel=0, note=pitch, velocity=0))

    source_end_tick = max(note[2] for note in normalized)
    emit(source_end_tick, mido.Message("control_change", channel=0, control=123, value=0))
    offset = min(note[1] for note in normalized) if args.trim_leading else 0
    removed_gap_ticks = 0
    if args.interlude_rest_ticks is not None:
        inserted_ends = [
            end
            for channel, pitch, start, end, velocity in notes
            if channel == args.insert_channel and args.insert_start_tick <= start < args.insert_end_tick
        ]
        resumed_starts = [
            start
            for channel, pitch, start, end, velocity in notes
            if channel == args.handoff_channel and start >= args.insert_end_tick
        ]
        if not inserted_ends or not resumed_starts:
            parser.error("could not identify both sides of the requested interlude rest")
        gap_start = max(inserted_ends)
        resume_start = min(resumed_starts)
        removed_gap_ticks = resume_start - gap_start - args.interlude_rest_ticks
        if removed_gap_ticks < 0:
            parser.error("the requested replacement rest is longer than the existing rest")
        compressed = []
        for tick, serial, message in emitted:
            if gap_start < tick < resume_start:
                compressed.append((gap_start + args.interlude_rest_ticks, serial, message))
            elif tick >= resume_start:
                compressed.append((tick - removed_gap_ticks, serial, message))
            else:
                compressed.append((tick, serial, message))
        emitted = compressed
    end_tick = source_end_tick - offset - removed_gap_ticks

    output = mido.MidiFile(type=0, ticks_per_beat=source.ticks_per_beat)
    track = mido.MidiTrack()
    output.tracks.append(track)
    previous_tick = 0
    for tick, _serial, message in sorted(emitted, key=lambda item: (item[0], item[1])):
        output_tick = max(0, tick - offset)
        track.append(message.copy(time=output_tick - previous_tick))
        previous_tick = output_tick
    track.append(mido.MetaMessage("end_of_track", time=end_tick - previous_tick))
    output.save(args.output)
    print(
        f"Wrote {args.output}; {len(normalized)} strict-monophonic notes; "
        f"handoff at tick {args.handoff_tick}; leading trim {offset} ticks; "
        f"removed interlude gap {removed_gap_ticks} ticks."
    )


if __name__ == "__main__":
    main()
