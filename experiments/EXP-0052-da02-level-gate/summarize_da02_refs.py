#!/usr/bin/env python3
"""Summarize captured five-master raw FormID screens without large payloads."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/transactions/TX-20261016-0045"
DETAIL_SIGNATURES = {
    "SMQN", "QUST", "BOOK", "REFR", "ACHR", "ACTI", "FURN", "CONT",
    "LVLI", "FLST", "OTFT", "NPC_", "CREA", "SCEN", "PACK", "DIAL",
    "INFO", "CELL", "WRLD", "DOOR", "MISC",
}


def read_rows(filename: str) -> tuple[list[dict], list[dict]]:
    rows = []
    summaries = []
    for line in (CAPTURE / filename).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("scan_summary"):
            summaries.append(row)
        else:
            rows.append(row)
    return rows, summaries


def compact(row: dict) -> dict:
    value = row.get("subrecord_hex", "")
    return {
        "source_plugin": row.get("source_plugin"),
        "record_signature": row.get("record_signature"),
        "record_form_id": row.get("record_form_id"),
        "record_origin_plugin": row.get("record_origin_plugin"),
        "record_editor_id": row.get("record_editor_id"),
        "subrecord_signature": row.get("subrecord_signature"),
        "matching_form_ids": row.get("matching_form_ids"),
        "subrecord_hex_prefix": value[:240],
        "subrecord_hex_length": len(value),
    }


def summarize(filename: str, kind: str) -> dict:
    rows, summaries = read_rows(filename)
    counts = Counter()
    relevant = []
    for row in rows:
        if row.get("subrecord_signature") == "NVNM":
            continue
        signature = row.get("record_signature", "")
        for form_id in row.get("matching_form_ids", []):
            counts[(row.get("source_plugin", ""), form_id, signature)] += 1
        if signature in DETAIL_SIGNATURES:
            relevant.append(compact(row))
    return {
        "capture": filename,
        "scan_summaries": summaries,
        "counts_by_plugin_formid_signature": [
            {"plugin": plugin, "form_id": form_id, "record_signature": signature, "subrecord_hits": count}
            for (plugin, form_id, signature), count in sorted(counts.items())
        ],
        "selected_record_hits": relevant,
        "interpretation_limit": "Raw byte references are candidates; records, aliases, scripts, and winning profile overrides require separate interpretation.",
        "kind": kind,
    }


def main() -> int:
    report = [
        summarize("da02-all-master-formid-scan.stdout.raw", "main_and_helper_quest_reference_screen"),
        summarize("da02-book-reference-scan.stdout.raw", "book_distribution_reference_screen"),
    ]
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
