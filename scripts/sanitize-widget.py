#!/usr/bin/env python3
"""Drop error cards and make widget SVGs visible without CSS animation."""
import re
import sys
from pathlib import Path

BAD = ("failed to retrieve", "something went wrong", "deployment_paused")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: sanitize-widget.py SRC DEST", file=sys.stderr)
        return 2
    src, dest = Path(sys.argv[1]), Path(sys.argv[2])
    text = src.read_text(encoding="utf-8", errors="ignore")
    if "<svg" not in text.lower():
        print("not an svg", file=sys.stderr)
        return 1
    lowered = text.lower()
    if any(token in lowered for token in BAD):
        print("error card", file=sys.stderr)
        return 1
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
    dest.write_text(text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
