---
name: insta-caption
description: >-
  Write or fix an Instagram caption and lint it: the feed preview before
  "... more", one ask, the 5-hashtag cap, search keywords, and sponsored
  disclosure. Use for "write a caption", "check my caption", "hashtags for
  this", "caption for this reel/carousel/photo".
---

# insta-caption

## The job of a caption

1. **The preview (~125 chars) earns the tap.** It must make sense alone and
   contain something concrete. For a Reel it should *add* to the hook, not
   repeat it.
2. **The body pays it off.** Short paragraphs. One idea.
3. **One ask.** Match it to the goal: comment a keyword (leads), send to a friend
   (reach to non-followers), save (reference content), follow (series).
4. **Search terms, not hashtag walls.** Instagram search reads captions. Put the
   2-3 phrases someone would type ("wedding photographer jaipur") into normal
   sentences. Hashtags: 0-5 specific ones; the hard cap is 5.

## Process

1. Read brand.md. Get the post's goal and the Reel script or slide copy.
2. Write **two** captions with different openers (e.g. a number-led one and a
   question-led one).
3. Lint both:

```bash
igos caption a.txt --keywords "term one,term two"
igos caption b.txt --keywords "term one,term two"
# paid, gifted or affiliate content:
igos caption a.txt --sponsored
```

4. Fix every FAIL and any WARN you agree with. Re-run.
5. `igos humanize final.txt -o final.txt --report`
6. Show the feed-preview box, the final caption in a fenced block, and the
   alt text (below).

## Alt text (always include)

One or two plain sentences describing what is actually in the image or the
first frame, including any on-image text. It helps screen-reader users and gives
Instagram another description of the post. Paste it under Advanced settings.

## Rules

- Sponsored, gifted or affiliate: use Instagram's Paid partnership label **and**
  a clear disclosure in the visible preview (`#ad` or "Paid partnership with
  @brand"). The linter fails a `--sponsored` caption without it.
- No "link in bio" plus "comment X" plus "follow" in one caption. One ask.
- Links in captions are not clickable; use the bio link or a DM keyword.
- No engagement bait ("tag a friend", "comment YES", "double tap").
