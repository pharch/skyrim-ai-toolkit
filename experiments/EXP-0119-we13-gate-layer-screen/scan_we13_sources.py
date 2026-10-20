#!/usr/bin/env python3
"""Scan the fixed five-master source layer for WE13 refs and encounter-script owners."""
from __future__ import annotations

import hashlib
import json
import mmap
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / ".local/xedit-data/official-ae-v1"
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261018-0004/we13-source-scan.json"
EXPECTED = {
    "Dawnguard.esm": "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4",
    "Dragonborn.esm": "5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b",
    "HearthFires.esm": "ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97",
    "Skyrim.esm": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
    "Update.esm": "c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9",
}
WE13 = 0x0009F32F
SCRIPT_NAMES = (b"WETriggerScript", b"WEScript", b"WEParentScript", b"WEAliasScript")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.plugin_reader import read_plugin


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def group_map(path: Path) -> dict[str, list[dict[str, object]]]:
    groups: dict[str, list[dict[str, object]]] = {}
    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        def walk(start: int, end: int, parents: list[dict[str, object]]) -> None:
            pos = start
            while pos < end:
                if end - pos < 24:
                    raise ValueError(f"truncated header in {path.name} at 0x{pos:X}")
                sig, size = struct.unpack_from("<4sI", data, pos)
                if sig == b"GRUP":
                    if size < 24 or pos + size > end:
                        raise ValueError(f"bad group boundary in {path.name} at 0x{pos:X}")
                    label = bytes(data[pos + 8:pos + 12])
                    kind = struct.unpack_from("<I", data, pos + 12)[0]
                    entry = {"type": kind, "label_hex": label.hex()}
                    if kind == 0:
                        entry["label_signature"] = label.decode("ascii", "replace")
                    else:
                        entry["label_u32"] = int.from_bytes(label, "little")
                    walk(pos + 24, pos + size, [*parents, entry])
                    pos += size
                else:
                    if pos + 24 + size > end:
                        raise ValueError(f"record exceeds group in {path.name} at 0x{pos:X}")
                    groups[f"0x{pos:X}"] = parents
                    pos += 24 + size
        walk(0, len(data), [])
    return groups


def masters_for(path: Path) -> list[str]:
    for row in read_plugin(path, "TES4", include_subrecords=True):
        return [sub["text_cp1252"] for sub in row["subrecords"] if sub["signature"] == "MAST"]
    raise ValueError(f"TES4 header missing in {path.name}")


def logical_fid(raw: bytes, masters: list[str], plugin_name: str) -> tuple[str, str] | None:
    if len(raw) != 4:
        return None
    value = int.from_bytes(raw, "little")
    origin_index = value >> 24
    if origin_index < len(masters):
        origin = masters[origin_index]
    elif origin_index == len(masters):
        origin = plugin_name
    else:
        return None
    return origin.casefold(), f"{value & 0x00FFFFFF:06X}"


def main() -> int:
    source_rows = []
    all_records: list[dict[str, object]] = []
    we13_hits: list[dict[str, object]] = []
    script_owners: list[dict[str, object]] = []
    ref_rows: list[dict[str, object]] = []
    count_by_plugin: dict[str, int] = {}
    target_bytes = WE13.to_bytes(4, "little")

    for plugin_name, expected_sha in EXPECTED.items():
        path = SOURCE_DIR / plugin_name
        actual_sha = sha256(path)
        if actual_sha != expected_sha:
            raise SystemExit(f"{plugin_name} SHA-256 mismatch: {actual_sha}")
        ancestry = group_map(path)
        masters = masters_for(path)
        count = 0
        for row in read_plugin(path, include_subrecords=True):
            count += 1
            offset = row["offset"]
            parents = ancestry[offset]
            compact = {
                "plugin": plugin_name,
                "signature": row["signature"],
                "form_id": row["file_form_id"],
                "origin_plugin": row["origin_plugin"],
                "editor_id": row["editor_id"],
                "offset": offset,
                "group_ancestry": parents,
            }
            has_we_trigger = []
            for sub in row["subrecords"]:
                value = bytes.fromhex(sub["value_hex"])
                if value.startswith(target_bytes) or target_bytes in value:
                    at = value.find(target_bytes)
                    we13_hits.append({
                        **compact,
                        "subrecord": sub["signature"],
                        "offset_in_subrecord": at,
                        "raw_window_hex": value[max(0, at - 8):at + 12].hex(),
                    })
                if sub["signature"] == "VMAD":
                    for name in SCRIPT_NAMES:
                        at = value.lower().find(name.lower())
                        if at >= 0:
                            has_we_trigger.append({
                                "script_name": name.decode("ascii"),
                                "offset_in_vmad": at,
                            })
                if row["signature"] in {"REFR", "ACHR", "ACRE", "PGRE", "PMIS"} and sub["signature"] == "NAME":
                    target = logical_fid(value, masters, plugin_name)
                    if target:
                        ref_rows.append({
                            **compact,
                            "base_key": list(target),
                            "subrecord": "NAME",
                            "value_hex": value.hex(),
                        })
            if has_we_trigger:
                script_owners.append({**compact, "vmad_script_matches": has_we_trigger})
            all_records.append({"compact": compact, "masters": masters})
        count_by_plugin[plugin_name] = count
        source_rows.append({"plugin": plugin_name, "sha256": actual_sha, "records_walked": count})

    owner_keys = {
        (str(row["origin_plugin"]).casefold(), str(row["form_id"])[2:].upper())
        for row in script_owners
    }
    placed_refs = [
        row for row in ref_rows
        if tuple(row["base_key"]) in owner_keys
    ]
    output = {
        "scope": "fixed official five-master files under .local/xedit-data/official-ae-v1; not a profile winner or runtime query",
        "parser": "tools.plugin_reader.read_plugin subrecord parser; independent mmap GRUP-ancestry walk; exact FormID byte scan and VMAD script-name screen",
        "target": {"signature": "QUST", "form_id": "0009F32F", "editor_id": "WE13"},
        "sources": source_rows,
        "record_count": sum(count_by_plugin.values()),
        "we13_raw_reference_candidate_count": len(we13_hits),
        "we13_raw_reference_candidates": we13_hits,
        "vmad_script_owner_count": len(script_owners),
        "vmad_script_owners": script_owners,
        "placed_reference_to_script_owner_count": len(placed_refs),
        "placed_references_to_script_owners": placed_refs,
        "warning": "FormID-byte and VMAD string matches are source candidates; validate field semantics from record schemas/native exports before treating them as causal paths.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "sources": source_rows,
        "record_count": output["record_count"],
        "we13_raw_reference_candidate_count": len(we13_hits),
        "vmad_script_owner_count": len(script_owners),
        "placed_reference_to_script_owner_count": len(placed_refs),
        "output": OUTPUT.relative_to(ROOT).as_posix(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
