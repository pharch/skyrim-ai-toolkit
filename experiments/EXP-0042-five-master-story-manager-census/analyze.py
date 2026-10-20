#!/usr/bin/env python3
"""Summarize raw-parser Story Manager captures without resolving xEdit winners."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

PLUGINS = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]
SIGNATURES = ["SMEN", "SMQN"]
FILES = {
    ("SMQN", "Skyrim.esm"): "smqn-skyrim.json",
    ("SMEN", "Skyrim.esm"): "smen-skyrim.json",
    ("SMQN", "Update.esm"): "smqn-update.json",
    ("SMEN", "Update.esm"): "smen-update.json",
    ("SMQN", "Dawnguard.esm"): "smqn-dawnguard.json",
    ("SMEN", "Dawnguard.esm"): "smen-dawnguard-retry.json",
    ("SMQN", "HearthFires.esm"): "smqn-hearthfires.json",
    ("SMEN", "HearthFires.esm"): "smen-hearthfires.json",
    ("SMQN", "Dragonborn.esm"): "smqn-dragonborn.json",
    ("SMEN", "Dragonborn.esm"): "smen-dragonborn.json",
}
OPERATORS = {0x00: "=", 0x20: "!=", 0x40: ">", 0x60: ">=", 0x80: "<", 0xA0: "<="}


def decode_condition(raw_hex: str) -> dict[str, Any]:
    raw = bytes.fromhex(raw_hex)
    if len(raw) != 32:
        return {"length": len(raw), "raw": raw_hex}
    condition_type = raw[0]
    operand = raw[4:8]
    result: dict[str, Any] = {
        "type_byte": f"0x{condition_type:02X}",
        "operator": OPERATORS.get(condition_type & 0xF0, "unknown"),
        "or_flag": bool(condition_type & 0x01),
        "run_on_target_flag": bool(condition_type & 0x02),
        "use_global": bool(condition_type & 0x04),
        "function_index": struct.unpack_from("<H", raw, 8)[0],
        "param1_raw": raw[12:16].hex(),
        "param2_raw": raw[16:20].hex(),
        "run_on": struct.unpack_from("<I", raw, 20)[0],
        "reference_form_id": f"{struct.unpack_from('<I', raw, 24)[0]:08X}",
        "raw": raw_hex,
    }
    if result["use_global"]:
        result["operand_global_form_id"] = f"{struct.unpack_from('<I', operand)[0]:08X}"
    else:
        result["operand_constant"] = struct.unpack("<f", operand)[0]
    return result


def load_capture(path: Path, signature: str, plugin: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("exit_code") != 0:
        raise ValueError(f"capture did not succeed: {path}")
    records = [json.loads(line) for line in data.get("records_jsonl", "").splitlines() if line.strip()]
    for record in records:
        if record.get("signature") != signature or record.get("plugin") != plugin:
            raise ValueError(f"unexpected record identity in {path}: {record.get('signature')} {record.get('plugin')}")
    return records, {
        "capture_file": path.name,
        "signature": signature,
        "plugin": plugin,
        "record_count": data.get("record_count", len(records)),
        "parser_stdout_sha256": data.get("stdout_sha256"),
        "route": data.get("query_route"),
        "capture_file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def subrecords(record: dict[str, Any], signature: str) -> list[bytes]:
    return [bytes.fromhex(row["hex"]) for row in record.get("subrecords", []) if row.get("signature") == signature]


def analyze(capture_dir: Path) -> dict[str, Any]:
    all_records: dict[tuple[str, str], list[dict[str, Any]]] = {}
    capture_meta = []
    counts = {}
    for plugin in PLUGINS:
        for signature in SIGNATURES:
            capture_path = capture_dir / FILES[(signature, plugin)]
            records, metadata = load_capture(capture_path, signature, plugin)
            all_records[(plugin, signature)] = records
            counts[f"{plugin}:{signature}"] = len(records)
            capture_meta.append(metadata)

    observations = []
    winners: dict[tuple[str, str, str], dict[str, Any]] = {}
    for plugin in PLUGINS:
        for signature in SIGNATURES:
            for record in all_records[(plugin, signature)]:
                winners[(signature, record["origin_plugin"], record["local_form_id"].upper())] = record
                conditions = [decode_condition(raw.hex()) for raw in subrecords(record, "CTDA")]
                for condition_index, condition in enumerate(conditions):
                    if condition.get("function_index") == 80:
                        observations.append({
                            "signature": signature,
                            "file_form_id": record["file_form_id"].upper(),
                            "source_plugin": plugin,
                            "origin_plugin": record.get("origin_plugin"),
                            "editor_id": record.get("editor_id", ""),
                            "condition_index": condition_index,
                            "condition": condition,
                            "parent_form_id": f"{int.from_bytes(subrecords(record, 'PNAM')[0], 'little'):08X}" if subrecords(record, "PNAM") and len(subrecords(record, "PNAM")[0]) == 4 else None,
                            "children": [f"{int.from_bytes(raw, 'little'):08X}" for raw in subrecords(record, "NNAM") if len(raw) == 4],
                        })

    winner_observations = []
    for (signature, origin_plugin, local_form_id), record in sorted(winners.items()):
        conditions = [decode_condition(raw.hex()) for raw in subrecords(record, "CTDA")]
        for condition_index, condition in enumerate(conditions):
            if condition.get("function_index") == 80:
                winner_observations.append({
                    "signature": signature,
                    "origin_plugin": origin_plugin,
                    "local_form_id": local_form_id,
                    "file_form_id": record["file_form_id"].upper(),
                    "source_plugin": record["plugin"],
                    "origin_plugin": record.get("origin_plugin"),
                    "editor_id": record.get("editor_id", ""),
                    "condition_index": condition_index,
                    "condition": condition,
                    "parent_form_id": f"{int.from_bytes(subrecords(record, 'PNAM')[0], 'little'):08X}" if subrecords(record, "PNAM") and len(subrecords(record, "PNAM")[0]) == 4 else None,
                    "children": [f"{int.from_bytes(raw, 'little'):08X}" for raw in subrecords(record, "NNAM") if len(raw) == 4],
                })

    return {
        "route": "direct read-only TES4 record parser; same-FormID selection is a local official-order comparison, not native xEdit",
        "official_order": PLUGINS,
        "record_counts": counts,
        "total_smen": sum(counts[f"{plugin}:SMEN"] for plugin in PLUGINS),
        "total_smqn": sum(counts[f"{plugin}:SMQN"] for plugin in PLUGINS),
        "capture_metadata": capture_meta,
        "getlevel_observations_across_source_files": observations,
        "getlevel_observations_after_local_override_comparison": winner_observations,
        "interpretation_limits": [
            "Direct parser output is not a native xEdit field export or profile-specific winner.",
            "Global operands, child target record types/EditorIDs, and actual gate behavior need separate record/runtime evidence.",
            "The local same-FormID comparison selects the last serialized record in the official master order; it does not resolve field-level merge semantics.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.capture_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "record_counts": result["record_counts"],
        "total_smen": result["total_smen"],
        "total_smqn": result["total_smqn"],
        "getlevel_source_observations": len(result["getlevel_observations_across_source_files"]),
        "getlevel_merged_candidates": len(result["getlevel_observations_after_local_override_comparison"]),
        "output": args.output.as_posix(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
