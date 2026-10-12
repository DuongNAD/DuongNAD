"""Checks for the profile README and its generated artwork.

    python -m unittest discover tests      (or: pytest tests)
"""
import datetime
import importlib
import importlib.util
import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
GENERATED = [
    "header.svg", "footer.svg", "highlights.svg", "activity-graph.svg",
    "card-mcp-agy.svg", "card-smart-drive.svg", "card-aurora.svg", "card-mindsync.svg",
]


def import_script(name):
    """Import a module from scripts/ without leaving that directory on sys.path."""
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        return importlib.import_module(name)
    finally:
        sys.path.remove(str(ROOT / "scripts"))


class ProfileTests(unittest.TestCase):
    def test_every_svg_is_well_formed(self):
        for svg in sorted((ROOT / "assets").glob("*.svg")):
            with self.subTest(svg=svg.name):
                ET.parse(svg)

    def test_local_images_in_readme_exist(self):
        paths = re.findall(r'(?:src|srcset)="\./([^"?]+)', README)
        self.assertGreater(len(paths), 5)
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), f"README references missing file {path}")

    def test_generated_art_is_self_contained(self):
        # GitHub shows README images in an <img> sandbox: nothing external may be needed to render them.
        for name in GENERATED:
            with self.subTest(svg=name):
                text = (ROOT / "assets" / name).read_text(encoding="utf-8")
                self.assertIn("data:font/woff;base64,", text)
                external = re.findall(r'(?:href|src)="(https?://[^"]+)"|url\((https?://[^)]+)\)', text)
                self.assertEqual(external, [])

    @unittest.skipUnless(importlib.util.find_spec("fontTools"), "fontTools is not installed")
    def test_committed_art_matches_generator(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import generate_activity as activity
            import generate_banner as banner
            import generate_highlights as highlights
        finally:
            sys.path.remove(str(ROOT / "scripts"))
        built = {"header.svg": banner.build_header(), "footer.svg": banner.build_footer()}
        built.update({f"card-{card['slug']}.svg": banner.build_card(card) for card in banner.CARDS})
        built["highlights.svg"] = highlights.build_highlights(highlights.read_stats())
        built["activity-graph.svg"] = activity.build_activity(activity.read_activity())
        self.assertEqual(sorted(built), sorted(GENERATED))
        for name, svg in built.items():
            with self.subTest(svg=name):
                committed = (ROOT / "assets" / name).read_text(encoding="utf-8")
                self.assertEqual(
                    svg, committed,
                    f"assets/{name} is stale; run python scripts/generate_banner.py, "
                    "python scripts/generate_highlights.py and python scripts/generate_activity.py",
                )

    @unittest.skipUnless(importlib.util.find_spec("fontTools"), "fontTools is not installed")
    def test_highlights_show_the_stats_widget_numbers(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import generate_highlights as highlights
        finally:
            sys.path.remove(str(ROOT / "scripts"))
        stats = highlights.read_stats()
        self.assertEqual(sorted(stats), ["commits", "contribs", "followers", "prs", "repos", "stars", "streak"])
        svg = (ROOT / "assets" / "highlights.svg").read_text(encoding="utf-8")
        for key, value in stats.items():
            with self.subTest(stat=key):
                self.assertRegex(value, r"^[\d.,]+k?$")
                self.assertIn(f">{value}<", svg)


    def test_profile_stats_fetcher_reads_the_api_payload(self):
        spec = importlib.util.spec_from_file_location("fetch_profile_stats", ROOT / "scripts" / "fetch-profile-stats.py")
        fetcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fetcher)
        payload = {"login": "DuongNAD", "public_repos": 63, "followers": 11, "following": 10}
        self.assertEqual(fetcher.extract(payload), {"repos": 63, "followers": 11})
        with self.assertRaises(KeyError):
            fetcher.extract({"login": "DuongNAD"})
        committed = json.loads((ROOT / "assets" / "profile-stats.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(committed), ["followers", "repos"])

    @unittest.skipUnless(importlib.util.find_spec("fontTools"), "fontTools is not installed")
    def test_activity_graph_shows_the_fetched_numbers(self):
        activity = import_script("generate_activity")
        days = activity.read_activity()
        for (earlier, _), (later, _) in zip(days, days[1:]):
            self.assertEqual(later - earlier, datetime.timedelta(days=1), "activity.json has a gap")
        counts = [count for _, count in days]
        _, peak_day = max((count, day) for day, count in days)
        svg = (ROOT / "assets" / "activity-graph.svg").read_text(encoding="utf-8")
        expected = (
            f">{sum(counts):,}<",
            f">{sum(1 for count in counts if count)}<",
            f">{max(counts)}<",
            f"best day · {activity.short_date(peak_day)}<",
        )
        for text in expected:
            with self.subTest(text=text):
                self.assertIn(text, svg)

    @unittest.skipUnless(importlib.util.find_spec("fontTools"), "fontTools is not installed")
    def test_activity_axis_covers_the_peak_in_at_most_four_steps(self):
        activity = import_script("generate_activity")
        for peak in (0, 1, 4, 5, 17, 69, 100, 1234):
            with self.subTest(peak=peak):
                step, top = activity.nice_scale(peak)
                self.assertGreaterEqual(top, peak)
                self.assertLessEqual(top // step, 4)

    def test_activity_fetcher_reads_the_graphql_payload(self):
        spec = importlib.util.spec_from_file_location("fetch_activity", ROOT / "scripts" / "fetch-activity.py")
        fetcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fetcher)
        weeks = [
            {"contributionDays": [
                {"date": "2026-10-10", "contributionCount": 3},
                {"date": "2026-10-11", "contributionCount": 0},
            ]},
            {"contributionDays": [
                {"date": "2026-10-12", "contributionCount": 7},
                {"date": "2026-10-13", "contributionCount": 9},
            ]},
        ]
        payload = {"data": {"user": {"contributionsCollection": {"contributionCalendar": {"weeks": weeks}}}}}
        start, end = datetime.date(2026, 10, 11), datetime.date(2026, 10, 12)
        self.assertEqual(fetcher.extract(payload, start, end), {"2026-10-11": 0, "2026-10-12": 7})
        with self.assertRaises(ValueError):
            fetcher.extract({"errors": [{"message": "Bad credentials"}]}, start, end)
        with self.assertRaises(ValueError):
            fetcher.extract({"data": {"user": None}}, start, end)
        self.assertEqual(
            fetcher.window(datetime.date(2026, 10, 12)),
            (datetime.date(2026, 9, 12), datetime.date(2026, 10, 12)),
        )


if __name__ == "__main__":
    unittest.main()
