#!/usr/bin/env python3
"""
White-Box Adversarial Verification Test Suite for Milestone 4 (Phase 2: Tier 5 Coverage Hardening)
Ecosystem: DuongNAD/DuongNAD

Author: teamwork_preview_challenger_m4_2 (Empirical Challenger)
Target: assets/, profile-3d-contrib/, README.md, tests/test_profile_ecosystem.py

Verification Areas:
1. Vector Assets Audit (all 25 SVGs): strict XML well-formedness, SVG 1.1 spec, viewBox attributes, security.
2. External URLs Probe: bot-detection resiliency, SSL cert validity, HTTP status codes, redirect tracking.
3. GFM Responsive Rendering Simulation: mobile 320px to 4K 3840px, balanced DOM tree, responsive width constraints.
4. E2E Test Suite Strict Verification: test_profile_ecosystem.py --strict 20/20 PASS.
"""

import os
import re
import socket
import ssl
import subprocess
import sys
import unittest
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import markdown
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"
ASSETS_DIR = REPO_ROOT / "assets"
P3D_DIR = REPO_ROOT / "profile-3d-contrib"

ALL_EXPECTED_ASSETS = [
    # assets/ (15)
    "assets/activity-graph.svg",
    "assets/footer.svg",
    "assets/header.svg",
    "assets/pin-anima.svg",
    "assets/pin-buy-or-wait.svg",
    "assets/pin-liva.svg",
    "assets/pin-mcp-agy.svg",
    "assets/pin-smart-drive-os.svg",
    "assets/pin-vn-ai.svg",
    "assets/streak.svg",
    "assets/trophies.svg",
    "assets/github-contribution-grid-snake-dark.svg",
    "assets/github-contribution-grid-snake.svg",
    "assets/stats.svg",
    "assets/top-langs.svg",
    # profile-3d-contrib/ (10)
    "profile-3d-contrib/profile-gitblock.svg",
    "profile-3d-contrib/profile-green-animate.svg",
    "profile-3d-contrib/profile-green.svg",
    "profile-3d-contrib/profile-night-green.svg",
    "profile-3d-contrib/profile-night-rainbow.svg",
    "profile-3d-contrib/profile-night-view.svg",
    "profile-3d-contrib/profile-season-animate.svg",
    "profile-3d-contrib/profile-season.svg",
    "profile-3d-contrib/profile-south-season-animate.svg",
    "profile-3d-contrib/profile-south-season.svg",
]


