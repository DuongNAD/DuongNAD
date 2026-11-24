#!/usr/bin/env python3
"""Render the static profile artwork, once per GitHub theme.

    assets/header-{dark,light}.svg         name and role beside a phyllotaxis spiral
    assets/card-<slug>-{dark,light}.svg    the four project cards, each with its project's logo
                                           (scripts/logos/<slug>.svg) faint in the background
    assets/award-<slug>-{dark,light}.svg   the four achievement tiles

The README shows each pair through <picture>, so a reader on GitHub's light theme gets the
light file and a reader on the dark theme gets the dark one. Cards and tiles are drawn for a
fixed width (IMG_W) that fits two per row in the 846 px profile column; on a phone they wrap
to one per row and stay readable instead of shrinking to a quarter of the screen.

The spiral is the profile's theme: every seed is placed by one rule -- turn by the golden
angle, step outward by sqrt(n) -- and complex, living structure emerges from it.

Text is set in Geist and Geist Mono (SIL OFL 1.1, see scripts/fonts/OFL.txt). Each SVG
embeds a WOFF subset holding only the glyphs it uses, because GitHub shows README images
inside an <img> sandbox where external fonts never load.

    python scripts/generate_banner.py
"""
from __future__ import annotations

import base64
import io
import logging
import math
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

logging.getLogger("fontTools.subset").setLevel(logging.ERROR)  # "meta NOT subset" noise

SCRIPTS = Path(__file__).resolve().parent
FONTS = SCRIPTS / "fonts"
LOGOS = SCRIPTS / "logos"
ASSETS = SCRIPTS.parent / "assets"

GOLDEN_ANGLE = math.pi * (3 - math.sqrt(5))  # 137.508 degrees

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
    "mono-400": (MONO, "GeistMono-Regular.ttf", 400, "normal"),
    "mono-500": (MONO, "GeistMono-Medium.ttf", 500, "normal"),
}

# One palette per GitHub theme. Colors that sit on the card background meet WCAG AA for
# their size; `tint` is the soft fill behind chips and badges.
THEMES = {
    "dark": {
        "bg_top": "#121a25", "bg_bottom": "#0d131c", "edge": "#ffffff", "edge_opacity": ".10",
        "ink": "#e6edf3", "slate": "#9da7b3", "dim": "#7d8590",
        "accent": "#34d399", "accent2": "#22d3ee", "kicker": "#6ee7b7",
        "tint": "#10b981", "tint_opacity": ".10", "tint_edge": "#34d399", "tint_edge_opacity": ".30",
        "chip_text": "#a7f3d0", "dots": "#ffffff", "dots_opacity": ".06",
        "glow": "#10b981", "glow_opacity": 0.20, "glow2": "#22d3ee", "glow2_opacity": 0.08,
        "spiral": ("#ecfdf5", "#86efac", "#34d399", "#10b981", "#14b8a6", "#22d3ee", "#38bdf8"),
        "name_end": "#a7f3d0", "head": "#ffc857",
    },
    "light": {
        "bg_top": "#ffffff", "bg_bottom": "#f6f8fa", "edge": "#d0d7de", "edge_opacity": "1",
        "ink": "#1f2328", "slate": "#59636e", "dim": "#6e7781",
        "accent": "#047857", "accent2": "#0e7490", "kicker": "#047857",
        "tint": "#10b981", "tint_opacity": ".08", "tint_edge": "#059669", "tint_edge_opacity": ".30",
        "chip_text": "#065f46", "dots": "#1f2328", "dots_opacity": ".07",
        "glow": "#10b981", "glow_opacity": 0.10, "glow2": "#06b6d4", "glow2_opacity": 0.06,
        "spiral": ("#064e3b", "#047857", "#059669", "#0d9488", "#0891b2", "#0284c7", "#38bdf8"),
        "name_end": "#065f46", "head": "#d97706",
    },
}

# Cards and tiles: image width, and the transparent margin around the drawn panel that
# spaces them apart when two sit side by side. Two images plus the space between them must
# stay under the 846 px README column.
IMG_W = 412
MARGIN = 6
PANEL_W = IMG_W - 2 * MARGIN
PAD = 24


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


def fit(face: str, text: str, size: float, limit: float, tracking: float = 0.0) -> None:
    width = text_width(face, text, size, tracking)
    if width > limit:
        raise ValueError(f"{text!r} is {width:.0f}px wide but only {limit:.0f}px fit; shorten it")


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


