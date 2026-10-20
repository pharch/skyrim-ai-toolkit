#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/xedit-bridge/20261018T125120.279526Z/stdout.raw"
records = [
    json.loads(line)
    for line in CAPTURE.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
matches = [record for record in records if record.get("editor_id") == "DLC1VQ01"]
if len(matches) != 1:
    raise SystemExit("expected one exact DLC1VQ01 record, found {}".format(len(matches)))
record = matches[0]
selected = [
    item for item in record["subrecords"]
    if item["signature"] in {"DNAM", "ENAM", "DATA", "CTDA", "INDX", "QSTA", "VMAD", "ANAM", "NEXT", "FULL"}
]
summary = {
    "route": "direct read-only TES4 file parser; not xEdit",
    "plugin": record["plugin"],
    "origin_plugin": record["origin_plugin"],
    "file_form_id": record["file_form_id"],
    "local_form_id": record["local_form_id"],
    "editor_id": record["editor_id"],
    "record_flags": record["flags"],
    "record_offset": record["offset"],
    "selected_subrecords": selected,
}
print(json.dumps(summary, indent=2, ensure_ascii=False))
