"""Create a reviewable melody-layer candidate from the supplied piano MIDI.

This is deliberately song-specific: it selects the salient velocity layer
(velocity >= 93) found during the MIDI audit.  It does not claim to identify a
hand or recover an original isolated vocal track.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path

import mido


def collect_notes(midi: mido.MidiFile, minimum_velocity: int):
    active: dict[tuple[int, int], list[tuple[int, int]]] = collections.defaultdict(list)
    selected: list[tuple[int, int, int, int, int]] = []
    tick = 0
    for message in mido.merge_tracks(midi.tracks):
        tick += message.time
        if message.type == "note_on" and message.velocity > 0:
            active[(message.channel, message.note)].append((tick, message.velocity))
        elif message.type == "note_off" or (
            message.type == "note_on" and message.velocity == 0
        ):
            key = (message.channel, message.note)
            if not active[key]:
                continue
            onset, velocity = active[key].pop(0)
            if velocity >= minimum_velocity:
                selected.append((onset, tick, message.channel, message.note, velocity))
    return selected


def collect_global_meta(midi: mido.MidiFile):
    supported = {"set_tempo", "time_signature", "key_signature"}
    entries = []
    for track_index, track in enumerate(midi.tracks):
        tick = 0
        for order, message in enumerate(track):
            tick += message.time
            if message.type in supported:
                entries.append((tick, track_index, order, message.copy(time=0)))
    return sorted(entries, key=lambda item: item[:3])


def write_candidate(source: Path, destination: Path, report: Path, minimum_velocity: int):
    source_midi = mido.MidiFile(source)
    notes = collect_notes(source_midi, minimum_velocity)
    if not notes:
        raise ValueError("No notes match the selected velocity layer.")

    output = mido.MidiFile(type=1, ticks_per_beat=source_midi.ticks_per_beat)
    conductor = mido.MidiTrack()
    conductor.append(mido.MetaMessage("track_name", name="Conductor", time=0))
    last_tick = 0
    for tick, _, _, message in collect_global_meta(source_midi):
        conductor.append(message.copy(time=tick - last_tick))
        last_tick = tick
    conductor.append(mido.MetaMessage("end_of_track", time=0))
    output.tracks.append(conductor)

    melody = mido.MidiTrack()
    melody.append(
        mido.MetaMessage(
            "track_name", name=f"Velocity >= {minimum_velocity} melody candidate", time=0
        )
    )
    events = []
    for onset, end, channel, note, velocity in notes:
        events.append((onset, 1, mido.Message("note_on", channel=channel, note=note, velocity=velocity, time=0)))
        events.append((end, 0, mido.Message("note_off", channel=channel, note=note, velocity=0, time=0)))
    events.sort(key=lambda event: (event[0], event[1], event[2].note))
    last_tick = 0
    for tick, _, message in events:
        melody.append(message.copy(time=tick - last_tick))
        last_tick = tick
    melody.append(mido.MetaMessage("end_of_track", time=0))
    output.tracks.append(melody)
    output.save(destination)

    report_data = {
        "source_file": str(source),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "selection": {
            "kind": "song-specific velocity-layer candidate",
            "minimum_note_on_velocity": minimum_velocity,
            "rationale": "The selected layer was nearly monophonic in the supplied MIDI; it is a private single-line arrangement candidate, not a verified hand/voice separation.",
        },
        "selected_note_count": len(notes),
        "selected_pitch_range": [min(note[3] for note in notes), max(note[3] for note in notes)],
        "output_file": str(destination),
    }
    report.write_text(json.dumps(report_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--minimum-velocity", type=int, default=93)
    args = parser.parse_args()
    if args.destination.exists() or args.report.exists():
        raise FileExistsError("Refusing to overwrite an existing derived artifact.")
    write_candidate(args.source, args.destination, args.report, args.minimum_velocity)


if __name__ == "__main__":
    main()
