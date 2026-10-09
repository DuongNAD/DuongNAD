"""Checks for the profile README and its generated artwork.

    python -m unittest discover tests      (or: pytest tests)
"""
import importlib.util
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
GENERATED = ["header.svg", "footer.svg", "card-liva.svg", "card-mindsync.svg", "card-anima.svg", "card-mcp-agy.svg"]


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
        spec = importlib.util.spec_from_file_location("generate_banner", ROOT / "scripts" / "generate_banner.py")
        banner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(banner)
        built = {"header.svg": banner.build_header(), "footer.svg": banner.build_footer()}
        built.update({f"card-{card['slug']}.svg": banner.build_card(card) for card in banner.CARDS})
        self.assertEqual(sorted(built), sorted(GENERATED))
        for name, svg in built.items():
            with self.subTest(svg=name):
                committed = (ROOT / "assets" / name).read_text(encoding="utf-8")
                self.assertEqual(svg, committed, f"assets/{name} is stale; run python scripts/generate_banner.py")


if __name__ == "__main__":
    unittest.main()
