#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/xedit-bridge/20261018T125527.760139Z/stdout.raw"
records = [json.loads(line) for line in CAPTURE.read_text(encoding="utf-8").splitlines() if line.strip()]
record = next((item for item in records if item.get("editor_id") == "DLC1NPCMentalModel"), None)
if record is None:
    raise SystemExit("DLC1NPCMentalModel not found")
selected = [
    item for item in record["subrecords"]
    if item["signature"] in {"DNAM", "ENAM", "DATA", "CTDA", "INDX", "QSTA", "ALST", "ALID", "FNAM", "ALFI", "ALFR", "ALEQ", "ALEA", "NEXT", "ANAM"}
]
print(json.dumps({
    "plugin": record["plugin"],
    "origin_plugin": record["origin_plugin"],
    "file_form_id": record["file_form_id"],
    "editor_id": record["editor_id"],
    "record_flags": record["flags"],
    "subrecord_signatures": [item["signature"] for item in record["subrecords"]],
    "selected_subrecords": selected,
}, indent=2, ensure_ascii=False))
