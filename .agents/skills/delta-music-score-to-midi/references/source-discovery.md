# Source discovery rules

Use this reference only for the **research** stage.

## What the assistant does and does not do

The assistant may search public listing pages, compare visible metadata, and link the user to an original source page. It must not download any candidate on the user's behalf; authenticate, pay, spend credits, or use a paid/gated/login-protected/rate-limited workflow; extract a full score from a preview; evade technical access controls; or treat a search result as a license.

The user may choose to obtain a candidate through the source's ordinary process, confirm whether the output is private or public, and supply the file for conversion. For a community-hosted candidate, record `rights status: unknown` unless usable permission or license evidence is visible. A paid personal copy, a public download, or private intent can still be unsuitable for publishing a derived MIDI or Python package.

## Candidate ranking

Assign a rights-use tier first, then rank candidates within the tier with this default weighting:

- **Tier A — rights-cleared:** direct permission, a usable license, or a clearly applicable public-domain basis for the exact edition/arrangement. Prefer these sources, especially for public or shareable output.
- **Tier B — technical fallback:** community-hosted MIDI or uploader-declared permission that cannot be independently verified. It may be listed when it is a strong technical candidate, but must be labelled `rights status: unknown`; it is not clearance for public/shareable derivative output.
- **Tier C — do not recommend:** conflicting rights evidence, explicit restriction incompatible with the intended use, inaccessible except through prohibited means, or a source that is materially mismatched.

Do not use rights status as a binary discovery exclusion rule. A Tier B MIDI can be valuable because the page exposes actual MIDI, track, instrument, tempo, or duration metadata; its technical suitability remains subject to the local audit after the user supplies it.

| Dimension | Weight | Evidence to record |
| --- | ---: | --- |
| Rights clarity | 40 | License, publisher/composer authorization, or public-domain basis for this exact edition |
| Musical match | 25 | Work/version, arranger, instrument, key, difficulty, and completeness |
| Convertibility | 20 | MIDI/MusicXML availability, explicit melody part, notation quality, repeat/tempo detail |
| Source credibility | 10 | Official publisher, composer, recognized archive, or clearly identified uploader |
| Cost and access | 5 | Price, registration, geographic limits, and visible download format |

For a public-domain work, distinguish the composition from a modern edition, arrangement, engraving, recording, or scan. For Creative Commons material, preserve the exact license text/version and flag attribution, non-commercial, share-alike, and no-derivatives terms. Do not send a `CC BY-ND` work into an adaptation/conversion queue without permission.

## Community MIDI fallback (including MidiShow)

Use a community MIDI as a Tier B fallback when the user requests it or no better-cleared source is available, and the listing visibly identifies enough of the work to make a technical judgment: title/version, uploader, format, duration or tempo, track/instrument evidence, and normal acquisition requirements.

For a MidiShow candidate, record the item page, uploader, original composer/arranger when shown, displayed rights/use notice, login or credits requirement, and visible technical metadata. Treat any uploader-selected license notice as a claim to disclose, not a guarantee. MidiShow says that uploaders are responsible for non-original works and that its displayed authorization information is uploader-selected and not guaranteed by the platform.

The assistant must not log in, spend credits, download, inspect page code, derive a direct file URL, use packet capture, bulk-fetch, use a browser extension to extract files, or reconstruct a full work from playback/preview. The user alone may acquire it through the page's ordinary process.

After the user supplies a Tier B MIDI, audit it like any other candidate. It may prove technically excellent or fail because its melody is absent, polyphonic, incomplete, badly timed, or outside the playable range. Keep a Tier B artifact private unless the user later supplies usable permission for broader distribution.

## Preferred source formats

1. Authorized, complete melody MIDI or a multi-track MIDI with an explicitly named melody track.
2. Authorized MusicXML/MSCZ with a clearly isolated melody part.
3. A clear, complete single-line PDF from an authorized source, subject to visual review.
4. A scan or image only when the user understands that transcription requires manual verification.

"One track" is not proof of one melody line. Evidence such as a visible track name (`Melody`, `Lyrics`, `Vocal`, `Guide Melody`, `Solo`, `Principal`, `Flute`, `Lead`) is useful but must still be tested after the user supplies the file.

## Candidate card

For every candidate, record these fields rather than making unsupported claims:

```text
Title / recognized aliases:
Composer / arranger / performer:
Version and instrument:
Source page:
Rights-use tier: Tier A / Tier B / Tier C:
Platform/uploader rights or use notice:
Normal acquisition requirement (free, login, credits, paid):
Format shown:
Complete or excerpt:
Visible melody-part evidence:
Rights / license evidence:
Price, registration, and region:
Conversion suitability:
Risks or unknowns:
Checked on:
```

Clearly separate **suitable to obtain** from **suitable to distribute derivative output**.

## User hand-off

Use wording like this after ranking candidates:

> I found these source pages with the clearest visible rights and melody information. They are choices for you to obtain from the original page; I have not downloaded or bypassed access controls. Please confirm the version, instrument, and intended use, then purchase, download, or obtain permission there and upload the file you are entitled to use. I will audit the supplied file before generating a melody MIDI or player. If you plan to publish the result, please also provide the license or permission that covers adaptation and sharing.

For a Tier B community fallback, add: "This is a technically promising community MIDI, not a verified rights-cleared source. Its page/uploader notice is recorded, but the platform does not independently guarantee it. You may choose to acquire it through the normal page for your stated private workflow; upload it for technical audit. Do not treat this result as permission to publish or redistribute derivatives."
