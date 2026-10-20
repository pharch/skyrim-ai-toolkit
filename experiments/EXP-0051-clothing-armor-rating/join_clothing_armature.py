#!/usr/bin/env python3
"""Resolve ARMO Armature FormIDs to official ARMA records and armor types."""
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

PLUGINS = ("Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm")
ARMOR_TYPES = {0: "Light Armor", 1: "Heavy Armor", 2: "Clothing"}


def plugin_path(plugin: str) -> Path:
    value = read_local_config(ROOT).get("SKYRIM_DATA", "").strip()
    if not value:
        raise RuntimeError("SKYRIM_DATA is not configured")
    data = _native_path(value)
    if not data.is_absolute():
        data = ROOT / data
    result = data / plugin
    if not result.is_file():
        raise RuntimeError(f"configured official source is unavailable: {plugin}")
    return result


def body_type(row: dict) -> tuple[int | None, str | None]:
    subrecords = row["subrecords"]
    if row["signature"] == "ARMO":
        signature, offset, minimum = "BOD2", 4, 8
    else:
        # TES5Edit's ARMA BODT/BOD2 union places Armor Type after the
        # first-person flags, general flags, and three unused bytes.
        bod2 = [bytes.fromhex(item["value_hex"]) for item in subrecords if item["signature"] == "BOD2"]
        if bod2:
            signature, offset, minimum = "BOD2", 4, 8
        else:
            signature, offset, minimum = "BODT", 8, 12
    values = [bytes.fromhex(item["value_hex"]) for item in subrecords if item["signature"] == signature]
    if len(values) != 1 or len(values[0]) < minimum:
        return None, None
    value = struct.unpack_from("<I", values[0], offset)[0]
    return value, ARMOR_TYPES.get(value, f"unknown:{value}")


def main() -> int:
    sources = []
    armor_rows = []
    addon_rows = []
    by_file_form_id: dict[str, list[dict]] = {}
    for plugin in PLUGINS:
        path = plugin_path(plugin)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        armos = list(read_plugin(path, "ARMO", include_subrecords=True))
        armas = list(read_plugin(path, "ARMA", include_subrecords=True))
        armor_rows.extend(armos)
        for row in armas:
            row = dict(row)
            row["plugin"] = plugin
            row["armor_type_value"], row["armor_type"] = body_type(row)
            addon_rows.append(row)
            by_file_form_id.setdefault(row["file_form_id"], []).append(row)
        sources.append({"plugin": plugin, "sha256": digest, "armo_records": len(armos), "arma_records": len(armas)})

    candidates = []
    for row in armor_rows:
        armor_type, type_name = body_type(row)
        if armor_type != 2:
            continue
        subrecords = row["subrecords"]
        dnam = [bytes.fromhex(item["value_hex"]) for item in subrecords if item["signature"] == "DNAM"]
        if len(dnam) != 1 or len(dnam[0]) < 4:
            continue
        raw_rating = struct.unpack_from("<i", dnam[0])[0]
        if raw_rating <= 0:
            continue
        armature_refs = []
        for item in subrecords:
            if item["signature"] != "MODL":
                continue
            raw = bytes.fromhex(item["value_hex"])
            if len(raw) != 4:
                armature_refs.append({"raw_hex": raw.hex(), "error": "unexpected_reference_length"})
                continue
            form_id = struct.unpack("<I", raw)[0]
            linked = []
            for target in by_file_form_id.get(f"{form_id:08X}", []):
                linked.append({
                    "source_plugin": target["plugin"],
                    "source_form_id": target["file_form_id"],
                    "origin_plugin": target["origin_plugin"],
                    "local_form_id": target["local_form_id"],
                    "editor_id": target["editor_id"],
                    "armor_type_value": target["armor_type_value"],
                    "armor_type": target["armor_type"],
                })
            armature_refs.append({"form_id": f"{form_id:08X}", "matches": linked})
        candidates.append({
            "plugin": row["plugin"],
            "origin_plugin": row["origin_plugin"],
            "file_form_id": row["file_form_id"],
            "local_form_id": row["local_form_id"],
            "editor_id": row["editor_id"],
            "armor_type": type_name,
            "dnam_raw_s32": raw_rating,
            "armor_rating_schema_value": raw_rating / 100.0,
            "record_flags": row["flags"],
            "armature": armature_refs,
        })

    print(json.dumps({
        "tool": "EXP-0051 join_clothing_armature.py",
        "read_only": True,
        "profile_winner_resolved": False,
        "sources": sources,
        "total_arma_records": len(addon_rows),
        "positive_dnam_clothing_armo_records": len(candidates),
        "candidates": candidates,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, PluginFormatError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
