"""Write a MIDI copy ending at its last actual note without changing note data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / ".agents" / "skills" / "delta-music-score-to-midi" / "scripts"))

import mido  # noqa: E402
from midi_tools import absolute_messages, append_absolute_messages, parse_track_notes  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Refusing to overwrite an existing derived MIDI.")

    source = mido.MidiFile(args.source)
    last_note_tick = max(
        (note.end for track in source.tracks for note in parse_track_notes(track)[0]),
        default=0,
    )
    if not last_note_tick:
        raise ValueError("Source contains no complete notes.")

    result = mido.MidiFile(type=source.type, ticks_per_beat=source.ticks_per_beat)
    for source_track in source.tracks:
        target_track = result.add_track(source_track.name)
        events = [
            (tick, order, message.copy(time=0))
            for tick, order, message in absolute_messages(source_track)
            if tick <= last_note_tick and message.type != "end_of_track"
        ]
        append_absolute_messages(target_track, events)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output)
    print(f"Trimmed silent tail at tick {last_note_tick}: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
