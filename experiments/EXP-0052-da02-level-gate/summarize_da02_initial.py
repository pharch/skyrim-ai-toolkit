#!/usr/bin/env python3
"""Decode the captured DA02 Story Manager, global, and QUST records."""
from __future__ import annotations

import importlib.util
import json
import struct
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/transactions/TX-20261016-0045"
DECODER = ROOT / "experiments/EXP-0043-da04-helper-versus-main-start/decode_qust_vmad.py"
OPERATORS = {0x00: "=", 0x20: "!=", 0x40: ">", 0x60: ">=", 0x80: "<", 0xA0: "<="}
EVENT_MEMBERS = {
    0x3152: "Actor 1", 0x3252: "Actor 2", 0x314F: "Created Object",
    0x3146: "Form", 0x314B: "Keyword", 0x314C: "Location 1", 0x324C: "Location 2",
    0x3151: "Quest", 0x3156: "Value 1", 0x3256: "Value 2",
}
EVENT_FUNCTIONS = {0: "GetIsID", 1: "IsInList", 2: "GetValue", 3: "HasKeyword", 4: "GetItemValue"}
CTDA_FUNCTIONS = {
    46: "GetDead", 56: "GetQuestRunning", 58: "GetStage", 59: "GetStageDone",
    74: "GetGlobalValue", 80: "GetLevel", 136: "GetIsReference", 561: "HasRefType",
    576: "GetEventData", 650: "IsLinkedTo",
}
EVENT_MEMBER_CODES = {value: key for key, value in EVENT_MEMBERS.items()}
EVENT_MEMBER_TAGS = {
    0x3152: "R1", 0x3252: "R2", 0x314F: "O1", 0x3146: "F1",
    0x314B: "K1", 0x314C: "L1", 0x324C: "L2", 0x3151: "Q1",
    0x3156: "V1", 0x3256: "V2",
}


def load_record(filename: str, editor_id: str) -> tuple[dict, dict, list[dict]]:
    wrapper = json.loads((CAPTURE / filename).read_text(encoding="utf-8"))
    records = [json.loads(line) for line in wrapper.get("records_jsonl", "").splitlines() if line.strip()]
    matches = [row for row in records if row.get("editor_id") == editor_id]
    if len(matches) != 1:
        raise ValueError(f"expected one {editor_id} in {filename}; found {len(matches)}")
    return wrapper, matches[0], records


def fields(record: dict) -> dict[str, list[bytes]]:
    result: dict[str, list[bytes]] = {}
    for row in record.get("subrecords", []):
        result.setdefault(row["signature"], []).append(bytes.fromhex(row["hex"]))
    return result


