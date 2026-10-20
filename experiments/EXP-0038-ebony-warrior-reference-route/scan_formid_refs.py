#!/usr/bin/env python3
"""Report raw subrecords containing any requested little-endian FormID bytes.

This is a candidate-finding pass, not a semantic FormID decoder. Interpret each
hit using its record and subrecord schema before making a reference claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.plugin_reader import read_plugin


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugin", type=Path)
    parser.add_argument("form_id", nargs="+", help="full 8-digit FormID")
    args = parser.parse_args()
    needles = {value.upper(): bytes.fromhex(value)[::-1] for value in args.form_id}
    plugin = args.plugin.expanduser().resolve()
    digest = hashlib.sha256()
    with plugin.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    source_hash = digest.hexdigest()

    records_scanned = 0
    subrecords_scanned = 0
    matching_subrecords = 0
    matching_records: set[tuple[str, str]] = set()
    for row in read_plugin(plugin, include_subrecords=True):
        records_scanned += 1
        for subrecord in row.get("subrecords", []):
            subrecords_scanned += 1
            raw = bytes.fromhex(subrecord["value_hex"])
            hits = [form_id for form_id, needle in needles.items() if needle in raw]
            if not hits:
                continue
            matching_subrecords += 1
            matching_records.add((row["signature"], row["file_form_id"]))
            print(json.dumps({
                "source_plugin": plugin.name,
                "source_sha256": source_hash,
                "record_signature": row["signature"],
                "record_form_id": row["file_form_id"],
                "record_origin_plugin": row["origin_plugin"],
                "record_editor_id": row["editor_id"],
                "record_offset": row["offset"],
                "record_flags": row["flags"],
                "subrecord_signature": subrecord["signature"],
                "matching_form_ids": hits,
                "subrecord_hex": subrecord["value_hex"],
            }, separators=(",", ":")))
    print(json.dumps({
        "scan_summary": True,
        "source_plugin": plugin.name,
        "source_sha256": source_hash,
        "record_count": records_scanned,
        "subrecord_count": subrecords_scanned,
        "matching_subrecord_count": matching_subrecords,
        "matching_record_count": len(matching_records),
        "searched_form_ids": list(needles),
    }, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
