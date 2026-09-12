"""Create a MIDI copy with every tempo event multiplied by a chosen factor."""

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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--factor", type=float, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.factor <= 0:
        raise SystemExit("factor must be positive")
    if args.output.exists() or args.report.exists():
        raise SystemExit("refusing to overwrite an existing output or report")

    source = mido.MidiFile(args.input)
    output = mido.MidiFile(type=source.type, ticks_per_beat=source.ticks_per_beat)
    changes: list[dict[str, float | int]] = []
    for track in source.tracks:
        replacement = mido.MidiTrack()
        tick = 0
        for message in track:
            tick += message.time
            if message.type == "set_tempo":
                new_tempo = round(message.tempo / args.factor)
                changes.append(
                    {
                        "tick": tick,
                        "old_microseconds_per_beat": message.tempo,
                        "new_microseconds_per_beat": new_tempo,
                        "old_bpm": mido.tempo2bpm(message.tempo),
                        "new_bpm": mido.tempo2bpm(new_tempo),
                    }
                )
                replacement.append(message.copy(tempo=new_tempo))
            else:
                replacement.append(message.copy())
        output.tracks.append(replacement)
    if not changes:
        raise SystemExit("input contains no explicit tempo event")

    output.save(args.output)
    args.report.write_text(
        json.dumps(
            {
                "operation": "scale-tempo/v1",
                "input_file": str(args.input.resolve()),
                "input_sha256": sha256(args.input),
                "output_file": str(args.output.resolve()),
                "output_sha256": sha256(args.output),
                "speed_factor": args.factor,
                "tempo_changes": changes,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
