#!/usr/bin/env python3
"""Find official LVLI records with a raw LVLO FormID reference to ARMO 000FC061.

Reads only the five official master files selected from config/local.env. The
output preserves raw LVLO bytes and source hashes; it does not infer runtime
inventory generation or resolve a profile-specific winner.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.local_config import read_local_config  # noqa: E402
from tools.ae_target import REQUIRED_AE_MASTERS, _native_path  # noqa: E402
from tools.plugin_reader import read_plugin  # noqa: E402

EXPECTED = {
    "Skyrim.esm": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
    "Update.esm": "c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9",
    "Dawnguard.esm": "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4",
    "HearthFires.esm": "ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97",
    "Dragonborn.esm": "5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b",
}
TARGET = 0x000FC061


def main() -> None:
    config = read_local_config(ROOT)
    data = _native_path(config.get("SKYRIM_DATA", ""))
    if not data.is_dir():
        raise SystemExit("configured Skyrim Data directory is inaccessible")
    files = []
    hits = []
    total_lists = 0
    needle = struct.pack("<I", TARGET)
    for plugin in REQUIRED_AE_MASTERS:
        path = data / plugin
        if not path.is_file():
            raise SystemExit("an official master is inaccessible")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != EXPECTED[plugin]:
            raise SystemExit("official master hash differs from EV-0398 input: " + plugin)
        files.append({"plugin": plugin, "sha256": digest})
        for row in read_plugin(path, "LVLI", include_subrecords=True):
            total_lists += 1
            for sub in row.get("subrecords", []):
                if sub.get("signature") != "LVLO":
                    continue
                raw = bytes.fromhex(sub["value_hex"])
                at = raw.find(needle)
                if at >= 0:
                    hits.append({
                        "source_plugin": plugin,
                        "signature": row["signature"],
                        "file_form_id": row["file_form_id"],
                        "origin_plugin": row["origin_plugin"],
                        "local_form_id": row["local_form_id"],
                        "editor_id": row["editor_id"],
                        "LVLO_length": len(raw),
                        "LVLO_hex": raw.hex(),
                        "target_bytes_offset": at,
                    })
    print(json.dumps({
        "route": "read-only TES4 direct parser; five official masters, not profile winners",
        "target_record": {"plugin": "Skyrim.esm", "signature": "ARMO", "form_id": f"{TARGET:08X}"},
        "source_files": files,
        "LVLI_records_scanned": total_lists,
        "direct_LVLO_references": hits,
        "interpretation_limit": "A raw LVLO membership proves list inclusion only; list nesting, requested level, item selection, vendor/container availability, and live level-one acquisition are not established by this scan.",
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
