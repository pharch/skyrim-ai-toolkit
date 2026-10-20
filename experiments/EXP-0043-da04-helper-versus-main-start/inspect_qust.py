#!/usr/bin/env python3
"""Print DA04 QUST structural fields retained by the direct parser."""

from __future__ import annotations

import json
from pathlib import Path


path = Path(".local/alignment/transactions/TX-20261016-0036/qust-da04.json")
wrapper = json.loads(path.read_text(encoding="utf-8"))
for line in wrapper.get("records_jsonl", "").splitlines():
    if not line.strip():
        continue
    record = json.loads(line)
    if record.get("editor_id") != "DA04":
        continue
    print(f"QUST {record['file_form_id']} {record['editor_id']} flags={record['flags']}")
    for index, subrecord in enumerate(record.get("subrecords", [])):
        signature = subrecord.get("signature", "")
        value = subrecord.get("hex", "")
        if signature == "VMAD":
            print(f"{index:03d} VMAD bytes={len(value) // 2}")
        elif signature in {"EDID", "DNAM", "ENAM", "NEXT", "ANAM", "ALST", "ALLS", "ALID", "ALCO", "ALFR", "ALUA", "ALFE", "ALFD", "ALFA", "ALFT", "CTDA", "INDX", "QSDT", "CNAM", "SCTX", "QNAM"}:
            print(f"{index:03d} {signature} {value}")
