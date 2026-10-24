"""Shared text primitives. Every analyser in igos tokenises the same way.

Standard library only. Nothing here touches the network.
"""

from __future__ import annotations

import json
import re
import statistics
import unicodedata
from functools import lru_cache
from importlib import resources
from typing import Iterable

# --------------------------------------------------------------------------- #
# data files
# --------------------------------------------------------------------------- #


@lru_cache(maxsize=None)
def load_data(name: str) -> dict:
    """Load a JSON file shipped in igos/data."""
    with resources.files("igos.data").joinpath(name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def read_input(path: str | None) -> str:
    """Read a file path, or stdin when path is '-' or None."""
    import sys

    if path in (None, "-"):
        raw = sys.stdin.buffer.read() if hasattr(sys.stdin, "buffer") else sys.stdin.read().encode("utf-8")
    else:
        with open(path, "rb") as fh:
            raw = fh.read()
    return decode_bytes(raw)


def decode_bytes(raw: bytes) -> str:
    """Decode text the way it actually arrives: UTF-8, UTF-8 with BOM, UTF-16
    (Excel and Notepad exports) or a Windows code page. Never raises."""
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8", errors="replace")
    # UTF-16 without a BOM: lots of NUL bytes in alternate positions
    if raw and raw.count(b"\x00") > len(raw) // 4:
        for enc in ("utf-16-le", "utf-16-be"):
            try:
                return raw.decode(enc)
            except UnicodeDecodeError:
                pass
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")


# --------------------------------------------------------------------------- #
# patterns
# --------------------------------------------------------------------------- #

URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
HASHTAG_RE = re.compile(r"(?<![\w&])#(?=[^\s#]*[^\W\d_])([^\s#.,!?;:()\[\]{}\"']+)")
MENTION_RE = re.compile(r"(?<![\w.])@([A-Za-z0-9._]{1,30})")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)*(?:[.,]\d+)?")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])[\"')\]]*\s+|\n+")
EMOJI_RE = re.compile(
    "["
    "\U0001F000-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F900-\U0001F9FF"
    "\U00002B00-\U00002BFF"
    "]"
)
MONEY_RE = re.compile(r"[$€£₹]\s?\d[\d,]*(?:\.\d+)?\s?(?:[kKmMbB]\b)?")
FIGURE_RE = re.compile(r"\b\d[\d,]*(?:\.\d+)?(?:%|x\b|k\b|m\b)?", re.IGNORECASE)
CONTRACTION_RE = re.compile(
    r"\b\w+['’](?:s|t|re|ve|ll|d|m)\b", re.IGNORECASE
)

SPOKEN_NUMBERS = frozenset(
    """zero two three four five six seven eight nine ten eleven twelve thirteen
    fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty
    sixty seventy eighty ninety hundred thousand million billion dozen half
    twice triple double grand""".split()
)

TIME_UNITS = frozenset(
    """second seconds minute minutes hour hours day days week weeks month months
    year years""".split()
)

STOPWORDS = frozenset(
    """a an the and or but if then so of to in on at for with from by as is are
    was were be been being it its this that these those i me my we our you your
    he she they them his her their what which who whom how why when where not no
    do does did have has had just very really can could will would should may
    might must there here about into over than too also up out all any some more
    most such only own same other each few both am im i'm it's that's""".split()
)

# Characters a keyboard does not type, which survive copy/paste invisibly.
INVISIBLE_CODEPOINTS = {
    0x00AD: "soft hyphen",
    0x180E: "mongolian vowel separator",
    0x200B: "zero width space",
    0x200C: "zero width non-joiner",
    0x200D: "zero width joiner",
    0x200E: "left-to-right mark",
    0x200F: "right-to-left mark",
    0x2060: "word joiner",
    0x2061: "function application",
    0x2062: "invisible times",
    0x2063: "invisible separator",
    0x2064: "invisible plus",
    0x206A: "inhibit symmetric swapping",
    0x206F: "nominal digit shapes",
    0xFEFF: "byte order mark",
    0xFFF9: "interlinear annotation anchor",
    0xFFFA: "interlinear annotation separator",
    0xFFFB: "interlinear annotation terminator",
}
ODD_SPACES = {
    0x00A0: "no-break space",
    0x2000: "en quad",
    0x2001: "em quad",
    0x2002: "en space",
    0x2003: "em space",
    0x2004: "three-per-em space",
    0x2005: "four-per-em space",
    0x2006: "six-per-em space",
    0x2007: "figure space",
    0x2008: "punctuation space",
    0x2009: "thin space",
    0x200A: "hair space",
    0x202F: "narrow no-break space",
    0x205F: "medium mathematical space",
    0x3000: "ideographic space",
}


