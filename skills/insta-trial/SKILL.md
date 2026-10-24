---
name: insta-trial
description: >-
  Design and read a clean experiment with Instagram trial Reels (shown to
  non-followers first): one variable, a hypothesis, a decision rule, and a log.
  Use for "test two hooks", "trial reels", "A/B test", "which version should I
  post", "experiment".
---

# insta-trial

Trial Reels let a professional account show a Reel to non-followers first, then
share it to followers later if it does well. Use them to test, not to dump
drafts. Check the current availability and options in the app: the feature
changes.

## Design

1. **One variable.** Hook line, first frame, length, or caption. Never two at
   once.
2. **Hypothesis.** "A number-led hook will beat a question hook on 3-second
   hold for this topic."
3. **Metric and decision rule, written before posting.** Primary: sends per
   reach or 3-second hold. Example: "Ship B to followers if its sends per reach
   is at least 1.3x A's after 72 hours, otherwise keep A."
4. **Same conditions.** Same day of week and hour where possible; post both
   within 24-48h.

Build both versions with `/insta-reel`. Score both hooks (`igos hook`) and note
the scores; the experiment tells you whether the scorer agrees with *your*
audience.

## Read

After 72 hours collect reach, 3-second hold / average watch time, sends, saves,
follows for each. Report the decision the rule makes. Then:

```bash
igos log add winner.txt --kind trial
```

and add one line to `~/.instagram-growth-os/experiments.md`:
`date | variable | A | B | metric A | metric B | decision | lesson`.

## Rules

- Single tests are noisy. Call a pattern "proven" only after it wins 3+ times.
- Trial reach is not the same audience as follower reach; an idea can win one
  and lose the other.
- Don't re-upload the same Reel repeatedly hoping for a different result; that
  reads as duplicate content. Change the variable.
