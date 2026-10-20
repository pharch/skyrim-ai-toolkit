#!/usr/bin/env python3
"""Read official NPC inventory-list owners and preserve their ACBS level fields."""
from __future__ import annotations

import argparse
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
    ("Skyrim.esm", "001046D1"): "LootCitizenPocketsCommon",
    ("Skyrim.esm", "001046D3"): "LootCitizenPocketsRich",
    ("Skyrim.esm", "001046DD"): "LootCitizenNecklaceList",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="ignored .local JSON capture path")
    args = parser.parse_args()
    config = read_local_config(ROOT)
    data = _native_path(config.get("SKYRIM_DATA", ""))
    if not data.is_dir():
        raise SystemExit("configured Skyrim Data directory is inaccessible")

    source_files = []
    owners = []
    scanned_npcs = 0
    for plugin in REQUIRED_AE_MASTERS:
        path = data / plugin
        if not path.is_file():
            raise SystemExit("an official master is inaccessible")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != EXPECTED[plugin]:
            raise SystemExit("official master hash differs from the Q80 record scan: " + plugin)
        source_files.append({"plugin": plugin, "sha256": digest})
        header = next(read_plugin(path, "TES4", include_subrecords=True))
        masters = [
            item["text_cp1252"].rstrip("\0")
            for item in header["subrecords"]
            if item["signature"] == "MAST"
        ]
        for row in read_plugin(path, "NPC_", include_subrecords=True):
            scanned_npcs += 1
            refs = []
            for sub in row.get("subrecords", []):
                if sub.get("signature") != "CNTO":
                    continue
                raw = bytes.fromhex(sub["value_hex"])
                if len(raw) < 4:
                    continue
                form_id = struct.unpack_from("<I", raw, 0)[0]
                index = form_id >> 24
                # In TES4 FormIDs, the source plugin occupies the index after
                # the listed masters; Skyrim.esm has no MAST entries, so its
                # own base-game FormIDs use index zero.
                form_plugins = masters + [plugin]
                origin = form_plugins[index] if index < len(form_plugins) else "UNRESOLVED"
                key = (origin, f"{form_id & 0x00FFFFFF:08X}")
                if key in TARGETS:
                    refs.append({
                        "target": f"{origin}:{key[1]}",
                        "target_editor_id": TARGETS[key],
                        "CNTO_hex": raw.hex(),
                    })
            if not refs:
                continue

            acbs = next(
                (bytes.fromhex(sub["value_hex"]) for sub in row.get("subrecords", []) if sub.get("signature") == "ACBS"),
                b"",
            )
            if len(acbs) < 14:
                level_fields = {"parse_status": "ACBS absent_or_short", "ACBS_hex": acbs.hex()}
            else:
                flags = struct.unpack_from("<I", acbs, 0)[0]
                raw_level = struct.unpack_from("<h", acbs, 8)[0]
                calc_min = struct.unpack_from("<H", acbs, 10)[0]
                calc_max = struct.unpack_from("<H", acbs, 12)[0]
                level_fields = {
                    "parse_status": "schema_offsets_only",
                    "ACBS_hex": acbs.hex(),
                    "flags_u32": flags,
                    "auto_calc_stats_flag": bool(flags & 0x10),
                    "pc_level_mult_flag": bool(flags & 0x80),
                    "level_s16_or_mult": raw_level,
                    "calc_min_level_u16": calc_min,
                    "calc_max_level_u16": calc_max,
                    "interpretation_limit": "These are NPC record ACBS fields, not proof of the level supplied to a runtime leveled-list request.",
                }
            owners.append({
                "plugin": plugin,
                "file_form_id": row["file_form_id"],
                "origin_plugin": row["origin_plugin"],
                "local_form_id": row["local_form_id"],
                "editor_id": row["editor_id"],
                "inventory_list_references": refs,
                "ACBS": level_fields,
            })

    output = {
        "route": "read-only TES4 parser; five official masters; NPC CNTO references and ACBS raw fields; not a profile winner or runtime leveled-list request observation",
        "source_files": source_files,
        "official_NPC_records_scanned": scanned_npcs,
        "target_lists": {f"{p}:{fid}": name for (p, fid), name in TARGETS.items()},
        "owner_record_count": len(owners),
        "owners": owners,
    }
    dest = Path(args.output)
    if not dest.is_absolute():
        dest = ROOT / dest
    if ".local" not in dest.parts:
        raise SystemExit("raw capture destination must be below ignored .local/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    owners_by_list = {
        name: sum(any(ref["target_editor_id"] == name for ref in owner["inventory_list_references"]) for owner in owners)
        for name in TARGETS.values()
    }
    fixed_level_records = [
        o for o in owners
        if not o["ACBS"].get("pc_level_mult_flag") and o["ACBS"].get("level_s16_or_mult", -1) >= 8
    ]
    pc_mult_minimum_records = [
        o for o in owners
        if o["ACBS"].get("pc_level_mult_flag") and o["ACBS"].get("calc_min_level_u16", 0) >= 8
    ]
    print(json.dumps({
        "capture": dest.relative_to(ROOT).as_posix(),
        "owner_record_count": len(owners),
        "owners_by_target_list": owners_by_list,
        "record_level_field_at_least_8_with_PCLevelMult_off_count": len(fixed_level_records),
        "PCLevelMult_records_with_calc_min_at_least_8_count": len(pc_mult_minimum_records),
        "record_field_examples_only_not_runtime_request_levels": [
            {"plugin": o["plugin"], "form_id": o["file_form_id"], "editor_id": o["editor_id"], "ACBS": o["ACBS"]}
            for o in (fixed_level_records + pc_mult_minimum_records)
        ][:25],
        "capture_sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
