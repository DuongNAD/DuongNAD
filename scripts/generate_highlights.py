#!/usr/bin/env python3
"""Render assets/highlights.svg: GitHub stars, key numbers and achievement medals.

The numbers come from files the daily workflow already refreshes: assets/stats.svg and
assets/streak.svg (scripts/fetch-all-widgets.py) and assets/profile-stats.json
(scripts/fetch-profile-stats.py). Styling, fonts and helpers come from generate_banner.py,
which keeps the panel in the same visual language as the header and the project cards.

    python scripts/generate_banner.py          # banners and cards
    python scripts/fetch-all-widgets.py        # refresh stats.svg / streak.svg
    python scripts/fetch-profile-stats.py      # refresh repo and follower counts
    python scripts/generate_highlights.py      # this panel
"""
from __future__ import annotations

import json
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

from generate_banner import (
    ASSETS, EMERALD, INK, MINT, MONO_STACK, SANS_STACK, SLATE, SLATE_DIM,
    card, font_face, glow, text_width,
)

CYAN = "#22d3ee"
WIDTH, HEIGHT = 840, 480
X0 = 32

# Octicons (MIT) that ship inside the stats widget; every other glyph is drawn here.
STAR_PATH = (
    "M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 "
    "4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 "
    "6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25zm0 2.445L6.615 5.5a.75.75 "
    "0 01-.564.41l-3.097.45 2.24 2.184a.75.75 0 01.216.664l-.528 3.084 2.769-1.456a.75.75 0 "
    "01.698 0l2.77 1.456-.53-3.084a.75.75 0 01.216-.664l2.24-2.183-3.096-.45a.75.75 0 "
    "01-.564-.41L8 2.694v.001z"
)
PULL_PATH = (
    "M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 "
    "0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25 2.25 0 113 2.122v5.256a2.251 "
    "2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 "
    "0 101.5 0V5A2.5 2.5 0 0011 2.5zm1 10.25a.75.75 0 111.5 0 .75.75 0 01-1.5 0zM3.75 12a.75.75 "
    "0 100 1.5.75.75 0 000-1.5z"
)
# 16x16 glyphs: (markup, stroked) -- stroked glyphs use the accent as stroke, the rest as fill.
GLYPHS = {
    "trophy": (
        '<path d="M4.5 2h7v4.2a3.5 3.5 0 0 1-7 0z"/><path d="M4.5 3.2H2.8v1.3a2 2 0 0 0 1.9 2M11.5 '
        '3.2h1.7v1.3a2 2 0 0 1-1.9 2" fill="none" stroke="currentColor" stroke-width="1.2"/>'
        '<path d="M7.2 9.6h1.6v2.2H7.2zM5 12h6v1.6H5z"/>'
    ),
    "medal": (
        '<path d="M4.6 1.2 7 6M11.4 1.2 9 6" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round"/><circle cx="8" cy="10" r="4"/>'
    ),
    "flag": (
        '<path d="M3.8 1.5v13" fill="none" stroke="currentColor" stroke-width="1.5" '
        'stroke-linecap="round"/><path d="M4.5 2.4h8.2L10.6 5.6l2.1 3.2H4.5z"/>'
    ),
    "star": f'<path fill-rule="evenodd" d="{STAR_PATH}"/>',
    "commit": (
        '<circle cx="8" cy="8" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/>'
        '<path d="M1 8h4M11 8h4" fill="none" stroke="currentColor" stroke-width="1.5" '
        'stroke-linecap="round"/>'
    ),
    "pull": f'<path fill-rule="evenodd" d="{PULL_PATH}"/>',
}
SPARKLE = "M0-6Q0 0 6 0Q0 0 0 6Q0 0-6 0Q0 0 0-6Z"


def _text(element: ET.Element) -> str:
    return " ".join("".join(element.itertext()).split())


def read_stats(assets: Path = ASSETS) -> dict[str, str]:
    """Pull the displayed numbers out of the refreshed stats and streak widgets."""
    testids = {
        el.get("data-testid"): _text(el)
        for el in ET.parse(assets / "stats.svg").getroot().iter()
        if el.get("data-testid")
    }
    streak = [
        _text(el)
        for el in ET.parse(assets / "streak.svg").getroot().iter()
        if el.tag.rsplit("}", 1)[-1] == "text"
    ]

    def before(label: str) -> str:
        return streak[streak.index(label) - 1]

    stats = {
        "stars": testids.get("stars", ""),
        "commits": testids.get("commits", ""),
        "prs": testids.get("prs", ""),
        "contribs": before("Total Contributions"),
        "streak": before("Longest Streak"),
    }
    profile = json.loads((assets / "profile-stats.json").read_text(encoding="utf-8"))
    stats["repos"] = f"{profile['repos']:,}"
    stats["followers"] = f"{profile['followers']:,}"
    missing = [key for key, value in stats.items() if not value]
    if missing:
        raise ValueError(f"could not read {', '.join(missing)} from the stats widgets")
    return stats


