#!/usr/bin/env python3
"""Summarize the forced Ruminations reference capture."""

from __future__ import annotations

import json
from pathlib import Path


path = Path(".local/alignment/transactions/TX-20261016-0036/refr-ruminations.json")
wrapper = json.loads(path.read_text(encoding="utf-8"))
for line in wrapper.get("records_jsonl", "").splitlines():
    if not line.strip():
        continue
    record = json.loads(line)
    print(f"{record['signature']} {record['file_form_id']} {record['editor_id']} flags={record['flags']}")
    for subrecord in record.get("subrecords", []):
        print(f"  {subrecord.get('signature')} {subrecord.get('hex')}")
