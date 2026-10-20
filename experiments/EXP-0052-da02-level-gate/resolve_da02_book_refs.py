#!/usr/bin/env python3
"""Resolve the official-master CELL ancestry for placed DA02 book references."""
from __future__ import annotations

import hashlib
import json
import mmap
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / ".local" / "xedit-data" / "official-ae-v1"
SOURCES = {
    "Skyrim.esm": ("2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107", DATA / "Skyrim.esm"),
    "Dawnguard.esm": ("1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4", DATA / "Dawnguard.esm"),
}
TARGETS = {0x000B0E81, 0x000B0E83, 0x000B0E85, 0x000B0E86, 0x000C2D3C}
CELL_CHILD_GROUP_TYPES = {6, 8, 9, 10}
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.plugin_reader import read_plugin


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def ancestry_index(path: Path) -> tuple[dict[int, list[dict]], int]:
    found: dict[int, list[dict]] = {}
    walked = 0

    def walk(data: mmap.mmap, start: int, end: int, ancestry: list[dict]) -> None:
        nonlocal walked
        pos = start
        while pos < end:
            if end - pos < 24:
                raise ValueError(f"truncated group/record header at 0x{pos:X}")
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
                raise ValueError(f"record exceeds group at 0x{pos:X}")
            walked += 1
            form_id = struct.unpack_from("<I", data, pos + 12)[0]
            if signature == b"REFR" and form_id in TARGETS:
                found[form_id] = ancestry
            pos += 24 + size

    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        walk(data, 0, len(data), [])
    return found, walked


def subrecords(row: dict) -> dict[str, list[bytes]]:
    result: dict[str, list[bytes]] = {}
    for item in row.get("subrecords", []):
        result.setdefault(item["signature"], []).append(bytes.fromhex(item["value_hex"]))
    return result


def main() -> int:
    output = []
    source_hashes = {}
    records_walked = {}
    for plugin, (expected_hash, source) in SOURCES.items():
        if not source.is_file():
            raise SystemExit(f"prepared {plugin} is unavailable")
        source_hash = digest(source)
        if source_hash != expected_hash:
            raise SystemExit(f"prepared {plugin} SHA-256 mismatch")
        source_hashes[plugin] = source_hash
        group_paths, walked = ancestry_index(source)
        records_walked[plugin] = walked
        selected = {}
        cells = {}
        for row in read_plugin(source, include_subrecords=True):
            form_id = int(row["file_form_id"], 16)
            if row["signature"] == "REFR" and form_id in TARGETS:
                selected[form_id] = row
            elif row["signature"] == "CELL":
                cells[form_id] = row
        for form_id, row in sorted(selected.items()):
            values = subrecords(row)
            groups = group_paths.get(form_id, [])
            cell_candidates = [group["label_form_id"] for group in groups
                               if group["type"] in CELL_CHILD_GROUP_TYPES]
            cell_records = []
            for cell_id in cell_candidates:
                cell = cells.get(cell_id)
                if not cell:
                    continue
                cell_values = subrecords(cell)
                cell_records.append({
                    "form_id": cell["file_form_id"],
                    "editor_id": cell["editor_id"],
                    "full_name_bytes_hex": [value.hex() for value in cell_values.get("FULL", [])],
                    "flags": cell.get("flags"),
                })
            data = values.get("DATA", [b""])[0]
            position = list(struct.unpack_from("<3f", data, 0)) if len(data) >= 12 else None
            rotation = list(struct.unpack_from("<3f", data, 12)) if len(data) >= 24 else None
            base_form_id = int.from_bytes(values.get("NAME", [bytes(4)])[0], "little")
            output.append({
                "source_plugin": plugin,
                "form_id": f"{form_id:08X}",
                "base_form_id": f"{base_form_id:08X}",
                "record_offset": row["offset"],
                "record_flags": row["flags"],
                "group_ancestry": groups,
                "cell_group_candidate_ids": [f"{value:08X}" for value in cell_candidates],
                "resolved_cell_candidates": cell_records,
                "position": position,
                "rotation": rotation,
                "subrecord_signatures": [item["signature"] for item in row.get("subrecords", [])],
            })
    print(json.dumps({
        "source_plugins": list(SOURCES),
        "source_sha256": source_hashes,
        "source_scope": "prepared official masters; not a winning-record/profile query",
        "records_walked": records_walked,
        "record_count": len(output),
        "references": output,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
