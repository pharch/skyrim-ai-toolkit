#!/usr/bin/env python3
"""Resolve DA02 and WEDA02 parent/child Story Manager links from captures."""
from __future__ import annotations

import json
import struct
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/transactions/TX-20261016-0045"
TARGET_IDS = {
    0x0004D8D6, 0x0004A602, 0x0009E1AF, 0x000B48FC, 0x000B18E3,
    0x000896A9, 0x000896A8, 0x00101732, 0x00090028, 0x0005BD79, 0x0003833D,
}
QUEST_IDS = {0x0004D8D6, 0x0004A602}
OPERATORS = {0x00: "=", 0x20: "!=", 0x40: ">", 0x60: ">=", 0x80: "<", 0xA0: "<="}
EVENT_FUNCTIONS = {0: "GetIsID", 1: "IsInList", 2: "GetValue", 3: "HasKeyword", 4: "GetItemValue"}
EVENT_MEMBERS = {
    0x0000: "None", 0x3152: "Actor 1", 0x3252: "Actor 2", 0x314F: "Created Object",
    0x3146: "Form", 0x314B: "Keyword", 0x314C: "Location 1", 0x324C: "Location 2",
    0x3151: "Quest", 0x3156: "Value 1", 0x3256: "Value 2",
}


def get_rows(filename: str) -> tuple[dict, list[dict]]:
    wrapper = json.loads((CAPTURE / filename).read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in wrapper.get("records_jsonl", "").splitlines() if line.strip()]
    return wrapper, rows


def values(record: dict) -> dict[str, list[bytes]]:
    result: dict[str, list[bytes]] = defaultdict(list)
    for item in record.get("subrecords", []):
        result[item["signature"]].append(bytes.fromhex(item["hex"]))
    return result


def form_refs(values_by_sig: dict[str, list[bytes]], signature: str) -> list[int]:
    return [int.from_bytes(raw[:4], "little") for raw in values_by_sig.get(signature, []) if len(raw) >= 4]


def decode_ctda(raw: bytes) -> dict:
    if len(raw) != 32:
        return {"raw": raw.hex(), "length": len(raw)}
    condition_type = raw[0]
    use_global = bool(condition_type & 0x04)
    operand = struct.unpack_from("<I", raw, 4)[0] if use_global else struct.unpack_from("<f", raw, 4)[0]
    function_index = struct.unpack_from("<H", raw, 8)[0]
    param1 = struct.unpack_from("<I", raw, 12)[0]
    param2 = struct.unpack_from("<I", raw, 16)[0]
    decoded = {
        "operator": OPERATORS.get(condition_type & 0xF0, "unknown"),
        "comparison": operand,
        "function_index": function_index,
        "param1": f"{param1:08X}",
        "param2": f"{param2:08X}",
        "run_on": struct.unpack_from("<I", raw, 20)[0],
        "reference": f"{struct.unpack_from('<I', raw, 24)[0]:08X}",
        "raw": raw.hex(),
    }
    if function_index == 576:
        event_function = param1 & 0xFFFF
        event_member = (param1 >> 16) & 0xFFFF
        decoded["event_function"] = EVENT_FUNCTIONS.get(event_function, f"unknown:{event_function}")
        decoded["event_member"] = EVENT_MEMBERS.get(event_member, f"unknown:0x{event_member:04X}")
        decoded["event_data_form_id"] = f"{param2:08X}"
    elif function_index == 136:
        decoded["reference_form_id"] = f"{param1:08X}"
    return decoded


def compact(record: dict) -> dict:
    fields = values(record)
    parent = form_refs(fields, "PNAM")
    children = form_refs(fields, "NNAM")
    return {
        "signature": record.get("signature"),
        "form_id": record.get("file_form_id"),
        "editor_id": record.get("editor_id"),
        "source_plugin": record.get("plugin"),
        "origin_plugin": record.get("origin_plugin"),
        "parent_ids": [f"{value:08X}" for value in parent],
        "previous_node_ids": [f"{value:08X}" for value in form_refs(fields, "SNAM")],
        "event_type_values": [int.from_bytes(raw, "little") for raw in fields.get("ENAM", [])],
        "children": [f"{value:08X}" for value in children],
        "conditions": [decode_ctda(raw) for raw in fields.get("CTDA", [])],
        "other_fields": {
            key: [raw.hex() for raw in fields.get(key, [])]
            for key in ("DNAM", "QNAM", "CITC", "XNAM", "RNAM", "FNAM") if key in fields
        },
    }


def main() -> int:
    captures = []
    records_by_id: dict[int, list[dict]] = defaultdict(list)
    target_children: list[dict] = []
    for filename in ("da02-all-SMEN-Skyrim.stdout.raw", "da02-all-SMQN-Skyrim.stdout.raw"):
        wrapper, rows = get_rows(filename)
        captures.append({
            "capture": filename,
            "query_route": wrapper.get("query_route"),
            "record_count": wrapper.get("record_count"),
            "stdout_sha256": wrapper.get("stdout_sha256"),
        })
        for record in rows:
            records_by_id[int(record["file_form_id"], 16)].append(record)
    for filename in (
        "da02-specific-node-all-masters.stdout.raw",
        "da02-quest-node-all-all-masters.stdout.raw",
        "da02-priority-node-all-all-masters.stdout.raw",
    ):
        wrapper, rows = get_rows(filename)
        captures.append({
            "capture": filename,
            "query_route": wrapper.get("query_route"),
            "record_count": wrapper.get("record_count"),
            "stdout_sha256": wrapper.get("stdout_sha256"),
        })
        for record in rows:
            records_by_id[int(record["file_form_id"], 16)].append(record)
    selected = []
    for form_id, records in records_by_id.items():
        for record in records:
            fields = values(record)
            parents = form_refs(fields, "PNAM")
            children = form_refs(fields, "NNAM")
            has_quest_child = bool(QUEST_IDS.intersection(children))
            named_candidate = "DA02" in record.get("editor_id", "") or "WEPriorityQuests" in record.get("editor_id", "")
            if form_id in TARGET_IDS or has_quest_child or named_candidate or any(parent in TARGET_IDS for parent in parents):
                selected.append(compact(record))
    report = {
        "source_plugin": "Skyrim.esm",
        "scope": "all directly parsed Skyrim.esm SMEN and SMQN records; source hashes are in each wrapper and manifest",
        "captures": captures,
        "selected_nodes": sorted(selected, key=lambda row: (row["signature"], row["form_id"])),
        "interpretation_limit": "SNAM is decoded as the schema-defined previous-node link and ENAM as the SMEN event type. GetEventData parameters use the pinned TES5Edit schema's low-16-bit function/high-16-bit event-member encoding. Record dispatch, runtime selection, and active profile winners are not tested.",
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
