#!/usr/bin/env python3
"""Generate a breathtaking, serene nature & landscape SVG header banner for GitHub profile."""
import xml.etree.ElementTree as ET
from pathlib import Path

def generate_svg() -> str:
    # 1200 x 260 widescreen banner
    width = 1200
    height = 260
    
    # We will build layers of:
    # 1. Gradient Sky (Twilight Midnight -> Forest Emerald Horizon)
    # 2. Stars & Fireflies
    # 3. Soft Glowing Moon / Celestial Crescent
    # 4. Birds flying in twilight
    # 5. Distant Mountain Range
    # 6. Midground Mountain Range with pine forest crest
    # 7. Foreground Misty Ridge with majestic Stag/Deer silhouette
    # 8. Foreground Pine conifers & botanical silhouettes
    # 9. Elegant, readable typography
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" role="img" aria-label="Nguyen Anh Duong - Nature &amp; Landscape Banner">
  <defs>
    <!-- Sky Gradient -->
    <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#050c12" />
      <stop offset="45%" stop-color="#0b2223" />
      <stop offset="75%" stop-color="#113630" />
      <stop offset="100%" stop-color="#16463d" />
    </linearGradient>

    <!-- Celestial Moon Glow -->
    <radialGradient id="moonGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#d1fae5" stop-opacity="0.85" />
      <stop offset="35%" stop-color="#a7f3d0" stop-opacity="0.4" />
      <stop offset="70%" stop-color="#34d399" stop-opacity="0.12" />
      <stop offset="100%" stop-color="#064e3b" stop-opacity="0" />
    </radialGradient>

    <!-- Warm Firefly Glow -->
    <radialGradient id="firefly" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#fef08a" stop-opacity="0.9" />
      <stop offset="40%" stop-color="#fde047" stop-opacity="0.5" />
      <stop offset="100%" stop-color="#ca8a04" stop-opacity="0" />
    </radialGradient>

    <!-- Mountain Gradients for atmospheric depth -->
    <linearGradient id="distantMtn" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#18433b" stop-opacity="0.7" />
      <stop offset="100%" stop-color="#0d2823" stop-opacity="0.9" />
    </linearGradient>

    <linearGradient id="midMtn" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#123831" />
      <stop offset="100%" stop-color="#091d19" />
    </linearGradient>

    <linearGradient id="foreRidge" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#0b2420" />
      <stop offset="100%" stop-color="#05120f" />
    </linearGradient>

    <!-- Subtle border highlight -->
    <linearGradient id="topBorder" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#34d399" stop-opacity="0.3" />
      <stop offset="50%" stop-color="#6ee7b7" stop-opacity="0.8" />
      <stop offset="100%" stop-color="#10b981" stop-opacity="0.3" />
    </linearGradient>

    <style>
      .title-text {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, sans-serif;
        font-weight: 700;
        fill: #f0fdf4;
        letter-spacing: 2px;
      }}
      .subtitle-text {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, sans-serif;
        font-weight: 500;
        fill: #a7f3d0;
        letter-spacing: 0.8px;
      }}
      .meta-text {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', Roboto, sans-serif;
        font-weight: 400;
        fill: #6ee7b7;
        letter-spacing: 0.5px;
        opacity: 0.85;
      }}
      @keyframes floatParticle {{
        0%, 100% {{ transform: translateY(0px) scale(1); opacity: 0.7; }}
        50% {{ transform: translateY(-8px) scale(1.15); opacity: 1; }}
      }}
      .firefly-anim {{
        animation: floatParticle 5s ease-in-out infinite;
      }}
      .firefly-anim-2 {{
        animation: floatParticle 7s ease-in-out infinite reverse;
      }}
    </style>
  </defs>

  <!-- Sky Canvas with rounded corners -->
  <rect width="{width}" height="{height}" rx="12" fill="url(#skyGrad)" />
  <rect width="{width}" height="{height}" rx="12" fill="none" stroke="#1b4d3e" stroke-width="1" stroke-opacity="0.6" />
  
  <!-- Subtle Emerald Top Border Line -->
  <rect x="0" y="0" width="{width}" height="3" rx="1.5" fill="url(#topBorder)" />

  <!-- Stars in upper night sky -->
  <g fill="#ecfdf5" opacity="0.65">
    <circle cx="95" cy="42" r="1" />
    <circle cx="160" cy="28" r="1.3" opacity="0.9" />
    <circle cx="240" cy="55" r="0.8" />
    <circle cx="310" cy="35" r="1.2" />
    <circle cx="380" cy="62" r="0.9" />
    <circle cx="450" cy="25" r="1" />
    <circle cx="530" cy="48" r="0.7" />
    <circle cx="620" cy="30" r="1.1" />
    <circle cx="710" cy="52" r="0.9" />
    <circle cx="790" cy="22" r="1.4" opacity="0.95" />
    <circle cx="860" cy="45" r="0.8" />
    <circle cx="940" cy="32" r="1.2" />
    <circle cx="1020" cy="58" r="1" />
    <circle cx="1110" cy="38" r="1.5" opacity="0.9" />
    <circle cx="1165" cy="70" r="0.8" />
    <circle cx="65" cy="85" r="0.9" />
    <circle cx="1125" cy="95" r="1.1" />
  </g>

  <!-- Serene Moon & Soft Halo -->
  <circle cx="600" cy="55" r="32" fill="url(#moonGlow)" />
  <circle cx="600" cy="55" r="12" fill="#ecfdf5" opacity="0.9" />

  <!-- Silhouette of Soaring Birds in Twilight -->
  <g fill="#a7f3d0" opacity="0.45">
    <!-- Bird 1 -->
    <path d="M 460 65 Q 466 60 472 63 Q 478 60 484 65 Q 478 62 472 66 Q 466 62 460 65 Z" />
    <!-- Bird 2 -->
    <path d="M 488 56 Q 493 52 498 54 Q 503 52 508 56 Q 503 54 498 57 Q 493 54 488 56 Z" transform="scale(0.85) translate(80, 5)" />
    <!-- Bird 3 -->
    <path d="M 440 76 Q 444 73 448 74 Q 452 73 456 76 Q 452 74 448 77 Q 444 74 440 76 Z" transform="scale(0.7) translate(195, 20)" />
    <!-- Bird 4 & 5 right side -->
    <path d="M 720 60 Q 726 55 732 58 Q 738 55 744 60 Q 738 57 732 61 Q 726 57 720 60 Z" transform="scale(0.8) translate(180, 10)" />
    <path d="M 750 72 Q 755 68 760 70 Q 765 68 770 72 Q 765 70 760 73 Q 755 70 750 72 Z" transform="scale(0.65) translate(400, 30)" />
  </g>

  <!-- Layer 1: Distant Majestic Mountain Range -->
  <path fill="url(#distantMtn)" d="M 0 175 L 0 260 L 1200 260 L 1200 160 L 1140 172 L 1060 145 L 980 168 L 910 138 L 840 165 L 760 148 L 680 172 L 600 135 L 530 165 L 450 142 L 370 170 L 290 148 L 210 168 L 130 145 L 60 168 Z" />

  <!-- Layer 2: Midground Mountain Ridges with Forest Mist -->
  <path fill="url(#midMtn)" opacity="0.95" d="M 0 195 L 0 260 L 1200 260 L 1200 188 L 1150 198 L 1090 180 L 1020 200 L 940 178 L 870 195 L 790 175 L 710 198 L 620 172 L 540 194 L 460 174 L 380 196 L 310 176 L 230 195 L 150 175 L 70 194 Z" />

  <!-- Layer 3: Foreground Atmospheric Foothill & Pine Crest -->
  <path fill="url(#foreRidge)" d="M 0 215 L 0 260 L 1200 260 L 1200 210 Q 1050 195 900 215 Q 750 230 600 215 Q 450 200 300 220 Q 150 235 0 215 Z" />

  <!-- Majestic Stag / Deer Silhouette on Left Hilltop (Symbol of wildlife & living systems) -->
  <g fill="#061612" transform="translate(130, 138) scale(0.62)">
    <!-- Body -->
    <path d="M 45 65 C 40 55, 30 52, 20 54 C 12 55, 5 60, 2 68 C 0 74, 4 82, 10 84 C 18 86, 32 86, 42 82 C 45 80, 48 72, 45 65 Z" />
    <!-- Neck and Head -->
    <path d="M 38 66 C 42 54, 48 40, 52 30 C 53 26, 56 22, 60 20 C 64 19, 68 22, 67 26 C 66 30, 60 38, 55 48 C 50 56, 46 64, 44 68 Z" />
    <!-- Muzzle / Head details -->
    <ellipse cx="64" cy="22" rx="6" ry="4" transform="rotate(-15, 64, 22)" />
    <path d="M 68 20 L 73 22 L 67 25 Z" />
    <!-- Ears -->
    <path d="M 58 19 L 55 12 L 60 16 Z" />
    <path d="M 62 18 L 65 11 L 65 17 Z" />
    <!-- Antlers (Intricate majestic branches) -->
    <!-- Main Left Beam -->
    <path d="M 59 17 Q 56 5 50 -2 Q 46 -7 40 -10 Q 45 -5 49 0 Q 53 6 56 16 Z" fill="#061612" />
    <!-- Left Tines -->
    <path d="M 56 11 Q 48 9 44 11 Q 48 12 54 14 Z" />
    <path d="M 52 3 Q 44 -1 38 2 Q 43 4 50 6 Z" />
    <path d="M 46 -4 Q 40 -12 34 -15 Q 38 -9 44 -5 Z" />
    <!-- Main Right Beam -->
    <path d="M 62 17 Q 66 4 72 -3 Q 78 -9 85 -12 Q 79 -6 74 1 Q 69 8 65 16 Z" fill="#061612" />
    <!-- Right Tines -->
    <path d="M 65 10 Q 72 8 77 9 Q 71 11 65 13 Z" />
    <path d="M 69 3 Q 78 -2 83 1 Q 77 4 70 6 Z" />
    <path d="M 74 -4 Q 81 -11 88 -14 Q 82 -9 76 -5 Z" />
    <!-- Front Legs -->
    <path d="M 42 80 L 40 102 L 38 120 L 41 121 L 43 103 L 46 80 Z" />
    <path d="M 37 81 L 34 100 L 32 119 L 35 120 L 38 101 L 41 81 Z" opacity="0.85" />
    <!-- Back Legs -->
    <path d="M 8 78 Q 6 92 10 106 L 12 122 L 15 122 L 13 105 Q 11 94 14 79 Z" />
    <path d="M 15 79 Q 14 93 18 107 L 20 123 L 23 123 L 21 106 Q 18 94 20 80 Z" opacity="0.85" />
    <!-- Little Tail -->
    <path d="M 4 70 C 1 68, 0 74, 3 76 C 5 77, 6 74, 4 70 Z" />
  </g>

  <!-- Natural Pine Conifers Silhouettes Across Horizon -->
  <!-- Left Pine Cluster -->
  <g fill="#071b16">
    <!-- Tree 1 -->
    <polygon points="50,150 42,175 45,175 38,198 42,198 33,225 36,225 28,255 72,255 64,225 67,225 58,198 62,198 55,175 58,175" />
    <!-- Tree 2 -->
    <polygon points="90,165 83,185 86,185 79,205 83,205 75,230 78,230 70,255 110,255 102,230 105,230 97,205 101,205 94,185 97,185" />
    <!-- Tree 3 -->
    <polygon points="20,180 15,198 17,198 11,218 14,218 8,240 32,240 26,218 29,218 23,198 25,198" />
    <!-- Tree near deer -->
    <polygon points="230,170 224,190 227,190 220,210 224,210 216,235 244,235 236,210 240,210 233,190 236,190" />
    <polygon points="260,185 255,202 257,202 252,220 268,220 263,202 265,202" />
  </g>

  <!-- Right Pine Cluster -->
  <g fill="#071b16">
    <!-- Tree Right 1 -->
    <polygon points="1130,145 1122,172 1125,172 1117,198 1121,198 1112,225 1115,225 1106,258 1154,258 1145,225 1148,225 1139,198 1143,198 1135,172 1138,172" />
    <!-- Tree Right 2 -->
    <polygon points="1080,160 1073,182 1076,182 1069,204 1073,204 1065,230 1068,230 1059,255 1101,255 1092,230 1095,230 1087,204 1091,204 1084,182 1087,182" />
    <!-- Tree Right 3 -->
    <polygon points="1035,175 1029,194 1032,194 1025,214 1029,214 1021,238 1049,238 1041,214 1045,214 1038,194 1041,194" />
    <!-- Tree Right 4 -->
    <polygon points="1175,170 1170,190 1172,190 1166,212 1184,212 1178,190 1180,190" />
    <!-- Small trees -->
    <polygon points="980,195 975,212 977,212 972,230 988,230 983,212 985,212" />
    <polygon points="940,205 936,220 944,220" />
  </g>

  <!-- Floating Forest Fireflies (Subtle warm glows) -->
  <g class="firefly-anim">
    <circle cx="110" cy="205" r="2.5" fill="url(#firefly)" />
    <circle cx="215" cy="185" r="2" fill="url(#firefly)" />
    <circle cx="280" cy="225" r="2.2" fill="url(#firefly)" />
    <circle cx="950" cy="180" r="2.2" fill="url(#firefly)" />
    <circle cx="1060" cy="215" r="2.8" fill="url(#firefly)" />
  </g>
  <g class="firefly-anim-2">
    <circle cx="170" cy="235" r="2.2" fill="url(#firefly)" />
    <circle cx="340" cy="210" r="1.8" fill="url(#firefly)" />
    <circle cx="890" cy="210" r="2.5" fill="url(#firefly)" />
    <circle cx="1010" cy="195" r="2" fill="url(#firefly)" />
    <circle cx="1120" cy="230" r="2.4" fill="url(#firefly)" />
  </g>

  <!-- Typography Card Background (Soft Translucent Forest Mist Pill) -->
  <rect x="300" y="85" width="600" height="120" rx="16" fill="#04120e" fill-opacity="0.65" stroke="#1d4e3f" stroke-width="1" stroke-opacity="0.5" />

  <!-- Center Typography -->
  <g text-anchor="middle">
    <!-- Full Name -->
    <text x="600" y="125" class="title-text" font-size="28">NGUYỄN ANH DƯƠNG</text>
    <!-- Core Identity -->
    <text x="600" y="156" class="subtitle-text" font-size="15.5">AI Engineer &amp; Software Developer · Living Systems &amp; Agentic AI</text>
    <!-- Academic & Location -->
    <text x="600" y="184" class="meta-text" font-size="13">FPT University · Hanoi, Vietnam · Evolving Artificial Life &amp; Autonomous Agents</text>
  </g>
</svg>"""
    return svg

def main():
    target = Path("assets/header.svg")
    content = generate_svg()
    
    # Verify XML well-formedness
    try:
        ET.fromstring(content)
        print("XML validation passed successfully!")
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return 1
        
    target.write_text(content, encoding="utf-8", newline="\n")
    print(f"Successfully generated {target} ({len(content)} bytes)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
