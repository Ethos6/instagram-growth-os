"""Turn a content plan into calendar events (.ics) you can import anywhere.

Plan format: CSV with columns  date,time,format,title,notes
  date   YYYY-MM-DD
  time   HH:MM (24h, local time; optional, default 18:00)
  format reel / carousel / story / post / live
"""

from __future__ import annotations

import csv
import hashlib
import io
from datetime import datetime, timedelta, timezone

FORMATS = {"reel", "carousel", "story", "post", "live", "trial", "collab"}


def read_plan(raw: str) -> tuple[list[dict], list[str]]:
    reader = csv.DictReader(io.StringIO(raw.lstrip("\ufeff")))
    items, problems = [], []
    for i, r in enumerate(reader, 2):
        r = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
        try:
            day = datetime.strptime(r.get("date", ""), "%Y-%m-%d")
        except ValueError:
            problems.append(f"row {i}: bad or missing date {r.get('date')!r}")
            continue
        t = r.get("time") or "18:00"
        try:
            hh, mm = (int(x) for x in t.split(":"))
            start = day.replace(hour=hh, minute=mm)
        except ValueError:
            problems.append(f"row {i}: bad time {t!r}")
            continue
        fmt = (r.get("format") or "post").lower()
        if fmt not in FORMATS:
            problems.append(f"row {i}: unknown format {fmt!r} (use one of {', '.join(sorted(FORMATS))})")
        items.append({"start": start, "format": fmt, "title": r.get("title") or fmt, "notes": r.get("notes", "")})
    return items, problems


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line: str) -> str:
    out, cur = [], line
    while len(cur.encode("utf-8")) > 75:
        cut = 75
        while len(cur[:cut].encode("utf-8")) > 75:
            cut -= 1
        out.append(cur[:cut])
        cur = " " + cur[cut:]
    out.append(cur)
    return "\r\n".join(out)


def to_ics(items: list[dict], calname: str = "Instagram plan", minutes: int = 30, alarm: int = 60) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//instagram-growth-os//igos//EN",
             "CALSCALE:GREGORIAN", f"X-WR-CALNAME:{_esc(calname)}"]
    for it in items:
        uid = hashlib.sha1(f"{it['start']}{it['title']}".encode()).hexdigest()[:16] + "@igos"
        end = it["start"] + timedelta(minutes=minutes)
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{stamp}",
            f"DTSTART:{it['start'].strftime('%Y%m%dT%H%M%S')}",
            f"DTEND:{end.strftime('%Y%m%dT%H%M%S')}",
            f"SUMMARY:{_esc('[' + it['format'].upper() + '] ' + it['title'])}",
            f"DESCRIPTION:{_esc(it['notes'] + chr(10) + 'Post manually. Reply to comments for the first hour.')}",
            "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{_esc(it['title'])}",
            f"TRIGGER:-PT{alarm}M", "END:VALARM",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(l) for l in lines) + "\r\n"


def balance(items: list[dict]) -> list[str]:
    """Simple sanity notes on a week's mix."""
    notes = []
    counts: dict[str, int] = {}
    for it in items:
        counts[it["format"]] = counts.get(it["format"], 0) + 1
    if counts:
        notes.append("mix: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    if items and counts.get("reel", 0) == 0:
        notes.append("no Reels planned; Reels are where non-followers find you")
    if items and counts.get("carousel", 0) == 0:
        notes.append("no carousels; they are the save-and-send format")
    days: dict[str, int] = {}
    for it in items:
        d = it["start"].strftime("%Y-%m-%d")
        days[d] = days.get(d, 0) + (0 if it["format"] == "story" else 1)
    heavy = [d for d, n in days.items() if n > 2]
    if heavy:
        notes.append(f"more than 2 feed posts on {', '.join(heavy)}; they compete with each other")
    return notes
