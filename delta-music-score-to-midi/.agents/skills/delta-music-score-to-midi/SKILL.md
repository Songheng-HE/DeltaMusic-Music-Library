---
name: delta-music-score-to-midi
description: "Research rights-aware sources for a Delta melody line and convert user-supplied MIDI or clear monophonic numbered/staff score PDFs/images into reviewed, validated melody-only MIDI plus a Delta three-octave player. Use only for Delta Music source research, melody extraction/transcription, or player generation—not general composition, generic MIDI editing, or unrelated Python work. Never download protected music or present unreviewed OCR as fact."
---

# Delta Music Score To Midi

Create trustworthy, reproducible source-to-player artifacts for Delta Music. Keep source discovery, user acquisition, music conversion, and game input as separate stages.

## Scope and authority

- Treat a score listing as a discovery lead, not a license to download, copy, adapt, or redistribute it.
- Search, compare, and link to candidates. Never download, authenticate, pay, spend credits, or bypass a paywall, login, DRM, rate limit, or anti-bot control on the user's behalf.
- The user chooses whether to obtain a candidate through its normal original page, then supplies it locally. Record its rights status as `cleared`, `unknown`, or `unsuitable for public derivatives`; download availability is never proof of permission. Before generating shareable artifacts, record whether the intended use is private or public and the source's stated license or permission.
- A user-supplied community MIDI with `unknown` rights may be technically audited after the user confirms it is appropriate for their stated private workflow. Do not describe it as authorized or suitable for public sharing without stated permission or a usable license.
- Keep all work under the current project folder unless the user explicitly selects another destination. Do not rely on temporary chat attachment paths as durable inputs.
- This skill has two deterministic conversion routes: extract an isolated line from user-supplied MIDI, or compile a fully reviewed score IR transcribed from a user-supplied clear monophonic PDF/image. Treat MusicXML as a possible source only when an available converter can be verified.
- Do not claim general-purpose or lossless optical music recognition. Automated text/vector/vision results are hints only; an event may enter the reviewed score IR only after its pitch, onset, duration, and source location have been visually checked.

## Choose the mode

Use the smallest applicable mode. A request can move from one mode to the next only after the relevant input exists.

1. **Research** — find 3–8 lawful, useful candidates and write `<song>/reports/research_report.md`. Read [source discovery rules](references/source-discovery.md) before searching.
2. **Transcribe** — turn a user-supplied, visually clear monophonic PDF/image into a reviewed score IR and compile it to MIDI. Read [score transcription rules](references/score-transcription.md) first.
3. **Analyze** — audit a locally supplied MIDI, classify its musical structure, choose a melody strategy, and present the report before extracting uncertain material. Read [MIDI structure rules](references/midi-structure.md) first.
4. **Build** — create a strict `*_melody_only.mid`, a three-octave player `.py`, a source/processing `manifest.json`, and a concise per-song `README.md`.

If the user has already supplied a MIDI or a complete readable score, skip research. If a request is only to find sources, stop after the research report and user hand-off.

In the PowerShell examples below, `$python` means an available Python 3 executable. Resolve it once for the current host; if `py`/`python` is not on `PATH`, use the bundled workspace Python rather than assuming the launcher exists.

Before running a bundled helper, set $skillRoot to the actual directory containing this SKILL.md. Do not assume the current project has a .agents\skills copy: the Skill may have been installed in a user-level or Codex-level directory.

If the host does not expose the loaded SKILL.md path, use this PowerShell fallback before invoking a helper:

```powershell
$skillName = "delta-music-score-to-midi"
$skillRoot = $null
$folder = Get-Item -LiteralPath (Get-Location)
while ($null -ne $folder) {
  $candidate = Join-Path $folder.FullName ".agents\skills\$skillName"
  if (Test-Path -LiteralPath (Join-Path $candidate "SKILL.md") -PathType Leaf) {
    $skillRoot = $candidate
    break
  }
  $folder = $folder.Parent
}
if (-not $skillRoot) {
  $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
  foreach ($candidate in @(
    (Join-Path $env:USERPROFILE ".agents\skills\$skillName"),
    (Join-Path $codexHome "skills\$skillName")
  )) {
    if (Test-Path -LiteralPath (Join-Path $candidate "SKILL.md") -PathType Leaf) {
      $skillRoot = $candidate
      break
    }
  }
}
if (-not $skillRoot) { throw "Cannot locate delta-music-score-to-midi. Reopen the project or reinstall the Skill." }
```

## Research mode

Search for a source that can become one audible melody line, not merely any sheet music.

