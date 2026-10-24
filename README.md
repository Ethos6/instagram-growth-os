# instagram-growth-os

**Run an Instagram account with Claude.** 16 skills that write your Reels,
captions, carousels, stories, DMs and plans, and a local command-line tool,
`igos`, that checks the work before you post it.

- **It never posts for you.** The skills write and you publish, so the approval
  step can't be skipped. Nothing logs in, scrapes or automates actions on
  Instagram.
- **Standard Python only.** No dependencies, no API keys, no network calls.
  Python 3.9+.
- **Uses your own numbers.** `igos audit` reads your Insights export. Plans and
  ideas are built on what works for *your* audience, not generic best-time charts.
- **Platform limits checked October 2026.** The tools enforce the 5-hashtag cap,
  20-slide carousels, 150-character bios and the new 3:4 grid. `igos limits`
  shows each limit and its source.

---

## Install

**As a Claude Code plugin**

```
/plugin marketplace add Ethos6/instagram-growth-os
/plugin install instagram-growth-os@ethos6
pip install git+https://github.com/Ethos6/instagram-growth-os   # the igos CLI
```

**Or with the script** (copies the skills into `~/.claude/skills` and installs `igos`)

```bash
git clone https://github.com/Ethos6/instagram-growth-os.git
cd instagram-growth-os && sh install.sh        # add --project for ./.claude/skills
```

**Or just ask Claude**

```
Install https://github.com/Ethos6/instagram-growth-os, then run /insta-setup.
```

No install possible? Paste any `skills/*/SKILL.md` into a chat and it works as a
prompt. You lose the tool checks, but the method still applies.

**Then spend ten minutes on `/insta-setup`.** It creates
`~/.instagram-growth-os/brand.md` (your voice, audience, offer, real proof and
pillars). Every skill reads that file, and it's the biggest single factor in
quality.

---

## The skills

| Command | What you get |
| --- | --- |
| `/insta` | Router. Describe the problem and it picks the right skill. |
| `/insta-setup` | Workspace and brand file, built from your own captions, DMs or a short interview. |
| `/insta-reel` | One idea in, a shoot-ready Reel out: three scored hooks, script, on-screen cards, timed beat sheet, `.srt` captions, shot list. |
| `/insta-caption` | Two caption options, each linted: the feed preview, one ask, search terms, hashtag cap, sponsored disclosure, alt text. |
| `/insta-carousel` | Cover, slides, ask, rendered to **1080px SVG slides** in 4:5 or 3:4 with your colours. |
| `/insta-story` | Story *sequences* with a job each, the right sticker per frame, and a hand-off to DMs. |
| `/insta-profile` | 100-point profile score, then rewrites ordered by what loses the most points: name field, bio, pins, highlights. |
| `/insta-plan` | The week or month as a table plus an **`.ics` calendar** with reminders. |
| `/insta-research` | Reels in your niche ranked against *each account's own* typical result, with the hook pattern named and a swipe file written. |
| `/insta-humanize` | Strips invisible characters, typography tells and stock phrasing, flags structural tells, scores before and after. |
| `/insta-engage` | Comments worth pinning on other people's posts, and triaged replies under yours. |
| `/insta-dm` | Keyword deliveries, warm openers, collab pitches, and two follow-ups at most. |
| `/insta-repurpose` | A video, podcast or post turned into standalone Reels and carousels, with duplicate checks. |
| `/insta-audit` | Your Insights CSV ranked by **sends per reach**, compared by format, with patterns and days that work for you. |
| `/insta-trial` | Trial Reel experiments with one variable, a decision rule set in advance, and a log. |
| `/insta-collab` | Collab posts and brand deals: brief, usage rights, and a disclosure that's actually visible. |

---

## The `igos` CLI

Every command takes a file (or `-` for stdin) and supports `--json`.

```
igos init        create ~/.instagram-growth-os with brand.md
igos hook        score and rank hooks
igos patterns    the 24-pattern hook library
igos beats       time a script, flag drop-off risks, export .srt
igos caption     lint a caption, preview the feed cut
igos humanize    clean a draft, report changes and tells
igos detect      five reads-human checks, before/after
igos research    rank captured reels by outlier multiple, write a swipe file
igos audit       analyse your Insights CSV export
igos plan        validate a plan CSV, export .ics
igos carousel    lint and render slides to SVG
igos profile     lint name field and bio; --rubric prints the 100-point rubric
igos log         post log + near-duplicate check before you post
igos limits      the platform limits enforced, with sources
```

Not installed? Run `python3 igos_run.py <command>` from the repo folder.

### Hooks

```
$ igos hook examples/hooks.txt
HOOK RANKING  (a filter for weak openers, not a view predictor)
==============================================================================
->  79.1  STRONG   You lost your best client over a two-day reply time. He...
         3.9s  pattern: -  weakest: TENSION (70)
    78.7  STRONG   Skipping a deposit cost me $6,400 last spring.
         3.8s  pattern: Price of a Mistake  weakest: FRONT (73)
    63.4  USABLE   Two years of posting taught me one thing: reach follows...
         3.0s  pattern: -  weakest: TENSION (35)
    59.2  USABLE   Why do your best posts get the fewest saves?
         2.5s  pattern: Pointed Why  weakest: CONCRETE (15)
    35.2  REWRITE  Here are some tips for better engagement.
         2.5s  pattern: -  weakest: CONCRETE (15)
     4.8  REWRITE  Don't scroll past this if you care about growing your p...
         2.6s  pattern: Quit This  weakest: CONCRETE (15)
         x Begs for attention instead of earning it.
         x Hashtags or emoji in a spoken line. Nobody can say them.
     0.0  REWRITE  Hi everyone, so today I want to talk about my content p...
         3.7s  pattern: -  weakest: FRONT (10)
         x Opens with a hello. Skip it; the viewer is already deciding.
         x Preamble ('in this video', 'I want to talk about'). Start at the point.
```

