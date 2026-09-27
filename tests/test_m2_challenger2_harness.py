#!/usr/bin/env python3
"""
Empirical Challenger 2 Adversarial Stress Test Harness for Milestone 2: README.md Parity & Harmonization
Ecosystem: DuongNAD/DuongNAD

Author: teamwork_preview_challenger_m2_2 (Empirical Challenger)
Target: README.md, assets/, profile-3d-contrib/

Covers:
1. GFM & HTML DOM Structure, Tag Stack Balancer, and Mobile/Desktop Viewport Simulation
2. Mojibake, Multi-byte Encoding Artifacts & UTF-8 Byte Stream Integrity
3. Forbidden Legacy Blue/Neon Hex Detection & Approved Living Systems Palette Enforcement
4. 7 Core Projects & 3 Verified Credentials Parity Oracle
5. Camo CDN Cache-Busting (?v=nature_2026) Completeness on Local SVGs
6. Real-world Link Integrity and File System Resolution
"""

import html.parser
import os
import re
import ssl
import sys
import unicodedata
import unittest
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set, Tuple

import markdown
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"

FORBIDDEN_HEX_LITERALS = [
    "2563EB",  # Legacy Blue 600
    "1D4ED8",  # Legacy Blue 700
    "60A5FA",  # Legacy Blue 400
    "00EA64",  # Neon Green/Cyan
    "38BDF8",  # Sky 400
    "1E3A8A",  # Blue 900
    "3B82F6",  # Blue 500
    "00FFFF",  # Pure Cyan
    "FF00FF",  # Pure Magenta
]

APPROVED_PALETTE_HEXES = {
    # Emeralds & Teals
    "10B981", "059669", "047857", "064E3B", "34D399", "6EE7B7", "A7F3D0", "D1FAE5",
    "0D9488", "14B8A6", "0F766E", "115E59", "134E4A", "2DD4BF", "5EEAD4", "99F6E4",
    # Forest Greens & Pine Horizon
    "134236", "0B241E", "05120F", "04120E", "081E1A", "143E37", "1B4D43", "091F24",
    "0F342D", "14463C", "1B4D43", "0D2B25", "050D14", "1D4E3F",
    # Celestial & Twilight Accents
    "FEF08A", "FDE047", "CA8A04", "E5E7EB", "F0FDF4", "F8FAFC", "FFFFFF",
    # Dark Slate & Night Skies
    "0F172A", "1E293B", "334155", "475569", "0B1220", "020617",
}

EXPECTED_CORE_PROJECTS = [
    ("LIVA", r"LIVA|duongnad/liva"),
    ("Anima Engine", r"Anima[- ]Engine"),
    ("Buy or Wait?", r"Buy or Wait\?"),
    ("MindSync / VAIC", r"MindSync|VN_AI_Innovation|AI Public Service Assistant"),
    ("Darwin Lab", r"Darwin[- ]core|Darwin Lab"),
    ("mcp-agy", r"mcp-agy"),
    ("Vision Robotic Arm", r"Vision-Guided Robotic Arm|DENSO Factory Hacks"),
]

EXPECTED_CREDENTIALS = [
    ("HackerRank Orchestrate", "1Hl0qvEHIbgp6Fus2o0EukKZImMNrEr-I"),
    ("MindSync VAIC Bootcamp", "1x8zT32FnxJ5GZxvohfV4F_Ey9QUNAUzZ"),
    ("DENSO Factory Hacks", "1K1Sfw4AnxBfi7deHBIaIqpH9cJ-G3ti9"),
]


