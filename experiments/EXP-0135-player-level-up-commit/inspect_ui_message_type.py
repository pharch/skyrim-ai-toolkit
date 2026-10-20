#!/usr/bin/env python3
"""Find the pinned CommonLib UI message type names without revealing machine paths."""
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
    include = source / "include/RE"
    if not include.is_dir():
        raise SystemExit("configured CommonLib include tree is unavailable")
    try:
        revision = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        revision = "unknown"
    print(f"source_revision={revision}")
    for path in include.rglob("*.h"):
        raw = path.read_bytes()
        lines = raw.decode("utf-8", errors="replace").splitlines()
        selected = [i for i, line in enumerate(lines) if re.search(r"UI_MESSAGE_TYPE|UIMessage::|enum class UI_MESSAGE", line)]
        if not selected:
            continue
        print(f"\nFILE {path.relative_to(source).as_posix()} sha256={hashlib.sha256(raw).hexdigest()}")
        keep: set[int] = set()
        for i in selected:
            keep.update(range(i, min(len(lines), i + 18)))
        for i in sorted(keep):
            print(f"{i + 1}: {lines[i][:300]}")


if __name__ == "__main__":
    main()
