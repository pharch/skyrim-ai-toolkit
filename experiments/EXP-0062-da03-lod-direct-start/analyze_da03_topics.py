#!/usr/bin/env python3
"""Index DA03Start topic conditions, localized IDs and INFO VMAD script names."""
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/alignment/transactions/TX-20261017-0008/EV-0322-da03-topic-summary.json"
VMAD_SOURCE = ROOT / ".local/alignment/transactions/TX-20261017-0008/EV-0322-da03-vmad.json"
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261017-0008/EV-0322-da03-topic-analysis.json"


def vmad_script_names(fields: list[dict]) -> list[str]:
    names: set[str] = set()
    for field in fields:
        if field.get("signature") != "VMAD":
            continue
        raw = bytes.fromhex(field["value_hex"])
        names.update(value.decode("ascii", "replace") for value in re.findall(rb"[A-Za-z0-9_]{4,}", raw))
    return sorted(name for name in names if name.startswith(("TIF_", "QF_")))


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    vmad = json.loads(VMAD_SOURCE.read_text(encoding="utf-8"))
    lod_alias = next((row for row in vmad["quest_aliases"] if row["alias_name"] == "Lod"), None)
    lod_alias_id = lod_alias["alias_id"] if lod_alias else None
    lod_actor_id = next((field.get("value_hex_u32") for field in (lod_alias or {}).get("fields", []) if field["signature"] == "ALUA"), None)
    topics = []
    for topic in source["topics"]:
        for info in topic["info_children"]:
            conditions = []
            for condition in info["conditions"]:
                conditions.append({
                    "function_index": condition["function_index"],
                    "function_name": condition.get("function_name"),
                    "comparison": condition.get("comparison"),
                    "operand_float": condition.get("operand_float"),
                    "operand_global": condition.get("operand_global"),
                    "param1": condition.get("param1"),
                    "run_on": condition.get("run_on"),
                    "raw": condition.get("raw"),
                    "param1_matches_lod_actor": bool(lod_actor_id and condition.get("param1") == lod_actor_id),
                })
            topics.append({
                "dial_form_id": topic["form_id"],
                "dial_editor_id": topic["editor_id"],
                "info_form_id": info["form_id"],
                "info_editor_id": info["editor_id"],
                "info_source_plugin": info["source_plugin"],
                "source_copies": info["source_copies"],
                "localized_response_ids": info["localized_response_ids"],
                "conditions": conditions,
                "vmad_script_names": vmad_script_names(info["callback_fields"]),
                "callback_signatures": [row["signature"] for row in info["callback_fields"]],
                "subrecord_signatures": info["subrecord_signatures"],
            })
    result = {
        "source_capture": ".local/alignment/transactions/TX-20261017-0008/EV-0322-da03-topic-summary.json",
        "quest_alias": {"alias_id": lod_alias_id, "alias_name": "Lod" if lod_alias else None, "actor_form_id": lod_actor_id},
        "topic_info_count": len(topics),
        "topics": topics,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "quest_alias": result["quest_alias"],
        "topic_info_count": len(topics),
        "topics": [{
            "dial_form_id": row["dial_form_id"],
            "dial_editor_id": row["dial_editor_id"],
            "info_form_id": row["info_form_id"],
            "string_ids": row["localized_response_ids"],
            "conditions": [{
                "function_index": c["function_index"],
                "function_name": c["function_name"],
                "comparison": c["comparison"],
                "operand_float": c["operand_float"],
                "param1": c["param1"],
                "param1_matches_lod_actor": c["param1_matches_lod_actor"],
            } for c in row["conditions"]],
            "vmad_script_names": row["vmad_script_names"],
        } for row in topics],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
