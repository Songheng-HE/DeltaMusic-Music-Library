"""Create a tiny original MIDI fixture for local end-to-end testing.

The note sequence is intentionally synthetic and is not transcribed from any song.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import mido


def build_demo(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    midi = mido.MidiFile(type=1, ticks_per_beat=480)

    conductor = mido.MidiTrack()
    conductor.append(mido.MetaMessage("track_name", name="Synthetic Demo Conductor", time=0))
    conductor.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(96), time=0))
    conductor.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
    conductor.append(mido.MetaMessage("end_of_track", time=0))
    midi.tracks.append(conductor)

    melody = mido.MidiTrack()
    melody.append(mido.MetaMessage("track_name", name="Demo Melody", time=0))
    melody.append(mido.Message("program_change", channel=0, program=0, time=0))
    # Original test phrase: an ascending/descending scale with two explicit rests.
    phrase: list[int | None] = [60, 62, 64, 67, None, 69, 67, 64, 62, None, 60]
    pending = 0
    for note in phrase:
        if note is None:
            pending += 480
            continue
        melody.append(mido.Message("note_on", note=note, velocity=80, channel=0, time=pending))
        melody.append(mido.Message("note_off", note=note, velocity=0, channel=0, time=360))
        pending = 120
    melody.append(mido.MetaMessage("end_of_track", time=pending))
    midi.tracks.append(melody)
    midi.save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an original synthetic MIDI test input.")
    parser.add_argument("output", type=Path, help="Where to write the .mid file")
    args = parser.parse_args()
    build_demo(args.output)
    print(f"Created synthetic MIDI: {args.output}")


if __name__ == "__main__":
    main()
