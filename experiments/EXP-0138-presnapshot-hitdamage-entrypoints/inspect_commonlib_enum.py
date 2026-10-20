#!/usr/bin/env python3
"""Read the configured primary CommonLib EntryPoint enum without exposing paths."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import _native_path

SELECTORS = {0x1A, 0x1C, 0x00, 0x23, 0x24, 0x12, 0x01, 0x11, 0x02, 0x55}
NEEDLES = (
    "enum class EntryPoint", "enum EntryPoint", "kModArmorRating",
    "kModIncoming", "kCalculateWeaponDamage", "kModTargetDamageResistance",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    cfg = read_local_config(ROOT)
    configured = cfg.get("COMMONLIBSSE_ROOT", "").strip()
    if not configured:
        raise SystemExit("COMMONLIBSSE_ROOT is not configured")
    source_root = _native_path(configured)
    include = source_root / "include"
    if not include.is_dir():
        raise SystemExit("configured CommonLib include directory is inaccessible")
    commit = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()

    matches = []
    enum_blocks = []
    for path in sorted(include.rglob("*.h")):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        relevant = [i for i, line in enumerate(lines) if any(needle in line for needle in NEEDLES)]
        for i, line in enumerate(lines):
            if "enum ENTRY_POINT" not in line:
                continue
            end = next((j + 1 for j in range(i + 1, len(lines)) if lines[j].strip() == "};"), len(lines))
            enum_blocks.append({
                "source_relative_path": path.relative_to(source_root).as_posix(),
                "source_sha256": digest(path),
                "start_line": i + 1,
                "lines": [{"line": j + 1, "text": lines[j].strip()} for j in range(i, end)],
            })
        if not relevant:
            continue
        selected = set()
        for i in relevant:
            selected.update(range(max(0, i - 3), min(len(lines), i + 4)))
        matches.append({
            "source_relative_path": path.relative_to(source_root).as_posix(),
            "source_sha256": digest(path),
            "matched_lines": [{"line": i + 1, "text": lines[i].strip()} for i in sorted(selected)],
        })

    out = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_commit": commit,
        "selector_values_screened": [f"0x{value:02X}" for value in sorted(SELECTORS)],
        "entrypoint_enum_blocks": enum_blocks,
        "matches": matches,
        "interpretation_limit": "CommonLib names are primary source labels for enum values, not proof that a selector is active or has a particular gameplay effect in the captured runtime.",
    }
    capture = ROOT / ".local/alignment/transactions/TX-20261020-0010/q91"
    capture.mkdir(parents=True, exist_ok=True)
    target = capture / "commonlib-entrypoint-enum.json"
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact": target.relative_to(ROOT).as_posix(),
        "sha256": digest(target),
        "source_commit": commit,
        "matched_files": [item["source_relative_path"] for item in matches],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
