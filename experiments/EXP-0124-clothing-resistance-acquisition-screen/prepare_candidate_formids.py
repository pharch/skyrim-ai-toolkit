#!/usr/bin/env python3
"""Derive full official-master ARMO FormIDs from the EXP-0123 raw capture."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

MASTER_INDEX = {
    "skyrim.esm": 0,
    "update.esm": 1,
    "dawnguard.esm": 2,
    "hearthfires.esm": 3,
    "dragonborn.esm": 4,
}
TARGET_AVS = {40, 41, 42, 43, 44}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--ids-only", action="store_true", help="emit the sorted full FormID list for the reference scanner")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    path = args.capture if args.capture.is_absolute() else root / args.capture
    path = path.resolve()
    try:
        path.relative_to((root / ".local").resolve())
    except ValueError as exc:
        raise ValueError("input capture must remain below ignored .local/") from exc
    raw = path.read_bytes()
    capture = json.loads(raw)
    candidates: dict[str, dict] = {}
    for armor in capture.get("clothing_records", []):
        for effect in armor.get("enchantment_effects", []):
            mgef = effect.get("mgef") or {}
            data = mgef.get("data", {})
            av = data.get("primary_actor_value_s32")
            if av not in TARGET_AVS:
                continue
            record_id = str(armor.get("record_id", ""))
            origin, sep, local = record_id.partition(":")
            if not sep or origin.casefold() not in MASTER_INDEX or len(local) != 6:
                raise ValueError(f"unsupported source FormID identity: {record_id!r}")
            full_id = f"{MASTER_INDEX[origin.casefold()]:02X}{int(local, 16):06X}"
            row = candidates.setdefault(full_id, {
                "form_id": full_id,
                "origin_plugin": origin,
                "record_id": record_id,
                "winning_source_plugin": armor.get("winning_source_plugin"),
                "editor_id": armor.get("editor_id"),
                "type_field": armor.get("body_template_signature"),
                "dnam_rating_raw_s32": armor.get("dnam_rating_raw_s32"),
                "enchantment_id": armor.get("enchantment_id"),
                "enchantment_editor_id": armor.get("enchantment_editor_id"),
                "resistance_effects": [],
            })
            item = {
                "mgef_id": effect.get("mgef_id"),
                "mgef_editor_id": mgef.get("editor_id"),
                "primary_actor_value_s32": av,
                "magnitude": effect.get("magnitude"),
                "enchantment_condition_count": len(effect.get("conditions", [])),
                "mgef_condition_count": len(mgef.get("conditions", [])),
            }
            if item not in row["resistance_effects"]:
                row["resistance_effects"].append(item)
    output = {
        "capture_sha256": hashlib.sha256(raw).hexdigest(),
        "source_files": capture.get("source_files"),
        "candidate_definition": "Clothing ARMO with linked MGEF primary AV 40-44",
        "candidate_count": len(candidates),
        "candidates": sorted(candidates.values(), key=lambda row: row["form_id"]),
        "read_only": True,
        "profile_winner_resolved": False,
    }
    print(json.dumps([row["form_id"] for row in output["candidates"]] if args.ids_only else output,
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
