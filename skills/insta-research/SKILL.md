---
name: insta-research
description: >-
  Find what is actually working in the user's niche: capture recent Reels from
  chosen accounts, rank each by its multiple over that account's own median,
  name the hook patterns, and write a swipe file the other skills use. Use for
  "what's working in my niche", "competitor research", "viral reels in X",
  "find outliers", "build a swipe file".
---

# insta-research

Raw view counts are not evidence. A 1M-follower account doing 300k is a normal
day; a 5k account doing 300k found something. Rank against each account's own
median.

## 1. Choose accounts

From brand.md (competitors / references) or ask: 5-10 accounts in the niche
plus 2-3 adjacent ones with a similar audience. Mix sizes.

## 2. Capture, by hand-speed reading only

For each account, read the 10-15 most recent Reels and note: handle, views,
the first spoken line or on-screen hook, the URL. Sources, in order of
preference:

1. The user copies the numbers from the app/web themselves.
2. If a browser tool is available, read public profile pages **at human pace,
   with the user watching**, never logged in as anyone, never in bulk.

Do not use scrapers, unofficial APIs or automated collection. That is what gets
accounts restricted and it violates Instagram's Terms.

Save as `captured.csv`:

```
handle,views,hook,url
```

## 3. Rank and write the swipe file

```bash
igos research captured.csv --md ~/.instagram-growth-os/swipe.md
```

Accounts with fewer than 3 captured Reels fall back to views/followers (if you
included a `followers` column) and are labelled as such.

## 4. Read it like an analyst

For the top 5 outliers write: the pattern, why it worked *for that audience*,
the format (talking head / B-roll / text), length, and the **transferable move**
the user could apply to their own idea. Then 3 Reel ideas for the user built on
those moves, in their voice, with their proof.

## Rules

- Never copy a script. Borrow the structure, never the words or the story.
- Small samples lie. With fewer than ~30 Reels captured, call findings "leads",
  not conclusions.
