#!/usr/bin/env python3
"""Map DA06 trigger-base placements and fixed refs to source group context."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import struct
import sys
import mmap

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.plugin_reader import _subrecords

MASTERS = ("Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm")
EXPECTED = {
    "Skyrim.esm": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
    "Update.esm": "c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9",
    "Dawnguard.esm": "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4",
    "HearthFires.esm": "ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97",
    "Dragonborn.esm": "5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b",
}
PLACED_BASES = {
    "0010F6A2", "000EAB2A", "0002E527", "0001FF47", "000A7B04",
    "00019E18",  # DA06AtubAlias unique-actor candidate from QUST ALUA
    "0008BEE6",  # fixed giant ACHR 0008BEE2 base
}
FIXED_AND_KNOWN_REFS = {
    "0008CD9E", "0008BEE2", "000EAB2B", "0002E528", "0002C007",
    "00019E23", "00019E21", "00019E1F", "00019E1D", "00019E1B",
    "000A0E72",  # XESP enable parent of fixed giant ACHR 0008BEE2
}


def resolve_data_root() -> Path:
    configured = read_local_config(ROOT).get("SKYRIM_DATA", "").strip()
    win = PureWindowsPath(configured)
    if os.name != "nt" and win.drive and len(win.drive) == 2 and win.drive[1] == ":":
        path = Path("/mnt") / win.drive[0].lower() / Path(*win.parts[1:])
    else:
        path = Path(configured).expanduser()
    if not path.is_dir():
        raise SystemExit("SKYRIM_DATA in config/local.env is inaccessible")
    return path


def decode_form(value: bytes) -> str | None:
    if len(value) < 4:
        return None
    return f"{struct.unpack_from('<I', value)[0]:08X}"


def main() -> int:
    data_root = resolve_data_root()
    rows: list[dict[str, object]] = []
    cell_form_ids: set[str] = set()
    cell_records: list[dict[str, object]] = []
    for master in MASTERS:
        path = data_root / master
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != EXPECTED[master]:
            raise SystemExit(f"prepared master SHA-256 mismatch: {master}")
        with path.open("rb") as stream, mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            def walk(start: int, end: int, ancestry: list[dict[str, object]]) -> None:
                pos = start
                while pos < end:
                    if end - pos < 24:
                        raise ValueError(f"truncated TES4 header in {master} at 0x{pos:X}")
                    sig, size = struct.unpack_from("<4sI", data, pos)
                    if sig == b"GRUP":
                        if size < 24 or pos + size > end:
                            raise ValueError(f"bad GRUP in {master} at 0x{pos:X}")
                        label = bytes(data[pos + 8:pos + 12])
                        kind = struct.unpack_from("<I", data, pos + 12)[0]
                        next_ancestry = ancestry + [{
                            "type": kind,
                            "label_hex": label.hex(),
                            "label_u32": f"{int.from_bytes(label, 'little'):08X}",
                        }]
                        walk(pos + 24, pos + size, next_ancestry)
                        pos += size
                        continue
                    if pos + 24 + size > end:
                        raise ValueError(f"record overflow in {master} at 0x{pos:X}")
                    signature = sig.decode("ascii", "strict")
                    flags, formid = struct.unpack_from("<II", data, pos + 8)
                    form_text = f"{formid:08X}"
                    payload = bytes(data[pos + 24:pos + 24 + size])
                    fields = list(_subrecords(payload, flags))
                    field_map: dict[str, list[bytes]] = {}
                    for field_sig, raw in fields:
                        field_map.setdefault(field_sig, []).append(raw)
                    local = f"{formid & 0x00FFFFFF:06X}"
                    name_ids = [decode_form(raw) for raw in field_map.get("NAME", [])]
                    is_fixed = form_text in FIXED_AND_KNOWN_REFS
                    is_base_placement = signature in ("REFR", "ACHR") and any(
                        item is not None and item in PLACED_BASES
                        for item in name_ids
                    )
                    is_cell_target = signature == "CELL" and form_text in cell_form_ids
                    data_fields = []
                    for field_sig in ("EDID", "NAME", "XESP", "DATA", "XCLC", "XTEL"):
                        for raw in field_map.get(field_sig, []):
                            data_fields.append({"signature": field_sig, "hex": raw.hex()})
                    if is_fixed or is_base_placement or is_cell_target:
                        for part in ancestry:
                            if part["type"] in (6, 8, 9):
                                cell_form_ids.add(str(part["label_u32"]))
                    record_row = {
                        "source_plugin": master,
                        "source_sha256": digest,
                        "signature": signature,
                        "file_form_id": form_text,
                        "local_form_id": local,
                        "record_flags": f"0x{flags:08X}",
                        "record_offset": f"0x{pos:X}",
                        "editor_id": next((raw.rstrip(b"\0").decode("cp1252", "replace") for raw in field_map.get("EDID", [])), ""),
                        "base_form_ids": name_ids,
                        "group_ancestry": ancestry,
                        "fields": data_fields,
                    }
                    if signature == "CELL" and (formid >> 24) == 0:
                        cell_records.append(record_row)
                    if is_fixed or is_base_placement:
                        rows.append(record_row)
                    pos += 24 + size
            walk(0, len(data), [])

    rows.extend(row for row in cell_records if str(row["file_form_id"]) in cell_form_ids)

    print(json.dumps({
        "scope": "five prepared official masters; source records only",
        "placed_base_form_ids": sorted(PLACED_BASES),
        "fixed_or_known_reference_ids": sorted(FIXED_AND_KNOWN_REFS),
        "matches": rows,
        "cell_record_ids_to_resolve": sorted(cell_form_ids),
        "limitations": [
            "source-file placement does not establish loaded-cell or player reachability",
            "record flags and XESP fields are preserved raw and require schema-aware interpretation",
            "no active-profile winner is established",
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
