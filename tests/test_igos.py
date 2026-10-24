import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from igos import beats, caption, carousel, detect, hooks, humanize, log, metrics, plan, profile  # noqa: E402
from igos import text as T  # noqa: E402

EX = os.path.join(ROOT, "examples")


def read(name):
    with open(os.path.join(EX, name), encoding="utf-8") as fh:
        return fh.read()


class TextTests(unittest.TestCase):
    def test_hashtags_and_mentions(self):
        s = "Hi @asha.rao see https://x.com/#frag #one #two"
        self.assertEqual(T.hashtags(s), ["#one", "#two"])
        self.assertEqual(T.mentions(s), ["@asha.rao"])

    def test_spoken_numbers_are_concrete(self):
        self.assertTrue(T.concrete_markers("I lost twenty grand"))
        self.assertTrue(T.concrete_markers("I lost $20,000"))
        self.assertFalse(T.concrete_markers("I lost a lot of money"))

    def test_syllables_reasonable(self):
        self.assertEqual(T.syllables("cat"), 1)
        self.assertGreaterEqual(T.syllables("unbelievably"), 4)


class HookTests(unittest.TestCase):
    def test_bad_hooks_rank_below_good(self):
        good = "Skipping a deposit cost me $6,400 last spring."
        bad = "Hi everyone, so today I want to talk about my content process"
        r = hooks.rank([bad, good])
        self.assertEqual(r[0].hook, good)
        self.assertEqual(r[-1].verdict, "REWRITE")
        self.assertTrue(r[-1].dealbreakers)

    def test_attention_begging_is_a_dealbreaker(self):
        self.assertTrue(hooks.score_hook("Stop scrolling, you need to see this").dealbreakers)

    def test_classify_known_and_abstain(self):
        self.assertEqual(hooks.classify("What nobody tells you about freelancing is the silence")[0], "The Quiet Part")
        self.assertIsNone(hooks.classify("my desk setup")[0])

    def test_every_pattern_regex_matches_its_example(self):
        for p in T.load_data("hooks.json")["patterns"]:
            name, _ = hooks.classify(p["example"])
            self.assertEqual(name, p["name"], p["id"])


class BeatTests(unittest.TestCase):
    def test_build_and_flags(self):
        script = read("script.txt")
        bs = beats.build(script)
        self.assertEqual(bs[0].label, "HOOK")
        self.assertEqual(bs[-1].label, "PAYOFF")
        self.assertTrue(bs[0].cards)
        flags = beats.check(bs, target=25)
        self.assertTrue(any("Loop OK" in f for f in flags))

    def test_srt(self):
        srt = beats.to_srt(beats.build("one two three four five six seven\nend line here"))
        self.assertIn("00:00:00,000 -->", srt)
        self.assertTrue(srt.startswith("1\n"))


class CaptionTests(unittest.TestCase):
    def test_hashtag_cap(self):
        c = "Line one 5 things\n" + " ".join(f"#t{i}" for i in range(7))
        names = {x.name: x.status for x in caption.lint(c)}
        self.assertEqual(names["HASHTAGS"], "FAIL")

    def test_sponsored_requires_disclosure(self):
        names = {x.name: x.status for x in caption.lint("Love this 3-day trip.", sponsored=True)}
        self.assertEqual(names["DISCLOSURE"], "FAIL")
        names = {x.name: x.status for x in caption.lint("#ad Love this 3-day trip.", sponsored=True)}
        self.assertEqual(names["DISCLOSURE"], "PASS")

    def test_preview(self):
        vis, trunc = caption.feed_preview("a" * 300)
        self.assertEqual(len(vis), 125)
        self.assertTrue(trunc)


