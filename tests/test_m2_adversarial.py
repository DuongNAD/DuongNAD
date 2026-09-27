#!/usr/bin/env python3
"""
Adversarial Stress Test Suite for Milestone 2: README.md Parity & Harmonization
Ecosystem: DuongNAD/DuongNAD (Living Systems / Nordic Twilight Nature Aesthetic)

Author: teamwork_preview_challenger_m2_1 (Empirical Challenger)
Target: README.md

Adversarial Dimensions:
1. Regex Boundary & Case-Sensitivity Stress Test (7 Projects & 3 Credentials)
2. Camo Cache-Busting Parser (Local SVG versioning completeness & URL validation)
3. Strict Stack-Based Tag Balance & DOM Nesting Validator (GFM-safe nesting & zero indent traps)
4. Empirical URL Reachability Probe (Google Drive credentials, GitHub repositories, and dynamic services)
5. Color Palette & Aesthetic Conformance (Zero legacy hexes, emerald/teal token verification)
"""

import html.parser
import os
import re
import ssl
import sys
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"

# Approved Living Systems Emerald/Teal Palette Hexes
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

FORBIDDEN_LEGACY_HEXES = [
    "2563EB",  # Legacy Royal Blue
    "1D4ED8",  # Legacy Dark Blue
    "60A5FA",  # Legacy Light Sky Blue
    "00EA64",  # Legacy Neon Green
    "00FFFF",  # Neon Cyan
    "FF00FF",  # Neon Magenta
]


# ============================================================================
# 1. REGEX BOUNDARY & CASE-SENSITIVITY STRESS TEST
# ============================================================================