def is_invisible(ch: str) -> bool:
    cp = ord(ch)
    if cp in INVISIBLE_CODEPOINTS:
        return True
    if 0xE0000 <= cp <= 0xE007F:  # unicode tag block
        return True
    # Any other format character, except ZWJ inside emoji sequences is handled
    # by the caller (we keep ZWJ between two emoji).
    return unicodedata.category(ch) == "Cf"


# --------------------------------------------------------------------------- #
# tokenisers
# --------------------------------------------------------------------------- #


def strip_urls(text: str) -> str:
    return URL_RE.sub(" ", text)


def words(text: str) -> list[str]:
    """Words, with URLs, hashtags and mentions removed."""
    t = strip_urls(text)
    t = HASHTAG_RE.sub(" ", t)
    t = MENTION_RE.sub(" ", t)
    return WORD_RE.findall(t)


def content_words(text: str) -> list[str]:
    return [w.lower() for w in words(text) if w.lower() not in STOPWORDS and len(w) > 2]


def sentences(text: str) -> list[str]:
    t = strip_urls(text)
    parts = [p.strip() for p in SENTENCE_SPLIT_RE.split(t)]
    return [p for p in parts if p and WORD_RE.search(p)]


def hashtags(text: str) -> list[str]:
    return ["#" + h for h in HASHTAG_RE.findall(strip_urls(text))]


def mentions(text: str) -> list[str]:
    return ["@" + m.rstrip(".") for m in MENTION_RE.findall(strip_urls(text))]


def emojis(text: str) -> list[str]:
    return EMOJI_RE.findall(text)


# --------------------------------------------------------------------------- #
# measurements
# --------------------------------------------------------------------------- #

_VOWEL_GROUP = re.compile(r"[aeiouy]+")


def syllables(word: str) -> int:
    """Rough English syllable count. Good enough for speech timing."""
    w = word.lower().strip("'’")
    if not w:
        return 0
    if w.isdigit() or re.fullmatch(r"[\d,.]+%?", w):
        # numbers are spoken long: "18,000" is "eighteen thousand"
        digits = re.sub(r"\D", "", w)
        return max(2, min(8, len(digits) + 1)) + (2 if w.endswith("%") else 0)
    groups = _VOWEL_GROUP.findall(w)
    n = len(groups)
    if w.endswith("e") and not w.endswith(("le", "ee", "ye")) and n > 1:
        n -= 1
    if w.endswith(("ed",)) and not w.endswith(("ted", "ded")) and n > 1:
        n -= 1
    return max(1, n)


def spoken_seconds(text: str, syllables_per_second: float = 5.0) -> float:
    """Estimated time to say a line out loud.

    Uses syllables rather than words because "I" and "unbelievably" are not the
    same length. Money and symbols are expanded. A short pause is added for each
    sentence break and comma.
    """
    t = MONEY_RE.sub(lambda m: m.group(0) + " dollars", text)
    t = t.replace("%", " percent").replace("&", " and ")
    syl = sum(syllables(w) for w in words(t))
    pauses = 0.25 * len(re.findall(r"[.!?]", t)) + 0.12 * t.count(",")
    return syl / syllables_per_second + pauses


def concrete_markers(text: str) -> list[str]:
    """Numbers (written or spoken), money, proper nouns, time spans."""
    found: list[str] = []
    t = strip_urls(text)
    found += MONEY_RE.findall(t)
    t_wo_money = MONEY_RE.sub(" ", t)
    found += [f for f in FIGURE_RE.findall(t_wo_money) if f.strip()]
    toks = words(t)
    lower = [w.lower() for w in toks]
    for i, w in enumerate(lower):
        if w in SPOKEN_NUMBERS:
            found.append(toks[i])
    # proper nouns: capitalised words that do not start a sentence
    for sent in sentences(t):
        sw = WORD_RE.findall(sent)
        for w in sw[1:]:
            if (
                len(w) > 2
                and w[0].isupper()
                and not w.isupper()
                and w.lower() not in STOPWORDS
            ):
                found.append(w)
    return found


def coefficient_of_variation(values: Iterable[float]) -> float:
    vals = [v for v in values if v > 0]
    if len(vals) < 2:
        return 0.0
    mean = statistics.fmean(vals)
    return statistics.pstdev(vals) / mean if mean else 0.0


def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def bar(score: float, width: int = 24) -> str:
    filled = int(round(clamp(score) / 100 * width))
    return "#" * filled + "." * (width - filled)


def shorten(text: str, n: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 3].rstrip() + "..."