class TestVectorAssetsAudit(unittest.TestCase):
    """Adversarial white-box audit of all 25 vector assets across assets/ and profile-3d-contrib/."""

    def setUp(self):
        self.asset_files = [REPO_ROOT / p for p in ALL_EXPECTED_ASSETS]

    def test_all_25_assets_inventory_exists(self):
        """Verify exactly 25 vector assets exist on disk across assets/ and profile-3d-contrib/."""
        assets_found = sorted(list(ASSETS_DIR.glob("*.svg")))
        p3d_found = sorted(list(P3D_DIR.glob("*.svg")))
        total_found = len(assets_found) + len(p3d_found)

        self.assertEqual(len(assets_found), 15, f"Expected 15 SVGs in assets/, found {len(assets_found)}")
        self.assertEqual(len(p3d_found), 10, f"Expected 10 SVGs in profile-3d-contrib/, found {len(p3d_found)}")
        self.assertEqual(total_found, 25, f"Expected 25 total SVGs, found {total_found}")

        for path in self.asset_files:
            self.assertTrue(path.exists(), f"Asset {path.relative_to(REPO_ROOT)} is missing on disk")

    def test_strict_xml_parsing_all_25(self):
        """Verify strict XML well-formedness and namespace parsing on all 25 SVG assets."""
        failures = []
        for path in self.asset_files:
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            try:
                raw_bytes = path.read_bytes()
                # Check byte stream integrity: valid UTF-8, no NULL bytes
                self.assertNotIn(b"\x00", raw_bytes, f"{rel} contains NULL bytes")
                text = raw_bytes.decode("utf-8")
                
                # Parse with ElementTree
                root = ET.fromstring(text)
                tag = root.tag.lower()
                self.assertTrue(
                    tag.endswith("svg"),
                    f"{rel} root element is not <svg> (got '{root.tag}')"
                )
            except Exception as e:
                failures.append((rel, str(e)))

        self.assertEqual(len(failures), 0, f"XML parsing failed on {len(failures)} assets: {failures}")

    def test_viewbox_and_dimensions_spec_all_25(self):
        """
        Verify SVG 1.1 viewBox and dimensional attributes across all 25 vector assets:
        - Root must have valid viewBox attribute or valid width/height scalable coordinate system.
        - If viewBox is present, it must consist of 4 numeric values (min-x, min-y, width, height) where width > 0 and height > 0.
        """
        failures = []
        for path in self.asset_files:
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            try:
                root = ET.parse(path).getroot()
                vb = root.get("viewBox")
                width = root.get("width")
                height = root.get("height")

                # An SVG must have a viewBox or width & height to define coordinate system
                has_vb = bool(vb and vb.strip())
                has_dims = bool(width and height)

                self.assertTrue(
                    has_vb or has_dims,
                    f"{rel} has neither viewBox nor width/height defined"
                )

                if has_vb:
                    # Validate viewBox syntax: 4 numeric values
                    vb_clean = vb.strip().replace(",", " ")
                    parts = [p for p in vb_clean.split() if p]
                    self.assertEqual(
                        len(parts), 4,
                        f"{rel} viewBox '{vb}' must have exactly 4 values (min-x, min-y, width, height)"
                    )
                    min_x, min_y, w, h = [float(x) for x in parts]
                    self.assertGreater(w, 0, f"{rel} viewBox width must be > 0 (got {w})")
                    self.assertGreater(h, 0, f"{rel} viewBox height must be > 0 (got {h})")

                if has_dims:
                    # Check width/height strings are not empty or malformed
                    self.assertGreater(len(str(width).strip()), 0)
                    self.assertGreater(len(str(height).strip()), 0)

            except Exception as e:
                failures.append((rel, str(e)))

        self.assertEqual(len(failures), 0, f"viewBox/dimension verification failed on {len(failures)} assets: {failures}")

    def test_svg_security_and_script_injection_all_25(self):
        """
        Adversarial Security Audit:
        Ensure no vector asset contains dangerous executable elements:
        - No <script> tags
        - No inline on* event listeners (e.g. onload, onerror, onclick)
        - No 'javascript:' URIs
        - No remote <link> or remote CSS @import
        """
        forbidden_patterns = [
            (r"<\s*script\b", "Prohibited <script> tag"),
            (r"\bon[a-z]{3,15}\s*=", "Prohibited inline event handler (on*)"),
            (r"javascript\s*:", "Prohibited javascript: URI"),
            (r"<\s*link\b", "Prohibited external <link> stylesheet"),
            (r"@import\s+url", "Prohibited remote CSS @import"),
        ]

        violations = []
        for path in self.asset_files:
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            content = path.read_text(encoding="utf-8")
            for pattern, desc in forbidden_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    violations.append((rel, desc, match.group(0)))

        self.assertEqual(len(violations), 0, f"Security violations found in SVG assets: {violations}")

    def test_header_and_footer_spec_compliance(self):
        """Verify strict specification compliance for header.svg and footer.svg."""
        header_path = ASSETS_DIR / "header.svg"
        footer_path = ASSETS_DIR / "footer.svg"

        h_root = ET.parse(header_path).getroot()
        f_root = ET.parse(footer_path).getroot()

        # Header: viewBox="0 0 1200 260"
        self.assertEqual(h_root.get("viewBox", "").strip(), "0 0 1200 260")
        self.assertEqual(h_root.get("role"), "img")

        # Footer: viewBox="0 0 1200 90"
        self.assertEqual(f_root.get("viewBox", "").strip(), "0 0 1200 90")
        self.assertEqual(f_root.get("preserveAspectRatio"), "xMidYMid meet")