class TestRegexBoundaryAndParity(unittest.TestCase):
    """
    Stress-tests regex boundaries, casing, and section isolation for all
    7 core projects and 3 verified credentials.
    """

    def setUp(self):
        self.assertTrue(README_PATH.exists(), f"README.md missing at {README_PATH}")
        self.content = README_PATH.read_text(encoding="utf-8")

        # Extract "Featured Projects" section exclusively
        match = re.search(
            r'## Featured Projects\s*\n(.*?)(?=\n## |\n<!-- ═+ AWARDS|\Z)',
            self.content,
            re.DOTALL
        )
        self.assertIsNotNone(match, "Could not isolate ## Featured Projects section in README.md")
        self.featured_projects_section = match.group(1)

        # Extract "Awards & Leadership" section exclusively
        match_awards = re.search(
            r'## Awards & Leadership\s*\n(.*?)(?=\n## |\n<!-- ═+ TECH|\Z)',
            self.content,
            re.DOTALL
        )
        self.assertIsNotNone(match_awards, "Could not isolate ## Awards & Leadership section in README.md")
        self.awards_section = match_awards.group(1)

    def test_canonical_casing_and_strict_word_boundaries_projects(self):
        """
        Verify each of the 7 core projects exists with its canonical casing
        and strict word boundaries, preventing partial-match false positives.
        """
        strict_project_specs = [
            ("LIVA", r'(?<![A-Za-z0-9_-])LIVA(?![A-Za-z0-9_-])', "https://github.com/DuongNAD/LIVA"),
            ("Anima Engine", r'(?<![A-Za-z0-9_-])Anima Engine(?![A-Za-z0-9_-])', "https://github.com/DuongNAD/Anima-Engine"),
            ("mcp-agy", r'(?<![A-Za-z0-9_])mcp-agy(?![A-Za-z0-9_])', "https://github.com/DuongNAD/mcp-agy"),
            ("Darwin Lab", r'(?<![A-Za-z0-9_-])Darwin Lab(?![A-Za-z0-9_-])', "https://github.com/DuongNAD/Darwin-core"),
            ("MindSync", r'(?<![A-Za-z0-9_-])MindSync(?![A-Za-z0-9_-])', "https://github.com/DuongNAD/VN_AI_Innovation"),
            ("Buy or Wait?", r'Buy or Wait\?', None),
            ("Vision-Guided Robotic Arm", r'Vision-Guided Robotic Arm', None),
        ]

        # Adversarial distractors that must NOT trigger false positives
        distractors = [
            "OLIVA", "DELIVER", "LIVABLE", "liva_test",
            "Animal Engine", "AnimaEngineers",
            "mcp-agyd", "xmcp-agy",
            "Darwinism", "Darwin Laboratory Extended",
            "MasterMindSync", "MindSynchronize",
            "Don't Buy or Wait Now",
        ]

        for distractor in distractors:
            for proj_name, strict_pattern, _ in strict_project_specs:
                if strict_pattern:
                    match = re.search(strict_pattern, distractor)
                    self.assertIsNone(
                        match,
                        f"Adversarial flaw: Pattern for '{proj_name}' falsely matched distractor '{distractor}'"
                    )

        # Now test against actual Featured Projects section
        for proj_name, strict_pattern, repo_url in strict_project_specs:
            match = re.search(strict_pattern, self.featured_projects_section)
            self.assertIsNotNone(
                match,
                f"Core project '{proj_name}' failed strict boundary/case-sensitive match in Featured Projects section"
            )

            # If repo URL is associated, verify its exact presence in Featured Projects
            if repo_url:
                self.assertIn(
                    repo_url,
                    self.featured_projects_section,
                    f"Repository URL '{repo_url}' for '{proj_name}' missing from Featured Projects"
                )

    def test_featured_projects_grid_cell_count(self):
        """Verify the Featured Projects table contains exactly 8 balanced <td> cells (4 rows x 2 cols)."""
        td_count = len(re.findall(r'<td\b', self.featured_projects_section, re.IGNORECASE))
        tr_count = len(re.findall(r'<tr\b', self.featured_projects_section, re.IGNORECASE))
        self.assertEqual(tr_count, 4, f"Expected 4 <tr> rows in Featured Projects table, got {tr_count}")
        self.assertEqual(td_count, 8, f"Expected 8 <td> cells in Featured Projects table, got {td_count}")

    def test_verified_credentials_exact_ids_and_claims(self):
        """
        Verify all 3 verified credentials have exact Google Drive document IDs
        and matching verified text claims in README.md.
        """
        credentials_spec = [
            {
                "name": "HackerRank Orchestrate",
                "doc_id": "1Hl0qvEHIbgp6Fus2o0EukKZImMNrEr-I",
                "url": "https://drive.google.com/file/d/1Hl0qvEHIbgp6Fus2o0EukKZImMNrEr-I/view",
                "required_claim": r"(?:Top 16%|Rank #493|3,062)",
            },
            {
                "name": "MindSync VAIC Bootcamp",
                "doc_id": "1x8zT32FnxJ5GZxvohfV4F_Ey9QUNAUzZ",
                "url": "https://drive.google.com/file/d/1x8zT32FnxJ5GZxvohfV4F_Ey9QUNAUzZ/view",
                "required_claim": r"(?:Team Lead|MindSync|VAIC 2026)",
            },
            {
                "name": "DENSO Factory Hacks",
                "doc_id": "1K1Sfw4AnxBfi7deHBIaIqpH9cJ-G3ti9",
                "url": "https://drive.google.com/file/d/1K1Sfw4AnxBfi7deHBIaIqpH9cJ-G3ti9/view",
                "required_claim": r"(?:Top 4|Promising Award|DENSO)",
            },
        ]

        for cred in credentials_spec:
            # 1. Exact ID presence
            self.assertIn(
                cred["doc_id"],
                self.content,
                f"Document ID '{cred['doc_id']}' for '{cred['name']}' not found in README.md"
            )

            # 2. Complete URL presence
            self.assertIn(
                cred["url"],
                self.content,
                f"Full URL '{cred['url']}' for '{cred['name']}' not found in README.md"
            )

            # 3. Required claim context
            match = re.search(cred["required_claim"], self.content)
            self.assertIsNotNone(
                match,
                f"Verified claim '{cred['required_claim']}' for '{cred['name']}' not substantiated in README.md"
            )


# ============================================================================
# 2. CAMO CACHE-BUSTING PARSER STRESS TEST
# ============================================================================

