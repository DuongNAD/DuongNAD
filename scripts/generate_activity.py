#!/usr/bin/env python3
"""Render assets/activity-graph.svg: daily GitHub contributions over the last month.

Replaces the third-party activity-graph widget, whose Vercel deployment answers 402. The
numbers come from assets/activity.json (scripts/fetch-activity.py, GitHub GraphQL API).
Styling, fonts and helpers come from generate_banner.py, like the highlights panel.

    python scripts/fetch-activity.py        # refresh the daily counts (needs GITHUB_TOKEN)
    python scripts/generate_activity.py     # this graph
"""
from __future__ import annotations

import datetime
import json
import logging
import math
from pathlib import Path
from xml.sax.saxutils import escape

from generate_banner import (
    ASSETS, BG_BOTTOM, EMERALD, INK, MINT, MONO_STACK, SANS_STACK, SLATE, SLATE_DIM,
    card, font_face, glow, text_width,
)
from generate_highlights import CYAN

WIDTH, HEIGHT = 840, 320
X0 = 32
PLOT_LEFT, PLOT_RIGHT = X0 + 30, WIDTH - X0
PLOT_TOP, PLOT_BOTTOM = 112, 272
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def read_activity(assets: Path = ASSETS) -> list[tuple[datetime.date, int]]:
    raw = json.loads((assets / "activity.json").read_text(encoding="utf-8"))
    days = sorted((datetime.date.fromisoformat(day), int(count)) for day, count in raw.items())
    if len(days) < 2:
        raise ValueError("activity.json needs at least two days to draw a line")
    if any(count < 0 for _, count in days):
        raise ValueError("activity.json holds a negative contribution count")
    return days


def nice_scale(peak: int) -> tuple[int, int]:
    """(step, top) for a y axis with at most four grid intervals that still contains `peak`."""
    magnitude = 1
    while True:
        for multiple in (1, 2, 5):
            step = magnitude * multiple
            if peak <= 4 * step:
                return step, step * max(math.ceil(peak / step), 1)
        magnitude *= 10


def monotone_path(points: list[tuple[float, float]]) -> str:
    """Monotone cubic through `points`: smooth, and it never dips below a zero day."""
    n = len(points)
    h = [points[i + 1][0] - points[i][0] for i in range(n - 1)]
    d = [(points[i + 1][1] - points[i][1]) / h[i] for i in range(n - 1)]
    m = [d[0]] + [0.0] * (n - 2) + [d[-1]]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    path = [f"M{points[0][0]:.1f} {points[0][1]:.1f}"]
    for i in range(n - 1):
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        c1 = (x0 + h[i] / 3, y0 + m[i] * h[i] / 3)
        c2 = (x1 - h[i] / 3, y1 - m[i + 1] * h[i] / 3)
        path.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {x1:.1f} {y1:.1f}")
    return "".join(path)


def short_date(day: datetime.date) -> str:
    return f"{MONTHS[day.month - 1]} {day.day}"


