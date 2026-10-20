#!/usr/bin/env python3
"""Find public CommonLib declarations related to player level and skill progress."""
from __future__ import annotations
import os
from pathlib import Path
from pathlib import PureWindowsPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config

def main() -> None:
    value = read_local_config(ROOT).get("COMMONLIBSSE_ROOT", "").strip()
    win = PureWindowsPath(value)
    if os.name != "nt" and win.drive and len(win.drive) == 2 and win.drive[1] == ":":
        source = Path("/mnt") / win.drive[0].lower() / Path(*win.parts[1:])
    else:
        source = Path(value).expanduser()
    if not source.is_absolute():
        source = ROOT / source
    if not source.is_dir():
        raise SystemExit("configured CommonLib source is unavailable")
    try:
        revision = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        revision = "unknown"
    print(f"source_revision={revision}")
    terms = re.compile(r"advance.?skill|skill.?experience|player.?experience|experience.?for.?level|level.?up|set.?level|get.?level", re.IGNORECASE)
    for path in sorted(source.rglob("*.h")):
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        hits = [(n, line.strip()) for n, line in enumerate(lines, 1) if terms.search(line)]
        if hits:
            rel = path.relative_to(source).as_posix()
            print(f"FILE {rel}")
            for number, line in hits[:80]:
                print(f"{number}: {line[:300]}")
    for relative, needles in {
        "include/RE/A/Actor.h": ["GetLevel() const"],
        "include/RE/P/PlayerCharacter.h": ["AddSkillExperience", "levelUp", "LevelUp"],
        "include/RE/Offsets.h": ["GetLevel"],
        "include/RE/T/TESActorBaseData.h": ["GetLevel() const"],
    }.items():
        path = source / relative
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for needle in needles:
            for index, line in enumerate(lines):
                if needle.casefold() in line.casefold():
                    print(f"\nCONTEXT {relative}:{index + 1} needle={needle}")
                    for n in range(max(0, index - 8), min(len(lines), index + 14)):
                        print(f"{n + 1}: {lines[n][:300]}")

if __name__ == "__main__":
    main()