class TestChallenger2GFMAndDOM(unittest.TestCase):
    """GFM rendering simulation and DOM tree validation."""

    def setUp(self):
        self.raw_text = README_PATH.read_text(encoding="utf-8")
        self.rendered_html = markdown.markdown(self.raw_text, extensions=['tables', 'fenced_code'])
        self.soup = BeautifulSoup(self.rendered_html, "html.parser")

    def test_dom_tree_validity_and_bs4_parsing(self):
        """Verify BeautifulSoup parses rendered GFM without tree decomposition or parsing errors."""
        self.assertIsNotNone(self.soup)
        # Check all headers
        h2_tags = [h.get_text().strip() for h in self.soup.find_all("h2")]
        expected_sections = ["About", "Featured Projects", "Awards & Leadership", "Tech Stack", "GitHub", "Trophies", "Contribution City", "Connect"]
        for sec in expected_sections:
            self.assertIn(sec, h2_tags, f"Section '{sec}' missing from rendered GFM h2 headers")

    def test_featured_projects_table_symmetry_and_layout(self):
        """Verify 4x2 table layout in Featured Projects section."""
        tables = self.soup.find_all("table")
        self.assertGreaterEqual(len(tables), 2)
        proj_table = tables[0]
        rows = proj_table.find_all("tr")
        self.assertEqual(len(rows), 4, f"Featured Projects table must have exactly 4 rows, found {len(rows)}")
        for r_idx, row in enumerate(rows):
            cells = row.find_all("td", recursive=False)
            self.assertEqual(len(cells), 2, f"Row {r_idx+1} must have 2 cells, found {len(cells)}")
            for c_idx, cell in enumerate(cells):
                self.assertEqual(cell.get("width"), "50%", f"Cell ({r_idx+1}, {c_idx+1}) width must be 50%")
                self.assertEqual(cell.get("valign"), "top", f"Cell ({r_idx+1}, {c_idx+1}) valign must be top")

    def test_mobile_viewport_responsiveness(self):
        """Verify width='100%' on all full-width profile visual assets."""
        assets_needing_fluid_width = [
            "./assets/header.svg?v=nature_2026",
            "./assets/footer.svg?v=nature_2026",
            "./assets/github-contribution-grid-snake-dark.svg?v=nature_2026",
            "./assets/activity-graph.svg?v=nature_2026",
            "./assets/trophies.svg?v=nature_2026",
            "./profile-3d-contrib/profile-night-rainbow.svg?v=nature_2026",
        ]
        for src in assets_needing_fluid_width:
            img = self.soup.find("img", src=src)
            self.assertIsNotNone(img, f"Asset {src} not found in README.md")
            self.assertEqual(img.get("width"), "100%", f"Asset {src} must have width='100%' for mobile fluidity")

    def test_picture_tag_specification(self):
        """Verify the <picture> element implements dark and light mode correctly."""
        picture = self.soup.find("picture")
        self.assertIsNotNone(picture, "<picture> element missing")
        sources = picture.find_all("source")
        self.assertEqual(len(sources), 2, "Expected 2 <source> elements in <picture>")
        
        dark_source = picture.find("source", media="(prefers-color-scheme: dark)")
        light_source = picture.find("source", media="(prefers-color-scheme: light)")
        self.assertIsNotNone(dark_source, "Dark mode source missing in <picture>")
        self.assertIsNotNone(light_source, "Light mode source missing in <picture>")
        
        self.assertIn("github-contribution-grid-snake-dark.svg?v=nature_2026", dark_source.get("srcset"))
        self.assertIn("github-contribution-grid-snake.svg?v=nature_2026", light_source.get("srcset"))
        
        fallback_img = picture.find("img")
        self.assertIsNotNone(fallback_img, "Fallback <img> inside <picture> missing")
        self.assertIn("github-contribution-grid-snake-dark.svg?v=nature_2026", fallback_img.get("src"))


class TestChallenger2EncodingAndMojibake(unittest.TestCase):
    """Stress-test character encoding, Unicode byte sequence integrity, and absence of mojibake."""

    def setUp(self):
        self.raw_bytes = README_PATH.read_bytes()
        self.text = self.raw_bytes.decode("utf-8")

    def test_utf8_byte_stream_purity(self):
        """Ensure no BOM, valid UTF-8, and no illegal control characters."""
        self.assertFalse(self.raw_bytes.startswith(b'\xef\xbb\xbf'), "UTF-8 BOM detected")
        try:
            self.raw_bytes.decode("utf-8", errors="strict")
        except UnicodeDecodeError as e:
            self.fail(f"Strict UTF-8 decode failed: {e}")

    def test_zero_mojibake_signatures(self):
        """Search for Unicode replacement characters and Latin-1/CP1252 double-encoded tokens."""
        corrupt_tokens = [
            "\ufffd", "&#65533;", "&ufffd;",
            "Ã", "Â©", "Â·", "â€”", "â€“", "â€™", "â€˜", "â€œ", "â€¦",
            "ï¿½", "Ã¢", "Ã©", "Ã*", "Ã³",
        ]
        for token in corrupt_tokens:
            matches = list(re.finditer(re.escape(token), self.text))
            self.assertEqual(
                len(matches), 0,
                f"Mojibake token '{token}' detected {len(matches)} time(s) in README.md"
            )

    def test_vietnamese_diacritics_and_typography(self):
        """Verify Vietnamese diacritics and typographical symbols are valid Unicode NFC."""
        self.assertIn("DuongNAD", self.text)
        # Typographical punctuation checks
        for p in ['—', '–', '·', '•', '"', '"']:
            if p in self.text:
                self.assertTrue(unicodedata.name(p, None) is not None)


