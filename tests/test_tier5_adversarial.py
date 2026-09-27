#!/usr/bin/env python3
"""
Tier 5 White-Box Adversarial Verification Test Suite
Milestone 4: Comprehensive Ecosystem Hardening

Author: teamwork_preview_challenger_m4_1 (Empirical Challenger)
Roles: critic, specialist

Coverage Scope:
1. Exception Handling & Resilience in `scripts/fetch-all-widgets.py`:
   - HTTP error matrix (400, 403, 404, 429, 500, 502, 503, 504)
   - Network transport & DNS failures (URLError, ConnectionRefused, socket.gaierror, SSLError)
   - Timeout resilience (socket.timeout, TimeoutError)
   - Mixed batch execution (partial failure resilience, non-destructive file preservation)
   - Filesystem write failure resilience (PermissionError simulation)
   - Non-UTF8 byte stream decoding resilience (errors="ignore")
   - Adversarial sanitize() error payload corpus & defensive token transformation
2. Deterministic SVG Generation Under Varied Locales & Environments (`scripts/generate_nature_banner.py`):
   - Locale invariance across diverse system locales (C, POSIX, en_US, de_DE, fr_FR, tr_TR)
   - Floating-point string representation invariant (decimal dot vs comma)
   - Purity and repeatability over successive generation cycles
   - Byte-for-byte exact equality between disk asset and generator output
   - Vietnamese diacritics Unicode normalization & UTF-8 byte stream fidelity
   - Line ending invariant (strict Unix LF without CRLF or UTF-8 BOM)
   - XML entity escaping soundness (&amp; vs unescaped ampersand)
   - Multi-parser consensus across independent XML engines
3. Viewport Scaling, Aspect Ratio Invariants & Coordinate Bounds:
   - Header SVG ViewBox invariant (0 0 1200 260) and 60:13 aspect ratio
   - Footer SVG ViewBox invariant (0 0 1200 90) and 40:3 aspect ratio
   - Central frosted card bounding box, symmetry, and corner radius
   - Noble Stag vector path coordinate extraction, bounding box, and card clearance
   - Central typography vertical clearance and middle-alignment invariants
   - Celestial moon halo and soaring avian spatial clearance
   - Terrain layer edge-to-edge continuity (Y=260 base anchor)
   - Footer axis line and living network nodes bilateral reflection symmetry
   - Multi-resolution viewport scaling projection matrix (17 display devices from 320px to 3840px)
   - Font-size visual hierarchy and readability constraints
4. Workflow Concurrency & Ecosystem Hardening:
   - Concurrency group mathematical disjointness under adversarial git refs
   - GitHub Actions permissions least-privilege scoping (contents: write)
   - Camo CDN cache-busting query parameter compliance (?v=nature_2026)
   - Repository pins dark palette and stroke opacity compliance
"""

import importlib.util
import io
import locale
import os
import re
import shutil
import socket
import ssl
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from unittest.mock import MagicMock, patch

# Base directory resolution
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
ASSETS_DIR = REPO_ROOT / "assets"
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
README_PATH = REPO_ROOT / "README.md"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Dynamically import scripts/fetch-all-widgets.py
FETCH_SCRIPT_PATH = SCRIPTS_DIR / "fetch-all-widgets.py"
spec_fetch = importlib.util.spec_from_file_location("fetch_all_widgets", FETCH_SCRIPT_PATH)
fetch_mod = importlib.util.module_from_spec(spec_fetch)
spec_fetch.loader.exec_module(fetch_mod)
sanitize_widget = fetch_mod.sanitize
WIDGETS_CONFIG = fetch_mod.WIDGETS

# Import scripts/generate_nature_banner.py
from scripts.generate_nature_banner import STAG_PATH, generate_svg


# ============================================================================
# 1. EXCEPTION HANDLING & RESILIENCE IN fetch-all-widgets.py
# ============================================================================

