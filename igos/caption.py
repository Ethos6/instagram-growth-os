"""Caption linter. Shows what the feed actually shows before '... more', then
runs the checks that decide whether anyone taps it.
"""

from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass

from . import text as T

CTA_PATTERNS = {
    "comment keyword": r"\bcomment\b[^.!?\n]{0,25}(?:\"[^\"]+\"|'[^']+'|\b[A-Z]{3,}\b)|\b(?:type|drop|reply)\s+(?:\"[^\"]+\"|'[^']+'|\b[A-Z]{3,}\b)",
    "save": r"\bsave (?:this|it|for later|the post)\b",
    "share/send": r"\b(?:send|share) (?:this|it) (?:to|with)\b",
    "follow": r"\bfollow (?:for|me|@|along)\b",
    "link": r"\blink in (?:my )?bio\b|\btap the link\b",
    "dm": r"\b(?:dm|message) me\b",
    "question": r"\?\s*(?:\n|$)",
}
DISCLOSURE_RE = re.compile(r"#(?:ad|sponsored|paidpartnership|partner)\b|\bpaid partnership\b|\bsponsored by\b|\bgifted\b|\b#gifted\b", re.I)
BAIT_RE = re.compile(r"\b(?:tag (?:a friend|someone)|double tap|like if|comment yes|follow for more|share if you agree)\b", re.I)


@dataclass
class Check:
    status: str  # PASS WARN FAIL
    name: str
    detail: str


def feed_preview(caption: str, limit: int = 125) -> tuple[str, bool]:
    """What shows before '... more'. Line breaks also truncate: the feed shows
    roughly two lines, so a hard break after line one shortens the window."""
    lines = caption.strip().splitlines()
    if not lines:
        return "", False
    first_two = "\n".join(lines[:2])
    visible = first_two[:limit]
    truncated = len(caption.strip()) > len(visible)
    return visible, truncated


def lint(caption: str, keywords: list[str] | None = None, sponsored: bool = False) -> list[Check]:
    lim = T.load_data("platform.json")["limits"]
    checks: list[Check] = []
    n = len(caption)
    cap = lim["caption_chars"]["value"]
    checks.append(Check("PASS" if n <= cap else "FAIL", "LENGTH", f"{n} / {cap} characters"))

    first = caption.strip().splitlines()[0] if caption.strip() else ""
    if len(first) <= 125:
        checks.append(Check("PASS", "FIRST LINE", f"{len(first)} characters, fits the preview"))
    else:
        checks.append(Check("WARN", "FIRST LINE", f"{len(first)} characters, cut mid-thought at ~125"))

    visible, _ = feed_preview(caption)
    markers = T.concrete_markers(visible)
    checks.append(
        Check("PASS" if markers else "WARN", "CONCRETE OPENER",
              f"{len(markers)} number/name in the preview" if markers else "nothing countable before '... more'")
    )
    if re.match(r"^\s*(?:hey|hi|hello|happy \w+day|new post|so,|okay)\b", visible, re.I):
        checks.append(Check("FAIL", "OPENER", "starts with a greeting or throat-clearing"))

    tags = T.hashtags(caption)
    tcap = lim["hashtags_per_post"]["value"]
    if len(tags) > tcap:
        checks.append(Check("FAIL", "HASHTAGS", f"{len(tags)} tags; the cap is {tcap}. Extra tags may block posting."))
    else:
        generic = [t for t in tags if t.lower() in ("#reels", "#explore", "#explorepage", "#viral", "#fyp", "#instagood", "#trending")]
        status = "WARN" if generic else "PASS"
        detail = f"{len(tags)}/{tcap}" + (f"; generic tags do nothing: {' '.join(generic)}" if generic else "")
        checks.append(Check(status, "HASHTAGS", detail))

    ms = T.mentions(caption)
    mcap = lim["mentions_per_post"]["value"]
    if len(ms) > mcap:
        checks.append(Check("FAIL", "MENTIONS", f"{len(ms)}; cap is {mcap}"))

    ctas = [name for name, pat in CTA_PATTERNS.items() if re.search(pat, caption, re.I | re.M)]
    if not ctas:
        checks.append(Check("WARN", "ONE ASK", "no call to action"))
    elif len([c for c in ctas if c != "question"]) > 1:
        checks.append(Check("WARN", "ONE ASK", f"{len(ctas)} asks compete: {', '.join(ctas)}. Keep one."))
    else:
        checks.append(Check("PASS", "ONE ASK", ctas[0]))

    if BAIT_RE.search(caption):
        checks.append(Check("WARN", "BAIT", "engagement bait phrasing; Instagram demotes it and readers skip it"))

    if T.URL_RE.search(caption):
        checks.append(Check("WARN", "LINK", "links in captions are not clickable"))

    if keywords:
        low = caption.lower()
        missing = [k for k in keywords if k.lower() not in low]
        status = "PASS" if not missing else "WARN"
        detail = f"{len(keywords) - len(missing)}/{len(keywords)} search terms present"
        if missing:
            detail += f"; missing: {', '.join(missing)}"
        checks.append(Check(status, "SEARCH TERMS", detail))

    if sponsored and not DISCLOSURE_RE.search(caption):
        checks.append(Check("FAIL", "DISCLOSURE", "sponsored post with no disclosure. Use the Paid partnership label and say #ad up front."))
    elif DISCLOSURE_RE.search(caption):
        idx = DISCLOSURE_RE.search(caption).start()
        if idx > 125:
            checks.append(Check("FAIL" if sponsored else "WARN", "DISCLOSURE", "disclosure is hidden behind '... more'; move it into the preview"))
        else:
            checks.append(Check("PASS", "DISCLOSURE", "visible in the preview"))

    em = T.emojis(caption)
    if T.words(caption) and len(em) / max(1, len(T.words(caption))) > 0.12:
        checks.append(Check("WARN", "EMOJI", f"{len(em)} emoji; reads as decoration, not voice"))

    shouty = re.findall(r"\b[A-Z]{4,}\b", caption)
    if len(shouty) >= 4:
        checks.append(Check("WARN", "CAPS", f"{len(shouty)} all-caps words"))

    longest = max((len(p) for p in caption.split("\n\n")), default=0)
    if longest > 400:
        checks.append(Check("WARN", "WALL", f"a {longest}-char block with no break; split it"))
    return checks


def render(caption: str, checks: list[Check]) -> str:
    visible, truncated = feed_preview(caption)
    out = ["  WHAT THE FEED SHOWS"]
    width = 56
    out.append("  +" + "-" * (width + 2) + "+")
    for para in visible.splitlines() or [""]:
        for ln in textwrap.wrap(para, width) or [""]:
            out.append(f"  | {ln:<{width}} |")
    tail = " ... more +" if truncated else "-+"
    out.append("  +" + "-" * (width + 3 - len(tail)) + tail)
    out.append("")
    for c in checks:
        out.append(f"  {c.status:<4}  {c.name:<16} {c.detail}")
    fails = sum(c.status == "FAIL" for c in checks)
    warns = sum(c.status == "WARN" for c in checks)
    out.append("")
    out.append(f"  {'READY' if not fails and warns <= 1 else 'FIX FIRST' if fails else 'REVIEW'}  ({fails} fail, {warns} warn)")
    return "\n".join(out)
