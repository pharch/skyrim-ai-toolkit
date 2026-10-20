#!/usr/bin/env python3
"""Summarize captured QUST conditions, flag-bearing fields, and alias scripts."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/transactions/TX-20261016-0033/dawnguard-vq-quests.json"
DECODER = ROOT / "experiments/EXP-0043-da04-helper-versus-main-start/decode_qust_vmad.py"
WANTED = {"0200D90B", "0200D90E", "0200352A", "0200D06C", "0201A415"}


def load_rows():
    wrapper = json.loads(CAPTURE.read_text(encoding="utf-8"))
    for line in wrapper.get("records_jsonl", "").splitlines():
        if line.strip():
            yield json.loads(line)


def main() -> int:
    spec = importlib.util.spec_from_file_location("qust_vmad_reader", DECODER)
    if spec is None or spec.loader is None:
        raise RuntimeError("QUST VMAD decoder unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    decode_vmad = module.decode_vmad
    result = []
    for row in load_rows():
        if row.get("signature") != "QUST" or row.get("file_form_id") not in WANTED:
            continue
        fields = row.get("subrecords", [])
        vmad = next((field.get("hex") for field in fields if field.get("signature") == "VMAD"), None)
        decoded = decode_vmad(vmad) if vmad else None
        result.append({
            "file_form_id": row.get("file_form_id"),
            "editor_id": row.get("editor_id"),
            "record_flags": row.get("flags"),
            "conditions": row.get("conditions", []),
            "dnam_hex": [field.get("hex") for field in fields if field.get("signature") == "DNAM"],
            "ctda_hex": [field.get("hex") for field in fields if field.get("signature") == "CTDA"],
            "vmad_script": decoded.get("file_name") if decoded else None,
            "fragments": decoded.get("fragments", []) if decoded else [],
            "alias_scripts": [{
                "alias_id": alias.get("alias_id"),
                "target_form_id": f"{alias.get('form_id', 0):08X}",
                "scripts": alias.get("scripts", []),
            } for alias in decoded.get("aliases", [])] if decoded else [],
        })
    result.sort(key=lambda row: row["file_form_id"])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
