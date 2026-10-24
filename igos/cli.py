"""igos: the command line for instagram-growth-os.

Everything runs locally on text and CSV files. Nothing posts, logs in or
fetches. Every command takes a file path or '-' for stdin and supports --json.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from importlib import resources

from . import __version__
from . import beats as B
from . import caption as C
from . import carousel as K
from . import detect as D
from . import hooks as H
from . import humanize as U
from . import log as L
from . import metrics as M
from . import plan as P
from . import profile as PR
from . import text as T


def _emit(args, payload, human: str) -> None:
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))
    else:
        print(human)


def _write(path: str, content: str) -> None:
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(content)


# --------------------------------------------------------------------------- #


def cmd_init(args) -> int:
    home = args.home or L.HOME
    os.makedirs(home, exist_ok=True)
    dest = os.path.join(home, "brand.md")
    if os.path.exists(dest) and not args.force:
        print(f"exists: {dest}  (use --force to overwrite)")
    else:
        src = resources.files("igos.data").joinpath("brand_template.md")
        with src.open("r", encoding="utf-8") as fh:
            _write(dest, fh.read())
        print(f"wrote {dest}")
    for name in ("swipe.md", "log.jsonl"):
        p = os.path.join(home, name)
        if not os.path.exists(p):
            open(p, "a").close()
    print(f"workspace: {home}")
    return 0


def cmd_hook(args) -> int:
    if args.hook:
        lines = args.hook
    else:
        lines = [l for l in T.read_input(args.file).splitlines() if l.strip()]
    res = H.rank(lines)
    _emit(args, [r.as_dict() for r in res], H.render(res))
    return 0 if res and res[0].verdict != "REWRITE" else 1


def cmd_patterns(args) -> int:
    data = T.load_data("hooks.json")
    pats = [p for p in data["patterns"] if not args.family or p["family"] == args.family]
    if args.json:
        print(json.dumps(pats, indent=2, ensure_ascii=False))
        return 0
    for p in pats:
        print(f"{p['name']}  [{p['family']}]")
        print(f"  template : {p['template']}")
        print(f"  example  : {p['example']}")
        print(f"  card     : {p['on_screen']}")
        print(f"  use when : {p['use_when']}")
        print(f"  fails if : {p['failure_mode']}\n")
    return 0


def cmd_beats(args) -> int:
    script = T.read_input(args.file)
    beats = B.build(script, args.sps)
    flags = B.check(beats, args.target)
    if args.srt:
        _write(args.srt, B.to_srt(beats))
    payload = {"total_seconds": round(beats[-1].end, 2) if beats else 0,
               "beats": [{"start": round(b.start, 2), "seconds": round(b.seconds, 2), "label": b.label,
                          "line": b.line, "cards": b.cards} for b in beats], "flags": flags}
    human = B.render(beats, flags, args.target, args.sps)
    if args.srt:
        human += f"\n\nwrote captions: {args.srt}"
    _emit(args, payload, human)
    return 0


def cmd_caption(args) -> int:
    cap = T.read_input(args.file)
    kws = [k.strip() for k in (args.keywords or "").split(",") if k.strip()]
    checks = C.lint(cap, kws, args.sponsored)
    _emit(args, {"preview": C.feed_preview(cap)[0], "checks": [c.__dict__ for c in checks]}, C.render(cap, checks))
    return 1 if any(c.status == "FAIL" for c in checks) else 0


def cmd_humanize(args) -> int:
    src = T.read_input(args.file)
    out, rep = U.humanize(src)
    if args.output:
        _write(args.output, out)
    if args.json:
        print(json.dumps({"text": out, "report": rep.as_dict()}, indent=2, ensure_ascii=False))
        return 0
    if args.report or args.output:
        print(U.render_report(rep), file=sys.stderr if not args.output else sys.stdout)
    if not args.output:
        print(out, end="" if out.endswith("\n") else "\n")
    return 0


def cmd_detect(args) -> int:
    a = D.detect(T.read_input(args.file))
    if args.compare:
        b = D.detect(T.read_input(args.compare))
        _emit(args, {"before": a.as_dict(), "after": b.as_dict()}, D.render_delta(a, b))
        return 0
    _emit(args, a.as_dict(), D.render(a))
    return 0 if a.verdict == "PASS" else 1


def cmd_research(args) -> int:
    outs = M.research(M.read_rows(T.read_input(args.file)), args.min_posts)
    if args.md:
        _write(args.md, M.swipe_markdown(outs))
    payload = [o.__dict__ for o in outs]
    human = M.render_research(outs) + (f"\n\nwrote swipe file: {args.md}" if args.md else "")
    _emit(args, payload, human)
    return 0


def cmd_audit(args) -> int:
    posts = M.audit(M.read_rows(T.read_input(args.file)))
    payload = [{"first_line": p.first_line, "type": p.kind, "reach": p.reach, "views": p.views,
                "multiple": round(p.multiple, 2), "rates": {k: round(v, 3) for k, v in p.rates.items()},
                "published": p.published} for p in posts]
    _emit(args, payload, M.render_audit(posts, args.top))
    return 0


def cmd_plan(args) -> int:
    items, problems = P.read_plan(T.read_input(args.file))
    if args.ics:
        _write(args.ics, P.to_ics(items, args.name, args.minutes, args.alarm))
    notes = P.balance(items)
    human = "\n".join([f"PLAN  {len(items)} items"] + [f"  ! {p}" for p in problems] + [f"  - {n}" for n in notes]
                      + ([f"wrote calendar: {args.ics}"] if args.ics else []))
    _emit(args, {"items": items, "problems": problems, "notes": notes}, human)
    return 1 if problems else 0


def cmd_carousel(args) -> int:
    slides = K.parse(T.read_input(args.file))
    notes = K.lint(slides)
    paths = []
    if not args.lint_only:
        paths = K.render_all(slides, args.out, ratio=args.ratio, bg=args.bg, fg=args.fg,
                             accent=args.accent, handle=args.handle)
    human = "\n".join([f"CAROUSEL  {len(slides)} slides  {args.ratio}"] + [f"  {n}" for n in notes]
                      + ([f"  wrote {len(paths)} SVGs to {args.out}"] if paths else []))
    _emit(args, {"slides": len(slides), "lint": notes, "files": paths}, human)
    return 1 if any(n.startswith("FAIL") for n in notes) else 0


def cmd_profile(args) -> int:
    if args.rubric:
        rub = T.load_data("profile_rubric.json")
        if args.json:
            print(json.dumps(rub, indent=2))
        else:
            print(rub["about"])
            for it in rub["items"]:
                print(f"  {it['max']:>3}  {it['id']:<17}{'(auto) ' if it.get('auto') else ''}{it['check']}")
        return 0
    bio = T.read_input(args.bio) if args.bio and os.path.exists(args.bio) else (args.bio or "")
    bio = bio.replace("\\n", "\n")
    kws = [k.strip() for k in (args.keywords or "").split(",") if k.strip()]
    res = PR.lint(args.name or "", bio, args.links, kws)
    human = "PROFILE\n" + "\n".join(f"  {s:<4}  {n:<13} {d}" for s, n, d in res)
    _emit(args, [{"status": s, "check": n, "detail": d} for s, n, d in res], human)
    return 0


def cmd_log(args) -> int:
    if args.action == "add":
        txt = T.read_input(args.file)
        e = L.add(args.kind, txt, H.classify(txt.split("\n")[0])[0])
        print(f"logged {e['kind']}: {T.shorten(e['first_line'], 60)}")
    elif args.action == "list":
        for e in L.entries()[-args.n:]:
            print(f"{e['at'][:10]}  {e['kind']:<9} {e.get('pattern') or '-':<22} {T.shorten(e['first_line'], 50)}")
    elif args.action == "check":
        hits = L.near_duplicates(T.read_input(args.file), args.threshold)
        if not hits:
            print("no near-duplicates in your log")
            return 0
        for s, e in hits[:10]:
            print(f"{s:.0%} overlap  {e['at'][:10]}  {T.shorten(e['first_line'], 60)}")
        print("Re-angle it (new hook, new example, new format) rather than re-posting.")
        return 1
    return 0


def cmd_limits(args) -> int:
    data = T.load_data("platform.json")
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print(f"checked {data['checked']}  -  {data['warning']}")
    for k, v in data["limits"].items():
        print(f"  {k:<20} {v['value']}")
    for k, v in data["sizes"].items():
        dims = f"{v['w']}x{v['h']}" if "w" in v else ""
        print(f"  {k:<20} {v['ratio']:<5} {dims}")
    return 0


# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="igos", description=__doc__.split("\n\n")[0])
    ap.add_argument("--version", action="version", version=f"igos {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, help_):
        p = sub.add_parser(name, help=help_)
        p.set_defaults(fn=fn)
        p.add_argument("--json", action="store_true", help="machine-readable output")
        return p

    p = add("init", cmd_init, "create ~/.instagram-growth-os with brand.md")
    p.add_argument("--home")
    p.add_argument("--force", action="store_true")

    p = add("hook", cmd_hook, "score and rank hooks (one per line)")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("--hook", action="append", help="score a hook given inline (repeatable)")

    p = add("patterns", cmd_patterns, "list the hook pattern library")
    p.add_argument("--family", choices=["proof", "tension", "curiosity", "utility", "story"])

    p = add("beats", cmd_beats, "time a Reel script, flag drop-off risks, export .srt")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("--target", type=float)
    p.add_argument("--sps", type=float, default=5.0, help="syllables per second (default 5.0)")
    p.add_argument("--srt", help="write burned-caption .srt here")

    p = add("caption", cmd_caption, "lint a caption and preview the feed cut")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("--keywords", help="comma-separated search terms that should appear")
    p.add_argument("--sponsored", action="store_true", help="require a paid-partnership disclosure")

    p = add("humanize", cmd_humanize, "strip invisible chars, typography and stock phrasing")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("-o", "--output")
    p.add_argument("--report", action="store_true")

    p = add("detect", cmd_detect, "five reads-human checks; pass a second file to compare")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("compare", nargs="?")

    p = add("research", cmd_research, "rank captured reels by outlier multiple")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("--md", help="write a markdown swipe file here")
    p.add_argument("--min-posts", type=int, default=3)

    p = add("audit", cmd_audit, "analyse your Insights CSV export")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("--top", type=int, default=5)

    p = add("plan", cmd_plan, "validate a plan CSV and export .ics")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("--ics")
    p.add_argument("--name", default="Instagram plan")
    p.add_argument("--minutes", type=int, default=30)
    p.add_argument("--alarm", type=int, default=60)

    p = add("carousel", cmd_carousel, "lint and render carousel slides to SVG")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("--out", default="carousel")
    p.add_argument("--ratio", choices=list(K.SIZES), default="4:5")
    p.add_argument("--bg", default="#111111")
    p.add_argument("--fg", default="#F5F5F0")
    p.add_argument("--accent", default="#FFB000")
    p.add_argument("--handle", default="")
    p.add_argument("--lint-only", action="store_true")

    p = add("profile", cmd_profile, "lint name field and bio")
    p.add_argument("--name")
    p.add_argument("--bio", help="bio text or a file path; use \\n for line breaks")
    p.add_argument("--links", type=int, default=1)
    p.add_argument("--keywords")
    p.add_argument("--rubric", action="store_true", help="print the 100-point rubric")

    p = add("log", cmd_log, "local post log and near-duplicate check")
    p.add_argument("action", choices=["add", "list", "check"])
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("--kind", default="reel")
    p.add_argument("-n", type=int, default=20)
    p.add_argument("--threshold", type=float, default=0.35)

    add("limits", cmd_limits, "print the platform limits igos enforces")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except FileNotFoundError as e:
        print(f"igos: {e.strerror}: {e.filename}", file=sys.stderr)
        return 2
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main())
