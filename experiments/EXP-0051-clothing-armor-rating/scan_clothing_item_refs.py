#!/usr/bin/env python3
"""Candidate-scan official records for direct references to Clothing ARMO items."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import _native_path
from tools.plugin_reader import PluginFormatError, read_plugin

PLUGINS = ("Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--form-id", nargs="+", default=["00013105"], help="full eight-digit FormID(s)")
    args = parser.parse_args()
    form_ids = [value.upper() for value in args.form_id]
    if any(len(value) != 8 or any(char not in "0123456789ABCDEF" for char in value) for value in form_ids):
        parser.error("each FormID must contain exactly eight hexadecimal digits")
    needles = {value: bytes.fromhex(value)[::-1] for value in form_ids}
    config = read_local_config(ROOT)
    configured = config.get("SKYRIM_DATA", "").strip()
    if not configured:
        raise RuntimeError("SKYRIM_DATA is not configured")
    data_root = _native_path(configured)
    if not data_root.is_absolute():
        data_root = ROOT / data_root
    if not data_root.is_dir():
        raise RuntimeError("configured official data directory is inaccessible")

    summaries = []
    for plugin in PLUGINS:
        path = data_root / plugin
        if not path.is_file():
            raise RuntimeError(f"configured official source is unavailable: {plugin}")
        source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        record_count = subrecord_count = hit_subrecords = 0
        matching_records = set()
        for row in read_plugin(path, include_subrecords=True):
            record_count += 1
            for subrecord in row.get("subrecords", []):
                subrecord_count += 1
                raw = bytes.fromhex(subrecord["value_hex"])
                found = [form_id for form_id, needle in needles.items() if needle in raw]
                if not found:
                    continue
                hit_subrecords += 1
                matching_records.add((row["signature"], row["file_form_id"]))
                print(json.dumps({
                    "source_plugin": plugin,
                    "source_sha256": source_hash,
                    "record_signature": row["signature"],
                    "record_form_id": row["file_form_id"],
                    "record_origin_plugin": row["origin_plugin"],
                    "record_editor_id": row["editor_id"],
                    "subrecord_signature": subrecord["signature"],
                    "matching_form_ids": found,
                    "subrecord_hex": subrecord["value_hex"],
                }, separators=(",", ":")))
        summaries.append({
            "source_plugin": plugin,
            "source_sha256": source_hash,
            "record_count": record_count,
            "subrecord_count": subrecord_count,
            "matching_subrecord_count": hit_subrecords,
            "matching_record_count": len(matching_records),
        })
    print(json.dumps({"scan_summary": True, "searched_form_ids": form_ids, "sources": summaries}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, PluginFormatError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
