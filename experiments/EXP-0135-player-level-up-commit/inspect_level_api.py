#!/usr/bin/env python3
"""Capture the small CommonLib API surface needed for Q86 source mapping."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path, PureWindowsPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config


def resolve_root(value: str) -> Path:
    win = PureWindowsPath(value)
    if os.name != "nt" and win.drive and len(win.drive) == 2 and win.drive[1] == ":":
        path = Path("/mnt") / win.drive[0].lower() / Path(*win.parts[1:])
    else:
        path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path


def main() -> None:
    source = resolve_root(read_local_config(ROOT).get("COMMONLIBSSE_ROOT", "").strip())
    if not source.is_dir():
        raise SystemExit("configured CommonLib source is unavailable")
    try:
        revision = subprocess.run(
            ["git", "-C", str(source), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        revision = "unknown"
    print(f"source_revision={revision}")

    targets = {
        "include/RE/A/Actor.h": (r"GetLevel\(|UseSkill\(", 5),
        "include/RE/P/PlayerCharacter.h": (
            r"AddSkillExperience|advanceSkill|LevelUp|levelUp|GetLevel|experience",
            5,
        ),
        "include/RE/T/TESActorBaseData.h": (r"GetLevel\(|actorData|level|PCLevelMult", 2),
        "include/RE/L/LevelUpMenu.h": (r".", 0),
        "include/RE/Offsets.h": (r"GetLevel|LevelUp|AddSkillExperience|AdvanceSkill", 2),
        "include/RE/Offsets_VTABLE.h": (r"VTABLE_LevelUpMenu|VTABLE___ConfirmLevelUpAttributeCallback", 1),
        "include/RE/Offsets_RTTI.h": (r"RTTI_LevelUpMenu|RTTI___ConfirmLevelUpAttributeCallback", 1),
    }
    for relative, (pattern, radius) in targets.items():
        path = source / relative
        if not path.is_file():
            print(f"MISSING {relative}")
            continue
        raw = path.read_bytes()
        lines = raw.decode("utf-8", errors="replace").splitlines()
        matcher = re.compile(pattern, re.IGNORECASE)
        selected: set[int] = set()
        for index, line in enumerate(lines):
            if matcher.search(line):
                selected.update(range(max(0, index - radius), min(len(lines), index + radius + 1)))
        print(f"\nFILE {relative} sha256={hashlib.sha256(raw).hexdigest()} line_count={len(lines)}")
        for index in sorted(selected):
            print(f"{index + 1}: {lines[index][:360]}")


if __name__ == "__main__":
    main()
