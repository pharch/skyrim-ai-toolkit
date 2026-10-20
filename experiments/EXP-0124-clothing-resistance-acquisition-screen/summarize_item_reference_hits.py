#!/usr/bin/env python3
"""Group raw EXP-0124 direct FormID-reference candidates by record/field."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--include-raw", action="store_true", help="retain matched subrecord bytes in the grouped summary")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    path = args.capture if args.capture.is_absolute() else root / args.capture
    path = path.resolve()
    try:
        path.relative_to((root / ".local").resolve())
    except ValueError as exc:
        raise ValueError("input capture must remain below ignored .local/") from exc
    capture = path.read_text(encoding="utf-8")
    marker = '\n{\n  "scan_summary": true'
    if marker not in capture:
        raise ValueError("raw scan lacks its final scan_summary object")
    hit_text, summary_tail = capture.rsplit(marker, 1)
    summary_text = '{\n  "scan_summary": true' + summary_tail
    hits = [json.loads(line) for line in hit_text.splitlines() if line.strip()]
    summaries = [json.loads(summary_text)]
    grouped: dict[tuple, dict] = {}
    for row in hits:
        key = (
            row["source_plugin"], row["record_signature"], row["record_form_id"],
            row["record_origin_plugin"], row["record_editor_id"], row["subrecord_signature"],
        )
        item = grouped.setdefault(key, {
            "source_plugin": row["source_plugin"],
            "record_signature": row["record_signature"],
            "record_form_id": row["record_form_id"],
            "record_origin_plugin": row["record_origin_plugin"],
            "record_editor_id": row["record_editor_id"],
            "subrecord_signature": row["subrecord_signature"],
            "matching_form_ids": set(),
            "raw_subrecord_hex": set(),
            "hit_count": 0,
        })
        item["matching_form_ids"].update(row["matching_form_ids"])
        item["raw_subrecord_hex"].add(row["subrecord_hex"])
        item["hit_count"] += 1
    result = []
    for item in grouped.values():
        item["matching_form_ids"] = sorted(item["matching_form_ids"])
        raw_hex = sorted(item.pop("raw_subrecord_hex"))
        item["subrecord_hex"] = raw_hex if args.include_raw else None
        result.append(item)
    result.sort(key=lambda row: (
        row["source_plugin"], row["record_signature"], row["record_form_id"], row["subrecord_signature"],
    ))
    field_counts = Counter(f"{row['record_signature']}.{row['subrecord_signature']}" for row in result)
    non_xrgd = [row for row in result if row["subrecord_signature"] != "XRGD"]
    print(json.dumps({
        "input_file": path.name,
        "summary_rows": summaries,
        "raw_hit_count": len(hits),
        "unique_record_subrecord_groups": len(result),
        "record_subrecord_group_counts": dict(sorted(field_counts.items())),
        "non_xrgd_candidate_groups": non_xrgd,
        "raw_bytes_included": args.include_raw,
        "interpretation_limit": "Byte hits are candidates; record and subrecord schemas must confirm semantic references and acquisition context.",
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