def fonts_css(faces: dict[str, str]) -> str:
    return "".join(font_face(face, text) for face, text in faces.items() if text.strip())


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


def spiral_markup(points, size_min: float, size_max: float, ramp: tuple[str, ...]) -> list[str]:
    out = []
    for x, y, t in points:
        size = size_min + (size_max - size_min) * t**0.8
        opacity = 0.95 - 0.5 * t**1.6
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size:.2f}" fill="{mix(ramp, t)}" opacity="{opacity:.2f}"/>'
        )
    return out


def glow(gid: str, cx: float, cy: float, r: float, color: str, opacity: float) -> str:
    return (
        f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{color}" stop-opacity="{opacity}"/>'
        f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
    )


def spin(cx: float, cy: float, seconds: float) -> str:
    return (
        f'<animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" '
        f'to="360 {cx} {cy}" dur="{seconds}s" repeatCount="indefinite"/>'
    )


def document(width: int, height: int, layers: list[str], defs: list[str], css: str,
             title: str, desc: str) -> str:
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title>',
            f'<desc id="desc">{escape(desc)}</desc>',
            f"<style>{css}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>",
            "<defs>",
            *defs,
            "</defs>",
            *layers,
            "</svg>",
            "",
        ]
    )


def panel(theme: dict, x: float, y: float, w: float, h: float, r: float) -> tuple[list[str], list[str]]:
    """(defs, layers) for a rounded panel: background gradient, faint dot grid, hairline edge.

    The panel's content goes between the returned layers' opening and closing <g>, which
    clips to the rounded shape; callers append their layers and then `"</g>" + edge`.
    """
    defs = [
        f'<clipPath id="panel"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/></clipPath>',
        '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{theme["bg_top"]}"/>'
        f'<stop offset="1" stop-color="{theme["bg_bottom"]}"/></linearGradient>',
        '<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="11" cy="11" r="0.9" fill="{theme["dots"]}" fill-opacity="{theme["dots_opacity"]}"/></pattern>',
    ]
    layers = [
        '<g clip-path="url(#panel)">',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#bg)"/>',
    ]
    return defs, layers


def panel_edge(theme: dict, x: float, y: float, w: float, h: float, r: float) -> str:
    return (
        f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{h - 1}" rx="{r - 0.5}" fill="none" '
        f'stroke="{theme["edge"]}" stroke-opacity="{theme["edge_opacity"]}"/>'
    )


def outbound(theme: dict, x: float, y: float) -> str:
    """A small north-east arrow: this panel is a link."""
    return (
        f'<path d="M{x - 9:.1f} {y + 9:.1f}L{x:.1f} {y:.1f}M{x - 7:.1f} {y:.1f}H{x:.1f}V{y + 7:.1f}" '
        f'fill="none" stroke="{theme["dim"]}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
    )


# --------------------------------------------------------------------------- header

HEADER = {
    "kicker": "HANOI, VIETNAM · FPT UNIVERSITY",
    "name": "Nguyễn Anh Dương",
    "role_accent": "AI Engineer",
    "role_rest": " · agentic systems & artificial life",
}


