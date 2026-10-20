#!/usr/bin/env python3
"""Decode the QUST VMAD fragment and alias-script tables for EXP-0043.

The byte layout follows TES5Edit dev-4.1.6 Core/wbDefinitionsTES5.pas:
wbScriptEntry and wbVMADFragmentedQUST. This only decodes captured bytes; it
does not make an xEdit or winning-record claim.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path


DEFAULT = Path(".local/alignment/transactions/TX-20261016-0036/qust-da04.json")


class Reader:
    def __init__(self, data: bytes):
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
        alias = reader.i16()
        form = reader.u32()
    elif object_format == 1:
        form = reader.u32()
        alias = reader.i16()
        reader.take(2)
    else:
        raise ValueError(f"unsupported object format {object_format}")
    return {"alias_id": alias, "form_id": form}


def read_property_value(reader: Reader, value_type: int, object_format: int):
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
        scalar_type = value_type - 10
        return [read_property_value(reader, scalar_type, object_format) for _ in range(count)]
    raise ValueError(f"unsupported VMAD property type {value_type}")


def read_script(reader: Reader, object_format: int) -> dict:
    name = reader.string()
    flags = reader.u8()
    count = reader.u16()
    properties = []
    for _ in range(count):
        property_name = reader.string()
        value_type = reader.u8()
        property_flags = reader.u8()
        value = read_property_value(reader, value_type, object_format)
        properties.append({"name": property_name, "type": value_type, "flags": property_flags, "value": value})
    return {"name": name, "flags": flags, "properties": properties}


def decode_vmad(hex_data: str) -> dict:
    reader = Reader(bytes.fromhex(hex_data))
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
        script_name = reader.string()
        fragment_name = reader.string()
        fragments.append({"stage": stage, "log_entry": log_entry, "script": script_name, "fragment": fragment_name})
    aliases = []
    alias_count = reader.u16()
    for _ in range(alias_count):
        target = skip_object(reader, object_format)
        alias_version = reader.u16()
        alias_object_format = reader.u16()
        alias_scripts = [read_script(reader, alias_object_format) for _ in range(reader.u16())]
        aliases.append({**target, "version": alias_version, "object_format": alias_object_format, "scripts": alias_scripts})
    if reader.offset != len(reader.data):
        raise ValueError(f"{len(reader.data) - reader.offset} unparsed VMAD bytes at {reader.offset}")
    return {
        "version": version,
        "object_format": object_format,
        "scripts": scripts,
        "extra_bind_version": extra_bind_version,
        "file_name": file_name,
        "fragments": fragments,
        "aliases": aliases,
    }


def main() -> None:
    wrapper = json.loads(DEFAULT.read_text(encoding="utf-8"))
    for line in wrapper.get("records_jsonl", "").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("editor_id") != "DA04":
            continue
        vmad = next(item["hex"] for item in record["subrecords"] if item["signature"] == "VMAD")
        decoded = decode_vmad(vmad)
        print(json.dumps({"form_id": record["file_form_id"], "editor_id": record["editor_id"], **decoded}, indent=2))


if __name__ == "__main__":
    main()
