#!/usr/bin/env python3
"""Hash-check Skyrim.esm and find direct raw references to WE13."""
from __future__ import annotations

import argparse
import hashlib
import json
import mmap
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/xedit-data/official-ae-v1/Skyrim.esm"
EXPECTED_SHA256 = "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107"
WE13 = 0x0009F32F
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.plugin_reader import read_plugin


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def ancestry_for(path: Path, target: int) -> tuple[list[dict[str, object]], int]:
    found: list[dict[str, object]] = []
    count = 0

    def walk(data: mmap.mmap, start: int, end: int, parents: list[dict[str, object]]) -> None:
        nonlocal count
        pos = start
        while pos < end:
            if end - pos < 24:
                raise ValueError(f"truncated header at 0x{pos:X}")
            sig, size = struct.unpack_from("<4sI", data, pos)
            if sig == b"GRUP":
                if size < 24 or pos + size > end:
                    raise ValueError(f"bad GRUP boundary at 0x{pos:X}")
                label = data[pos + 8 : pos + 12]
                desc = {"type": struct.unpack_from("<I", data, pos + 12)[0], "label_hex": label.hex(), "label_form_id": int.from_bytes(label, "little")}
                walk(data, pos + 24, pos + size, [*parents, desc])
                pos += size
                continue
            if pos + 24 + size > end:
                raise ValueError(f"record exceeds group at 0x{pos:X}")
            count += 1
            form_id = struct.unpack_from("<I", data, pos + 12)[0]
            if form_id == target:
                found.extend(parents)
            pos += 24 + size

    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        walk(data, 0, len(data), [])
    return found, count


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    source_sha = digest(SOURCE)
    if source_sha != EXPECTED_SHA256:
        raise SystemExit("prepared Skyrim.esm SHA-256 mismatch")
    target_bytes = WE13.to_bytes(4, "little")
    hits = []
    target_record = None
    smqn_count = 0
    record_count = 0
    for row in read_plugin(SOURCE, include_subrecords=True):
        record_count += 1
        if row["signature"] == "SMQN":
            smqn_count += 1
        fid = int(row["file_form_id"], 16)
        if row["signature"] == "QUST" and fid == WE13:
            target_record = row
        occurrences = []
        for subrecord in row.get("subrecords", []):
            value = bytes.fromhex(subrecord["value_hex"])
            offset = value.find(target_bytes)
            if offset >= 0:
                occurrences.append({"subrecord": subrecord["signature"], "offset_in_value": offset, "raw_window_hex": value[max(0, offset - 4) : offset + 8].hex()})
        if occurrences and not (row["signature"] == "QUST" and fid == WE13):
            hits.append({"signature": row["signature"], "form_id": row["file_form_id"], "editor_id": row["editor_id"], "record_offset": row["offset"], "occurrences": occurrences})
    if target_record is None:
        raise RuntimeError("QUST 0009F32F WE13 not found")
    ancestry, group_records = ancestry_for(SOURCE, WE13)
    output = {
        "source_plugin": "Skyrim.esm", "source_sha256": source_sha,
        "parser": "tools.plugin_reader.read_plugin plus independent GRUP ancestry scan and raw FormID-byte match",
        "scope": "prepared Skyrim.esm only; not a profile winner query",
        "records_walked": record_count, "group_records_walked": group_records, "smqn_count": smqn_count,
        "target": {"signature": "QUST", "form_id": target_record["file_form_id"], "editor_id": target_record["editor_id"], "offset": target_record["offset"], "group_ancestry": ancestry, "subrecords": target_record.get("subrecords", [])},
        "raw_direct_reference_hit_count": len(hits), "raw_direct_reference_hits": hits,
        "smqn_raw_reference_hits": [row for row in hits if row["signature"] == "SMQN"],
        "warning": "Raw byte matches are candidate references; interpret their subrecord schemas before treating them as semantic links."
    }
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    if not output_path.resolve().is_relative_to((ROOT / ".local").resolve()):
        raise SystemExit("output must stay under ignored .local/")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"source_sha256": source_sha, "records_walked": record_count, "smqn_count": smqn_count, "raw_direct_reference_hit_count": len(hits), "smqn_raw_reference_hit_count": len(output["smqn_raw_reference_hits"]), "group_records_walked": group_records, "output": output_path.relative_to(ROOT).as_posix()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
