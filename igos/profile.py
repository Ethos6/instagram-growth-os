"""Profile linter: name field, bio, links. The parts a script can check.

The judgement parts (pinned posts, highlights, grid coherence) are scored by
the /insta-profile skill against data/profile_rubric.json.
"""

from __future__ import annotations

import re

from . import text as T


def lint(name: str, bio: str, links: int = 0, keywords: list[str] | None = None) -> list[tuple[str, str, str]]:
    lim = T.load_data("platform.json")["limits"]
    out: list[tuple[str, str, str]] = []
    nmax = lim["name_field_chars"]["value"]
    out.append(("PASS" if len(name) <= nmax else "FAIL", "NAME LENGTH", f"{len(name)}/{nmax}"))
    if keywords:
        hit = [k for k in keywords if k.lower() in name.lower()]
        out.append(("PASS" if hit else "WARN", "NAME KEYWORD",
                    f"searchable term in name: {hit[0]}" if hit else "the name field is searchable; add what you do (e.g. 'Asha | Wedding Photographer')"))
    bmax = lim["bio_chars"]["value"]
    out.append(("PASS" if len(bio) <= bmax else "FAIL", "BIO LENGTH", f"{len(bio)}/{bmax}"))
    first = bio.strip().splitlines()[0] if bio.strip() else ""
    if re.search(r"\b(?:i help|helping|for)\b", first, re.I):
        out.append(("PASS", "WHO IT'S FOR", "first line names an audience"))
    else:
        out.append(("WARN", "WHO IT'S FOR", "first line should say who you help and with what"))
    if T.concrete_markers(bio):
        out.append(("PASS", "PROOF", "has a number or a name"))
    else:
        out.append(("WARN", "PROOF", "no proof point (a number, a client, a result)"))
    if re.search(r"\b(?:dm|comment|book|grab|get|download|join|shop|tap|click|below|link)\b|↓|\U0001F447", bio, re.I):
        out.append(("PASS", "NEXT STEP", "tells the visitor what to do"))
    else:
        out.append(("WARN", "NEXT STEP", "no next step; end on one action"))
    if links == 0:
        out.append(("WARN", "LINK", "no link; a profile visitor has nowhere to go"))
    vague = re.findall(r"\b(?:passionate|enthusiast|lover of|guru|ninja|wizard|dreamer|creative soul|entrepreneur)\b", bio, re.I)
    if vague:
        out.append(("WARN", "VAGUE", "filler identity words: " + ", ".join(sorted(set(v.lower() for v in vague)))))
    if len(T.hashtags(bio)) > 1:
        out.append(("WARN", "HASHTAGS", "hashtags in the bio send visitors away from you"))
    return out
