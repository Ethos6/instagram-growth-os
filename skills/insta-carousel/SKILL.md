---
name: insta-carousel
description: >-
  Plan, write and render an Instagram carousel: a cover that earns the swipe,
  one idea per slide, a last slide with one ask, exported as 1080px SVG slides
  in 4:5 or 3:4. Use for "carousel", "slides", "swipe post", "make slides from
  this", "make an educational post".
---

# insta-carousel

Carousels are the save-and-send format. People keep them as reference, which is
why they need to be specific enough to be worth keeping.

## Structure

```
1  COVER     the promise, with a number; 4-10 words; readable in the 3:4 grid crop
2  SETUP     the problem in the reader's words (from brand.md / DMs)
3..n-1       one point per slide: headline + <= 45 words, or one visual
n-1 PROOF    a real result, screenshot description, or before/after (optional)
n  ASK       one ask: save it / send it to <specific person> / comment KEYWORD
```

7-10 slides is the usual sweet spot; the hard cap is 20. Do not pad to reach it.

## Process

1. Read brand.md. Confirm the single promise of the carousel.
2. Write `carousel.md` (slides separated by a `---` line; first line of each
   slide is the headline).
3. Lint, then render:

```bash
igos carousel carousel.md --lint-only
igos carousel carousel.md --out slides --ratio 4:5 --handle @them \
     --bg "#111111" --fg "#F5F5F0" --accent "#FFB000"
```

- `4:5` (1080x1350) is the safe default and can be boosted as an ad.
- `3:4` (1080x1440) fills the new profile grid exactly; check boostability
  before using it for anything you might promote.
- Use the brand's colours if brand.md lists them.

4. Humanize the slide copy: `igos humanize carousel.md -o carousel.md --report`
5. Then run `/insta-caption` for the caption.

The SVGs open in any browser and import into Canva, Figma or Keynote for final
polish. To get PNGs: `rsvg-convert -w 1080 slide-01.svg > slide-01.png`, or
open in a browser and export.

## Rules

- The cover must work as a thumbnail in the grid: big type, centred, nothing in
  the outer edges a 3:4 crop would cut.
- Every slide must earn the next swipe. If a slide could be deleted without
  loss, delete it.
- Numbers and names over adjectives. No invented stats.
