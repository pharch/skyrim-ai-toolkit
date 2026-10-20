#!/usr/bin/env python3
"""Decode bounded v4/object-format-1 and v5/object-format-2 helper REF VMADs."""
from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / ".local/alignment/transactions/TX-20261018-0005/da05-helper-vmad-triage.json"
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261018-0005/decoded-helper-vmad-properties.json"


class Reader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 0

    def take(self, size: int) -> bytes:
        if self.pos + size > len(self.data):
            raise ValueError(f"truncated VMAD at byte {self.pos}, wanted {size}")
        result = self.data[self.pos:self.pos + size]
        self.pos += size
        return result

    def u8(self) -> int:
        return self.take(1)[0]

    def u16(self) -> int:
        return struct.unpack("<H", self.take(2))[0]

    def i32(self) -> int:
        return struct.unpack("<i", self.take(4))[0]

    def f32(self) -> float:
        return struct.unpack("<f", self.take(4))[0]

    def string(self) -> str:
        return self.take(self.u16()).decode("cp1252", errors="replace")


def property_value(reader: Reader, kind: int, object_format: int) -> Any:
    if kind == 1:
        width = 8 if object_format in {1, 2} else 0
        if not width:
            raise ValueError(f"unsupported object format {object_format}")
        data = reader.take(width)
        if object_format == 1:
            form_id = data[:4]
            alias_id = data[4:6]
            unused = data[6:]
        else:
            unused = data[:2]
            alias_id = data[2:4]
            form_id = data[4:8]
        return {
            "form_id_u32": f"{int.from_bytes(form_id, 'little'):08X}",
            "alias_id": int.from_bytes(alias_id, "little", signed=True),
            "unused_hex": unused.hex(),
        }
    if kind == 2:
        return reader.string()
    if kind == 3:
        return reader.i32()
    if kind == 4:
        return reader.f32()
    if kind == 5:
        return bool(reader.u8())
    raise ValueError(f"unsupported VMAD property kind {kind}")


def parse_vmad(hex_data: str) -> dict[str, Any]:
    reader = Reader(bytes.fromhex(hex_data))
    version = reader.u16()
    object_format = reader.u16()
    if (version, object_format) not in {(4, 1), (5, 2)}:
        raise ValueError(f"unsupported VMAD version/format {version}/{object_format}")
    script_count = reader.u16()
    scripts = []
    for _ in range(script_count):
        name = reader.string()
        flags = reader.u8()
        properties = []
        for _ in range(reader.u16()):
            property_name = reader.string()
            kind = reader.u8()
            property_flags = reader.u8()
            value = property_value(reader, kind, object_format)
            properties.append({
                "name": property_name,
                "kind": kind,
                "flags": property_flags,
                "value": value,
            })
        scripts.append({"name": name, "flags": flags, "properties": properties})
    if reader.pos != len(reader.data):
        raise ValueError(f"{len(reader.data) - reader.pos} trailing VMAD bytes")
    return {"version": version, "object_format": object_format, "scripts": scripts}


def main() -> int:
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    records = []
    errors = []
    for row in source["candidates"]:
        if row["signature"] != "REFR":
            continue
        try:
            decoded = parse_vmad(row["vmad_hex"])
        except ValueError as exc:
            errors.append({"form_id": row["form_id"], "error": str(exc)})
            continue
        records.append({
            "plugin": row["plugin"],
            "form_id": row["form_id"],
            "editor_id": row["editor_id"],
            **decoded,
        })
    output = {
        "scope": "the 18 Skyrim.esm REFR candidates whose VMAD subrecords contain exact 000955CF bytes; v4/object-format-1 and v5/object-format-2 properties",
        "candidate_count": len(records),
        "errors": errors,
        "records": records,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate_count": len(records),
        "errors": errors,
        "records": [
            {"form_id": row["form_id"], "scripts": [
                {"name": script["name"], "properties": script["properties"]}
                for script in row["scripts"]
            ]}
            for row in records
        ],
        "output": OUTPUT.relative_to(ROOT).as_posix(),
    }, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
