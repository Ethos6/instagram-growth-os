"""Score and rank the opening line of a Reel.

This is a *filter*, not a predictor. It reliably catches the hooks that lose
people in the first second (greetings, preambles, nothing concrete, too long to
say). It cannot pick the winner between two solid hooks: that depends on
the first frame, the delivery, the audio and distribution. Your retention graph
is the final judge.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import text as T

OPENER_FILLER = re.compile(
    r"^\s*(?:hey|hi|hello|yo|what'?s up|welcome|good (?:morning|evening)|so+,?|okay,?|ok,?|alright,?|um+|uh+|today|guys|friends)\b",
    re.IGNORECASE,
)
PREAMBLE = re.compile(
    r"\b(?:in (?:this|today'?s) (?:video|reel|post)|i (?:want|wanted|'m going|am going|'m gonna|am gonna) to (?:talk|share|show|tell)|let me (?:tell|show|share)|quick (?:video|reel|tip)|before we (?:start|begin)|make sure (?:to|you) (?:follow|like))\b",
    re.IGNORECASE,
)
ATTENTION_BEG = re.compile(
    r"\b(?:stop scrolling|wait for it|watch (?:till|until|to) the end|don'?t scroll|you need to see this|you won'?t believe)\b",
    re.IGNORECASE,
)
GENERIC_DID_YOU_KNOW = re.compile(r"^\s*did you know\b", re.IGNORECASE)

TENSION_WORDS = frozenset(
    """lost lose losing cost mistake mistakes wrong never stop quit broke broken
    failed fail failing fired worst secret nobody hidden real truth lie myth
    instead without why risk warning before after doubled tripled halved killed
    hate wasted mistake regret banned dead overrated trap backwards almost
    only finally actually problem""".split()
)


@dataclass
class HookResult:
    hook: str
    checks: dict[str, float]
    notes: dict[str, str]
    dealbreakers: list[str] = field(default_factory=list)
    pattern: str | None = None
    family: str | None = None
    seconds: float = 0.0

    @property
    def score(self) -> float:
        vals = list(self.checks.values())
        base = 0.65 * (sum(vals) / len(vals)) + 0.35 * min(vals)
        return round(T.clamp(base - 22 * len(self.dealbreakers)), 1)

    @property
    def verdict(self) -> str:
        s = self.score
        if s >= 75 and not self.dealbreakers:
            return "STRONG"
        if s >= 55:
            return "USABLE"
        return "REWRITE"

    @property
    def weakest(self) -> str:
        return min(self.checks, key=self.checks.get)

    def as_dict(self) -> dict:
        return {
            "hook": self.hook,
            "score": self.score,
            "verdict": self.verdict,
            "seconds": round(self.seconds, 2),
            "checks": {k: round(v, 1) for k, v in self.checks.items()},
            "notes": self.notes,
            "weakest": self.weakest,
            "dealbreakers": self.dealbreakers,
            "pattern": self.pattern,
            "family": self.family,
        }


def classify(hook: str) -> tuple[str | None, str | None]:
    """Name the hook pattern, or (None, None) when nothing fits.

    Abstaining is the honest answer for a lot of real hooks.
    """
    for p in T.load_data("hooks.json")["patterns"]:
        if re.search(p["regex"], hook, re.IGNORECASE):
            return p["name"], p["family"]
    return None, None


def score_hook(hook: str, syllables_per_second: float = 5.0) -> HookResult:
    hook = " ".join(hook.split())
    w = T.words(hook)
    lw = [x.lower() for x in w]
    checks: dict[str, float] = {}
    notes: dict[str, str] = {}
    dealbreakers: list[str] = []

    # PACE: can it be said before the thumb moves?
    secs = T.spoken_seconds(hook, syllables_per_second)
    if secs <= 3.0:
        pace = 100.0
    elif secs <= 5.4:
        pace = 100 - (secs - 3.0) / 2.4 * 75
    else:
        pace = max(0.0, 25 - (secs - 5.4) * 10)
    checks["PACE"] = pace
    notes["PACE"] = f"~{secs:.1f}s to say, {len(w)} words"

    # CONCRETE: numbers, money, names, time spans
    markers = T.concrete_markers(hook)
    has_time = any(x in T.TIME_UNITS for x in lw)
    n = len(markers) + (1 if has_time and not markers else 0)
    checks["CONCRETE"] = {0: 15.0, 1: 78.0}.get(n, 100.0)
    notes["CONCRETE"] = ", ".join(markers[:4]) if markers else "nothing countable"

    # FRONT-LOAD: how early does the first loaded word arrive?
    first_loaded = None
    marker_tokens = {m.lower().strip("$€£₹,") for m in markers}
    for i, tok in enumerate(lw):
        bare = tok.strip("$€£₹,")
        if tok in TENSION_WORDS or bare in marker_tokens or tok in T.SPOKEN_NUMBERS or tok in ("you", "your"):
            first_loaded = i
            break
    if first_loaded is None:
        front = 30.0
        notes["FRONT"] = "no loaded word anywhere"
    else:
        front = max(30.0, 100 - first_loaded * 9)
        notes["FRONT"] = f"first loaded word at position {first_loaded + 1}"
    if OPENER_FILLER.search(hook):
        front = min(front, 10.0)
        notes["FRONT"] = "opens on filler"
    checks["FRONT"] = front

    # TENSION: is anything at stake or unresolved?
    pattern, family = classify(hook)
    t_hits = [x for x in lw if x in TENSION_WORDS]
    tension = 35.0
    if t_hits:
        tension += 35
    if pattern:
        tension += 30
    if hook.rstrip().endswith("?") and len(w) <= 12:
        tension += 10
    checks["TENSION"] = T.clamp(tension)
    notes["TENSION"] = (
        (f"pattern: {pattern}" if pattern else "no known pattern")
        + (f"; stakes: {', '.join(t_hits[:3])}" if t_hits else "")
    )

    # AIM: is it pointed at someone?
    if any(x in ("you", "your", "you're", "youre", "yours") for x in lw):
        aim, why = 100.0, "speaks to the viewer"
    elif any(x in ("i", "we", "my", "our", "me", "us", "i'm", "i've", "we're", "i'd", "i'll") for x in lw):
        aim, why = 82.0, "first person, ok when it is a confession or a result"
    elif lw and lw[0] == "pov":
        aim, why = 90.0, "POV frame puts the viewer in it"
    else:
        aim, why = 50.0, "no one is addressed"
    checks["AIM"] = aim
    notes["AIM"] = why

    # dealbreakers
    if OPENER_FILLER.search(hook) and re.match(r"^\s*(?:hey|hi|hello|yo|what'?s up|welcome|good)", hook, re.I):
        dealbreakers.append("Opens with a hello. Skip it; the viewer is already deciding.")
    if PREAMBLE.search(hook):
        dealbreakers.append("Preamble ('in this video', 'I want to talk about'). Start at the point.")
    if ATTENTION_BEG.search(hook):
        dealbreakers.append("Begs for attention instead of earning it.")
    if GENERIC_DID_YOU_KNOW.search(hook) and n == 0:
        dealbreakers.append("'Did you know' with no fact attached.")
    if T.hashtags(hook) or len(T.emojis(hook)) > 1:
        dealbreakers.append("Hashtags or emoji in a spoken line. Nobody can say them.")
    if len(w) > 22:
        dealbreakers.append(f"{len(w)} words. That is a paragraph, not a hook.")

    return HookResult(hook, checks, notes, dealbreakers, pattern, family, secs)


def rank(hooks: list[str]) -> list[HookResult]:
    results = [score_hook(h) for h in hooks if h.strip()]
    return sorted(results, key=lambda r: r.score, reverse=True)


def render(results: list[HookResult]) -> str:
    out = ["HOOK RANKING  (a filter for weak openers, not a view predictor)", "=" * 78]
    for i, r in enumerate(results):
        arrow = "->" if i == 0 and len(results) > 1 else "  "
        out.append(f"{arrow} {r.score:5.1f}  {r.verdict:<8} {T.shorten(r.hook, 58)}")
        out.append(
            f"         {r.seconds:.1f}s  pattern: {r.pattern or '-'}  weakest: {r.weakest} ({r.checks[r.weakest]:.0f})"
        )
        for d in r.dealbreakers:
            out.append(f"         x {d}")
    out.append("-" * 78)
    out.append("PACE  CONCRETE  FRONT  TENSION  AIM   each 0-100; overall weights the weakest check.")
    return "\n".join(out)
