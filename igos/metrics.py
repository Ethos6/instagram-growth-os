"""Two analyses on CSV files you already have. Nothing is fetched.

research : reels you noted down from other accounts -> outlier ranking + swipe file
audit    : your own Instagram Insights export -> what actually earned reach

View counts alone mislead: a big account's slow day outscores a small
account's breakout. Everything here is ranked against each account's (or each format's)
own median.
"""

from __future__ import annotations

import csv
import io
import re
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from . import text as T
from .hooks import classify

ALIASES = {
    "handle": ["handle", "account", "accountusername", "username", "creator", "account_name"],
    "views": ["views", "plays", "videoviews", "impressions", "reelsplays", "initialplays"],
    "reach": ["reach", "accountsreached"],
    "likes": ["likes", "reactions"],
    "comments": ["comments"],
    "shares": ["shares", "sends", "sendsviadm"],
    "saves": ["saves", "saved"],
    "follows": ["follows", "followsfrompost", "newfollowers"],
    "followers": ["followers", "followercount"],
    "hook": ["hook", "firstline", "transcript", "openingline"],
    "caption": ["description", "caption", "text", "title"],
    "type": ["posttype", "mediatype", "type", "format"],
    "published": ["publishtime", "published", "date", "posted", "createdtime", "timestamp"],
    "url": ["permalink", "url", "link"],
    "duration": ["durationsec", "duration", "length"],
}


def _norm(h: str) -> str:
    return re.sub(r"[^a-z0-9]", "", h.lower())


def _num(v: str | None) -> float | None:
    if v is None:
        return None
    s = str(v).strip().replace(",", "")
    if not s or s in ("-", "--", "n/a", "NA"):
        return None
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*([kKmM]?)", s)
    if not m:
        return None
    x = float(m.group(1))
    return x * {"": 1, "k": 1e3, "K": 1e3, "m": 1e6, "M": 1e6}[m.group(2)]


def read_rows(raw: str) -> list[dict]:
    """Read a CSV/TSV with flexible headers into canonical keys."""
    # Meta exports sometimes start with a BOM and use commas; captures may be TSV
    raw = raw.lstrip("﻿")
    first = raw.splitlines()[0] if raw.strip() else ""
    dialect = "excel-tab" if first.count("\t") > first.count(",") else "excel"
    reader = csv.DictReader(io.StringIO(raw), dialect=dialect)
    headers = {_norm(h): h for h in (reader.fieldnames or [])}
    mapping = {}
    for key, al in ALIASES.items():
        for a in al:
            if a in headers:
                mapping[key] = headers[a]
                break
    rows = []
    for r in reader:
        row = {k: (r.get(src) or "").strip() for k, src in mapping.items()}
        rows.append(row)
    return rows


def _median(xs: list[float]) -> float:
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else 0.0


# --------------------------------------------------------------------------- #
# research
# --------------------------------------------------------------------------- #


@dataclass
class Outlier:
    handle: str
    views: float
    multiple: float
    basis: str
    hook: str
    pattern: str | None
    url: str = ""


def research(rows: list[dict], min_posts: int = 3) -> list[Outlier]:
    by_acct: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        if _num(r.get("views")) is not None:
            by_acct[r.get("handle") or "?"].append(r)
    out: list[Outlier] = []
    for handle, rs in by_acct.items():
        med = _median([_num(r["views"]) for r in rs])
        for r in rs:
            v = _num(r["views"]) or 0
            hook = r.get("hook") or (r.get("caption") or "").split("\n")[0]
            fol = _num(r.get("followers"))
            if len(rs) >= min_posts and med > 0:
                mult, basis = v / med, "account median"
            elif fol:
                mult, basis = v / fol, "views/followers (few posts)"
            else:
                mult, basis = 1.0, "no baseline"
            out.append(Outlier(handle, v, mult, basis, hook, classify(hook)[0] if hook else None, r.get("url", "")))
    return sorted(out, key=lambda o: o.multiple, reverse=True)


def research_summary(outs: list[Outlier]) -> list[str]:
    if len(outs) < 6:
        return ["Fewer than 6 reels: capture more before reading patterns into this."]
    k = len(outs) // 3
    top, bottom = outs[:k], outs[-k:]

    def dist(group: list[Outlier]) -> dict[str, int]:
        d: dict[str, int] = defaultdict(int)
        for o in group:
            d[o.pattern or "unclassified"] += 1
        return d

    dt, db = dist(top), dist(bottom)
    lines = []
    for p in sorted(set(dt) | set(db), key=lambda p: dt.get(p, 0) - db.get(p, 0), reverse=True):
        if dt.get(p, 0) != db.get(p, 0):
            lines.append(f"{p}: {dt.get(p, 0)} in top third vs {db.get(p, 0)} in bottom third")
    tc = statistics.mean(1 if T.concrete_markers(o.hook) else 0 for o in top)
    bc = statistics.mean(1 if T.concrete_markers(o.hook) else 0 for o in bottom)
    lines.append(f"hooks with a number or name: {tc:.0%} of top third vs {bc:.0%} of bottom third")
    return lines


