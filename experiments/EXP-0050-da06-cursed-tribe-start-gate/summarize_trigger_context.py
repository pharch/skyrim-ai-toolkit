#!/usr/bin/env python3
"""Produce a compact semantic view of DA06's retained placement capture."""
from __future__ import annotations

import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/alignment/transactions/TX-20261016-0043/da06-trigger-reference-context.stdout.raw"


def field_values(row: dict, signature: str) -> list[bytes]:
    return [bytes.fromhex(item["hex"]) for item in row.get("fields", []) if item["signature"] == signature]


def main() -> int:
    capture = json.loads(SOURCE.read_text(encoding="utf-8"))
    refs = []
    cells = []
    for row in capture["matches"]:
        if row["signature"] in ("REFR", "ACHR"):
            ancestry = [f"type{item['type']}={item['label_u32']}" for item in row["group_ancestry"] if item["type"] in (6, 8, 9)]
            xesp = []
            for raw in field_values(row, "XESP"):
                xesp.append({
                    "parent_form_id": f"{struct.unpack_from('<I', raw)[0]:08X}" if len(raw) >= 4 else None,
                    "flags": f"0x{struct.unpack_from('<I', raw, 4)[0]:08X}" if len(raw) >= 8 else None,
                })
            refs.append({
                "source_plugin": row["source_plugin"], "signature": row["signature"],
                "form_id": row["file_form_id"], "editor_id": row["editor_id"],
                "record_flags": row["record_flags"], "base_form_ids": row["base_form_ids"],
                "cell_group_labels": ancestry, "xesp": xesp,
            })
        elif row["signature"] == "CELL":
            cells.append({
                "source_plugin": row["source_plugin"], "form_id": row["file_form_id"],
                "editor_id": row["editor_id"], "record_flags": row["record_flags"],
            })
    print(json.dumps({"references": refs, "cells": cells}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