class TestExternalURLsProbe(unittest.TestCase):
    """Adversarial link probing: SSL cert validity, status codes, and anti-bot tolerance."""

    @classmethod
    def setUpClass(cls):
        readme_text = README_PATH.read_text(encoding="utf-8")
        raw_urls = []
        # Markdown links [text](url)
        raw_urls += re.findall(r'\[.*?\]\((https?://[^\s\)]+)\)', readme_text)
        # HTML href
        raw_urls += re.findall(r'href=[\'"](https?://[^\s\'"]+)[\'"]', readme_text)
        # HTML src
        raw_urls += re.findall(r'src=[\'"](https?://[^\s\'"]+)[\'"]', readme_text)

        # Unique normalized URLs
        cls.urls = sorted(list(set(raw_urls)))
        cls.browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def test_extracted_url_count(self):
        """Verify README.md contains at least 15 unique external URLs."""
        self.assertGreaterEqual(len(self.urls), 15, f"Expected >= 15 URLs, extracted {len(self.urls)}")

    def test_ssl_certificate_validity(self):
        """
        Probe SSL/TLS certificates of all unique HTTPS hosts in README.md.
        Verify certificate is valid, matches hostname, and expiration is in the future.
        """
        https_hosts = set()
        for url in self.urls:
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme == "https":
                https_hosts.add(parsed.hostname)

        ssl_failures = []
        for host in sorted(list(https_hosts)):
            if not host:
                continue
            ctx = ssl.create_default_context()
            try:
                with socket.create_connection((host, 443), timeout=10) as sock:
                    with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                        cert = ssock.getpeercert()
                        not_after_str = cert["notAfter"]
                        # Format: 'May 15 12:00:00 2027 GMT'
                        expire_dt = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                        now_dt = datetime.now(timezone.utc)
                        if expire_dt <= now_dt:
                            ssl_failures.append((host, f"Expired on {expire_dt}"))
            except Exception as e:
                # Some servers might require SNI or specific cipher suites; record failure
                ssl_failures.append((host, str(e)))

        self.assertEqual(len(ssl_failures), 0, f"SSL verification failed on hosts: {ssl_failures}")

    def test_google_drive_credentials_strict_reachability(self):
        """
        Strictly probe Google Drive credential links for all 3 honors & certifications.
        Must return HTTP 200 or 302/303/307 redirect leading to HTTP 200.
        """
        gdrive_urls = [u for u in self.urls if "drive.google.com" in u]
        self.assertGreaterEqual(len(gdrive_urls), 3, "Expected at least 3 Google Drive credential URLs")

        ctx = ssl.create_default_context()
        for url in gdrive_urls:
            req = urllib.request.Request(url, headers=self.browser_headers)
            try:
                with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
                    self.assertIn(resp.status, [200, 301, 302, 307], f"Google Drive URL returned {resp.status}: {url}")
            except urllib.error.HTTPError as e:
                self.fail(f"Google Drive credential URL failed with HTTP {e.code}: {url}")

    def test_badge_and_widget_endpoints_reachability(self):
        """Probe dynamic badge & widget service endpoints (komarev, shields.io, demolab typing svg, skillicons)."""
        badge_endpoints = [u for u in self.urls if any(d in u for d in ["komarev.com", "shields.io", "readme-typing-svg", "skillicons.dev"])]
        self.assertGreaterEqual(len(badge_endpoints), 3)

        ctx = ssl.create_default_context()
        for url in badge_endpoints:
            req = urllib.request.Request(url, headers=self.browser_headers)
            try:
                with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
                    self.assertIn(resp.status, [200, 301, 302], f"Badge service {url} returned {resp.status}")
            except urllib.error.HTTPError as e:
                # Komarev or shields may rate limit, but should be 200/304
                if e.code not in (429,):
                    self.fail(f"Badge URL {url} failed with HTTP {e.code}")

    def test_all_external_urls_bot_tolerance_audit(self):
        """
        Probe all external URLs in README.md.
        Bot-defended platforms (LinkedIn, Facebook, TryHackMe, HuggingFace) return 403 or 429 when hit programmatically.
        All other URLs must return HTTP 200 or 30x.
        """
        BOT_DEFENDED_DOMAINS = {"linkedin.com", "facebook.com", "tryhackme.com", "huggingface.co"}

        failed_urls = []
        ctx = ssl.create_default_context()

        for url in self.urls:
            parsed = urllib.parse.urlparse(url)
            is_bot_defended = any(domain in (parsed.hostname or "") for domain in BOT_DEFENDED_DOMAINS)

            req = urllib.request.Request(url, headers=self.browser_headers)
            try:
                with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
                    # Successful response
                    status = resp.status
                    if status not in (200, 301, 302, 307, 308):
                        failed_urls.append((url, f"Unexpected HTTP status {status}"))
            except urllib.error.HTTPError as e:
                if is_bot_defended and e.code in (403, 429, 999):
                    # Known bot defense mechanism (e.g. Cloudflare / LinkedIn 999 / Facebook 403)
                    continue
                failed_urls.append((url, f"HTTP Error {e.code}: {e.reason}"))
            except Exception as e:
                failed_urls.append((url, str(e)))

        self.assertEqual(len(failed_urls), 0, f"Unreachable or failed external URLs: {failed_urls}")


