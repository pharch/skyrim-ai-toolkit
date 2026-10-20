#!/usr/bin/env python3
"""Capture the Arch-Mage quarters child references and linked door endpoints."""
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
TARGET_CELL = 0x000CAB92
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.plugin_reader import PluginFormatError, _subrecords

INTERESTING = {"EDID", "FULL", "NAME", "XLOC", "XTEL", "XOWN", "XESP", "XLCN", "DATA", "VMAD", "CTDA"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def walk(data: mmap.mmap, start: int = 0, end: int | None = None, groups=(), *, wanted=None):
    limit = len(data) if end is None else end
    pos = start
    while pos < limit:
        if limit - pos < 24:
            raise PluginFormatError(f"truncated record/group header at 0x{pos:X}")
        signature, size = struct.unpack_from("<4sI", data, pos)
        if signature == b"GRUP":
            if size < 24 or pos + size > limit:
                raise PluginFormatError(f"invalid group at 0x{pos:X}")
            label = bytes(data[pos + 8:pos + 12])
            group_type = struct.unpack_from("<i", data, pos + 12)[0]
            group = {
                "type": group_type,
                "label_hex": label.hex(),
                "label_form_id": int.from_bytes(label, "little"),
                "label_text": label.decode("ascii", "replace") if group_type == 0 else None,
            }
            yield from walk(data, pos + 24, pos + size, (*groups, group), wanted=wanted)
            pos += size
            continue
        if pos + 24 + size > limit:
            raise PluginFormatError(f"record exceeds group at 0x{pos:X}")
        flags, form_id = struct.unpack_from("<II", data, pos + 8)
        record_signature = signature.decode("ascii", "strict")
        selected = wanted is None or wanted(record_signature, form_id, groups)
        payload = bytes(data[pos + 24:pos + 24 + size]) if selected else b""
        yield {
            "signature": record_signature,
            "form_id": form_id,
            "flags": flags,
            "offset": pos,
            "groups": groups,
            "subrecords": list(_subrecords(payload, flags)) if selected else [],
        }
        pos += 24 + size


def by_signature(fields: list[tuple[str, bytes]]) -> dict[str, list[bytes]]:
    result: dict[str, list[bytes]] = {}
    for name, value in fields:
        result.setdefault(name, []).append(value)
    return result


def field_value(data: bytes) -> dict:
    value = data.hex()
    if len(data) == 4:
        value = f"{struct.unpack('<I', data)[0]:08X}"
    return {"length": len(data), "value": value}


def record_summary(record: dict, *, cell_labels: dict[int, str]) -> dict:
    fields = by_signature(record["subrecords"])
    selected = []
    for name, values in fields.items():
        if name not in INTERESTING:
            continue
        for raw in values:
            entry = {"signature": name, **field_value(raw)}
            if name == "XLOC" and len(raw) >= 8:
                entry["lock_level_byte0"] = raw[0]
                entry["key_form_id_bytes4_7"] = f"{struct.unpack_from('<I', raw, 4)[0]:08X}"
            elif name == "XTEL" and len(raw) >= 4:
                entry["paired_reference_form_id"] = f"{struct.unpack_from('<I', raw, 0)[0]:08X}"
            elif name == "XESP" and len(raw) >= 8:
                entry["enable_parent_form_id"] = f"{struct.unpack_from('<I', raw, 0)[0]:08X}"
                entry["enable_parent_flags"] = raw[4]
            selected.append(entry)
    ancestry = []
    for group in record["groups"]:
        entry = dict(group)
        entry["cell_editor_id"] = cell_labels.get(group["label_form_id"])
        ancestry.append(entry)
    return {
        "signature": record["signature"],
        "form_id": f"{record['form_id']:08X}",
        "record_flags": f"{record['flags']:08X}",
        "record_offset": f"0x{record['offset']:X}",
        "all_subrecord_signatures": [name for name, _ in record["subrecords"]],
        "group_ancestry": ancestry,
        "fields": selected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not SOURCE.is_file():
        raise FileNotFoundError("prepared official Skyrim.esm is unavailable")
    source_hash = digest(SOURCE)
    if source_hash != EXPECTED_SHA256:
        raise ValueError("prepared Skyrim.esm SHA-256 differs from the expected source")
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if not output.resolve().is_relative_to((ROOT / ".local").resolve()):
        raise ValueError("capture output must remain below ignored .local/")

    cell_children = []
    cell_labels = {}
    record_count_walked = 0
    with SOURCE.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        wanted = lambda sig, form, groups: (
            (sig == "CELL" and form == TARGET_CELL)
            or (sig == "REFR" and any(group["type"] == 6 and group["label_form_id"] == TARGET_CELL for group in groups))
        )
        for record in walk(data, wanted=wanted):
            record_count_walked += 1
            if record["signature"] == "REFR" and any(
                group["type"] == 6 and group["label_form_id"] == TARGET_CELL for group in record["groups"]
            ):
                cell_children.append(record)
            elif record["signature"] == "CELL" and record["form_id"] == TARGET_CELL:
                fields = by_signature(record["subrecords"])
                cell_labels[TARGET_CELL] = fields.get("EDID", [b""])[0].rstrip(b"\0").decode("cp1252", "replace")
    cell_refs = {record["form_id"] for record in cell_children}
    cell_base_ids = {
        int.from_bytes(raw, "little")
        for record in cell_children
        for name, raw in record["subrecords"]
        if name == "NAME" and len(raw) == 4
    }
    base_records = []
    with SOURCE.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        for record in walk(data, wanted=lambda sig, form, groups: form in cell_base_ids):
            record_count_walked += 1
            if record["form_id"] in cell_base_ids:
                base_records.append(record)
    base_by_id = {record["form_id"]: record for record in base_records}
    door_base_ids = {form_id for form_id, record in base_by_id.items() if record["signature"] == "DOOR"}
    cell_door_refs = []
    paired_ids: set[int] = set()
    for record in cell_children:
        fields = by_signature(record["subrecords"])
        base_values = fields.get("NAME", [])
        if not base_values or len(base_values[0]) != 4 or int.from_bytes(base_values[0], "little") not in door_base_ids:
            continue
        cell_door_refs.append(record)
        for raw in fields.get("XTEL", []):
            if len(raw) >= 4:
                paired_ids.add(struct.unpack_from("<I", raw)[0])

    access_ref_ids = cell_refs | paired_ids
    access_records = list(cell_children)
    with SOURCE.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        for record in walk(data, wanted=lambda sig, form, groups: sig == "REFR" and form in paired_ids):
            record_count_walked += 1
            if record["signature"] == "REFR" and record["form_id"] in paired_ids:
                access_records.append(record)
    related_cell_ids = {
        group["label_form_id"]
        for record in access_records
        for group in record["groups"]
        if group["type"] == 6
    }
    with SOURCE.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        for record in walk(data, wanted=lambda sig, form, groups: sig == "CELL" and form in related_cell_ids):
            record_count_walked += 1
            if record["signature"] == "CELL" and record["form_id"] in related_cell_ids:
                fields = by_signature(record["subrecords"])
                cell_labels[record["form_id"]] = fields.get("EDID", [b""])[0].rstrip(b"\0").decode("cp1252", "replace")
    access_base_ids = {
        int.from_bytes(raw, "little")
        for record in access_records
        for name, raw in record["subrecords"]
        if name == "NAME" and len(raw) == 4
    }
    access_bases = []
    with SOURCE.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
        for record in walk(data, wanted=lambda sig, form, groups: form in access_base_ids):
            record_count_walked += 1
            if record["form_id"] in access_base_ids:
                access_bases.append(record)
    base_names = {}
    for record in access_bases:
        fields = by_signature(record["subrecords"])
        edid = fields.get("EDID", [b""])[0].rstrip(b"\0").decode("cp1252", "replace")
        base_names[record["form_id"]] = {"signature": record["signature"], "editor_id": edid}
    door_base_records = []
    for record in access_bases:
        if record["signature"] != "DOOR":
            continue
        fields = by_signature(record["subrecords"])
        door_base_records.append({
            "form_id": f"{record['form_id']:08X}",
            "editor_id": fields.get("EDID", [b""])[0].rstrip(b"\0").decode("cp1252", "replace"),
            "all_subrecord_signatures": [name for name, _ in record["subrecords"]],
            "vmad_hex": [raw.hex() for raw in fields.get("VMAD", [])],
            "ctda_hex": [raw.hex() for raw in fields.get("CTDA", [])],
        })

    def summarize(record: dict) -> dict:
        result = record_summary(record, cell_labels=cell_labels)
        fields = by_signature(record["subrecords"])
        base_id = int.from_bytes(fields["NAME"][0], "little") if fields.get("NAME") and len(fields["NAME"][0]) == 4 else None
        result["base_record"] = ({"form_id": f"{base_id:08X}", **base_names.get(base_id, {})} if base_id is not None else None)
        return result

    result = {
        "source_plugin": "Skyrim.esm",
        "source_sha256": source_hash,
        "parser": "Read-only TES4 group walk and bounded subrecord decoding using tools.plugin_reader._subrecords",
        "target_cell": {"form_id": f"{TARGET_CELL:08X}", "editor_id": cell_labels.get(TARGET_CELL)},
        "scope": "All REFR records in CELL children group type 6 for 000CAB92, their DOOR base records, and the exact XTEL-paired REFR endpoints. No active-profile winner or runtime state.",
        "record_count_walked": record_count_walked,
        "cell_child_reference_count": len(cell_children),
        "cell_door_reference_count": len(cell_door_refs),
        "paired_endpoint_count": len(paired_ids),
        "cell_door_references": [summarize(record) for record in cell_door_refs],
        "paired_endpoints": [summarize(record) for record in access_records if record["form_id"] in paired_ids],
        "door_base_records": door_base_records,
        "profile_winner_resolved": False,
        "runtime_tested": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_sha256": source_hash,
        "record_count_walked": record_count_walked,
        "cell_child_reference_count": len(cell_children),
        "cell_door_reference_count": len(cell_door_refs),
        "paired_endpoint_count": len(paired_ids),
        "cell_door_references": [{"form_id": row["form_id"], "base_record": row["base_record"], "fields": row["fields"]}
                                  for row in result["cell_door_references"]],
        "paired_endpoints": [{"form_id": row["form_id"], "base_record": row["base_record"], "fields": row["fields"]}
                             for row in result["paired_endpoints"]],
        "door_base_records": door_base_records,
        "output": output.relative_to(ROOT).as_posix(),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, PluginFormatError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
