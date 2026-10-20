#!/usr/bin/env python3
"""Extract raw placement, enable-parent, and VMAD property data for WE triggers."""
from __future__ import annotations

import hashlib
import json
import mmap
from collections import Counter
from pathlib import Path
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / ".local/xedit-data/official-ae-v1"
SCAN = ROOT / ".local/alignment/transactions/TX-20261018-0004/we13-source-scan.json"
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261018-0004/we-trigger-placements.json"
ORDER = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]
EXPECTED = {
    "Dawnguard.esm": "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4",
    "Dragonborn.esm": "5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b",
    "HearthFires.esm": "ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97",
    "Skyrim.esm": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
    "Update.esm": "c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9",
}

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.plugin_reader import _records, _subrecords


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode(raw: bytes) -> str:
    return raw.rstrip(b"\0").decode("cp1252", "replace")


def read_masters(path: Path) -> list[str]:
    with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        sig, flags, fid, offset, payload = next(_records(data))
        if sig != "TES4":
            raise ValueError(f"TES4 is not first in {path.name}")
        return [decode(value) for name, value in _subrecords(payload, flags) if name == "MAST"]


def logical_form(value: int, masters: list[str], plugin: str) -> dict[str, str] | None:
    if value == 0:
        return None
    index = value >> 24
    if index < len(masters):
        origin = masters[index]
    elif index == len(masters):
        origin = plugin
    else:
        return {"origin": "UNRESOLVED", "local_id": f"{value & 0x00FFFFFF:06X}", "raw": f"{value:08X}"}
    return {"origin": origin, "local_id": f"{value & 0x00FFFFFF:06X}", "raw": f"{value:08X}"}


def read_vmad(raw: bytes, masters: list[str], plugin: str) -> dict[str, object]:
    pos = 0
    object_format = 2
    def u16() -> int:
        nonlocal pos
        value = struct.unpack_from("<H", raw, pos)[0]
        pos += 2
        return value
    def u32() -> int:
        nonlocal pos
        value = struct.unpack_from("<I", raw, pos)[0]
        pos += 4
        return value
    def string() -> str:
        nonlocal pos
        size = u16()
        if pos + size > len(raw):
            raise ValueError("VMAD string exceeds subrecord")
        value = decode(raw[pos:pos + size])
        pos += size
        return value
    def array(read_one):
        count = u32()
        if count > 4096:
            raise ValueError(f"unexpected VMAD array length {count}")
        return [read_one() for _ in range(count)]
    def object_value() -> dict[str, object]:
        nonlocal pos
        if object_format == 1:
            value = u32()
            alias = struct.unpack_from("<h", raw, pos)[0]
            pos += 2
            unused = raw[pos:pos + 2].hex()
            pos += 2
        elif object_format == 2:
            unused = raw[pos:pos + 2].hex()
            pos += 2
            alias = struct.unpack_from("<h", raw, pos)[0]
            pos += 2
            value = u32()
        else:
            raise ValueError(f"unsupported VMAD object format {object_format}")
        result = {"raw": f"{value:08X}", "logical": logical_form(value, masters, plugin), "alias": alias, "unused_hex": unused}
        return result
    def value_for(kind: int) -> object:
        nonlocal pos
        if kind == 1:
            return object_value()
        if kind == 2:
            return string()
        if kind == 3:
            value = struct.unpack_from("<i", raw, pos)[0]; pos += 4; return value
        if kind == 4:
            value = struct.unpack_from("<f", raw, pos)[0]; pos += 4; return value
        if kind == 5:
            value = raw[pos]; pos += 1; return bool(value)
        if kind == 11:
            return array(object_value)
        if kind == 12:
            return array(string)
        if kind == 13:
            def one():
                nonlocal pos
                value = struct.unpack_from("<i", raw, pos)[0]; pos += 4; return value
            return array(one)
        if kind == 14:
            def one():
                nonlocal pos
                value = struct.unpack_from("<f", raw, pos)[0]; pos += 4; return value
            return array(one)
        if kind == 15:
            def one():
                nonlocal pos
                value = raw[pos]; pos += 1; return bool(value)
            return array(one)
        raise ValueError(f"unsupported VMAD property type {kind} at {pos}")
    try:
        version, object_format, script_count = u16(), u16(), u16()
        scripts = []
        for _ in range(script_count):
            script_name = string()
            script_flags = raw[pos]
            pos += 1
            property_count = u16()
            properties = []
            for _ in range(property_count):
                name = string()
                kind, status = raw[pos], raw[pos + 1]
                pos += 2
                properties.append({"name": name, "type": kind, "status": status, "value": value_for(kind)})
            scripts.append({"script_name": script_name, "script_flags": script_flags, "properties": properties})
        return {"version": version, "object_format": object_format, "scripts": scripts, "bytes_consumed": pos, "byte_count": len(raw), "parser_error": None}
    except (IndexError, struct.error, ValueError) as exc:
        return {"byte_count": len(raw), "parser_error": str(exc), "raw_prefix_hex": raw[:160].hex(), "ascii_tokens": [token.decode("ascii", "replace") for token in __import__("re").findall(rb"[A-Za-z][A-Za-z0-9_]{3,}", raw)]}


