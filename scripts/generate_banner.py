#!/usr/bin/env python3
"""Render the profile banners: assets/header.svg and assets/footer.svg.

The artwork is a phyllotaxis spiral. Every seed is placed by one rule -- turn by the
golden angle, step outward by sqrt(n) -- which is the profile's theme: complex, living
structure emerging from a simple rule.

Text is set in Geist and Geist Mono (SIL OFL 1.1, see scripts/fonts/OFL.txt). Each SVG
embeds a WOFF subset holding only the glyphs it uses, because GitHub shows README
images inside an <img> sandbox where external fonts never load.

    python scripts/generate_banner.py
"""
from __future__ import annotations

import base64
import io
import logging
import math
import unicodedata
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

SCRIPTS = Path(__file__).resolve().parent
FONTS = SCRIPTS / "fonts"
ASSETS = SCRIPTS.parent / "assets"

GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))  # 137.508 degrees

BG_TOP = "#05080d"
BG_BOTTOM = "#0a1119"
INK = "#f1f5f9"
SLATE = "#9aa8bb"
SLATE_DIM = "#627187"
CAPTION = "#3d4a5c"
MINT = "#a7f3d0"
EMERALD = "#34d399"
SPIRAL_RAMP = ("#ecfdf5", "#86efac", "#34d399", "#10b981", "#14b8a6", "#22d3ee", "#38bdf8")

SANS = "Geist"
MONO = "Geist Mono"
# Fallbacks keep the layout sane if a renderer ever refuses the embedded fonts.
SANS_STACK = "'Geist','Segoe UI',system-ui,-apple-system,sans-serif"
MONO_STACK = "'Geist Mono',ui-monospace,'Cascadia Mono',Menlo,Consolas,monospace"
FACES = {
    # key: (family, file, weight, style)
    "sans-400": (SANS, "Geist-Regular.ttf", 400, "normal"),
    "sans-500": (SANS, "Geist-Medium.ttf", 500, "normal"),
    "sans-600": (SANS, "Geist-SemiBold.ttf", 600, "normal"),
    "sans-400i": (SANS, "Geist-Italic.ttf", 400, "italic"),
    "mono-400": (MONO, "GeistMono-Regular.ttf", 400, "normal"),
    "mono-500": (MONO, "GeistMono-Medium.ttf", 500, "normal"),
}


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


@lru_cache(maxsize=None)
def load_font(filename: str) -> TTFont:
    return TTFont(FONTS / filename)


def text_width(face: str, text: str, size: float, tracking: float = 0.0) -> float:
    """Advance width of `text` in user units; `tracking` is letter-spacing in em."""
    font = load_font(FACES[face][1])
    cmap, hmtx = font.getBestCmap(), font["hmtx"]
    text = nfc(text)
    units = sum(hmtx[cmap[ord(ch)]][0] for ch in text)
    return units * size / font["head"].unitsPerEm + tracking * size * max(len(text) - 1, 0)


def font_face(face: str, text: str) -> str:
    """@font-face rule embedding a WOFF subset that covers exactly `text`."""
    family, filename, weight, style = FACES[face]
    font = TTFont(FONTS / filename, recalcTimestamp=False)  # byte-stable output
    options = subset.Options()
    options.flavor = "woff"
    options.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk"]
    options.hinting = False
    options.desubroutinize = True
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=nfc(text) + " ")
    subsetter.subset(font)
    buffer = io.BytesIO()
    font.save(buffer)
    data = base64.b64encode(buffer.getvalue()).decode("ascii")
    return (
        f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:{style};"
        f"src:url(data:font/woff;base64,{data}) format('woff')}}"
    )


def mix(colors: tuple[str, ...], t: float) -> str:
    """Sample a multi-stop color ramp at t in [0, 1]."""
    t = min(max(t, 0.0), 1.0) * (len(colors) - 1)
    i = min(int(t), len(colors) - 2)
    f = t - i
    a = [int(colors[i][k : k + 2], 16) for k in (1, 3, 5)]
    b = [int(colors[i + 1][k : k + 2], 16) for k in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * f):02x}" for x, y in zip(a, b))