- Class candidates by rights-use tier before ranking musical suitability. **Tier A** has usable, verifiable permission or a clearly applicable public-domain basis; **Tier B** is a separately labelled community/technical fallback with unknown or uploader-declared rights; **Tier C** has conflicting rights evidence, cannot be obtained normally, or is unsuitable for the user's stated use. Prefer Tier A. A public-domain composition does not automatically make a modern edition or arrangement reusable.
- A community MIDI, including MidiShow, may be a Tier B technical fallback when visible page metadata shows a matching complete MIDI or useful melody-track evidence. Do not silently omit it just because technical correctness cannot be known from the listing; state what the post-upload audit must verify. Tier B is never proof of permission or a basis for public/shareable derivative output.
- Prefer a complete, explicitly identified `Melody`, `Lyrics`, `Vocal`, `Guide Melody`, `Solo`, `Principal`, `Flute`, or `Lead` MIDI track. For a pop song, favor vocal/guide tracks; for a concerto, favor solo/principal parts.
- Do not call a one-track MIDI monophonic without inspection. Do not treat a community upload, a preview, or an accessible page as authorization.
- For each candidate record: title/version, arranger and instrument, format, completeness, visible melody-track evidence, licensing/access evidence, price/registration, source link, risks, and retrieval date. Clearly label unknowns.
- Recommend a Tier A first choice when available and, when useful, one clearly marked Tier B technical fallback. If no Tier A source exists, say so plainly rather than silently omitting a useful community fallback. The user obtains any chosen file through its original page; the assistant audits the supplied file before conversion. Use the hand-off language in the source-discovery reference when it helps.

## Transcribe mode

Use this route only for a complete user-supplied score whose intended melody line is visually identifiable. Do not replace the supplied edition with an unrelated same-title MIDI; the score remains the source of truth.

1. Preserve the original under `<song-slug>/input/`, compute its SHA-256, inventory every page/system, and classify the texture. A clear single staff/voice with one global meter and no pickup can proceed in v1. Multiple simultaneous parts, hidden accompaniment, pickup bars, meter/tempo changes, ambiguous repeats, missing pages, or unreadable symbols require a specific review decision or a future IR extension before compilation.
2. Create `<song-slug>/transcription/reviewed_score.json` conforming to [the reviewed-score schema](references/reviewed-score.schema.json), plus `<song-slug>/reports/transcription_decisions.md`. Keep three separately labelled sections in that decision log: printed score facts, transcription judgments, and editorial playback settings.
3. Record beats as exact rational strings in quarter-note units, preserve explicit rests, and attach stable source references. Record the actual playback `bpm`, its `bpm_origin`, and the printed tempo text/number separately. Mark an event `visually_checked` only after comparing it with the supplied page. Never change an uncertain symbol merely to make a measure balance.
4. Expand the intended play order as a finite `performance_route`. Resolve repeats/endings/coda choices before compiling, then merge only contiguous same-pitch ties. A slur does not extend a MIDI note.
5. Compile the reviewed IR and save the conversion evidence:

```powershell
& $python (Join-Path $skillRoot "scripts\compile_score_midi.py") <song-slug>\transcription\reviewed_score.json <song-slug>\<song-slug>_melody_only.mid --report <song-slug>\reports\transcription_report.json
```

The compiler must reject an unreviewed event, a measure whose events do not exactly cover its meter, an invalid route, a non-contiguous or pitch-changing tie, a source hash mismatch, and timing that cannot be represented exactly at the declared PPQ. Re-run the normal MIDI audit on the compiled output and listen/compare against the score before building the player.

## Analyze mode

Make a song folder such as `<song-slug>/input` and `<song-slug>/reports`. Preserve the supplied original in `input/`; never overwrite it.

Run the bundled MIDI audit before choosing a track:

```powershell
& $python (Join-Path $skillRoot "scripts\midi_tools.py") audit <input.mid> --json <song-slug>\reports\track_report.json --markdown <song-slug>\reports\track_report.md
```

The audit must establish all of the following:

- track index/name, programs/channels, note and onset counts, pitch range, maximum simultaneous notes, and overlaps;
- PPQ, tempo map, meter/key changes, and duration;
- whether near-uniform, very short note-offs make a karaoke/guide track likely.

Strict monophony is necessary but not sufficient. Before applying any lossy reduction, classify the selected track as `isolated-melody`, `karaoke-guide`, `independent-melodic-part`, `mixed-melody-accompaniment`, `imitative-polyphony`, `chordal-texture`, or `unknown`. A result can have zero overlaps and still be musically wrong if accompaniment notes have entered the line.

Choose a melody source in this order:

1. A named, strictly monophonic melody/vocal/guide/solo track.
2. A named melody track with same-onset chords only; reduce chords only within that named source, normally to the upper voice.
3. A named solo/principal source whose silent structural regions may be supplemented by one clearly identified hand-off track only as a user-confirmed, labelled single-line arrangement. Preserve the untouched solo/part baseline as A and produce the hand-off adaptation as B when the musical choice is consequential.
4. A clearly separated high melody voice in a known arrangement, after explaining the extraction rule and obtaining confirmation.

Never select the highest note from the entire arrangement as a default. Stop for review when the source is a dense piano/orchestral mix without a defensible melody voice.

For a canon or other imitative polyphony, the faithful single-player baseline is one independently identifiable part with its original leading rests and shared time origin preserved. Switching among voices at phrase boundaries is a new arrangement: require the user's choice, label it as an adaptation, and keep a decision log. Separate synchronized players for distinct parts are a different output mode and must not be represented as one melody track.

## Extract and validate

