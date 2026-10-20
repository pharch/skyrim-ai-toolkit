#!/usr/bin/env python3
"""Find exact Story Manager parent IDs across all five prepared official masters."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.local_config import read_local_config
from tools.plugin_reader import read_plugin

MASTERS = ("Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm")
TARGETS = {0x000896A8, 0x00090028, 0x0005BD79, 0x0003833D, 0x000B18E1, 0x000B48FB}


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def main() -> int:
    config = read_local_config(ROOT)
    configured = config.get("SKYRIM_DATA", "").strip()
    windows = PureWindowsPath(configured)
    if os.name != "nt" and windows.drive and windows.drive[1] == ":":
        data_root = Path("/mnt") / windows.drive[0].lower() / Path(*windows.parts[1:])
    else:
        data_root = Path(configured).expanduser()
    if not data_root.is_dir():
        raise SystemExit("configured prepared Skyrim Data directory is unavailable")
    results = []
    for master in MASTERS:
        path = data_root / master
        if not path.is_file():
            raise SystemExit(f"prepared master missing: {master}")
        rows = []
        record_count = 0
        for record in read_plugin(path):
            record_count += 1
            form_id = int(record["file_form_id"], 16)
            if form_id in TARGETS:
                rows.append({
                    "signature": record["signature"],
                    "form_id": record["file_form_id"],
                    "origin_plugin": record["origin_plugin"],
                    "editor_id": record["editor_id"],
                    "offset": record["offset"],
                })
        results.append({
            "plugin": master,
            "sha256": digest(path),
            "record_count": record_count,
            "matching_records": rows,
        })
    print(json.dumps({
        "targets": [f"{form_id:08X}" for form_id in sorted(TARGETS)],
        "source_scope": "five prepared official masters, exact record FormID lookup",
        "results": results,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
