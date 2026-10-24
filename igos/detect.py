"""Five local checks for text that reads as generated or corporate.

Everything is computed locally. This is not, and does not call,
any commercial AI detector, and it cannot promise any detector's verdict.
They measure things a reader notices: rhythm, specifics, stock phrasing,
typographic fingerprints and voice.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from . import text as T
from .humanize import find_tells


@dataclass
class Detection:
    checks: dict[str, float]
    notes: dict[str, str]

    @property
    def score(self) -> float:
        v = list(self.checks.values())
        return round(0.6 * sum(v) / len(v) + 0.4 * min(v), 1)

    @property
    def verdict(self) -> str:
        if self.score >= 70 and min(self.checks.values()) >= 55:
            return "PASS"
        if self.score >= 50:
            return "REVIEW"
        return "FLAGGED"

    def as_dict(self) -> dict:
        return {"score": self.score, "verdict": self.verdict,
                "checks": {k: round(v, 1) for k, v in self.checks.items()}, "notes": self.notes}


def _stock_hits(text: str) -> list[str]:
    hits = []
    low = text.lower()
    for phrase in T.load_data("lexicon.json")["swap"]:
        left = r"(?<![\w'])" if phrase[0].isalnum() else ""
        right = r"(?![\w'])" if phrase[-1].isalnum() else ""
        hits += [phrase] * len(re.findall(left + re.escape(phrase) + right, low))
    return hits


def detect(text: str) -> Detection:
    ws = T.words(text)
    nw = max(1, len(ws))
    checks: dict[str, float] = {}
    notes: dict[str, str] = {}

    sents = T.sentences(text)
    lens = [len(T.words(s)) for s in sents]
    if len(lens) < 3:
        checks["RHYTHM"] = 70.0
        notes["RHYTHM"] = "too short to judge rhythm"
    else:
        cv = T.coefficient_of_variation(lens)
        checks["RHYTHM"] = T.clamp((cv - 0.15) / 0.40 * 90 + 10)
        notes["RHYTHM"] = f"sentence length varies {cv:.2f} (flat < 0.25 < lively)"

    markers = T.concrete_markers(text)
    per100 = len(markers) / nw * 100
    checks["SPECIFICS"] = T.clamp(15 + per100 * 22)
    notes["SPECIFICS"] = f"{per100:.1f} numbers/names per 100 words"

    stock = _stock_hits(text)
    s100 = len(stock) / nw * 100
    checks["STOCK"] = T.clamp(100 - s100 * 25)
    notes["STOCK"] = f"{len(stock)} stock phrases" + (f": {', '.join(sorted(set(stock))[:5])}" if stock else "")

    inv = sum(1 for ch in text if T.is_invisible(ch) or ord(ch) in T.ODD_SPACES)
    dashes = text.count("—")
    curly = sum(text.count(c) for c in "‘’“”")
    per1k = (inv * 3 + dashes * 2 + curly * 0.5) / max(1, len(text)) * 1000
    checks["TYPOGRAPHY"] = T.clamp(100 - per1k * 12)
    notes["TYPOGRAPHY"] = f"{inv} invisible, {dashes} em dash, {curly} curly quotes"

    contractions = len(T.CONTRACTION_RE.findall(text))
    lw = [w.lower() for w in ws]
    person = sum(lw.count(p) for p in ("i", "you", "we", "my", "your", "our", "me"))
    tells = find_tells(text)
    voice = 40 + min(30, contractions / nw * 100 * 6) + min(30, person / nw * 100 * 3) - 12 * len(tells)
    checks["VOICE"] = T.clamp(voice)
    notes["VOICE"] = f"{contractions} contractions, {person} I/you/we, {len(tells)} structural tells"
    return Detection(checks, notes)


def render(d: Detection, label: str = "") -> str:
    out = [f"READS-HUMAN CHECK {label}".rstrip(), "=" * 70]
    for k, v in d.checks.items():
        out.append(f"  {k:<11} {T.bar(v)} {v:5.1f}   {d.notes[k]}")
    out.append("-" * 70)
    out.append(f"  {'OVERALL':<11} {T.bar(d.score)} {d.score:5.1f}   {d.verdict}")
    return "\n".join(out)


def render_delta(a: Detection, b: Detection) -> str:
    out = ["BEFORE -> AFTER", "=" * 50]
    for k in a.checks:
        out.append(f"  {k:<11} {a.checks[k]:5.1f} -> {b.checks[k]:5.1f}  ({b.checks[k] - a.checks[k]:+.1f})")
    out.append("-" * 50)
    out.append(f"  {'OVERALL':<11} {a.score:5.1f} -> {b.score:5.1f}  ({b.score - a.score:+.1f})  {a.verdict} -> {b.verdict}")
    return "\n".join(out)
