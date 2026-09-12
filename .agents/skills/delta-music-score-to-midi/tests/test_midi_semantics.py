from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import mido


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "midi_tools.py"
SPEC = importlib.util.spec_from_file_location("delta_midi_tools", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
midi_tools = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = midi_tools
SPEC.loader.exec_module(midi_tools)


class StructurePolicyTests(unittest.TestCase):
    def test_staggered_bass_can_pass_strict_mono_after_naive_reduction(self) -> None:
        notes = [
            midi_tools.Note(start=0, end=300, pitch=65, velocity=90, channel=0),
            midi_tools.Note(start=150, end=300, pitch=46, velocity=75, channel=1),
            midi_tools.Note(start=300, end=450, pitch=65, velocity=90, channel=0),
        ]

        reduced = midi_tools.reduce_same_onset(notes, "highest", "truncate")

        self.assertEqual(
            [(note.start, note.end, note.pitch) for note in reduced],
            [(0, 150, 65), (150, 300, 46), (300, 450, 65)],
        )
        self.assertEqual(midi_tools.overlap_metrics(reduced), (1, 0, 1))

    def test_lossy_policy_requires_explicit_structure_class(self) -> None:
        with self.assertRaisesRegex(ValueError, "--structure-class"):
            midi_tools.validate_structure_policy(None, "highest", "reject")
        with self.assertRaisesRegex(ValueError, "--structure-class"):
            midi_tools.validate_structure_policy(None, "reject", "truncate")

    def test_mixed_and_polyphonic_classes_refuse_lossy_reduction(self) -> None:
        for structure_class in (
            "mixed-melody-accompaniment",
            "imitative-polyphony",
            "chordal-texture",
            "unknown",
        ):
            with self.subTest(structure_class=structure_class):
                with self.assertRaisesRegex(ValueError, "does not permit"):
                    midi_tools.validate_structure_policy(
                        structure_class, "highest", "truncate"
                    )

    def test_safe_classes_and_default_reject_route_remain_available(self) -> None:
        for structure_class in (
            "isolated-melody",
            "karaoke-guide",
            "independent-melodic-part",
        ):
            with self.subTest(structure_class=structure_class):
                midi_tools.validate_structure_policy(
                    structure_class, "highest", "truncate"
                )

        midi_tools.validate_structure_policy(None, "reject", "reject")
        midi_tools.validate_structure_policy(
            "mixed-melody-accompaniment", "reject", "reject"
        )

    def test_onset_reconstruction_requires_karaoke_guide(self) -> None:
        with self.assertRaisesRegex(ValueError, "karaoke-guide"):
            midi_tools.validate_structure_policy(
                None, "reject", "reject", duration_mode="onset"
            )
        with self.assertRaisesRegex(ValueError, "karaoke-guide"):
            midi_tools.validate_structure_policy(
                "isolated-melody", "reject", "reject", duration_mode="onset"
            )
        midi_tools.validate_structure_policy(
            "karaoke-guide", "reject", "reject", duration_mode="onset"
        )

    def test_leading_rest_trim_requires_safe_non_independent_structure(self) -> None:
        for structure_class in (
            None,
            "independent-melodic-part",
            "mixed-melody-accompaniment",
            "imitative-polyphony",
            "unknown",
        ):
            with self.subTest(structure_class=structure_class):
                with self.assertRaisesRegex(ValueError, "time origin"):
                    midi_tools.validate_structure_policy(
                        structure_class,
                        "reject",
                        "reject",
                        trim_leading_rest=True,
                    )
        for structure_class in ("isolated-melody", "karaoke-guide"):
            midi_tools.validate_structure_policy(
                structure_class,
                "reject",
                "reject",
                trim_leading_rest=True,
            )

    def test_extraction_report_records_structure_and_preserves_leading_rest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_path = root / "synthetic.mid"
            output_path = root / "melody.mid"
            report_path = root / "report.json"

            source = mido.MidiFile(type=1, ticks_per_beat=480)
            conductor = source.add_track("conductor")
            conductor.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
            melody = source.add_track("Lead")
            melody.append(
                mido.Message("note_on", note=60, velocity=90, channel=0, time=480)
            )
            melody.append(
                mido.Message("note_on", note=64, velocity=70, channel=0, time=0)
            )
            melody.append(
                mido.Message("note_off", note=64, velocity=0, channel=0, time=240)
            )
            melody.append(
                mido.Message("note_off", note=60, velocity=0, channel=0, time=240)
            )
            source.save(source_path)

            args = argparse.Namespace(
                input=source_path,
                output=output_path,
                track="Lead",
                same_onset="highest",
                overlaps="reject",
                structure_class="isolated-melody",
                duration_mode="source",
                onset_gate=0.88,
                long_gap_beats=2.0,
                long_gap_hold_beats=1.0,
                trim_leading_rest=False,
                report=report_path,
                force=False,
            )

            self.assertEqual(midi_tools.run_extract(args), 0)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["structure_class"], "isolated-melody")
            self.assertEqual(report["source_sha256"], midi_tools.file_sha256(source_path))
            self.assertEqual(report["output_melody"]["first_onset_tick"], 480)


if __name__ == "__main__":
    unittest.main()
