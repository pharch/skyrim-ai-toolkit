#!/usr/bin/env python3
"""Decode DA06's retained QUST VMAD with the existing schema-ordered reader."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/alignment/transactions/TX-20261016-0043/da06-qust-plugin-reader.stdout.raw"
DECODER = ROOT / "experiments/EXP-0043-da04-helper-versus-main-start/decode_qust_vmad.py"


def main() -> int:
    spec = importlib.util.spec_from_file_location("qust_vmad_decoder", DECODER)
    if spec is None or spec.loader is None:
        raise SystemExit("existing schema-ordered QUST VMAD decoder is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    row = json.loads(SOURCE.read_text(encoding="utf-8"))
    vmad_hex = next(item["value_hex"] for item in row["subrecords"] if item["signature"] == "VMAD")
    decoded = module.decode_vmad(vmad_hex)
    print(json.dumps({
        "source_plugin": row["plugin"], "source_form_id": row["file_form_id"],
        "editor_id": row["editor_id"], "source_vmad_hex_length": len(vmad_hex) // 2,
        "fragments": decoded["fragments"],
        "aliases": [
            {"alias_id": alias["alias_id"], "scripts": alias["scripts"]}
            for alias in decoded["aliases"]
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
