---
name: insta-setup
description: >-
  First-run setup for instagram-growth-os: create the workspace and fill the
  brand file (voice, audience, offer, proof, pillars) that every /insta-* skill
  reads. Use when the user is new, says "set up", "onboard me", "learn my
  voice", or when ~/.instagram-growth-os/brand.md is missing or empty.
---

# insta-setup

## 1. Create the workspace

```bash
igos init            # creates ~/.instagram-growth-os/{brand.md,swipe.md,log.jsonl}
```

## 2. Fill brand.md, fastest path first

Pick whichever the user can do right now:

- **From their own content (best).** Ask for 3-5 of their own captions or Reel
  transcripts, ideally their best and their most "them". Extract: the words they
  repeat, sentence length, how they open, what they never say, how they ask.
  Quote their phrases back into the file; do not paraphrase their voice into
  yours.
- **From DMs and comments.** Ask them to paste 5-10 messages from followers or
  clients. These give the audience's own words for the problem, which beats any
  persona you could invent.
- **Interview.** Ask the brand.md questions in two batches of at most five. Do
  not ask one question per message.

## 3. Sanity-check what you wrote

- Every "proof" line is something the user confirmed is true and shareable.
- The audience line names a person in a situation, not a demographic.
- Pillars are 3-4 topics the user can talk about for a year, each tied to the
  offer.
- Hard lines are captured (regulated claims, NDAs, topics to avoid).

Show the finished brand.md, ask for corrections once, then save it.

## 4. Optional, high value

- Profile check: run `/insta-profile` next.
- Baseline: ask for an Insights CSV export and run `/insta-audit` so later plans
  are built on their numbers, not generic advice.