class TestCamoCacheBustingAdversarial(unittest.TestCase):
    """
    Exhaustive search across all HTML and Markdown image syntax to assert
    that 0 unversioned local SVGs remain in README.md.
    """

    def setUp(self):
        self.content = README_PATH.read_text(encoding="utf-8")

    def test_zero_unversioned_local_svgs_across_all_syntaxes(self):
        """
        Extract every image reference (src, srcset, markdown image, link href)
        pointing to a local SVG and verify it strictly uses '?v=nature_2026'.
        """
        # Find all SVG references in the document
        raw_svg_matches = re.findall(
            r'''(?:src|srcset|href|data)\s*=\s*['"]([^'"]*\.svg[^'"]*)['"]|!\[.*?\]\(([^)]*\.svg[^)]*)\)''',
            self.content,
            re.IGNORECASE
        )

        all_svg_urls = []
        for m in raw_svg_matches:
            url = m[0] if m[0] else m[1]
            all_svg_urls.append(url.strip())

        # Filter strictly for local SVG references (assets/ or profile-3d-contrib/)
        local_svg_refs = []
        for url in all_svg_urls:
            # Check if it starts with relative or local directory
            clean_url = url.split("?")[0].lstrip("./")
            if clean_url.startswith("assets/") or clean_url.startswith("profile-3d-contrib/"):
                local_svg_refs.append(url)

        self.assertGreaterEqual(
            len(local_svg_refs), 10,
            f"Expected at least 10 local SVG references in README.md, found {len(local_svg_refs)}: {local_svg_refs}"
        )

        unversioned = []
        legacy_versioned = []
        missing_files = []

        for ref in local_svg_refs:
            parsed = urllib.parse.urlparse(ref)
            query_params = urllib.parse.parse_qs(parsed.query)

            # Check version param
            if "v" not in query_params:
                unversioned.append(ref)
            elif query_params["v"] != ["nature_2026"]:
                legacy_versioned.append((ref, query_params["v"]))

            # Verify the actual file exists on disk
            local_file_rel = parsed.path.lstrip("./")
            target_path = REPO_ROOT / local_file_rel
            if not target_path.exists():
                missing_files.append((ref, str(target_path)))

        self.assertEqual(
            len(unversioned), 0,
            f"Adversarial failure: Found unversioned local SVGs: {unversioned}"
        )
        self.assertEqual(
            len(legacy_versioned), 0,
            f"Adversarial failure: Found SVGs with obsolete/incorrect cache query: {legacy_versioned}"
        )
        self.assertEqual(
            len(missing_files), 0,
            f"Adversarial failure: Local SVG target file does not exist on disk: {missing_files}"
        )

    def test_remote_badges_do_not_have_corrupted_query_strings(self):
        """Ensure external badge services (komarev, shields.io, demolab) do not have invalid query injections."""
        external_svgs = re.findall(
            r'''(?:src|href)\s*=\s*['"](https?://[^'"]+)['"]''',
            self.content,
            re.IGNORECASE
        )
        for url in external_svgs:
            parsed = urllib.parse.urlparse(url)
            # komarev, shields, demolab should have valid query strings
            if "komarev.com" in parsed.netloc:
                qs = urllib.parse.parse_qs(parsed.query)
                self.assertIn("username", qs)
                self.assertIn("color", qs)
            elif "readme-typing-svg.demolab.com" in parsed.netloc:
                qs = urllib.parse.parse_qs(parsed.query)
                self.assertIn("lines", qs)
                self.assertIn("color", qs)


# ============================================================================
# 3. TAG BALANCE & DOM NESTING VALIDATOR
# ============================================================================

class _DOMBalanceValidator(html.parser.HTMLParser):
    """Custom SAX-style HTML parser to validate container tag balance and nesting."""

    VOID_ELEMENTS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"
    }

    def __init__(self):
        super().__init__()
        self.tag_stack: List[Tuple[str, int]] = []  # (tag_name, line_num)
        self.errors: List[str] = []
        self.open_counts: Dict[str, int] = {}
        self.close_counts: Dict[str, int] = {}

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        tag_lower = tag.lower()
        if tag_lower in self.VOID_ELEMENTS:
            return

        self.open_counts[tag_lower] = self.open_counts.get(tag_lower, 0) + 1
        self.tag_stack.append((tag_lower, self.getpos()[0]))

    def handle_startendtag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        tag_lower = tag.lower()
        if tag_lower in self.VOID_ELEMENTS:
            # Standard self-closing void tag (e.g., <img ... />, <br />)
            return

        # Non-void tag self-closed (e.g., <div />)
        self.open_counts[tag_lower] = self.open_counts.get(tag_lower, 0) + 1
        self.close_counts[tag_lower] = self.close_counts.get(tag_lower, 0) + 1

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if tag_lower in self.VOID_ELEMENTS:
            self.errors.append(f"Line {self.getpos()[0]}: Spurious closing tag for void element </{tag_lower}>")
            return

        self.close_counts[tag_lower] = self.close_counts.get(tag_lower, 0) + 1

        if not self.tag_stack:
            self.errors.append(f"Line {self.getpos()[0]}: Unexpected closing tag </{tag_lower}> with empty stack")
            return

        top_tag, top_line = self.tag_stack.pop()
        if top_tag != tag_lower:
            self.errors.append(
                f"Line {self.getpos()[0]}: Mismatched closing tag </{tag_lower}>. Expected </{top_tag}> (opened on line {top_line})"
            )