def main() -> int:
    scan = json.loads(SCAN.read_text(encoding="utf-8"))
    owners = [
        row for row in scan["vmad_script_owners"]
        if row["signature"] == "REFR" and any(m["script_name"] == "WETriggerScript" for m in row["vmad_script_matches"])
    ]
    wanted_offsets = {name: {row["offset"] for row in owners if row["plugin"] == name} for name in ORDER}
    source_meta = {}
    form_index: dict[tuple[str, str], dict[str, object]] = {}
    base_keys = {("skyrim.esm", "04A5EE"), ("skyrim.esm", "09C152"), ("dragonborn.esm", "01AA28"), ("dragonborn.esm", "01AA29")}
    base_candidates: dict[tuple[str, str], list[dict[str, object]]] = {}
    for name in ORDER:
        path = SOURCE_DIR / name
        digest = sha256(path)
        if digest != EXPECTED[name]:
            raise SystemExit(f"{name} SHA-256 mismatch")
        masters = read_masters(path)
        source_meta[name] = {"sha256": digest, "masters": masters}
        with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            for sig, flags, fid, offset, payload in _records(data):
                if sig not in {"ACTI", "CELL", "WRLD", "KYWD", "LCTN"}:
                    continue
                fields = list(_subrecords(payload, flags))
                edid = next((decode(value) for sub, value in fields if sub == "EDID"), "")
                full = next((decode(value) for sub, value in fields if sub == "FULL"), "")
                origin = logical_form(fid, masters, name)
                if origin is None or origin["origin"] == "UNRESOLVED":
                    continue
                logical_key = (str(origin["origin"]).casefold(), str(origin["local_id"]))
                form_index[logical_key] = {
                    "signature": sig, "plugin_record": name, "form_id": f"{fid:08X}", "editor_id": edid, "full_name": full,
                }
                if sig == "ACTI" and logical_key in base_keys:
                    vmad = next((value for sub, value in fields if sub == "VMAD"), b"")
                    base_candidates.setdefault(logical_key, []).append({
                        "signature": sig, "source_plugin": name, "form_id": f"{fid:08X}",
                        "origin_plugin": origin["origin"], "editor_id": edid,
                        "vmad": read_vmad(vmad, masters, name) if vmad else None,
                    })

    references = []
    matched = set()
    for name in ORDER:
        targets = wanted_offsets[name]
        if not targets:
            continue
        path = SOURCE_DIR / name
        with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            for sig, flags, fid, offset, payload in _records(data):
                offset_hex = f"0x{offset:X}"
                if offset_hex not in targets or sig != "REFR":
                    continue
                fields = list(_subrecords(payload, flags))
                raw_fields = {sub: value for sub, value in fields}
                masters = source_meta[name]["masters"]
                base_value = int.from_bytes(raw_fields["NAME"], "little") if len(raw_fields.get("NAME", b"")) == 4 else 0
                base_logical = logical_form(base_value, masters, name)
                base = form_index.get((base_logical["origin"].casefold(), base_logical["local_id"])) if base_logical else None
                xesp = raw_fields.get("XESP", b"")
                parent_value = int.from_bytes(xesp[:4], "little") if len(xesp) >= 4 else 0
                parent_logical = logical_form(parent_value, masters, name)
                parent = form_index.get((parent_logical["origin"].casefold(), parent_logical["local_id"])) if parent_logical else None
                ancestry = next(row["group_ancestry"] for row in owners if row["plugin"] == name and row["offset"] == offset_hex)
                world_label = next((g["label_u32"] for g in ancestry if g.get("type") == 1 and "label_u32" in g), None)
                cell_label = next((g["label_u32"] for g in reversed(ancestry) if g.get("type") in {6, 8} and "label_u32" in g), None)
                world_logical = logical_form(world_label, masters, name) if world_label is not None else None
                cell_logical = logical_form(cell_label, masters, name) if cell_label is not None else None
                world = form_index.get((world_logical["origin"].casefold(), world_logical["local_id"])) if world_logical else None
                cell = form_index.get((cell_logical["origin"].casefold(), cell_logical["local_id"])) if cell_logical else None
                vmad = raw_fields.get("VMAD", b"")
                transform = None
                if len(raw_fields.get("DATA", b"")) >= 24:
                    transform = list(struct.unpack_from("<6f", raw_fields["DATA"]))
                references.append({
                    "source_plugin": name, "signature": sig, "form_id": f"{fid:08X}", "origin_plugin": owners[0]["origin_plugin"] if False else logical_form(fid, masters, name)["origin"],
                    "offset": offset_hex, "record_flags_hex": f"{flags:08X}",
                    "base_raw_form_id": f"{base_value:08X}", "base_logical": base_logical, "base_record": base,
                    "cell_group_raw": f"{cell_label:08X}" if cell_label is not None else None, "cell_record": cell,
                    "worldspace_group_raw": f"{world_label:08X}" if world_label is not None else None, "worldspace_record": world,
                    "xesp_raw_hex": xesp.hex(), "enable_parent_raw": f"{parent_value:08X}" if parent_value else None,
                    "enable_parent_logical": parent_logical, "enable_parent_record": parent,
                    "transform_xyz_rot": transform,
                    "vmad": read_vmad(vmad, masters, name) if vmad else None,
                })
                matched.add((name, offset_hex))
    missing = sorted((name, offset) for name, offsets in wanted_offsets.items() for offset in offsets if (name, offset) not in matched)
    parent_keys = {
        (str(row["enable_parent_logical"]["origin"]).casefold(), str(row["enable_parent_logical"]["local_id"]))
        for row in references if row["enable_parent_logical"]
        and row["enable_parent_logical"]["origin"] != "UNRESOLVED"
    }
    parent_candidates: dict[tuple[str, str], list[dict[str, object]]] = {}
    for name in ORDER:
        path = SOURCE_DIR / name
        masters = source_meta[name]["masters"]
        with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            for sig, flags, fid, offset, payload in _records(data):
                logical = logical_form(fid, masters, name)
                if logical is None or logical["origin"] == "UNRESOLVED":
                    continue
                key = (logical["origin"].casefold(), logical["local_id"])
                if key not in parent_keys:
                    continue
                fields = list(_subrecords(payload, flags))
                raw_fields = {sub: value for sub, value in fields}
                edid = next((decode(value) for sub, value in fields if sub == "EDID"), "")
                base_value = int.from_bytes(raw_fields.get("NAME", b"\0\0\0\0"), "little")
                base_logical = logical_form(base_value, masters, name)
                base = form_index.get((base_logical["origin"].casefold(), base_logical["local_id"])) if base_logical else None
                parent_candidates.setdefault(key, []).append({
                    "signature": sig, "source_plugin": name, "form_id": f"{fid:08X}",
                    "origin_plugin": logical["origin"], "editor_id": edid,
                    "base_raw_form_id": f"{base_value:08X}" if base_value else None,
                    "base_record": base,
                    "record_flags_hex": f"{flags:08X}",
                })
    parent_winners = {}
    for key, rows in parent_candidates.items():
        parent_winners[key] = max(rows, key=lambda row: ORDER.index(str(row["source_plugin"])))
    for row in references:
        logical = row["enable_parent_logical"]
        if logical and logical["origin"] != "UNRESOLVED":
            key = (str(logical["origin"]).casefold(), str(logical["local_id"]))
            row["enable_parent_record"] = parent_winners.get(key)

    def resolve_vmad_forms(value):
        if isinstance(value, dict):
            logical = value.get("logical")
            if logical and logical.get("origin") != "UNRESOLVED":
                value["resolved_record"] = form_index.get((logical["origin"].casefold(), logical["local_id"]))
            for child in value.values():
                resolve_vmad_forms(child)
        elif isinstance(value, list):
            for child in value:
                resolve_vmad_forms(child)
    for row in references:
        resolve_vmad_forms(row["vmad"])
    base_objects = []
    for key, rows in base_candidates.items():
        winner = max(rows, key=lambda row: ORDER.index(str(row["source_plugin"])))
        resolve_vmad_forms(winner["vmad"])
        base_objects.append({"logical_form": list(key), "official_source_versions": rows, "fixed_five_master_winner": winner})
    source_rows = [{"plugin": name, "sha256": source_meta[name]["sha256"]} for name in ORDER]
    winner_order = {name.casefold(): index for index, name in enumerate(ORDER)}
    logical_groups: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in references:
        key = (str(row["origin_plugin"]).casefold(), str(row["form_id"])[2:].upper())
        logical_groups.setdefault(key, []).append(row)
    resolved = []
    for key, rows in logical_groups.items():
        winner = max(rows, key=lambda row: winner_order[str(row["source_plugin"]).casefold()])
        resolved.append({"logical_form": list(key), "official_source_versions": rows, "fixed_five_master_winner": winner})
    summary = {
        "scope": "fixed official five-master source layer; no profile winner or live runtime result",
        "parser": "tools.plugin_reader._records/_subrecords for targeted REFR payloads plus independent group ancestry from we13-source-scan.json; schema meanings are not inferred from raw bytes",
        "sources": source_rows,
        "direct_reference_owner_records": len(references),
        "logical_reference_count": len(resolved),
        "missing_target_offsets": missing,
        "direct_reference_source_counts": dict(Counter(row["source_plugin"] for row in references)),
        "base_record_counts": dict(Counter(f"{row['base_record']['signature']}:{row['base_record']['editor_id']}" if row["base_record"] else row["base_raw_form_id"] for row in references)),
        "worldspace_counts": dict(Counter(f"{row['worldspace_record']['signature']}:{row['worldspace_record']['editor_id']}" if row["worldspace_record"] else str(row["worldspace_group_raw"]) for row in references)),
        "cell_counts": dict(Counter(f"{row['cell_record']['signature']}:{row['cell_record']['editor_id']}:{row['cell_record']['full_name']}" if row["cell_record"] else str(row["cell_group_raw"]) for row in references)),
        "enable_parent_counts": dict(Counter(f"{row['enable_parent_record']['signature']}:{row['enable_parent_record']['editor_id']}" if row["enable_parent_record"] else str(row["enable_parent_raw"]) for row in references)),
        "record_flag_counts": dict(Counter(row["record_flags_hex"] for row in references)),
        "xesp_raw_counts": dict(Counter(row["xesp_raw_hex"] for row in references)),
        "references": references,
        "fixed_five_master_logical_winners": resolved,
        "enable_parent_logical_winners": {f"{key[0]}:{key[1]}": value for key, value in parent_winners.items()},
        "trigger_base_objects": base_objects,
        "warning": "Raw flags, XESP, group ancestry and VMAD values are preserved; field semantics and game-loaded cell state require schema or runtime evidence.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in (
        "sources", "direct_reference_owner_records", "logical_reference_count", "missing_target_offsets",
        "direct_reference_source_counts", "base_record_counts", "worldspace_counts", "cell_counts",
        "enable_parent_counts", "record_flag_counts", "xesp_raw_counts",
    )} | {"output": OUTPUT.relative_to(ROOT).as_posix()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
