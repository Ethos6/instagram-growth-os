---
name: insta
description: >-
  Router for instagram-growth-os. Use when the user asks for Instagram help
  without naming a specific task ("help with my Instagram", "what should I post",
  "grow my account", "I'm stuck on IG"), and pick the right /insta-* skill.
---

# insta: the router

Decide what the user needs, then follow that skill's SKILL.md. Do not do the work
from memory when a dedicated skill exists.

| The user says... | Use |
| --- | --- |
| first time, "set this up", no brand file yet | `/insta-setup` |
| "script a reel", "I need a hook", "what do I say" | `/insta-reel` |
| "write the caption", "check my caption" | `/insta-caption` |
| "carousel", "slides", "swipe post" | `/insta-carousel` |
| "stories", "story sequence", "poll ideas" | `/insta-story` |
| "fix my bio", "profile review" | `/insta-profile` |
| "plan my week/month", "content calendar" | `/insta-plan` |
| "what's working in my niche", "competitors" | `/insta-research` |
| "sounds like AI", "humanize", "clean this up" | `/insta-humanize` |
| "comment on X", "reply to my comments" | `/insta-engage` |
| "DM", "keyword auto-reply", "follow-up" | `/insta-dm` |
| "turn this video/podcast/blog into posts" | `/insta-repurpose` |
| "how did my posts do", Insights export | `/insta-audit` |
| "test two hooks", "trial reels" | `/insta-trial` |
| "brand deal", "collab post", "sponsored" | `/insta-collab` |

## Ground rules shared by every /insta-* skill

1. **Read `~/.instagram-growth-os/brand.md` first.** If it is missing or empty,
   run `/insta-setup` (it takes ten minutes) unless the user only wants a quick
   one-off; then ask the two questions that matter most: who is this for, and
   what is one real result you can share.
2. **Never post, log in, follow, like, comment or DM on the user's behalf.**
   The skills write; the user publishes. Automating actions on Instagram outside
   the official API breaks its Terms and gets accounts restricted.
3. **Never invent proof.** No made-up numbers, clients, testimonials or results.
   If a draft needs a fact you don't have, write `{{fact needed: ...}}` and ask.
4. **Run the tools, don't eyeball.** `igos` is a local CLI (no network). If the
   `igos` command is missing, use `python3 -m igos` from the repo folder or
   `python3 <repo>/igos_run.py`. Install with
   `pip install git+https://github.com/Ethos6/instagram-growth-os`.
5. **Everything shown to the user goes through `igos humanize` first.**
6. **Platform numbers drift.** `igos limits` prints the limits the tools enforce
   and the date they were checked. If Instagram's app disagrees, the app wins.