class TestTagBalanceAndGFMNesting(unittest.TestCase):
    """
    Stress-tests HTML tag balancing, proper hierarchical nesting,
    and GFM indentation behavior.
    """

    def setUp(self):
        self.content = README_PATH.read_text(encoding="utf-8")

    def test_strict_dom_nesting_and_balance(self):
        """Verify strict hierarchical nesting using a SAX-style parser."""
        # Strip comments
        no_comments = re.sub(r'<!--.*?-->', '', self.content, flags=re.DOTALL)

        parser = _DOMBalanceValidator()
        parser.feed(no_comments)

        # Check if stack is empty
        if parser.tag_stack:
            unclosed_details = [f"<{t}> (line {l})" for t, l in parser.tag_stack]
            parser.errors.append(f"Unclosed tags remaining on stack at EOF: {', '.join(unclosed_details)}")

        self.assertEqual(
            len(parser.errors), 0,
            f"Tag balance / DOM nesting errors detected in README.md:\n" + "\n".join(parser.errors)
        )

    def test_gfm_indentation_traps(self):
        """
        Verify that no HTML table tags (<table>, <tr>, <td>) are indented by 4 or more spaces
        after a blank line, which causes GFM to treat them as raw code blocks.
        """
        lines = self.content.split("\n")
        in_code_block = False
        prev_blank = False

        table_tags = ("<table", "<tr", "<td", "<th", "</table", "</tr", "</td")

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                prev_blank = False
                continue

            if in_code_block:
                continue

            if not stripped:
                prev_blank = True
                continue

            if prev_blank:
                # Check if this non-blank line starts with 4+ spaces and contains a table tag
                if line.startswith("    ") or line.startswith("\t"):
                    line_lstrip = line.lstrip().lower()
                    if any(line_lstrip.startswith(tt) for tt in table_tags):
                        self.fail(
                            f"GFM Indentation Trap at line {idx}: Table tag '{stripped}' has 4+ spaces indent after blank line. "
                            f"GitHub Flavored Markdown will render this as an unformatted code block!"
                        )

            prev_blank = False

    def test_table_cell_inline_formatting_balance(self):
        """Verify that every inline tag (<a>, <strong>, <code>, <i>) inside table cells is strictly balanced."""
        td_blocks = re.findall(r'<td\b[^>]*>(.*?)</td>', self.content, re.DOTALL | re.IGNORECASE)
        self.assertGreaterEqual(len(td_blocks), 8, "Expected at least 8 table cells")

        inline_tags = ["a", "strong", "code", "i", "b", "em", "span"]
        for idx, cell in enumerate(td_blocks, start=1):
            for tag in inline_tags:
                open_cnt = len(re.findall(rf'<{tag}\b[^>]*>', cell, re.IGNORECASE))
                close_cnt = len(re.findall(rf'</{tag}>', cell, re.IGNORECASE))
                self.assertEqual(
                    open_cnt, close_cnt,
                    f"Cell {idx} has unbalanced <{tag}> tags: opened {open_cnt}, closed {close_cnt}"
                )

    def test_picture_tag_dark_light_schema(self):
        """Verify the <picture> container has both dark and light modes configured with fallback."""
        pic_match = re.search(r'<picture>(.*?)</picture>', self.content, re.DOTALL)
        self.assertIsNotNone(pic_match, "Missing <picture> container in README.md")
        inner = pic_match.group(1)

        # Dark source
        dark_source = re.search(
            r'<source\s+media=[\'"]\(prefers-color-scheme:\s*dark\)[\'"]\s+srcset=[\'"]([^\'"]+)[\'"]',
            inner
        )
        self.assertIsNotNone(dark_source, "Missing dark mode <source> in <picture>")
        self.assertIn("github-contribution-grid-snake-dark.svg?v=nature_2026", dark_source.group(1))

        # Light source
        light_source = re.search(
            r'<source\s+media=[\'"]\(prefers-color-scheme:\s*light\)[\'"]\s+srcset=[\'"]([^\'"]+)[\'"]',
            inner
        )
        self.assertIsNotNone(light_source, "Missing light mode <source> in <picture>")
        self.assertIn("github-contribution-grid-snake.svg?v=nature_2026", light_source.group(1))

        # Fallback img
        fallback_img = re.search(r'<img\s+src=[\'"]([^\'"]+)[\'"][^>]*alt=[\'"]([^\'"]+)[\'"]', inner)
        self.assertIsNotNone(fallback_img, "Missing fallback <img> in <picture>")
        self.assertIn("github-contribution-grid-snake-dark.svg?v=nature_2026", fallback_img.group(1))


# ============================================================================
# 4. EMPIRICAL URL REACHABILITY PROBE
# ============================================================================

