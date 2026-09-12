# Reviewed score transcription

Use this reference for the `Transcribe` route: a complete, user-supplied PDF or image is converted into a reviewed score IR and then compiled deterministically to a strict monophonic MIDI.

## Capability boundary

This is guided visual transcription, not general optical music recognition.

- Good v1 input: a clear numbered-notation or staff-notation score with one intended melody line, stable meter, and readable pitch/rhythm symbols.
- Review-required input: multiple voices, accompaniment on the same staff, tuplets, grace notes, ornaments whose playback is not explicit, cross-staff writing, hidden octave conventions, ambiguous ties/slurs, nonstandard repeat/navigation marks, meter changes, or missing/cropped systems.
- Unsupported input must not be guessed into a plausible MIDI. Record the exact page/system/measure/symbol and ask one specific question or seek a better source.
- Text extraction, vector geometry, OCR, or a vision model may propose a draft. None of those outputs is accepted as score truth until visually checked against the supplied page.

The v1 compiler has one global BPM and time signature. It does not encode pickup bars or mid-piece meter/tempo changes. Repeats and other navigation are supported only after they are manually resolved into a finite `performance_route`. Do not hide a pickup by padding it with an invented rest or flatten a meter/tempo change without labelling that result as an editorial adaptation.

Do not substitute a same-title internet MIDI for the supplied edition without the user's explicit choice. It may be used as a labelled comparison aid, never as silent evidence that ambiguous notation was resolved correctly.

## Preserve source evidence

Before transcription:

1. Put the durable original under `<song>/input/`; never work only from a temporary attachment path.
2. Compute its SHA-256 and record it in `source.sha256`.
3. Inventory every page, system, staff, printed measure number, pickup, repeat, ending, D.C./D.S., segno, coda, Fine, key/meter/tempo marking, and visibly missing or unreadable region.
4. Give every measure a stable `source_ref` such as page + system + printed/logical measure. Add an event-level `source_ref` for ambiguous or special symbols that need beat/glyph precision.

The compiler verifies that the current source file still has the recorded hash. A mismatch means the transcription evidence belongs to a different file and compilation must stop.

## Keep three evidence layers separate

Do not blur these categories. Save a durable `<song>/reports/transcription_decisions.md` with one separately labelled section for each:

- **Score facts**: visible pitches, accidentals, durations, rests, ties, barlines, printed tempo, key/meter, and navigation marks.
- **Transcription judgments**: how an ambiguous glyph was read, which voice is the intended melody, how a pickup is represented, or why a mark is treated as a tie rather than a slur. Put uncertainty and reasoning in `review_note`; unresolved judgments do not receive `visually_checked`.
- **Editorial playback settings**: chosen BPM when none is printed, velocity, performance-route choice, omitted ornament realization, count-in, or a user-requested structural adaptation. These are not presented as printed facts.

If a score has a printed tempo and the player uses a different BPM, record both and say that the latter is editorial.

`bpm` is always the actual playback value. Set `bpm_origin` to `printed_score` only when a printed numeric metronome value exists and `bpm` matches it; otherwise use `editorial_setting`. Preserve the literal printed wording in `printed_tempo_text` (or `null`) and its numeric value in `printed_numeric_bpm` (or `null`). Never turn a qualitative marking such as *Andante* into a claimed printed number.

The IR carries the deterministic values needed by the compiler; the decision log records why those values were accepted. In the score-facts section cite stable `source_ref` locations. In the judgment section list every ambiguous reading and its disposition. In the editorial section record the origin of BPM, the reason for the chosen `performance_route`, and whether any cross-part or structural adaptation was requested.

## Reviewed score IR v1

The canonical JSON format is defined by [reviewed-score.schema.json](reviewed-score.schema.json). A minimal shape is:

```json
{
  "format": "delta-reviewed-score/v1",
  "title": "Example",
  "source": {
    "path": "../input/score.png",
    "sha256": "<64 lowercase hex characters>",
    "document_type": "image"
  },
  "bpm": 108,
  "bpm_origin": "editorial_setting",
  "printed_tempo_text": "Andante",
  "printed_numeric_bpm": null,
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
            {"type": "note", "offset_beats": "0", "duration_beats": "1", "pitch": 60, "review_state": "visually_checked"},
            {"type": "rest", "offset_beats": "1", "duration_beats": "3", "review_state": "visually_checked"}
          ]
        }
      ]
    }
  ],
  "performance_route": [{"part_id": "melody", "measure_id": "m1"}]
}
```

Beat values are exact rational strings measured in quarter-note beats, for example `"1"`, `"3/2"`, or `"1/4"`. Do not use approximate decimals. Every measure must have a stable `source_ref` and be covered exactly once by non-overlapping notes/rests from beat zero to the meter length; write a rest rather than leaving an implicit gap. Events inherit the measure location for ordinary notation; add an event-level `source_ref` when a glyph, cross-system mark, tie/slur, or ambiguity needs more precise evidence.

Use integer MIDI pitch only after confirming key signature, current accidental state, octave, and any numbered-notation octave dots. An accidental's scope follows the notation system/edition, not an assumed global rewrite.

## Route, ties, and slurs

`performance_route` is the finite, auditable playback order. Expand repeats, endings, D.C./D.S., coda, and any chosen extra pass into explicit measure references. Do not encode an unbounded loop or infer a route while compiling.

Resolve navigation first. Then evaluate ties in performed order:

- `tie_out` can merge only with the immediately following performed note when it has the same MIDI pitch, begins contiguously, and carries the matching `tie_in` state.
- A rest, pitch change, time gap, or unrelated route boundary breaks a tie and must be rejected if tie flags claim otherwise.
- `slur_start` and `slur_end` are articulation evidence only; they never merge note durations.

This order matters when a tied note crosses a repeat or ending.

## Compile and verify

Compile only when every event is `visually_checked` and the route is final:

```powershell
& $python .agents\skills\delta-music-score-to-midi\scripts\compile_score_midi.py <reviewed_score.json> <melody_only.mid> --report <transcription_report.json>
```

The JSON report binds the score IR, source file, route, settings, output MIDI, validation result, pitch range, and hashes. Preserve it unchanged. Then:

1. Run `midi_tools.py audit` on the MIDI.
2. Require one logical melody track, `max_simultaneous_notes = 1`, and `overlapping_note_count = 0`.
3. Compare playback measure by measure with the rendered score, including the first onset, explicit rests, repeat/ending order, tied durations, and the final note-off.
4. Use the conversion report—not a fabricated extraction-track report—when building the player.

The score compiler does not prove that the human transcription is musically correct. The source references, review states, balance checks, route expansion, MIDI audit, and listening pass make the remaining judgment traceable.

## Stop conditions

Stop before compilation when any of these remains:

- source hash mismatch, missing page, duplicate/cropped system, or unknown page order;
- unclear melody voice or simultaneous material that cannot be represented honestly as one line;
- unresolved pitch, accidental, octave, duration, rest, tie/slur, tuplet, ornament, pickup, meter, or navigation mark;
- measure coverage that balances only after inventing or deleting time;
- performance route that depends on an unstated editorial choice; or
- a requested public/shareable derivative without adequate permission for the supplied edition.
