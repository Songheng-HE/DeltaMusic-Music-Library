from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import mido


SKILL_ROOT = Path(__file__).resolve().parents[1]
COMPILE = SKILL_ROOT / "scripts" / "compile_score_midi.py"
MIDI_TOOLS = SKILL_ROOT / "scripts" / "midi_tools.py"
BUILD = SKILL_ROOT / "scripts" / "build_delta_player.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReviewedScorePipelineTests(unittest.TestCase):
    def test_reviewed_score_to_audited_player_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source.png"
            score_ir = root / "reviewed_score.json"
            melody = root / "synthetic_melody_only.mid"
            compile_report = root / "transcription_report.json"
            audit_report = root / "melody_audit.json"
            audit_markdown = root / "melody_audit.md"
            player = root / "synthetic_three_octave_player.py"
            manifest = root / "manifest.json"

            source.write_bytes(b"synthetic visual score evidence")
            score_ir.write_text(
                json.dumps(
                    {
                        "format": "delta-reviewed-score/v1",
                        "title": "Synthetic pipeline melody",
                        "source": {
                            "path": source.name,
                            "sha256": sha256(source),
                            "document_type": "image",
                        },
                        "bpm": 96,
                        "bpm_origin": "editorial_setting",
                        "printed_tempo_text": "Moderato",
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
                                            {
                                                "type": "rest",
                                                "offset_beats": "0",
                                                "duration_beats": "1",
                                                "review_state": "visually_checked",
                                            },
                                            {
                                                "type": "note",
                                                "offset_beats": "1",
                                                "duration_beats": "1",
                                                "pitch": 60,
                                                "review_state": "visually_checked",
                                            },
                                            {
                                                "type": "rest",
                                                "offset_beats": "2",
                                                "duration_beats": "2",
                                                "review_state": "visually_checked",
                                            },
                                        ],
                                    },
                                    {
                                        "id": "m2",
                                        "source_ref": "page 1 / system 1 / measure 2",
                                        "events": [
                                            {
                                                "type": "note",
                                                "offset_beats": "0",
                                                "duration_beats": "2",
                                                "pitch": 62,
                                                "review_state": "visually_checked",
                                            },
                                            {
                                                "type": "rest",
                                                "offset_beats": "2",
                                                "duration_beats": "2",
                                                "review_state": "visually_checked",
                                            },
                                        ],
                                    },
                                ],
                            }
                        ],
                        "performance_route": [
                            {"part_id": "melody", "measure_id": "m1"},
                            {"part_id": "melody", "measure_id": "m2"},
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            compiled = subprocess.run(
                [
                    sys.executable,
                    str(COMPILE),
                    str(score_ir),
                    str(melody),
                    "--report",
                    str(compile_report),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(compiled.returncode, 0, compiled.stderr)
            compile_data = json.loads(compile_report.read_text(encoding="utf-8"))
            self.assertEqual(compile_data["performance_route"]["total_ticks"], 3840)
            midi = mido.MidiFile(str(melody))
            melody_track = next(
                track
                for track in midi.tracks
                if any(
                    message.type == "track_name" and message.name == "melody_only"
                    for message in track
                )
            )
            tick = 0
            note_events = []
            for message in melody_track:
                tick += int(message.time)
                if message.type in {"note_on", "note_off"}:
                    note_events.append((tick, message.type, message.note, message.velocity))
            self.assertEqual(
                [(tick, pitch) for tick, kind, pitch, velocity in note_events if kind == "note_on" and velocity > 0],
                [(480, 60), (1920, 62)],
            )
            self.assertEqual(
                max(tick for tick, kind, _, _ in note_events if kind == "note_off"),
                2880,
            )

            audited = subprocess.run(
                [
                    sys.executable,
                    str(MIDI_TOOLS),
                    "audit",
                    str(melody),
                    "--json",
                    str(audit_report),
                    "--markdown",
                    str(audit_markdown),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(audited.returncode, 0, audited.stderr)

            built = subprocess.run(
                [
                    sys.executable,
                    str(BUILD),
                    str(melody),
                    str(player),
                    "--song-title",
                    "Synthetic pipeline melody",
                    "--manifest",
                    str(manifest),
                    "--audit-report",
                    str(audit_report),
                    "--conversion-report",
                    str(compile_report),
                    "--source-page",
                    "user-supplied synthetic score",
                    "--license",
                    "synthetic private test evidence",
                    "--intended-use",
                    "private",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(built.returncode, 0, built.stderr)

            dry_run = subprocess.run(
                [sys.executable, str(player), "--dry-run"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertIn("2 playable events", dry_run.stdout)
            self.assertIn("0.625s", dry_run.stdout)

            manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
            conversion = manifest_data["conversion_report"]
            self.assertEqual(conversion["output_midi_sha256"], sha256(melody))
            self.assertEqual(
                conversion["current_files_verified"],
                {"score_ir": True, "source": True},
            )
            self.assertTrue(
                conversion["validation"]["all_events_visually_checked"]
            )
            self.assertTrue(
                conversion["validation"]["strictly_monophonic"]
            )


if __name__ == "__main__":
    unittest.main()