def build_header(theme_name: str) -> str:
    theme = THEMES[theme_name]
    width, height, radius = 960, 250, 20
    cx, cy, spiral_r, count = 822, 125, 104, 480
    x0 = 52
    kicker, name = HEADER["kicker"], HEADER["name"]
    role_accent, role_rest = HEADER["role_accent"], HEADER["role_rest"]

    fit("sans-600", name, 60, 560)
    fit("sans-500", role_accent + role_rest, 23, 600)

    defs, layers = panel(theme, 0, 0, width, height, radius)
    defs += [
        glow("gSpiral", cx, cy, 230, theme["glow"], theme["glow_opacity"]),
        glow("gCool", 120, -40, 420, theme["glow2"], theme["glow2_opacity"]),
        '<radialGradient id="gridFade" cx="300" cy="125" r="520" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        f'<mask id="gridMask"><rect width="{width}" height="{height}" fill="url(#gridFade)"/></mask>',
        '<linearGradient id="nameFill" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{theme["ink"]}"/><stop offset=".7" stop-color="{theme["ink"]}"/>'
        f'<stop offset="1" stop-color="{theme["name_end"]}"/></linearGradient>',
        '<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{theme["accent"]}"/><stop offset="1" stop-color="{theme["accent2"]}"/></linearGradient>',
    ]
    layers += [
        f'<rect width="{width}" height="{height}" fill="url(#gCool)"/>',
        f'<rect width="{width}" height="{height}" fill="url(#gSpiral)"/>',
        f'<rect width="{width}" height="{height}" fill="url(#dots)" mask="url(#gridMask)"/>',
        "<g>",
        *spiral_markup(seeds(cx, cy, count, spiral_r), 1.2, 3.3, theme["spiral"]),
        spin(cx, cy, 200),
        "</g>",
        f'<circle cx="{x0 + 4}" cy="73.5" r="3.5" fill="{theme["accent"]}"/>',
        f'<text class="kick" x="{x0 + 16}" y="78">{escape(kicker)}</text>',
        f'<text class="name" x="{x0 - 3}" y="146" fill="url(#nameFill)">{escape(name)}</text>',
        f'<text class="role" x="{x0}" y="190"><tspan fill="url(#accent)">{escape(role_accent)}</tspan>'
        f"{escape(role_rest)}</text>",
        "</g>",
        panel_edge(theme, 0, 0, width, height, radius),
    ]
    css = "".join(
        [
            fonts_css({"sans-600": name, "sans-500": role_accent + role_rest, "mono-500": kicker}),
            f".kick{{font:500 12px {MONO_STACK};letter-spacing:.16em;fill:{theme['kicker']}}}",
            f".name{{font:600 60px {SANS_STACK};letter-spacing:-.03em}}",
            f".role{{font:500 23px {SANS_STACK};letter-spacing:-.01em;fill:{theme['slate']}}}",
        ]
    )
    return document(
        width, height, layers, defs, css,
        title=f"{name} — AI Engineer",
        desc=f"{name}, AI Engineer building agentic systems and artificial life, "
        "beside a slowly turning phyllotaxis spiral.",
    )


# --------------------------------------------------------------------------- project cards

CARDS = (
    {
        "slug": "anima",
        "repo": "Anima-Engine",
        "title": "Anima Engine",
        "kicker": "RUST · BEVY · BURN · TAURI",
        "desc": "Preregistered evolution experiments on a living world with a closed energy budget.",
        "chips": ("artificial life", "seeded replays"),
        "glyph": "creature",
    },
    {
        "slug": "oxideswarm",
        "repo": "OxideSwarm",
        "title": "OxideSwarm",
        "kicker": "RUST · TOKIO · IROH QUIC",
        "desc": "One Rust binary turns your Macs, Windows PCs and Linux boxes into a build-and-test grid.",
        "chips": ("v0.4.4", "macOS · Windows · Linux", "MCP"),
        "glyph": "logo",
    },
    {
        "slug": "mindsync",
        "repo": "VN_AI_Innovation",
        "title": "MindSync",
        "kicker": "NEXT.JS · POSTGRESQL · FPT AI",
        "desc": "AI assistant for Vietnamese public services: lists the papers, blocks invalid filings.",
        "chips": ("VAIC 2026 national final", "team lead"),
        "glyph": "chat",
    },
    {
        "slug": "smartdrive",
        "repo": "smart-drive-os",
        "title": "SmartDrive-OS",
        "kicker": "PYTHON · SQLITE FTS5 · MCP",
        "desc": "Move and tidy the folders on a drive without breaking your coding agents and IDEs.",
        "chips": ("on PyPI", "9 MCP tools", "zero dependencies"),
        "glyph": "drive",
    },
)


def creature_glyph(theme: dict, cx: float, cy: float) -> str:
    """The Anima Engine logo in miniature: a segmented body growing along a spiral to a head."""
    out, n = [], 26
    for i in range(n):
        t = i / (n - 1)
        angle = 0.4 + t * 2.15 * math.pi
        r = 2.0 + 13.0 * t
        x, y = cx + r * math.cos(angle), cy + r * math.sin(angle)
        size = 0.9 + 2.6 * t**1.2
        color = mix((theme["accent2"], theme["accent"], theme["head"]), t**2.4)
        out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{size:.2f}" fill="{color}"/>')
    head_angle = 0.4 + 2.15 * math.pi
    hx, hy = cx + 15.0 * math.cos(head_angle), cy + 15.0 * math.sin(head_angle)
    out.append(f'<circle cx="{hx:.2f}" cy="{hy:.2f}" r="4.6" fill="{theme["head"]}"/>')
    out.append(f'<circle cx="{hx + 1.2:.2f}" cy="{hy - 1.0:.2f}" r="1.3" fill="{theme["bg_bottom"]}"/>')
    return "".join(out)