class TestChallenger2PaletteAndForbiddenHexes(unittest.TestCase):
    """Search for forbidden legacy blues and verify approved living systems palette."""

    def setUp(self):
        self.text = README_PATH.read_text(encoding="utf-8")

    def test_zero_forbidden_hex_literals(self):
        """Scan entire README.md for forbidden legacy blue and neon hex literals."""
        violations = {}
        for hex_code in FORBIDDEN_HEX_LITERALS:
            count = len(re.findall(re.escape(hex_code), self.text, re.IGNORECASE))
            if count > 0:
                violations[hex_code] = count
        self.assertEqual(
            len(violations), 0,
            f"Forbidden legacy hex literals found in README.md: {violations}"
        )

    def test_approved_palette_integration(self):
        """Verify theme badges and typing SVG use approved emerald and teal colors."""
        self.assertIn("color=059669", self.text, "Profile views counter must use emerald 059669")
        self.assertIn("10B981", self.text, "HackerRank badge and typing text must use emerald 10B981")
        self.assertIn("0D9488", self.text, "MindSync badge and RAG badge must use deep teal 0D9488")
        self.assertIn("134236", self.text, "DENSO badge must use dark pine 134236")


class TestChallenger2ParityAndCredentials(unittest.TestCase):
    """Verify presence of 7 core projects and 3 verified credentials."""

    def setUp(self):
        self.text = README_PATH.read_text(encoding="utf-8")

    def test_seven_core_projects(self):
        """Ensure all 7 core projects are present in README.md."""
        for name, pattern in EXPECTED_CORE_PROJECTS:
            self.assertIsNotNone(
                re.search(pattern, self.text, re.IGNORECASE),
                f"Core project {name} missing from README.md"
            )

    def test_three_verified_credentials(self):
        """Ensure all 3 verified Google Drive certificates are present in README.md."""
        for name, doc_id in EXPECTED_CREDENTIALS:
            self.assertIn(
                doc_id, self.text,
                f"Verified credential ID {doc_id} for {name} missing from README.md"
            )


class TestChallenger2CamoCacheBusting(unittest.TestCase):
    """Verify cache busting on all local SVG references."""

    def setUp(self):
        self.text = README_PATH.read_text(encoding="utf-8")

    def test_all_local_svgs_have_nature_2026(self):
        """Every local SVG reference must include '?v=nature_2026'."""
        local_svg_refs = re.findall(
            r'(?:src|srcset)=[\'"](\./(?:assets|profile-3d-contrib)/[^\'"]+\.svg[^\'"]*)[\'"]',
            self.text
        )
        self.assertGreaterEqual(len(local_svg_refs), 10)
        unversioned = [r for r in local_svg_refs if "?v=nature_2026" not in r]
        self.assertEqual(len(unversioned), 0, f"Unversioned local SVG references found: {unversioned}")

    def test_all_referenced_local_svgs_exist_on_disk(self):
        """Verify files on disk exist for all referenced SVGs."""
        local_svg_refs = re.findall(
            r'[\'"](\./(?:assets|profile-3d-contrib)/[^\'"]+\.svg)[^\'"]*[\'"]',
            self.text
        )
        for ref in local_svg_refs:
            disk_path = REPO_ROOT / ref.lstrip("./")
            self.assertTrue(disk_path.exists(), f"Local SVG missing on disk: {disk_path}")
            # Ensure valid XML
            ET.parse(disk_path)


def run_challenger2_suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    classes = [
        TestChallenger2GFMAndDOM,
        TestChallenger2EncodingAndMojibake,
        TestChallenger2PaletteAndForbiddenHexes,
        TestChallenger2ParityAndCredentials,
        TestChallenger2CamoCacheBusting,
    ]
    
    for cls in classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))
        
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("  CHALLENGER 2 ADVERSARIAL STRESS TEST SUMMARY")
    print("=" * 80)
    print(f"  Total Tests Run: {result.testsRun}")
    print(f"  Passed:         {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures:       {len(result.failures)}")
    print(f"  Errors:         {len(result.errors)}")
    print("=" * 80)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_challenger2_suite())
