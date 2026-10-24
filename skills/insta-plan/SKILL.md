---
name: insta-plan
description: >-
  Plan a week or month of Instagram content from the user's pillars and data:
  pieces, formats, time slots, and a daily engagement block,
  exported as a calendar (.ics) and CSV. Use for "plan my week", "content
  calendar", "what should I post this month", "posting schedule".
---

# insta-plan

## Inputs

- brand.md (pillars, offer, proof).
- The most recent `/insta-audit` output if any. **Their own data beats any
  generic "best time to post".** Without data, default to evenings in their
  audience's time zone and say so.
- `swipe.md` from `/insta-research` if present.
- Capacity: how many pieces they can actually make per week. Plan to that, not
  to an ideal.

## A sensible default week (adjust to capacity)

- 2-4 Reels (reach; at least one aimed at non-followers: specific, sendable)
- 1-2 carousels (saves and sends)
- Stories most days (one purposeful sequence, see `/insta-story`)
- 1 trial Reel when two hooks are close (see `/insta-trial`)
- Engagement: 20-30 minutes on posting days to reply to comments, plus 10
  accounts to comment on meaningfully (see `/insta-engage`)

Rotate pillars so no pillar appears twice in a row. Tie at least one piece per
week to the offer, plainly.

## Produce

1. A table: date, time, format, pillar, working title, hook pattern, ask.
2. `plan.csv` with columns `date,time,format,title,notes` (formats: reel,
   carousel, story, post, live, trial, collab), then:

```bash
igos plan plan.csv --ics instagram-plan.ics --name "IG: <month>"
```

Fix any problems it reports. The .ics imports into Google Calendar, Apple
Calendar and Outlook, with a reminder an hour before each slot.

3. For the first two pieces, offer to go straight into `/insta-reel` or
   `/insta-carousel`.

## Rules

- Never schedule or publish through unofficial tools. The calendar is a reminder;
  the user posts.
- Do not invent "best times". Use audit data or say it is a default.
