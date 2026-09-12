# MIDI structure classification

Classify the selected musical material before applying any lossy note-selection
policy. A report showing `max_simultaneous_notes = 1` and zero overlaps is a
necessary output check, not proof that the output is the intended melody.

## Structure classes

| `--structure-class` value | Meaning | `highest` / `lowest` / `truncate` |
| --- | --- | --- |
| `isolated-melody` | A reviewed melody track whose exceptional doubled notes or note-off overlaps have a known musical explanation | Allowed after review |
| `karaoke-guide` | A reviewed guide-vocal track; artificial short note-offs may also justify onset-duration reconstruction | Allowed after review |
| `independent-melodic-part` | One named, independent instrumental/vocal part chosen as the single-line baseline | Allowed after review |
| `mixed-melody-accompaniment` | Melody and accompaniment share one track or event stream | Refused; isolate the candidate register/voice first |
| `imitative-polyphony` | Multiple independent entries imitate or answer one another, as in a canon | Refused; preserve independent parts first |
| `chordal-texture` | Chords or homophonic accompaniment dominate the selected material | Refused; obtain or transcribe an isolated melody |
| `unknown` | The structure has not been reviewed confidently | Refused |

The default `--same-onset reject --overlaps reject --duration-mode source` route
without leading-rest trimming does not require a structure class. Supplying
`highest`, `lowest`, or `truncate` is a lossy musical decision and therefore
requires an explicit safe class. `--duration-mode onset` is allowed only for a
reviewed `karaoke-guide`. `--trim-leading-rest` changes the time origin and is
allowed only for a reviewed `isolated-melody` or `karaoke-guide`, never for an
independent/canonic part. Classification does not automatically make the result
correct; it records why the operation was considered appropriate and the result
still requires score/listening review.

## Why strict mono is not sufficient

Consider a melody F4 held from tick 0 to 300, a low Bb2 accompaniment note entering
at tick 150, and the next F4 beginning at tick 300. Mechanical overlap truncation
can produce F4 (0–150), Bb2 (150–300), F4 (300–...), which is strictly monophonic
but has truncated the melody and inserted the bass. Do not apply `highest +
truncate` directly to a mixed arrangement track.

Before extraction, document evidence for the classification: track name and
instrument, register separation, channel/part organization, short score windows,
and listening when available. A song-specific pitch cutoff is acceptable only as
a documented candidate-isolation step; it is not a reusable global rule.

## Imitative counterpoint and hand-offs

For a canon or other imitative polyphony, keep each faithful independent part as a
baseline. Preserve the original common time origin and each part's leading rests;
trimming every part to its first note destroys their staggered entries. Do not call
one part the complete work when simultaneous imitative parts were omitted.

If a single-key adaptation must move between parts, select whole musical phrases,
not whichever note is highest or currently active. Record every source part,
phrase boundary, seam, omitted passage, and newly duplicated passage, and label the
result as a **single-line arrangement**, not a recovered unique original melody.

Preserve meaningful repeated attacks and rests. Repeated notes can be structural
material; activity, speed, pitch height, or repetition alone does not identify
foreground melody. Any removal or newly introduced repetition is an arrangement
decision that must be reported and auditioned.
