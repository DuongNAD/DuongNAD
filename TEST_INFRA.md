# Test Infrastructure Specification: GitHub Profile Ecosystem Harmonization

**Author**: `teamwork_preview_test_writer_e2e`  
**Target Repository**: `DuongNAD/DuongNAD`  
**Execution Environment**: Python 3.11+ / Standard Library (Zero Third-Party Runtime Requirement)  
**Standard Test Command**: `python tests/test_profile_ecosystem.py`  
**Strict Full-Suite Command**: `python tests/test_profile_ecosystem.py --strict` (or `STRICT_E2E=1`)

---

## 1. Test Architecture & 4-Tier Methodology

The verification suite for the **GitHub Profile Ecosystem Harmonization** project adopts an opaque-box, requirement-driven, 4-tier testing hierarchy. Each tier tests a distinct dimension of ecosystem health: from raw asset syntax and content completeness to adversarial stress cases, cross-component visual harmony, and end-to-end simulated rendering.

```
+-------------------------------------------------------------------------+
|                  TIER 4: REAL-WORLD WORKLOAD SCENARIOS                  |
|  - Simulated GitHub Profile DOM & Table Rendering (Desktop & Mobile)    |
|  - Workflow Concurrency Dry-Runs & Schedule Collision Auditing          |
|  - External URL Reachability with Bot-Protection Tolerance & Retries   |
+-------------------------------------------------------------------------+
                                    |
+-------------------------------------------------------------------------+
|                 TIER 3: CROSS-FEATURE COMBINATIONS                      |
|  - Responsive <picture> Grid for Dark/Light Mode Theme Switching        |
|  - Camo CDN Cache-Busting Parameter Synchronization (?v=nature_2026)    |
|  - Palette Cohesion (Emerald/Teal/Slate Hex Accents across Components)  |
+-------------------------------------------------------------------------+
                                    |
+-------------------------------------------------------------------------+
|                  TIER 2: BOUNDARY & CORNER CASES                        |
|  - XML Parser Adversarial Stress (Malformed Tags, Unescaped Entities)   |
|  - Sanitizer Resilience (Error Cards, Stagger Freezes, Undefined Rows)  |
|  - Extreme Viewports & Coordinate Scaling (Aspect Ratio Verification)   |
|  - UTF-8 Encoding & Multilingual Diacritics ("Nguyễn Anh Dương")       |
+-------------------------------------------------------------------------+
                                    |
+-------------------------------------------------------------------------+
|                     TIER 1: FEATURE COVERAGE                            |
|  - 100% XML Validity across all SVGs in assets/ & profile-3d-contrib/   |
|  - Header & Footer Contract Compliance (viewBox, motifs, typography)    |
|  - Parity for 7 Core Projects & 3 Verified Google Drive Credentials     |
|  - Dynamic Widget Inventory & GitHub Actions Workflow Schema            |
+-------------------------------------------------------------------------+
```

---

## 2. Expected Output Derivation & Authoritative Oracles

Every test case derives its expected assertions directly from authoritative sources:

