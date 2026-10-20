#!/usr/bin/env python3
"""Summarize the private five-master DA06 trigger/reference byte scan."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/alignment/transactions/TX-20261016-0043/da06-trigger-placement-scan.stdout.raw"


def main() -> int:
    summaries = []
    matches = []
    with SOURCE.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("scan_summary"):
                summaries.append({key: row.get(key) for key in (
                    "source_plugin", "source_sha256", "record_count", "subrecord_count",
                    "matching_subrecord_count", "matching_record_count", "searched_form_ids")
                })
            elif row.get("record_signature") in {"REFR", "ACHR", "QUST", "SCEN", "ACTI", "CELL"}:
                matches.append({key: row.get(key) for key in (
                    "source_plugin", "source_sha256", "record_signature", "record_form_id",
                    "record_origin_plugin", "record_editor_id", "record_offset",
                    "subrecord_signature", "matching_form_ids")
                })
    print(json.dumps({"summaries": summaries, "matches": matches}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
