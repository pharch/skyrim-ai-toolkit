#!/usr/bin/env python3
"""Decode the captured Savior's Hide ARMO -> ENCH -> MGEF fields."""
from __future__ import annotations

import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/transactions/TX-20261018-0011"


def json_record(path: Path) -> dict:
    wrapper = json.loads(path.read_text(encoding="utf-8"))
    records_jsonl = wrapper.get("records_jsonl")
    if records_jsonl is not None:
        rows = [json.loads(line) for line in records_jsonl.splitlines() if line.strip()]
        if len(rows) != 1:
            raise ValueError(f"expected one direct-parser record in {path.name}, got {len(rows)}")
        return rows[0]
    return wrapper


def fields(record: dict, signature: str) -> list[bytes]:
    return [bytes.fromhex(row["value_hex"] if "value_hex" in row else row["hex"])
            for row in record["subrecords"] if row["signature"] == signature]


def form_id(raw: bytes) -> str:
    if len(raw) != 4:
        raise ValueError(f"expected four-byte FormID, got {len(raw)}")
    return f"{struct.unpack('<I', raw)[0]:08X}"


def decode_mgef(path: Path) -> dict:
    record = json_record(path)
    data_rows = fields(record, "DATA")
    if len(data_rows) != 1 or len(data_rows[0]) < 92:
        raise ValueError(f"unexpected MGEF DATA structure in {path.name}")
    raw = data_rows[0]
    conditions = fields(record, "CTDA")
    return {
        "form_id": record["file_form_id"],
        "editor_id": record["editor_id"],
        "magic_skill_s32": struct.unpack_from("<i", raw, 12)[0],
        "resist_value_s32": struct.unpack_from("<i", raw, 16)[0],
        "archetype_u32": struct.unpack_from("<I", raw, 64)[0],
        "primary_actor_value_s32": struct.unpack_from("<i", raw, 68)[0],
        "second_actor_value_s32": struct.unpack_from("<i", raw, 88)[0],
        "condition_count": len(conditions),
        "data_hex": raw.hex(),
    }


def main() -> int:
    armo = json_record(CAPTURE / "skyrim-savior-armor-records.json")
    ench = json_record(CAPTURE / "skyrim-saviors-hide-enchantment-plugin-reader.json")
    armo_bod2 = fields(armo, "BOD2")
    armo_dnam = fields(armo, "DNAM")
    armo_eitm = fields(armo, "EITM")
    if len(armo_bod2) != 1 or len(armo_bod2[0]) < 8 or len(armo_dnam) != 1 or len(armo_dnam[0]) != 4:
        raise ValueError("unexpected ARMO BOD2 or DNAM shape")
    enit = fields(ench, "ENIT")
    efids = fields(ench, "EFID")
    efits = fields(ench, "EFIT")
    if len(enit) != 1 or len(enit[0]) < 24 or len(efids) != len(efits):
        raise ValueError("unexpected ENCH ENIT/EFID/EFIT shape")
    effects = []
    for index, (effect_id, effect_data) in enumerate(zip(efids, efits)):
        if len(effect_data) != 12:
            raise ValueError(f"unexpected EFIT length at effect {index}")
        magnitude, area, duration = struct.unpack("<fii", effect_data)
        mgef_path = CAPTURE / ("skyrim-saviors-hide-magic-effect.json" if index == 0
                               else "skyrim-saviors-hide-poison-effect.json")
        effects.append({
            "mgef_form_id": form_id(effect_id),
            "effect_magnitude_f32": magnitude,
            "area_s32": area,
            "duration_s32": duration,
            "mgef": decode_mgef(mgef_path),
        })
    print(json.dumps({
        "plugin": armo["plugin"],
        "source_form_ids": {
            "armo": armo["file_form_id"],
            "enchantment": ench["file_form_id"],
        },
        "armor": {
            "editor_id": armo["editor_id"],
            "bod2_first_person_flags_u32": struct.unpack_from("<I", armo_bod2[0], 0)[0],
            "bod2_armor_type_u32": struct.unpack_from("<I", armo_bod2[0], 4)[0],
            "dnam_raw_s32": struct.unpack_from("<i", armo_dnam[0], 0)[0],
            "eitm_form_id": form_id(armo_eitm[0]),
        },
        "enchantment": {
            "editor_id": ench["editor_id"],
            "enit_cost_s32": struct.unpack_from("<i", enit[0], 0)[0],
            "enit_flags_u32": struct.unpack_from("<I", enit[0], 4)[0],
            "enit_cast_type_u32": struct.unpack_from("<I", enit[0], 8)[0],
            "enit_amount_s32": struct.unpack_from("<i", enit[0], 12)[0],
            "enit_delivery_u32": struct.unpack_from("<I", enit[0], 16)[0],
            "enit_enchant_type_u32": struct.unpack_from("<I", enit[0], 20)[0],
            "effect_count": len(effects),
            "effects": effects,
        },
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
