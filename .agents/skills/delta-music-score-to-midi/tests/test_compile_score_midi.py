from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import mido


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "compile_score_midi.py"
SPEC = importlib.util.spec_from_file_location("compile_score_midi", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
COMPILER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMPILER
SPEC.loader.exec_module(COMPILER)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CompileScoreMidiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source = self.root / "source.png"
        self.source.write_bytes(b"synthetic-score-source-v1")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def checked_note(self, offset: str, duration: str, pitch: int, **extra):
        event = {
            "type": "note",
            "offset_beats": offset,
            "duration_beats": duration,
            "pitch": pitch,
            "review_state": "visually_checked",
        }
        event.update(extra)
        return event

    def checked_rest(self, offset: str, duration: str, **extra):
        event = {
            "type": "rest",
            "offset_beats": offset,
            "duration_beats": duration,
            "review_state": "visually_checked",
        }
        event.update(extra)
        return event

    def score(self):
        return {
            "format": "delta-reviewed-score/v1",
            "title": "Synthetic test melody",
            "source": {
                "path": self.source.name,
                "sha256": sha256(self.source),
                "document_type": "image",
            },
            "bpm": 96,
            "bpm_origin": "editorial_setting",
            "printed_tempo_text": None,
            "printed_numeric_bpm": None,
            "time_signature": {"numerator": 4, "denominator": 4},
            "ticks_per_beat": 480,
            "parts": [
                {
                    "id": "melody",
                    "measures": [
                        {
                            "id": "m1",
                            "source_ref": "page 1 / system 1 / measure 1",
                            "events": [
                                self.checked_note("0", "1", 60, slur_start=True),
                                self.checked_note("1", "1", 62, slur_end=True),
                                self.checked_rest("2", "2"),
                            ],
                        },
                        {
                            "id": "m2",
                            "source_ref": "page 1 / system 1 / measure 2",
                            "events": [
                                self.checked_note("0", "1", 64, tie_out=True),
                                self.checked_note("1", "1", 64, tie_in=True),
                                self.checked_note("2", "1", 65),
                                self.checked_rest("3", "1"),
                            ],
                        },
                    ],
                }
            ],
            "performance_route": [
                {"part_id": "melody", "measure_id": "m1"},
                {"part_id": "melody", "measure_id": "m2"},
            ],
        }

    def write_ir(self, score=None) -> Path:
        path = self.root / "reviewed_score.json"
        path.write_text(
            json.dumps(self.score() if score is None else score, indent=2),
            encoding="utf-8",
        )
        return path

    def compile(self, score=None):
        ir = self.write_ir(score)
        output = self.root / "melody_only.mid"
        report = self.root / "compile_report.json"
        result = COMPILER.compile_score(ir, output, report)
        return output, report, result

    def absolute_note_events(self, midi_path: Path):
        midi = mido.MidiFile(str(midi_path))
        track = next(
            track
            for track in midi.tracks
            if any(
                message.type == "track_name" and message.name == "melody_only"
                for message in track
            )
        )
        tick = 0
        events = []
        for message in track:
            tick += int(message.time)
            if message.type in {"note_on", "note_off"}:
                events.append((tick, message.type, message.note, message.velocity))
        return events

    def test_valid_compile_merges_only_explicit_tie_and_writes_hash_report(self):
        output, report_path, report = self.compile()
        self.assertTrue(output.is_file())
        self.assertTrue(report_path.is_file())
        self.assertEqual(report["report_format"], "delta-reviewed-score-compile/v1")
        self.assertTrue(report["source"]["hash_verified"])
        self.assertEqual(report["output_sha256"], sha256(output))
        self.assertEqual(report["performance_route"]["total_quarter_beats"], "8")
        self.assertEqual(report["performance_route"]["total_ticks"], 3840)
        self.assertEqual(report["validation"]["source_note_event_count"], 5)
        self.assertEqual(report["validation"]["note_count"], 4)
        self.assertEqual(report["validation"]["tie_groups_merged"], 1)
        onsets = [event for event in self.absolute_note_events(output) if event[1] == "note_on"]
        self.assertEqual([(tick, pitch) for tick, _, pitch, _ in onsets], [(0, 60), (480, 62), (1920, 64), (2880, 65)])
        with self.assertRaises(FileExistsError):
            COMPILER.compile_score(self.root / "reviewed_score.json", output, report_path)

    def test_rejects_measure_with_wrong_beat_coverage(self):
        score = self.score()
        score["parts"][0]["measures"][0]["events"][-1]["duration_beats"] = "1"
        with self.assertRaisesRegex(ValueError, "covers 3 quarter beats"):
            self.compile(score)

    def test_rejects_measure_without_source_reference(self):
        score = self.score()
        del score["parts"][0]["measures"][0]["source_ref"]
        with self.assertRaisesRegex(ValueError, "source_ref"):
            self.compile(score)

    def test_rejects_unreviewed_event_even_outside_the_route(self):
        score = self.score()
        score["performance_route"] = [{"part_id": "melody", "measure_id": "m1"}]
        score["parts"][0]["measures"][1]["events"][0]["review_state"] = "machine_draft"
        with self.assertRaisesRegex(ValueError, "visually_checked"):
            self.compile(score)

    def test_rejects_wrong_pitch_tie(self):
        score = self.score()
        score["parts"][0]["measures"][1]["events"][1]["pitch"] = 67
        with self.assertRaisesRegex(ValueError, "Invalid tie_out"):
            self.compile(score)

    def test_rejects_unknown_route_reference(self):
        score = self.score()
        score["performance_route"][1]["measure_id"] = "missing"
        with self.assertRaisesRegex(ValueError, "references unknown measure"):
            self.compile(score)

    def test_rejects_duplicate_part_id_even_with_distinct_measure_ids(self):
        score = self.score()
        score["parts"].append(
            {
                "id": "melody",
                "measures": [
                    {
                        "id": "different",
                        "events": [self.checked_rest("0", "4")],
                    }
                ],
            }
        )
        with self.assertRaisesRegex(ValueError, "Duplicate part id"):
            self.compile(score)

    def test_roundtrip_preserves_fractional_timing_and_slur_does_not_merge(self):
        score = self.score()
        score["time_signature"] = {"numerator": 6, "denominator": 8}
        score["parts"] = [
            {
                "id": "melody",
                "measures": [
                    {
                        "id": "m1",
                        "source_ref": "page 1 / system 1 / measure 1",
                        "events": [
                            self.checked_note("0", "1/2", 60, slur_start=True),
                            self.checked_note("1/2", "1/2", 60, slur_end=True),
                            self.checked_rest("1", "1/2"),
                            self.checked_note("3/2", "3/2", 67),
                        ],
                    }
                ],
            }
        ]
        score["performance_route"] = [{"part_id": "melody", "measure_id": "m1"}]
        output, _, report = self.compile(score)
        events = self.absolute_note_events(output)
        note_on = [event for event in events if event[1] == "note_on"]
        self.assertEqual([(tick, pitch) for tick, _, pitch, _ in note_on], [(0, 60), (240, 60), (720, 67)])
        same_tick = [event[1] for event in events if event[0] == 240]
        self.assertEqual(same_tick, ["note_off", "note_on"])
        self.assertEqual(report["performance_route"]["total_ticks"], 1440)
        self.assertTrue(report["validation"]["roundtrip_verified"])

    def test_rejects_source_hash_mismatch_without_outputs(self):
        score = self.score()
        score["source"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            self.compile(score)
        self.assertFalse((self.root / "melody_only.mid").exists())
        self.assertFalse((self.root / "compile_report.json").exists())

    def test_rejects_changed_ir_during_compilation_without_outputs(self):
        ir = self.write_ir()
        output = self.root / "melody_only.mid"
        report = self.root / "compile_report.json"
        original_build_midi = COMPILER._build_midi

        def mutate_ir_after_validation(score, notes, total_ticks):
            midi = original_build_midi(score, notes, total_ticks)
            ir.write_text('{"changed": true}\n', encoding="utf-8")
            return midi

        with patch.object(COMPILER, "_build_midi", side_effect=mutate_ir_after_validation):
            with self.assertRaisesRegex(RuntimeError, "changed during compilation"):
                COMPILER.compile_score(ir, output, report)
        self.assertFalse(output.exists())
        self.assertFalse(report.exists())

    def test_printed_bpm_origin_requires_matching_printed_numeric_value(self):
        score = self.score()
        score["bpm_origin"] = "printed_score"
        score["printed_numeric_bpm"] = 120
        with self.assertRaisesRegex(ValueError, "must equal printed_numeric_bpm"):
            self.compile(score)


if __name__ == "__main__":
    unittest.main()
