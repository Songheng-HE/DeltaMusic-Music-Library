# Canon in D — Delta artifacts

## Authorization record

- Source file: `input/CanonInD.mid` (preserved copy of the MIDI supplied by the user).
- Source page: user-authorized source; exact source page was not supplied.
- Declared permission: the user states they are authorized to use the supplied MIDI; a specific license was not supplied.
- Intended use: `private` is a working assumption, not a user-confirmed publication license. Update `manifest.json` before sharing or publishing.

## Selection and validation

- Selected source track: #1 (unnamed, channel 1); it is the only sounding track.
- Extraction: no chord/overlap relaxation, original note durations retained, no leading-rest trim.
- Output: 138 notes, strictly monophonic; no overlaps, same-onset chords, or note anomalies.
- Timing: original tempo map retained (60 BPM, 4/4); no tempo or pitch transposition.
- Range: F#3–F#5, placed at global octave shift `+0` within Delta's C3–B5 range.
- Unplayable/skipped events: 0.

## Files

- Melody-only MIDI: `pachelbel-canon-in-d_melody_only.mid`
- Delta player: `pachelbel-canon-in-d_three_octave_player.py`
- Audit: `reports/melody_audit.md` and `reports/melody_audit.json`
- Extraction record: `reports/extraction_report.json`
- Processing and rights record: `manifest.json`

## Safe review and playback

First listen to `pachelbel-canon-in-d_melody_only.mid` in a local MIDI player and confirm the notes sound correct. Then inspect the player without sending input:

```powershell
python -B '.\pachelbel-canon-in-d_three_octave_player.py' --dry-run
```

The dry run completed successfully during generation and sent no keyboard or mouse input. Before a real run, verify Delta's bindings in a harmless test: natural notes use `Z X C V B N M ,`; middle mouse adds a sharp; left/right mouse select the lower/higher octave. Keep Delta focused and use `F10` to stop. Do not run the player where automated input is not allowed.
