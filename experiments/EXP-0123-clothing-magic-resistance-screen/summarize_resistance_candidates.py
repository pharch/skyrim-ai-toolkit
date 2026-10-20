#!/usr/bin/env python3
"""Summarize source-captured Clothing ENCH effects that target resistance AVs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

AV_NAMES = {
    39: "Damage Resist",
    40: "Poison Resist",
    41: "Resist Fire",
    42: "Resist Shock",
    43: "Resist Frost",
    44: "Resist Magic",
}
ARCHETYPES = {0: "Value Modifier", 4: "Absorb", 5: "Dual Value Modifier", 34: "Peak Value Modifier"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    args = parser.parse_args()
    capture_path = args.capture
    if not capture_path.is_absolute():
        capture_path = Path.cwd() / capture_path
    capture_path = capture_path.resolve()
    root = Path(__file__).resolve().parents[2]
    try:
        capture_path.relative_to(root / ".local")
    except ValueError as exc:
        raise ValueError("input capture must remain below ignored .local/") from exc
    raw = capture_path.read_bytes()
    capture = json.loads(raw)

    rows = []
    for item in capture.get("clothing_records", []):
        for effect in item.get("enchantment_effects", []):
            mgef = effect.get("mgef") or {}
            data = mgef.get("data", {})
            av = data.get("primary_actor_value_s32")
            mgef_name = mgef.get("editor_id", "")
            if av not in AV_NAMES and "resist" not in mgef_name.casefold():
                continue
            arch = data.get("archetype_u32")
            rows.append({
                "armor_id": item["record_id"],
                "armor_source_plugin": item["winning_source_plugin"],
                "armor_editor_id": item["editor_id"],
                "armor_type_field": item["body_template_signature"],
                "armor_rating_raw_s32": item["dnam_rating_raw_s32"],
                "enchantment_id": item["enchantment_id"],
                "enchantment_editor_id": item["enchantment_editor_id"],
                "enit_cast_type": item["enchantment_enit"].get("cast_type_u32"),
                "enit_delivery": item["enchantment_enit"].get("delivery_u32"),
                "mgef_id": effect.get("mgef_id"),
                "mgef_editor_id": mgef_name,
                "mgef_archetype": ARCHETYPES.get(arch, f"unknown:{arch}"),
                "mgef_primary_actor_value": AV_NAMES.get(av, av),
                "mgef_resist_value": data.get("resist_value_s32"),
                "magnitude": effect.get("magnitude"),
                "area": effect.get("area"),
                "duration": effect.get("duration"),
                "enchantment_effect_condition_count": len(effect.get("conditions", [])),
                "mgef_condition_count": len(mgef.get("conditions", [])),
            })
    print(json.dumps({
        "capture_sha256": hashlib.sha256(raw).hexdigest(),
        "record_resolution": capture.get("record_resolution"),
        "source_files": capture.get("source_files"),
        "winning_clothing_count": capture.get("winning_clothing_count"),
        "unclassified_armor_records": capture.get("unclassified_armor_records"),
        "resistance_effect_chains": rows,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