class TestGFMRenderingExtremeViewports(unittest.TestCase):
    """GitHub Flavored Markdown (GFM) DOM simulation across extreme viewports (320px to 3840px)."""

    def setUp(self):
        self.raw_text = README_PATH.read_text(encoding="utf-8")
        self.rendered_html = markdown.markdown(self.raw_text, extensions=["tables", "fenced_code"])
        self.soup = BeautifulSoup(self.rendered_html, "html.parser")

    def test_html_tag_nesting_and_balance(self):
        """Adversarial DOM parser test: check exact tag balance and nesting structure."""
        no_comments = re.sub(r"<!--.*?-->", "", self.raw_text, flags=re.DOTALL)
        
        # Track opening and closing tags
        open_tags = re.findall(r"<([a-zA-Z0-9]+)(?:\s+[^>]*)?>", no_comments)
        close_tags = re.findall(r"</([a-zA-Z0-9]+)>", no_comments)
        void_tags = {"img", "br", "hr", "source", "input", "meta", "link"}

        open_counts = {}
        for t in open_tags:
            tag = t.lower()
            if tag not in void_tags:
                open_counts[tag] = open_counts.get(tag, 0) + 1

        close_counts = {}
        for t in close_tags:
            tag = t.lower()
            close_counts[tag] = close_counts.get(tag, 0) + 1

        mismatched = []
        for tag in set(open_counts.keys()).union(set(close_counts.keys())):
            o = open_counts.get(tag, 0)
            c = close_counts.get(tag, 0)
            if o != c:
                mismatched.append(f"<{tag}>: open={o}, close={c}")

        self.assertEqual(len(mismatched), 0, f"Unbalanced HTML tags in README.md: {mismatched}")

    def test_extreme_viewports_simulation(self):
        """
        Simulate GFM responsive rendering behavior across extreme viewports:
        - 320px (Mobile Narrow / iPhone SE)
        - 375px (Mobile Standard)
        - 768px (Tablet)
        - 1440px (Desktop HD)
        - 3840px (4K Ultra HD)
        """
        VIEWPORTS = [320, 375, 768, 1440, 3840]

        # Scan all images in rendered DOM
        img_tags = self.soup.find_all("img")
        self.assertGreater(len(img_tags), 10, "Expected >10 images in rendered README")

        # Full-width responsive banner check: header, footer, snake, activity-graph, trophies, 3D city
        full_width_assets = [
            "header.svg",
            "footer.svg",
            "github-contribution-grid-snake-dark.svg",
            "activity-graph.svg",
            "trophies.svg",
            "profile-night-rainbow.svg",
        ]

        for asset_name in full_width_assets:
            matching = [img for img in img_tags if asset_name in img.get("src", "")]
            self.assertGreaterEqual(
                len(matching), 1,
                f"Full-width responsive asset {asset_name} missing from rendered DOM"
            )
            for img in matching:
                width_attr = img.get("width", "")
                self.assertEqual(
                    width_attr, "100%",
                    f"Asset {asset_name} must have width='100%' for responsive fluid scaling (got '{width_attr}')"
                )

        # Simulation across viewports: verify table layout resilience
        tables = self.soup.find_all("table")
        self.assertGreaterEqual(len(tables), 2, "Expected at least 2 tables (Featured Projects, Tech Stack)")

        for vp_width in VIEWPORTS:
            # Table columns should not have fixed pixel widths >= viewport
            for table in tables:
                for td in table.find_all("td"):
                    w = td.get("width", "")
                    if w.endswith("px"):
                        pixel_w = float(w.rstrip("px"))
                        self.assertLess(
                            pixel_w, vp_width,
                            f"Table cell width {w} overflows viewport {vp_width}px"
                        )
                    elif w.endswith("%"):
                        # Percentage width scales automatically across all viewports
                        pct = float(w.rstrip("%"))
                        self.assertLessEqual(pct, 100.0)

    def test_featured_projects_symmetry_and_grid(self):
        """Verify Featured Projects table contains exactly 7 core projects in clean 4x2 grid."""
        tables = self.soup.find_all("table")
        proj_table = tables[0]
        rows = proj_table.find_all("tr")
        self.assertEqual(len(rows), 4, f"Featured Projects table must have 4 rows, found {len(rows)}")

        cells = proj_table.find_all("td")
        self.assertEqual(len(cells), 8, f"Featured Projects table must have 8 cells (4x2 grid), found {len(cells)}")

        # Verify each cell has width="50%"
        for i, cell in enumerate(cells):
            self.assertEqual(cell.get("width"), "50%", f"Cell {i} in Featured Projects table must specify width='50%'")
            self.assertEqual(cell.get("valign"), "top", f"Cell {i} in Featured Projects table must specify valign='top'")


class TestCoreEcosystemStrictRunner(unittest.TestCase):
    """Subprocess runner validating python tests/test_profile_ecosystem.py --strict passes 20/20 with exit code 0."""

    def test_strict_ecosystem_suite_passes(self):
        """Execute test_profile_ecosystem.py --strict in fresh Python interpreter."""
        cmd = [sys.executable, str(REPO_ROOT / "tests" / "test_profile_ecosystem.py"), "--strict"]
        result = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)

        self.assertEqual(
            result.returncode, 0,
            f"test_profile_ecosystem.py --strict exited with code {result.returncode}.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        self.assertIn("Ran 20 tests", result.stderr + result.stdout)
        self.assertIn("OK", result.stderr + result.stdout)
        self.assertIn("RESULT: [PASS] All test tiers verified successfully!", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
