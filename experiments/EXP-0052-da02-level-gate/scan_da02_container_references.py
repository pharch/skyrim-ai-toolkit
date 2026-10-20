#!/usr/bin/env python3
"""Find reference-bearing official-master fields that name QABooksContainer."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TARGET = 0x000C2D3B
OFFICIAL_PLUGINS = (
    "Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm",
)
REFERENCE_FIELDS = {
    "REFR": {"NAME"}, "ACHR": {"NAME"}, "CONT": {"CNTO"}, "QUST": {
        "ALFR", "ALUA", "ALFA", "ALRT", "ALEQ", "ALCO", "QTGL", "NNAM", "CNTO",
    }, "NPC_": {"CNTO"}, "LVLI": {"LVLO"}, "SMBN": {"PNAM", "SNAM"},
    "SMQN": {"PNAM", "SNAM", "NNAM"}, "SMEN": {"PNAM", "SNAM"},
    "PACK": {"QNAM", "PKID"},
}


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
        hashes[plugin] = hashlib.sha256(path.read_bytes()).hexdigest()
        for row in read_plugin(path, include_subrecords=True):
            wanted_fields = REFERENCE_FIELDS.get(row["signature"], set())
            for subrecord in row.get("subrecords", []):
                if subrecord["signature"] not in wanted_fields:
                    continue
                raw = bytes.fromhex(subrecord["value_hex"])
                if raw[:4] == TARGET.to_bytes(4, "little") or raw.find(TARGET.to_bytes(4, "little")) >= 0:
                    results.append({
                        "plugin": row["plugin"], "origin_plugin": row["origin_plugin"],
                        "signature": row["signature"], "form_id": row["file_form_id"],
                        "editor_id": row["editor_id"], "subrecord": subrecord["signature"],
                        "subrecord_hex": subrecord["value_hex"],
                    })
    print(json.dumps({
        "route": "read-only tools.plugin_reader; official five-master files only",
        "source_sha256": hashes,
        "target_form_id": f"{TARGET:08X}",
        "matches": results,
        "interpretation_limit": "The screen inspects selected reference-bearing fields; it is not a profile winner or runtime container-state check.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
