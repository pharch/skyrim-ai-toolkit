#!/usr/bin/env python3
"""Screen exact official-master subrecords for the College Arch-Mage key."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / ".local/xedit-data/official-ae-v1"
BASELINE = ROOT / ".local/alignment/transactions/TX-20261017-0007/EV-0321-getlevel-census.json"
KEY_FORM_ID = 0x000C5140
PLUGINS = ("Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.plugin_reader import read_plugin


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    if not baseline.get("scan_complete") or not baseline.get("condition_census_complete"):
        raise ValueError("the complete EV-0321 source manifest is required")
    expected_hashes = {row["plugin"]: row["sha256"] for row in baseline["source_files"]}
    target = KEY_FORM_ID.to_bytes(4, "little")
    source_files = []
    matches = []
    raw_counts: dict[str, int] = {}
    record_counts: dict[str, int] = {}
    for plugin in PLUGINS:
        path = SOURCE_DIR / plugin
        actual_hash = digest(path)
        if actual_hash != expected_hashes.get(plugin):
            raise ValueError(f"official source hash differs from EV-0321: {plugin}")
        source_files.append({"plugin": plugin, "sha256": actual_hash, "size_bytes": path.stat().st_size})
        record_count = 0
        for record in read_plugin(path, include_subrecords=True):
            record_count += 1
            for subrecord in record.get("subrecords", []):
                raw = bytes.fromhex(subrecord["value_hex"])
                occurrences = raw.count(target)
                if not occurrences:
                    continue
                signature = subrecord["signature"]
                raw_counts[signature] = raw_counts.get(signature, 0) + occurrences
                matches.append({
                    "source_plugin": plugin,
                    "record_signature": record["signature"],
                    "record_form_id": record["file_form_id"],
                    "record_editor_id": record.get("editor_id"),
                    "subrecord_signature": signature,
                    "subrecord_hex": subrecord["value_hex"],
                    "byte_occurrence_count": occurrences,
                })
        record_counts[plugin] = record_count
    result = {
        "target": {"form_id": f"{KEY_FORM_ID:08X}", "editor_id": "CollegeArchMageKey"},
        "route": "Read-only exact five-master subrecord byte screen via tools.plugin_reader.read_plugin",
        "baseline_manifest": "EV-0321 complete exact-five-master source manifest",
        "source_files": source_files,
        "records_scanned": record_counts,
        "subrecord_byte_occurrences_by_signature": dict(sorted(raw_counts.items())),
        "match_count": len(matches),
        "matches": matches,
        "scope_limit": "Byte matches are candidates until their record field is interpreted. This does not resolve a profile winner, Papyrus/native dynamic writers, actual inventory state, key acquisition, or runtime lock behavior.",
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if not output.resolve().is_relative_to((ROOT / ".local").resolve()):
        raise ValueError("capture output must remain below ignored .local/")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "target": result["target"],
        "source_files": source_files,
        "records_scanned": record_counts,
        "subrecord_byte_occurrences_by_signature": result["subrecord_byte_occurrences_by_signature"],
        "match_count": len(matches),
        "matches": matches,
        "output": output.relative_to(ROOT).as_posix(),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
