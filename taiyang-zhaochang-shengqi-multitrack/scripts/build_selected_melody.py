"""Build the user-approved single-line arrangement from reviewed source parts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / ".agents" / "skills" / "delta-music-score-to-midi" / "scripts"))

import mido  # noqa: E402
from midi_tools import (  # noqa: E402
    audit_midi,
    parse_track_notes,
    reduce_same_onset,
    write_melody_midi,
)


TICKS_PER_QUARTER = 480
ROUTE = {
    "A_trombone": {"track": 1, "start": 480, "end": 33120},
    "B_strings": {"track": 4, "start": 38880, "end": 88794},
    "C_cello": {"track": 6, "start": 88800, "end": 129840},
    "D_flute": {"track": 7, "start": 129840, "end": None},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def range_notes(notes, start: int, end: int | None):
    return [
        note
        for note in notes
        if note.start >= start and (end is None or note.end <= end)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    if args.output.exists() or args.report.exists():
        raise FileExistsError("Refusing to overwrite a reviewed derived artifact.")

    source = mido.MidiFile(args.source)
    if source.ticks_per_beat != TICKS_PER_QUARTER:
        raise ValueError(f"Expected PPQ {TICKS_PER_QUARTER}, got {source.ticks_per_beat}.")

    track_notes = [parse_track_notes(track)[0] for track in source.tracks]

    # A: prior to its later change into a two-note accompaniment texture.
    trombone = range_notes(
        track_notes[1], ROUTE["A_trombone"]["start"], ROUTE["A_trombone"]["end"]
    )

    # B: known foreground string passage. Only its same-onset octave doublings
    # are reduced, retaining the upper voice. Remaining notes are already single.
    strings_raw = range_notes(
        track_notes[4], ROUTE["B_strings"]["start"], ROUTE["B_strings"]["end"]
    )
    strings = reduce_same_onset(strings_raw, same_onset="highest", overlaps="reject")

    # C/D: user selected the flute-led ending. The final cello C4 starts at
    # 129120 and naturally ends at 130560; it is intentionally shortened to the
    # flute's first onset at 129840, preventing overlap in the new arrangement.
    cello = [
        replace(note, end=min(note.end, ROUTE["C_cello"]["end"]))
        for note in track_notes[6]
        if ROUTE["C_cello"]["start"] <= note.start < ROUTE["C_cello"]["end"]
    ]
    flute = range_notes(
        track_notes[7], ROUTE["D_flute"]["start"], ROUTE["D_flute"]["end"]
    )

    selected = sorted(trombone + strings + cello + flute, key=lambda note: (note.start, note.end, note.pitch))
    if not selected:
        raise ValueError("No notes selected.")
    for prior, current in zip(selected, selected[1:]):
        if prior.end > current.start:
            raise ValueError(
                f"Route overlaps at ticks {prior.start}-{prior.end} and {current.start}-{current.end}."
            )

    write_melody_midi(source, selected, args.output, trim_ticks=0)
    output_audit = audit_midi(args.output)
    melody_track = output_audit["tracks"][1]
    if melody_track["max_simultaneous_notes"] != 1 or melody_track["overlapping_note_count"] != 0:
        raise ValueError("Generated output is not strictly monophonic.")

    report = {
        "report_format": "delta-single-line-arrangement/v1",
        "source_file": str(args.source.resolve()),
        "source_sha256": sha256(args.source),
        "output_file": str(args.output.resolve()),
        "output_sha256": sha256(args.output),
        "intended_use": "private",
        "rights_status": "unknown",
        "arrangement_label": "single-line arrangement; not a recovered existing source track",
        "user_selected_ending": "option 2: flute-led ending",
        "route": [
            {"source_track": 1, "instrument": "Trombone", "start_tick": 480, "end_tick": 33117, "operation": "direct selection"},
            {"source_track": 4, "instrument": "String Ensemble 2", "start_tick": 38880, "end_tick": 88794, "operation": "select highest note only at same-onset octave doublings"},
            {"source_track": 6, "instrument": "Cello", "start_tick": 88800, "end_tick": 129840, "operation": "shorten final C4 from tick 130560 to the flute hand-off"},
            {"source_track": 7, "instrument": "Flute", "start_tick": 129840, "end_tick": 134880, "operation": "direct selection"},
        ],
        "selection_counts": {
            "trombone": len(trombone),
            "strings_before_octave_reduction": len(strings_raw),
            "strings_after_octave_reduction": len(strings),
            "cello": len(cello),
            "flute": len(flute),
            "total": len(selected),
        },
        "output_audit": melody_track,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} with {len(selected)} notes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
