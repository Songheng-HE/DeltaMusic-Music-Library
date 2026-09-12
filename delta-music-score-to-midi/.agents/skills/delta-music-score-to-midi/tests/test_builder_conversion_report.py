from __future__ import annotations

import hashlib
import io
import json
import runpy
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import mido  # noqa: E402
import build_delta_player as builder  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BuilderConversionReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.melody = self.root / "melody.mid"
        self.player = self.root / "player.py"
        self.manifest = self.root / "manifest.json"
        self.audit = self.root / "audit.json"
        self.conversion = self.root / "conversion.json"
        self.extraction = self.root / "extraction.json"
        self.source = self.root / "source.pdf"
        self.score_ir = self.root / "reviewed_score.json"

        self._write_melody()
        self.source.write_bytes(b"synthetic score evidence")
        self._write_json(
            self.score_ir,
            {
                "format": "delta-reviewed-score/v1",
                "title": "Synthetic builder evidence",
                "source": {
                    "path": self.source.name,
                    "sha256": sha256(self.source),
                    "document_type": "pdf",
                },
                "bpm": 120,
                "bpm_origin": "printed_score",
                "printed_tempo_text": "quarter note = 120",
                "printed_numeric_bpm": 120,
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
                                    {
                                        "type": "note",
                                        "offset_beats": "0",
                                        "duration_beats": "1",
                                        "pitch": 60,
                                        "review_state": "visually_checked",
                                    },
                                    {
                                        "type": "note",
                                        "offset_beats": "1",
                                        "duration_beats": "1",
                                        "pitch": 64,
                                        "review_state": "visually_checked",
                                    },
                                    {
                                        "type": "rest",
                                        "offset_beats": "2",
                                        "duration_beats": "2",
                                        "review_state": "visually_checked",
                                    },
                                ],
                            }
                        ],
                    }
                ],
                "performance_route": [{"part_id": "melody", "measure_id": "m1"}],
            },
        )
        self._write_json(
            self.audit,
            {
                "source_file": str(self.melody),
                "source_sha256": sha256(self.melody),
                "tracks": [
                    {
                        "track_index": 0,
                        "track_name": "melody_only",
                        "strictly_monophonic": True,
                    }
                ],
            },
        )
        self._write_conversion_report()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _write_melody(self) -> None:
        midi = mido.MidiFile(ticks_per_beat=480)
        track = mido.MidiTrack()
        midi.tracks.append(track)
        track.append(mido.MetaMessage("track_name", name="melody_only", time=0))
        track.append(mido.MetaMessage("set_tempo", tempo=500_000, time=0))
        track.append(mido.Message("note_on", note=60, velocity=80, time=0))
        track.append(mido.Message("note_off", note=60, velocity=0, time=480))
        track.append(mido.Message("note_on", note=64, velocity=80, time=0))
        track.append(mido.Message("note_off", note=64, velocity=0, time=480))
        midi.save(self.melody)

    @staticmethod
    def _write_json(path: Path, value: dict[str, object]) -> None:
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def _write_conversion_report(self, *, output_sha256: str | None = None) -> None:
        self._write_json(
            self.conversion,
            {
                "report_format": "delta-reviewed-score-compile/v1",
                "score_ir": {"path": str(self.score_ir), "sha256": sha256(self.score_ir)},
                "source": {
                    "path": str(self.source),
                    "document_type": "pdf",
                    "expected_sha256": sha256(self.source),
                    "verified_sha256": sha256(self.source),
                    "hash_verified": True,
                },
                "output_file": str(self.melody),
                "output_sha256": output_sha256 or sha256(self.melody),
                "settings": {
                    "ticks_per_beat": 480,
                    "bpm": 120,
                    "playback_bpm": 120,
                    "playback_bpm_origin": "printed_score",
                    "printed_tempo_text": "quarter note = 120",
                    "printed_numeric_bpm": 120,
                    "microseconds_per_beat": 500000,
                    "time_signature": {"numerator": 4, "denominator": 4},
                },
                "performance_route": {
                    "step_count": 1,
                    "steps": [{"part_id": "melody", "measure_id": "m1"}],
                    "total_quarter_beats": "4",
                    "total_ticks": 1920,
                },
                "validation": {
                    "all_events_visually_checked": True,
                    "strictly_monophonic": True,
                    "roundtrip_verified": True,
                    "note_count": 2,
                },
                "pitch_range": {"lowest_pitch": 60, "highest_pitch": 64},
            },
        )

    def _read_conversion_report(self) -> dict[str, object]:
        return json.loads(self.conversion.read_text(encoding="utf-8"))

    def _args(self, *extra: str) -> object:
        return builder.build_parser().parse_args(
            [
                str(self.melody),
                str(self.player),
                "--manifest",
                str(self.manifest),
                "--audit-report",
                str(self.audit),
                "--source-page",
                "user-supplied",
                "--license",
                "user-confirmed private workflow",
                "--intended-use",
                "private",
                *extra,
            ]
        )

    def test_conversion_report_builds_and_dry_run_needs_no_input_packages(self) -> None:
        args = self._args("--conversion-report", str(self.conversion))
        self.assertEqual(builder.run(args), 0)

        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        evidence = manifest["conversion_report"]
        self.assertIsNone(manifest["extraction_report"])
        self.assertEqual(evidence["report_format"], "delta-reviewed-score-compile/v1")
        self.assertEqual(evidence["output_midi_sha256"], sha256(self.melody))
        self.assertEqual(evidence["score_ir"]["path"], str(self.score_ir))
        self.assertEqual(evidence["source"]["verified_sha256"], sha256(self.source))
        self.assertEqual(
            evidence["current_files_verified"], {"score_ir": True, "source": True}
        )
        self.assertEqual(evidence["performance_route"]["steps"][0]["measure_id"], "m1")
        self.assertNotIn("source_track_index", evidence)
        self.assertNotIn("source_track_name", evidence)

        with patch.object(sys, "argv", [str(self.player), "--dry-run"]), patch.dict(
            sys.modules,
            {"keyboard": None, "pydirectinput": None},
        ), redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as stopped:
                runpy.run_path(str(self.player), run_name="__main__")
        self.assertEqual(stopped.exception.code, 0)
        self.assertIn("2 playable events", output.getvalue())

        with patch.object(sys, "argv", [str(self.player)]), patch.dict(
            sys.modules,
            {"keyboard": None, "pydirectinput": None},
        ), redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as stopped:
                runpy.run_path(str(self.player), run_name="__main__")
        self.assertEqual(stopped.exception.code, 0)
        self.assertIn("Safety stop: no input was sent.", output.getvalue())

        with patch.object(sys, "argv", [str(self.player), "--play"]), patch(
            "builtins.input", return_value="NO"
        ), patch.dict(
            sys.modules,
            {"keyboard": None, "pydirectinput": None},
        ), redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as stopped:
                runpy.run_path(str(self.player), run_name="__main__")
        self.assertEqual(stopped.exception.code, 0)
        self.assertIn("Cancelled: no input was sent.", output.getvalue())

    def test_conversion_and_extraction_reports_remain_separate(self) -> None:
        extraction_source = self.root / "source_arrangement.mid"
        extraction_source.write_bytes(b"synthetic source arrangement")
        self._write_json(
            self.extraction,
            {
                "report_format": "delta-midi-extract/v2",
                "output_file": str(self.melody),
                "output_sha256": sha256(self.melody),
                "source_file": str(extraction_source),
                "source_sha256": sha256(extraction_source),
                "source_track_index": 3,
                "source_track_name": "Guide",
                "structure_class": "isolated-melody",
                "settings": {
                    "same_onset": "reject",
                    "overlaps": "reject",
                    "duration_mode": "source",
                    "trim_leading_rest": False,
                },
            },
        )
        args = self._args(
            "--extraction-report",
            str(self.extraction),
            "--conversion-report",
            str(self.conversion),
        )
        self.assertEqual(builder.run(args), 0)

        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        self.assertEqual(manifest["extraction_report"]["source_track_index"], 3)
        self.assertEqual(
            manifest["extraction_report"]["structure_class"], "isolated-melody"
        )
        self.assertEqual(
            manifest["extraction_report"]["source_sha256"], sha256(extraction_source)
        )
        self.assertEqual(
            manifest["conversion_report"]["score_ir"]["sha256"], sha256(self.score_ir)
        )
        self.assertNotIn("source_track_index", manifest["conversion_report"])

    def test_conversion_report_requires_exact_output_hash(self) -> None:
        self._write_conversion_report(output_sha256="0" * 64)
        args = self._args("--conversion-report", str(self.conversion))
        with self.assertRaisesRegex(ValueError, "hash does not match"):
            builder.run(args)
        self.assertFalse(self.player.exists())
        self.assertFalse(self.manifest.exists())

    def test_conversion_report_requires_exact_output_path(self) -> None:
        report = self._read_conversion_report()
        report["output_file"] = str(self.root / "different.mid")
        self._write_json(self.conversion, report)
        args = self._args("--conversion-report", str(self.conversion))
        with self.assertRaisesRegex(ValueError, "exact melody MIDI"):
            builder.run(args)
        self.assertFalse(self.player.exists())
        self.assertFalse(self.manifest.exists())

    def test_conversion_report_rejects_unverified_or_inconsistent_source_hashes(self) -> None:
        cases = {
            "not verified": {"hash_verified": False},
            "internal mismatch": {"expected_sha256": "1" * 64},
            "invalid digest": {
                "expected_sha256": "not-a-sha256",
                "verified_sha256": "not-a-sha256",
            },
        }
        for label, changes in cases.items():
            with self.subTest(label=label):
                report = self._read_conversion_report()
                source = report["source"]
                assert isinstance(source, dict)
                source.update(changes)
                self._write_json(self.conversion, report)
                args = self._args("--conversion-report", str(self.conversion))
                with self.assertRaisesRegex(ValueError, "source"):
                    builder.run(args)
                self._write_conversion_report()

    def test_conversion_report_rejects_unreviewed_or_polyphonic_validation(self) -> None:
        for field in (
            "all_events_visually_checked",
            "strictly_monophonic",
            "roundtrip_verified",
        ):
            with self.subTest(field=field):
                report = self._read_conversion_report()
                validation = report["validation"]
                assert isinstance(validation, dict)
                validation[field] = False
                self._write_json(self.conversion, report)
                args = self._args("--conversion-report", str(self.conversion))
                with self.assertRaisesRegex(ValueError, field):
                    builder.run(args)
                self._write_conversion_report()

    def test_conversion_report_rejects_changed_score_ir(self) -> None:
        self.score_ir.write_text('{"schema_version": 1, "tampered": true}\n', encoding="utf-8")
        args = self._args("--conversion-report", str(self.conversion))
        with self.assertRaisesRegex(ValueError, "score_ir hash"):
            builder.run(args)

    def test_conversion_report_rejects_changed_accessible_source(self) -> None:
        self.source.write_bytes(b"changed score evidence")
        args = self._args("--conversion-report", str(self.conversion))
        with self.assertRaisesRegex(ValueError, "current source file"):
            builder.run(args)

    def test_moved_source_keeps_internal_hash_evidence_but_is_marked_unchecked(self) -> None:
        self.source.unlink()
        args = self._args("--conversion-report", str(self.conversion))
        self.assertEqual(builder.run(args), 0)
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))
        self.assertFalse(manifest["conversion_report"]["current_files_verified"]["source"])

    def test_report_paths_cannot_conflict_with_artifact_paths(self) -> None:
        args = self._args("--conversion-report", str(self.player))
        with self.assertRaisesRegex(ValueError, "Path conflict"):
            builder.run(args)
        self.assertFalse(self.player.exists())
        self.assertFalse(self.manifest.exists())

    def test_conversion_report_must_match_ir_source_settings_and_route(self) -> None:
        cases = (
            ("source", "path", str(self.root / "other.pdf"), "source.path"),
            ("settings", "bpm", 121, "settings"),
            (
                "performance_route",
                "steps",
                [{"part_id": "melody", "measure_id": "m2"}],
                "performance_route",
            ),
        )
        for section_name, field, replacement, message in cases:
            with self.subTest(section=section_name, field=field):
                report = self._read_conversion_report()
                section = report[section_name]
                assert isinstance(section, dict)
                section[field] = replacement
                self._write_json(self.conversion, report)
                with self.assertRaisesRegex(ValueError, message):
                    builder.run(self._args("--conversion-report", str(self.conversion)))
                self._write_conversion_report()

    def test_title_matching_template_tokens_remains_valid_python(self) -> None:
        source = builder.render_player(
            "Title __EVENTS__ __SKIPPED_EVENTS__ __OCTAVE_SHIFT__",
            0,
            [[0.0, 1.0, 60]],
            [],
        )
        compile(source, "generated_player.py", "exec")
        self.assertIn("Title __EVENTS__ __SKIPPED_EVENTS__ __OCTAVE_SHIFT__", source)

    def test_extraction_evidence_rechecks_lossy_structure_policy(self) -> None:
        extraction_source = self.root / "source_arrangement.mid"
        extraction_source.write_bytes(b"synthetic source arrangement")
        base_report = {
            "report_format": "delta-midi-extract/v2",
            "output_file": str(self.melody),
            "output_sha256": sha256(self.melody),
            "source_file": str(extraction_source),
            "source_sha256": sha256(extraction_source),
            "source_track_index": 1,
            "source_track_name": "Lead",
            "structure_class": "mixed-melody-accompaniment",
            "settings": {
                "same_onset": "highest",
                "overlaps": "reject",
                "duration_mode": "source",
                "trim_leading_rest": False,
            },
        }
        self._write_json(self.extraction, base_report)
        with self.assertRaisesRegex(ValueError, "structure_class"):
            builder.run(self._args("--extraction-report", str(self.extraction)))

        base_report["structure_class"] = "isolated-melody"
        base_report["settings"]["same_onset"] = "reject"
        base_report["settings"]["duration_mode"] = "onset"
        self._write_json(self.extraction, base_report)
        with self.assertRaisesRegex(ValueError, "karaoke-guide"):
            builder.run(self._args("--extraction-report", str(self.extraction)))


if __name__ == "__main__":
    unittest.main()