Use an explicit track index or exact track name. The helper rejects chords and overlaps by default, so any relaxation is reviewable:

```powershell
& $python (Join-Path $skillRoot "scripts\midi_tools.py") extract <input.mid> <song-slug>\<song-slug>_melody_only.mid --track "Lyrics" --report <song-slug>\reports\extraction_report.json
```

- Add `--same-onset highest` only for an already chosen melody/solo track whose simultaneous notes are genuine double stops or chord notation, and pass an eligible reviewed structure such as `--structure-class isolated-melody`.
- Add `--overlaps truncate` only after documenting why legato overlaps should end at the next onset, and pass `--structure-class isolated-melody`, `karaoke-guide`, or `independent-melodic-part` as appropriate.
- Never use `highest`, `lowest`, or `truncate` on `mixed-melody-accompaniment`, `imitative-polyphony`, `chordal-texture`, or `unknown`. First isolate a real part/voice, or stop for review. Do not use a final zero-overlap audit as evidence that a bad reduction became musically correct.
- For a karaoke/guide track with artificial short note-offs, use `--duration-mode onset --onset-gate 0.88 --structure-class karaoke-guide` only after reviewing the report. No other structure class may use onset reconstruction. Large onset gaps must remain rests.
- Use `--trim-leading-rest` only with an explicitly reviewed `isolated-melody` or `karaoke-guide` when the desired player should begin at the melody rather than an instrumental introduction. Never trim an `independent-melodic-part` or `imitative-polyphony`; its leading rest preserves the shared time origin.
- Re-run the audit on the output and preserve the resulting report for the builder:

~~~powershell
& $python (Join-Path $skillRoot "scripts\midi_tools.py") audit <song-slug>\<song-slug>_melody_only.mid --json <song-slug>\reports\melody_audit.json --markdown <song-slug>\reports\melody_audit.md
~~~

It must report `max_simultaneous_notes = 1` and `overlapping_note_count = 0`. Listen to the melody-only MIDI before generating game input. The helper will not overwrite a source or report by default; use `--force` only for an already reviewed derived artifact.

## Build the Delta player

Generate the player from the validated melody MIDI:

```powershell
& $python (Join-Path $skillRoot "scripts\build_delta_player.py") <song-slug>\<song-slug>_melody_only.mid <song-slug>\<song-slug>_three_octave_player.py --song-title "Song title" --manifest <song-slug>\manifest.json --audit-report <song-slug>\reports\melody_audit.json --extraction-report <song-slug>\reports\extraction_report.json --source-page "<source URL or user-original>" --license "<license or permission>" --intended-use private
```

For a reviewed-score transcription, replace `--extraction-report` with the compiler evidence:

```powershell
& $python (Join-Path $skillRoot "scripts\build_delta_player.py") <song-slug>\<song-slug>_melody_only.mid <song-slug>\<song-slug>_three_octave_player.py --song-title "Song title" --manifest <song-slug>\manifest.json --audit-report <song-slug>\reports\melody_audit.json --conversion-report <song-slug>\reports\transcription_report.json --source-page "user-supplied score" --license "<permission or private-use record>" --intended-use private
```

The generator keeps the tempo map and uses absolute `time.perf_counter()` timing. Its mapping is deliberately editable: verify the game bindings once before playback. The default convention inherited from the prior workflow is `Z X C V B N M ,` for natural notes, mouse-middle for a sharp, and mouse-left/right for the adjacent lower/higher octave.

- Do not transpose a song. The only automatic pitch placement is one global multiple of 12 semitones.
- Review the reported exact-playable ratio and every out-of-range event. Do not use `--allow-unplayable` until the user accepts that those events will be skipped; never fold individual notes into a different octave silently.
- The builder always requires the post-conversion audit, source reference, license/permission record, intended use, and manifest. When this workflow created the MIDI through extraction or reviewed-score compilation, its corresponding evidence report is also mandatory. A user-supplied MIDI that was already strict monophonic may have only its audit evidence. The builder will not silently replace an existing artifact; use `--force` only for a reviewed derived file, never for the supplied source.
- For a Tier B/`unknown` source, keep the intended use private and record the uncertainty in the manifest. Decline public or shareable derivative output until the user supplies a usable permission or license.
- First run the generated player with `--dry-run`. The generated program sends no input unless the user explicitly passes `--play` and types `PLAY` at its interactive confirmation; it then targets whichever window is foreground. For actual play, keep game focus and use `F10` to stop; release all modifiers on exit. If the game does not accept the generated input or its rules prohibit it, stop automatic input and offer a visual/manual key guide instead.

## Complete only with an audit trail

Before handing off, create a short `README.md` beside the song artifacts and report:

- source page, version, declared permission/license, and intended use;
- selected track and every extraction decision, or the reviewed score IR, source hash, performance route, and the three-section transcription decision log;
- strict-monophony result, tempo treatment, original/final range, global octave shift, and unplayable count;
- exact output paths and the dry-run command.

Use [quality gates](references/quality-gates.md) when a source is polyphonic, karaoke-like, concert music, PDF/image-only, or intended for public release.
