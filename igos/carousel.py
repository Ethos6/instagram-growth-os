"""Lint and render carousels to SVG slides. No image libraries needed.

Source format (markdown-ish), slides separated by a line containing only ---

    # The cover line that earns the swipe
    small kicker under it
    ---
    ## Slide headline
    Body text. Short lines.
    ---
    ...

The first slide is the cover. The last slide should carry the one ask.
SVGs open in any browser and import into Canva, Figma, Keynote and most
editors. Convert to PNG with `rsvg-convert` or `cairosvg` if you have them.
"""

from __future__ import annotations

import html
import os
import re
import textwrap
from dataclasses import dataclass

from . import text as T

SIZES = {"4:5": (1080, 1350), "3:4": (1080, 1440), "1:1": (1080, 1080)}


@dataclass
class Slide:
    title: str
    body: list[str]


def parse(src: str) -> list[Slide]:
    slides = []
    for chunk in re.split(r"^\s*---\s*$", src, flags=re.M):
        lines = [l.rstrip() for l in chunk.strip().splitlines() if l.strip()]
        if not lines:
            continue
        title = re.sub(r"^#+\s*", "", lines[0])
        slides.append(Slide(title, [re.sub(r"^[-*]\s+", "- ", l) for l in lines[1:]]))
    return slides


def lint(slides: list[Slide]) -> list[str]:
    cap = T.load_data("platform.json")["limits"]["carousel_slides"]["value"]
    notes = []
    if not slides:
        return ["FAIL no slides found"]
    if len(slides) > cap:
        notes.append(f"FAIL {len(slides)} slides; the cap is {cap}")
    elif len(slides) < 3:
        notes.append("WARN under 3 slides; a carousel this short should probably be a single image")
    cover = slides[0]
    cw = len(T.words(cover.title))
    if cw > 12:
        notes.append(f"WARN cover headline is {cw} words; aim for 4-10")
    if not T.concrete_markers(cover.title):
        notes.append("WARN cover has nothing countable; numbers make the swipe")
    for i, s in enumerate(slides[1:], 2):
        n = len(T.words(" ".join([s.title] + s.body)))
        if n > 45:
            notes.append(f"WARN slide {i} has {n} words; over ~45 reads as homework")
    last = " ".join([slides[-1].title] + slides[-1].body).lower()
    if not re.search(r"\b(save|send|share|comment|follow|dm|link|bookmark)\b", last):
        notes.append("WARN last slide has no ask (save / send / comment / follow)")
    if not notes:
        notes.append("PASS")
    return notes


def _wrap(s: str, size: int, width_px: int) -> list[str]:
    chars = max(8, int(width_px / (size * 0.55)))
    return textwrap.wrap(s, chars) or [""]


def render_svg(slide: Slide, idx: int, total: int, ratio: str = "4:5", bg: str = "#111111",
               fg: str = "#F5F5F0", accent: str = "#FFB000", handle: str = "",
               font: str = "Inter, Helvetica, Arial, sans-serif") -> str:
    w, h = SIZES[ratio]
    pad = 96
    # keep important text inside the centre 3:4-safe band so the grid crop never cuts it
    is_cover = idx == 1
    title_size = 92 if is_cover else 64
    body_size = 40
    y = int(h * (0.30 if is_cover else 0.20))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        f'<rect width="100%" height="100%" fill="{bg}"/>',
        f'<rect x="{pad}" y="{y - title_size - 28}" width="96" height="10" fill="{accent}"/>',
    ]
    for line in _wrap(slide.title, title_size, w - 2 * pad):
        parts.append(f'<text x="{pad}" y="{y}" font-family="{font}" font-size="{title_size}" font-weight="800" fill="{fg}">{html.escape(line)}</text>')
        y += int(title_size * 1.12)
    y += 36
    for para in slide.body:
        for line in _wrap(para, body_size, w - 2 * pad):
            parts.append(f'<text x="{pad}" y="{y}" font-family="{font}" font-size="{body_size}" fill="{fg}" opacity="0.88">{html.escape(line)}</text>')
            y += int(body_size * 1.4)
        y += 18
    foot = h - 72
    if handle:
        parts.append(f'<text x="{pad}" y="{foot}" font-family="{font}" font-size="30" fill="{fg}" opacity="0.6">{html.escape(handle)}</text>')
    parts.append(f'<text x="{w - pad}" y="{foot}" text-anchor="end" font-family="{font}" font-size="30" fill="{fg}" opacity="0.6">{idx}/{total}{"  swipe ->" if is_cover else ""}</text>')
    parts.append("</svg>")
    if y > h - 120:
        parts.insert(1, "<!-- igos: text overflows; shorten this slide -->")
    return "\n".join(parts)


def overflowing(slides: list[Slide], ratio: str = "4:5") -> list[int]:
    """1-based numbers of slides whose text runs past the safe bottom margin."""
    return [i for i, s in enumerate(slides, 1)
            if "text overflows" in render_svg(s, i, len(slides), ratio=ratio)]


def render_all(slides: list[Slide], outdir: str, **kw) -> list[str]:
    os.makedirs(outdir, exist_ok=True)
    paths = []
    for i, s in enumerate(slides, 1):
        p = os.path.join(outdir, f"slide-{i:02d}.svg")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(render_svg(s, i, len(slides), **kw))
        paths.append(p)
    return paths