def alias_schema(record: dict) -> list[dict]:
    aliases: list[dict] = []
    current: dict | None = None
    for subrecord in record.get("subrecords", []):
        sig = subrecord["signature"]
        raw = bytes.fromhex(subrecord["hex"])
        if sig in {"ALST", "ALLS"}:
            if current is not None:
                aliases.append(current)
            current = {
                "alias_id": int.from_bytes(raw, "little"),
                "alias_kind": "reference" if sig == "ALST" else "location",
                "fields": [],
            }
        if current is not None:
            current["fields"].append({"signature": sig, "hex": raw.hex()})
    if current is not None:
        aliases.append(current)
    for alias in aliases:
        for field in alias["fields"]:
            if field["signature"] == "ALID":
                alias["alias_name"] = bytes.fromhex(field["hex"]).rstrip(b"\0").decode("cp1252", "replace")
                break
        fields = alias.pop("fields")
        alias["field_signatures"] = [field["signature"] for field in fields]
        alias["selected_field_values"] = [
            field for field in fields
            if field["signature"] in {
                "FNAM", "ALCO", "ALCA", "ALCL", "ALFR", "ALUA", "ALFE",
                "ALFD", "ALNA", "ALNT", "ALFL", "KNAM", "CNTO", "CTDA", "ALED", "VTCK",
            }
        ]
        alias["conditions"] = [
            decode_ctda(bytes.fromhex(field["hex"]))
            for field in fields if field["signature"] == "CTDA"
        ]
        sigs = set(alias["field_signatures"])
        if "ALCO" in sigs and "ALCA" in sigs:
            alias["fill_type"] = "Create Reference to Object"
        elif "ALNA" in sigs and "ALNT" in sigs:
            alias["fill_type"] = "Find Matching Reference near Alias"
        elif "ALFE" in sigs and "ALFD" in sigs:
            alias["fill_type"] = "Find Matching Location from Event" if alias["alias_kind"] == "location" else "Find Matching Reference from Event"
        elif "ALFL" in sigs:
            alias["fill_type"] = "Specific Location"
        elif "ALFR" in sigs:
            alias["fill_type"] = "Specific Reference"
        elif "ALUA" in sigs:
            alias["fill_type"] = "Unique Actor"
        else:
            alias["fill_type"] = "unclassified from selected fill fields"
        alias["decoded_event_fields"] = [
            {
                "event_type_code": field["hex"],
                "event_type_tag": bytes.fromhex(field["hex"]).rstrip(b"\0").decode("ascii", "replace"),
            }
            for field in fields if field["signature"] == "ALFE"
        ] + [
            {
                "event_member_code": f"{int.from_bytes(bytes.fromhex(field['hex']), 'little'):04X}",
                "event_member_tag": EVENT_MEMBER_TAGS.get(int.from_bytes(bytes.fromhex(field["hex"]), "little"), "unknown"),
            }
            for field in fields if field["signature"] == "ALFD"
        ]
    return aliases


def decode_ctda(raw: bytes) -> dict:
    if len(raw) != 32:
        return {"length": len(raw), "raw": raw.hex()}
    type_byte = raw[0]
    global_id = struct.unpack_from("<I", raw, 4)[0]
    function_index = struct.unpack_from("<H", raw, 8)[0]
    param1 = struct.unpack_from("<I", raw, 12)[0]
    param2 = struct.unpack_from("<I", raw, 16)[0]
    param3 = struct.unpack_from("<i", raw, 28)[0]
    decoded = {
        "raw": raw.hex(),
        "comparison": OPERATORS.get(type_byte & 0xF0, "unknown"),
        "use_global": bool(type_byte & 0x04),
        "function_index": function_index,
        "function_name": CTDA_FUNCTIONS.get(function_index, f"unknown:{function_index}"),
        "param1": f"{param1:08X}",
        "param2": f"{param2:08X}",
        "param3": param3,
        "operand_global": f"{global_id:08X}" if type_byte & 0x04 else None,
        "operand_float": struct.unpack_from("<f", raw, 4)[0] if not type_byte & 0x04 else None,
        "run_on": struct.unpack_from("<I", raw, 20)[0],
        "reference": f"{struct.unpack_from('<I', raw, 24)[0]:08X}",
    }
    if function_index == 576:
        event_function = param1 & 0xFFFF
        event_member = (param1 >> 16) & 0xFFFF
        decoded["event_function_index"] = event_function
        decoded["event_function"] = EVENT_FUNCTIONS.get(event_function, f"unknown:{event_function}")
        decoded["event_member_code"] = f"{event_member:04X}"
        decoded["event_member"] = EVENT_MEMBERS.get(event_member, "unknown")
    elif function_index == 136:
        decoded["reference_form_id"] = f"{param1:08X}"
        if decoded["run_on"] == 7:
            decoded["event_data_member"] = EVENT_MEMBERS.get(param3, f"unknown:0x{param3 & 0xFFFF:04X}")
    return decoded


