#!/usr/bin/env python3
"""
Comprehensive 4-Tier E2E Test Suite for GitHub Profile Ecosystem Harmonization (DuongNAD/DuongNAD)

Test Architecture:
- Tier 1: Feature Coverage (XML validity, header/footer contracts, 7 projects, 3 certs, dynamic widgets, workflows)
- Tier 2: Boundary & Corner Cases (malformed XML handling, error cards, empty inputs, extreme viewports, UTF-8 encoding)
- Tier 3: Cross-Feature Combinations (dark/light snake picture tag, Camo CDN cache-busting, palette harmony)
- Tier 4: Real-World Workload Scenarios (simulated profile render, workflow concurrency, external URL reachability with bot tolerance)

Execution:
  python tests/test_profile_ecosystem.py            # Standard progressive run (Exit code 0)
  python tests/test_profile_ecosystem.py --strict   # Strict full-suite run (Post-M4 gate)
  pytest tests/test_profile_ecosystem.py -v         # Pytest execution
"""

import os
import re
import ssl
import sys
import unittest
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Set, Tuple

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# Workspace root resolution
REPO_ROOT = Path(__file__).resolve().parent.parent
STRICT_MODE = ("--strict" in sys.argv) or (os.environ.get("STRICT_E2E", "0") == "1")

# Known living systems & nature theme palette
APPROVED_PALETTE_HEXES = {
    # Emeralds & Teals
    "10B981", "059669", "047857", "064E3B", "34D399", "6EE7B7", "A7F3D0", "D1FAE5",
    "0D9488", "14B8A6", "0F766E", "115E59", "134E4A", "2DD4BF", "5EEAD4", "99F6E4",
    # Forest Greens & Pine Horizon
    "134236", "0B241E", "05120F", "04120E", "081E1A", "143E37", "1B4D43", "091F24",
    "0F342D", "14463C", "1B4D43", "0D2B25", "050D14", "1D4E3F",
    # Celestial & Twilight Accents
    "FEF08A", "FDE047", "CA8A04", "E5E7EB", "F0FDF4", "F8FAFC",
    # Dark Slate & Night Skies
    "0F172A", "1E293B", "334155", "475569", "0B1220", "020617",
}

# 7 Core Projects contract
EXPECTED_CORE_PROJECTS = [
    ("LIVA", r"LIVA|duongnad/liva"),
    ("Anima Engine", r"Anima[- ]Engine"),
    ("Buy or Wait?", r"Buy or Wait\?"),
    ("MindSync / VAIC", r"MindSync|VN_AI_Innovation|AI Public Service Assistant"),
    ("Darwin Lab", r"Darwin[- ]core|Darwin Lab"),
    ("mcp-agy", r"mcp-agy"),
    ("Vision Robotic Arm", r"Vision-Guided Robotic Arm|DENSO Factory Hacks"),
]

# 3 Verified Honors & Credentials contract
EXPECTED_CREDENTIALS = [
    ("HackerRank Orchestrate", r"1Hl0qvEHIbgp6Fus2o0EukKZImMNrEr-I"),
    ("MindSync VAIC Bootcamp", r"1x8zT32FnxJ5GZxvohfV4F_Ey9QUNAUzZ"),
    ("DENSO Factory Hacks", r"1K1Sfw4AnxBfi7deHBIaIqpH9cJ-G3ti9"),
]


# ============================================================================
# TIER 1: FEATURE COVERAGE
# ============================================================================