def seeds(cx: float, cy: float, count: int, radius: float) -> list[tuple[float, float, float]]:
    """(x, y, t) for each seed of a phyllotaxis spiral; t runs 0 -> 1 from core to rim."""
    scale = radius / math.sqrt(count)
    points = []
    for n in range(1, count + 1):
        r, a = scale * math.sqrt(n), n * GOLDEN_ANGLE
        points.append((cx + r * math.cos(a), cy + r * math.sin(a), n / count))
    return points


def spiral_markup(points, size_min: float, size_max: float, bands: int) -> list[str]:
    out = []
    for x, y, t in points:
        size = size_min + (size_max - size_min) * t**0.8
        opacity = 0.95 - 0.5 * t**1.6
        band = min(int(t * bands), bands - 1)
        out.append(
            f'<circle class="w{band}" cx="{x:.1f}" cy="{y:.1f}" r="{size:.2f}" '
            f'fill="{mix(SPIRAL_RAMP, t)}" opacity="{opacity:.2f}"/>'
        )
    return out


def smooth_path(points: list[tuple[float, float]]) -> str:
    """Catmull-Rom spline through `points`, written as cubic Bezier segments."""
    d = [f"M{points[0][0]:.1f} {points[0][1]:.1f}"]
    for i in range(len(points) - 1):
        p0 = points[max(i - 1, 0)]
        p1, p2 = points[i], points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    return "".join(d)


def wave_css(bands: int, period: float, step: float) -> str:
    """A brightness wave that ripples outward through the seed bands."""
    rules = [
        f".seeds circle{{animation:wave {period}s ease-in-out infinite}}",
        "@keyframes wave{0%,100%{fill-opacity:.5}40%{fill-opacity:1}}",
    ]
    rules += [f".w{b}{{animation-delay:{b * step:.2f}s}}" for b in range(1, bands)]
    return "".join(rules)


def glow(gid: str, cx: float, cy: float, r: float, color: str, opacity: float) -> str:
    return (
        f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{color}" stop-opacity="{opacity}"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
    )


def drift(dx: float, dy: float, seconds: float) -> str:
    return (
        f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" '
        f'dur="{seconds}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
    )


def spin(cx: float, cy: float, seconds: float, reverse: bool = False) -> str:
    end = -360 if reverse else 360
    return (
        f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" '
        f'to="{end} {cx} {cy}" dur="{seconds}s" repeatCount="indefinite"/>'
    )


def card(width: int, height: int, radius: int, layers: list[str], defs: list[str], css: str,
         title: str, desc: str) -> str:
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="desc">{escape(desc)}</desc>',
            f"<style>{css}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>",
            "<defs>",
            f'<clipPath id="card"><rect width="{width}" height="{height}" rx="{radius}"/></clipPath>',
            '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOTTOM}"/></linearGradient>',
            '<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
            '<circle cx="11" cy="11" r="0.9" fill="#fff" fill-opacity=".07"/></pattern>',
            *defs,
            "</defs>",
            '<g clip-path="url(#card)">',
            f'<rect width="{width}" height="{height}" fill="url(#bg)"/>',
            *layers,
            "</g>",
            f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="{radius - 0.5}" '
            'fill="none" stroke="#fff" stroke-opacity=".09"/>',
            "</svg>",
            "",
        ]
    )


# --------------------------------------------------------------------------- header

