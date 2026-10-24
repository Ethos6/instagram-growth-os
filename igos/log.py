"""A local post log (JSON lines) plus a near-duplicate check.

Instagram has been tightening how it treats reposted and lightly edited
content. Before you post, compare the new script/caption against what you have
already shipped so you are re-angling an idea, not re-uploading it.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime

from . import text as T

HOME = os.environ.get("IGOS_HOME", os.path.join(os.path.expanduser("~"), ".instagram-growth-os"))


def path() -> str:
    return os.path.join(HOME, "log.jsonl")


def add(kind: str, text: str, pattern: str | None = None, extra: dict | None = None) -> dict:
    os.makedirs(HOME, exist_ok=True)
    entry = {"at": datetime.now().isoformat(timespec="seconds"), "kind": kind,
             "first_line": text.strip().split("\n")[0][:200], "text": text, "pattern": pattern}
    if extra:
        entry.update(extra)
    with open(path(), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def entries() -> list[dict]:
    if not os.path.exists(path()):
        return []
    out = []
    with open(path(), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def _shingles(text: str, k: int = 3) -> set[tuple[str, ...]]:
    ws = [w.lower() for w in T.words(text)]
    return {tuple(ws[i : i + k]) for i in range(max(0, len(ws) - k + 1))}


def similarity(a: str, b: str) -> float:
    sa, sb = _shingles(a), _shingles(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def near_duplicates(text: str, threshold: float = 0.35, corpus: list[dict] | None = None) -> list[tuple[float, dict]]:
    corpus = entries() if corpus is None else corpus
    hits = [(similarity(text, e.get("text", "")), e) for e in corpus]
    return sorted([h for h in hits if h[0] >= threshold], key=lambda h: -h[0])