class HumanizeTests(unittest.TestCase):
    def test_invisible_and_dash(self):
        out, rep = humanize.humanize("We delve​ into it — really.")
        self.assertNotIn("​", out)
        self.assertNotIn("—", out)
        self.assertIn("dig into", out)
        self.assertGreaterEqual(rep.total, 3)

    def test_keeps_emoji_zwj(self):
        fam = "\U0001F468‍\U0001F469‍\U0001F467"
        out, _ = humanize.humanize(f"family {fam} day")
        self.assertIn(fam, out)

    def test_urls_and_tags_untouched(self):
        out, _ = humanize.humanize("See https://example.com/leverage and #leverage")
        self.assertIn("https://example.com/leverage", out)
        self.assertIn("#leverage", out)

    def test_capitalisation_preserved(self):
        out, _ = humanize.humanize("Utilize this. Leverage that.")
        self.assertTrue(out.startswith("Use this. Use that."))

    def test_detect_improves(self):
        src = read("slop.txt")
        a = detect.detect(src)
        b = detect.detect(humanize.humanize(src)[0])
        self.assertGreater(b.score, a.score)


class MetricsTests(unittest.TestCase):
    def test_research_multiple(self):
        raw = "handle,views,hook\n" + "\n".join(
            [f"a,{v},hook {i}" for i, v in enumerate([100, 100, 100, 1000])]
        )
        outs = metrics.research(metrics.read_rows(raw))
        self.assertAlmostEqual(outs[0].multiple, 10.0)

    def test_audit_example(self):
        raw = read("insights_export.csv")
        posts = metrics.audit(metrics.read_rows(raw))
        self.assertEqual(len(posts), 24)
        self.assertIn("shares", posts[0].rates)
        self.assertIn("SENDS PER REACH", metrics.render_audit(posts))

    def test_num(self):
        self.assertEqual(metrics._num("1.2K"), 1200)
        self.assertEqual(metrics._num("3,400"), 3400)
        self.assertIsNone(metrics._num("--"))


class PlanTests(unittest.TestCase):
    def test_ics(self):
        items, problems = plan.read_plan(read("plan.csv"))
        self.assertFalse(problems)
        ics = plan.to_ics(items)
        self.assertEqual(ics.count("BEGIN:VEVENT"), len(items))
        self.assertTrue(all(len(l.encode()) <= 75 for l in ics.split("\r\n")))

    def test_bad_rows(self):
        _, problems = plan.read_plan("date,time,format,title\nnope,10:00,reel,x\n")
        self.assertTrue(problems)


class CarouselTests(unittest.TestCase):
    def test_parse_lint_render(self):
        slides = carousel.parse(read("carousel.md"))
        self.assertEqual(len(slides), 6)
        self.assertEqual(carousel.lint(slides), ["PASS"])
        with tempfile.TemporaryDirectory() as d:
            paths = carousel.render_all(slides, d, ratio="3:4")
            self.assertEqual(len(paths), 6)
            with open(paths[0], encoding="utf-8") as fh:
                self.assertIn('height="1440"', fh.read())

    def test_slide_cap(self):
        slides = [carousel.Slide(f"s{i}", []) for i in range(21)]
        self.assertTrue(carousel.lint(slides)[0].startswith("FAIL"))


class ProfileTests(unittest.TestCase):
    def test_bio_too_long(self):
        res = {n: s for s, n, _ in profile.lint("x", "a" * 151)}
        self.assertEqual(res["BIO LENGTH"], "FAIL")


class LogTests(unittest.TestCase):
    def test_near_duplicate(self):
        corpus = [{"text": "Skipping a deposit cost me 6400 dollars last spring and here is why", "first_line": "x", "at": "2026"}]
        hits = log.near_duplicates("Skipping a deposit cost me 6400 dollars last spring and here is how", corpus=corpus)
        self.assertTrue(hits)
        self.assertFalse(log.near_duplicates("Completely different idea about lighting", corpus=corpus))


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "igos", *args], cwd=ROOT, capture_output=True, text=True)

    def test_json_outputs_parse(self):
        for args in (["hook", "examples/hooks.txt"], ["caption", "examples/caption.txt"],
                     ["detect", "examples/caption.txt"], ["limits"], ["patterns"]):
            r = self.run_cli(*args, "--json")
            json.loads(r.stdout)

    def test_missing_file(self):
        r = self.run_cli("caption", "does-not-exist.txt")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
