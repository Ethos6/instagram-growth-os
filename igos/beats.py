"""Time a Reel script beat by beat, flag what loses viewers, and
export burned-in caption files (.srt) straight from the script.

Script format: one beat per line. Blank lines are ignored. A line starting with
`[card]` or `>` is on-screen text, attached to the spoken beat above it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import text as T


@dataclass
class Beat:
    line: str
    start: float
    seconds: float
    label: str = ""
    cards: list[str] = field(default_factory=list)
    concrete: bool = False

    @property
    def end(self) -> float:
        return self.start + self.seconds


def parse(script: str) -> list[tuple[str, list[str]]]:
    beats: list[tuple[str, list[str]]] = []
    for raw in script.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(?:\[card\]|>)\s*(.+)$", line, re.IGNORECASE)
        if m:
            if beats:
                beats[-1][1].append(m.group(1).strip())
            continue
        beats.append((line, []))
    return beats


def build(script: str, sps: float = 5.0) -> list[Beat]:
    beats: list[Beat] = []
    t = 0.0
    parsed = parse(script)
    for i, (line, cards) in enumerate(parsed):
        secs = max(0.6, T.spoken_seconds(line, sps))
        label = "HOOK" if i == 0 else ("PAYOFF" if i == len(parsed) - 1 else "")
        b = Beat(line, t, secs, label, cards, bool(T.concrete_markers(line)))
        beats.append(b)
        t += secs
    return beats


def check(beats: list[Beat], target: float | None = None, max_beat: float = 4.5) -> list[str]:
    flags: list[str] = []
    if not beats:
        return ["Empty script."]
    hook = beats[0]
    if hook.seconds > 3.5:
        flags.append(f"Hook takes {hook.seconds:.1f}s. Cut it under 3.5s or the swipe happens mid-sentence.")
    if not hook.cards:
        flags.append("No on-screen card on the hook. Most people start with the sound off.")
    for i, b in enumerate(beats, 1):
        if i > 1 and b.seconds > max_beat:
            flags.append(f"Beat {i} runs {b.seconds:.1f}s on one shot. Split it or cut to a new frame inside it.")
        for c in b.cards:
            if len(T.words(c)) > 6:
                flags.append(f"Card on beat {i} has {len(T.words(c))} words. Six is the ceiling at arm's length.")
    # abstract stretches
    run = 0
    for i, b in enumerate(beats, 1):
        run = 0 if b.concrete else run + 1
        if run == 3:
            flags.append(f"Beats {i-2}-{i} have nothing concrete. Add a number, a name or a thing on screen.")
    # loop: last beat echoes a content word from the hook
    hook_words = set(T.content_words(beats[0].line)) | {m.lower() for m in T.concrete_markers(beats[0].line)}
    last_words = set(T.content_words(beats[-1].line)) | {m.lower() for m in T.concrete_markers(beats[-1].line)}
    echo = hook_words & last_words
    if len(beats) > 2:
        if echo:
            flags.append(f"Loop OK: the last beat echoes '{sorted(echo)[0]}' from the hook.")
        else:
            flags.append("No loop. Reuse a hook word in the final line so a rewatch feels continuous.")
    total = beats[-1].end
    if target:
        diff = total - target
        if diff > 2:
            flags.append(f"{diff:.1f}s over the {target:.0f}s target. Cut ~{int(diff * 2.6)} words.")
        elif diff < -5:
            flags.append(f"{-diff:.1f}s under target. Shorter is usually fine; do not pad.")
    return flags


def fmt_ts(s: float) -> str:
    m, sec = divmod(s, 60)
    return f"{int(m)}:{sec:04.1f}"


def render(beats: list[Beat], flags: list[str], target: float | None, sps: float) -> str:
    total = beats[-1].end if beats else 0
    nwords = sum(len(T.words(b.line)) for b in beats)
    head = f"BEAT SHEET  {nwords} words  ~{total:.1f}s  {sps} syll/s"
    if target:
        head += f"  target {target:.0f}s"
    out = [head, "=" * 78]
    for b in beats:
        out.append(f"{fmt_ts(b.start):>7} {b.seconds:4.1f}s  {b.label:<6} {T.shorten(b.line, 54)}")
        for c in b.cards:
            out.append(f"{'':22}[card] {c}")
    out.append("-" * 78)
    out += [f"- {f}" for f in flags]
    return "\n".join(out)


def _srt_time(s: float) -> str:
    ms = int(round(s * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def to_srt(beats: list[Beat], max_words: int = 5) -> str:
    """Burned-caption friendly: chunks of <= max_words, timed within each beat."""
    blocks = []
    idx = 1
    for b in beats:
        ws = b.line.split()
        chunks = [ws[i : i + max_words] for i in range(0, len(ws), max_words)] or [[]]
        per = b.seconds / len(chunks)
        for j, ch in enumerate(chunks):
            start = b.start + j * per
            blocks.append(f"{idx}\n{_srt_time(start)} --> {_srt_time(start + per)}\n{' '.join(ch)}\n")
            idx += 1
    return "\n".join(blocks)
