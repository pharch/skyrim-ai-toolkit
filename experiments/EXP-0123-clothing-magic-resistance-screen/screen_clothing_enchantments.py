#!/usr/bin/env python3
"""Read-only five-master Clothing ARMO -> ENCH -> MGEF source census."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
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
from tools.plugin_reader import PluginFormatError, read_plugin, resolve_record_winner

PLUGINS = (
    "Skyrim.esm",
    "Update.esm",
    "Dawnguard.esm",
    "HearthFires.esm",
    "Dragonborn.esm",
)
ARMOR_TYPES = {0: "Light Armor", 1: "Heavy Armor", 2: "Clothing"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def source_root() -> Path:
    config = read_local_config(ROOT)
    value = config.get("SKYRIM_DATA", "").strip()
    if not value:
        raise RuntimeError("SKYRIM_DATA is not configured")
    path = _native_path(value)
    if not path.is_absolute():
        path = ROOT / path
    if not path.is_dir():
        raise RuntimeError("configured official data directory is unavailable")
    return path


def get_subrecords(row: dict, signature: str) -> list[dict]:
    return [sub for sub in row.get("subrecords", []) if sub["signature"] == signature]


def id_key(origin: str, local_form_id: str) -> tuple[str, str]:
    return origin.casefold(), local_form_id.upper()


def canonical_id(key: tuple[str, str]) -> str:
    return f"{key[0]}:{key[1]}"


def row_key(row: dict) -> tuple[str, str]:
    return id_key(row["origin_plugin"], row["local_form_id"])


def masters_by_plugin(paths: dict[str, Path]) -> dict[str, list[str]]:
    result = {}
    for plugin, path in paths.items():
        tes4 = next(read_plugin(path, "TES4", include_subrecords=True))
        result[plugin.casefold()] = [
            sub["text_cp1252"] for sub in get_subrecords(tes4, "MAST")
        ]
    return result


def resolve_ref(raw: bytes, plugin: str, masters: dict[str, list[str]]) -> tuple[str, str] | None:
    if len(raw) != 4:
        return None
    form_id = struct.unpack("<I", raw)[0]
    if form_id == 0:
        return None
    table = masters[plugin.casefold()] + [Path(plugin).name]
    index = form_id >> 24
    if index >= len(table):
        return None
    return id_key(table[index], f"{form_id & 0x00FFFFFF:06X}")


def winner_index(paths: dict[str, Path], signature: str) -> tuple[dict[tuple[str, str], dict], dict[str, int]]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    counts = {}
    for plugin, path in paths.items():
        rows = list(read_plugin(path, signature, include_subrecords=True))
        counts[plugin] = len(rows)
        for row in rows:
            grouped[row_key(row)].append(row)
    winners = {
        key: resolve_record_winner(rows, list(PLUGINS))
        for key, rows in grouped.items()
    }
    return winners, counts


def raw_subrecords(row: dict) -> list[dict]:
    return [
        {"signature": sub["signature"], "length": sub["length"], "value_hex": sub["value_hex"]}
        for sub in row.get("subrecords", [])
    ]


def parse_effects(ench: dict, masters: dict[str, list[str]], mgefs: dict[tuple[str, str], dict]) -> list[dict]:
    effects = []
    current = None
    for sub in ench.get("subrecords", []):
        if sub["signature"] == "EFID":
            ref = resolve_ref(bytes.fromhex(sub["value_hex"]), ench["plugin"], masters)
            current = {
                "mgef_id": canonical_id(ref) if ref else None,
                "efid_hex": sub["value_hex"],
                "efit_hex": None,
                "magnitude": None,
                "area": None,
                "duration": None,
                "conditions": [],
            }
            effects.append(current)
        elif sub["signature"] == "EFIT" and current is not None:
            raw = bytes.fromhex(sub["value_hex"])
            current["efit_hex"] = sub["value_hex"]
            if len(raw) >= 12:
                current["magnitude"] = struct.unpack_from("<f", raw, 0)[0]
                current["area"] = struct.unpack_from("<I", raw, 4)[0]
                current["duration"] = struct.unpack_from("<I", raw, 8)[0]
        elif sub["signature"] == "CTDA" and current is not None:
            current["conditions"].append({"length": sub["length"], "value_hex": sub["value_hex"]})

    for effect in effects:
        ref = effect["mgef_id"]
        key = tuple(ref.split(":", 1)) if ref else None
        target = mgefs.get(key) if key else None
        if target is None:
            effect["mgef"] = None
            continue
        data = get_subrecords(target, "DATA")
        raw = bytes.fromhex(data[-1]["value_hex"]) if data else b""
        decoded = {"data_length": len(raw), "data_hex": raw.hex() if raw else None}
        if len(raw) >= 72:
            decoded.update({
                "flags_u32": struct.unpack_from("<I", raw, 0)[0],
                "magic_skill_s32": struct.unpack_from("<i", raw, 12)[0],
                "resist_value_s32": struct.unpack_from("<i", raw, 16)[0],
                "archetype_u32": struct.unpack_from("<I", raw, 64)[0],
                "primary_actor_value_s32": struct.unpack_from("<i", raw, 68)[0],
            })
        if len(raw) >= 92:
            decoded["second_actor_value_s32"] = struct.unpack_from("<i", raw, 88)[0]
        effect["mgef"] = {
            "source_plugin": target["plugin"],
            "form_id": target["file_form_id"],
            "editor_id": target["editor_id"],
            "full_name": next((s["text_cp1252"] for s in get_subrecords(target, "FULL")), ""),
            "data": decoded,
            "conditions": [
                {"length": s["length"], "value_hex": s["value_hex"]}
                for s in get_subrecords(target, "CTDA")
            ],
            "raw_subrecords": raw_subrecords(target),
        }
    return effects


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write the raw JSON capture below the repository's ignored .local directory")
    args = parser.parse_args()

    data_root = source_root()
    paths = {plugin: data_root / plugin for plugin in PLUGINS}
    missing = [plugin for plugin, path in paths.items() if not path.is_file()]
    if missing:
        raise RuntimeError("configured official source is unavailable for: " + ", ".join(missing))
    source_manifest = [
        {"plugin": plugin, "sha256": digest(path), "size_bytes": path.stat().st_size}
        for plugin, path in paths.items()
    ]
    masters = masters_by_plugin(paths)
    armos, armo_counts = winner_index(paths, "ARMO")
    enchs, ench_counts = winner_index(paths, "ENCH")
    mgefs, mgef_counts = winner_index(paths, "MGEF")

    clothing = []
    unclassified = []
    for key, row in sorted(armos.items()):
        bod2 = get_subrecords(row, "BOD2")
        bodt = get_subrecords(row, "BODT")
        if len(bod2) == 1 and not bodt:
            template_sig = "BOD2"
            template = bytes.fromhex(bod2[0]["value_hex"])
            type_offset = 4
            minimum = 8
        elif len(bodt) == 1 and not bod2:
            template_sig = "BODT"
            template = bytes.fromhex(bodt[0]["value_hex"])
            type_offset = 8
            minimum = 12
        else:
            unclassified.append({
                "record_id": canonical_id(key),
                "bod2_count": len(bod2),
                "bodt_count": len(bodt),
                "reason": "missing_or_ambiguous_body_template",
            })
            continue
        if len(template) < minimum:
            unclassified.append({
                "record_id": canonical_id(key),
                "body_template": template_sig,
                "length": len(template),
                "reason": "short_body_template",
            })
            continue
        armor_type = struct.unpack_from("<I", template, type_offset)[0]
        if armor_type != 2:
            continue
        dnam = get_subrecords(row, "DNAM")
        raw_dnam = bytes.fromhex(dnam[-1]["value_hex"]) if dnam else b""
        enchantment = get_subrecords(row, "EITM")
        ench_key = resolve_ref(bytes.fromhex(enchantment[-1]["value_hex"]), row["plugin"], masters) if enchantment else None
        ench = enchs.get(ench_key) if ench_key else None
        raw_enit = bytes.fromhex(get_subrecords(ench, "ENIT")[-1]["value_hex"]) if ench and get_subrecords(ench, "ENIT") else b""
        enit = {"length": len(raw_enit), "hex": raw_enit.hex() if raw_enit else None}
        if len(raw_enit) >= 24:
            enit.update({
                "cost_s32": struct.unpack_from("<i", raw_enit, 0)[0],
                "flags_u32": struct.unpack_from("<I", raw_enit, 4)[0],
                "cast_type_u32": struct.unpack_from("<I", raw_enit, 8)[0],
                "enchantment_amount_s32": struct.unpack_from("<i", raw_enit, 12)[0],
                "delivery_u32": struct.unpack_from("<I", raw_enit, 16)[0],
                "enchant_type_u32": struct.unpack_from("<I", raw_enit, 20)[0],
            })
        chains = parse_effects(ench, masters, mgefs) if ench else []
        clothing.append({
            "record_id": canonical_id(key),
            "winning_source_plugin": row["plugin"],
            "file_form_id": row["file_form_id"],
            "editor_id": row["editor_id"],
            "full_name": next((s["text_cp1252"] for s in get_subrecords(row, "FULL")), ""),
            "body_template_signature": template_sig,
            "body_template_hex": template.hex(),
            "armor_type_value": armor_type,
            "dnam_hex": dnam[-1]["value_hex"] if dnam else None,
            "dnam_rating_raw_s32": struct.unpack_from("<i", raw_dnam, 0)[0] if len(raw_dnam) >= 4 else None,
            "enchantment_id": canonical_id(ench_key) if ench_key else None,
            "enchantment_winner_plugin": ench["plugin"] if ench else None,
            "enchantment_editor_id": ench["editor_id"] if ench else None,
            "enchantment_enit": enit,
            "enchantment_effects": chains,
            "unresolved_enchantment_reference": bool(ench_key and not ench),
            "enchantment_raw_subrecords": raw_subrecords(ench) if ench else [],
        })

    effect_counts = Counter()
    actor_value_counts = Counter()
    effect_names = Counter()
    for item in clothing:
        for effect in item["enchantment_effects"]:
            effect_counts["total"] += 1
            if effect["mgef"] is None:
                effect_counts["unresolved_mgef"] += 1
                continue
            effect_names[effect["mgef"]["editor_id"]] += 1
            data = effect["mgef"]["data"]
            if "primary_actor_value_s32" in data:
                actor_value_counts[str(data["primary_actor_value_s32"])] += 1
            else:
                effect_counts["mgef_without_decoded_data"] += 1

    capture = {
        "tool": "EXP-0123 screen_clothing_enchantments.py",
        "read_only": True,
        "record_resolution": "last override in exact official-five-master order: Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm, Dragonborn.esm; not a profile winner",
        "schema_reference": "TES5Edit dev-4.1.6 Core/wbDefinitionsTES5.pas; BOD2 Armor Type offset 4; ARMO EITM, ENCH ENIT/EFID/EFIT/CTDA, MGEF DATA and CTDA",
        "source_files": source_manifest,
        "record_counts_by_plugin": {
            "ARMO": armo_counts,
            "ENCH": ench_counts,
            "MGEF": mgef_counts,
        },
        "winning_unique_armor_count": len(armos),
        "winning_clothing_count": len(clothing),
        "clothing_with_enchantment_link_count": sum(bool(row["enchantment_id"]) for row in clothing),
        "clothing_with_enchantment_effect_count": sum(bool(row["enchantment_effects"]) for row in clothing),
        "unresolved_enchantment_reference_count": sum(row["unresolved_enchantment_reference"] for row in clothing),
        "unclassified_armor_records": unclassified,
        "effect_summary": {
            "counts": dict(effect_counts),
            "primary_actor_value_counts": dict(actor_value_counts),
            "mgef_editor_id_counts": dict(effect_names),
        },
        "clothing_records": clothing,
    }
    rendered = json.dumps(capture, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        try:
            output.relative_to(ROOT / ".local")
        except ValueError as exc:
            raise RuntimeError("raw capture output must be below ignored .local/") from exc
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(json.dumps({
        "tool": capture["tool"],
        "read_only": True,
        "record_resolution": capture["record_resolution"],
        "source_files": source_manifest,
        "record_counts_by_plugin": capture["record_counts_by_plugin"],
        "winning_unique_armor_count": len(armos),
        "winning_clothing_count": len(clothing),
        "clothing_with_enchantment_link_count": capture["clothing_with_enchantment_link_count"],
        "clothing_with_enchantment_effect_count": capture["clothing_with_enchantment_effect_count"],
        "unresolved_enchantment_reference_count": capture["unresolved_enchantment_reference_count"],
        "unclassified_armor_records": unclassified,
        "effect_summary": capture["effect_summary"],
        "clothing_resistance_effect_chains": [
            {
                "armor_id": row["record_id"],
                "armor_editor_id": row["editor_id"],
                "armor_source_plugin": row["winning_source_plugin"],
                "armor_body_template": row["body_template_signature"],
                "enchantment_id": row["enchantment_id"],
                "enchantment_editor_id": row["enchantment_editor_id"],
                "mgef_id": effect["mgef_id"],
                "mgef_editor_id": effect["mgef"]["editor_id"] if effect["mgef"] else None,
                "efit_magnitude": effect["magnitude"],
                "effect_conditions_count": len(effect["conditions"]),
                "mgef_data": {
                    name: effect["mgef"]["data"].get(name)
                    for name in (
                        "data_length",
                        "flags_u32",
                        "magic_skill_s32",
                        "resist_value_s32",
                        "archetype_u32",
                        "primary_actor_value_s32",
                        "second_actor_value_s32",
                    )
                } if effect["mgef"] else None,
                "mgef_conditions_count": len(effect["mgef"]["conditions"]) if effect["mgef"] else None,
            }
            for row in clothing
            for effect in row["enchantment_effects"]
            if effect["mgef"] and any(token in effect["mgef"]["editor_id"].casefold() for token in ("resist", "damage", "ward", "shield"))
        ],
        "raw_capture": str(args.output) if args.output else None,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, PluginFormatError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
