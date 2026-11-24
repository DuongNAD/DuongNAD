"""Checks for the profile README and its generated artwork.

    python -m unittest discover tests      (or: pytest tests)
"""
import datetime
import importlib
import importlib.util
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
HAS_FONTTOOLS = importlib.util.find_spec("fontTools") is not None
PICTURE = re.compile(r"<picture>(.*?)</picture>", re.S)


def import_script(name):
    """Import a module from scripts/ without leaving that directory on sys.path."""
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        return importlib.import_module(name)
    finally:
        sys.path.remove(str(ROOT / "scripts"))


def without_fonts(svg: str) -> str:
    # The WOFF payload depends on the zlib build; the layout and the text must not.
    return re.sub(r"data:font/woff;base64,[A-Za-z0-9+/=]+", "data:font/woff;base64,", svg)


def generated() -> dict:
    banner = import_script("generate_banner")
    activity = import_script("generate_activity")
    stats = import_script("generate_stats")
    built = banner.build_all()
    built.update(activity.build_all(activity.read_activity()))
    built.update(stats.build_all(stats.read_stats()))
    return built


class ReadmeTests(unittest.TestCase):
    def test_local_images_in_readme_exist(self):
        paths = re.findall(r'(?:src|srcset)="\./([^"?]+)', README)
        self.assertGreater(len(paths), 5)
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file(), f"README references missing file {path}")

    def test_every_asset_is_used(self):
        for svg in sorted((ROOT / "assets").glob("*.svg")):
            with self.subTest(svg=svg.name):
                self.assertIn(f"./assets/{svg.name}", README, "orphaned asset; delete it or use it")

    def test_every_picture_has_a_dark_source_and_a_light_fallback(self):
        pictures = PICTURE.findall(README)
        self.assertGreaterEqual(len(pictures), 11)
        for body in pictures:
            sources = re.findall(r'<source media="([^"]+)" srcset="([^"]+)">', body)
            imgs = re.findall(r'<img src="([^"]+)"', body)
            with self.subTest(img=imgs):
                self.assertEqual(len(sources), 1)
                self.assertEqual(len(imgs), 1)
                media, dark = sources[0]
                self.assertEqual(media, "(prefers-color-scheme: dark)")
                # srcset splits candidates on commas, so a comma in the URL breaks the dark image.
                self.assertNotIn(",", dark)
                self.assertEqual(dark.replace("dark", "light"), imgs[0])

    def test_every_image_has_alt_text(self):
        imgs = re.findall(r"<img [^>]*>", README)
        self.assertGreater(len(imgs), 5)
        for img in imgs:
            with self.subTest(img=img[:60]):
                alt = re.search(r'alt="([^"]*)"', img)
                self.assertIsNotNone(alt)
                self.assertGreater(len(alt.group(1)), 20)

    def test_readme_features_the_four_cards_in_order(self):
        banner = import_script("generate_banner")
        shown = re.findall(r'<a href="https://github.com/DuongNAD/([^"]+)"><picture>.*?card-([a-z]+)-light\.svg', README)
        self.assertEqual(shown, [(card["repo"], card["slug"]) for card in banner.CARDS])
        self.assertEqual(len(shown), 4)

    def test_achievement_tiles_link_to_their_proof(self):
        banner = import_script("generate_banner")
        shown = re.findall(r'<a href="([^"]+)"><picture>.*?award-([a-z]+)-light\.svg', README)
        self.assertEqual(shown, [(award["href"], award["slug"]) for award in banner.AWARDS])

    def test_cards_fit_two_per_row_in_the_profile_column(self):
        # GitHub's profile README column is 846 px wide; a space separates inline images.
        banner = import_script("generate_banner")
        self.assertLessEqual(2 * banner.IMG_W + 6, 846)
        for width in re.findall(r'card-[a-z]+-light\.svg" width="(\d+)"', README):
            self.assertEqual(int(width), banner.IMG_W)