def build_header() -> str:
    width, height = 1200, 340
    cx, cy, radius, count, bands = 1046, 170, 300, 900, 10
    x0 = 76

    pill = "HANOI, VIETNAM · FPT UNIVERSITY"
    name = "Nguyễn Anh Dương"
    role_accent, role_rest = "AI Engineer", " — Agentic Systems & Artificial Life"
    tagline = "Agents that remember, reason and act — and worlds that evolve."
    stack = "rust · python · typescript · mcp · llama.cpp · bevy"
    caption = f"golden angle 137.508° · n = {count}"
    caption_w = text_width("mono-400", caption, 10.5, 0.06)

    points = seeds(cx, cy, count, radius)

    # Spiral arms: every 34th seed lines up along one parastichy (34 is a Fibonacci number).
    arms = [smooth_path([(x, y) for x, y, _ in points[start - 1 :: 34]]) for start in (60, 75, 88)]

    pill_size, pill_tracking = 12, 0.16
    pill_w = 32 + text_width("mono-500", pill, pill_size, pill_tracking) + 16
    stack_w = text_width("mono-400", "› " + stack, 13.5)

    css = "".join(
        [
            font_face("sans-600", name),
            font_face("sans-500", role_accent + role_rest),
            font_face("sans-400", tagline),
            font_face("mono-500", pill),
            font_face("mono-400", "› " + stack + caption),
            f".pill{{font:500 {pill_size}px {MONO_STACK};letter-spacing:{pill_tracking}em;fill:{MINT}}}",
            f".name{{font:600 72px {SANS_STACK};letter-spacing:-.03em}}",
            f".role{{font:500 24px {SANS_STACK};letter-spacing:-.01em;fill:{INK}}}",
            f".tag{{font:400 17.5px {SANS_STACK};fill:{SLATE}}}",
            f".stack{{font:400 13.5px {MONO_STACK};fill:{SLATE_DIM}}}",
            f".cap{{font:400 10.5px {MONO_STACK};letter-spacing:.06em;fill:{SLATE_DIM}}}",
            wave_css(bands, 6, 0.28),
            "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.cursor{animation:blink 1.1s steps(1) infinite}",
            "@keyframes ping{0%{transform:scale(1);opacity:.7}100%{transform:scale(3.2);opacity:0}}"
            ".ping{transform-box:fill-box;transform-origin:center;animation:ping 2.4s ease-out infinite}",
        ]
    )

    defs = [
        glow("gSpiral", cx, cy, 360, "#10b981", 0.30),
        glow("gCyan", 1160, -30, 330, "#22d3ee", 0.15),
        glow("gBlue", 150, 400, 430, "#3b82f6", 0.10),
        glow("gName", 300, 70, 320, "#34d399", 0.06),
        glow("gCore", cx, cy, 110, "#a7f3d0", 0.22),
        glow("halo", 0, 0, 10, "#d1fae5", 0.9),
        f'<radialGradient id="armFade" cx="{cx}" cy="{cy}" r="{radius}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{MINT}" stop-opacity=".55"/>'
        f'<stop offset=".7" stop-color="{EMERALD}" stop-opacity=".22"/>'
        '<stop offset="1" stop-color="#14b8a6" stop-opacity="0"/></radialGradient>',
        '<radialGradient id="gridFade" cx="380" cy="170" r="600" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        '<linearGradient id="spiralFadeX" x1="700" y1="0" x2="880" y2="0" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>',
        f'<mask id="spiralMask"><rect width="{width}" height="{height}" fill="url(#spiralFadeX)"/></mask>',
        f'<mask id="gridMask"><rect width="{width}" height="{height}" fill="url(#gridFade)"/></mask>',
        '<linearGradient id="nameFill" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#ffffff"/><stop offset=".65" stop-color="{INK}"/>'
        f'<stop offset="1" stop-color="{MINT}"/></linearGradient>',
        '<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{EMERALD}"/><stop offset="1" stop-color="#22d3ee"/></linearGradient>',
        '<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset=".35" stop-color="#a7f3d0" stop-opacity="0"/>'
        '<stop offset=".78" stop-color="#a7f3d0" stop-opacity=".6"/>'
        '<stop offset="1" stop-color="#a7f3d0" stop-opacity="0"/></linearGradient>',
    ]

    signals = []
    for i, d in enumerate(arms):
        begin = f"{i * 2.1:.1f}s"
        signals.append(
            '<g opacity="0">'
            '<circle r="10" fill="url(#halo)"/><circle r="2.4" fill="#f0fdf4"/>'
            f'<animateMotion path="{d}" dur="6.3s" begin="{begin}" repeatCount="indefinite" '
            'calcMode="spline" keyTimes="0;1" keySplines=".35 0 .25 1"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.15;.8;1" dur="6.3s" '
            f'begin="{begin}" repeatCount="indefinite"/>'
            "</g>"
        )

    big = f'x="-200" y="-200" width="{width + 400}" height="{height + 400}"'
    layers = [
        '<rect width="100%" height="100%" fill="url(#gName)"/>',
        f'<g><rect {big} fill="url(#gCyan)"/>{drift(-40, 18, 17)}</g>',
        f'<g><rect {big} fill="url(#gBlue)"/>{drift(50, -14, 21)}</g>',
        '<rect width="100%" height="100%" fill="url(#gSpiral)"/>',
        '<rect width="100%" height="100%" fill="url(#gCore)"/>',
        f'<rect width="{width}" height="{height}" fill="url(#dots)" mask="url(#gridMask)"/>',
        f'<g><circle cx="{cx}" cy="{cy}" r="{radius + 26}" fill="none" stroke="{MINT}" stroke-opacity=".14" '
        f'stroke-dasharray="1 7" stroke-linecap="round"/>{spin(cx, cy, 240, reverse=True)}</g>',
        '<g mask="url(#spiralMask)"><g>',
        *[f'<path d="{d}" fill="none" stroke="url(#armFade)" stroke-width="1.1"/>' for d in arms],
        '<g class="seeds">',
        *spiral_markup(points, 1.7, 4.0, bands),
        "</g>",
        *signals,
        spin(cx, cy, 150),
        "</g></g>",
        f'<rect x="{x0}" y="60" width="{pill_w:.1f}" height="30" rx="15" fill="#10b981" fill-opacity=".09" '
        'stroke="#34d399" stroke-opacity=".32"/>',
        f'<circle class="ping" cx="{x0 + 17}" cy="75" r="3.5" fill="{EMERALD}"/>',
        f'<circle cx="{x0 + 17}" cy="75" r="3.5" fill="{EMERALD}"/>',
        f'<text class="pill" x="{x0 + 32}" y="79.3">{escape(pill)}</text>',
        f'<text class="name" x="{x0 - 3}" y="170" fill="url(#nameFill)">{escape(name)}</text>',
        f'<text class="role" x="{x0}" y="214"><tspan fill="url(#accent)">{escape(role_accent)}</tspan>'
        f"{escape(role_rest)}</text>",
        f'<text class="tag" x="{x0}" y="248">{escape(tagline)}</text>',
        f'<text class="stack" x="{x0}" y="296"><tspan fill="{EMERALD}">›</tspan> {escape(stack)}</text>',
        f'<rect class="cursor" x="{x0 + stack_w + 6:.1f}" y="284.5" width="7.5" height="15" rx="1" '
        f'fill="{EMERALD}" fill-opacity=".85"/>',
        f'<rect x="{width - 38 - caption_w - 14:.1f}" y="{height - 46}" width="{caption_w + 28:.1f}" height="24" rx="12" '
        'fill="#05080d" fill-opacity=".78" stroke="#fff" stroke-opacity=".08"/>',
        f'<text class="cap" x="{width - 38}" y="{height - 30.2}" text-anchor="end">{escape(caption)}</text>',
        f'<rect width="{width}" height="1.5" fill="url(#edge)"/>',
    ]

    return card(
        width, height, 22, layers, defs, css,
        title=f"{name} — AI Engineer",
        desc="Nguyễn Anh Dương, AI Engineer building agentic systems and artificial life, "
        "beside a slowly turning phyllotaxis spiral.",
    )


