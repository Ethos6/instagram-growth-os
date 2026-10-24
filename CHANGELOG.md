# Changelog

## 1.0.1 (2026-10-24)

Fixes from a full re-test (11 new regression tests, 39 total, Python 3.9-3.13).

- Inputs in UTF-16 (Excel/Notepad exports), UTF-8 with BOM or Windows-1252 no longer crash; every command decodes them.
- Empty input now exits with a clear error instead of an empty report; `igos log add` refuses to log nothing.
- Numeric-only tags like `#1` are no longer counted as hashtags.
- Humanizer: no leftover punctuation after a deleted phrase ("Stop scrolling! Here's..." -> "Here's..."); no capital forced after "..."; removed swaps that broke ordinary words (foster, harness, unlock, next level, in terms of, absolutely); fixed "a lots of".
- `--sponsored` now fails when the disclosure is hidden below "... more".
- Carousel: text overflow is reported as a FAIL; an empty source fails instead of passing.
- Installer documented as `sh install.sh` (GitHub web uploads drop the executable bit).
- Plugin icon added; marketplace description added; `claude plugin validate` passes clean.

## 1.0.0 (2026-10-24)

First release.

- 16 `/insta-*` skills: router, setup, reel, caption, carousel, story, profile,
  plan, research, humanize, engage, dm, repurpose, audit, trial, collab.
- `igos` CLI (standard library only): hook scoring, 24-pattern hook library,
  beat sheets with `.srt` export, caption lint with disclosure check, humanizer
  and five-check detector, outlier research and swipe files, Insights CSV audit,
  plan validation and `.ics` export, SVG carousel rendering (4:5 / 3:4 / 1:1),
  profile lint and rubric, post log with near-duplicate check, platform limits.
- Platform limits verified 2026-10-24.
