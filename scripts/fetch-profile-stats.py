#!/usr/bin/env python3
"""Fetch the public repo and follower counts into assets/profile-stats.json.

The stats widgets do not expose these two numbers, so the highlights panel reads them from
the GitHub API. GITHUB_TOKEN is optional (it only raises the rate limit). On any failure the
existing file is kept, like fetch-all-widgets.py does for the widgets.
"""
import json
import os
import urllib.request
from pathlib import Path

USER = "DuongNAD"
DEST = Path(__file__).resolve().parent.parent / "assets" / "profile-stats.json"


def extract(payload: dict) -> dict[str, int]:
    return {"repos": int(payload["public_repos"]), "followers": int(payload["followers"])}


def main() -> int:
    headers = {"User-Agent": "profile-readme", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        request = urllib.request.Request(f"https://api.github.com/users/{USER}", headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            stats = extract(json.load(response))
    except Exception as error:  # network, rate limit, or an unexpected payload
        print(f"SKIPPED: could not fetch profile stats ({error}); keeping {DEST.name}")
        return 0
    DEST.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {DEST.name}: {stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
