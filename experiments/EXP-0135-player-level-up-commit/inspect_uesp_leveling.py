#!/usr/bin/env python3
"""Extract bounded grounding snippets from the revision-pinned local UESP page."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / ".local/uesp/q86/leveling.raw.json"

def main() -> None:
    raw = PAGE.read_bytes()
    page = json.loads(raw)
    content = page["content"]
    print(json.dumps({"title": page.get("title"), "revision_id": page.get("revision_id"), "timestamp": page.get("timestamp"), "url": page.get("url"), "raw_sha256": hashlib.sha256(raw).hexdigest()}, indent=2))
    needles = ["There are two types of", "Gaining Levels", "When you level up", "Leveling Decisions", "You can choose", "level-up", "character level-up"]
    seen = set()
    for needle in needles:
        start = 0
        occurrences = 0
        while occurrences < 3:
            at = content.lower().find(needle.lower(), start)
            if at < 0:
                break
            key = (at, needle)
            if key not in seen:
                seen.add(key)
                print(f"\n--- {needle} at {at} ---\n{content[max(0, at-240):min(len(content), at+1150)]}")
            start = at + len(needle)
            occurrences += 1

if __name__ == "__main__":
    main()
