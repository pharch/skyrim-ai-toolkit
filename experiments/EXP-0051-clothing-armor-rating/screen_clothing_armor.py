#!/usr/bin/env python3
"""Read-only five-master census of Clothing-class positive-rating ARMO records."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import _native_path
from tools.plugin_reader import PluginFormatError, read_plugin

PLUGINS = (
    "Skyrim.esm",
    "Update.esm",
    "Dawnguard.esm",
    "HearthFires.esm",
    "Dragonborn.esm",
)
ARMOR_TYPES = {0: "Light Armor", 1: "Heavy Armor", 2: "Clothing"}
ARMO_NON_PLAYABLE = 0x00000004  # TES5Edit ARMO record flag bit index 2.


def source_path(plugin: str) -> Path:
    config = read_local_config(ROOT)
    value = config.get("SKYRIM_DATA", "").strip()
    if not value:
        raise RuntimeError("SKYRIM_DATA is not configured")
    path = _native_path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = path / plugin
    if not path.is_file():
        raise RuntimeError(f"configured official source is unavailable: {plugin}")
    return path


def main() -> int:
    sources = []
    all_candidates = []
    malformed = []
    for plugin in PLUGINS:
        path = source_path(plugin)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        type_counts: dict[str, int] = {}
        record_count = 0
        positive_clothing = 0
        playable_clothing = 0
        for row in read_plugin(path, "ARMO", include_subrecords=True):
            record_count += 1
            subrecords = row["subrecords"]
            bod2_values = [bytes.fromhex(value["value_hex"]) for value in subrecords if value["signature"] == "BOD2"]
            dnam_values = [bytes.fromhex(value["value_hex"]) for value in subrecords if value["signature"] == "DNAM"]
            if len(bod2_values) != 1 or len(bod2_values[0]) < 8:
                malformed.append({"plugin": plugin, "local_form_id": row["local_form_id"], "editor_id": row["editor_id"], "reason": "missing_or_nonstandard_BOD2"})
                continue
            armor_type = struct.unpack_from("<I", bod2_values[0], 4)[0]
            type_name = ARMOR_TYPES.get(armor_type, f"unknown:{armor_type}")
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
            if armor_type != 2:
                continue
            if len(dnam_values) != 1 or len(dnam_values[0]) < 4:
                malformed.append({"plugin": plugin, "local_form_id": row["local_form_id"], "editor_id": row["editor_id"], "reason": "missing_or_nonstandard_DNAM"})
                continue
            raw_rating = struct.unpack_from("<i", dnam_values[0])[0]
            if raw_rating <= 0:
                continue
            positive_clothing += 1
            flags = int(row["flags"], 16)
            non_playable = bool(flags & ARMO_NON_PLAYABLE)
            if not non_playable:
                playable_clothing += 1
            keywords = []
            for value in subrecords:
                if value["signature"] == "KWDA":
                    raw = bytes.fromhex(value["value_hex"])
                    keywords.extend(f"{int.from_bytes(raw[i:i + 4], 'little'):08X}" for i in range(0, len(raw) - 3, 4))
            all_candidates.append({
                "plugin": plugin,
                "origin_plugin": row["origin_plugin"],
                "local_form_id": row["local_form_id"],
                "file_form_id": row["file_form_id"],
                "editor_id": row["editor_id"],
                "record_flags": row["flags"],
                "non_playable": non_playable,
                "armor_type_value": armor_type,
                "armor_type": type_name,
                "dnam_raw_s32": raw_rating,
                "armor_rating_schema_value": raw_rating / 100.0,
                "bod2_hex": bod2_values[0].hex(),
                "keywords": keywords,
            })
        sources.append({
            "plugin": plugin,
            "sha256": digest,
            "armo_record_count": record_count,
            "armor_type_counts": type_counts,
            "positive_dnam_clothing_count": positive_clothing,
            "positive_dnam_clothing_without_nonplayable_flag": playable_clothing,
        })
    all_candidates.sort(key=lambda row: (row["plugin"], row["editor_id"], row["local_form_id"]))
    result = {
        "tool": "EXP-0051 screen_clothing_armor.py",
        "read_only": True,
        "profile_winner_resolved": False,
        "parser": "tools.plugin_reader.read_plugin",
        "source_scope": "five configured official masters",
        "sources": sources,
        "total_positive_dnam_clothing_records": len(all_candidates),
        "total_without_nonplayable_flag": sum(not row["non_playable"] for row in all_candidates),
        "candidates": all_candidates,
        "records_with_missing_or_nonstandard_fields": malformed,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, PluginFormatError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
