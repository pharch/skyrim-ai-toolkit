#!/usr/bin/env python3
"""Join MG01/MG02 DIAL topics to INFO children and decode their conditions."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import mmap
from pathlib import Path
import struct
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/xedit-data/official-ae-v1/Skyrim.esm"
EXPECTED_SHA256 = "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107"
QUESTS = {"MG01": 0x0001F251, "MG02": 0x0001F252}
DECODER_PATH = ROOT / "experiments/EXP-0052-da02-level-gate/summarize_da02_initial.py"
# Names are copied from the TES5Edit/TES5Edit dev-4.1.6 schema lines recorded
# in schema-notes.md. Other condition operands remain decoded by EXP-0052.
SCHEMA_FUNCTIONS = {
    1: "GetDistance", 14: "GetActorValue", 47: "GetItemCount",
    50: "GetTalkedToPC", 58: "GetStage", 59: "GetStageDone",
    67: "GetInCell", 71: "GetInFaction", 72: "GetIsID", 80: "GetLevel",
    130: "GetPCIsRace", 131: "GetPCIsSex", 182: "GetEquipped",
    249: "IsInDialogueWithPlayer", 264: "HasSpell", 359: "GetInCurrentLoc",
    448: "HasPerk", 566: "GetIsAliasRef", 629: "GetVMQuestVariable",
    630: "GetVMScriptVariable",
}
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.plugin_reader import read_plugin


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def decoder():
    spec = importlib.util.spec_from_file_location("exp0052_college_ctda", DECODER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("existing EXP-0052 CTDA decoder is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decode_ctda


def subrecords(row: dict) -> dict[str, list[bytes]]:
    result: dict[str, list[bytes]] = {}
    for field in row.get("subrecords", []):
        result.setdefault(field["signature"], []).append(bytes.fromhex(field["value_hex"]))
    return result


def decode_conditions(fields: dict[str, list[bytes]], decode_ctda) -> list[dict]:
    result = []
    for value in fields.get("CTDA", []):
        decoded = decode_ctda(value)
        if decoded.get("function_index") in SCHEMA_FUNCTIONS:
            decoded["function_name"] = SCHEMA_FUNCTIONS[decoded["function_index"]]
        result.append(decoded)
    return result


def info_ancestry(path: Path, topic_ids: set[int]) -> tuple[dict[int, list[dict]], int]:
    parents: dict[int, list[dict]] = {}
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
                group = {
                    "type": struct.unpack_from("<I", data, pos + 12)[0],
                    "label_hex": label.hex(),
                    "label_form_id": int.from_bytes(label, "little"),
                }
                walk(data, pos + 24, pos + size, ancestry + [group])
                pos += size
                continue
            if pos + 24 + size > end:
                raise ValueError(f"record exceeds containing group at 0x{pos:X}")
            record_count += 1
            form_id = struct.unpack_from("<I", data, pos + 12)[0]
            if signature == b"INFO":
                owners = [group for group in ancestry if group["label_form_id"] in topic_ids]
                if owners:
                    parents[form_id] = owners
            pos += 24 + size

    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        walk(data, 0, len(data), [])
    return parents, record_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not SOURCE.is_file():
        raise FileNotFoundError("prepared official Skyrim.esm is unavailable")
    source_hash = digest(SOURCE)
    if source_hash != EXPECTED_SHA256:
        raise ValueError("prepared Skyrim.esm SHA-256 differs from the expected source")
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    if not output_path.resolve().is_relative_to((ROOT / ".local").resolve()):
        raise ValueError("capture output must remain under ignored .local/")

    decode_ctda = decoder()
    dials = list(read_plugin(SOURCE, "DIAL", include_subrecords=True))
    quest_topics: dict[str, dict[int, dict]] = {name: {} for name in QUESTS}
    quest_ids = {value: name for name, value in QUESTS.items()}
    for row in dials:
        fields = subrecords(row)
        qnam = fields.get("QNAM", [])
        if not qnam or len(qnam[0]) != 4:
            continue
        quest_id = int.from_bytes(qnam[0], "little")
        quest_name = quest_ids.get(quest_id)
        if quest_name is None:
            continue
        topic_id = int(row["file_form_id"], 16)
        quest_topics[quest_name][topic_id] = {
            "form_id": row["file_form_id"],
            "editor_id": row.get("editor_id"),
            "conditions": decode_conditions(fields, decode_ctda),
            "info_ids": [],
            "infos": [],
        }

    all_topic_ids = {topic_id for topics in quest_topics.values() for topic_id in topics}
    parents, walked = info_ancestry(SOURCE, all_topic_ids)
    infos = {}
    info_rows = {int(row["file_form_id"], 16): row
                 for row in read_plugin(SOURCE, "INFO", include_subrecords=True)
                 if int(row["file_form_id"], 16) in parents}
    info_counts: dict[str, Counter[str]] = {name: Counter() for name in QUESTS}
    dial_counts: dict[str, Counter[str]] = {name: Counter() for name in QUESTS}
    getlevel_hits: dict[str, list[dict]] = {name: [] for name in QUESTS}
    topic_owner = {topic_id: name for name, topics in quest_topics.items() for topic_id in topics}
    for name, topics in quest_topics.items():
        for topic_id, topic in topics.items():
            for condition in topic["conditions"]:
                name_value = condition.get("function_name", f"unknown:{condition.get('function_index')}")
                dial_counts[name][name_value] += 1
                if condition.get("function_index") == 80:
                    getlevel_hits[name].append({
                        "record_kind": "DIAL",
                        "topic_form_id": f"{topic_id:08X}",
                        "condition": condition,
                    })
    for info_id, row in info_rows.items():
        fields = subrecords(row)
        conditions = decode_conditions(fields, decode_ctda)
        owners = parents[info_id]
        info = {
            "form_id": row["file_form_id"],
            "editor_id": row.get("editor_id"),
            "parent_groups": owners,
            "conditions": conditions,
            "response_text_byte_lengths": [len(value) for value in fields.get("NAM1", [])],
        }
        infos[info_id] = info
        for group in owners:
            owner_name = topic_owner.get(group["label_form_id"])
            if owner_name is None:
                continue
            topic = quest_topics[owner_name][group["label_form_id"]]
            topic["info_ids"].append(row["file_form_id"])
            topic["infos"].append(info)
            for condition in conditions:
                name_value = condition.get("function_name", f"unknown:{condition.get('function_index')}")
                info_counts[owner_name][name_value] += 1
                if condition.get("function_index") == 80:
                    getlevel_hits[owner_name].append({
                        "record_kind": "INFO",
                        "topic_form_id": f"{group['label_form_id']:08X}",
                        "info_form_id": row["file_form_id"],
                        "condition": condition,
                    })

    quest_results = {}
    for name, topics in quest_topics.items():
        topic_rows = []
        for topic_id, topic in sorted(topics.items()):
            topic["info_ids"].sort()
            topic_rows.append(topic)
        quest_results[name] = {
            "quest_form_id": f"{QUESTS[name]:08X}",
            "dial_topic_count": len(topics),
            "info_count": len({info_id for topic in topics.values() for info_id in topic["info_ids"]}),
            "dial_condition_function_counts": dict(sorted(dial_counts[name].items())),
            "info_condition_function_counts": dict(sorted(info_counts[name].items())),
            "getlevel_conditions": getlevel_hits[name],
            "topics": topic_rows,
        }
    result = {
        "source_plugin": "Skyrim.esm",
        "source_sha256": source_hash,
        "parser": "tools.plugin_reader.read_plugin plus full GRUP ancestry walk",
        "scope": "DIAL QNAM -> QUST and INFO child groups for exact MG01/MG02 QUST source FormIDs; not a profile winner or runtime query",
        "record_count_walked": walked,
        "dials_read": len(dials),
        "results": quest_results,
        "profile_winner_resolved": False,
        "runtime_tested": False,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_sha256": source_hash,
        "record_count_walked": walked,
        "dials_read": len(dials),
        "results": {
            name: {
                "dial_topic_count": value["dial_topic_count"],
                "info_count": value["info_count"],
                "dial_condition_function_counts": value["dial_condition_function_counts"],
                "info_condition_function_counts": value["info_condition_function_counts"],
                "getlevel_condition_count": len(value["getlevel_conditions"]),
            }
            for name, value in quest_results.items()
        },
        "output": output_path.relative_to(ROOT).as_posix(),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
