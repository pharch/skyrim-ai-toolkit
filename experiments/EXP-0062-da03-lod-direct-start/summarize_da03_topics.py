#!/usr/bin/env python3
"""Produce a compact condition/string/fragment index from the DA03 topic join."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/alignment/transactions/TX-20261017-0008/EV-0322-da03-topics.json"
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261017-0008/EV-0322-da03-topic-summary.json"


def field_values(record: dict, signature: str) -> list[dict]:
    return [row for row in record.get("subrecords", []) if row["signature"] == signature]


def string_ids(record: dict) -> list[dict]:
    values = []
    for row in record.get("subrecords", []):
        if row["signature"] not in {"NAM1", "NAM2", "NAM3"}:
            continue
        raw = bytes.fromhex(row["value_hex"])
        values.append({
            "signature": row["signature"],
            "length": len(raw),
            "raw_hex": raw.hex(),
            "localized_string_id": int.from_bytes(raw, "little") if len(raw) == 4 else None,
        })
    return values


def summarize_info(wrapper: dict, topic: dict) -> dict:
    record = wrapper["winner"]
    return {
        "form_id": record["file_form_id"],
        "origin_plugin": record["origin_plugin"],
        "source_plugin": record["plugin"],
        "editor_id": record["editor_id"],
        "parent_groups": record.get("parent_groups", []),
        "source_copies": wrapper["source_copies"],
        "subrecord_signatures": [row["signature"] for row in record["subrecords"]],
        "conditions": record["conditions"],
        "localized_response_ids": string_ids(record),
        "callback_fields": [row for row in record["subrecords"] if row["signature"] in {"VMAD", "QSTI", "TPIC", "SCRO", "SCHR", "SCDA", "SCTX"}],
        "text_fields": [row for row in record["subrecords"] if row["signature"] in {"NAM1", "RNAM", "FULL", "CNAM"}],
    }


def main() -> int:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    topics = []
    for entry in source["topics"]:
        dial = entry["winner"]
        topics.append({
            "form_id": dial["file_form_id"],
            "editor_id": dial["editor_id"],
            "source_plugin": dial["plugin"],
            "source_copies": entry["source_copies"],
            "topic_type": next((row.get("text_cp1252") for row in dial["subrecords"] if row["signature"] == "SNAM"), None),
            "quest_form_id": next((row["value_hex"] for row in dial["subrecords"] if row["signature"] == "QNAM"), None),
            "tif_count": next((int.from_bytes(bytes.fromhex(row["value_hex"]), "little") for row in dial["subrecords"] if row["signature"] == "TIFC" and row["length"] == 4), None),
            "info_children": [summarize_info(child, entry) for child in entry["info_children"]],
        })
    result = {
        "source_capture": ".local/alignment/transactions/TX-20261017-0008/EV-0322-da03-topics.json",
        "source_sha256": source["source_hashes_rechecked"],
        "source_order_scope": source["source_order_scope"],
        "topic_count": len(topics),
        "topics": topics,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "topic_count": len(topics),
        "topics": [{
            "form_id": topic["form_id"],
            "editor_id": topic["editor_id"],
            "info": [{
                "form_id": info["form_id"],
                "string_ids": info["localized_response_ids"],
                "conditions": info["conditions"],
                "callbacks": [row["signature"] for row in info["callback_fields"]],
            } for info in topic["info_children"]],
        } for topic in topics],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
