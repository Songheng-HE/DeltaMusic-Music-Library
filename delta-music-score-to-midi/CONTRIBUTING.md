# Contributing

Thank you for helping improve this Skill.

## What belongs in this repository

- General-purpose Skill instructions, scripts, tests, and documentation.
- Synthetic examples created for this repository, or assets whose license and required attribution are recorded in the commit.
- Bug fixes that preserve the review-first and rights-aware workflow.

## What must not be submitted

- A commercial, community, or otherwise unverified score/MIDI/recording.
- A melody-only MIDI, player script, report, manifest, screenshot, or test artifact derived from a real song unless you can document permission for public redistribution.
- Tokens, credentials, user paths, purchase receipts, account data, or browser/session data.

## Before opening a pull request

1. Keep the scope focused.
2. Add or update a meaningful test when changing deterministic Python behavior.
3. Run the commands in [the developer guide](docs/07-developer-guide.md).
4. Explain any new source/license assumption in the pull request.

## Design principles

- Do not turn uncertain OCR/vision output into asserted musical facts.
- Do not make destructive or lossy MIDI choices without an explicit, reviewable reason.
- Do not make web discovery become downloading, payment, login, or rights clearance.
- Keep generated real-input playback opt-in, dry-run first, and stoppable.