def glyph(name: str, x: float, y: float, size: float, color: str) -> str:
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) scale({size / 16:.3f})" fill="{color}" '
        f'color="{color}">{GLYPHS[name]}</g>'
    )


def fit(face: str, text: str, size: float, limit: float, tracking: float = 0.0) -> None:
    width = text_width(face, text, size, tracking)
    if width > limit:
        raise ValueError(f"{text!r} is {width:.0f}px wide but only {limit:.0f}px fit; shorten it")


def build_highlights(stats: dict[str, str]) -> str:
    stars = stats["stars"]
    medals = (
        ("trophy", EMERALD, "#493 / 3,062", "HackerRank Orchestrate 2026"),
        ("medal", EMERALD, "Top 4 & Promising Award", "DENSO Factory Hacks 2025"),
        ("flag", EMERALD, "Team Lead · MindSync", "VAIC 2026 national final"),
        ("star", CYAN, "Stargazer", f"{stars} GitHub stars"),
        ("commit", CYAN, "Deep Committer", f"{stats['commits']} commits"),
        ("pull", CYAN, "Hyper Puller", f"{stats['prs']} pull requests"),
    )
    # Row-major grid to the right of the star tile: (label, value, unit).
    tiles = (
        ("COMMITS", stats["commits"], ""),
        ("PULL REQUESTS", stats["prs"], ""),
        ("CONTRIBUTIONS", stats["contribs"], ""),
        ("REPOSITORIES", stats["repos"], ""),
        ("FOLLOWERS", stats["followers"], ""),
        ("BEST STREAK", stats["streak"], "days"),
    )

    label_size, label_track = 10.5, 0.1
    num_size, hero_num_size = 34, 60
    gap, tile_h = 12, 78
    col_w = (WIDTH - 2 * X0 - 3 * gap) / 4
    top = 58
    hero_x, hero_y, hero_w, hero_h = X0, top, col_w, 2 * tile_h + gap

    cell_gap, cell_h, cell_step = 16, 52, 62
    cell_w = (WIDTH - 2 * X0 - cell_gap) / 2
    cell_y0 = top + hero_h + 52

    layers = [
        '<rect width="100%" height="100%" fill="url(#gHero)"/>',
        '<rect width="100%" height="100%" fill="url(#gLow)"/>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#dots)" opacity=".55"/>',
        f'<text class="kick" x="{X0}" y="40">BY THE NUMBERS</text>',
        f'<text class="cap" x="{WIDTH - X0}" y="40" text-anchor="end">refreshed daily</text>',
    ]

    # Hero tile: the star count, two rows tall.
    fit("mono-500", "GITHUB STARS", label_size, hero_w - 36, label_track)
    fit("sans-600", stars, hero_num_size, hero_w - 32)
    star_size = 64
    star_x, star_y = hero_x + hero_w - 18 - star_size, hero_y + 38
    layers += [
        f'<rect x="{hero_x}" y="{hero_y}" width="{hero_w:.1f}" height="{hero_h}" rx="18" '
        'fill="url(#heroFill)" stroke="#34d399" stroke-opacity=".5"/>',
        f'<text class="lbl" x="{hero_x + 18}" y="{hero_y + 29}">GITHUB STARS</text>',
        f'<text class="num hero" x="{hero_x + 16}" y="{hero_y + hero_h - 22}">{escape(stars)}</text>',
        glyph("star", star_x, star_y, star_size, MINT),
    ]
    for i, (dx, dy, scale) in enumerate(((-10, 6, 1.1), (4, 74, 0.7), (82, 6, 0.55), (-12, 48, 0.5))):
        layers.append(
            f'<path class="sp" style="animation-delay:{i * 0.8:.1f}s" fill="#ecfdf5" '
            f'transform="translate({star_x + dx:.1f} {star_y + dy:.1f}) scale({scale})" d="{SPARKLE}"/>'
        )

    # The other number tiles.
    for i, (label, value, unit) in enumerate(tiles):
        col, row = i % 3 + 1, i // 3
        x, y = X0 + col * (col_w + gap), top + row * (tile_h + gap)
        fit("mono-500", label, label_size, col_w - 32, label_track)
        number_w = text_width("sans-600", value, num_size)
        fit("sans-600", value, num_size, col_w - 32 - (36 if unit else 0))
        layers += [
            f'<rect x="{x:.1f}" y="{y}" width="{col_w:.1f}" height="{tile_h}" rx="16" '
            'fill="#10b981" fill-opacity=".05" stroke="#34d399" stroke-opacity=".2"/>',
            f'<text class="lbl" x="{x + 16:.1f}" y="{y + 27}">{escape(label)}</text>',
            f'<text class="num" x="{x + 15:.1f}" y="{y + 64}">{escape(value)}</text>',
        ]
        if unit:
            layers.append(f'<text class="unit" x="{x + 15 + number_w + 6:.1f}" y="{y + 64}">{unit}</text>')

    # Achievement medals: competitions on the left, GitHub trophies on the right.
    groups = ("ACHIEVEMENTS · COMPETITIONS", "TROPHIES · ON GITHUB")
    for col, heading in enumerate(groups):
        layers.append(
            f'<text class="kick" x="{X0 + col * (cell_w + cell_gap):.1f}" y="{cell_y0 - 18}">{heading}</text>'
        )
    for i, (icon, accent, title, sub) in enumerate(medals):
        col, row = i // 3, i % 3
        x, y = X0 + col * (cell_w + cell_gap), cell_y0 + row * cell_step
        fit("sans-600", title, 16, cell_w - 62 - 12)
        fit("sans-400", sub, 12, cell_w - 62 - 12)
        cx, cy = x + 32, y + cell_h / 2
        layers += [
            f'<rect x="{x:.1f}" y="{y}" width="{cell_w:.1f}" height="{cell_h}" rx="14" '
            f'fill="{accent}" fill-opacity=".05" stroke="{accent}" stroke-opacity=".22"/>',
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="18" fill="{accent}" fill-opacity=".12" '
            f'stroke="{accent}" stroke-opacity=".55"/>',
            glyph(icon, cx - 10, cy - 10, 20, accent),
            f'<text class="mt" x="{x + 62:.1f}" y="{y + 23}">{escape(title)}</text>',
            f'<text class="ms" x="{x + 62:.1f}" y="{y + 41}">{escape(sub)}</text>',
        ]

    faces = {
        "sans-600": " ".join([stars, *(t[1] for t in tiles), *(m[2] for m in medals)]),
        "sans-400": " ".join(m[3] for m in medals) + " days",
        "mono-500": "BY THE NUMBERS GITHUB STARS refreshed daily " + " ".join(groups) + " "
        + " ".join(t[0] for t in tiles),
    }
    css = "".join(
        [
            *(font_face(face, text) for face, text in faces.items()),
            f".kick{{font:500 11px {MONO_STACK};letter-spacing:.16em;fill:{MINT}}}",
            f".cap{{font:500 11px {MONO_STACK};letter-spacing:.06em;fill:{SLATE_DIM}}}",
            f".lbl{{font:500 {label_size}px {MONO_STACK};letter-spacing:{label_track}em;fill:{SLATE}}}",
            f".num{{font:600 {num_size}px {SANS_STACK};letter-spacing:-.025em;fill:{INK}}}",
            f".hero{{font-size:{hero_num_size}px}}",
            f".unit{{font:400 13px {SANS_STACK};fill:{SLATE_DIM}}}",
            f".mt{{font:600 16px {SANS_STACK};letter-spacing:-.01em;fill:{INK}}}",
            f".ms{{font:400 12px {SANS_STACK};fill:{SLATE}}}",
            ".sp{animation:twinkle 3.2s ease-in-out infinite;transform-box:fill-box;"
            "transform-origin:center}",
            "@keyframes twinkle{0%,100%{opacity:.15}50%{opacity:1}}",
        ]
    )
    defs = [
        glow("gHero", hero_x + 70, hero_y + 80, 320, "#10b981", 0.22),
        glow("gLow", WIDTH, HEIGHT, 340, "#22d3ee", 0.08),
        '<linearGradient id="heroFill" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#10b981" stop-opacity=".22"/>'
        '<stop offset="1" stop-color="#10b981" stop-opacity=".05"/></linearGradient>',
    ]
    return card(
        WIDTH, HEIGHT, 18, layers, defs, css,
        title="GitHub stars and achievements",
        desc=f"{stars} GitHub stars, {stats['commits']} commits, {stats['prs']} pull requests, "
        f"{stats['contribs']} contributions, {stats['repos']} repositories, {stats['followers']} followers, "
        f"best streak {stats['streak']} days. " + "; ".join(f"{m[2]} - {m[3]}" for m in medals),
    )


def main() -> None:
    logging.getLogger("fontTools.subset").setLevel(logging.ERROR)
    svg = build_highlights(read_stats())
    path = ASSETS / "highlights.svg"
    path.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {path.relative_to(ASSETS.parent)} ({len(svg.encode('utf-8')) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
