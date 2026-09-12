# Quality gates

Use this reference for analysis/build decisions that need more than the normal happy path.

## Input hierarchy

| Input | Default treatment |
| --- | --- |
| Strict monophonic MIDI | Audit, preserve timing, extract, and verify |
| Named melody/solo track with occasional same-onset chords | Review; extract only from that named track, normally retaining the top note |
| Karaoke/guide MIDI with artificial short note-offs | Confirm the diagnosis; reconstruct durations from onsets and preserve long rests |
| Community MIDI with unknown rights status | It remains a technically auditable fallback after user acquisition; preserve the source/uploader notice, keep intended use private, and do not label it cleared for public derivatives |
| Piano or ensemble MIDI without an isolated melody | Stop for a documented selection rule and user confirmation; do not take the global highest voice |
| Concerto/orchestral score | Keep solo/principal as A; only create a B variant if a clearly documented hand-off part carries the theme while the solo rests |
| MusicXML | Use an available, tested conversion route; preserve the original file and record the converter/version |
| Clear, complete monophonic PDF/image with one global meter and no pickup | Use the reviewed-score transcription route; every event and the finite performance route must be visually checked before compilation |
| Polyphonic, incomplete, or ambiguous PDF/image | Stop at the exact page/system/measure uncertainty; isolate a defensible voice or obtain a better source rather than guessing |

## Musical-structure gate

Strict monophony is necessary but not sufficient: a lossy process can produce a zero-overlap MIDI that alternates melody and accompaniment notes incorrectly.

- Classify the selected source before using `--same-onset highest/lowest`, `--overlaps truncate`, `--duration-mode onset`, or `--trim-leading-rest`.
- `isolated-melody`, `karaoke-guide`, and `independent-melodic-part` may use a documented reduction after review.
- Only `karaoke-guide` may reconstruct duration from onsets. Only `isolated-melody` or `karaoke-guide` may trim the leading rest; preserve the common time origin of every independent/imitative part.
- `mixed-melody-accompaniment`, `imitative-polyphony`, `chordal-texture`, and `unknown` must reject lossy reduction. Isolate a real part first.
- For a canon/imitative work, preserve one independent part and its leading rests as the faithful single-line baseline. Phrase-level voice switching is an adaptation, not an extraction; require user choice and label it.
- Treat repeated phrases, first/second endings, da capo/dal segno/coda routes, pickups, and structural rests as musical content. Do not trim or collapse them for convenience.

Read [midi-structure.md](midi-structure.md) for the decision rules.

## Reviewed-score transcription gates

Before `compile_score_midi.py` is allowed to write a MIDI, require:

- a durable source file whose SHA-256 matches the reviewed score IR;
- complete page/system inventory and a defensible single intended voice;
- exact rational beat offsets/durations and explicit rests covering every measure;
- explicit playback BPM origin plus separate literal/numeric printed-tempo evidence;
- `visually_checked` on every note and rest, a required stable source reference on every measure, and event-level source references for special or ambiguous symbols;
- a finite explicit `performance_route` reflecting the chosen repeats/endings/navigation;
- ties merged only after route expansion, and no slur treated as a tie;
- no unresolved pitch, rhythm, accidental, octave, voice, navigation, or editorial choice; and
- a successful compile report followed by the normal MIDI audit and measure-by-measure listening/visual comparison.

Case-specific values such as measure count, BPM, coda-pass count, instrument, or filename must come from the current source/user decision. Never copy them from an earlier song's review report.

## Required MIDI checks

Before a player is built, the chosen melody output must have:

- one logical melody track;
- `max_simultaneous_notes = 1`;
- `overlapping_note_count = 0`;
- a valid tempo map; and
- a saved audio/visual review by the user when the source required extraction or rhythm reconstruction.

## Pitch and timing rules

- Preserve MIDI pitch classes. A global `±12`, `±24`, etc. placement is allowed; transposition and per-note octave folding are not defaults.
- Report every event outside the configured playable range. The user must choose whether to revise the source, make a different global placement, or explicitly tolerate skipped notes.
- Preserve tempo changes and rests. Use an absolute clock during playback rather than adding `sleep()` durations cumulatively.
- For guide MIDI, document the onset gate ratio and the long-gap threshold/hold used. A plausible-looking output is not sufficient—listen to it.

## Game-input safety

- Verify the live key and modifier mapping with a short test before a full song.
- Test a generated player with `--dry-run` first.
- `F10` must stop playback and release keyboard/mouse modifiers.
- Do not try to defeat an anti-cheat or input restriction. If automated input is rejected or disallowed, provide a timing/key-display mode instead.

## Manifest fields

At minimum, save the supplied source filename and page, source hash, license/permission as stated by the user, intended use, audit outcome, pitch range, chosen octave shift, and any skipped/unplayable events. For MIDI extraction, also save the selected track, structure class, and extraction flags. For score transcription, save the reviewed IR hash/path, source verification, explicit performance route summary, compiler settings, and conversion-report hash/path.
