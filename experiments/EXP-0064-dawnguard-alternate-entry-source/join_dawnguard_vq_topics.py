#!/usr/bin/env python3
"""Join fixed-official Dawnguard alternate-entry DIAL topics to INFO children."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import importlib.util
import json
import mmap
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.local_config import read_local_config
from tools.ae_target import REQUIRED_AE_MASTERS, _native_path
from tools.plugin_reader import _subrecords, resolve_record_winner

CENSUS = ROOT / ".local/alignment/transactions/TX-20261017-0007/EV-0321-getlevel-census.json"
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261017-0010/dawnguard-vq-topic-join.json"
TARGET_QUESTS = {
    "0200D90E": "DLC1VQ00",
    "0200D06C": "DLC1VQ01MiscObjective",
    "0201A415": "DLC1VQCastleGuard",
    "0200352A": "DLC1VQ01",
}
TEXT_FIELDS = {"EDID", "FULL", "NAM1", "ANAM", "NNAM", "QNAM", "SNAM"}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def source_masters(path: Path) -> list[str]:
    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        if data[:4] != b"TES4":
            raise ValueError(f"missing TES4 header in {path.name}")
        size = struct.unpack_from("<I", data, 4)[0]
        flags = struct.unpack_from("<I", data, 8)[0]
        return [value.rstrip(b"\0").decode("cp1252") for sig, value in _subrecords(bytes(data[24:24 + size]), flags) if sig == "MAST"]


def origin(form_id: int, plugin: str, masters: dict[str, list[str]]) -> tuple[str, str]:
    index = form_id >> 24
    names = masters[plugin]
    return (names + [plugin])[index] if index <= len(names) else "UNRESOLVED", f"{form_id & 0x00FFFFFF:06X}"


def record_row(data: mmap.mmap, pos: int, sig: str, size: int, path: Path,
               masters: dict[str, list[str]], ancestry: list[dict] | None = None) -> dict:
    flags, form_id = struct.unpack_from("<II", data, pos + 8)
    record_origin, local = origin(form_id, path.name, masters)
    fields = list(_subrecords(bytes(data[pos + 24:pos + 24 + size]), flags))
    row = {
        "signature": sig,
        "plugin": path.name,
        "origin_plugin": record_origin,
        "file_form_id": f"{form_id:08X}",
        "local_form_id": local,
        "offset": pos,
        "flags": f"{flags:08X}",
        "editor_id": next((value.rstrip(b"\0").decode("cp1252", "replace") for name, value in fields if name == "EDID"), ""),
        "subrecords": [{"signature": name, "length": len(value), "value_hex": value.hex(),
                        "text_cp1252": value.rstrip(b"\0").decode("cp1252", "replace")[:512]}
                       for name, value in fields],
    }
    if ancestry is not None:
        row["parent_groups"] = ancestry
    return row


def walk_records(data: mmap.mmap, start: int, end: int, path: Path,
                 masters: dict[str, list[str]], *, wanted_signature: str,
                 ancestry: list[dict] | None = None):
    pos = start
    groups = ancestry or []
    while pos < end:
        if end - pos < 24:
            raise ValueError(f"truncated record header at 0x{pos:X}")
        raw_sig, size = struct.unpack_from("<4sI", data, pos)
        if raw_sig == b"GRUP":
            if size < 24 or pos + size > end:
                raise ValueError(f"invalid GRUP boundary at 0x{pos:X}")
            label = data[pos + 8:pos + 12]
            group = {"type": struct.unpack_from("<I", data, pos + 12)[0],
                     "label_hex": label.hex(), "label_form_id": int.from_bytes(label, "little")}
            yield from walk_records(data, pos + 24, pos + size, path, masters,
                                    wanted_signature=wanted_signature, ancestry=groups + [group])
            pos += size
            continue
        if pos + 24 + size > end:
            raise ValueError(f"record exceeds containing GRUP at 0x{pos:X}")
        signature = raw_sig.decode("ascii", "strict")
        if signature == wanted_signature:
            yield record_row(data, pos, signature, size, path, masters, groups)
        pos += 24 + size


def qnam_id(row: dict, masters: dict[str, list[str]]) -> str | None:
    for field in row["subrecords"]:
        if field["signature"] == "QNAM" and field["length"] == 4:
            return f"{int.from_bytes(bytes.fromhex(field['value_hex']), 'little'):08X}"
    return None


def decode_ctda_module():
    path = ROOT / "experiments/EXP-0052-da02-level-gate/summarize_da02_initial.py"
    spec = importlib.util.spec_from_file_location("dawnguard_ctda_decoder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("existing TES5Edit-schema CTDA decoder is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decode_ctda


def annotate(row: dict, plugin_hashes: dict[str, str], decode_ctda) -> dict:
    out = dict(row)
    out["source_sha256"] = plugin_hashes[row["plugin"]]
    out["conditions"] = []
    for field in row["subrecords"]:
        if field["signature"] == "CTDA":
            raw = bytes.fromhex(field["value_hex"])
            out["conditions"].append(decode_ctda(raw) if len(raw) == 32 else {"length": len(raw), "raw": raw.hex()})
    return out


def resolve(copies: dict[tuple[str, str, str], list[dict]], signature: str,
            source_order: list[str]) -> tuple[dict[tuple[str, str], dict], dict[tuple[str, str], list[dict]]]:
    winners: dict[tuple[str, str], dict] = {}
    all_copies: dict[tuple[str, str], list[dict]] = {}
    for (sig, record_origin, local), rows in copies.items():
        candidate_rows = [{"signature": sig, "plugin": row["plugin"], "origin_plugin": record_origin,
                           "local_form_id": local} for row in rows]
        winner_desc = resolve_record_winner(candidate_rows, source_order)
        winners[(record_origin, local)] = next(row for row in rows if row["plugin"] == winner_desc["plugin"])
        all_copies[(record_origin, local)] = sorted(rows, key=lambda row: source_order.index(row["plugin"]))
    return winners, all_copies


def main() -> int:
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    expected = {row["plugin"]: row["sha256"] for row in census["source_files"]}
    config = read_local_config(ROOT)
    data_value = config.get("SKYRIM_DATA", "").strip()
    if not data_value:
        raise RuntimeError("configured official Data directory is unavailable")
    data_root = _native_path(data_value)
    masters: dict[str, list[str]] = {}
    plugin_hashes: dict[str, str] = {}
    dials_by_key: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    record_counts: dict[str, int] = {}
    for plugin in REQUIRED_AE_MASTERS:
        path = data_root / plugin
        if not path.is_file() or digest(path) != expected.get(plugin):
            raise RuntimeError(f"official source identity changed since EV-0321: {plugin}")
        plugin_hashes[plugin] = expected[plugin]
        masters[plugin] = source_masters(path)
        with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            count = 0
            for sig, *_ in __import__("tools.plugin_reader", fromlist=["_records"])._records(data):
                count += 1
            record_counts[plugin] = count
            for row in walk_records(data, 0, len(data), path, masters, wanted_signature="DIAL"):
                quest = qnam_id(row, masters)
                if quest in TARGET_QUESTS:
                    dials_by_key[("DIAL", row["origin_plugin"], row["local_form_id"])].append(row)

    dial_winners, dial_copies = resolve(dials_by_key, "DIAL", list(REQUIRED_AE_MASTERS))
    targets = {}
    for key, winner in dial_winners.items():
        qnam = qnam_id(winner, masters)
        if qnam in TARGET_QUESTS:
            targets[key] = winner
    topic_ids = {int(row["file_form_id"], 16) for row in targets.values()}
    info_copies: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    info_counts: dict[str, int] = {}
    for plugin in REQUIRED_AE_MASTERS:
        path = data_root / plugin
        with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            count = 0
            for row in walk_records(data, 0, len(data), path, masters, wanted_signature="INFO"):
                count += 1
                if any(group["type"] == 7 and group["label_form_id"] in topic_ids for group in row.get("parent_groups", [])):
                    info_copies[("INFO", row["origin_plugin"], row["local_form_id"])].append(row)
            info_counts[plugin] = count
    info_winners, info_sources = resolve(info_copies, "INFO", list(REQUIRED_AE_MASTERS))
    decode_ctda = decode_ctda_module()

    topics = []
    for key, dial in sorted(targets.items(), key=lambda item: int(item[1]["file_form_id"], 16)):
        dial_copy_key = ("DIAL", key[0], key[1])
        dial_rows = dial_copies[key]
        topic_id = int(dial["file_form_id"], 16)
        children = [row for child_key, row in info_winners.items()
                    if any(group["type"] == 7 and group["label_form_id"] == topic_id for group in row.get("parent_groups", []))]
        child_payloads = []
        for child in sorted(children, key=lambda row: int(row["file_form_id"], 16)):
            child_copies = info_sources[(child["origin_plugin"], child["local_form_id"])]
            child_payloads.append({
                "winner": annotate(child, plugin_hashes, decode_ctda),
                "source_copies": [{"plugin": copy["plugin"], "file_form_id": copy["file_form_id"],
                                   "parent_groups": copy.get("parent_groups", [])} for copy in child_copies],
            })
        topics.append({
            "quest_form_id": qnam_id(dial, masters),
            "quest_editor_id": TARGET_QUESTS[qnam_id(dial, masters)],
            "dial_winner": annotate(dial, plugin_hashes, decode_ctda),
            "dial_source_copies": [{"plugin": row["plugin"], "file_form_id": row["file_form_id"], "qnam": qnam_id(row, masters)} for row in dial_rows],
            "info_children": child_payloads,
        })
    result = {
        "capture_id": "Q-0063 Dawnguard VQ dialogue source join",
        "source_evidence": "EV-0321 official-master hash census",
        "source_hashes_rechecked": plugin_hashes,
        "source_record_counts": record_counts,
        "source_info_counts": info_counts,
        "source_order": list(REQUIRED_AE_MASTERS),
        "source_order_scope": "Fixed official-master source-winner resolution only; not a user-profile winner or native xEdit view.",
        "quest_form_ids": TARGET_QUESTS,
        "topic_count": len(topics),
        "topic_form_ids": [topic["dial_winner"]["file_form_id"] for topic in topics],
        "topics": topics,
        "limits": ["DIAL-to-INFO linkage uses GRUP type-7 ancestry, not TPIC.",
                   "No user plugin/profile order or live dialogue/quest state is represented.",
                   "Localized strings are retained as raw IDs/bytes; they are not inferred."]
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "topic_count": len(topics),
        "info_child_count": sum(len(topic["info_children"]) for topic in topics),
        "topics": [{"quest": topic["quest_editor_id"], "form_id": topic["dial_winner"]["file_form_id"],
                    "editor_id": topic["dial_winner"]["editor_id"],
                    "children": [{"form_id": child["winner"]["file_form_id"], "editor_id": child["winner"]["editor_id"],
                                  "conditions": child["winner"]["conditions"],
                                  "vmad": any(field["signature"] == "VMAD" for field in child["winner"]["subrecords"])}
                                 for child in topic["info_children"]]}
                   for topic in topics]
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
