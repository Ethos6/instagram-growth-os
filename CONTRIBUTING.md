# Contributing

- **Keep it dependency-free.** The CLI must run on a stock Python 3.9+.
- **Tests first.** Add a case to `tests/test_igos.py` for any behaviour change.
  Every hook pattern's example must classify as that pattern (a test enforces it).
- **Platform facts need a source.** When you change `igos/data/platform.json`,
  update `checked` and add a `source` URL.
- **Skills:** folder name == `name:` in the frontmatter; the description says
  *when* to use it. Skills write; they never post or automate Instagram actions.
- **No fabricated data** in examples presented as real results.

Run: `python3 -m unittest discover -s tests -v`
