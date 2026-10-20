#!/usr/bin/env python3
"""Screen every record/subrecord in prepared official masters for DA13 FormID bytes.

This is candidate finding only. It does not resolve record semantics, winning
overrides, active-profile order, dynamic lookups, or PEX calls in uninspected
archives.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from pathlib import PureWindowsPath
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.plugin_reader import read_plugin

DEFAULT_IDS = ["0008998D", "000BEDEC", "000BED92", "000BEDAF"]
MASTERS = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def scan_plugin(path: Path, needles: dict[str, bytes]) -> None:
    source_sha = digest(path)
    records = 0
    subrecords = 0
    hits = 0
    matching_records: set[tuple[str, str]] = set()
    for row in read_plugin(path, include_subrecords=True):
        records += 1
        for subrecord in row.get("subrecords", []):
            subrecords += 1
            raw = bytes.fromhex(subrecord["value_hex"])
            found = [fid for fid, needle in needles.items() if needle in raw]
            if not found:
                continue
            hits += 1
            matching_records.add((row["signature"], row["file_form_id"]))
            print(json.dumps({
                "source_plugin": path.name,
                "source_sha256": source_sha,
                "record_signature": row["signature"],
                "record_form_id": row["file_form_id"],
                "record_origin_plugin": row["origin_plugin"],
                "record_editor_id": row["editor_id"],
                "record_offset": row["offset"],
                "subrecord_signature": subrecord["signature"],
                "matching_form_ids": found,
                "subrecord_hex": subrecord["value_hex"],
            }, separators=(",", ":")))
    print(json.dumps({
        "scan_summary": True,
        "source_plugin": path.name,
        "source_sha256": source_sha,
        "record_count": records,
        "subrecord_count": subrecords,
        "matching_subrecord_count": hits,
        "matching_record_count": len(matching_records),
        "searched_form_ids": list(needles),
    }, separators=(",", ":")))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--form-id", nargs="+", default=DEFAULT_IDS, help="full 8-digit FormID(s)")
    args = parser.parse_args()
    needles = {fid.upper(): bytes.fromhex(fid)[::-1] for fid in args.form_id}
    if any(len(fid) != 8 for fid in needles):
        parser.error("each FormID must contain exactly eight hexadecimal digits")
    config = read_local_config(ROOT)
    configured_data = config.get("SKYRIM_DATA", "").strip()
    windows_data = PureWindowsPath(configured_data)
    if os.name != "nt" and windows_data.drive and len(windows_data.drive) == 2 and windows_data.drive[1] == ":":
        data_root = Path("/mnt") / windows_data.drive[0].lower() / Path(*windows_data.parts[1:])
    else:
        data_root = Path(configured_data).expanduser()
    if not data_root.is_dir():
        parser.error("SKYRIM_DATA in config/local.env is not an accessible directory")
    for master in MASTERS:
        path = data_root / master
        if not path.is_file():
            parser.error(f"prepared official master is missing: {master}")
        scan_plugin(path, needles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