class TestUrlReachabilityEmpirical(unittest.TestCase):
    """
    Actively probes external URLs: Google Drive certificates and GitHub repository links.
    Asserts HTTP 200 (or permissible auth/view redirection to 200).
    """

    def setUp(self):
        self.content = README_PATH.read_text(encoding="utf-8")
        self.ssl_ctx = ssl.create_default_context()
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

    def _probe_url(self, url: str, expected_codes=(200, 301, 302, 307, 308)) -> int:
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=15, context=self.ssl_ctx) as resp:
                return resp.status
        except urllib.error.HTTPError as e:
            return e.code
        except Exception as e:
            raise RuntimeError(f"Network error probing {url}: {e}")

    def test_google_drive_credentials_reachability(self):
        """Verify all Google Drive links in README.md are publicly accessible (HTTP 200)."""
        gdrive_links = re.findall(
            r'href=[\'"](https://drive\.google\.com/[^\s\'"]+)[\'"]',
            self.content
        )
        self.assertGreaterEqual(
            len(gdrive_links), 3,
            f"Expected at least 3 Google Drive credential links, found: {gdrive_links}"
        )

        for url in set(gdrive_links):
            status = self._probe_url(url)
            self.assertIn(
                status, [200, 301, 302, 307, 308],
                f"Google Drive credential URL {url} failed with status {status}"
            )

    def test_github_repo_links_reachability(self):
        """Verify all referenced DuongNAD GitHub repository links return HTTP 200."""
        repos = [
            "https://github.com/DuongNAD/LIVA",
            "https://github.com/DuongNAD/Anima-Engine",
            "https://github.com/DuongNAD/mcp-agy",
            "https://github.com/DuongNAD/Darwin-core",
            "https://github.com/DuongNAD/VN_AI_Innovation",
            "https://github.com/DuongNAD/smart-drive-os",
            "https://github.com/DuongNAD",
        ]

        for repo_url in repos:
            # Check presence in README
            self.assertIn(repo_url, self.content, f"Repo URL {repo_url} not referenced in README.md")
            # Probe reachability
            status = self._probe_url(repo_url)
            self.assertIn(
                status, [200, 301, 302],
                f"GitHub repo URL {repo_url} failed reachability check with status {status}"
            )


# ============================================================================
# 5. COLOR PALETTE & AESTHETIC CONFORMANCE
# ============================================================================

class TestAestheticAndPaletteConformance(unittest.TestCase):
    """
    Stress-tests color codes across README.md to ensure complete eradication
    of legacy blue/neon hexes and strict adherence to emerald/teal/slate.
    """

    def setUp(self):
        self.content = README_PATH.read_text(encoding="utf-8")

    def test_zero_forbidden_legacy_hexes_in_readme(self):
        """Assert zero occurrences of legacy blue and neon hexes in README.md."""
        found_forbidden = {}
        for forbidden in FORBIDDEN_LEGACY_HEXES:
            # Check case-insensitively
            matches = re.findall(rf'\b{forbidden}\b', self.content, re.IGNORECASE)
            if matches:
                found_forbidden[forbidden] = len(matches)

        self.assertEqual(
            len(found_forbidden), 0,
            f"Adversarial failure: Legacy forbidden hexes found in README.md: {found_forbidden}"
        )

    def test_approved_palette_tokens_in_badges_and_typing(self):
        """Verify key profile badges utilize approved emerald and teal palette codes."""
        # Profile Views counter badge
        self.assertRegex(
            self.content,
            r'ghpvc/\?username=DuongNAD&label=Profile%20Views&color=059669',
            "Profile Views badge color should be 059669 (Emerald 600)"
        )

        # HackerRank badge
        self.assertRegex(
            self.content,
            r'badge/HackerRank%20Orchestrate-[^"\']+-10B981',
            "HackerRank badge color should be 10B981 (Emerald 500)"
        )

        # MindSync badge
        self.assertRegex(
            self.content,
            r'badge/Team%20Lead-[^"\']+-0D9488',
            "MindSync badge color should be 0D9488 (Deep Teal 600)"
        )

        # DENSO badge
        self.assertRegex(
            self.content,
            r'badge/DENSO%20Factory%20Hacks-[^"\']+-134236',
            "DENSO badge color should be 134236 (Dark Pine / Forest)"
        )

        # Typing SVG color
        self.assertRegex(
            self.content,
            r'readme-typing-svg\.demolab\.com\?[^"\']*color=10B981',
            "Typing SVG color should be 10B981 (Emerald 500)"
        )


# ============================================================================
# MAIN ENTRYPOINT
# ============================================================================

def main():
    print("=" * 80)
    print("  MILESTONE 2: ADVERSARIAL STRESS TEST SUITE (CHALLENGER)")
    print(f"  Target: {README_PATH}")
    print("=" * 80)
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