def line_glyph(kind: str, theme: dict, x: float, y: float) -> str:
    """Line icons drawn on a 44 px badge whose top-left corner is (x, y)."""
    pen = (
        f'stroke="{theme["accent"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
    )
    stroke = f'fill="none" {pen}'
    if kind == "chat":
        body = [
            f'<path d="M14 11h16a5 5 0 0 1 5 5v9a5 5 0 0 1-5 5h-9l-6 5v-5h-1a5 5 0 0 1-5-5v-9a5 5 0 0 1 5-5z" {stroke}/>',
            f'<path d="M16.5 20.5l3.5 3.5 7-7" {stroke}/>',
        ]
    elif kind == "drive":
        body = [
            f'<rect x="9" y="12" width="26" height="20" rx="4" {stroke}/>',
            f'<path d="M9 24h26" {stroke}/>',
            f'<circle cx="29.5" cy="28.2" r="1.5" fill="{theme["accent"]}"/>',
            f'<path d="M14 17.5h9" {stroke} stroke-opacity=".6"/>',
        ]
    else:
        raise ValueError(f"unknown glyph {kind!r}")
    return f'<g transform="translate({x} {y})">{"".join(body)}</g>'


def badge(theme: dict, kind: str, x: float, y: float, size: float = 44, slug: str = "") -> list[str]:
    """A tinted square holding the project's mark: its own logo (kind "logo"), or a drawn glyph."""
    out = [
        f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="12" fill="{theme["tint"]}" '
        f'fill-opacity="{theme["tint_opacity"]}" stroke="{theme["tint_edge"]}" '
        f'stroke-opacity="{theme["tint_edge_opacity"]}"/>'
    ]
    if kind == "creature":
        out.append(creature_glyph(theme, x + size / 2, y + size / 2))
    elif kind == "logo":
        mark = logo_mark(slug)
        if mark is None:
            raise ValueError(f"{slug}: glyph 'logo' needs scripts/logos/{slug}.svg")
        viewbox, inner = mark
        inset = 4
        out.append(
            f'<svg class="logo-badge" x="{x + inset}" y="{y + inset}" width="{size - 2 * inset}" '
            f'height="{size - 2 * inset}" viewBox="{viewbox}">{inner}</svg>'
        )
    else:
        out.append(line_glyph(kind, theme, x, y))
    return out


def chips_markup(theme: dict, labels: tuple[str, ...], x0: float, y: float, limit: float) -> list[str]:
    size, height = 12.5, 28
    out, x = [], x0
    for label in labels:
        w = text_width("sans-500", label, size) + 22
        out.append(
            f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{height}" rx="{height / 2}" '
            f'fill="{theme["tint"]}" fill-opacity="{theme["tint_opacity"]}" stroke="{theme["tint_edge"]}" '
            f'stroke-opacity="{theme["tint_edge_opacity"]}"/>'
            f'<text class="chip" x="{x + 11:.1f}" y="{y + 18.4}">{escape(label)}</text>'
        )
        x += w + 8
    if x - 8 > x0 + limit:
        raise ValueError(f"chips {labels} are {x - 8 - x0:.0f}px wide but only {limit:.0f}px fit")
    return out


# A project that has its own logo shows it large and faint behind the right side of its
# card, fading out towards the text. scripts/logos/<slug>.svg holds the logo as it appears in
# that project's repository, minus any background tile; a project without one gets no backdrop.
LOGO_SIZE = 176
LOGO_STRENGTH = {"dark": ".22", "light": ".18"}
# Logos whose colours depend on the theme style them through classes; the card supplies them.
LOGO_CSS = {
    "oxideswarm": {
        "dark": ".ox-shell{fill:#ffffff;stroke:#64748b;stroke-width:2;stroke-linejoin:round}"
                ".logo-badge .ox-shell{stroke-width:5}",
        "light": ".ox-shell{fill:#ffffff;stroke:#64748b;stroke-width:2;stroke-linejoin:round}"
                 ".logo-badge .ox-shell{stroke-width:5}",
    },
}