# --------------------------------------------------------------------------- footer

def build_footer() -> str:
    width, height = 1200, 150
    cx, cy, radius, count, bands = 96, 75, 48, 160, 6
    x0 = 178

    quote = "In nature as in code, complex intelligence emerges from simple, elegant rules."
    sign = "— NGUYỄN ANH DƯƠNG · THANKS FOR STOPPING BY"

    css = "".join(
        [
            font_face("sans-400i", quote),
            font_face("mono-400", sign),
            f".quote{{font:italic 400 21px {SANS_STACK};letter-spacing:-.005em;fill:{INK}}}",
            f".sign{{font:400 11.5px {MONO_STACK};letter-spacing:.16em;fill:{SLATE_DIM}}}",
            wave_css(bands, 6, 0.35),
        ]
    )
    defs = [
        glow("gSeed", cx, cy, 230, "#10b981", 0.22),
        glow("gRight", 1150, 170, 300, "#22d3ee", 0.08),
        '<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#a7f3d0" stop-opacity="0"/>'
        '<stop offset=".22" stop-color="#a7f3d0" stop-opacity=".5"/>'
        '<stop offset=".6" stop-color="#a7f3d0" stop-opacity="0"/></linearGradient>',
    ]
    layers = [
        '<rect width="100%" height="100%" fill="url(#gSeed)"/>',
        '<rect width="100%" height="100%" fill="url(#gRight)"/>',
        f'<rect width="{width}" height="{height}" fill="url(#dots)" opacity=".6"/>',
        '<g class="seeds">',
        *spiral_markup(seeds(cx, cy, count, radius), 0.45, 2.0, bands),
        spin(cx, cy, 90),
        "</g>",
        f'<text class="quote" x="{x0}" y="72">{escape(quote)}</text>',
        f'<text class="sign" x="{x0}" y="104">{escape(sign)}</text>',
        f'<rect y="{height - 1.5}" width="{width}" height="1.5" fill="url(#edge)"/>',
    ]
    return card(
        width, height, 22, layers, defs, css,
        title=quote,
        desc="Footer: a quote beside a small phyllotaxis spiral.",
    )