| Feature Dimension | Authoritative Source | Oracle / Expected Value Derivation |
|---|---|---|
| **Header SVG Contract** | `PROJECT.md` § Interface Contracts | `viewBox="0 0 1200 260"`, `width="100%"`, `role="img"`, valid XML element tree, presence of `#skyGrad`, `#mtnFar`, `#mtnMid`, `#mtnNear`, conifer trees, stag silhouette, and central title `NGUYỄN ANH DƯƠNG`. |
| **Footer SVG Contract** | `PROJECT.md` § Interface Contracts | `viewBox="0 0 1200 90"`, `width="100%"`, `role="img"`, valid XML, organic leaf motif, quote text, author signature `NGUYEN ANH DUONG (DuongNAD)`. |
| **XML Syntactic Integrity** | W3C SVG 1.1 / XML 1.0 Spec | Python `xml.etree.ElementTree.parse()` returns a root element without raising `ET.ParseError`. Root tag is `{http://www.w3.org/2000/svg}svg` or `svg`. |
| **Featured Projects Parity** | `ORIGINAL_REQUEST.md` § R3 | Exactly 7 projects: `LIVA`, `Anima Engine`, `Buy or Wait?`, `MindSync` (VAIC 2026), `Darwin Lab`, `mcp-agy`, `Vision-Guided Robotic Arm`. Pin SVGs present in `assets/`. |
| **Verified Honors & Certs** | `ORIGINAL_REQUEST.md` § R3 | 3 verified honors with valid Google Drive links: HackerRank Orchestrate Top 16% (`1Hl0qvEHIbgp6Fus2o0EukKZImMNrEr-I`), VAIC 2026 Team Lead (`1x8zT32FnxJ5GZxvohfV4F_Ey9QUNAUzZ`), DENSO Factory Hacks Top 4 (`1K1Sfw4AnxBfi7deHBIaIqpH9cJ-G3ti9`). |
| **Palette Cohesion** | `PROJECT.md` § Architecture | Emerald/Teal palette: Primary greens (`#10B981`, `#059669`, `#047857`, `#064E3B`, `#34D399`, `#6EE7B7`, `#A7F3D0`), forest bases (`#134236`, `#0B241E`, `#05120F`, `#04120E`), dark slates (`#0F172A`, `#1E293B`, `#0B1220`). |
| **GitHub Actions Workflows** | GitHub Actions Workflow Syntax | Valid YAML, `actions/checkout@v4`, `contents: write` permissions, schedule crons, concurrency groups. |
| **External URL Health** | HTTP RFC 9110 | HTTP 200 for Google Drive assets, shields, and repositories. HTTP 200/301/302/307/308 or anti-bot 403/429 challenge tolerated for bot-guarded social endpoints. |

---

## 3. Tier Details & Test Suite Mapping

### Tier 1: Feature Coverage

1. **`test_tier1_svg_xml_validity`**:
   - Enumerates every `.svg` file in `assets/` (15 files) and `profile-3d-contrib/` (10 files).
   - Validates well-formed XML structure via `xml.etree.ElementTree`.
   - Confirms root tag is `<svg>` and `xmlns="http://www.w3.org/2000/svg"` is defined.

2. **`test_tier1_header_contract`**:
   - Validates `assets/header.svg` adheres to exact interface contract:
     - `viewBox == "0 0 1200 260"`
     - Aspect ratio is 4.615:1
     - Zero external `<link rel="stylesheet">` or `@import` (self-contained `<defs><style>`)
     - Contains Nordic mountain silhouettes, conifer gradients, celestial glow, and firefly effects.
     - Title contains `"NGUYỄN ANH DƯƠNG"` and subtitle reflects `"Living Systems & Agentic AI"`.

3. **`test_tier1_footer_contract`**:
   - Validates `assets/footer.svg`:
     - `viewBox == "0 0 1200 90"`
     - Leaf emblem path `M 0 -8 C 6 -4...`
     - Philosophical quote: `"In nature as in software: complex, living intelligence emerges from simple, elegant rules."`
     - Author signature text and emerald accent stroke `#134236`.

4. **`test_tier1_snake_assets_contract`**:
   - Validates existence and XML validity of both `github-contribution-grid-snake.svg` and `github-contribution-grid-snake-dark.svg`.
   - Validates dark snake color styling aligns with emerald/slate variables.

5. **`test_tier1_repo_pins`**:
   - Validates existence of project pin cards: `pin-liva.svg`, `pin-anima.svg`, `pin-buy-or-wait.svg`, `pin-mcp-agy.svg`, `pin-smart-drive-os.svg`, `pin-vn-ai.svg`.

6. **`test_tier1_featured_projects_parity`**:
   - Checks presence of all 7 core projects across the ecosystem.
   - Asserts ecosystem readiness for `LIVA`, `Anima Engine`, `Buy or Wait?`, `MindSync`, `Darwin Lab`, `mcp-agy`, and `Vision-Guided Robotic Arm`.

