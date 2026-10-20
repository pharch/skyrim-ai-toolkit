#!/usr/bin/env python3
"""Find official records that reference the citizen-pocket and necklace LVLIs."""
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
TARGETS = {
    "Skyrim.esm:001046D1": 0x001046D1,  # LootCitizenPocketsCommon
    "Skyrim.esm:001046D3": 0x001046D3,  # LootCitizenPocketsRich
    "Skyrim.esm:001046DD": 0x001046DD,  # LootCitizenNecklaceList
    "Skyrim.esm:00101071": 0x00101071,  # LItemEnchNecklaceAll
    "Skyrim.esm:0010106C": 0x0010106C,  # LItemEnchNecklaceResistMagic
}


def main() -> None:
    config = read_local_config(ROOT)
    data = _native_path(config.get("SKYRIM_DATA", ""))
    if not data.is_dir():
        raise SystemExit("configured Skyrim Data directory is inaccessible")
    source_files = []
    targets = {label: struct.pack("<I", value) for label, value in TARGETS.items()}
    hits = []
    signatures = {}
    for plugin in REQUIRED_AE_MASTERS:
        path = data / plugin
        if not path.is_file():
            raise SystemExit("an official master is inaccessible")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != EXPECTED[plugin]:
            raise SystemExit("official master hash differs from EV-0398 input: " + plugin)
        source_files.append({"plugin": plugin, "sha256": digest})
        for row in read_plugin(path, include_subrecords=True):
            signatures[row["signature"]] = signatures.get(row["signature"], 0) + 1
            for sub in row.get("subrecords", []):
                raw = bytes.fromhex(sub["value_hex"])
                for label, needle in targets.items():
                    pos = raw.find(needle)
                    if pos >= 0:
                        hits.append({
                            "target": label,
                            "owner_plugin": plugin,
                            "owner_signature": row["signature"],
                            "owner_file_form_id": row["file_form_id"],
                            "owner_origin_plugin": row["origin_plugin"],
                            "owner_local_form_id": row["local_form_id"],
                            "owner_editor_id": row["editor_id"],
                            "subrecord": sub["signature"],
                            "subrecord_offset": pos,
                            "subrecord_length": len(raw),
                        })
    allowed = {"NPC_", "LVLN", "CONT", "REFR", "ACHR", "LVLI", "FLST", "QUST", "PACK", "DIAL"}
    selected = [h for h in hits if h["owner_signature"] in allowed]
    print(json.dumps({
        "route": "read-only TES4 parser; exact five official master hashes; not a profile winner",
        "source_files": source_files,
        "total_record_signatures_scanned": sum(signatures.values()),
        "reference_hits": selected,
        "other_signature_hit_count": len(hits) - len(selected),
        "signature_counts": {k: signatures[k] for k in sorted(allowed) if k in signatures},
        "limit": "Raw reference occurrence identifies a record field containing the list FormID, not whether the referenced list is selected during play or how its requested level is supplied.",
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
