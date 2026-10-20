#!/usr/bin/env python3
"""Locate the exact placed MS06 REFR candidates in their Skyrim.esm CELL groups."""
from __future__ import annotations

import argparse
import hashlib
import json
import mmap
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.plugin_reader import read_plugin

SOURCE = ROOT / ".local" / "xedit-data" / "official-ae-v1" / "Skyrim.esm"
EXPECTED = "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107"
REFS = {0x00108A62, 0x00099D27, 0x00099D25, 0x00099D24, 0x00097E23}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def walk(path: Path) -> tuple[dict[int, list[dict]], int]:
    matches: dict[int, list[dict]] = {}
    count = 0

    def visit(data: mmap.mmap, start: int, end: int, ancestry: list[dict]) -> None:
        nonlocal count
        pos = start
        while pos < end:
            if end - pos < 24:
                raise ValueError(f"truncated entry at 0x{pos:X}")
            sig, size = struct.unpack_from("<4sI", data, pos)
            if sig == b"GRUP":
                if size < 24 or pos + size > end:
                    raise ValueError(f"invalid GRUP boundary at 0x{pos:X}")
                label = int.from_bytes(data[pos + 8:pos + 12], "little")
                kind = struct.unpack_from("<I", data, pos + 12)[0]
                entry = {"type": kind, "label_form_id": f"{label:08X}"}
                visit(data, pos + 24, pos + size, ancestry + [entry])
                pos += size
                continue
            if pos + 24 + size > end:
                raise ValueError(f"record exceeds group at 0x{pos:X}")
            count += 1
            if sig == b"REFR":
                form = struct.unpack_from("<I", data, pos + 12)[0]
                if form in REFS:
                    matches[form] = ancestry
            pos += 24 + size

    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        visit(data, 0, len(data), [])
    return matches, count


def subrecords(row: dict) -> dict[str, list[bytes]]:
    result: dict[str, list[bytes]] = {}
    for item in row.get("subrecords", []):
        result.setdefault(item["signature"], []).append(bytes.fromhex(item["value_hex"]))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    local = (ROOT / ".local").resolve()
    output = output.resolve()
    if output != local and local not in output.parents:
        raise SystemExit("output must remain below ignored .local/")
    source_hash = digest(SOURCE)
    if source_hash != EXPECTED:
        raise SystemExit("prepared Skyrim.esm identity differs from the fixed source hash")
    ancestry, record_count = walk(SOURCE)
    refs = []
    cell_ids: set[int] = set()
    for row in read_plugin(SOURCE, "REFR", include_subrecords=True):
        form = int(row["file_form_id"], 16)
        if form not in REFS:
            continue
        parents = ancestry.get(form, [])
        for g in parents:
            if g["type"] == 6:
                cell_ids.add(int(g["label_form_id"], 16))
        values = subrecords(row)
        refs.append({
            "form_id": row["file_form_id"],
            "editor_id": row["editor_id"],
            "record_flags": row["flags"],
            "base_form_ids": [f"{int.from_bytes(v, 'little'):08X}" for v in values.get("NAME", []) if len(v) == 4],
            "parent_groups": parents,
            "subrecords": {k: [v.hex() for v in val] for k, val in values.items()},
        })
    cells = []
    if cell_ids:
        for row in read_plugin(SOURCE, "CELL", include_subrecords=True):
            if int(row["file_form_id"], 16) not in cell_ids:
                continue
            cells.append({"form_id": row["file_form_id"], "editor_id": row["editor_id"],
                          "record_flags": row["flags"],
                          "subrecords": {x["signature"]: x["value_hex"] for x in row.get("subrecords", [])}})
    result = {
        "source_plugin": SOURCE.name,
        "source_sha256": source_hash,
        "record_count_walked": record_count,
        "reference_count": len(refs),
        "references": refs,
        "cell_ids_from_type6_groups": [f"{x:08X}" for x in sorted(cell_ids)],
        "cells": cells,
        "scope": "Hash-verified prepared Skyrim.esm direct parser and GRUP ancestry only; no active-profile or runtime claim",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output.relative_to(ROOT)), "sha256": digest(output),
                      "source_sha256": source_hash, "record_count": record_count,
                      "reference_count": len(refs), "cell_ids": result["cell_ids_from_type6_groups"],
                      "cell_records": len(cells)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
