#!/usr/bin/env python3
"""Decode only schema-relevant subrecords from the Q-0075 record capture."""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


def form_ids(raw: bytes) -> list[str]:
    if len(raw) % 4:
        raise ValueError(f"FormID array has non-multiple-of-four length {len(raw)}")
    return [f"{struct.unpack_from('<I', raw, offset)[0]:08X}" for offset in range(0, len(raw), 4)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    path = args.capture if args.capture.is_absolute() else root / args.capture
    path = path.resolve()
    try:
        path.relative_to((root / ".local").resolve())
    except ValueError as exc:
        raise ValueError("input capture must remain below ignored .local/") from exc
    raw_capture = path.read_bytes()
    capture = json.loads(raw_capture)
    records = []
    for row in capture.get("records", []):
        decoded = []
        for field in row.get("subrecords", []):
            signature = field["signature"]
            raw = bytes.fromhex(field["value_hex"])
            value = None
            if signature == "LVLO":
                if len(raw) != 12:
                    value = {"raw_hex": raw.hex(), "error": "unexpected_lvlo_size"}
                else:
                    value = {
                        "level_u16": struct.unpack_from("<H", raw, 0)[0],
                        "form_id": f"{struct.unpack_from('<I', raw, 4)[0]:08X}",
                        "count_u16": struct.unpack_from("<H", raw, 8)[0],
                    }
            elif signature == "CNTO" and len(raw) == 8:
                value = {
                    "form_id": f"{struct.unpack_from('<I', raw, 0)[0]:08X}",
                    "count_s32": struct.unpack_from("<i", raw, 4)[0],
                }
            elif signature in {"INAM", "LNAM"}:
                value = form_ids(raw)
            elif signature in {"NAME", "EITM", "DOFT", "SOFT", "XESP", "XLCN", "XOWN", "LVLG"} and len(raw) == 4:
                value = f"{struct.unpack_from('<I', raw, 0)[0]:08X}"
            elif signature == "LVLD" and raw:
                value = {"chance_none_u8": raw[0], "raw_hex": raw.hex()}
            elif signature == "LVLF" and raw:
                value = {"flags_u8": raw[0], "raw_hex": raw.hex()}
            elif signature == "BOD2" and len(raw) >= 8:
                value = {
                    "first_person_flags_u32": struct.unpack_from("<I", raw, 0)[0],
                    "armor_type_u32": struct.unpack_from("<I", raw, 4)[0],
                }
            elif signature == "DNAM" and len(raw) == 4:
                value = {"raw_s32": struct.unpack_from("<i", raw, 0)[0]}
            if value is not None:
                decoded.append({"signature": signature, "length": len(raw), "decoded": value})
        if decoded:
            records.append({
                "source_plugin": row["plugin"],
                "source_sha256": row["source_sha256"],
                "signature": row["signature"],
                "form_id": row["file_form_id"],
                "origin_plugin": row["origin_plugin"],
                "editor_id": row["editor_id"],
                "flags_hex": row["flags"],
                "fields": decoded,
            })
    print(json.dumps({
        "input_capture_sha256": hashlib.sha256(raw_capture).hexdigest(),
        "source_files": capture.get("sources"),
        "decoded_record_count": len(records),
        "records": records,
        "scope": "TES5Edit dev-4.1.6 field-layout interpretation of direct plugin-reader bytes; source records only, not profile winners.",
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
