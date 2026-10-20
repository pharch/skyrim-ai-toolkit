#!/usr/bin/env python3
"""Find exact Story Manager node FormIDs across the five official masters."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PureWindowsPath
import os
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TARGET_IDS = {
    0x00101732, 0x000896A8, 0x000896A9,
    0x0009CB5F, 0x02014CBA, 0x020331C1,
    0x0000A603, 0x0000A604, 0x0000A605, 0x0000A606,
    0x0004A603, 0x0004A604, 0x0004A605, 0x0004A606,
    0x000B8EC1, 0x0009A543, 0x0004A600, 0x001027A6,
}
OFFICIAL_PLUGINS = (
    "Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm",
)


def native_path(value: str) -> Path:
    win = PureWindowsPath(value)
    if os.name != "nt" and win.drive and len(win.drive) == 2 and win.drive[1] == ":":
        return Path("/mnt") / win.drive[0].lower() / Path(*win.parts[1:])
    return Path(value).expanduser()


def main() -> int:
    from scripts.local_config import read_local_config
    from tools.plugin_reader import read_plugin

    data_dir = native_path(read_local_config(ROOT)["SKYRIM_DATA"])
    results: list[dict[str, object]] = []
    hashes: dict[str, str] = {}
    for plugin in OFFICIAL_PLUGINS:
        path = data_dir / plugin
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes[plugin] = digest
        for row in read_plugin(path, include_subrecords=True):
            if int(row["file_form_id"], 16) in TARGET_IDS:
                results.append(row)
    print(json.dumps({
        "route": "read-only tools.plugin_reader record inventory; official five-master files only",
        "source_sha256": hashes,
        "target_form_ids": [f"{value:08X}" for value in sorted(TARGET_IDS)],
        "matching_story_nodes": results,
        "interpretation_limit": "This is a record-identity lookup, not a profile winner or xEdit export.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