@lru_cache(maxsize=None)
def logo_mark(slug: str) -> tuple[str, str] | None:
    """(viewBox, inner markup) of scripts/logos/<slug>.svg, or None when the project has no logo."""
    path = LOGOS / f"{slug}.svg"
    if not path.is_file():
        return None
    text = re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8"), flags=re.S)
    match = re.search(r'<svg[^>]*\bviewBox="([^"]+)"[^>]*>(.*)</svg>', text, re.S)
    if match is None:
        raise ValueError(f"{path} needs a root <svg> with a viewBox")
    return match.group(1), match.group(2).strip()


def logo_backdrop(slug: str, theme_name: str, ox: float, oy: float, w: float, h: float
                  ) -> tuple[list[str], list[str]]:
    """(defs, layers) for the project's logo behind the card's right side; empty without one."""
    mark = logo_mark(slug)
    if mark is None:
        return [], []
    viewbox, inner = mark
    size = LOGO_SIZE
    # Low on the right, below the small kicker line, a little of it running off the right edge.
    x, y = ox + w - size * 0.78, oy + h / 2 + 28 - size / 2
    # The strength rides on stop-opacity so the light and dark files differ only in colour.
    defs = [
        f'<linearGradient id="logoFade" x1="{x - size * 0.2:.1f}" y1="0" x2="{x + size * 0.3:.1f}" y2="0" '
        'gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="#ffffff" stop-opacity="{LOGO_STRENGTH[theme_name]}"/></linearGradient>',
        f'<mask id="logoMask" maskUnits="userSpaceOnUse" x="{ox}" y="{oy}" width="{w}" height="{h}">'
        f'<rect x="{ox}" y="{oy}" width="{w}" height="{h}" fill="url(#logoFade)"/></mask>',
    ]
    layers = [
        f'<g mask="url(#logoMask)"><svg x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" '
        f'viewBox="{viewbox}">{inner}</svg></g>'
    ]
    return defs, layers


def build_card(spec: dict, theme_name: str) -> str:
    theme = THEMES[theme_name]
    ox, oy, w, h, radius = MARGIN, MARGIN, PANEL_W, 196, 16
    inner = w - 2 * PAD
    text_x = ox + PAD + 44 + 16

    fit("sans-600", spec["title"], 25, w - (text_x - ox) - PAD - 20)
    fit("mono-500", spec["kicker"], 10.5, w - (text_x - ox) - PAD, 0.12)
    desc = wrap("sans-400", spec["desc"], 16, inner)
    if len(desc) > 2:
        raise ValueError(f"{spec['slug']}: description wraps to {len(desc)} lines; shorten it")

    defs, layers = panel(theme, ox, oy, w, h, radius)
    defs.append(glow("gCorner", ox + w, oy, 260, theme["glow"], theme["glow_opacity"] * 0.6))
    logo_defs, logo_layers = logo_backdrop(spec["slug"], theme_name, ox, oy, w, h)
    defs += logo_defs
    layers += [
        f'<rect x="{ox}" y="{oy}" width="{w}" height="{h}" fill="url(#gCorner)"/>',
        *logo_layers,
        *badge(theme, spec["glyph"], ox + PAD, oy + PAD, slug=spec["slug"]),
        f'<text class="title" x="{text_x - 1}" y="{oy + 45}">{escape(spec["title"])}</text>',
        f'<text class="kick" x="{text_x}" y="{oy + 65}">{escape(spec["kicker"])}</text>',
        outbound(theme, ox + w - PAD, oy + PAD + 4),
        *[
            f'<text class="desc" x="{ox + PAD}" y="{oy + 104 + 23 * i}">{escape(line)}</text>'
            for i, line in enumerate(desc)
        ],
        *chips_markup(theme, spec["chips"], ox + PAD, oy + 146, inner),
        "</g>",
        panel_edge(theme, ox, oy, w, h, radius),
    ]
    css = "".join(
        [
            fonts_css(
                {
                    "sans-600": spec["title"],
                    "sans-500": "".join(spec["chips"]),
                    "sans-400": spec["desc"],
                    "mono-500": spec["kicker"],
                }
            ),
            f".title{{font:600 25px {SANS_STACK};letter-spacing:-.025em;fill:{theme['ink']}}}",
            f".kick{{font:500 10.5px {MONO_STACK};letter-spacing:.12em;fill:{theme['dim']}}}",
            f".desc{{font:400 16px {SANS_STACK};fill:{theme['slate']}}}",
            f".chip{{font:500 12.5px {SANS_STACK};fill:{theme['chip_text']}}}",
            LOGO_CSS.get(spec["slug"], {}).get(theme_name, ""),
        ]
    )
    return document(
        IMG_W, h + 2 * MARGIN, layers, defs, css,
        title=f"{spec['title']} — {spec['desc']}",
        desc=f"{spec['kicker'].title()}. " + " · ".join(spec["chips"]),
    )


