#!/usr/bin/env python3
"""Join every fixed-official-order DA03Start DIAL topic to its INFO children."""
from __future__ import annotations

from collections import defaultdict
import argparse
import hashlib
import importlib.util
import json
import mmap
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import REQUIRED_AE_MASTERS, _native_path
from tools.plugin_reader import _subrecords, resolve_record_winner

DECODER_PATH = ROOT / "experiments/EXP-0052-da02-level-gate/summarize_da02_initial.py"
VMAD_CAPTURE = ROOT / ".local/alignment/transactions/TX-20261017-0008/EV-0322-da03-vmad.json"
QUEST_FORM_ID = "000D7939"
TEXT_FIELDS = {"EDID", "FULL", "NAM1", "ANAM", "NNAM", "QNAM", "SNAM"}


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def source_master_names(path: Path) -> list[str]:
    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        if data[:4] != b"TES4":
            raise ValueError(f"missing TES4 header in {path.name}")
        size = struct.unpack_from("<I", data, 4)[0]
        flags = struct.unpack_from("<I", data, 8)[0]
        header = bytes(data[24:24 + size])
        return [value.rstrip(b"\0").decode("cp1252") for name, value in _subrecords(header, flags) if name == "MAST"]


def form_origin(form_id: int, plugin: str, masters_by_plugin: dict[str, list[str]]) -> tuple[str, str]:
    origin_index = form_id >> 24
    masters = masters_by_plugin[plugin]
    origin = (masters + [plugin])[origin_index] if origin_index <= len(masters) else "UNRESOLVED"
    return origin, f"{form_id & 0x00FFFFFF:06X}"


def base_row(data: mmap.mmap, pos: int, signature: str, size: int, path: Path,
             masters_by_plugin: dict[str, list[str]], ancestry: list[dict] | None = None) -> dict:
    flags, form_id = struct.unpack_from("<II", data, pos + 8)
    origin, local_form_id = form_origin(form_id, path.name, masters_by_plugin)
    fields = list(_subrecords(bytes(data[pos + 24:pos + 24 + size]), flags))
    editor_id = next((value.rstrip(b"\0").decode("cp1252", "replace") for name, value in fields if name == "EDID"), "")
    row = {
        "signature": signature,
        "plugin": path.name,
        "origin_plugin": origin,
        "file_form_id": f"{form_id:08X}",
        "local_form_id": local_form_id,
        "offset": pos,
        "flags": f"{flags:08X}",
        "editor_id": editor_id,
        "subrecords": [
            {"signature": name, "length": len(value), "value_hex": value.hex(),
             "text_cp1252": value.rstrip(b"\0").decode("cp1252", "replace")[:512]}
            for name, value in fields
        ],
    }
    if ancestry is not None:
        row["parent_groups"] = ancestry
    return row


def scan_dials(path: Path, masters: list[str]) -> tuple[list[dict], int]:
    """Capture DIAL rows only; record/subrecord payloads for other signatures are skipped."""
    dials: list[dict] = []
    record_count = 0
    master_map = {path.name: masters}

    def walk(data: mmap.mmap, start: int, end: int) -> None:
        nonlocal record_count
        pos = start
        while pos < end:
            if end - pos < 24:
                raise ValueError(f"truncated GRUP/record header at 0x{pos:X}")
            raw_signature, size = struct.unpack_from("<4sI", data, pos)
            if raw_signature == b"GRUP":
                if size < 24 or pos + size > end:
                    raise ValueError(f"invalid GRUP boundary at 0x{pos:X}")
                walk(data, pos + 24, pos + size)
                pos += size
                continue
            if pos + 24 + size > end:
                raise ValueError(f"record exceeds containing GRUP at 0x{pos:X}")
            signature = raw_signature.decode("ascii", "strict")
            record_count += 1
            if signature == "DIAL":
                dials.append(base_row(data, pos, signature, size, path, master_map))
            pos += 24 + size

    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        walk(data, 0, len(data))
    return dials, record_count


def qnam_is_da03(row: dict, masters_by_plugin: dict[str, list[str]]) -> bool:
    for field in row["subrecords"]:
        if field["signature"] != "QNAM" or field["length"] != 4:
            continue
        raw = bytes.fromhex(field["value_hex"])
        origin, local = form_origin(int.from_bytes(raw, "little"), row["plugin"], masters_by_plugin)
        if origin == "Skyrim.esm" and local == QUEST_FORM_ID[2:]:
            return True
    return False


