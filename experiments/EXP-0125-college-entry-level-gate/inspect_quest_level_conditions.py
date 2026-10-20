#!/usr/bin/env python3
"""Summarize captured College QUST CTDAs and cross-check the EV-0321 GetLevel census."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
MASTER_SHA256 = "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107"
EXPECTED = {"MG01": "0001F251", "MG02": "0001F252"}
DECODER_PATH = ROOT / "experiments/EXP-0052-da02-level-gate/summarize_da02_initial.py"


def load_decoder():
    spec = importlib.util.spec_from_file_location("exp0052_ctda_decoder", DECODER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("existing EXP-0052 CTDA decoder is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decode_ctda


def local_input(root: Path, value: Path) -> Path:
    path = value if value.is_absolute() else root / value
    path = path.resolve()
    try:
        path.relative_to((root / ".local").resolve())
    except ValueError as exc:
        raise ValueError("capture input must remain below ignored .local/") from exc
    if not path.is_file():
        raise FileNotFoundError(f"capture is unavailable: {path.name}")
    return path


def read_jsonl_capture(path: Path) -> tuple[list[dict], str]:
    raw = path.read_bytes()
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    return rows, hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mg01_capture", type=Path)
    parser.add_argument("mg02_capture", type=Path)
    parser.add_argument("--getlevel-census", required=True, type=Path)
    args = parser.parse_args()
    decode_ctda = load_decoder()
    captures = {
        "MG01": local_input(ROOT, args.mg01_capture),
        "MG02": local_input(ROOT, args.mg02_capture),
    }
    records = []
    for expected_editor_id, path in captures.items():
        rows, digest = read_jsonl_capture(path)
        matches = [
            row for row in rows
            if row.get("signature") == "QUST" and row.get("editor_id") == expected_editor_id
        ]
        if len(matches) != 1:
            raise ValueError(f"expected one exact {expected_editor_id} QUST in {path.name}; found {len(matches)}")
        record = matches[0]
        if record.get("plugin") != "Skyrim.esm" or record.get("file_form_id") != EXPECTED[expected_editor_id]:
            raise ValueError(f"unexpected source identity for {expected_editor_id}: {record.get('plugin')} {record.get('file_form_id')}")
        conditions = []
        counts: Counter[str] = Counter()
        for index, field in enumerate(record.get("subrecords", [])):
            if field.get("signature") != "CTDA":
                continue
            decoded = decode_ctda(bytes.fromhex(field["hex"]))
            name = decoded.get("function_name", f"unknown:{decoded.get('function_index')}")
            counts[name] += 1
            if decoded.get("function_index") == 80:
                conditions.append({"subrecord_index": index, **decoded})
        records.append({
            "editor_id": expected_editor_id,
            "form_id": record["file_form_id"],
            "plugin": record["plugin"],
            "plugin_sha256": MASTER_SHA256,
            "capture_file": path.name,
            "capture_sha256": digest,
            "ctda_count": sum(counts.values()),
            "ctda_function_counts": dict(sorted(counts.items())),
            "getlevel_conditions": conditions,
            "scope_limit": "Direct source QUST record only; CTDA placement is retained by subrecord index. Dialogue, Story Manager, door, physical access and runtime paths are not implied by this record query.",
        })

    census_path = local_input(ROOT, args.getlevel_census)
    census_raw = census_path.read_bytes()
    census = json.loads(census_raw)
    if not census.get("scan_complete") or not census.get("condition_census_complete"):
        raise ValueError("EV-0321 GetLevel census is incomplete")
    census_records = {row.get("record_form_id") for row in census.get("getlevel_hits", [])
                      if row.get("record_signature") == "QUST" and row.get("source_plugin") == "Skyrim.esm"}
    expected_ids = set(EXPECTED.values())
    intersect = sorted(expected_ids & census_records)
    result = {
        "source_master": "Skyrim.esm",
        "source_master_sha256": MASTER_SHA256,
        "record_captures": records,
        "getlevel_census": {
            "evidence_id": "EV-0321",
            "capture_file": census_path.name,
            "capture_sha256": hashlib.sha256(census_raw).hexdigest(),
            "target_product_version": census.get("target_identity", {}).get("product_version"),
            "target_sha256": census.get("target_identity", {}).get("sha256"),
            "scan_complete": census.get("scan_complete"),
            "condition_census_complete": census.get("condition_census_complete"),
            "ctda_length_anomaly_count": len(census.get("ctda_length_anomalies", [])),
            "getlevel_qust_count": sum(1 for row in census.get("getlevel_hits", []) if row.get("record_signature") == "QUST"),
            "target_quest_formids_with_getlevel": intersect,
            "scope_limit": "Complete GetLevel CTDA census over the exact official masters; does not rule out other condition functions, non-CTDA logic, or physical/runtime gates.",
        },
        "read_only": True,
        "profile_winner_resolved": False,
        "runtime_tested": False,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
