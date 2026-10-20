#!/usr/bin/env python3
"""Join five-master DIAL owners and INFO children for MS06/MS06Start."""
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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.plugin_reader import read_plugin

DATA = ROOT / ".local" / "xedit-data" / "official-ae-v1"
PLUGINS = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]
EXPECTED = {
    "Skyrim.esm": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
    "Update.esm": "c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9",
    "Dawnguard.esm": "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4",
    "HearthFires.esm": "ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97",
    "Dragonborn.esm": "5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b",
}
TARGETS = {0x00026C4D: "MS06", 0x00093807: "MS06Start"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def subrecords(row: dict) -> dict[str, list[bytes]]:
    out: dict[str, list[bytes]] = {}
    for item in row.get("subrecords", []):
        out.setdefault(item["signature"], []).append(bytes.fromhex(item["value_hex"]))
    return out


def group_info_rows(path: Path, info_ids: set[int] | None = None,
                    target_topics: set[int] | None = None) -> tuple[dict[int, list[dict]], int]:
    """Walk GRUP ancestry and collect INFO parent paths, with boundary checks."""
    found: dict[int, list[dict]] = {}
    records = 0

    def walk(data: mmap.mmap, start: int, end: int, ancestry: list[dict]) -> None:
        nonlocal records
        pos = start
        while pos < end:
            if end - pos < 24:
                raise ValueError(f"truncated group entry at 0x{pos:X}")
            sig, size = struct.unpack_from("<4sI", data, pos)
            if sig == b"GRUP":
                if size < 24 or pos + size > end:
                    raise ValueError(f"invalid GRUP boundary at 0x{pos:X}")
                label = int.from_bytes(data[pos + 8:pos + 12], "little")
                kind = struct.unpack_from("<I", data, pos + 12)[0]
                entry = {"type": kind, "label_form_id": f"{label:08X}"}
                walk(data, pos + 24, pos + size, ancestry + [entry])
                pos += size
                continue
            if pos + 24 + size > end:
                raise ValueError(f"record exceeds parent group at 0x{pos:X}")
            records += 1
            if sig == b"INFO":
                form = struct.unpack_from("<I", data, pos + 12)[0]
                is_target_child = target_topics is not None and any(
                    int(g["label_form_id"], 16) in target_topics
                    for g in ancestry if g["type"] == 7
                )
                selected_copy = info_ids is not None and form in info_ids
                if is_target_child or selected_copy:
                    found[form] = ancestry
            pos += 24 + size

    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        walk(data, 0, len(data), [])
    return found, records


def decode_ctda(raw: bytes) -> dict:
    if len(raw) != 32:
        return {"raw_hex": raw.hex(), "length": len(raw), "decoded": False}
    return {
        "raw_hex": raw.hex(),
        "flags_byte": raw[0],
        "operator_byte": raw[1],
        "comparison_float": struct.unpack_from("<f", raw, 4)[0],
        "function_index_u16": struct.unpack_from("<H", raw, 8)[0],
        "param1_u32": struct.unpack_from("<I", raw, 12)[0],
        "param2_u32": struct.unpack_from("<I", raw, 16)[0],
        "run_on_u32": struct.unpack_from("<I", raw, 20)[0],
        "reference_u32": struct.unpack_from("<I", raw, 24)[0],
    }


def compact_row(row: dict, ancestry: list[dict] | None = None) -> dict:
    values = subrecords(row)
    return {
        "signature": row["signature"],
        "source_plugin": row["plugin"],
        "origin_plugin": row["origin_plugin"],
        "form_id": row["file_form_id"],
        "editor_id": row["editor_id"],
        "offset": row["offset"],
        "ancestry": ancestry,
        "qnam": [f"{int.from_bytes(v, 'little'):08X}" for v in values.get("QNAM", []) if len(v) == 4],
        "conditions": [decode_ctda(v) for v in values.get("CTDA", [])],
        "tif_names": sorted({m.decode("ascii") for v in values.get("VMAD", [])
                              for m in re.findall(rb"TIF_[A-Za-z0-9_]+", v)}),
        "subrecords": {sig: [v.hex() for v in vals] for sig, vals in values.items()
                       if sig in {"QNAM", "SNAM", "TIFC", "CTDA", "VMAD", "PNAM", "DATA", "NAM1"}},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="output JSON path under ignored .local/")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    local = (ROOT / ".local").resolve()
    output = output.resolve()
    if output != local and local not in output.parents:
        raise SystemExit("output must remain below ignored .local/")

    files = {name: DATA / name for name in PLUGINS}
    hashes = {name: digest(path) for name, path in files.items() if path.is_file()}
    if set(hashes) != set(PLUGINS) or hashes != EXPECTED:
        raise SystemExit("prepared official-master identities differ from the fixed allowlist")

    topic_ids: set[int] = set()
    topic_copies: dict[str, list[dict]] = {f"{v:08X}": [] for v in TARGETS}
    for plugin in PLUGINS:
        for row in read_plugin(files[plugin], "DIAL", include_subrecords=True):
            vals = subrecords(row)
            qnam = [int.from_bytes(v, "little") for v in vals.get("QNAM", []) if len(v) == 4]
            if not any(q in TARGETS for q in qnam):
                continue
            topic = int(row["file_form_id"], 16)
            topic_ids.add(topic)
            for q in qnam:
                if q in TARGETS:
                    topic_copies[f"{q:08X}"].append(compact_row(row))

    info_ids: set[int] = set()
    record_counts: dict[str, int] = {}
    for plugin in PLUGINS:
        children, count = group_info_rows(files[plugin], target_topics=topic_ids)
        record_counts[plugin] = count
        info_ids.update(children)

    info_copies: dict[str, list[dict]] = {}
    for plugin in PLUGINS:
        parents, count = group_info_rows(files[plugin], info_ids=info_ids)
        record_counts[plugin] = max(record_counts[plugin], count)
        for row in read_plugin(files[plugin], "INFO", include_subrecords=True):
            form = int(row["file_form_id"], 16)
            if form in info_ids:
                compact = compact_row(row, parents.get(form, []))
                info_copies.setdefault(f"{form:08X}", []).append(compact)

    order = {name: i for i, name in enumerate(PLUGINS)}
    for copies in topic_copies.values():
        copies.sort(key=lambda r: order[r["source_plugin"]])
    for copies in info_copies.values():
        copies.sort(key=lambda r: order[r["source_plugin"]])

    result = {
        "scope": "Five prepared official masters only; direct TES4 parser; no profile winner or runtime claim",
        "plugins": [{"name": p, "sha256": hashes[p], "record_count": record_counts[p]} for p in PLUGINS],
        "target_quests": {f"{fid:08X}": editor for fid, editor in TARGETS.items()},
        "dial_owner_copy_counts": {key: len(value) for key, value in topic_copies.items()},
        "dial_owner_copies": topic_copies,
        "target_dial_ids": [f"{x:08X}" for x in sorted(topic_ids)],
        "info_ids_under_target_dials": [f"{x:08X}" for x in sorted(info_ids)],
        "info_source_copy_count": sum(map(len, info_copies.values())),
        "info_copies": info_copies,
        "coverage_limit": "The QNAM/GRUP join identifies source-defined dialogue ownership and INFO children. It does not prove availability, PEX execution, quest startup, alias fill, or gameplay. Schema and source load order are bounded to the five listed masters.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output.relative_to(ROOT)), "sha256": digest(output),
                      "target_dial_ids": len(topic_ids), "info_ids": len(info_ids),
                      "info_source_copies": result["info_source_copy_count"],
                      "plugin_hashes": hashes}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
