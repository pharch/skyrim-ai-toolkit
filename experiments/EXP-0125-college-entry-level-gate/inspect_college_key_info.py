#!/usr/bin/env python3
"""Resolve INFO 00107E3D's dialogue owner, quest, conditions, and key property."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import mmap
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/xedit-data/official-ae-v1/Skyrim.esm"
EXPECTED_SHA256 = "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107"
TARGET_INFO = 0x00107E3D
DECODER_PATH = ROOT / "experiments/EXP-0052-da02-level-gate/summarize_da02_initial.py"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.plugin_reader import read_plugin


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def decode_ctda(raw: bytes) -> dict:
    spec = importlib.util.spec_from_file_location("exp0052_ctda_info", DECODER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("EXP-0052 CTDA decoder is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.decode_ctda(raw)
    names = {58: "GetStage", 72: "GetIsID", 629: "GetVMQuestVariable"}
    if result.get("function_index") in names:
        result["function_name"] = names[result["function_index"]]
    return result


def field_map(row: dict) -> dict[str, list[bytes]]:
    result: dict[str, list[bytes]] = {}
    for item in row.get("subrecords", []):
        result.setdefault(item["signature"], []).append(bytes.fromhex(item["value_hex"]))
    return result


def ancestors(path: Path, target: int) -> tuple[list[dict], int]:
    found = []
    record_count = 0

    def walk(data: mmap.mmap, start: int, end: int, groups: list[dict]) -> None:
        nonlocal record_count
        pos = start
        while pos < end:
            if end - pos < 24:
                raise ValueError(f"truncated group/record header at 0x{pos:X}")
            signature, size = struct.unpack_from("<4sI", data, pos)
            if signature == b"GRUP":
                if size < 24 or pos + size > end:
                    raise ValueError(f"invalid group at 0x{pos:X}")
                label = bytes(data[pos + 8:pos + 12])
                group = {
                    "type": struct.unpack_from("<i", data, pos + 12)[0],
                    "label_hex": label.hex(),
                    "label_form_id": int.from_bytes(label, "little"),
                }
                walk(data, pos + 24, pos + size, groups + [group])
                pos += size
                continue
            if pos + 24 + size > end:
                raise ValueError(f"record exceeds group at 0x{pos:X}")
            record_count += 1
            record_id = struct.unpack_from("<I", data, pos + 12)[0]
            if signature == b"INFO" and record_id == target:
                found.append(list(groups))
            pos += 24 + size

    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        walk(data, 0, len(data), [])
    return found, record_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if digest(SOURCE) != EXPECTED_SHA256:
        raise ValueError("prepared Skyrim.esm SHA-256 differs from the expected source")
    ancestry, walked = ancestors(SOURCE, TARGET_INFO)
    if len(ancestry) != 1:
        raise ValueError(f"expected one group ancestry for INFO {TARGET_INFO:08X}; found {len(ancestry)}")
    dial_ids = sorted({group["label_form_id"] for group in ancestry[0] if group["type"] == 7})
    info_row = next((row for row in read_plugin(SOURCE, "INFO", include_subrecords=True)
                     if int(row["file_form_id"], 16) == TARGET_INFO), None)
    if info_row is None:
        raise ValueError("target INFO record was not found by direct TES4 parser")
    dial_rows = [row for row in read_plugin(SOURCE, "DIAL", include_subrecords=True)
                 if int(row["file_form_id"], 16) in dial_ids]
    dials = []
    qids = set()
    for row in dial_rows:
        fields = field_map(row)
        qnam = fields.get("QNAM", [])
        qid = int.from_bytes(qnam[0], "little") if qnam and len(qnam[0]) == 4 else None
        if qid is not None:
            qids.add(qid)
        dials.append({
            "form_id": row["file_form_id"],
            "editor_id": row.get("editor_id"),
            "qnam_quest_form_id": f"{qid:08X}" if qid is not None else None,
            "conditions": [decode_ctda(raw) for raw in fields.get("CTDA", [])],
            "subrecord_signatures": [item["signature"] for item in row.get("subrecords", [])],
        })
    qust_rows = [row for row in read_plugin(SOURCE, "QUST", include_subrecords=True)
                 if int(row["file_form_id"], 16) in qids]
    quests = []
    for row in qust_rows:
        fields = field_map(row)
        quests.append({
            "form_id": row["file_form_id"],
            "editor_id": row.get("editor_id"),
            "subrecord_signatures": [item["signature"] for item in row.get("subrecords", [])],
            "conditions": [decode_ctda(raw) for raw in fields.get("CTDA", [])],
            "vmad_hex": [raw.hex() for raw in fields.get("VMAD", [])],
        })
    info_fields = field_map(info_row)
    result = {
        "source_plugin": "Skyrim.esm",
        "source_sha256": EXPECTED_SHA256,
        "parser": "Read-only TES4 direct record parser plus full GRUP ancestry walk",
        "record_count_walked": walked,
        "target_info": {
            "form_id": info_row["file_form_id"],
            "editor_id": info_row.get("editor_id"),
            "group_ancestry": ancestry[0],
            "subrecord_signatures": [item["signature"] for item in info_row.get("subrecords", [])],
            "conditions": [decode_ctda(raw) for raw in info_fields.get("CTDA", [])],
            "vmad_hex": [raw.hex() for raw in info_fields.get("VMAD", [])],
        },
        "parent_dials": dials,
        "owning_quests": quests,
        "profile_winner_resolved": False,
        "runtime_tested": False,
        "scope_limit": "Source record relationships and condition bytes only; no Papyrus PEX body, active-profile winner, live key inventory, or quest transition was observed.",
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if not output.resolve().is_relative_to((ROOT / ".local").resolve()):
        raise ValueError("capture output must remain below ignored .local/")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_sha256": EXPECTED_SHA256,
        "record_count_walked": walked,
        "target_info": result["target_info"],
        "parent_dials": dials,
        "owning_quests": [{"form_id": q["form_id"], "editor_id": q["editor_id"], "conditions": q["conditions"]} for q in quests],
        "output": output.relative_to(ROOT).as_posix(),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
