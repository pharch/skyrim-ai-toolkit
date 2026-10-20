#!/usr/bin/env python3
"""Summarize bounded direct-parser Dragonborn Story Manager captures for Q81."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[2]
CAPTURES = {
    "SMEN": ROOT / ".local/alignment/xedit-bridge/20261019T233633.938231Z/stdout.raw",
    "SMBN": ROOT / ".local/alignment/xedit-bridge/20261019T233633.938793Z/stdout.raw",
    "SMQN": ROOT / ".local/alignment/xedit-bridge/20261019T233633.940124Z/stdout.raw",
}
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-storymanager-summary.json"
TARGET_QUESTS = {"0203546D": "DLC2CultistAmbush", "020331C0": "DLC2WE09"}
OPERATORS = {0x00: "=", 0x20: "!=", 0x40: ">", 0x60: ">=", 0x80: "<", 0xA0: "<="}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def records(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def subrecords(record: dict, signature: str) -> list[bytes]:
    return [bytes.fromhex(row["hex"]) for row in record.get("subrecords", []) if row.get("signature") == signature]


def decode_condition(raw: bytes) -> dict:
    if len(raw) != 32:
        return {"length": len(raw), "raw": raw.hex()}
    condition_type = raw[0]
    operand = raw[4:8]
    return {
        "type_byte": f"0x{condition_type:02X}",
        "operator": OPERATORS.get(condition_type & 0xF0, "unknown"),
        "use_global": bool(condition_type & 0x04),
        "function_index": struct.unpack_from("<H", raw, 8)[0],
        "function_name_if_verified": "GetLevel" if struct.unpack_from("<H", raw, 8)[0] == 80 else None,
        "operand_constant": struct.unpack("<f", operand)[0] if not (condition_type & 0x04) else None,
        "operand_global_form_id": f"{struct.unpack('<I', operand)[0]:08X}" if condition_type & 0x04 else None,
        "parameter_1_raw": raw[12:16].hex(),
        "parameter_2_raw": raw[16:20].hex(),
        "run_on": struct.unpack_from("<I", raw, 20)[0],
        "reference_form_id": f"{struct.unpack_from('<I', raw, 24)[0]:08X}",
        "raw": raw.hex(),
    }


def view(record: dict) -> dict:
    return {
        "signature": record.get("signature"),
        "file_form_id": record.get("file_form_id"),
        "origin_plugin": record.get("origin_plugin"),
        "editor_id": record.get("editor_id"),
        "parent_form_ids": [f"{int.from_bytes(row, 'little'):08X}" for row in subrecords(record, "PNAM") if len(row) == 4],
        "child_form_ids_nnam": [f"{int.from_bytes(row, 'little'):08X}" for row in subrecords(record, "NNAM") if len(row) == 4],
        "snAM_raw": [row.hex() for row in subrecords(record, "SNAM")],
        "qNAM_raw": [row.hex() for row in subrecords(record, "QNAM")],
        "conditions": [decode_condition(raw) for raw in subrecords(record, "CTDA")],
    }


def main() -> None:
    all_rows = {signature: records(path) for signature, path in CAPTURES.items()}
    for signature, rows in all_rows.items():
        if any(row.get("signature") != signature or row.get("plugin") != "Dragonborn.esm" for row in rows):
            raise SystemExit(f"unexpected record scope in {signature} capture")

    targets = set(TARGET_QUESTS)
    linked = []
    for signature, rows in all_rows.items():
        for row in rows:
            children = [f"{int.from_bytes(raw, 'little'):08X}" for raw in subrecords(row, "NNAM") if len(raw) == 4]
            matches = [child for child in children if child in targets]
            if matches:
                item = view(row)
                item["matched_quest_children"] = matches
                linked.append(item)

    named = []
    for signature, rows in all_rows.items():
        for row in rows:
            if row.get("editor_id") in {"DLC2CultistAmbushNode", "DLC2WENode"}:
                named.append(view(row))

    if len(all_rows["SMQN"]) != 43 or len(all_rows["SMEN"]) != 2 or len(all_rows["SMBN"]) != 15:
        raise SystemExit("unexpected Dragonborn Story Manager census counts")
    if not any(row.get("editor_id") == "DLC2CultistAmbushNode" for row in named):
        raise SystemExit("DLC2CultistAmbushNode absent from captures")
    if not any(row.get("editor_id") == "DLC2WENode" for row in named):
        raise SystemExit("DLC2WENode absent from captures")

    result = {
        "evidence_id_candidate": "EV-0656",
        "route": "direct read-only TES4 file parser; source-file records, not native xEdit or profile winners",
        "source_plugin": "Dragonborn.esm",
        "counts": {signature: len(rows) for signature, rows in all_rows.items()},
        "targets": TARGET_QUESTS,
        "story_records_with_nnam_child_matching_target_quest": linked,
        "named_records": named,
        "raw_capture_hashes": {signature: digest(path) for signature, path in CAPTURES.items()},
        "interpretation_limit": "The scan screens only serialized Dragonborn.esm SMEN/SMQN/SMBN source-file records. Direct-parser CTDA function index 80 is GetLevel per the version-pinned schema used in EXP-0042. Child and parent links still require native xEdit verification; this result does not establish an active-profile winner or runtime route.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUTPUT.as_posix(), "counts": result["counts"], "target_child_links": linked, "named_records": named, "raw_capture_hashes": result["raw_capture_hashes"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