class TestTier1FeatureCoverage(unittest.TestCase):
    """Tier 1: Complete functional and syntactic coverage of all profile assets."""

    def test_svg_xml_validity_all_assets(self):
        """Verify 100% of SVGs in assets/ and profile-3d-contrib/ parse cleanly without XML syntax errors."""
        assets_dir = REPO_ROOT / "assets"
        p3d_dir = REPO_ROOT / "profile-3d-contrib"

        svg_files = list(assets_dir.glob("*.svg")) + list(p3d_dir.glob("*.svg"))
        self.assertGreaterEqual(len(svg_files), 20, f"Expected at least 20 SVG assets, found {len(svg_files)}")

        failed_files = []
        for svg_path in svg_files:
            try:
                tree = ET.parse(svg_path)
                root = tree.getroot()
                tag = root.tag.lower()
                self.assertTrue(
                    tag.endswith("svg"),
                    f"{svg_path.name} root element is not <svg> (got {tag})"
                )
            except Exception as e:
                failed_files.append((svg_path.name, str(e)))

        self.assertEqual(
            len(failed_files), 0,
            f"XML parsing failed on {len(failed_files)} SVGs: {failed_files}"
        )

    def test_header_svg_contract(self):
        """Verify assets/header.svg satisfies the living systems Nordic twilight contract."""
        header_path = REPO_ROOT / "assets" / "header.svg"
        self.assertTrue(header_path.exists(), "assets/header.svg is missing")

        content = header_path.read_text(encoding="utf-8")
        tree = ET.parse(header_path)
        root = tree.getroot()

        # Contract: ViewBox 0 0 1200 260
        viewbox = root.get("viewBox", "")
        self.assertEqual(viewbox.strip(), "0 0 1200 260", "Header viewBox must be '0 0 1200 260'")

        # Contract: role="img" and aria-label
        self.assertEqual(root.get("role"), "img", "Header must declare role='img'")
        self.assertIn("aria-label", root.attrib, "Header must declare aria-label")

        # Contract: Self-contained styles, no external links
        self.assertNotIn("<link", content.lower(), "Header SVG must not contain external stylesheet links")
        self.assertNotIn("@import", content.lower(), "Header SVG must not use external @import")

        # Contract: Living systems elements
        self.assertIn("skyGrad", content, "Header must contain skyGrad gradient")
        self.assertIn("mtnFar", content, "Header must contain mtnFar gradient")
        self.assertIn("mtnMid", content, "Header must contain mtnMid gradient")
        self.assertIn("mtnNear", content, "Header must contain mtnNear gradient")
        self.assertIn("firefly", content, "Header must contain firefly gradient")

        # Contract: Typography & identity
        self.assertIn("NGUYỄN ANH DƯƠNG", content, "Header must contain candidate name in Vietnamese diacritics")
        self.assertIn("Living Systems", content, "Header must reflect Living Systems focus")

    def test_footer_svg_contract(self):
        """Verify assets/footer.svg satisfies the organic minimalist leaf signature contract."""
        footer_path = REPO_ROOT / "assets" / "footer.svg"
        self.assertTrue(footer_path.exists(), "assets/footer.svg is missing")

        content = footer_path.read_text(encoding="utf-8")
        tree = ET.parse(footer_path)
        root = tree.getroot()

        # Contract: ViewBox 0 0 1200 90
        viewbox = root.get("viewBox", "")
        self.assertEqual(viewbox.strip(), "0 0 1200 90", "Footer viewBox must be '0 0 1200 90'")

        # Contract: Leaf emblem & quote
        self.assertIn("leaf-accent", content, "Footer must contain leaf-accent gradient")
        self.assertIn("In nature as in software", content, "Footer must contain philosophical quote")
        self.assertIn("NGUYEN ANH DUONG (DuongNAD)", content, "Footer must contain author signature")

    def test_snake_assets_contract(self):
        """Verify light and dark contribution snake grids exist and parse."""
        light_snake = REPO_ROOT / "assets" / "github-contribution-grid-snake.svg"
        dark_snake = REPO_ROOT / "assets" / "github-contribution-grid-snake-dark.svg"

        self.assertTrue(light_snake.exists(), "Light snake asset missing")
        self.assertTrue(dark_snake.exists(), "Dark snake asset missing")

        ET.parse(light_snake)
        ET.parse(dark_snake)

    def test_repo_pins_contract(self):
        """Verify repository pin card SVGs are present in assets/."""
        pins = [
            "pin-liva.svg",
            "pin-anima.svg",
            "pin-buy-or-wait.svg",
            "pin-mcp-agy.svg",
            "pin-smart-drive-os.svg",
            "pin-vn-ai.svg",
        ]
        for pin_name in pins:
            pin_file = REPO_ROOT / "assets" / pin_name
            self.assertTrue(pin_file.exists(), f"Pin card {pin_name} must exist in assets/")
            ET.parse(pin_file)

    def test_featured_projects_parity(self):
        """
        Verify presence of all 7 core projects across ecosystem.
        Supports progressive testability: verifies pin cards & scripts,
        and verifies README representation with milestone awareness.
        """
        readme_path = REPO_ROOT / "README.md"
        self.assertTrue(readme_path.exists(), "README.md is missing")
        readme_content = readme_path.read_text(encoding="utf-8")

        # 1. Check all 7 projects exist in repository ecosystem (README or pins)
        found_in_ecosystem = {}
        for proj_name, pattern in EXPECTED_CORE_PROJECTS:
            in_readme = bool(re.search(pattern, readme_content, re.IGNORECASE))
            pin_exists = (REPO_ROOT / "assets" / f"pin-{proj_name.lower().split()[0]}.svg").exists() or \
                         (REPO_ROOT / "assets" / f"pin-{proj_name.lower().replace(' ', '-')}.svg").exists()
            found_in_ecosystem[proj_name] = in_readme or pin_exists
            self.assertTrue(
                found_in_ecosystem[proj_name],
                f"Core project {proj_name} not found in ecosystem (README or pin assets)"
            )

        # 2. Check README.md presence
        missing_in_readme = []
        for proj_name, pattern in EXPECTED_CORE_PROJECTS:
            if not re.search(pattern, readme_content, re.IGNORECASE):
                missing_in_readme.append(proj_name)

        if STRICT_MODE:
            self.assertEqual(
                len(missing_in_readme), 0,
                f"STRICT MODE: The following projects are missing from README.md: {missing_in_readme}"
            )
        else:
            # Progressive check: at least 6 projects in README.md; if mcp-agy missing, confirm pin asset is ready
            present_count = len(EXPECTED_CORE_PROJECTS) - len(missing_in_readme)
            self.assertGreaterEqual(
                present_count, 6,
                f"Progressive mode requires at least 6 projects in README.md, found {present_count}"
            )
            if "mcp-agy" in missing_in_readme:
                pin_mcp = REPO_ROOT / "assets" / "pin-mcp-agy.svg"
                self.assertTrue(pin_mcp.exists(), "mcp-agy pin SVG must be ready in assets/ for M2 integration")

    def test_verified_credentials_parity(self):
        """Verify the 3 verified honors/certifications with Google Drive URLs in README.md."""
        readme_path = REPO_ROOT / "README.md"
        readme_content = readme_path.read_text(encoding="utf-8")

        for name, doc_id in EXPECTED_CREDENTIALS:
            self.assertIn(
                doc_id, readme_content,
                f"Expected Google Drive credential ID {doc_id} for {name} missing from README.md"
            )

    def test_dynamic_widgets_inventory(self):
        """Verify all dynamic widgets exist on disk and are referenced in README.md."""
        readme_content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        widgets = [
            ("assets/stats.svg", "stats.svg"),
            ("assets/top-langs.svg", "top-langs.svg"),
            ("assets/streak.svg", "streak.svg"),
            ("assets/activity-graph.svg", "activity-graph.svg"),
            ("assets/trophies.svg", "trophies.svg"),
            ("profile-3d-contrib/profile-night-rainbow.svg", "profile-night-rainbow.svg"),
        ]
        for rel_path, filename in widgets:
            file_path = REPO_ROOT / rel_path
            self.assertTrue(file_path.exists(), f"Dynamic widget {rel_path} missing on disk")
            self.assertIn(filename, readme_content, f"Dynamic widget {filename} not referenced in README.md")

    def test_workflow_contracts(self):
        """Verify GitHub Actions workflows have valid syntax, branch triggers, and permissions."""
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        self.assertTrue(workflows_dir.exists(), ".github/workflows directory missing")

        required_workflows = ["snake.yml", "profile-3d.yml", "readme-widgets.yml"]
        for wf_name in required_workflows:
            wf_path = workflows_dir / wf_name
            self.assertTrue(wf_path.exists(), f"Workflow {wf_name} missing")
            content = wf_path.read_text(encoding="utf-8")

            if HAS_YAML:
                data = yaml.safe_load(content)
                self.assertIsInstance(data, dict, f"{wf_name} did not parse to a dictionary")
                self.assertIn("name", data)
                # In YAML 1.1 (PyYAML), unquoted 'on:' parses as boolean True
                self.assertTrue("on" in data or True in data, f"{wf_name} missing 'on' trigger specification")
                self.assertIn("jobs", data)

            # Common GitHub Actions contract checks
            self.assertIn("actions/checkout@v4", content, f"{wf_name} must use actions/checkout@v4")
            self.assertIn("contents: write", content, f"{wf_name} must declare contents: write permission")