def build_activity(days: list[tuple[datetime.date, int]]) -> str:
    n = len(days)
    counts = [count for _, count in days]
    total, active = sum(counts), sum(1 for count in counts if count)
    peak, peak_day = max((count, day) for day, count in days)
    peak_index = next(i for i, (day, _) in enumerate(days) if day == peak_day)
    step, top = nice_scale(peak)

    span_x, span_y = PLOT_RIGHT - PLOT_LEFT, PLOT_BOTTOM - PLOT_TOP
    points = [
        (PLOT_LEFT + i * span_x / (n - 1), PLOT_BOTTOM - count / top * span_y)
        for i, count in enumerate(counts)
    ]
    line = monotone_path(points)
    area = f"{line}L{points[-1][0]:.1f} {PLOT_BOTTOM}L{points[0][0]:.1f} {PLOT_BOTTOM}Z"

    kicker = "CONTRIBUTION ACTIVITY"
    caption = f"last {n} days · refreshed daily"
    summary = (
        (f"{total:,}", "contributions"),
        (f"{active}", "active days"),
        (f"{peak}", f"best day · {short_date(peak_day)}"),
    )
    value_size, label_size, group_gap = 22, 12, 28
    row_width = sum(
        text_width("sans-600", value, value_size) + 6 + text_width("sans-400", label, label_size)
        for value, label in summary
    ) + group_gap * (len(summary) - 1)
    if row_width > WIDTH - 2 * X0:
        raise ValueError(f"summary row is {row_width:.0f}px wide but only {WIDTH - 2 * X0} fit")

    layers = [
        '<rect width="100%" height="100%" fill="url(#gHero)"/>',
        '<rect width="100%" height="100%" fill="url(#gLow)"/>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#dots)" opacity=".55"/>',
        f'<text class="kick" x="{X0}" y="40">{kicker}</text>',
        f'<text class="cap" x="{WIDTH - X0}" y="40" text-anchor="end">{escape(caption)}</text>',
    ]

    x = float(X0)
    for value, label in summary:
        value_w = text_width("sans-600", value, value_size)
        layers += [
            f'<text class="sv" x="{x:.1f}" y="80">{escape(value)}</text>',
            f'<text class="sl" x="{x + value_w + 6:.1f}" y="80">{escape(label)}</text>',
        ]
        x += value_w + 6 + text_width("sans-400", label, label_size) + group_gap

    # Y grid and labels.
    ticks = []
    for value in range(0, top + 1, step):
        y = PLOT_BOTTOM - value / top * span_y
        ticks.append(str(value))
        opacity = ".16" if value == 0 else ".07"
        layers += [
            f'<line x1="{PLOT_LEFT}" x2="{PLOT_RIGHT}" y1="{y:.1f}" y2="{y:.1f}" '
            f'stroke="#fff" stroke-opacity="{opacity}"/>',
            f'<text class="tick" x="{PLOT_LEFT - 10}" y="{y + 3.5:.1f}" text-anchor="end">{value}</text>',
        ]

    # X labels: every seventh day counting back from today, so the latest date is always shown.
    dates = []
    for i in range(n - 1, -1, -7):
        label = short_date(days[i][0])
        dates.append(label)
        layers.append(
            f'<text class="tick" x="{points[i][0]:.1f}" y="{PLOT_BOTTOM + 24}" '
            f'text-anchor="middle">{label}</text>'
        )

    layers += [
        f'<path d="{area}" fill="url(#aFill)"/>',
        f'<path d="{line}" fill="none" stroke="url(#aLine)" stroke-width="2.4" '
        'stroke-linecap="round" stroke-linejoin="round"/>',
    ]
    for i, (px, py) in enumerate(points):
        if i == peak_index or i == n - 1:
            continue
        if counts[i]:
            layers.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.8" fill="{BG_BOTTOM}" '
                f'stroke="{EMERALD}" stroke-width="1.4"/>'
            )
        else:
            layers.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.8" fill="{SLATE_DIM}" opacity=".7"/>')

    # Latest day, then the best day on top; they coincide when today is the peak.
    last_x, last_y = points[-1]
    peak_x, peak_y = points[peak_index]
    if peak_index != n - 1:
        layers += [
            f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="9" fill="{CYAN}" opacity=".18"/>',
            f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="4" fill="{CYAN}"/>',
        ]
    peak_w = text_width("mono-500", str(peak), 11)
    label_x = min(max(peak_x, PLOT_LEFT + peak_w / 2), WIDTH - 8 - peak_w / 2)
    layers += [
        f'<circle class="pulse" cx="{peak_x:.1f}" cy="{peak_y:.1f}" r="10" fill="{EMERALD}" opacity=".3"/>',
        f'<circle cx="{peak_x:.1f}" cy="{peak_y:.1f}" r="5" fill="{MINT}"/>',
        f'<text class="pk" x="{label_x:.1f}" y="{peak_y - 16:.1f}" text-anchor="middle">{peak}</text>',
    ]

    faces = {
        "mono-500": f"{kicker} {caption} {peak}",
        "mono-400": " ".join([*ticks, *dates]),
        "sans-600": " ".join(value for value, _ in summary),
        "sans-400": " ".join(label for _, label in summary),
    }
    css = "".join(
        [
            *(font_face(face, text) for face, text in faces.items()),
            f".kick{{font:500 11px {MONO_STACK};letter-spacing:.16em;fill:{MINT}}}",
            f".cap{{font:500 11px {MONO_STACK};letter-spacing:.06em;fill:{SLATE_DIM}}}",
            f".sv{{font:600 {value_size}px {SANS_STACK};letter-spacing:-.02em;fill:{INK}}}",
            f".sl{{font:400 {label_size}px {SANS_STACK};fill:{SLATE}}}",
            f".tick{{font:400 10.5px {MONO_STACK};fill:{SLATE_DIM}}}",
            f".pk{{font:500 11px {MONO_STACK};fill:{INK}}}",
            ".pulse{animation:pulse 3.2s ease-in-out infinite;transform-box:fill-box;"
            "transform-origin:center}",
            "@keyframes pulse{0%,100%{opacity:.12;transform:scale(.8)}50%{opacity:.4;transform:scale(1.15)}}",
        ]
    )
    defs = [
        glow("gHero", X0 + 60, 40, 340, "#10b981", 0.16),
        glow("gLow", WIDTH, HEIGHT, 320, CYAN, 0.07),
        '<linearGradient id="aFill" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#10b981" stop-opacity=".32"/>'
        '<stop offset="1" stop-color="#10b981" stop-opacity="0"/></linearGradient>',
        f'<linearGradient id="aLine" gradientUnits="userSpaceOnUse" x1="{PLOT_LEFT}" y1="0" '
        f'x2="{PLOT_RIGHT}" y2="0"><stop offset="0" stop-color="{EMERALD}"/>'
        f'<stop offset="1" stop-color="{CYAN}"/></linearGradient>',
    ]
    return card(
        WIDTH, HEIGHT, 18, layers, defs, css,
        title=f"Contribution activity over the last {n} days",
        desc=f"Daily GitHub contributions from {days[0][0]} to {days[-1][0]}: {total} in total on "
        f"{active} active days, best day {peak} on {short_date(peak_day)}.",
    )


def main() -> None:
    logging.getLogger("fontTools.subset").setLevel(logging.ERROR)
    svg = build_activity(read_activity())
    path = ASSETS / "activity-graph.svg"
    path.write_text(svg, encoding="utf-8", newline="\n")
    print(f"wrote {path.relative_to(ASSETS.parent)} ({len(svg.encode('utf-8')) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
