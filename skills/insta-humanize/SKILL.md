---
name: insta-humanize
description: >-
  Make any caption, script, comment or DM read like a person wrote it: strip
  invisible characters and typographic fingerprints, swap stock phrasing, flag
  structural tells for a manual rewrite, and score before/after. Use for
  "humanize", "this reads like AI", "de-slop", "remove em dashes", and
  before showing any drafted text to the user.
---

# insta-humanize

## Run

```bash
igos humanize post.txt -o post.clean.txt --report   # automatic passes + flags
igos detect post.txt post.clean.txt                 # before -> after
```

Automatic: invisible/format characters (emoji joiners are kept), odd spaces,
em dashes, curly quotes, ellipsis characters, and ~140 stock phrases from
the package's `igos/data/lexicon.json` (each replaced with plainer wording or dropped).

Flagged, never auto-edited: "not just X, it's Y", staged one-line reveals,
emoji bullets, triads, greeting openers, algorithm talk, preambles, hashtag
walls, engagement bait.

## Then do the human part

Rewrite every flagged line yourself, keeping the meaning and the user's voice
(brand.md). Typical fixes:

- "It's not just a tool, it's a system." -> say what it does, once.
- "The result? 3x saves." -> "Saves tripled."
- Emoji bullets -> plain lines or numbers.
- A triad that is rhythm, not content -> keep the one item that's true.

Re-run `igos detect`. PASS is 70+ overall with no check under 55. Two rounds is
normal. If five rounds still fail, the draft is built wrong: rewrite from the
user's own words instead of polishing.

## Be straight about what this is

Local heuristics across five signals: rhythm, specifics, stock phrasing, typography, voice.
Not a commercial AI detector, no API calls, and it cannot promise any detector's
verdict. Never tell the user text is "undetectable". The real goal is that a
follower reading it hears the user.
