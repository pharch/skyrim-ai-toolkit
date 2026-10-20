#!/usr/bin/env python3
"""Join DA06-owned Skyrim.esm DIAL topics to INFO children and raw callbacks.

This is a bounded source-file join, not a profile-winner or runtime query.
The DIAL quest association is selected from QNAM, and INFO children are joined
by the containing GRUP label that matches the parent DIAL FormID.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mmap
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local" / "xedit-data" / "official-ae-v1" / "Skyrim.esm"
EXPECTED_SHA256 = "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107"
DA06 = 0x0003B681

import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.plugin_reader import read_plugin


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def group_parent_index(path: Path, topic_ids: set[int]) -> tuple[dict[int, list[dict]], int]:
    """Return INFO FormID -> matching ancestor groups, while walking all GRUPs."""
    matches: dict[int, list[dict]] = {}
    record_count = 0

    def walk(data: mmap.mmap, start: int, end: int, ancestry: list[dict]) -> None:
        nonlocal record_count
        pos = start
        while pos < end:
            if end - pos < 24:
                raise ValueError(f"truncated header at 0x{pos:X}")
            signature, size = struct.unpack_from("<4sI", data, pos)
            if signature == b"GRUP":
                if size < 24 or pos + size > end:
                    raise ValueError(f"bad GRUP boundary at 0x{pos:X}")
                label = data[pos + 8:pos + 12]
                group_type = struct.unpack_from("<I", data, pos + 12)[0]
                entry = {
                    "type": group_type,
                    "label_hex": label.hex(),
                    "label_form_id": int.from_bytes(label, "little"),
                }
                walk(data, pos + 24, pos + size, ancestry + [entry])
                pos += size
                continue
            if pos + 24 + size > end:
                raise ValueError(f"record exceeds containing group at 0x{pos:X}")
            record_count += 1
            form_id = struct.unpack_from("<I", data, pos + 12)[0]
            if signature == b"INFO":
                owners = [group for group in ancestry if group["label_form_id"] in topic_ids]
                if owners:
                    matches[form_id] = owners
            pos += 24 + size

    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        walk(data, 0, len(data), [])
    return matches, record_count


def subrecords(row: dict) -> dict[str, list[bytes]]:
    result: dict[str, list[bytes]] = {}
    for item in row.get("subrecords", []):
        result.setdefault(item["signature"], []).append(bytes.fromhex(item["value_hex"]))
    return result


def decode_ctda(raw: bytes) -> dict[str, object]:
    if len(raw) != 32:
        return {"raw_hex": raw.hex(), "length": len(raw), "decoded": False}
    return {
        "raw_hex": raw.hex(),
        "flags_byte": raw[0],
        "operator_byte": raw[1],
        "reserved_hex": raw[2:4].hex(),
        "comparison_float": struct.unpack_from("<f", raw, 4)[0],
        "function_index_u32": struct.unpack_from("<I", raw, 8)[0],
        "param1_u32": struct.unpack_from("<I", raw, 12)[0],
        "param2_u32": struct.unpack_from("<I", raw, 16)[0],
        "run_on_u32": struct.unpack_from("<I", raw, 20)[0],
        "reference_u32": struct.unpack_from("<I", raw, 24)[0],
        "trailing_hex": raw[28:32].hex(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="ignored .local JSON output path")
    args = parser.parse_args()
    if not SOURCE.is_file():
        raise SystemExit("prepared official Skyrim.esm is unavailable")
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    local_root = (ROOT / ".local").resolve()
    output_path = output_path.resolve()
    if not output_path.is_relative_to(local_root):
        raise SystemExit("capture output must remain under ignored .local/")
    source_hash = digest(SOURCE)
    if source_hash != EXPECTED_SHA256:
        raise SystemExit("prepared official Skyrim.esm SHA-256 mismatch")

    dial_rows = list(read_plugin(SOURCE, "DIAL", include_subrecords=True))
    topics: dict[int, dict] = {}
    for row in dial_rows:
        fields = subrecords(row)
        qnam = fields.get("QNAM", [])
        if not any(len(value) == 4 and int.from_bytes(value, "little") == DA06 for value in qnam):
            continue
        form_id = int(row["file_form_id"], 16)
        topics[form_id] = {
            "form_id": row["file_form_id"],
            "editor_id": row["editor_id"],
            "topic_type": fields.get("SNAM", [b""])[0].decode("ascii", "replace"),
            "tif_count": int.from_bytes(fields.get("TIFC", [b"\0\0\0\0"])[0], "little"),
            "record_offset": row["offset"],
        }

    info_parents, walked_count = group_parent_index(SOURCE, set(topics))
    needed_info = set(info_parents)
    infos: dict[int, dict] = {}
    for row in read_plugin(SOURCE, "INFO", include_subrecords=True):
        form_id = int(row["file_form_id"], 16)
        if form_id not in needed_info:
            continue
        fields = subrecords(row)
        vmad = fields.get("VMAD", [])
        tif_names: list[str] = []
        for value in vmad:
            text = value.decode("latin-1")
            tif_names.extend(re.findall(r"TIF_[A-Za-z0-9_]+", text))
        infos[form_id] = {
            "form_id": row["file_form_id"],
            "editor_id": row["editor_id"],
            "record_offset": row["offset"],
            "parent_groups": info_parents[form_id],
            "conditions": [decode_ctda(value) for value in fields.get("CTDA", [])],
            "tif_script_name_candidates": sorted(set(tif_names)),
            "vmad_hex": [value.hex() for value in vmad],
        }

    for topic_id, topic in topics.items():
        topic["infos"] = [infos[info_id] for info_id in sorted(infos) if topic_id in {
            group["label_form_id"] for group in info_parents[info_id]
        }]

    output = {
        "source_plugin": "Skyrim.esm",
        "source_sha256": source_hash,
        "parser": "tools.plugin_reader.read_plugin + full GRUP ancestry walk",
        "source_scope": "prepared official master; not a winning-record/profile query",
        "main_quest": "0003B681 DA06",
        "records_walked": walked_count,
        "dials_read": len(dial_rows),
        "da06_dial_count": len(topics),
        "da06_info_count": len(infos),
        "topics": [topics[key] for key in sorted(topics)],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_sha256": source_hash,
        "records_walked": walked_count,
        "dials_read": len(dial_rows),
        "da06_dial_count": len(topics),
        "da06_info_count": len(infos),
        "infos_with_tif_names": sum(bool(info["tif_script_name_candidates"]) for info in infos.values()),
        "output": output_path.relative_to(ROOT).as_posix(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
