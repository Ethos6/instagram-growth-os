---
name: insta-reel
description: >-
  Turn one idea into a shoot-ready Instagram Reel: three scored hooks, the
  spoken script, on-screen cards, a timed beat sheet, and an .srt caption file.
  Use for "make a reel about X", "script this", "I need a hook", "what do I say
  in this video", voiceovers, talking-head or B-roll scripts.
---

# insta-reel

## Inputs to get first

Read `~/.instagram-growth-os/brand.md` and, if present, `swipe.md` (patterns
that are working in their niche now). You need **one specific true thing**:
what happened, to whom, with what number. If the idea has none, ask one batched
question for it. Do not write around the gap.

Ask (or infer from brand.md): face on camera, voiceover over B-roll, or text-only?
Target length? Default to 20-35 seconds.

## Step 1: three hooks from three different patterns

```bash
igos patterns                     # the library: template, example, card, failure mode
```

Pick three patterns that fit the idea (different families, not three rewrites
of one). For each, draft what is **said** and what is **shown** as text
(<= 6 words, readable at arm's length). Save the spoken lines one per line and
score them:

```bash
igos hook hooks.txt
```

Show the ranking. If the best is REWRITE, fix the weakest check it names or pick
a different pattern. Tell the user plainly: this is a filter for weak openers,
not a view predictor; their delivery and first frame matter more.

## Step 2: the script

Structure, one idea only:

```
HOOK      0-3s    the claim; movement in the opening shot, text visible immediately
STAKE     ~3-7s   why this matters to the viewer; one line
BODY              one point per beat; change the shot every beat
PAYOFF            keep the opening promise, ideally before the midpoint
ASK               one ask only (comment a keyword / send to someone / save / follow)
LOOP              close on a word from the opening line; rewatches feel continuous
```

Write it how the user talks (brand.md): contractions, short lines, nothing they
would need to rehearse. Put on-screen cards on their own lines prefixed with `>`.

## Step 3: time it and fix every flag

```bash
igos beats script.txt --target 30 --srt captions.srt
```

Fix: hook over 3.5s, any beat over 4.5s on one shot, three abstract beats in a
row, cards over six words, no loop, more than 2s over target. Re-run until the
only remaining note is "Loop OK". The .srt file is ready for CapCut / Edits /
Premiere burned captions (most viewers start muted).

## Step 4: originality and voice

```bash
igos log check script.txt     # near-duplicate of something already posted?
igos humanize script.txt -o script.txt --report
```

If it overlaps an earlier post, re-angle it (new example, new pattern, new format).

## Step 5: hand-off block

````
REEL READY
hook        <pattern>, <score> <verdict>
length      ~<s>s, <n> beats
cards       <n>
shot list   <one line per beat: what is on screen>
captions    captions.srt
next        /insta-caption, and /insta-trial if two hooks were close
````

Then the script in a fenced block and the shot list. On "posted", run
`igos log add script.txt --kind reel`.

## Safe zone for 1080x1920

Keep text out of the top ~220px, bottom ~420px and right ~160px. The caption,
action buttons and audio label cover those areas. `igos limits` shows the values.

## Never

- Invent a number or a client. Use `{{fact needed}}`.
- Script around trending audio the user can't license for a business account.
- Put two ideas in one Reel. Offer the second as its own Reel.
