#!/usr/bin/env python3
"""Join DA02-owned Skyrim.esm DIAL topics to INFO children and conditions."""
from __future__ import annotations

import argparse
import hashlib
import json
import mmap
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local" / "xedit-data" / "official-ae-v1" / "Skyrim.esm"
EXPECTED_SHA256 = "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107"
DA02 = 0x0004D8D6
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
    matches: dict[int, list[dict]] = {}
    record_count = 0

    def walk(data: mmap.mmap, start: int, end: int, ancestry: list[dict]) -> None:
        nonlocal record_count
        pos = start
        while pos < end:
            if end - pos < 24:
                raise ValueError(f"truncated group/record header at 0x{pos:X}")
            signature, size = struct.unpack_from("<4sI", data, pos)
            if signature == b"GRUP":
                if size < 24 or pos + size > end:
                    raise ValueError(f"invalid GRUP boundary at 0x{pos:X}")
                label = data[pos + 8:pos + 12]
                entry = {"type": struct.unpack_from("<I", data, pos + 12)[0],
                         "label_hex": label.hex(), "label_form_id": int.from_bytes(label, "little")}
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


def decode_ctda(raw: bytes) -> dict:
    if len(raw) != 32:
        return {"raw_hex": raw.hex(), "length": len(raw), "decoded": False}
    type_byte = raw[0]
    operand = raw[4:8]
    use_global = bool(type_byte & 0x04)
    return {
        "raw_hex": raw.hex(),
        "type_byte": f"0x{type_byte:02X}",
        "operator": {0x00: "=", 0x20: "!=", 0x40: ">", 0x60: ">=", 0x80: "<", 0xA0: "<="}.get(type_byte & 0xF0, "unknown"),
        "or_flag": bool(type_byte & 1),
        "use_global": use_global,
        "comparison_float": struct.unpack_from("<f", raw, 4)[0] if not use_global else None,
        "operand_global_form_id": f"{struct.unpack_from('<I', operand)[0]:08X}" if use_global else None,
        "function_index": struct.unpack_from("<H", raw, 8)[0],
        "param1_u32": struct.unpack_from("<I", raw, 12)[0],
        "param2_u32": struct.unpack_from("<I", raw, 16)[0],
        "run_on": struct.unpack_from("<I", raw, 20)[0],
        "reference_form_id": f"{struct.unpack_from('<I', raw, 24)[0]:08X}",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not SOURCE.is_file():
        raise SystemExit("prepared official Skyrim.esm is unavailable")
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    if not output_path.resolve().is_relative_to((ROOT / ".local").resolve()):
        raise SystemExit("capture output must remain under ignored .local/")
    source_hash = digest(SOURCE)
    if source_hash != EXPECTED_SHA256:
        raise SystemExit("prepared official Skyrim.esm SHA-256 mismatch")

    dial_rows = list(read_plugin(SOURCE, "DIAL", include_subrecords=True))
    topics: dict[int, dict] = {}
    for row in dial_rows:
        content = subrecords(row)
        if not any(len(value) == 4 and int.from_bytes(value, "little") == DA02 for value in content.get("QNAM", [])):
            continue
        form_id = int(row["file_form_id"], 16)
        topics[form_id] = {
            "form_id": row["file_form_id"],
            "editor_id": row["editor_id"],
            "topic_type": content.get("SNAM", [b""])[0].decode("ascii", "replace"),
            "tif_count": int.from_bytes(content.get("TIFC", [b"\0" * 4])[0], "little"),
            "record_offset": row["offset"],
        }

    info_parent, walked_count = group_parent_index(SOURCE, set(topics))
    info_ids = set(info_parent)
    infos: dict[int, dict] = {}
    for row in read_plugin(SOURCE, "INFO", include_subrecords=True):
        form_id = int(row["file_form_id"], 16)
        if form_id not in info_ids:
            continue
        content = subrecords(row)
        vmad = content.get("VMAD", [])
        tif_names: list[str] = []
        for value in vmad:
            tif_names.extend(re.findall(r"TIF_[A-Za-z0-9_]+", value.decode("latin-1")))
        infos[form_id] = {
            "form_id": row["file_form_id"],
            "editor_id": row["editor_id"],
            "record_offset": row["offset"],
            "parent_groups": info_parent[form_id],
            "conditions": [decode_ctda(value) for value in content.get("CTDA", [])],
            "tif_script_name_candidates": sorted(set(tif_names)),
            "vmad_hex": [value.hex() for value in vmad],
        }

    for topic_id, topic in topics.items():
        topic["infos"] = [infos[info_id] for info_id in sorted(infos)
                           if topic_id in {group["label_form_id"] for group in info_parent[info_id]}]

    output = {
        "source_plugin": "Skyrim.esm",
        "source_sha256": source_hash,
        "parser": "tools.plugin_reader.read_plugin plus full GRUP ancestry walk",
        "source_scope": "prepared official master; not a winning-record/profile query",
        "main_quest": "0004D8D6 DA02 (Update.esm source override)",
        "records_walked": walked_count,
        "dials_read": len(dial_rows),
        "da02_dial_count": len(topics),
        "da02_info_count": len(infos),
        "topics": [topics[key] for key in sorted(topics)],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    tif_names = sorted({name for info in infos.values() for name in info["tif_script_name_candidates"]})
    print(json.dumps({
        "source_sha256": source_hash,
        "records_walked": walked_count,
        "dials_read": len(dial_rows),
        "da02_dial_count": len(topics),
        "da02_info_count": len(infos),
        "infos_with_tif_names": sum(bool(info["tif_script_name_candidates"]) for info in infos.values()),
        "tif_script_names": tif_names,
        "output": output_path.relative_to(ROOT).as_posix(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