@unittest.skipUnless(HAS_FONTTOOLS, "fontTools is not installed")
class ArtTests(unittest.TestCase):
    def test_every_svg_is_well_formed(self):
        for svg in sorted((ROOT / "assets").glob("*.svg")):
            with self.subTest(svg=svg.name):
                ET.parse(svg)

    def test_committed_art_matches_generator(self):
        built = generated()
        committed = sorted(path.name for path in (ROOT / "assets").glob("*.svg"))
        self.assertEqual(sorted(built), committed)
        for name, svg in built.items():
            with self.subTest(svg=name):
                on_disk = (ROOT / "assets" / name).read_text(encoding="utf-8")
                self.assertEqual(
                    without_fonts(svg), without_fonts(on_disk),
                    f"assets/{name} is stale; run python scripts/generate_banner.py "
                    "and python scripts/generate_activity.py",
                )

    def test_generated_art_is_self_contained(self):
        # GitHub shows README images in an <img> sandbox: nothing external may be needed to render them.
        for name, svg in generated().items():
            with self.subTest(svg=name):
                self.assertIn("data:font/woff;base64,", svg)
                external = re.findall(r'(?:href|src)="(https?://[^"]+)"|url\((https?://[^)]+)\)', svg)
                self.assertEqual(external, [])
                self.assertIn("<title", svg)
                self.assertIn("<desc", svg)

    def test_light_and_dark_art_differ_only_in_color(self):
        built = generated()
        hexes = re.compile(r"#[0-9a-fA-F]{6}\b|stroke-opacity=\"[^\"]+\"|fill-opacity=\"[^\"]+\"|stop-opacity=\"[^\"]+\"")
        for name in built:
            if not name.endswith("-dark.svg"):
                continue
            light = name.replace("-dark.svg", "-light.svg")
            with self.subTest(svg=name):
                self.assertEqual(
                    hexes.sub("", without_fonts(built[name])), hexes.sub("", without_fonts(built[light]))
                )

    def test_activity_graph_shows_the_fetched_numbers(self):
        activity = import_script("generate_activity")
        days = activity.read_activity()
        for (earlier, _), (later, _) in zip(days, days[1:]):
            self.assertEqual(later - earlier, datetime.timedelta(days=1), "activity.json has a gap")
        counts = [count for _, count in days]
        _, peak_day = max((count, day) for day, count in days)
        expected = (
            f">{sum(counts):,}<",
            f">{sum(1 for count in counts if count)}<",
            f">{max(counts)}<",
            f"best day · {activity.short_date(peak_day)}<",
        )
        for theme in ("dark", "light"):
            svg = (ROOT / "assets" / f"activity-{theme}.svg").read_text(encoding="utf-8")
            for text in expected:
                with self.subTest(theme=theme, text=text):
                    self.assertIn(text, svg)

    def test_stats_panel_shows_the_fetched_numbers(self):
        stats_module = import_script("generate_stats")
        stats = stats_module.read_stats()
        for theme in ("dark", "light"):
            svg = (ROOT / "assets" / f"stats-{theme}.svg").read_text(encoding="utf-8")
            for field, label, _, _ in stats_module.METRICS:
                with self.subTest(theme=theme, field=field):
                    self.assertIn(f">{stats_module.number(stats[field])}<", svg)
                    self.assertIn(f">{label}<", svg)

    def test_trophy_ranks_follow_the_milestones(self):
        stats_module = import_script("generate_stats")
        milestones = (1, 10, 30, 50, 100, 200, 500, 1000)
        self.assertIsNone(stats_module.rank(0, milestones))
        self.assertEqual(stats_module.RANKS[stats_module.rank(1, milestones)], "C")
        self.assertEqual(stats_module.RANKS[stats_module.rank(410, milestones)], "S")
        self.assertEqual(stats_module.RANKS[stats_module.rank(1000, milestones)], "SSS")
        self.assertEqual(stats_module.RANKS[stats_module.rank(99999, milestones)], "SSS")
        for _, _, _, steps in stats_module.TROPHIES:
            self.assertEqual(len(steps), len(stats_module.RANKS))
            self.assertEqual(list(steps), sorted(set(steps)))

    def test_activity_axis_covers_the_peak_in_at_most_four_steps(self):
        activity = import_script("generate_activity")
        for peak in (0, 1, 4, 5, 17, 69, 100, 1234):
            with self.subTest(peak=peak):
                step, top = activity.nice_scale(peak)
                self.assertGreaterEqual(top, peak)
                self.assertLessEqual(top // step, 4)


class FetcherTests(unittest.TestCase):
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

    def test_stats_fetcher_counts_streaks_and_totals(self):
        spec = importlib.util.spec_from_file_location("fetch_stats", ROOT / "scripts" / "fetch-stats.py")
        fetcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fetcher)
        today = datetime.date(2026, 11, 24)

        def days(*pairs):
            return {f"2026-11-{day:02d}": count for day, count in pairs}

        # Best run of 3 (10-12); the current run of 2 ends yesterday because today is still quiet.
        self.assertEqual(fetcher.streaks(days((10, 1), (11, 4), (12, 2), (13, 0), (22, 5), (23, 1), (24, 0)), today), (2, 3))
        # A quiet yesterday ends the current streak.
        self.assertEqual(fetcher.streaks(days((20, 1), (21, 1), (22, 1), (23, 0), (24, 0)), today), (0, 3))
        # Today counts once it has a contribution; days after today are ignored.
        self.assertEqual(fetcher.streaks(days((23, 1), (24, 2), (25, 9), (26, 9)), today), (2, 2))
        self.assertEqual(fetcher.streaks({}, today), (0, 0))

        def calendar(pairs):
            return {"weeks": [{"contributionDays": [{"date": d, "contributionCount": c} for d, c in pairs]}]}

        profile = {"data": {"user": {
            "followers": {"totalCount": 14},
            "pullRequests": {"totalCount": 738},
            "contributionsCollection": {"contributionYears": [2026, 2025]},
            "repositories": {"totalCount": 3, "nodes": [{"stargazerCount": 400}, {"stargazerCount": 9}, {"stargazerCount": 1}],
                             "pageInfo": {"hasNextPage": False, "endCursor": None}},
        }}}
        years = {"data": {"user": {
            "y2025": {"totalCommitContributions": 7, "contributionCalendar": {
                "totalContributions": 10, **calendar([("2025-12-31", 10)])}},
            "y2026": {"totalCommitContributions": 4902, "contributionCalendar": {
                "totalContributions": 5897, **calendar([("2026-01-01", 3), ("2026-11-23", 6), ("2026-11-24", 1)])}},
        }}}
        self.assertEqual(fetcher.summarize([profile], years, today), {
            "stars": 410, "commits": 4909, "pull_requests": 738, "contributions": 5907,
            "repositories": 3, "followers": 14, "current_streak": 2, "best_streak": 2,
        })
        with self.assertRaises(ValueError):
            fetcher.summarize([{"errors": [{"message": "Bad credentials"}]}], years, today)
        self.assertIn('y2025:contributionsCollection(from:"2025-01-01T00:00:00Z"', fetcher.years_query([2025, 2026]))


if __name__ == "__main__":
    unittest.main()