# --------------------------------------------------------------------------- project cards

CARDS = (
    {
        "slug": "liva",
        "kicker": "LOCAL-FIRST AI ASSISTANT",
        "title": "LIVA",
        "desc": "Desktop voice and vision assistant. A Rust core runs llama.cpp in-process, "
        "with hybrid sqlite-vec + FTS5 memory.",
        "chips": ("18 ms TTFT on GPU", "650+ Rust tests", "Vietnamese ASR"),
        "tags": "rust · tokio · tauri v2 · vue 3",
    },
    {
        "slug": "mindsync",
        "kicker": "TEAM LEAD · VAIC 2026 NATIONAL FINAL",
        "title": "MindSync",
        "desc": "AI assistant for Vietnamese public services: finds the procedure, lists the legal "
        "documents, blocks invalid filings.",
        "chips": ("48-hour build", "rule engine", "138 tests · CI"),
        "tags": "next.js 16 · prisma · postgresql · fpt ai",
    },
    {
        "slug": "anima",
        "kicker": "ARTIFICIAL LIFE",
        "title": "Anima Engine",
        "desc": "Deterministic ecosystem simulator: terrain, hydrology, predator–prey ecology "
        "and MAP-Elites evolution.",
        "chips": ("seeded replay", "zero-alloc ticks", "877 Rust tests"),
        "tags": "rust · bevy_ecs · burn · three.js",
    },
    {
        "slug": "mcp-agy",
        "kicker": "AGENT TOOLING · MCP",
        "title": "mcp-agy",
        "desc": "MCP server that lets Claude Code, Cursor or Cline hand coding jobs to a "
        "Google Antigravity worker.",
        "chips": ("9 tools", "467 tests", "workspace locks"),
        "tags": "python · fastmcp · pydantic",
    },
)