def info_parent_index(path: Path, masters: list[str], topic_ids: set[int]) -> tuple[dict[tuple[str, str], list[dict]], int, int, set[tuple[str, str]]]:
    """Index all INFO locations and identify logical children below target type-7 groups."""
    index: dict[tuple[str, str], list[dict]] = defaultdict(list)
    child_keys: set[tuple[str, str]] = set()
    record_count = 0
    info_count = 0
    master_map = {path.name: masters}

    def walk(data: mmap.mmap, start: int, end: int, ancestry: list[dict]) -> None:
        nonlocal record_count, info_count
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
            record_count += 1
            if raw_signature == b"INFO":
                info_count += 1
                form_id = struct.unpack_from("<I", data, pos + 12)[0]
                origin, local = form_origin(form_id, path.name, master_map)
                key = (origin, local)
                row = {
                    "signature": "INFO",
                    "plugin": path.name,
                    "origin_plugin": origin,
                    "file_form_id": f"{form_id:08X}",
                    "local_form_id": local,
                    "offset": pos,
                    "flags": struct.unpack_from("<I", data, pos + 8)[0],
                    "payload_size": size,
                    "parent_groups": ancestry,
                }
                index[key].append(row)
                if any(group["type"] == 7 and group["label_form_id"] in topic_ids for group in ancestry):
                    child_keys.add(key)
            pos += 24 + size

    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        walk(data, 0, len(data), [])
    return index, record_count, info_count, child_keys


