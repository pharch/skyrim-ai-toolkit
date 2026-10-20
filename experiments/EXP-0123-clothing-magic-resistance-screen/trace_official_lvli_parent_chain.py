#!/usr/bin/env python3
"""Trace official LVLI parent entries for the Resist Magic necklace by LVLO FormID."""
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
START = ("Skyrim.esm", "0FC061")


def key_text(key: tuple[str, str]) -> str:
    return f"{key[0]}:{key[1]}"


def main() -> None:
    config = read_local_config(ROOT)
    data = _native_path(config.get("SKYRIM_DATA", ""))
    if not data.is_dir():
        raise SystemExit("configured Skyrim Data directory is inaccessible")
    source_files = []
    records = []
    for plugin in REQUIRED_AE_MASTERS:
        path = data / plugin
        if not path.is_file():
            raise SystemExit("an official master is inaccessible")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != EXPECTED[plugin]:
            raise SystemExit("official master hash differs from EV-0398 input: " + plugin)
        source_files.append({"plugin": plugin, "sha256": digest})
        header = next(read_plugin(path, "TES4", include_subrecords=True))
        masters = [s["text_cp1252"].rstrip("\0") for s in header["subrecords"] if s["signature"] == "MAST"]
        for row in read_plugin(path, "LVLI", include_subrecords=True):
            list_key = (row["origin_plugin"], row["local_form_id"].upper())
            for sub in row.get("subrecords", []):
                if sub.get("signature") != "LVLO":
                    continue
                raw = bytes.fromhex(sub["value_hex"])
                if len(raw) < 12:
                    continue
                raw_form_id = struct.unpack_from("<I", raw, 4)[0]
                origin_index = raw_form_id >> 24
                form_plugins = masters + [plugin]
                origin = form_plugins[origin_index] if origin_index < len(form_plugins) else "UNRESOLVED"
                target_key = (origin, f"{raw_form_id & 0x00FFFFFF:06X}")
                level = struct.unpack_from("<H", raw, 0)[0]
                level_unknown = raw[2:4].hex()
                count = struct.unpack_from("<H", raw, 8)[0]
                count_unknown = raw[10:12].hex()
                records.append({
                    "list_key": list_key,
                    "list_file_form_id": row["file_form_id"],
                    "list_editor_id": row["editor_id"],
                    "target_key": target_key,
                    "level_u16": level,
                    "level_unknown_hex": level_unknown,
                    "count_u16": count,
                    "count_unknown_hex": count_unknown,
                    "LVLO_length": len(raw),
                    "LVLO_hex": raw.hex(),
                    "source_plugin": plugin,
                })
    by_target: dict[tuple[str, str], list[dict]] = {}
    for row in records:
        by_target.setdefault(row["target_key"], []).append(row)
    levels = {START}
    seen = {START}
    chain = []
    while levels:
        child = levels.pop()
        for edge in by_target.get(child, []):
            if edge["list_key"] == child:
                continue
            chain.append({
                "parent_list": key_text(edge["list_key"]),
                "parent_file_form_id": edge["list_file_form_id"],
                "parent_editor_id": edge["list_editor_id"],
                "child": key_text(child),
                "level_u16": edge["level_u16"],
                "level_unknown_hex": edge["level_unknown_hex"],
                "count_u16": edge["count_u16"],
                "count_unknown_hex": edge["count_unknown_hex"],
                "LVLO_hex": edge["LVLO_hex"],
                "source_plugin": edge["source_plugin"],
            })
            if edge["list_key"] not in seen:
                seen.add(edge["list_key"])
                levels.add(edge["list_key"])
    print(json.dumps({
        "route": "read-only TES4 parser; LVLI entries only, five official masters; not a profile winner",
        "start_item": {"key": key_text(START), "editor_id": "EnchNecklaceResistMagic01"},
        "LVLO_layout": "Cross-checked against configured read-only xEdit schema tmp/wbDefinitionsTES5.pas (SHA-256 a148b391f175d5cd6af102d6fbb8594e19dcd92916802fe1086eda1fc873356b): Level is u16 at bytes 0-1, bytes 2-3 are unknown, Reference FormID is bytes 4-7, Count is u16 at bytes 8-9, and bytes 10-11 are unknown. The raw target rows decode to levels 8-11.",
        "source_files": source_files,
        "LVLI_entry_count": len(records),
        "LVLI_parent_chain": chain,
        "reachable_parent_list_keys": sorted(key_text(k) for k in seen),
        "limit": "This follows LVLI nesting only. It does not identify which world container/NPC requests a root list, requested level, probability, vendor stock, or live level-one result.",
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