Five checks: **PACE** (syllable-based speaking time), **CONCRETE** (numbers
written or spoken, money, names), **FRONT** (how early the first loaded word
arrives), **TENSION** (stakes, or a known pattern) and **AIM** (who it speaks
to). The overall score weights the weakest check, and dealbreakers cost
points.

**What it is and isn't:** a fast filter for openers that lose people (greetings,
preambles, nothing concrete, too long to say). It doesn't predict views, and no
text-only tool can. Your face, first frame, audio and distribution decide that.
Use `/insta-trial` and `igos audit` to see which patterns work for your
audience.

### Beat sheets and captions

```
$ igos beats examples/script.txt --target 25 --srt captions.srt
BEAT SHEET  59 words  ~21.2s  5.0 syll/s  target 25s
==============================================================================
 0:00.0  3.8s  HOOK   Skipping a deposit cost me $6,400 last spring.
                      [card] $6,400 LESSON
 0:03.8  2.8s         The client loved the first draft, then went quiet f...
 ...
 0:16.7  4.6s  PAYOFF That one line in the contract has already paid for...
------------------------------------------------------------------------------
- Hook takes 3.8s. Cut it under 3.5s or the swipe happens mid-sentence.
- Beat 6 runs 4.6s on one shot. Split it or cut to a new frame inside it.
- Loop OK: the last beat echoes '6,400' from the hook.
```

Lines starting with `>` are on-screen cards. `--srt` writes short caption chunks
timed to the script, ready to burn in with any editor.

### Caption lint

```
$ igos caption examples/caption.txt --keywords "freelance contract,deposit"
  WHAT THE FEED SHOWS
  +----------------------------------------------------------+
  | Skipping a deposit cost me $6,400 last spring. Here's    |
  | the one line I added to every contract after.            |
  +------------------------------------------------ ... more +

  PASS  LENGTH           374 / 2200 characters
  PASS  FIRST LINE       99 characters, fits the preview
  PASS  CONCRETE OPENER  1 number/name in the preview
  PASS  HASHTAGS         3/5
  PASS  ONE ASK          comment keyword
  WARN  SEARCH TERMS     1/2 search terms present; missing: freelance contract
```

`--sponsored` fails any paid or gifted caption that lacks a disclosure in the
visible preview.

### Humanizer

```
$ igos detect examples/slop.txt examples/rewrite.txt
  RHYTHM      100.0 ->  73.3
  SPECIFICS    49.9 -> 100.0
  STOCK         0.0 -> 100.0
  TYPOGRAPHY    0.0 -> 100.0
  VOICE         0.0 ->  72.9
  OVERALL      18.0 ->  82.7   FLAGGED -> PASS
```

`igos humanize` removes zero-width and other format characters (it keeps the
joiners inside emoji), converts em dashes and curly quotes, and swaps about 140
stock phrases listed in [`igos/data/lexicon.json`](igos/data/lexicon.json).
Edit that file freely. Structural tells are **flagged for you to rewrite**,
never mangled by a regex. These are local heuristics, not a commercial AI
detector, and no tool can honestly promise "undetectable".

### Audit your own account

```
$ igos audit examples/insights_export.csv   # synthetic example data
BY FORMAT (medians)            reach   sends%   saves%  follows/1k
  ig reel                n=7       8,913    0.66     1.57       0.96
  ig carousel            n=8      13,593    1.23     1.24       0.96
TOP 5 BY SENDS PER REACH  (sends reach non-followers; this is the number to grow)
  ...
OPENING-LINE PATTERN (median reach multiple)
  2.17x  n=1   The Quiet Part
  ...
```

Export from Meta Business Suite → Insights → Content → Export. Column names are
matched flexibly.

### Carousels to SVG

```
igos carousel examples/carousel.md --out slides --ratio 3:4 --handle @you --accent "#FFB000"
```

You get one SVG per slide, sized 1080×1350 (4:5) or 1080×1440 (3:4). Open them
in a browser, Canva or Figma, or convert with `rsvg-convert`.

---

## Data you can edit

| File | What |
| --- | --- |
| `igos/data/hooks.json` | 24 hook patterns in 5 families: template, example, card, when to use, failure mode, regex |
| `igos/data/lexicon.json` | stock-phrase swaps, structural tells, typography map |
| `igos/data/platform.json` | limits and sizes, with check date and sources |
| `igos/data/profile_rubric.json` | the 100-point profile rubric |
| `~/.instagram-growth-os/brand.md` | your voice, audience, offer, proof, pillars |

## Ground rules built into every skill

1. **No automation of Instagram actions.** Posting, following, liking,
   commenting and DMing stay manual. The only automated DMs suggested are
   keyword replies through Instagram's own tools or Meta-approved partners,
   after the person messages first.
2. **No invented proof.** Missing facts come back as `{{fact needed: ...}}`.
3. **Disclosure is visible.** Paid, gifted and affiliate content uses the Paid
   partnership label *and* a plain disclosure before "... more".
4. **Your data over generic advice.** Any "best time" or "best format" claim
   comes from `igos audit` on your own export, or is labelled as a default.
5. **Platform numbers drift.** If the app disagrees with `igos limits`, the app
   is right. Please open a PR.

## Development

```bash
python3 -m unittest discover -s tests -v
```

CI runs the tests on Python 3.9, 3.11 and 3.13 and checks every skill's
frontmatter. Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT © 2026 Ethos6
