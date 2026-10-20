#!/usr/bin/env python3
"""Print only Dawnguard VQ introduction and CastleGuard callback branches."""
from __future__ import annotations
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/alignment/transactions/TX-20261017-0010/dawnguard-vq-topic-join.json"
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261017-0010/dawnguard-vq-topic-summary.json"
PICKS = ("Intro", "Vigilants", "CastleGuard", "Tolan")

def script_names(record: dict) -> list[str]:
    names = set()
    for field in record.get("subrecords", []):
        if field.get("signature") == "VMAD":
            names.update(value.decode("ascii", "replace") for value in re.findall(rb"[A-Za-z0-9_]{4,}", bytes.fromhex(field["value_hex"])))
    return sorted(name for name in names if name.startswith(("DLC1_TIF_", "DLC1_QF_")))

def compact_condition(condition: dict) -> dict:
    return {key: condition.get(key) for key in ("function_index", "function_name", "comparison", "operand_float", "operand_global", "param1", "param2", "param3", "run_on")}

def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    selected = []
    for topic in source["topics"]:
        dial = topic["dial_winner"]
        if not any(token.casefold() in dial["editor_id"].casefold() for token in PICKS):
            continue
        children = []
        for item in topic["info_children"]:
            row = item["winner"]
            children.append({
                "form_id": row["file_form_id"],
                "editor_id": row["editor_id"],
                "source_plugin": row["plugin"],
                "parent_groups": row.get("parent_groups", []),
                "conditions": [compact_condition(c) for c in row.get("conditions", [])],
                "scripts": script_names(row),
                "callback_signatures": [f["signature"] for f in row.get("subrecords", []) if f["signature"] in {"VMAD", "QSTI", "SCRO", "SCHR", "SCDA", "SCTX"}],
                "string_ids": [{"signature": f["signature"], "value_hex": f["value_hex"]} for f in row.get("subrecords", []) if f["signature"] in {"NAM1", "NAM2", "NAM3"}],
            })
        selected.append({
            "quest_form_id": topic["quest_form_id"],
            "quest_editor_id": topic["quest_editor_id"],
            "dial_form_id": dial["file_form_id"],
            "dial_editor_id": dial["editor_id"],
            "source_plugin": dial["plugin"],
            "topic_type": next((f["text_cp1252"] for f in dial["subrecords"] if f["signature"] == "SNAM"), None),
            "tif_count": next((int.from_bytes(bytes.fromhex(f["value_hex"]), "little") for f in dial["subrecords"] if f["signature"] == "TIFC" and f["length"] == 4), None),
            "info_children": children,
        })
    result = {"source": SOURCE.relative_to(ROOT).as_posix(), "source_order_scope": source["source_order_scope"], "topic_count": len(selected), "topics": selected}
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "selected_topic_count": len(selected), "topics": [
        {"quest": t["quest_editor_id"], "dial": t["dial_form_id"], "editor_id": t["dial_editor_id"],
         "tif_count": t["tif_count"], "children": [
             {"form_id": c["form_id"], "scripts": c["scripts"], "conditions": c["conditions"],
              "callbacks": c["callback_signatures"], "strings": c["string_ids"]} for c in t["info_children"]]}
        for t in selected]}, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