7. **`test_tier1_verified_credentials_parity`**:
   - Verifies 3 primary honors in `README.md`:
     - HackerRank Orchestrate (Final Rank #493 / 3,062, Top 16% Globally) with Google Drive link.
     - MindSync / VAIC 2026 Team Lead with Google Drive bootcamp certificate link.
     - DENSO Factory Hacks Top 4 & Promising Award with Google Drive certificate link.
     - Gemini Academy for Student folder link.

8. **`test_tier1_dynamic_widgets_inventory`**:
   - Validates `stats.svg`, `top-langs.svg`, `streak.svg`, `trophies.svg`, `activity-graph.svg`, and `profile-3d-contrib/profile-night-rainbow.svg` are present on disk and referenced in `README.md`.

9. **`test_tier1_workflow_contracts`**:
   - Validates `snake.yml`, `profile-3d.yml`, `readme-widgets.yml` exist, parse as valid YAML, declare `contents: write`, and use `actions/checkout@v4`.

---

### Tier 2: Boundary & Corner Cases

1. **`test_tier2_malformed_xml_handling`**:
   - Tests parser behavior against corrupted SVG payloads (unclosed `<svg>`, unescaped `&`, broken attribute quotes).
   - Confirms parser correctly identifies and rejects malformed inputs.

2. **`test_tier2_sanitizer_error_cards`**:
   - Exercises `scripts/fetch-all-widgets.py` and `scripts/sanitize-widget.py` against upstream error payloads (`"failed to retrieve"`, `"something went wrong"`, `"deployment_paused"`).
   - Confirms sanitizer returns `None` or exit code 1 to protect local asset stability.

3. **`test_tier2_empty_and_whitespace_inputs`**:
   - Verifies sanitizers and XML parsers gracefully handle empty strings, whitespace, null characters, and truncated content without unhandled exceptions.

4. **`test_tier2_extreme_viewports_and_aspect_ratios`**:
   - Verifies viewBox parser handles non-standard viewports (extreme aspect ratios, large coordinates, zero width/height) and enforces header aspect ratio tolerance (width between 1000-1400, height between 220-300).

5. **`test_tier2_special_characters_and_encoding`**:
   - Validates UTF-8 encoding across all files.
   - Asserts Vietnamese diacritics (`NGUYỄN ANH DƯƠNG`, `Dương Nguyễn Anh`) are correctly represented without mojibake (`Ã`, `Â©`, `&#65533;`, `\ufffd`).
   - Asserts HTML entities in SVG (`&amp;`) are properly escaped.

---

### Tier 3: Cross-Feature Combinations

1. **`test_tier3_dark_light_snake_picture_tag`**:
   - Validates `<picture>` structure in `README.md`:
     - Exactly one `<source media="(prefers-color-scheme: dark)" srcset="...">`
     - Exactly one `<source media="(prefers-color-scheme: light)" srcset="...">`
     - Fallback `<img ... alt="Contribution Grid Snake" ... />`
     - File targets referenced in `srcset` resolve to existing, valid SVGs.

2. **`test_tier3_camo_cache_busting`**:
   - Examines all local image references in `README.md` (`./assets/...` and `./profile-3d-contrib/...`).
   - Validates cache-busting query parameter presence (`?v=...`), ensuring GitHub Camo CDN does not serve stale cached SVGs.
   - Enforces `?v=nature_2026` in strict mode or confirms milestone transition.

3. **`test_tier3_palette_harmony`**:
   - Extracts all color hex codes from `header.svg`, `footer.svg`, and widget scripts.
   - Verifies visual harmony with the living systems palette:
     - Rejects neon cyberpunk clashes (`#FF00FF`, `#00FFFF`, `#FF0055`).
     - Rejects unstyled pure white backgrounds (`#FFFFFF` background cards).
     - Confirms predominance of emerald (`#10B981`, `#059669`, `#34D399`), deep teal (`#0D9488`, `#14463C`), forest pine (`#134236`, `#05120F`), and slate (`#0F172A`, `#1E293B`).

---

### Tier 4: Real-World Workload Scenarios

1. **`test_tier4_simulated_github_profile_render`**:
   - Simulates GitHub Flavored Markdown (GFM) parsing and DOM structure:
     - Validates all HTML tags in `README.md` are strictly balanced (open tag count matches close tag count for all non-void elements `div`, `a`, `p`, `table`, `tr`, `td`, `picture`, `h3`, `code`, `strong`).
     - Verifies GFM table syntax in Featured Projects and Awards (header rows, markdown pipes, delimiter dashes `| :--- |`).
     - Validates mobile responsiveness: fluid widths (`width="100%"`) on primary cards and SVGs, balanced columns (`width="50%"`) on desktop tables.

2. **`test_tier4_workflow_concurrency_and_hygiene`**:
   - Checks `.github/workflows/` for concurrency protection:
     - Confirms concurrency groups (e.g., `concurrency: group: readme-widgets`) or safe rebase/push patterns (`git pull --rebase origin main`, `|| exit 0` on empty commits).
     - Confirms cron schedule dispersion (jobs do not trigger simultaneously on the same minute, preventing worker lock contention).

3. **`test_tier4_external_url_reachability_with_bot_tolerance`**:
   - Traverses every unique HTTP/HTTPS link in `README.md`.
   - Probes endpoints with standard browser `User-Agent`.
   - Tolerance Matrix:
     - HTTP 200, 301, 302, 307, 308: **PASS**
     - HTTP 403 / 429 on bot-protected platforms (LinkedIn, Facebook, TryHackMe): **TOLERATED** (classified as anti-bot challenge; verifies DNS resolution and server uptime).
     - HTTP 404, 410, 500, or DNS failure: **FAIL**
     - Critical Google Drive certificate URLs: **STRICT HTTP 200 REQUIRED**.

---

## 4. Progressive Testability Matrix

To maintain progressive testability during milestone rollout, the test runner operates in two modes:

| Test Target | Baseline / Progressive Mode (`python tests/test_profile_ecosystem.py`) | Strict Mode (`--strict` or `STRICT_E2E=1`) |
|---|---|---|
| **SVG XML Validity (assets & 3d)** | 100% Pass Required (M1) | 100% Pass Required |
| **Header & Footer Contracts** | 100% Pass Required (M1) | 100% Pass Required |
| **Snake Grid Assets** | 100% Pass Required (M1) | 100% Pass Required |
| **7 Core Projects Parity** | Verifies 7 projects in ecosystem; asserts 6 active in README + mcp-agy pin ready (M1 state) or 7 active in README (M2 state). | Strictly asserts exactly 7 projects rendered in `README.md` table. |
| **Camo Cache-Busting** | Validates `?v=...` query presence (e.g. `?v=nature` or `?v=nature_2026`). | Strictly asserts `?v=nature_2026` across all dynamic widget references. |
| **Workflow Concurrency & Git Hygiene** | Validates existing workflow schemas; notes M3 concurrency enhancements. | Strictly asserts concurrency keys in all 3 workflow files. |
| **External URLs Reachability** | Probes all links; validates Google Drive certs = 200; tolerates bot challenges. | Probes all links; validates Google Drive certs = 200; tolerates bot challenges. |

---

## 5. Execution Instructions

### Running the Suite

```bash
# Standard progressive run (exits with code 0)
python tests/test_profile_ecosystem.py

# Running with pytest
pytest tests/test_profile_ecosystem.py -v

# Strict Full-E2E mode (post-M4 audit)
python tests/test_profile_ecosystem.py --strict
```

### Output Format
The test runner provides clean, colorized ANSI console logging, summarizing test progress across all 4 tiers, total test count, elapsed time, and a pass/fail summary matrix.
