#!/usr/bin/env python3
"""Fetch and sanitize all dynamic GitHub profile widgets and repository pin cards."""
import re
import sys
import urllib.request
from pathlib import Path

BAD = ("failed to retrieve", "something went wrong", "deployment_paused")

WIDGETS = {
    "assets/stats.svg": "https://github-readme-stats-eight-theta.vercel.app/api?username=DuongNAD&show_icons=true&theme=transparent&hide_border=true&bg_color=0B1220&title_color=60A5FA&icon_color=3B82F6&text_color=E5E7EB&ring_color=2563EB&count_private=true&include_all_commits=true&disable_animations=true",
    "assets/top-langs.svg": "https://github-readme-stats-eight-theta.vercel.app/api/top-langs/?username=DuongNAD&layout=compact&theme=transparent&hide_border=true&bg_color=0B1220&title_color=60A5FA&text_color=E5E7EB&langs_count=8&disable_animations=true",
    "assets/streak.svg": "https://streak-stats.demolab.com?user=DuongNAD&theme=transparent&hide_border=true&background=0B1220&ring=2563EB&fire=60A5FA&currStreakLabel=60A5FA&sideLabels=E5E7EB&dates=94A3B8&sideNums=E5E7EB&currStreakNum=60A5FA",
    "assets/trophies.svg": "https://github-profile-trophy-eight.vercel.app/?username=DuongNAD&theme=algolia&no-frame=true&no-bg=true&column=7&margin-w=8&margin-h=8",
    "assets/activity-graph.svg": "https://github-readme-activity-graph.vercel.app/graph?username=DuongNAD&theme=react-dark&hide_border=true&bg_color=0B1220&color=60A5FA&line=2563EB&point=ffffff",
    "assets/pin-liva.svg": "https://github-readme-stats-eight-theta.vercel.app/api/pin/?username=DuongNAD&repo=LIVA&theme=transparent&hide_border=true&bg_color=0B1220&title_color=60A5FA&icon_color=3B82F6&text_color=E5E7EB",
    "assets/pin-smart-drive-os.svg": "https://github-readme-stats-eight-theta.vercel.app/api/pin/?username=DuongNAD&repo=smart-drive-os&theme=transparent&hide_border=true&bg_color=0B1220&title_color=60A5FA&icon_color=3B82F6&text_color=E5E7EB",
    "assets/pin-vn-ai.svg": "https://github-readme-stats-eight-theta.vercel.app/api/pin/?username=DuongNAD&repo=VN_AI_Innovation&theme=transparent&hide_border=true&bg_color=0B1220&title_color=60A5FA&icon_color=3B82F6&text_color=E5E7EB",
    "assets/pin-anima.svg": "https://github-readme-stats-eight-theta.vercel.app/api/pin/?username=DuongNAD&repo=Anima-Engine&theme=transparent&hide_border=true&bg_color=0B1220&title_color=60A5FA&icon_color=3B82F6&text_color=E5E7EB",
    "assets/pin-mcp-agy.svg": "https://github-readme-stats-eight-theta.vercel.app/api/pin/?username=DuongNAD&repo=mcp-agy&theme=transparent&hide_border=true&bg_color=0B1220&title_color=60A5FA&icon_color=3B82F6&text_color=E5E7EB",
}


def sanitize(text: str) -> str | None:
    if "<svg" not in text.lower():
        return None
    lowered = text.lower()
    if any(token in lowered for token in BAD):
        return None
    text = re.sub(r"\n[ \t]*undefined[ \t]*\n", "\n", text)
    text = re.sub(
        r"\.stagger\s*\{[^}]*opacity:\s*0;[^}]*\}",
        ".stagger { opacity: 1; }",
        text,
    )
    text = re.sub(
        r"opacity:\s*0;\s*animation:\s*fadein[^'\"]+",
        "opacity: 1",
        text,
    )
    return text


def main() -> int:
    base_dir = Path(__file__).resolve().parent.parent
    assets_dir = base_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    success_count = 0
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for rel_path, url in WIDGETS.items():
        dest = base_dir / rel_path
        print(f"Fetching {rel_path}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw_text = resp.read().decode("utf-8", errors="ignore")
            
            sanitized = sanitize(raw_text)
            if sanitized:
                dest.write_text(sanitized, encoding="utf-8", newline="\n")
                print(f"  -> SUCCESS: updated {rel_path} ({len(sanitized)} bytes)")
                success_count += 1
            else:
                print(f"  -> SKIPPED: invalid/error SVG for {rel_path} (keeping existing if present)")
        except Exception as e:
            print(f"  -> ERROR fetching {rel_path}: {e}")

    print(f"\nDone: {success_count}/{len(WIDGETS)} widgets processed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
