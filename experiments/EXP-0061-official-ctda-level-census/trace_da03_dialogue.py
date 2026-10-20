#!/usr/bin/env python3
"""Join the level-gated DA03 guard package topic to official DIAL/INFO records."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import importlib.util
import json
import mmap
from pathlib import Path
import re
import sys
import struct

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import REQUIRED_AE_MASTERS, _native_path
from tools.plugin_reader import _subrecords, resolve_record_winner

DECODER_PATH = ROOT / "experiments/EXP-0052-da02-level-gate/summarize_da02_initial.py"
TOPIC_FORM_ID = "000E0D44"
PACKAGE_FORM_ID = "000E0D53"
START_QUEST_FORM_ID = "000D7939"
TEXT_FIELDS = {"EDID", "FULL", "NAM1", "ANAM", "NNAM", "QNAM", "SNAM"}


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def load_decoder():
    spec = importlib.util.spec_from_file_location("exp0052_ctda_decoder", DECODER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("existing EXP-0052 CTDA decoder is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decode_ctda


def summarize_record(row: dict, plugin_hash: str, decode_ctda) -> dict:
    fields = []
    conditions = []
    for index, subrecord in enumerate(row.get("subrecords", [])):
        raw = bytes.fromhex(subrecord["value_hex"])
        item = {
            "index": index,
            "signature": subrecord["signature"],
            "length": len(raw),
            "value_hex": raw.hex(),
        }
        if subrecord["signature"] in TEXT_FIELDS:
            item["text_cp1252"] = raw.rstrip(b"\0").decode("cp1252", "replace")
        if subrecord["signature"] == "CTDA":
            item["decoded_ctda"] = decode_ctda(raw) if len(raw) == 32 else {"length": len(raw), "raw": raw.hex()}
            conditions.append(item["decoded_ctda"])
        fields.append(item)
    return {
        "signature": row["signature"],
        "plugin": row["plugin"],
        "source_sha256": plugin_hash,
        "origin_plugin": row["origin_plugin"],
        "file_form_id": row["file_form_id"],
        "local_form_id": row["local_form_id"],
        "editor_id": row["editor_id"],
        "flags": row["flags"],
        "subrecords": fields,
        "conditions": conditions,
    }


def info_parent_index(path: Path, topic_id: int) -> tuple[dict[str, list[dict]], int]:
    """Map INFO FormIDs below the target DIAL child group to their GRUP ancestry."""
    matches: dict[str, list[dict]] = {}
    record_count = 0

    def walk(data: mmap.mmap, start: int, end: int, ancestry: list[dict]) -> None:
        nonlocal record_count
        pos = start
        while pos < end:
            if end - pos < 24:
                raise ValueError(f"truncated GRUP/record header at 0x{pos:X}")
            signature, size = struct.unpack_from("<4sI", data, pos)
            if signature == b"GRUP":
                if size < 24 or pos + size > end:
                    raise ValueError(f"invalid GRUP boundary at 0x{pos:X}")
                label = data[pos + 8:pos + 12]
                group_type = struct.unpack_from("<I", data, pos + 12)[0]
                group = {
                    "type": group_type,
                    "label_hex": label.hex(),
                    "label_form_id": int.from_bytes(label, "little"),
                }
                walk(data, pos + 24, pos + size, ancestry + [group])
                pos += size
                continue
            if pos + 24 + size > end:
                raise ValueError(f"record exceeds containing GRUP at 0x{pos:X}")
            record_count += 1
            if signature == b"INFO":
                parents = [group for group in ancestry if group["type"] == 7 and group["label_form_id"] == topic_id]
                if parents:
                    form_id = struct.unpack_from("<I", data, pos + 12)[0]
                    matches[f"{form_id:08X}"] = ancestry
            pos += 24 + size

    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        walk(data, 0, len(data), [])
    return matches, record_count


def plugin_masters(path: Path) -> list[str]:
    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        if data[:4] != b"TES4":
            raise ValueError(f"missing TES4 header in {path.name}")
        size = struct.unpack_from("<I", data, 4)[0]
        flags = struct.unpack_from("<I", data, 8)[0]
        payload = bytes(data[24:24 + size])
        return [value.rstrip(b"\0").decode("cp1252") for name, value in _subrecords(payload, flags) if name == "MAST"]


def selected_records(path: Path, candidate_info_keys: set[tuple[str, str]], topic_id: int) -> tuple[list[dict], list[dict]]:
    """Read only the target DIAL and INFO candidates while preserving each INFO parent group."""
    masters = plugin_masters(path)
    dials: list[dict] = []
    infos: list[dict] = []

    def make_row(data: mmap.mmap, pos: int, signature: str, size: int, ancestry: list[dict]) -> dict:
        flags, form_id = struct.unpack_from("<II", data, pos + 8)
        origin_index = form_id >> 24
        origin = (masters + [path.name])[origin_index] if origin_index <= len(masters) else "UNRESOLVED"
        fields = list(_subrecords(bytes(data[pos + 24:pos + 24 + size]), flags))
        editor_id = next((value.rstrip(b"\0").decode("cp1252", "replace") for name, value in fields if name == "EDID"), "")
        return {
            "signature": signature,
            "plugin": path.name,
            "origin_plugin": origin,
            "file_form_id": f"{form_id:08X}",
            "local_form_id": f"{form_id & 0x00FFFFFF:06X}",
            "offset": f"0x{pos:X}",
            "flags": f"{flags:08X}",
            "editor_id": editor_id,
            "parent_groups": ancestry,
            "subrecords": [
                {"signature": name, "length": len(value), "value_hex": value.hex(),
                 "text_cp1252": value.rstrip(b"\0").decode("cp1252", "replace")[:512]}
                for name, value in fields
            ],
        }

    def walk(data: mmap.mmap, start: int, end: int, ancestry: list[dict]) -> None:
        pos = start
        while pos < end:
            if end - pos < 24:
                raise ValueError(f"truncated GRUP/record header at 0x{pos:X}")
            raw_signature, size = struct.unpack_from("<4sI", data, pos)
            if raw_signature == b"GRUP":
                if size < 24 or pos + size > end:
                    raise ValueError(f"invalid GRUP boundary at 0x{pos:X}")
                label = data[pos + 8:pos + 12]
                group = {
                    "type": struct.unpack_from("<I", data, pos + 12)[0],
                    "label_hex": label.hex(),
                    "label_form_id": int.from_bytes(label, "little"),
                }
                walk(data, pos + 24, pos + size, ancestry + [group])
                pos += size
                continue
            if pos + 24 + size > end:
                raise ValueError(f"record exceeds containing GRUP at 0x{pos:X}")
            signature = raw_signature.decode("ascii", "strict")
            if signature in {"DIAL", "INFO"}:
                form_id = struct.unpack_from("<I", data, pos + 12)[0]
                if signature == "DIAL" and form_id == topic_id:
                    dials.append(make_row(data, pos, signature, size, ancestry))
                elif signature == "INFO":
                    origin_index = form_id >> 24
                    origin = (masters + [path.name])[origin_index] if origin_index <= len(masters) else "UNRESOLVED"
                    key = (origin, f"{form_id & 0x00FFFFFF:06X}")
                    if key in candidate_info_keys:
                        infos.append(make_row(data, pos, signature, size, ancestry))
            pos += 24 + size

    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        walk(data, 0, len(data), [])
    return dials, infos


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transaction-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"TX-[0-9]{8}-[0-9]{4}", args.transaction_id):
        parser.error("transaction id has an invalid format")
    base = ROOT / ".local/alignment/transactions" / args.transaction_id
    capture = json.loads((base / "EV-0321-getlevel-census.json").read_text(encoding="utf-8"))
    expected_hashes = {row["plugin"]: row["sha256"] for row in capture["source_files"]}
    config = read_local_config(ROOT)
    data_value = config.get("SKYRIM_DATA", "").strip()
    if not data_value:
        raise RuntimeError("configured official Data directory is unavailable")
    data_root = _native_path(data_value)
    decode_ctda = load_decoder()

    dialects: list[dict] = []
    initial_info_ids: set[tuple[str, str]] = set()
    info_parent_by_file: dict[str, dict[str, list[dict]]] = {}
    parser_record_counts: dict[str, int] = {}
    source_hashes: dict[str, str] = {}
    for plugin in REQUIRED_AE_MASTERS:
        path = data_root / plugin
        if not path.is_file() or digest(path) != expected_hashes.get(plugin):
            raise RuntimeError(f"official source identity changed since EV-0321: {plugin}")
        source_hashes[plugin] = expected_hashes[plugin]
        parents, record_count = info_parent_index(path, int(TOPIC_FORM_ID, 16))
        info_parent_by_file[plugin] = parents
        parser_record_counts[plugin] = record_count
        masters = plugin_masters(path)
        for raw_form_id in parents:
            form_id = int(raw_form_id, 16)
            origin_index = form_id >> 24
            origin = (masters + [plugin])[origin_index] if origin_index <= len(masters) else "UNRESOLVED"
            initial_info_ids.add((origin, f"{form_id & 0x00FFFFFF:06X}"))

    # Read every copy of each linked INFO logical record, even if an override
    # moves it under another DIAL group. The winner's parent group is reported.
    info_copies: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for plugin in REQUIRED_AE_MASTERS:
        path = data_root / plugin
        dial_rows, info_rows = selected_records(path, initial_info_ids, int(TOPIC_FORM_ID, 16))
        dialects.extend(summarize_record(row, expected_hashes[plugin], decode_ctda) for row in dial_rows)
        for row in info_rows:
            key = (row["signature"], row["origin_plugin"], row["local_form_id"])
            summary = summarize_record(row, expected_hashes[plugin], decode_ctda)
            summary["parent_groups"] = row["parent_groups"]
            info_copies[key].append({
                "summary": summary,
                "winner_input": {
                    "signature": row["signature"],
                    "plugin": plugin,
                    "origin_plugin": row["origin_plugin"],
                    "local_form_id": row["local_form_id"],
                },
            })

    if not dialects:
        raise RuntimeError(f"PDTO topic {TOPIC_FORM_ID} was not found in the five official masters")
    winning_info = []
    for key, copies in sorted(info_copies.items()):
        winner_input = resolve_record_winner([item["winner_input"] for item in copies], list(REQUIRED_AE_MASTERS))
        winner = next(item["summary"] for item in copies if item["summary"]["plugin"] == winner_input["plugin"])
        winning_info.append({
            "winner": winner,
            "source_copies": [
                {
                    "plugin": item["summary"]["plugin"],
                    "editor_id": item["summary"]["editor_id"],
                    "file_form_id": item["summary"]["file_form_id"],
                    "ctda_count": len(item["summary"]["conditions"]),
                }
                for item in sorted(copies, key=lambda item: REQUIRED_AE_MASTERS.index(item["summary"]["plugin"]))
            ],
        })
    result = {
        "capture_id": "EV-0321-DA03-dialogue-source-join",
        "source_capture": "EV-0321-getlevel-census.json",
        "source_hashes_rechecked": source_hashes,
        "source_record_counts_by_file_walk": parser_record_counts,
        "parser_group_type": 7,
        "INFO_parent_join": "INFO record ancestry under GRUP type 7 labeled by DIAL FormID; all official-source copies of matched logical INFO IDs are retained for source-layer resolution.",
        "source_order_scope": "Fixed official-master source order only; not a user profile winner or native xEdit view.",
        "package": {"form_id": PACKAGE_FORM_ID, "editor_id": "DA03StartGuardStartQuestGreet"},
        "start_helper_quest": {"form_id": START_QUEST_FORM_ID, "editor_id": "DA03Start"},
        "PDTO_topic_form_id": TOPIC_FORM_ID,
        "DIAL_record_copies": dialects,
        "INFO_source_copy_count": sum(len(copies) for copies in info_copies.values()),
        "INFO_winning_child_count": len(winning_info),
        "INFO_children": winning_info,
    }
    out_path = base / "EV-0321-da03-dialogue-join.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "PDTO_topic_form_id": TOPIC_FORM_ID,
        "DIAL_record_copies": [
            {"plugin": row["plugin"], "form_id": row["file_form_id"], "editor_id": row["editor_id"], "subrecord_signatures": [field["signature"] for field in row["subrecords"]]}
            for row in dialects
        ],
        "INFO_source_copy_count": result["INFO_source_copy_count"],
        "INFO_winning_child_count": len(winning_info),
        "INFO_children": [
            {
                "plugin": item["winner"]["plugin"],
                "form_id": item["winner"]["file_form_id"],
                "editor_id": item["winner"]["editor_id"],
                "subrecords": [
                    {"signature": field["signature"], "length": field["length"], "text_cp1252": field.get("text_cp1252"), "decoded_ctda": field.get("decoded_ctda")}
                    for field in item["winner"]["subrecords"]
                    if field["signature"] in TEXT_FIELDS | {"CTDA", "QSTI", "TPIC", "PNAM", "VMAD", "SCHR", "SCDA", "SCTX"}
                ],
            }
            for item in winning_info
        ],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
