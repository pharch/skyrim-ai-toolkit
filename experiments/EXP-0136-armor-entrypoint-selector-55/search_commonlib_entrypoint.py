#!/usr/bin/env python3
"""Find local primary CommonLib enum labels for Q89 without exposing machine paths."""
from __future__ import annotations
import hashlib
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.local_config import read_local_config
from tools.ae_target import _native_path

config=read_local_config(ROOT)
value=config.get("COMMONLIBSSE_ROOT", "").strip()
if not value:
    print("COMMONLIBSSE_ROOT is not configured")
    raise SystemExit(0)
source_root=_native_path(value)
if not source_root.is_dir():
    print("COMMONLIBSSE_ROOT is configured but inaccessible")
    raise SystemExit(0)
try:
    commit=subprocess.run(["git", "-C", str(source_root), "rev-parse", "HEAD"],check=True,capture_output=True,text=True).stdout.strip()
except Exception:
    commit="unavailable"
print("source_commit="+commit)
include=source_root/"include"
needles=("ModArmorRating", "kModArmorRating", "ENTRY_POINT", "ModArmorRating", "ArmorRating")
matched=0
for path in sorted(include.rglob("*.h")):
    try:
        lines=path.read_text(encoding="utf-8",errors="replace").splitlines()
    except OSError:
        continue
    found=[(i+1,line.strip()) for i,line in enumerate(lines) if any(n in line for n in needles)]
    if not found:
        continue
    matched+=len(found)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    rel=path.relative_to(source_root).as_posix()
    print(f"file={rel} sha256={digest}")
    for number,line in found:
        print(f"  {number}: {line}")
print(f"matching_lines={matched}")
