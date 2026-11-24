#!/usr/bin/env python3
"""Render assets/stats-{dark,light}.svg: the profile's GitHub numbers and trophy ranks.

The numbers come from assets/stats.json (scripts/fetch-stats.py, GitHub GraphQL API); the
daily workflow refreshes both. Palettes, fonts and helpers come from generate_banner.py, so
the panel matches the activity graph below it and the cards above it in either GitHub theme.

    python scripts/fetch-stats.py        # refresh the numbers (needs GITHUB_TOKEN)
    python scripts/generate_stats.py     # this panel
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from xml.sax.saxutils import escape

from generate_banner import (
    ASSETS, AWARD_GLYPHS, MONO_STACK, SANS_STACK, THEMES,
    document, fit, fonts_css, glow, panel, panel_edge, text_width,
)

WIDTH, HEIGHT = 840, 324
X0 = 32
COLUMNS = 4
COL_W = (WIDTH - 2 * X0) / COLUMNS

FIELDS = (
    "stars", "commits", "pull_requests", "contributions",
    "repositories", "followers", "current_streak", "best_streak",
)
# (field, label, glyph, unit) in reading order, four per row.
METRICS = (
    ("stars", "STARS", "star", ""),
    ("commits", "COMMITS", "commit", ""),
    ("pull_requests", "PULL REQUESTS", "pull", ""),
    ("contributions", "CONTRIBUTIONS", "grid", ""),
    ("repositories", "PUBLIC REPOS", "repo", ""),
    ("followers", "FOLLOWERS", "people", ""),
    ("current_streak", "CURRENT STREAK", "flame", "days"),
    ("best_streak", "BEST STREAK", "trophy", "days"),
)

# Trophies rank a number against eight milestones, from C (the first) to SSS (the last).
RANKS = ("C", "B", "A", "AA", "AAA", "S", "SS", "SSS")
TROPHIES = (
    ("Stargazer", "stars", "stars", (1, 10, 30, 50, 100, 200, 500, 1000)),
    ("Deep Committer", "commits", "commits", (1, 100, 250, 500, 1000, 2000, 5000, 10000)),
    ("Hyper Puller", "pull_requests", "pull requests", (1, 10, 25, 50, 100, 250, 500, 1000)),
    ("Streak Keeper", "best_streak", "day streak", (1, 3, 7, 14, 30, 60, 100, 365)),
)

# Octicons (MIT): star and git-pull-request, 16 px.
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
LINE = 'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"'
# 16x16 glyphs drawn in currentColor.
GLYPHS = {
    "star": f'<path fill-rule="evenodd" d="{STAR_PATH}"/>',
    "pull": f'<path fill-rule="evenodd" d="{PULL_PATH}"/>',
    "commit": f'<circle cx="8" cy="8" r="3" {LINE}/><path d="M1 8h4M11 8h4" {LINE}/>',
    "grid": "".join(
        f'<rect x="{x}" y="{y}" width="5.5" height="5.5" rx="1.3" fill-opacity="{o}"/>'
        for x, y, o in ((1.5, 1.5, ".45"), (9, 1.5, "1"), (1.5, 9, "1"), (9, 9, ".7"))
    ),
    "repo": f'<path d="M3 13.5V3.2A1.7 1.7 0 0 1 4.7 1.5H13v10H4.7A1.7 1.7 0 0 0 3 13.2a1.3 1.3 0 0 0 '
            f'1.3 1.3H6M9 14.5h4v-3" {LINE}/>',
    "people": f'<circle cx="8" cy="5" r="2.8" {LINE}/><path d="M2.5 14.5a5.5 5.5 0 0 1 11 0" {LINE}/>',
    "flame": '<path d="M8 .8c.4 2.4 1.9 3.6 3.2 5a5 5 0 0 1 1.3 3.5A4.5 4.5 0 0 1 8 14.8a4.5 4.5 0 0 1-4.5-4.6'
             'c0-1.6.8-2.8 1.8-3.7.1 1.2.6 2 1.4 2.3C6.3 6.4 6.8 3.2 8 .8z"/>',
    "trophy": AWARD_GLYPHS["trophy"],
}


def read_stats(assets: Path = ASSETS) -> dict[str, int]:
    raw = json.loads((assets / "stats.json").read_text(encoding="utf-8"))
    missing = [field for field in FIELDS if field not in raw]
    if missing:
        raise ValueError(f"stats.json is missing {', '.join(missing)}")
    stats = {field: int(raw[field]) for field in FIELDS}
    if any(value < 0 for value in stats.values()):
        raise ValueError("stats.json holds a negative number")
    if stats["current_streak"] > stats["best_streak"]:
        raise ValueError("the current streak cannot be longer than the best streak")
    return stats


def number(value: int) -> str:
    return f"{value:,}" if value < 100_000 else f"{value / 1000:,.0f}k"


def rank(value: int, milestones: tuple[int, ...]) -> int | None:
    """Index into RANKS of the highest milestone `value` reaches, or None below the first."""
    reached = [i for i, milestone in enumerate(milestones) if value >= milestone]
    return reached[-1] if reached else None


def glyph(name: str, x: float, y: float, color: str, scale: float = 0.875) -> str:
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) scale({scale})" fill="{color}" color="{color}">'
        f"{GLYPHS[name]}</g>"
    )


def build_stats(stats: dict[str, int], theme_name: str) -> str:
    theme = THEMES[theme_name]
    kicker, caption = "GITHUB", "public repositories · refreshed daily"
    defs, layers = panel(theme, 0, 0, WIDTH, HEIGHT, 18)
    defs.append(glow("gCorner", WIDTH, 0, 380, theme["glow"], theme["glow_opacity"] * 0.6))
    layers += [
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#gCorner)"/>',
        f'<text class="kick" x="{X0}" y="40">{kicker}</text>',
        f'<text class="cap" x="{WIDTH - X0}" y="40" text-anchor="end">{escape(caption)}</text>',
    ]

    values, units, labels = [], [], []
    for i, (field, label, icon, unit) in enumerate(METRICS):
        row, col = divmod(i, COLUMNS)
        x, top = X0 + col * COL_W, 64 + row * 78
        value = number(stats[field])
        fit("mono-500", label, 10.5, COL_W - 30, 0.12)
        fit("sans-600", value, 30, COL_W - 50)
        values.append(value)
        labels.append(label)
        layers += [
            glyph(icon, x, top + 11, theme["accent"]),
            f'<text class="ml" x="{x + 21:.1f}" y="{top + 22}">{label}</text>',
            f'<text class="mv" x="{x - 1:.1f}" y="{top + 58}">{value}</text>',
        ]
        if unit:
            units.append(unit)
            layers.append(
                f'<text class="mu" x="{x + text_width("sans-600", value, 30) + 6:.1f}" '
                f'y="{top + 58}">{unit}</text>'
            )

    layers.append(
        f'<line x1="{X0}" x2="{WIDTH - X0}" y1="226" y2="226" stroke="{theme["dots"]}" stroke-opacity=".12"/>'
    )

    gap = 12
    badge_w, badge_h, badge_y = (WIDTH - 2 * X0 - gap * (len(TROPHIES) - 1)) / len(TROPHIES), 56, 244
    titles, notes, letters, described = [], [], [], []
    for i, (title, field, noun, milestones) in enumerate(TROPHIES):
        x = X0 + i * (badge_w + gap)
        level = rank(stats[field], milestones)
        letter = RANKS[level] if level is not None else "–"
        note = f"{number(milestones[level])}+ {noun}" if level is not None else f"first {noun.split()[-1]}"
        if level is not None and level >= RANKS.index("S"):
            color = theme["head"]
        elif level is not None and level >= RANKS.index("A"):
            color = theme["accent"]
        else:
            color = theme["dim"]
        fit("sans-500", title, 14.5, badge_w - 66)
        fit("mono-500", note.upper(), 9.5, badge_w - 66, 0.08)
        cx, cy = x + 30, badge_y + badge_h / 2
        titles.append(title)
        notes.append(note.upper())
        letters.append(letter)
        described.append(f"{title} rank {letter} ({note})")
        layers += [
            f'<rect x="{x:.1f}" y="{badge_y}" width="{badge_w:.1f}" height="{badge_h}" rx="12" '
            f'fill="{theme["tint"]}" fill-opacity="{theme["tint_opacity"]}" stroke="{theme["tint_edge"]}" '
            f'stroke-opacity="{theme["tint_edge_opacity"]}"/>',
            f'<circle cx="{cx:.1f}" cy="{cy}" r="17" fill="{color}" fill-opacity=".14" '
            f'stroke="{color}" stroke-opacity=".7" stroke-width="1.4"/>',
            f'<text class="rk" x="{cx:.1f}" y="{cy + 4.5}" text-anchor="middle" fill="{color}">{letter}</text>',
            f'<text class="tt" x="{x + 56:.1f}" y="{cy - 2}">{escape(title)}</text>',
            f'<text class="tn" x="{x + 56:.1f}" y="{cy + 15}">{escape(note.upper())}</text>',
        ]

    layers += ["</g>", panel_edge(theme, 0, 0, WIDTH, HEIGHT, 18)]
    css = "".join(
        [
            fonts_css(
                {
                    "mono-500": " ".join([kicker, caption, *labels, *letters, *notes]),
                    "sans-600": " ".join(values),
                    "sans-500": " ".join(titles),
                    "sans-400": " ".join(units),
                }
            ),
            f".kick{{font:500 11px {MONO_STACK};letter-spacing:.16em;fill:{theme['kicker']}}}",
            f".cap{{font:500 11px {MONO_STACK};letter-spacing:.06em;fill:{theme['dim']}}}",
            f".ml{{font:500 10.5px {MONO_STACK};letter-spacing:.12em;fill:{theme['dim']}}}",
            f".mv{{font:600 30px {SANS_STACK};letter-spacing:-.025em;fill:{theme['ink']}}}",
            f".mu{{font:400 14px {SANS_STACK};fill:{theme['slate']}}}",
            f".rk{{font:500 12.5px {MONO_STACK};letter-spacing:-.04em}}",
            f".tt{{font:500 14.5px {SANS_STACK};fill:{theme['ink']}}}",
            f".tn{{font:500 9.5px {MONO_STACK};letter-spacing:.08em;fill:{theme['dim']}}}",
        ]
    )
    numbers = ", ".join(
        f"{number(stats[field])}{' ' + unit if unit else ''} {label.lower()}" for field, label, _, unit in METRICS
    )
    return document(
        WIDTH, HEIGHT, layers, defs, css,
        title="GitHub stats and trophies",
        desc=f"{numbers}. Trophies: {'; '.join(described)}.",
    )


def build_all(stats: dict[str, int]) -> dict[str, str]:
    return {f"stats-{theme}.svg": build_stats(stats, theme) for theme in THEMES}


def main() -> None:
    logging.getLogger("fontTools.subset").setLevel(logging.ERROR)
    for filename, svg in build_all(read_stats()).items():
        path = ASSETS / filename
        path.write_text(svg, encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(ASSETS.parent)} ({len(svg.encode('utf-8')) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
