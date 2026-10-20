#!/usr/bin/env python3
"""Map Dawnguard VQ DIAL/INFO conditions to attached Papyrus script names."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TX = ROOT / ".local/alignment/transactions/TX-20261017-0010"
SOURCE = TX / "dawnguard-vq-topic-join.json"
OUTPUT = TX / "dawnguard-vq-topic-callbacks.json"
WANTED = {"0200352A", "0200D06C", "0200D90E", "0201A415"}
PATTERN = re.compile(rb"[A-Za-z0-9_]{4,}")


def scripts(record: dict) -> list[str]:
    result = set()
    for field in record.get("subrecords", []):
        if field.get("signature") == "VMAD":
            data = bytes.fromhex(field.get("value_hex", ""))
            result.update(
                value.decode("ascii", "replace")
                for value in PATTERN.findall(data)
            )
    return sorted(name for name in result if name.casefold().startswith(("dlc1_tif_", "dlc1_qf_", "qf_dlc01vq")))


def conditions(record: dict) -> list[dict]:
    return [{key: item.get(key) for key in (
        "function_index", "function_name", "comparison", "operand_float",
        "operand_global", "param1", "param2", "param3", "run_on",
    )} for item in record.get("conditions", [])]


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    topics = []
    for topic in source["topics"]:
        if topic["quest_form_id"] not in WANTED:
            continue
        dial = topic["dial_winner"]
        children = []
        for item in topic["info_children"]:
            info = item["winner"]
            children.append({
                "info_form_id": info["file_form_id"],
                "info_editor_id": info["editor_id"],
                "source_plugin": info["plugin"],
                "conditions": conditions(info),
                "scripts": scripts(info),
            })
        topics.append({
            "quest_form_id": topic["quest_form_id"],
            "quest_editor_id": topic["quest_editor_id"],
            "dial_form_id": dial["file_form_id"],
            "dial_editor_id": dial["editor_id"],
            "dial_conditions": conditions(dial),
            "info_children": children,
        })
    result = {
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_order_scope": source["source_order_scope"],
        "topic_count": len(topics),
        "info_child_count": sum(len(topic["info_children"]) for topic in topics),
        "topics": topics,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    focus = []
    for topic in topics:
        if topic["quest_form_id"] != "0200D06C":
            continue
        for info in topic["info_children"]:
            if info["scripts"] or any(c["function_name"] == "GetStage" and c["param1"] == "0200D06C" for c in info["conditions"]):
                focus.append({
                    "dial_form_id": topic["dial_form_id"],
                    "dial_editor_id": topic["dial_editor_id"],
                    **info,
                })
    scripted = [row for row in focus if row["scripts"]]
    alternate = []
    for topic in topics:
        if topic["quest_form_id"] not in {"0200D90E", "0201A415"}:
            continue
        for info in topic["info_children"]:
            if info["scripts"]:
                alternate.append({
                    "quest_form_id": topic["quest_form_id"],
                    "quest_editor_id": topic["quest_editor_id"],
                    "dial_form_id": topic["dial_form_id"],
                    "dial_editor_id": topic["dial_editor_id"],
                    "dial_conditions": topic["dial_conditions"],
                    **info,
                })
    print(json.dumps({
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "topic_count": result["topic_count"],
        "info_child_count": result["info_child_count"],
        "miscobjective_tif_count": len({name for row in focus for name in row["scripts"] if name.casefold().startswith("dlc1_tif_")}),
        "miscobjective_focus": scripted,
        "vq00_and_castleguard_scripted_topics": alternate,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
