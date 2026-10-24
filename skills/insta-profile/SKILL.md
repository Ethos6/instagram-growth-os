---
name: insta-profile
description: >-
  Grade an Instagram profile on a 100-point rubric, then rewrite it fix-first: name field,
  bio, link, pinned posts, highlights, grid. Use for "review my profile", "fix
  my bio", "why don't people follow", "optimize my Instagram profile",
  "what should I pin".
---

# insta-profile

A visitor decides in a few seconds, from the top of the profile. Score what they
see.

## 1. Collect

Ask for: handle, name field, bio (exact text), link(s), what the 3 pinned posts
are, highlight names, and a screenshot or description of the top 9 grid posts.
Read brand.md for the audience and offer.

## 2. Run the automatic checks

```bash
igos profile --name "Name | Keyword" --bio "line one\nline two\nline three" \
             --links 1 --keywords "what they do,city"
```

## 3. Score with the rubric

```bash
igos profile --rubric
```

Score each item 0..max with a one-line reason. Items marked `auto` should agree
with the linter. Total out of 100.

## 4. Output, fix-first

```
PROFILE SCORE  62/100
biggest losses first:
  -12 who:      first line says "Creative soul" -> say who you help with what
  -10 pinned:   pins are 2023 event photos -> pin origin / best teaching / offer
  ...
```

Then the rewritten **name field** (searchable keyword in it, <= 64 chars), **three
bio options** (<= 150 chars each, proof point, one next step that matches the
link), the **three posts to pin** (from their existing posts if possible), and
**highlight set** (e.g. Start here / Results / Offer / FAQ).

## Rules

- Bio proof must be real. Ask before using a number or client name.
- No hashtags in the bio; they send visitors away.
- One link destination that matches the bio's promise. More links = less clicks.