def wrap(face: str, text: str, size: float, max_width: float) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if line and text_width(face, candidate, size) > max_width:
            lines.append(line)
            line = word
        else:
            line = candidate
    return lines + [line]


def build_card(spec: dict) -> str:
    width, height = 600, 236
    x0 = 32
    mx, my = width - 68, 60  # spiral motif

    desc = wrap("sans-400", spec["desc"], 16, width - 2 * x0)
    chip_size = 12.5
    chips, x = [], x0
    for label in spec["chips"]:
        w = text_width("mono-500", label, chip_size) + 22
        chips.append(
            f'<rect x="{x:.1f}" y="160" width="{w:.1f}" height="27" rx="13.5" fill="#10b981" '
            'fill-opacity=".08" stroke="#34d399" stroke-opacity=".28"/>'
            f'<text class="chip" x="{x + 11:.1f}" y="177.8">{escape(label)}</text>'
        )
        x += w + 8

    css = "".join(
        [
            font_face("sans-600", spec["title"]),
            font_face("sans-400", spec["desc"]),
            font_face("mono-500", spec["kicker"] + "".join(spec["chips"])),
            font_face("mono-400", spec["tags"] + "↗"),
            f".kick{{font:500 11px {MONO_STACK};letter-spacing:.16em;fill:{MINT}}}",
            f".title{{font:600 31px {SANS_STACK};letter-spacing:-.025em;fill:{INK}}}",
            f".desc{{font:400 16px {SANS_STACK};fill:{SLATE}}}",
            f".chip{{font:500 {chip_size}px {MONO_STACK};fill:#c9f5e4}}",
            f".tags{{font:400 12.5px {MONO_STACK};fill:{SLATE_DIM}}}",
            f".arrow{{font:400 17px {MONO_STACK};fill:{EMERALD}}}",
            wave_css(5, 6, 0.4),
        ]
    )
    defs = [
        glow("gMotif", mx, my, 190, "#10b981", 0.22),
        glow("gLow", 40, height + 40, 260, "#3b82f6", 0.07),
    ]
    layers = [
        '<rect width="100%" height="100%" fill="url(#gMotif)"/>',
        '<rect width="100%" height="100%" fill="url(#gLow)"/>',
        f'<rect width="{width}" height="{height}" fill="url(#dots)" opacity=".55"/>',
        '<g class="seeds">',
        *spiral_markup(seeds(mx, my, 110, 36), 0.6, 2.0, 5),
        spin(mx, my, 80),
        "</g>",
        f'<text class="kick" x="{x0}" y="46">{escape(spec["kicker"])}</text>',
        f'<text class="title" x="{x0 - 1}" y="88">{escape(spec["title"])}</text>',
        *[f'<text class="desc" x="{x0}" y="{120 + 22 * i}">{escape(line)}</text>' for i, line in enumerate(desc[:2])],
        *chips,
        f'<text class="tags" x="{x0}" y="{height - 22}">{escape(spec["tags"])}</text>',
        f'<text class="arrow" x="{width - 30}" y="{height - 20}" text-anchor="end">↗</text>',
    ]
    if len(desc) > 2:
        raise ValueError(f"{spec['slug']}: description wraps to {len(desc)} lines; shorten it")
    return card(
        width, height, 18, layers, defs, css,
        title=f"{spec['title']} — {spec['desc']}",
        desc=" · ".join(spec["chips"]),
    )


def main() -> None:
    logging.getLogger("fontTools.subset").setLevel(logging.ERROR)
    ASSETS.mkdir(exist_ok=True)
    outputs = [("header.svg", build_header()), ("footer.svg", build_footer())]
    outputs += [(f"card-{spec['slug']}.svg", build_card(spec)) for spec in CARDS]
    for filename, svg in outputs:
        path = ASSETS / filename
        path.write_text(svg, encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(SCRIPTS.parent)} ({len(svg.encode('utf-8')) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