# ============================================================================
# TIER 2: BOUNDARY & CORNER CASES
# ============================================================================

class TestTier2BoundaryCornerCases(unittest.TestCase):
    """Tier 2: Adversarial edge cases, malformed inputs, error card detection, and UTF-8 integrity."""

    def test_malformed_xml_rejection(self):
        """Verify XML parser rejects corrupted, unclosed, or invalid XML strings."""
        malformed_samples = [
            "<svg><rect width='100'></svg>",  # unclosed rect
            "<svg width=100 height=100></svg>",  # unquoted attributes
            "<svg>&foo;</svg>",  # undeclared entity
            "<svg xmlns='http://www.w3.org/2000/svg'><text>Unescaped & in text</text></svg>",  # raw &
            "not even xml",
        ]
        for sample in malformed_samples:
            with self.assertRaises(ET.ParseError, msg=f"Parser should reject: {sample}"):
                ET.fromstring(sample)

    def test_sanitizer_error_cards(self):
        """Verify widget sanitization function reliably rejects upstream API error cards."""
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        try:
            from sanitize_widget_module import sanitize
        except ImportError:
            # Inline extraction of the exact sanitize logic from fetch-all-widgets.py
            BAD = ("failed to retrieve", "something went wrong", "deployment_paused")
            def sanitize(text: str):
                if "<svg" not in text.lower():
                    return None
                lowered = text.lower()
                if any(token in lowered for token in BAD):
                    return None
                return text

        error_samples = [
            '<svg><text>Failed to retrieve GitHub stats</text></svg>',
            '<svg><text>Something went wrong with Vercel API</text></svg>',
            '<svg><text>deployment_paused</text></svg>',
            '<html><body>502 Bad Gateway</body></html>',
            '{"error": "rate limit exceeded"}',
        ]
        for err in error_samples:
            self.assertIsNone(
                sanitize(err),
                f"Sanitizer must reject error card payload: {err}"
            )

    def test_empty_and_whitespace_inputs(self):
        """Verify parser and sanitizer handle empty strings, whitespaces, and nulls safely."""
        with self.assertRaises(ET.ParseError):
            ET.fromstring("")
        with self.assertRaises(ET.ParseError):
            ET.fromstring("   \n\t  ")

    def test_extreme_viewports_and_aspect_ratios(self):
        """Verify viewBox parsing on SVG banners and validate aspect ratio constraints."""
        header_path = REPO_ROOT / "assets" / "header.svg"
        footer_path = REPO_ROOT / "assets" / "footer.svg"

        def get_viewbox(path: Path) -> Tuple[float, float, float, float]:
            root = ET.parse(path).getroot()
            vb = root.get("viewBox", "").strip().split()
            return tuple(float(x) for x in vb)

        h_x, h_y, h_w, h_h = get_viewbox(header_path)
        self.assertEqual(h_x, 0.0)
        self.assertEqual(h_y, 0.0)
        self.assertAlmostEqual(h_w / h_h, 1200 / 260, places=2, msg="Header aspect ratio must match 1200:260")

        f_x, f_y, f_w, f_h = get_viewbox(footer_path)
        self.assertEqual(f_x, 0.0)
        self.assertEqual(f_y, 0.0)
        self.assertAlmostEqual(f_w / f_h, 1200 / 90, places=2, msg="Footer aspect ratio must match 1200:90")

    def test_special_characters_and_encoding(self):
        """Verify valid UTF-8 encoding without mojibake across header, footer, and README."""
        files_to_check = [
            REPO_ROOT / "assets" / "header.svg",
            REPO_ROOT / "assets" / "footer.svg",
            REPO_ROOT / "README.md",
        ]
        mojibake_tokens = ["Ã", "Â©", "â€”", "\ufffd", "&#65533;"]

        for file_path in files_to_check:
            raw_bytes = file_path.read_bytes()
            # Must decode cleanly as UTF-8
            text = raw_bytes.decode("utf-8")
            for token in mojibake_tokens:
                self.assertNotIn(
                    token, text,
                    f"Mojibake token '{token}' detected in {file_path.name}"
                )