def render_research(outs: list[Outlier], limit: int = 25) -> str:
    accts = len({o.handle for o in outs})
    out = [f"OUTLIERS  {len(outs)} reels  {accts} accounts", "=" * 78]
    for o in outs[:limit]:
        out.append(f"  {o.multiple:6.1f}x  {o.pattern or '-':<22} @{o.handle:<18} {int(o.views):>11,}")
        out.append(f"           \"{T.shorten(o.hook, 66)}\"")
    out.append("-" * 78)
    out += ["  " + s for s in research_summary(outs)]
    return "\n".join(out)


def swipe_markdown(outs: list[Outlier], limit: int = 30) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    md = [f"# Swipe file ({today})", "", "Each reel is scored against the median of its own account.", "",
          "| x | pattern | account | hook | link |", "|---:|---|---|---|---|"]
    for o in outs[:limit]:
        hook = o.hook.replace("|", "/")
        link = f"[open]({o.url})" if o.url else ""
        md.append(f"| {o.multiple:.1f} | {o.pattern or '-'} | @{o.handle} | {hook} | {link} |")
    md += ["", "## What separates the top third", ""] + [f"- {s}" for s in research_summary(outs)]
    return "\n".join(md) + "\n"


# --------------------------------------------------------------------------- #
# audit
# --------------------------------------------------------------------------- #


@dataclass
class Post:
    row: dict
    kind: str
    views: float
    reach: float
    rates: dict[str, float] = field(default_factory=dict)
    multiple: float = 1.0
    published: datetime | None = None

    @property
    def first_line(self) -> str:
        return (self.row.get("caption") or "").strip().split("\n")[0]


def _parse_dt(s: str) -> datetime | None:
    for fmt in ("%m/%d/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%m/%d/%Y"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def audit(rows: list[dict]) -> list[Post]:
    posts: list[Post] = []
    for r in rows:
        views = _num(r.get("views")) or 0
        reach = _num(r.get("reach")) or views
        if not reach:
            continue
        p = Post(r, (r.get("type") or "post").strip().lower() or "post", views, reach)
        for k in ("shares", "saves", "likes", "comments", "follows"):
            v = _num(r.get(k))
            if v is not None:
                p.rates[k] = v / reach * (1000 if k == "follows" else 100)
        p.published = _parse_dt(r.get("published", ""))
        posts.append(p)
    by_kind: dict[str, list[Post]] = defaultdict(list)
    for p in posts:
        by_kind[p.kind].append(p)
    for kind, ps in by_kind.items():
        med = _median([p.reach for p in ps])
        for p in ps:
            p.multiple = p.reach / med if med else 1.0
    return posts


def render_audit(posts: list[Post], top: int = 5) -> str:
    if not posts:
        return "No usable rows. Export from Instagram Insights / Meta Business Suite as CSV and pass the file."
    out = [f"AUDIT  {len(posts)} posts", "=" * 78]
    kinds: dict[str, list[Post]] = defaultdict(list)
    for p in posts:
        kinds[p.kind].append(p)
    out.append("BY FORMAT (medians)            reach   sends%   saves%  follows/1k")
    for k, ps in sorted(kinds.items(), key=lambda kv: -len(kv[1])):
        out.append(
            f"  {k[:22]:<22} n={len(ps):<4} {int(_median([p.reach for p in ps])):>8,}"
            f"  {_median([p.rates.get('shares') for p in ps]):6.2f}  {_median([p.rates.get('saves') for p in ps]):7.2f}"
            f"  {_median([p.rates.get('follows') for p in ps]):9.2f}"
        )
    has_shares = any("shares" in p.rates for p in posts)
    key = (lambda p: p.rates.get("shares", 0)) if has_shares else (lambda p: p.multiple)
    label = "sends per reach" if has_shares else "reach multiple"
    ranked = sorted(posts, key=key, reverse=True)
    out.append("")
    out.append(f"TOP {top} BY {label.upper()}  (sends reach non-followers; this is the number to grow)")
    for p in ranked[:top]:
        out.append(f"  {p.rates.get('shares', 0):5.2f}%  {p.multiple:4.1f}x  {p.kind[:8]:<8} {T.shorten(p.first_line or '(no caption)', 50)}")
    out.append(f"BOTTOM {top}")
    for p in ranked[-top:]:
        out.append(f"  {p.rates.get('shares', 0):5.2f}%  {p.multiple:4.1f}x  {p.kind[:8]:<8} {T.shorten(p.first_line or '(no caption)', 50)}")
    dated = [p for p in posts if p.published]
    if len(dated) >= 10:
        by_day: dict[str, list[float]] = defaultdict(list)
        for p in dated:
            by_day[p.published.strftime("%a")].append(p.multiple)
        out.append("")
        out.append("DAY OF WEEK (median reach multiple; small samples lie, needs 3+ per day)")
        for d in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"):
            if len(by_day.get(d, [])) >= 3:
                out.append(f"  {d}  {_median(by_day[d]):4.2f}x  n={len(by_day[d])}")
    pats: dict[str, list[float]] = defaultdict(list)
    for p in posts:
        pats[classify(p.first_line)[0] or "unclassified"].append(p.multiple)
    if len(pats) > 1:
        out.append("")
        out.append("OPENING-LINE PATTERN (median reach multiple)")
        for name, ms in sorted(pats.items(), key=lambda kv: -_median(kv[1])):
            out.append(f"  {_median(ms):4.2f}x  n={len(ms):<3} {name}")
    return "\n".join(out)