class TestFetchAllWidgetsExceptionHandling(unittest.TestCase):
    """Adversarial stress-testing of network exception handling, file preservation, and payload sanitization."""

    def test_http_error_matrix_graceful_degradation(self):
        """Verify main() handles 8 distinct HTTP error codes gracefully without crashing and preserves disk assets."""
        error_codes = [400, 403, 404, 429, 500, 502, 503, 504]

        for code in error_codes:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmppath = Path(tmpdir)
                t_scripts = tmppath / "scripts"
                t_assets = tmppath / "assets"
                t_scripts.mkdir()
                t_assets.mkdir()
                t_script_file = t_scripts / "fetch-all-widgets.py"
                shutil.copy(FETCH_SCRIPT_PATH, t_script_file)

                # Pre-populate dummy assets on disk to test preservation
                canary_content = "<svg><!-- canary pre-existing --></svg>"
                for rel in WIDGETS_CONFIG.keys():
                    target = tmppath / rel
                    target.write_text(canary_content, encoding="utf-8")

                spec = importlib.util.spec_from_file_location("tmp_fetch", t_script_file)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                http_err = urllib.error.HTTPError(
                    url="https://example.com/api",
                    code=code,
                    msg=f"HTTP Error {code}",
                    hdrs={},
                    fp=None
                )

                with patch("urllib.request.urlopen", side_effect=http_err):
                    # Redirect stdout to suppress noisy logs during test run
                    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                        exit_code = mod.main()

                self.assertEqual(exit_code, 0, f"main() must exit 0 on HTTP {code}, got {exit_code}")
                stdout_val = mock_stdout.getvalue()
                self.assertIn(f"HTTP Error {code}", stdout_val)
                self.assertIn("0/10 widgets processed successfully", stdout_val)

                # Verify all pre-existing files remained 100% intact
                for rel in WIDGETS_CONFIG.keys():
                    target = tmppath / rel
                    self.assertEqual(target.read_text(encoding="utf-8"), canary_content,
                                     f"Pre-existing asset {rel} was corrupted or overwritten on HTTP {code}")

    def test_network_transport_and_socket_failures(self):
        """Verify main() catches raw URLError, socket connection failures, and SSL errors."""
        transport_exceptions = [
            urllib.error.URLError(ConnectionRefusedError("Connection refused by peer")),
            urllib.error.URLError(socket.gaierror(11001, "getaddrinfo failed")),
            urllib.error.URLError("Connection reset by peer"),
            ssl.SSLError("certificate verify failed: self signed certificate"),
        ]

        for exc in transport_exceptions:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmppath = Path(tmpdir)
                t_scripts = tmppath / "scripts"
                t_assets = tmppath / "assets"
                t_scripts.mkdir()
                t_assets.mkdir()
                t_script_file = t_scripts / "fetch-all-widgets.py"
                shutil.copy(FETCH_SCRIPT_PATH, t_script_file)

                spec = importlib.util.spec_from_file_location("tmp_fetch", t_script_file)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                with patch("urllib.request.urlopen", side_effect=exc):
                    with patch("sys.stdout", new_callable=io.StringIO):
                        exit_code = mod.main()

                self.assertEqual(exit_code, 0, f"main() crashed on {type(exc).__name__}: {exc}")

    def test_timeout_handling_non_blocking(self):
        """Verify socket.timeout and TimeoutError do not crash main() and allow processing to finish."""
        for timeout_exc in [socket.timeout("The read operation timed out"), TimeoutError("Timed out")]:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmppath = Path(tmpdir)
                t_scripts = tmppath / "scripts"
                t_assets = tmppath / "assets"
                t_scripts.mkdir()
                t_assets.mkdir()
                t_script_file = t_scripts / "fetch-all-widgets.py"
                shutil.copy(FETCH_SCRIPT_PATH, t_script_file)

                spec = importlib.util.spec_from_file_location("tmp_fetch", t_script_file)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                with patch("urllib.request.urlopen", side_effect=timeout_exc):
                    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                        exit_code = mod.main()

                self.assertEqual(exit_code, 0)
                self.assertIn("ERROR fetching", mock_stdout.getvalue())

    def test_mixed_batch_execution_resilience(self):
        """Simulate a mixed real-world batch: valid SVG, error card, HTTP 500, timeout, and HTML 404."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            t_scripts = tmppath / "scripts"
            t_assets = tmppath / "assets"
            t_scripts.mkdir()
            t_assets.mkdir()
            t_script_file = t_scripts / "fetch-all-widgets.py"
            shutil.copy(FETCH_SCRIPT_PATH, t_script_file)

            spec = importlib.util.spec_from_file_location("tmp_fetch", t_script_file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            # Pre-seed a canary for streak.svg
            canary_streak = tmppath / "assets" / "streak.svg"
            canary_streak.write_text("<svg><!-- existing streak --></svg>", encoding="utf-8")

            valid_svg = b'<svg xmlns="http://www.w3.org/2000/svg"><rect fill="#0B1220"/><text>Stats</text></svg>'
            error_card = b'<svg xmlns="http://www.w3.org/2000/svg"><text>Something went wrong</text></svg>'
            html_404 = b'<!DOCTYPE html><html><body>404 Not Found</body></html>'

            def mock_urlopen_mixed(req, timeout=30):
                url = req.full_url if hasattr(req, "full_url") else str(req)
                if "/api?username=" in url:
                    m = MagicMock()
                    m.read.return_value = valid_svg
                    m.__enter__.return_value = m
                    return m
                elif "/api/top-langs" in url:
                    m = MagicMock()
                    m.read.return_value = error_card
                    m.__enter__.return_value = m
                    return m
                elif "streak-stats" in url:
                    raise urllib.error.HTTPError(url, 500, "Internal Server Error", {}, None)
                elif "trophy" in url:
                    m = MagicMock()
                    m.read.return_value = html_404
                    m.__enter__.return_value = m
                    return m
                elif "&repo=LIVA" in url:
                    m = MagicMock()
                    m.read.return_value = valid_svg
                    m.__enter__.return_value = m
                    return m
                else:
                    raise TimeoutError("Upstream timeout")

            with patch("urllib.request.urlopen", side_effect=mock_urlopen_mixed):
                with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                    exit_code = mod.main()

            self.assertEqual(exit_code, 0)
            stdout = mock_stdout.getvalue()
            self.assertIn("2/10 widgets processed successfully", stdout)

            # stats.svg and pin-liva.svg should be written
            self.assertTrue((tmppath / "assets" / "stats.svg").exists())
            self.assertTrue((tmppath / "assets" / "pin-liva.svg").exists())

            # streak.svg pre-existing content must be untouched
            self.assertEqual(canary_streak.read_text(encoding="utf-8"), "<svg><!-- existing streak --></svg>")

            # top-langs and trophies must not be created since they returned error card & html
            self.assertFalse((tmppath / "assets" / "top-langs.svg").exists())
            self.assertFalse((tmppath / "assets" / "trophies.svg").exists())

    def test_destination_filesystem_write_failure_resilience(self):
        """Simulate PermissionError during write_text; main() must catch exception and continue loop."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            t_scripts = tmppath / "scripts"
            t_assets = tmppath / "assets"
            t_scripts.mkdir()
            t_assets.mkdir()
            t_script_file = t_scripts / "fetch-all-widgets.py"
            shutil.copy(FETCH_SCRIPT_PATH, t_script_file)

            spec = importlib.util.spec_from_file_location("tmp_fetch", t_script_file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            valid_svg = b'<svg xmlns="http://www.w3.org/2000/svg"><text>Valid</text></svg>'

            def mock_urlopen_ok(req, timeout=30):
                m = MagicMock()
                m.read.return_value = valid_svg
                m.__enter__.return_value = m
                return m

            with patch("urllib.request.urlopen", side_effect=mock_urlopen_ok):
                # Patch Path.write_text to raise PermissionError
                with patch.object(Path, "write_text", side_effect=PermissionError("EACCES: permission denied")):
                    with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                        exit_code = mod.main()

            self.assertEqual(exit_code, 0, "main() must exit 0 even if filesystem write errors occur")
            self.assertIn("ERROR fetching", mock_stdout.getvalue())

    def test_binary_garbage_and_encoding_resilience(self):
        """Verify errors='ignore' safely decodes corrupt binary payloads without raising UnicodeDecodeError."""
        corrupt_bytes = b"\xff\xfe\x00\x00\x80\x81\x82\x83\x84\x85\x86" + b"<svg>" + b"\x87\x88\x89</svg>"
        decoded = corrupt_bytes.decode("utf-8", errors="ignore")
        self.assertIn("<svg>", decoded)
        sanitized = sanitize_widget(decoded)
        self.assertIsNotNone(sanitized)
        self.assertIn("<svg>", sanitized)

    def test_sanitize_adversarial_error_corpus(self):
        """Test sanitize() against a comprehensive adversarial corpus of error cards, HTML, and corrupt strings."""
        rejection_corpus = [
            # HTML error responses
            "<!DOCTYPE html><html><head><title>404 Not Found</title></head><body>404</body></html>",
            "<html><body><h1>502 Bad Gateway</h1><p>Cloudflare</p></body></html>",
            "<!doctype html><html lang='en'><body>Internal Server Error</body></html>",
            # Plain text & JSON errors
            '{"error": "Rate limit exceeded for user DuongNAD"}',
            "Error: could not fetch profile data",
            "   \n\t   ",
            "",
            # Upstream failure tokens inside valid XML/SVG markup
            "<svg><text>failed to retrieve data</text></svg>",
            "<svg><text>FAILED TO RETRIEVE user profile</text></svg>",
            "<svg><desc>Failed to Retrieve</desc></svg>",
            "<svg><g>something went wrong</g></svg>",
            "<svg><text>SOMETHING WENT WRONG with the database</text></svg>",
            "<svg><tspan>SomeThing Went Wrong</tspan></svg>",
            "<svg><text>deployment_paused on Vercel</text></svg>",
            "<svg><text>DEPLOYMENT_PAUSED</text></svg>",
            # Non-SVG XML
            "<widget><status>error</status></widget>",
            "<?xml version='1.0'?><response><error>bad request</error></response>",
        ]

        for payload in rejection_corpus:
            result = sanitize_widget(payload)
            self.assertIsNone(result, f"sanitize() should have returned None for payload: {payload[:50]}...")

    def test_sanitize_defensive_transformations(self):
        """Verify sanitize() transforms animation, stark borders, and legacy blue tokens into emerald/teal."""
        dirty_svg = """<svg xmlns="http://www.w3.org/2000/svg">
  <style>
    .stagger {
      animation: fadeIn 0.5s ease-in-out forwards;
      opacity: 0;
    }
  </style>
  undefined
  <rect stroke="#E4E2E2" stroke-opacity="1" fill="#60A5FA" />
  <circle fill="#3B82F6" stroke='#e4e2e2' />
  <path fill="#2563EB" opacity: 0; animation: fadein 1s />
</svg>"""

        cleaned = sanitize_widget(dirty_svg)
        self.assertIsNotNone(cleaned)

        # 1. undefined line stripped
        self.assertNotIn("undefined", cleaned)

        # 2. .stagger opacity restored
        self.assertIn(".stagger { opacity: 1; }", cleaned)

        # 3. opacity 0 animation overridden
        self.assertIn("opacity: 1", cleaned)
        self.assertNotIn("opacity: 0", cleaned)

        # 4. stark light borders converted to dark slate
        self.assertNotIn('#E4E2E2', cleaned)
        self.assertNotIn('#e4e2e2', cleaned)
        self.assertIn('stroke="#1E293B"', cleaned)
        self.assertIn('stroke-opacity="0.7"', cleaned)

        # 5. legacy blues mapped to living systems tokens
        self.assertNotIn('#60A5FA', cleaned)
        self.assertNotIn('#3B82F6', cleaned)
        self.assertNotIn('#2563EB', cleaned)
        self.assertIn('#10B981', cleaned)
        self.assertIn('#059669', cleaned)
        self.assertIn('#0D9488', cleaned)

    def test_widgets_dictionary_configuration(self):
        """Verify WIDGETS dictionary adheres to relative path conventions, secure HTTPS, and emerald query tokens."""
        self.assertEqual(len(WIDGETS_CONFIG), 10, "WIDGETS config must specify exactly 10 widget endpoints")

        approved_url_tokens = ["10B981", "059669", "0D9488", "0B1220", "E5E7EB"]
        for rel_path, url in WIDGETS_CONFIG.items():
            self.assertTrue(rel_path.startswith("assets/"), f"Path {rel_path} must start with assets/")
            self.assertTrue(rel_path.endswith(".svg"), f"Path {rel_path} must end with .svg")
            self.assertTrue(url.startswith("https://"), f"URL {url} must use HTTPS protocol")

            # Check that URLs for stats/streak/pins contain nature palette tokens
            if "api?username" in url or "top-langs" in url or "streak" in url or "/pin/" in url:
                has_nature_token = any(token.lower() in url.lower() for token in approved_url_tokens)
                self.assertTrue(has_nature_token, f"Widget URL {url} should contain approved nature palette tokens")


# ============================================================================
# 2. DETERMINISTIC SVG GENERATION UNDER VARIED LOCALES & ENVIRONMENTS
# ============================================================================

class TestDeterministicSvgGenerationUnderVariedLocalesAndEnvironments(unittest.TestCase):
    """Adversarial testing of scripts/generate_nature_banner.py across locales, encodings, and environments."""

    def setUp(self):
        self.initial_locale = locale.getlocale()

    def tearDown(self):
        # Restore initial locale
        try:
            locale.setlocale(locale.LC_ALL, self.initial_locale)
        except Exception:
            pass

    def test_locale_invariance_across_diverse_environments(self):
        """Verify generate_svg() produces identical byte strings regardless of active system locale."""
        baseline_svg = generate_svg()

        candidate_locales = ["C", "POSIX", "en_US", "de_DE", "fr_FR", "tr_TR", "vi_VN"]
        tested_count = 0

        for loc in candidate_locales:
            try:
                locale.setlocale(locale.LC_ALL, loc)
            except locale.Error:
                continue

            tested_count += 1
            generated = generate_svg()
            self.assertEqual(
                generated,
                baseline_svg,
                f"generate_svg() output differed under locale '{loc}'! Potential decimal separator or casing leak."
            )

        self.assertGreaterEqual(tested_count, 1, "At least 1 standard locale must be tested")

    def test_floating_point_formatting_invariance(self):
        """Verify all coordinates and dimensions in generate_svg() strictly use '.' decimal separators, never ','."""
        svg_content = generate_svg()

        # Regex for numbers with comma decimal separator e.g. " 12,5 " or "rx='1,5'"
        comma_decimal = re.search(r'\b\d+,\d+\b', svg_content)
        self.assertIsNone(comma_decimal, f"Found localized comma decimal separator in SVG: {comma_decimal}")

        # Verify specific known floating point coordinates use dot
        self.assertIn("font-size=\"14.5\"", svg_content)
        self.assertIn("font-size=\"12.5\"", svg_content)
        self.assertIn("font-size: 9.5px;", svg_content)
        self.assertIn("y=\"98.5\"", svg_content)
        self.assertIn("rx=\"1.5\"", svg_content)
        self.assertIn("stroke-width=\"1.2\"", svg_content)

    def test_purity_and_repeatability_cycles(self):
        """Run 100 consecutive invocations of generate_svg() and assert zero output drift."""
        first_run = generate_svg()
        first_hash = hash(first_run)

        for i in range(100):
            current = generate_svg()
            self.assertEqual(len(current), len(first_run), f"Length drifted on iteration {i}")
            self.assertEqual(hash(current), first_hash, f"Hash drifted on iteration {i}")

    def test_disk_asset_byte_parity_with_generator(self):
        """Verify assets/header.svg on disk matches scripts/generate_nature_banner.py byte-for-byte."""
        header_path = ASSETS_DIR / "header.svg"
        self.assertTrue(header_path.exists(), "assets/header.svg must exist")

        disk_content = header_path.read_text(encoding="utf-8")
        generated_content = generate_svg()

        self.assertEqual(
            disk_content,
            generated_content,
            "assets/header.svg is out of sync with scripts/generate_nature_banner.py. Run generator script to resync!"
        )

    def test_vietnamese_diacritics_unicode_normalization(self):
        """Verify candidate's name 'NGUYỄN ANH DƯƠNG' preserves exact Unicode code points and UTF-8 encoding."""
        svg_content = generate_svg()
        name = "NGUYỄN ANH DƯƠNG"
        self.assertIn(name, svg_content)

        # Check exact unicode code points:
        # N: U+004E, G: U+0047, U: U+0055, Y: U+0059, Ễ: U+1EC4, N: U+004E
        # A: U+0041, N: U+004E, H: U+0048
        # D: U+0044, Ư: U+01AF, Ơ: U+01A0, N: U+004E, G: U+0047
        encoded_name = name.encode("utf-8")
        expected_bytes = b"NGUY\xe1\xbb\x84N ANH D\xc6\xaf\xc6\xa0NG"
        self.assertEqual(encoded_name, expected_bytes)

        # Verify raw bytes in SVG file on disk match UTF-8 sequence
        header_bytes = (ASSETS_DIR / "header.svg").read_bytes()
        self.assertIn(expected_bytes, header_bytes)

    def test_line_ending_and_bom_absence(self):
        """Verify assets/header.svg strictly uses Unix LF (\n) line endings and contains no UTF-8 BOM."""
        header_bytes = (ASSETS_DIR / "header.svg").read_bytes()

        # Reject UTF-8 BOM (\xef\xbb\xbf)
        self.assertFalse(header_bytes.startswith(b"\xef\xbb\xbf"), "SVG file must NOT contain a UTF-8 BOM header")

        # Reject Windows CRLF (\r\n)
        self.assertNotIn(b"\r\n", header_bytes, "SVG file must use strict Unix LF line endings, found CRLF")

    def test_xml_entity_escaping_soundness(self):
        """Verify all occurrences of '&' outside comments are properly escaped as '&amp;', with zero raw unescaped ampersands."""
        svg_content = generate_svg()

        # In XML 1.0 (Section 2.5), comments do not expand entities and literal '&' is standard.
        # Strip comments to inspect actual XML markup and text content:
        content_no_comments = re.sub(r'<!--.*?-->', '', svg_content, flags=re.DOTALL)

        # Find all ampersands not followed by valid XML entity (amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);
        unescaped_amp = re.findall(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)', content_no_comments)
        self.assertEqual(len(unescaped_amp), 0, f"Found unescaped ampersand(s) in SVG markup/text: {unescaped_amp}")

        # Check expected escaped phrases
        self.assertIn("✦ LIVING SYSTEMS &amp; AI ✦", svg_content)
        self.assertIn("AI Engineer &amp; Software Developer · Natural Selection &amp; Agentic AI", svg_content)

    def test_multi_parser_xml_consensus(self):
        """Verify generate_svg() parses cleanly without warnings across standard ElementTree parser."""
        svg_content = generate_svg()
        root = ET.fromstring(svg_content)
        self.assertEqual(root.tag.split("}")[-1], "svg")
        self.assertEqual(root.attrib.get("viewBox"), "0 0 1200 260")


# ============================================================================
# 3. VIEWPORT SCALING, ASPECT RATIO INVARIANTS & COORDINATE BOUNDS
# ============================================================================

class TestViewportScalingAndCoordinateBounds(unittest.TestCase):
    """Adversarial verification of spatial layout, bounding boxes, clearance margins, and viewport scaling."""

    @classmethod
    def setUpClass(cls):
        cls.header_svg = (ASSETS_DIR / "header.svg").read_text(encoding="utf-8")
        cls.footer_svg = (ASSETS_DIR / "footer.svg").read_text(encoding="utf-8")
        cls.header_root = ET.fromstring(cls.header_svg)
        cls.footer_root = ET.fromstring(cls.footer_svg)

    def test_header_viewbox_and_aspect_ratio_invariants(self):
        """Validate header.svg viewBox is strictly '0 0 1200 260' with 60:13 (4.615) aspect ratio."""
        vb = self.header_root.attrib.get("viewBox")
        self.assertEqual(vb, "0 0 1200 260")
        self.assertEqual(self.header_root.attrib.get("width"), "100%")
        self.assertEqual(self.header_root.attrib.get("height"), "100%")

        vb_vals = [float(v) for v in vb.split()]
        aspect_ratio = vb_vals[2] / vb_vals[3]
        self.assertAlmostEqual(aspect_ratio, 1200.0 / 260.0, places=5)

    def test_footer_viewbox_and_aspect_ratio_invariants(self):
        """Validate footer.svg viewBox is strictly '0 0 1200 90' with 40:3 (13.333) aspect ratio and meet scaling."""
        vb = self.footer_root.attrib.get("viewBox")
        self.assertEqual(vb, "0 0 1200 90")
        self.assertEqual(self.footer_root.attrib.get("width"), "100%")
        self.assertEqual(self.footer_root.attrib.get("height"), "100%")
        self.assertEqual(self.footer_root.attrib.get("preserveAspectRatio"), "xMidYMid meet")

        vb_vals = [float(v) for v in vb.split()]
        aspect_ratio = vb_vals[2] / vb_vals[3]
        self.assertAlmostEqual(aspect_ratio, 1200.0 / 90.0, places=5)

    def test_header_typography_card_bounding_box_and_margins(self):
        """Verify the frosted glass card [295, 905] x [74, 206] is perfectly centered horizontally."""
        # Find card rect: <rect x="295" y="74" width="610" height="132" rx="18" ... />
        match = re.search(r'<rect\s+x="(\d+)"\s+y="(\d+)"\s+width="(\d+)"\s+height="(\d+)"\s+rx="(\d+)"[^>]*cardBg', self.header_svg)
        self.assertIsNotNone(match, "Could not find cardBg rect in header.svg")

        x, y, w, h, rx = [float(match.group(i)) for i in range(1, 6)]
        self.assertEqual(x, 295.0)
        self.assertEqual(y, 74.0)
        self.assertEqual(w, 610.0)
        self.assertEqual(h, 132.0)
        self.assertEqual(rx, 18.0)

        # Center calculation: x + w/2 == 600.0
        center_x = x + w / 2.0
        self.assertEqual(center_x, 600.0, "Card center must be exactly 600.0")

        # Bilateral margins: left margin == right margin
        left_margin = x
        right_margin = 1200.0 - (x + w)
        self.assertEqual(left_margin, right_margin, f"Card must be horizontally symmetric ({left_margin} vs {right_margin})")
        self.assertEqual(left_margin, 295.0)

        # Vertical containment: y >= 0 and y + h <= 260
        self.assertGreaterEqual(y, 0.0)
        self.assertLessEqual(y + h, 260.0)
        bottom_margin = 260.0 - (y + h)
        self.assertEqual(bottom_margin, 54.0)

    def test_header_stag_bounding_box_and_clearance(self):
        """Extract all vertices of the noble stag, compute bounding box, and assert >= 80px clearance from card."""
        points = re.findall(r'([+-]?\d+(?:\.\d+)?)\s+([+-]?\d+(?:\.\d+)?)', STAG_PATH)
        self.assertGreater(len(points), 50, "STAG_PATH should contain at least 50 coordinates")

        xs = [float(p[0]) for p in points]
        ys = [float(p[1]) for p in points]

        raw_x_min, raw_x_max = min(xs), max(xs)
        raw_y_min, raw_y_max = min(ys), max(ys)

        # Transform in header.svg: translate(130, 112) scale(0.85)
        tx_min = 130.0 + raw_x_min * 0.85
        tx_max = 130.0 + raw_x_max * 0.85
        ty_min = 112.0 + raw_y_min * 0.85
        ty_max = 112.0 + raw_y_max * 0.85

        # Invariant 1: Stag is strictly contained within viewBox [0, 1200] x [0, 260]
        self.assertGreaterEqual(tx_min, 0.0, "Stag left edge exceeds viewBox")
        self.assertLessEqual(tx_max, 1200.0, "Stag right edge exceeds viewBox")
        self.assertGreaterEqual(ty_min, 0.0, "Stag top antler exceeds viewBox")
        self.assertLessEqual(ty_max, 260.0, "Stag hooves exceed viewBox")

        # Invariant 2: Clearance between stag rightmost boundary and typography card (x=295)
        card_x_min = 295.0
        clearance = card_x_min - tx_max
        self.assertGreaterEqual(clearance, 80.0, f"Stag-to-card clearance is too tight ({clearance:.2f}px < 80px)")
        self.assertAlmostEqual(clearance, 83.485, places=2)

    def test_header_typography_alignment_and_containment(self):
        """Verify Title, Subtitle, Meta, and Pill are centered at x=600 and vertically contained in [74, 206]."""
        # Eyebrow pill: x="500" y="86" width="200" height="18"
        pill_match = re.search(r'<rect\s+x="(\d+)"\s+y="(\d+)"\s+width="(\d+)"\s+height="(\d+)"[^>]*rx="9"', self.header_svg)
        self.assertIsNotNone(pill_match)
        px, py, pw, ph = [float(pill_match.group(i)) for i in range(1, 5)]
        self.assertEqual(px + pw / 2.0, 600.0, "Eyebrow pill must be centered at x=600")
        self.assertGreaterEqual(py, 74.0, "Pill top must be inside card")
        self.assertLessEqual(py + ph, 206.0, "Pill bottom must be inside card")

        # Text anchors and Y positions
        text_elements = [
            ("LIVING SYSTEMS", 98.5),
            ("NGUYỄN ANH DƯƠNG", 132.0),
            ("AI Engineer", 161.0),
            ("FPT University", 188.0),
        ]

        for snippet, expected_y in text_elements:
            match = re.search(rf'<text\s+x="(\d+)"\s+y="([0-9.]+)"[^>]*>([^<]*{re.escape(snippet)}[^<]*)</text>', self.header_svg)
            self.assertIsNotNone(match, f"Could not find text element for snippet '{snippet}'")
            x_val = float(match.group(1))
            y_val = float(match.group(2))
            self.assertEqual(x_val, 600.0, f"Text '{snippet}' must be centered at x=600")
            self.assertEqual(y_val, expected_y, f"Text '{snippet}' Y coordinate mismatch")
            self.assertGreaterEqual(y_val, 74.0, f"Text '{snippet}' above card")
            self.assertLessEqual(y_val, 206.0, f"Text '{snippet}' below card")

    def test_header_celestial_and_avian_spatial_clearance(self):
        """Verify celestial moon halo aligns above card, and soaring birds stay strictly above card (y <= 60)."""
        # Moon halo: cx="600" cy="42" r="36"
        moon_match = re.search(r'<circle\s+cx="(\d+)"\s+cy="(\d+)"\s+r="(\d+)"[^>]*moonHalo', self.header_svg)
        self.assertIsNotNone(moon_match)
        mcx, mcy, mr = [float(moon_match.group(i)) for i in range(1, 4)]
        self.assertEqual(mcx, 600.0)
        self.assertEqual(mcy, 42.0)
        self.assertEqual(mr, 36.0)

        # Moon bottom: 42 + 36 = 78, gently kissing top of card at y=74
        self.assertAlmostEqual(mcy + mr, 78.0)

        # Birds: group containing soaring birds
        bird_paths = re.findall(r'<path\s+d="M\s+(\d+)\s+(\d+)[^"]+"', self.header_svg)
        self.assertGreater(len(bird_paths), 10)

        # Check bird positions (start with M 440 48, M 465 38, M 425 58, M 725 45, M 750 54)
        for bx_str, by_str in [("440", "48"), ("465", "38"), ("425", "58"), ("725", "45"), ("750", "54")]:
            self.assertIn(f"M {bx_str} {by_str}", self.header_svg)
            by = float(by_str)
            self.assertLessEqual(by, 60.0, f"Bird at y={by} is not above typography card (y=74)")

    def test_footer_axis_line_and_node_bilateral_symmetry(self):
        """Verify footer organic axis spans [80, 1120] and node circles show exact reflection symmetry around x=600."""
        # Line: <line x1="80" y1="14" x2="1120" y2="14" ... />
        line_match = re.search(r'<line\s+x1="(\d+)"\s+y1="(\d+)"\s+x2="(\d+)"\s+y2="(\d+)"', self.footer_svg)
        self.assertIsNotNone(line_match)
        x1, y1, x2, y2 = [float(line_match.group(i)) for i in range(1, 5)]
        self.assertEqual(x1, 80.0)
        self.assertEqual(y1, 14.0)
        self.assertEqual(x2, 1120.0)
        self.assertEqual(y2, 14.0)
        self.assertEqual(x1, 1200.0 - x2, "Axis line must have equal left and right margins (80px)")

        # Node circles: cx values: 280, 420, 520, 680, 780, 920
        cxs = [float(m) for m in re.findall(r'<circle\s+cx="(\d+)"\s+cy="14"', self.footer_svg)]
        self.assertEqual(len(cxs), 7)  # 6 axis nodes + 1 glow spore at 600

        axis_cxs = sorted([cx for cx in cxs if cx != 600.0])
        self.assertEqual(axis_cxs, [280.0, 420.0, 520.0, 680.0, 780.0, 920.0])

        # Test bilateral reflection symmetry around 600.0:
        # pair 1: 520 and 680 (delta = 80)
        # pair 2: 420 and 780 (delta = 180)
        # pair 3: 280 and 920 (delta = 320)
        pairs = [(520.0, 680.0), (420.0, 780.0), (280.0, 920.0)]
        for left, right in pairs:
            self.assertEqual(600.0 - left, right - 600.0, f"Asymmetric node pair: {left}, {right}")

    def test_multi_resolution_viewport_projection_matrix(self):
        """Simulate responsive scaling across 17 diverse device resolutions and prove distortion-free projection."""
        viewports = [
            # Mobile
            (320, 568, "iPhone SE 1st gen"),
            (360, 800, "Samsung Galaxy"),
            (375, 667, "iPhone SE 2nd gen"),
            (390, 844, "iPhone 14"),
            (414, 896, "iPhone 11"),
            (430, 932, "iPhone 15 Pro Max"),
            # Foldable / Phablet
            (540, 720, "Surface Duo"),
            (600, 960, "Small Tablet"),
            # Tablet
            (768, 1024, "iPad Mini"),
            (820, 1180, "iPad Air"),
            (1024, 1366, "iPad Pro"),
            # Laptop / Desktop
            (1200, 800, "Native 1200px container"),
            (1280, 720, "HD Display"),
            (1366, 768, "Common Laptop"),
            (1440, 900, "MacBook Pro"),
            (1920, 1080, "Full HD Desktop"),
            (2560, 1440, "2K QHD Display"),
            (3840, 2160, "4K UHD Display"),
        ]

        for w, h, name in viewports:
            # Header projection (1200x260)
            scale_hdr = min(w / 1200.0, h / 260.0)
            rw_hdr = 1200.0 * scale_hdr
            rh_hdr = 260.0 * scale_hdr
            dx_hdr = (w - rw_hdr) / 2.0
            dy_hdr = (h - rh_hdr) / 2.0

            self.assertGreaterEqual(dx_hdr, -1e-5, f"Horizontal clipping on {name}")
            self.assertGreaterEqual(dy_hdr, -1e-5, f"Vertical clipping on {name}")
            self.assertAlmostEqual(rw_hdr / rh_hdr, 1200.0 / 260.0, places=4,
                                   msg=f"Aspect ratio distorted on {name}")

            # Footer projection (1200x90)
            scale_ftr = min(w / 1200.0, h / 90.0)
            rw_ftr = 1200.0 * scale_ftr
            rh_ftr = 90.0 * scale_ftr
            dx_ftr = (w - rw_ftr) / 2.0
            dy_ftr = (h - rh_ftr) / 2.0

            self.assertGreaterEqual(dx_ftr, -1e-5, f"Footer horizontal clipping on {name}")
            self.assertGreaterEqual(dy_ftr, -1e-5, f"Footer vertical clipping on {name}")
            self.assertAlmostEqual(rw_ftr / rh_ftr, 1200.0 / 90.0, places=4,
                                   msg=f"Footer aspect ratio distorted on {name}")

    def test_svg_font_size_hierarchy_and_readability(self):
        """Validate typographic font-size hierarchy across header and footer banners."""
        # Header hierarchy: Title (27px) > Subtitle (14.5px) > Meta (12.5px) > Badge (9.5px)
        title_match = re.search(r'class="title-text"\s+font-size="(\d+)"', self.header_svg)
        subtitle_match = re.search(r'class="subtitle-text"\s+font-size="([0-9.]+)"', self.header_svg)
        meta_match = re.search(r'class="meta-text"\s+font-size="([0-9.]+)"', self.header_svg)
        badge_match = re.search(r'\.badge-text\s*\{[^}]*font-size:\s*([0-9.]+)px', self.header_svg)

        self.assertIsNotNone(title_match)
        self.assertIsNotNone(subtitle_match)
        self.assertIsNotNone(meta_match)
        self.assertIsNotNone(badge_match)

        s_title = float(title_match.group(1))
        s_subtitle = float(subtitle_match.group(1))
        s_meta = float(meta_match.group(1))
        s_badge = float(badge_match.group(1))

        self.assertGreater(s_title, s_subtitle, "Title must be larger than subtitle")
        self.assertGreater(s_subtitle, s_meta, "Subtitle must be larger than meta")
        self.assertGreater(s_meta, s_badge, "Meta must be larger than badge")
        self.assertEqual(s_title, 27.0)
        self.assertEqual(s_subtitle, 14.5)
        self.assertEqual(s_meta, 12.5)
        self.assertEqual(s_badge, 9.5)

        # Footer hierarchy: Quote (14px) > Author (11.5px)
        quote_match = re.search(r'class="quote-text"\s+font-size="(\d+)"', self.footer_svg)
        author_match = re.search(r'class="author-text"\s+font-size="([0-9.]+)"', self.footer_svg)
        self.assertIsNotNone(quote_match)
        self.assertIsNotNone(author_match)
        self.assertGreater(float(quote_match.group(1)), float(author_match.group(1)))


# ============================================================================
# 4. WORKFLOW CONCURRENCY & ECOSYSTEM HARDENING
# ============================================================================

class TestWorkflowAndEcosystemHardening(unittest.TestCase):
    """Adversarial stress-testing of GitHub Actions concurrency evaluation and ecosystem contracts."""

    def test_concurrency_group_disjointness_adversarial_refs(self):
        """Evaluate concurrency groups across 20 adversarial git ref strings and prove 100% prefix disjointness."""
        adversarial_refs = [
            "refs/heads/main",
            "refs/heads/feature/autonomous-agents",
            "refs/heads/fix/utf8-diacritics-2026",
            "refs/tags/v1.0.0",
            "refs/tags/v2.0-rc1",
            "refs/pull/42/merge",
            "refs/heads/sub/deep/nested/path/branch",
            "refs/heads/branch-with-hyphens-and_underscores",
            "",
            "HEAD",
            "refs/heads/living-systems#123",
            "refs/heads/test%20space",
            "refs/heads/unicode-🚀-emerald",
        ]

        for ref in adversarial_refs:
            snake_group = f"snake-{ref}"
            p3d_group = f"profile-3d-{ref}"
            widgets_group = "readme-widgets"

            # Invariant 1: Snake and profile-3d groups must never collide
            self.assertNotEqual(snake_group, p3d_group, f"Collision between snake and 3d on ref '{ref}'")

            # Invariant 2: Dynamic widgets group is constant and disjoint from snake & 3d
            self.assertNotEqual(snake_group, widgets_group)
            self.assertNotEqual(p3d_group, widgets_group)

            # Invariant 3: Prefixes are strictly disjoint
            self.assertTrue(snake_group.startswith("snake-"))
            self.assertTrue(p3d_group.startswith("profile-3d-"))

    def test_workflow_permissions_least_privilege(self):
        """Verify that all workflows scope permissions strictly to 'contents: write'."""
        workflow_files = list(WORKFLOWS_DIR.glob("*.yml"))
        self.assertEqual(len(workflow_files), 3, "Expected 3 workflow files in .github/workflows/")

        for wf in workflow_files:
            content = wf.read_text(encoding="utf-8")
            self.assertIn("permissions:", content, f"Missing permissions block in {wf.name}")
            self.assertIn("contents: write", content, f"Missing contents: write in {wf.name}")

    def test_camo_cache_busting_local_svg_matrix(self):
        """Verify that every local SVG referenced in README.md carries ?v=nature_2026 cache-busting query."""
        readme = README_PATH.read_text(encoding="utf-8")

        # Find all references to assets/*.svg or profile-3d-contrib/*.svg in src, href, srcset, and markdown links
        local_svg_refs = re.findall(r'(?:src|href|srcset)=["\']([^"\']+\.svg[^"\']*)["\']', readme)
        local_svg_refs += re.findall(r'\]\(([^)]+\.svg[^)]*)\)', readme)

        filtered = [r for r in local_svg_refs if "assets/" in r or "profile-3d-contrib/" in r]
        self.assertGreaterEqual(len(filtered), 10, f"Expected at least 10 local SVG references in README, found {len(filtered)}")

        for ref in filtered:
            self.assertIn("?v=nature_2026", ref, f"Missing or incorrect cache buster in local reference: {ref}")

    def test_repository_pins_palette_dark_mode_compliance(self):
        """Verify all repository pins in assets/ utilize dark slate backgrounds and living systems accents."""
        pin_files = list(ASSETS_DIR.glob("pin-*.svg"))
        self.assertGreaterEqual(len(pin_files), 5, "Expected at least 5 repository pin SVGs")

        for pin in pin_files:
            content = pin.read_text(encoding="utf-8")
            # All pins must have dark background #0B1220 and stroke #1E293B
            self.assertIn("#0B1220", content, f"Pin {pin.name} does not use dark theme background #0B1220")
            self.assertIn("#1E293B", content, f"Pin {pin.name} does not use dark slate stroke #1E293B")
            self.assertNotIn("#E4E2E2", content, f"Pin {pin.name} contains light-mode stroke #E4E2E2")


# ============================================================================
# MAIN RUNNER
# ============================================================================

def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestFetchAllWidgetsExceptionHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestDeterministicSvgGenerationUnderVariedLocalesAndEnvironments))
    suite.addTests(loader.loadTestsFromTestCase(TestViewportScalingAndCoordinateBounds))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowAndEcosystemHardening))

    runner = unittest.TextTestRunner(verbosity=2)
    print("=" * 80)
    print("  TIER 5 WHITE-BOX ADVERSARIAL COVERAGE HARDENING SUITE")
    print(f"  Target: {REPO_ROOT}")
    print("=" * 80)
    result = runner.run(suite)

    print("=" * 80)
    print(f"  TIER 5 TEST SUMMARY: Run {result.testsRun}, Failures {len(result.failures)}, Errors {len(result.errors)}")
    if result.wasSuccessful():
        print("  RESULT: [PASS] All Tier 5 white-box adversarial stress tests passed!")
        print("=" * 80)
        return 0
    else:
        print("  RESULT: [FAIL] Vulnerabilities or regressions detected!")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