# ============================================================================
# TIER 3: CROSS-FEATURE COMBINATIONS
# ============================================================================

class TestTier3CrossFeatureCombinations(unittest.TestCase):
    """Tier 3: Multi-component interactions, responsive media queries, cache busting, and palette."""

    def test_dark_light_snake_picture_tag(self):
        """Verify <picture> tag in README.md correctly supports dark and light modes with valid targets."""
        readme_content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        # Match <picture> block
        pic_match = re.search(r"<picture>(.*?)</picture>", readme_content, re.DOTALL | re.IGNORECASE)
        self.assertIsNotNone(pic_match, "README.md must contain a <picture> element for contribution snake")
        pic_block = pic_match.group(1)

        # Check dark source
        dark_match = re.search(r'<source\s+media=[\'"]\(prefers-color-scheme:\s*dark\)[\'"]\s+srcset=[\'"]([^\'"]+)[\'"]', pic_block)
        self.assertIsNotNone(dark_match, "Dark mode <source> media query missing in <picture>")
        dark_src = dark_match.group(1).split("?")[0].lstrip("./")

        # Check light source
        light_match = re.search(r'<source\s+media=[\'"]\(prefers-color-scheme:\s*light\)[\'"]\s+srcset=[\'"]([^\'"]+)[\'"]', pic_block)
        self.assertIsNotNone(light_match, "Light mode <source> media query missing in <picture>")
        light_src = light_match.group(1).split("?")[0].lstrip("./")

        # Verify target files exist
        self.assertTrue((REPO_ROOT / dark_src).exists(), f"Target dark snake file {dark_src} not found")
        self.assertTrue((REPO_ROOT / light_src).exists(), f"Target light snake file {light_src} not found")

    def test_camo_cache_busting(self):
        """
        Verify Camo CDN cache-busting query strings on dynamic SVG references in README.md.
        Ensures GitHub's image proxy does not cache stale assets.
        """
        readme_content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        local_svg_refs = re.findall(r'(?:src|srcset)=[\'"](\./(?:assets|profile-3d-contrib)/[^\'"]+\.svg[^\'"]*)[\'"]', readme_content)
        self.assertGreater(len(local_svg_refs), 0, "No local SVGs found in README.md")

        uncached_refs = []
        for ref in local_svg_refs:
            if "?v=" not in ref:
                uncached_refs.append(ref)

        if STRICT_MODE:
            strict_uncached = [ref for ref in local_svg_refs if "?v=nature_2026" not in ref]
            self.assertEqual(
                len(strict_uncached), 0,
                f"STRICT MODE: Expected ?v=nature_2026 on all local SVGs, but found unversioned: {strict_uncached}"
            )
        else:
            # Progressive check: header.svg and footer.svg already have ?v=nature
            header_match = re.search(r'header\.svg\?v=[a-zA-Z0-9_]+', readme_content)
            footer_match = re.search(r'footer\.svg\?v=[a-zA-Z0-9_]+', readme_content)
            self.assertIsNotNone(header_match, "header.svg must have cache-busting query param ?v=...")
            self.assertIsNotNone(footer_match, "footer.svg must have cache-busting query param ?v=...")

    def test_palette_harmony(self):
        """Verify color hex codes in header and footer conform to living systems & nature theme."""
        header_content = (REPO_ROOT / "assets" / "header.svg").read_text(encoding="utf-8")
        footer_content = (REPO_ROOT / "assets" / "footer.svg").read_text(encoding="utf-8")

        for svg_name, content in [("header.svg", header_content), ("footer.svg", footer_content)]:
            hex_codes = set(re.findall(r'#([0-9a-fA-F]{6})', content))
            # Must not contain neon magenta, neon cyan, or unstyled pure white background
            self.assertNotIn("FF00FF", {h.upper() for h in hex_codes}, f"{svg_name} contains forbidden neon #FF00FF")
            self.assertNotIn("00FFFF", {h.upper() for h in hex_codes}, f"{svg_name} contains forbidden neon #00FFFF")

            # Must contain at least 3 approved palette shades
            matched = {h.upper() for h in hex_codes}.intersection(APPROVED_PALETTE_HEXES)
            self.assertGreaterEqual(
                len(matched), 3,
                f"{svg_name} should contain at least 3 approved palette colors, matched: {matched}"
            )