# --------------------------------------------------------------------------- achievement tiles

AWARDS = (
    {
        "slug": "hackerrank",
        "icon": "trophy",
        "value": "#50 of 4,090 · top 1.2%",
        "event": "HackerRank Orchestrate · Oct 2026",
        "href": "https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/"
        "ghost-data-still-exists/leaderboard?page=2",
    },
    {
        "slug": "arc",
        "icon": "trophy",
        "value": "#33 of 309 · final",
        "event": "ARC White-Box Estimation 2026 · Phase 2",
        "href": "https://www.aicrowd.com/challenges/arc-white-box-estimation-challenge-2026/leaderboards?round=phase-2",
    },
    {
        "slug": "denso",
        "icon": "medal",
        "value": "Top 4 & Promising Award",
        "event": "DENSO Factory Hacks 2025",
        "href": "https://drive.google.com/file/d/1K1Sfw4AnxBfi7deHBIaIqpH9cJ-G3ti9/view",
    },
    {
        "slug": "vaic",
        "icon": "flag",
        "value": "Team lead · MindSync",
        "event": "VAIC 2026 · national final",
        "href": "https://github.com/DuongNAD/VN_AI_Innovation",
    },
)

# 16x16 glyphs. Stroked parts use currentColor, the rest is filled.
AWARD_GLYPHS = {
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
}


def build_award(spec: dict, theme_name: str) -> str:
    theme = THEMES[theme_name]
    ox, oy, w, h, radius = MARGIN, MARGIN, PANEL_W, 84, 16
    text_x = ox + 76
    limit = w - (text_x - ox) - PAD - 14
    fit("sans-600", spec["value"], 17, limit)
    fit("sans-400", spec["event"], 13.5, limit)

    cx, cy = ox + 42, oy + h / 2
    color = theme["accent"]
    defs, layers = panel(theme, ox, oy, w, h, radius)
    layers += [
        f'<circle cx="{cx}" cy="{cy}" r="20" fill="{theme["tint"]}" fill-opacity="{theme["tint_opacity"]}" '
        f'stroke="{theme["tint_edge"]}" stroke-opacity="{theme["tint_edge_opacity"]}"/>',
        f'<g transform="translate({cx - 10} {cy - 10}) scale(1.25)" fill="{color}" color="{color}">'
        f'{AWARD_GLYPHS[spec["icon"]]}</g>',
        f'<text class="val" x="{text_x}" y="{oy + 38}">{escape(spec["value"])}</text>',
        f'<text class="evt" x="{text_x}" y="{oy + 60}">{escape(spec["event"])}</text>',
        outbound(theme, ox + w - PAD, oy + PAD + 2),
        "</g>",
        panel_edge(theme, ox, oy, w, h, radius),
    ]
    css = "".join(
        [
            fonts_css({"sans-600": spec["value"], "sans-400": spec["event"]}),
            f".val{{font:600 17px {SANS_STACK};letter-spacing:-.01em;fill:{theme['ink']}}}",
            f".evt{{font:400 13.5px {SANS_STACK};fill:{theme['slate']}}}",
        ]
    )
    return document(
        IMG_W, h + 2 * MARGIN, layers, defs, css,
        title=f"{spec['value']} — {spec['event']}",
        desc=f"Achievement: {spec['value']} at {spec['event']}.",
    )


# --------------------------------------------------------------------------- output

def build_all() -> dict[str, str]:
    """Every static asset, keyed by file name under assets/."""
    built = {}
    for theme in THEMES:
        built[f"header-{theme}.svg"] = build_header(theme)
        for spec in CARDS:
            built[f"card-{spec['slug']}-{theme}.svg"] = build_card(spec, theme)
        for spec in AWARDS:
            built[f"award-{spec['slug']}-{theme}.svg"] = build_award(spec, theme)
    return built


def main() -> None:
    logging.getLogger("fontTools.subset").setLevel(logging.ERROR)
    ASSETS.mkdir(exist_ok=True)
    for filename, svg in build_all().items():
        path = ASSETS / filename
        path.write_text(svg, encoding="utf-8", newline="\n")
        print(f"wrote {path.relative_to(SCRIPTS.parent)} ({len(svg.encode('utf-8')) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
