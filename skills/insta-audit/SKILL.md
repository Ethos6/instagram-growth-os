---
name: insta-audit
description: >-
  Audit the user's own Instagram performance from an Insights / Meta Business
  Suite CSV export: rank posts by sends per reach and reach multiple, compare
  formats, find opening-line patterns and posting days that work for them, and
  turn it into next steps. Use for "how are my posts doing", "analyse my
  Instagram", "what's working for me", "Insights export", "monthly report".
---

# insta-audit

## 1. Get the data

Ask the user to export it themselves (no logins, no scraping):
Meta Business Suite -> Insights -> Content -> select date range (90 days is
good) -> Export -> CSV. The professional dashboard in the app also shows
per-post insights if they need to type a few by hand into a CSV with columns
like `Description, Post type, Publish time, Views, Reach, Likes, Shares, Saves,
Comments, Follows`.

## 2. Run

```bash
igos audit export.csv
igos audit export.csv --json > audit.json   # if you need to compute more
```

Headers are matched flexibly. Missing columns just drop out of the report.

## 3. Interpret, in this order

1. **Sends per reach** is the number to grow: it is the signal most tied to
   reaching non-followers. Saves per reach for reference content. Follows per
   1k reach for conversion.
2. **Reach multiple** compares each post to the median of its own format, so a
   carousel isn't judged against a Reel.
3. **Format medians**: which format earns them reach vs. saves vs. follows.
4. **Opening-line patterns** and **days**: treat as leads when n < 5.

Then write:
```
WHAT'S WORKING     3 bullets with the numbers
WHAT ISN'T         2 bullets with the numbers
DO MORE OF         2 concrete moves (pattern + format + topic)
STOP               1 thing
TEST NEXT          1 experiment for /insta-trial
```

Save the summary to `~/.instagram-growth-os/audit-<date>.md` so `/insta-plan`
can use it.

## Rules

- Never claim causation from a handful of posts.
- Views alone are not the goal. Say so if the user's best "views" post had the
  worst sends or follows.