def decode_quest_vmad(vmad_hex: str) -> dict:
    spec = importlib.util.spec_from_file_location("qust_vmad_decoder", DECODER)
    if spec is None or spec.loader is None:
        raise RuntimeError("schema-ordered QUST VMAD decoder unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decode_vmad(vmad_hex)


def summarize(filename: str, editor_id: str) -> dict:
    wrapper, record, _ = load_record(filename, editor_id)
    values = fields(record)
    selected = {key: [value.hex() for value in values.get(key, [])]
                for key in ("PNAM", "NNAM", "DNAM", "ENAM", "CTDA", "FLTV", "VMAD") if key in values}
    condition_trace = []
    condition_section = "before NEXT marker"
    active_alias = None
    for index, subrecord in enumerate(record.get("subrecords", [])):
        sig = subrecord["signature"]
        raw = bytes.fromhex(subrecord["hex"])
        if sig == "NEXT":
            condition_section = "after NEXT marker"
            active_alias = None
        elif sig in {"ALST", "ALLS"}:
            active_alias = int.from_bytes(raw, "little")
            condition_section = f"alias {active_alias}"
        elif sig == "ALID" and active_alias is not None:
            active_alias = {
                "alias_id": active_alias,
                "alias_name": raw.rstrip(b"\0").decode("cp1252", "replace"),
            }
        elif sig == "CTDA":
            condition_trace.append({
                "subrecord_index": index,
                "section": condition_section,
                "condition": decode_ctda(raw),
            })
    vmad = None
    if values.get("VMAD"):
        decoded = decode_quest_vmad(values["VMAD"][0].hex())
        vmad = {
            "version": decoded["version"],
            "object_format": decoded["object_format"],
            "file_name": decoded["file_name"],
            "fragments": decoded["fragments"],
            "alias_count": len(decoded["aliases"]),
            "aliases": [
                {
                    "alias_id": alias["alias_id"],
                    "target_form_id": f"{alias['form_id']:08X}",
                    "scripts": [
                        {
                            "name": script["name"],
                            "properties": [
                                {"name": prop["name"], "value": prop["value"]}
                                for prop in script["properties"]
                            ],
                        }
                        for script in alias["scripts"]
                    ],
                }
                for alias in decoded["aliases"]
            ],
            "scripts": [
                {
                    "name": script["name"],
                    "properties": [
                        {"name": prop["name"], "value": prop["value"]}
                        for prop in script["properties"]
                    ],
                }
                for script in decoded["scripts"]
            ],
        }
        selected["VMAD"] = [f"<{len(values['VMAD'][0])} bytes>"]
    return {
        "capture": filename,
        "route": wrapper.get("query_route"),
        "source_hashes": wrapper.get("source_sha256"),
        "signature": record.get("signature"),
        "plugin": record.get("plugin"),
        "origin_plugin": record.get("origin_plugin"),
        "form_id": record.get("file_form_id"),
        "editor_id": record.get("editor_id"),
        "record_flags": record.get("flags"),
        "selected_subrecords": selected,
        "decoded_ctda": [decode_ctda(raw) for raw in values.get("CTDA", [])],
        "condition_trace": condition_trace,
        "ctda_function_counts": dict(Counter(str(decode_ctda(raw).get("function_index")) for raw in values.get("CTDA", []))),
        "aliases": alias_schema(record) if record.get("signature") == "QUST" else [],
        "decoded_vmad": vmad,
    }


def main() -> int:
    rows = [
        summarize("da02-smqn-node.stdout.raw", "DA02IncreaseLevelNodeSHARES"),
        summarize("da02-update-qust.stdout.raw", "DA02"),
        summarize("da02-hook-qust.stdout.raw", "WEDA02"),
    ]
    _, global_record, _ = load_record("da02-global.stdout.raw", "DA02MinLevel")
    global_values = fields(global_record)
    rows.append({
        "capture": "da02-global.stdout.raw",
        "signature": global_record.get("signature"),
        "plugin": global_record.get("plugin"),
        "origin_plugin": global_record.get("origin_plugin"),
        "form_id": global_record.get("file_form_id"),
        "editor_id": global_record.get("editor_id"),
        "record_flags": global_record.get("flags"),
        "FLTV_hex": [value.hex() for value in global_values.get("FLTV", [])],
        "FLTV_float": [struct.unpack("<f", value)[0] for value in global_values.get("FLTV", []) if len(value) == 4],
    })
    print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