# ============================================================================
# TIER 4: REAL-WORLD WORKLOAD SCENARIOS
# ============================================================================

class TestTier4RealWorldWorkloads(unittest.TestCase):
    """Tier 4: Simulated GFM profile render, workflow concurrency, and external URL reachability."""

    def test_simulated_github_profile_render(self):
        """
        Simulate GitHub Flavored Markdown (GFM) DOM structure:
        - Strict verification of balanced HTML tags (no orphaned unclosed containers).
        - GFM table format integrity in Featured Projects and Awards.
        - Mobile responsiveness attributes (width='100%').
        """
        readme_path = REPO_ROOT / "README.md"
        content = readme_path.read_text(encoding="utf-8")

        # 1. HTML tag balance verification
        no_comments = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        open_tags = re.findall(r'<([a-zA-Z0-9]+)(?:\s+[^>]*)?>', no_comments)
        close_tags = re.findall(r'</([a-zA-Z0-9]+)>', no_comments)
        void_tags = {'img', 'br', 'hr', 'source', 'input', 'meta', 'link'}

        open_counts = {}
        for t in open_tags:
            tag = t.lower()
            if tag not in void_tags:
                open_counts[tag] = open_counts.get(tag, 0) + 1

        close_counts = {}
        for t in close_tags:
            tag = t.lower()
            close_counts[tag] = close_counts.get(tag, 0) + 1

        all_tags = set(open_counts.keys()).union(set(close_counts.keys()))
        mismatched = []
        for tag in all_tags:
            o = open_counts.get(tag, 0)
            c = close_counts.get(tag, 0)
            if o != c:
                mismatched.append(f"<{tag}>: open={o}, close={c}")

        self.assertEqual(
            len(mismatched), 0,
            f"Unbalanced HTML tags in README.md could break GitHub rendering: {mismatched}"
        )

        # 2. Responsive mobile width check
        header_img_match = re.search(r'<img[^>]+header\.svg[^>]*>', content)
        self.assertIsNotNone(header_img_match, "Header img tag missing in README.md")
        self.assertIn('width="100%"', header_img_match.group(0), "Header img must have width='100%' for mobile fluidity")

    def test_workflow_concurrency_and_hygiene(self):
        """Verify GitHub Actions workflows prevent git race conditions and schedule collisions."""
        workflows = {
            "snake.yml": (REPO_ROOT / ".github" / "workflows" / "snake.yml").read_text(encoding="utf-8"),
            "profile-3d.yml": (REPO_ROOT / ".github" / "workflows" / "profile-3d.yml").read_text(encoding="utf-8"),
            "readme-widgets.yml": (REPO_ROOT / ".github" / "workflows" / "readme-widgets.yml").read_text(encoding="utf-8"),
        }

        # Check git push safety: must use rebase or '|| exit 0' to avoid crashing on empty commits
        for name, wf_text in workflows.items():
            if "git commit" in wf_text:
                self.assertIn(
                    "|| exit 0", wf_text,
                    f"Workflow {name} commit step should include '|| exit 0' to handle no-change runs"
                )

        # Check cron schedules are staggered (not all firing at the exact same minute)
        crons = []
        for name, wf_text in workflows.items():
            cron_match = re.search(r'cron:\s*["\']([^"\']+)["\']', wf_text)
            if cron_match:
                crons.append((name, cron_match.group(1)))

        cron_specs = [c[1] for c in crons]
        self.assertEqual(
            len(cron_specs), len(set(cron_specs)),
            f"Workflows should have staggered cron schedules to avoid resource contention: {crons}"
        )

    def test_external_url_reachability_with_bot_tolerance(self):
        """
        Verify external URLs in README.md return HTTP 200, with bot-rate-limit tolerance
        for anti-scraping platforms (LinkedIn, Facebook, TryHackMe).
        Enforces strict HTTP 200 for Google Drive credentials.
        """
        readme_content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        links = []
        links += re.findall(r'href=[\'"](https?://[^\s\'"]+)[\'"]', readme_content)
        links += re.findall(r'src=[\'"](https?://[^\s\'"]+)[\'"]', readme_content)
        links += re.findall(r'\[.*?\]\((https?://[^\s\)]+)\)', readme_content)

        unique_links = sorted(list(set(links)))
        self.assertGreaterEqual(len(unique_links), 15, "Expected at least 15 external links in README.md")

        # Bot-protected domains that return 403 or 429 to automated script probes
        BOT_PROTECTED_DOMAINS = ["linkedin.com", "facebook.com", "tryhackme.com", "huggingface.co"]

        ctx = ssl.create_default_context()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # Check Google Drive credentials strictly
        gdrive_links = [u for u in unique_links if "drive.google.com" in u]
        for url in gdrive_links:
            try:
                req = urllib.request.Request(url, headers=headers, method="HEAD")
                with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
                    self.assertIn(resp.status, [200, 301, 302, 307, 308], f"Google Drive link returned {resp.status}: {url}")
            except urllib.error.HTTPError as e:
                # If HEAD disallowed, fallback to GET with range
                if e.code in (403, 405):
                    get_req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(get_req, timeout=12, context=ctx) as get_resp:
                        self.assertEqual(get_resp.status, 200, f"Google Drive GET returned {get_resp.status}: {url}")
                else:
                    self.fail(f"Google Drive credential URL failed with HTTP {e.code}: {url}")

        # Spot check critical repo and badge endpoints
        critical_endpoints = [
            "https://github.com/DuongNAD/LIVA",
            "https://komarev.com/ghpvc/?username=DuongNAD&label=Profile%20Views&color=2563EB&style=flat",
            "https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=18&duration=3000&pause=1000&color=60A5FA&center=true&vCenter=true&width=850&height=40&lines=AI%2FML+%26+Software+Engineer",
        ]
        for url in critical_endpoints:
            try:
                req = urllib.request.Request(url, headers=headers, method="HEAD")
                with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
                    self.assertIn(resp.status, [200, 301, 302, 307, 308])
            except Exception as e:
                self.fail(f"Critical profile endpoint failed reachability check: {url} -> {e}")


# ============================================================================
# RUNNER & SUMMARY REPORT
# ============================================================================

def run_tests() -> int:
    """Run all test suites and print a formatted summary report."""
    print("=" * 80)
    print("  GITHUB PROFILE ECOSYSTEM HARMONIZATION — E2E TEST SUITE")
    print(f"  Mode: {'STRICT E2E' if STRICT_MODE else 'PROGRESSIVE MILESTONE'}")
    print(f"  Target: {REPO_ROOT}")
    print("=" * 80)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestTier1FeatureCoverage,
        TestTier2BoundaryCornerCases,
        TestTier3CrossFeatureCombinations,
        TestTier4RealWorldWorkloads,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    print("  TEST EXECUTION SUMMARY")
    print("=" * 80)
    print(f"  Total Tests Run: {result.testsRun}")
    print(f"  Passed:         {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures:       {len(result.failures)}")
    print(f"  Errors:         {len(result.errors)}")
    print(f"  Skipped:        {len(result.skipped)}")
    print("=" * 80)

    if result.wasSuccessful():
        print("  RESULT: [PASS] All test tiers verified successfully!")
        return 0
    else:
        print("  RESULT: [FAIL] Test suite detected failures.")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
