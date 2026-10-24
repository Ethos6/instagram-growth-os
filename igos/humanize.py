"""Clean a draft: invisible characters, typography, stock phrasing.

Three passes are automatic. Structural tells are reported, never rewritten,
because changing the shape of a sentence needs judgement.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from . import text as T


@dataclass
class Report:
    invisible: Counter = field(default_factory=Counter)
    typography: Counter = field(default_factory=Counter)
    swaps: Counter = field(default_factory=Counter)
    tells: list[tuple[str, str]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(self.invisible.values()) + sum(self.typography.values()) + sum(self.swaps.values())

    def as_dict(self) -> dict:
        return {
            "invisible": dict(self.invisible),
            "typography": dict(self.typography),
            "swaps": dict(self.swaps),
            "tells": [{"tell": t, "excerpt": e} for t, e in self.tells],
            "total_changes": self.total,
        }


def _is_emoji(ch: str) -> bool:
    return bool(ch) and bool(T.EMOJI_RE.match(ch))


def strip_invisible(text: str, rep: Report) -> str:
    out = []
    for i, ch in enumerate(text):
        cp = ord(ch)
        if cp in T.ODD_SPACES:
            rep.invisible[T.ODD_SPACES[cp]] += 1
            out.append(" ")
            continue
        if T.is_invisible(ch):
            # keep zero-width joiners that glue emoji sequences together
            if cp == 0x200D and i > 0 and i + 1 < len(text):
                prev = text[i - 1]
                nxt = text[i + 1]
                if (_is_emoji(prev) or prev == "️") and _is_emoji(nxt):
                    out.append(ch)
                    continue
            name = T.INVISIBLE_CODEPOINTS.get(cp) or ("tag character" if 0xE0000 <= cp <= 0xE007F else f"format char U+{cp:04X}")
            rep.invisible[name] += 1
            continue
        out.append(ch)
    return "".join(out)


def fix_typography(text: str, rep: Report) -> str:
    table = T.load_data("lexicon.json")["typography"]
    # em dash used as a parenthetical, with or without spaces
    n = len(re.findall("—", text))
    if n:
        rep.typography["em dash"] += n
        text = re.sub(r"\s*—\s*", ", ", text)
    for src, dst in table.items():
        if src == "—":
            continue
        c = text.count(src)
        if c:
            rep.typography[f"U+{ord(src):04X} {src!r}"] += c
            text = text.replace(src, dst)
    return _tidy(text)


def _tidy(text: str) -> str:
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" +([,.;:!?])", r"\1", text)
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r",\s*([.!?;:])", r"\1", text)
    text = re.sub(r"([.!?])\s*,", r"\1", text)
    text = re.sub(r"(^|\n)[ \t]*[,;:]?[ \t]*", r"\1", text)
    text = re.sub(r"[ \t]+(\n|$)", r"\1", text)
    text = re.sub(r"\(\s*\)", "", text)
    return text


def _recap(text: str) -> str:
    """Capitalise the first letter of each sentence after deletions."""
    def up(m: re.Match) -> str:
        return m.group(1) + m.group(2).upper()

    text = re.sub(r"(^\s*|[.!?]\s+|\n\s*)([a-z])", up, text)
    return text


def swap_lexicon(text: str, rep: Report) -> str:
    swaps: dict[str, str] = T.load_data("lexicon.json")["swap"]
    # protect URLs, handles and hashtags
    shields: list[str] = []

    def shield(m: re.Match) -> str:
        shields.append(m.group(0))
        return f"\x00{len(shields) - 1}\x00"

    text = re.sub(r"https?://\S+|www\.\S+|[@#][\w.]+", shield, text)
    for phrase in sorted(swaps, key=len, reverse=True):
        repl = swaps[phrase]
        left = r"(?<![\w'])" if phrase[0].isalnum() else ""
        right = r"(?![\w'])" if phrase[-1].isalnum() else ""
        pat = re.compile(left + re.escape(phrase) + right, re.IGNORECASE)

        def sub(m: re.Match, repl: str = repl, phrase: str = phrase) -> str:
            rep.swaps[phrase] += 1
            src = m.group(0)
            if repl and src[:1].isupper():
                return repl[:1].upper() + repl[1:]
            return repl

        text = pat.sub(sub, text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: shields[int(m.group(1))], text)
    return _recap(_tidy(text))


def find_tells(text: str) -> list[tuple[str, str]]:
    found = []
    for t in T.load_data("lexicon.json")["tells"]:
        flags = re.MULTILINE if t["id"] == "shouting" else re.IGNORECASE | re.MULTILINE
        for m in re.finditer(t["regex"], text, flags):
            found.append((t["msg"], T.shorten(m.group(0).strip(), 70)))
    return found


def humanize(text: str) -> tuple[str, Report]:
    rep = Report()
    out = strip_invisible(text, rep)
    out = fix_typography(out, rep)
    out = swap_lexicon(out, rep)
    out = re.sub(r"\n{3,}", "\n\n", out).strip() + ("\n" if text.endswith("\n") else "")
    rep.tells = find_tells(out)
    return out, rep


def render_report(rep: Report) -> str:
    out = [f"HUMANIZE  {rep.total} automatic changes", "=" * 60]
    for title, c in (("invisible characters", rep.invisible), ("typography", rep.typography), ("stock phrasing", rep.swaps)):
        if c:
            out.append(f"{title}:")
            for k, v in c.most_common():
                out.append(f"  {v:>3}  {k}")
    if rep.tells:
        out.append("rewrite by hand (flagged, not changed):")
        for msg, ex in rep.tells:
            out.append(f"  -  {msg}\n       \"{ex}\"")
    else:
        out.append("no structural tells flagged")
    return "\n".join(out)