def load_decoder():
    spec = importlib.util.spec_from_file_location("exp0052_ctda_decoder", DECODER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("existing EXP-0052 CTDA decoder is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decode_ctda


def summarize_row(row: dict, plugin_hash: str, decode_ctda) -> dict:
    fields = []
    conditions = []
    for index, subrecord in enumerate(row.get("subrecords", [])):
        raw = bytes.fromhex(subrecord["value_hex"])
        item = {"index": index, "signature": subrecord["signature"], "length": len(raw), "value_hex": raw.hex()}
        if subrecord["signature"] in TEXT_FIELDS:
            item["text_cp1252"] = raw.rstrip(b"\0").decode("cp1252", "replace")
        if subrecord["signature"] == "CTDA":
            item["decoded_ctda"] = decode_ctda(raw) if len(raw) == 32 else {"length": len(raw), "raw": raw.hex()}
            conditions.append(item["decoded_ctda"])
        fields.append(item)
    result = {
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
    if "parent_groups" in row:
        result["parent_groups"] = row["parent_groups"]
    return result


def selected_info_rows(path: Path, indexes: dict[tuple[str, str], list[dict]], wanted: set[tuple[str, str]], plugin_hash: str, decode_ctda) -> list[dict]:
    selected = [row for key in wanted for row in indexes.get(key, [])]
    if not selected:
        return []
    output: list[dict] = []
    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        for header in selected:
            row = base_row(data, header["offset"], "INFO", header["payload_size"], path,
                           {path.name: []}, header["parent_groups"])
            # Replace the origin decoded by the empty local map with the already-resolved header identity.
            row["origin_plugin"] = header["origin_plugin"]
            row["local_form_id"] = header["local_form_id"]
            row["file_form_id"] = header["file_form_id"]
            row["flags"] = f"{header['flags']:08X}"
            output.append(summarize_row(row, plugin_hash, decode_ctda))
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transaction-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"TX-[0-9]{8}-[0-9]{4}", args.transaction_id):
        parser.error("transaction id has an invalid format")
    base = ROOT / ".local/alignment/transactions" / args.transaction_id
    census = json.loads((ROOT / ".local/alignment/transactions/TX-20261017-0007/EV-0321-getlevel-census.json").read_text(encoding="utf-8"))
    expected_hashes = {row["plugin"]: row["sha256"] for row in census["source_files"]}
    config = read_local_config(ROOT)
    data_value = config.get("SKYRIM_DATA", "").strip()
    if not data_value:
        raise RuntimeError("configured official Data directory is unavailable")
    data_root = _native_path(data_value)
    decode_ctda = load_decoder()

    masters_by_plugin: dict[str, list[str]] = {}
    source_hashes: dict[str, str] = {}
    dials_by_key: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    record_counts: dict[str, int] = {}
    for plugin in REQUIRED_AE_MASTERS:
        path = data_root / plugin
        if not path.is_file() or digest(path) != expected_hashes.get(plugin):
            raise RuntimeError(f"official source identity changed since EV-0321: {plugin}")
        source_hashes[plugin] = expected_hashes[plugin]
        masters = source_master_names(path)
        masters_by_plugin[plugin] = masters
        dials, count = scan_dials(path, masters)
        record_counts[plugin] = count
        for row in dials:
            dials_by_key[("DIAL", row["origin_plugin"], row["local_form_id"])].append(row)

    dial_winners: dict[tuple[str, str], dict] = {}
    target_dial_keys = {
        (row["origin_plugin"], row["local_form_id"])
        for copies in dials_by_key.values() for row in copies
        if qnam_is_da03(row, masters_by_plugin)
    }
    for origin, local in target_dial_keys:
        copies = dials_by_key[("DIAL", origin, local)]
        winner_input = resolve_record_winner([
            {"signature": "DIAL", "plugin": row["plugin"], "origin_plugin": row["origin_plugin"], "local_form_id": row["local_form_id"]}
            for row in copies
        ], list(REQUIRED_AE_MASTERS))
        winner = next(row for row in copies if row["plugin"] == winner_input["plugin"])
        if qnam_is_da03(winner, masters_by_plugin):
            dial_winners[(origin, local)] = winner
    topic_ids = {int(row["file_form_id"], 16) for row in dial_winners.values()}
    topic_keys = set(dial_winners)

    indexes_by_plugin: dict[str, dict[tuple[str, str], list[dict]]] = {}
    info_children: set[tuple[str, str]] = set()
    info_counts: dict[str, int] = {}
    for plugin in REQUIRED_AE_MASTERS:
        index, walked, info_count, child_keys = info_parent_index(data_root / plugin, masters_by_plugin[plugin], topic_ids)
        indexes_by_plugin[plugin] = index
        info_children.update(child_keys)
        info_counts[plugin] = info_count
        if walked != record_counts[plugin]:
            raise RuntimeError(f"record traversal count changed between scans for {plugin}: {record_counts[plugin]} vs {walked}")

    info_copies: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for plugin in REQUIRED_AE_MASTERS:
        for (origin, local), summaries in indexes_by_plugin[plugin].items():
            if (origin, local) not in info_children:
                continue
            rows = selected_info_rows(data_root / plugin, indexes_by_plugin[plugin], {(origin, local)}, source_hashes[plugin], decode_ctda)
            info_copies[("INFO", origin, local)].extend(rows)

    info_winners: dict[tuple[str, str], dict] = {}
    info_sources: dict[tuple[str, str], list[dict]] = {}
    for (_, origin, local), copies in info_copies.items():
        winner_input = resolve_record_winner([
            {"signature": "INFO", "plugin": row["plugin"], "origin_plugin": row["origin_plugin"], "local_form_id": row["local_form_id"]}
            for row in copies
        ], list(REQUIRED_AE_MASTERS))
        winner = next(row for row in copies if row["plugin"] == winner_input["plugin"])
        info_winners[(origin, local)] = winner
        info_sources[(origin, local)] = [
            {"plugin": row["plugin"], "file_form_id": row["file_form_id"],
             "parent_groups": row.get("parent_groups", []), "ctda_count": len(row["conditions"])}
            for row in sorted(copies, key=lambda item: REQUIRED_AE_MASTERS.index(item["plugin"]))
        ]

    topics: list[dict] = []
    for key, winner in sorted(dial_winners.items(), key=lambda item: int(item[1]["file_form_id"], 16)):
        topic_id = int(winner["file_form_id"], 16)
        children = [info_winners[info_key] for info_key in sorted(info_winners)
                    if any(group["type"] == 7 and group["label_form_id"] == topic_id
                           for group in info_winners[info_key].get("parent_groups", []))]
        topics.append({
            "winner": summarize_row(winner, source_hashes[winner["plugin"]], decode_ctda),
            "source_copies": [
                {"plugin": row["plugin"], "file_form_id": row["file_form_id"],
                 "qnam": next((field["value_hex"] for field in row["subrecords"] if field["signature"] == "QNAM"), None)}
                for row in sorted(dials_by_key[("DIAL", key[0], key[1])], key=lambda item: REQUIRED_AE_MASTERS.index(item["plugin"]))
            ],
            "info_child_count": len(children),
            "info_children": [
                {"winner": child, "source_copies": info_sources[(child["origin_plugin"], child["local_form_id"])]}
                for child in children
            ],
        })

    result = {
        "capture_id": "EV-0322-DA03Start-topic-source-join",
        "source_capture": "EV-0321-getlevel-census.json",
        "source_hashes_rechecked": source_hashes,
        "source_record_counts": record_counts,
        "source_info_counts": info_counts,
        "source_order": list(REQUIRED_AE_MASTERS),
        "source_order_scope": "Fixed official-master winner resolution only; not a user-profile winner or native xEdit view.",
        "main_helper_quest": {"form_id": QUEST_FORM_ID, "editor_id": "DA03Start"},
        "topic_count": len(topics),
        "topic_form_ids": [row["winner"]["file_form_id"] for row in topics],
        "info_candidate_count": len(info_children),
        "topics": topics,
        "interpretation_limits": [
            "GRUP type-7 ancestry supplies the DIAL-to-INFO relation; INFO TPIC is not used as a parent key.",
            "Only the fixed official-master order is resolved. No complete target active order or profile winner is configured.",
            "NAM1 and other localized response fields are retained as raw IDs/bytes; no text is inferred without the matching strings source.",
            "Static topic ownership and conditions do not establish dialogue availability, quest startup, alias fill, functional access, or level-one runtime behavior.",
        ],
    }
    output = base / "EV-0322-da03-topics.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": output.relative_to(ROOT).as_posix(),
        "source_hashes_rechecked": source_hashes,
        "topic_count": len(topics),
        "info_child_count": len(info_children),
        "topics": [{
            "form_id": row["winner"]["file_form_id"],
            "editor_id": row["winner"]["editor_id"],
            "topic_type": next((field.get("text_cp1252") for field in row["winner"]["subrecords"] if field["signature"] == "SNAM"), None),
            "info_child_count": row["info_child_count"],
            "info_ids": [child["winner"]["file_form_id"] for child in row["info_children"]],
        } for row in topics],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
