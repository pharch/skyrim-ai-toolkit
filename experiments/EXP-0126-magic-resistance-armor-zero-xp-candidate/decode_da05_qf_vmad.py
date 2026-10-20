#!/usr/bin/env python3
"""Decode the captured Skyrim.esm DA05 QUST VMAD for its QF fragment binding."""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Reader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.offset = 0

    def take(self, count: int) -> bytes:
        if count < 0 or self.offset + count > len(self.data):
            raise ValueError(f"read outside VMAD at {self.offset}, count={count}, size={len(self.data)}")
        value = self.data[self.offset : self.offset + count]
        self.offset += count
        return value

    def u8(self) -> int:
        return self.take(1)[0]

    def u16(self) -> int:
        return struct.unpack("<H", self.take(2))[0]

    def i16(self) -> int:
        return struct.unpack("<h", self.take(2))[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.take(4))[0]

    def string(self) -> str:
        length = self.u16()
        return self.take(length).decode("utf-8", errors="replace")


def skip_object(reader: Reader, object_format: int) -> dict[str, int]:
    if object_format == 2:
        reader.take(2)
        alias_id = reader.i16()
        form_id = reader.u32()
    elif object_format == 1:
        form_id = reader.u32()
        alias_id = reader.i16()
        reader.take(2)
    else:
        raise ValueError(f"unsupported object format {object_format}")
    return {"alias_id": alias_id, "form_id": form_id}


def read_value(reader: Reader, value_type: int, object_format: int):
    if value_type == 0:
        return None
    if value_type == 1:
        return skip_object(reader, object_format)
    if value_type == 2:
        return reader.string()
    if value_type == 3:
        return struct.unpack("<i", reader.take(4))[0]
    if value_type == 4:
        return struct.unpack("<f", reader.take(4))[0]
    if value_type == 5:
        return bool(reader.u8())
    if 11 <= value_type <= 15:
        count = reader.u32()
        if count > 10000:
            raise ValueError(f"implausible property array count {count}")
        return [read_value(reader, value_type - 10, object_format) for _ in range(count)]
    raise ValueError(f"unsupported VMAD property type {value_type}")


def read_script(reader: Reader, object_format: int) -> dict:
    name = reader.string()
    flags = reader.u8()
    properties = []
    for _ in range(reader.u16()):
        property_name = reader.string()
        value_type = reader.u8()
        property_flags = reader.u8()
        value = read_value(reader, value_type, object_format)
        properties.append({"name": property_name, "type": value_type, "flags": property_flags, "value": value})
    return {"name": name, "flags": flags, "properties": properties}


def decode_vmad(data: bytes) -> dict:
    reader = Reader(data)
    version = reader.u16()
    object_format = reader.u16()
    scripts = [read_script(reader, object_format) for _ in range(reader.u16())]
    extra_bind_version = reader.u8()
    fragment_count = reader.u16()
    file_name = reader.string()
    fragments = []
    for _ in range(fragment_count):
        stage = reader.u32()
        log_entry = reader.u32()
        reader.u8()
        fragments.append({"stage": stage, "log_entry": log_entry, "script": reader.string(), "fragment": reader.string()})
    aliases = []
    alias_count = reader.u16()
    for _ in range(alias_count):
        target = skip_object(reader, object_format)
        alias_version = reader.u16()
        alias_format = reader.u16()
        alias_scripts = [read_script(reader, alias_format) for _ in range(reader.u16())]
        aliases.append({**target, "version": alias_version, "object_format": alias_format, "scripts": alias_scripts})
    if reader.offset != len(data):
        raise ValueError(f"{len(data) - reader.offset} unparsed VMAD bytes at {reader.offset}")
    return {"version": version, "object_format": object_format, "extra_bind_version": extra_bind_version,
            "file_name": file_name, "scripts": scripts, "fragments": fragments, "aliases": aliases}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("capture", nargs="?", default=".local/alignment/transactions/TX-20261018-0011/skyrim-da05-savior-source-records.json")
    args = parser.parse_args()
    source_path = Path(args.capture)
    if not source_path.is_absolute():
        source_path = ROOT / source_path
    source_path = source_path.resolve()
    try:
        source_path.relative_to((ROOT / ".local").resolve())
    except ValueError as exc:
        raise ValueError("input must remain below ignored .local/") from exc
    wrapper = json.loads(source_path.read_text(encoding="utf-8"))
    matching = [json.loads(line) for line in wrapper.get("records_jsonl", "").splitlines() if line.strip()]
    record = next(row for row in matching if row.get("file_form_id") == "0002A49A" and row.get("editor_id") == "DA05")
    vmad = next(field["hex"] for field in record["subrecords"] if field["signature"] == "VMAD")
    decoded = decode_vmad(bytes.fromhex(vmad))
    reward_properties = [prop for script in decoded["scripts"] for prop in script["properties"] if prop["name"] == "SaviorsHide"]
    fragments = [fragment for fragment in decoded["fragments"] if fragment["fragment"] == "Fragment_20"]
    print(json.dumps({"record": {"plugin": record["plugin"], "file_form_id": record["file_form_id"], "editor_id": record["editor_id"]},
                      "vmad_version": decoded["version"], "object_format": decoded["object_format"],
                      "file_name": decoded["file_name"], "saviors_hide_properties": reward_properties,
                      "fragment_20_bindings": fragments}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
