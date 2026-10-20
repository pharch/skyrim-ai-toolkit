#!/usr/bin/env python3
"""Join QUST/PACK GetLevel CTDAs to surrounding source-record structure."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import _native_path
from tools.plugin_reader import read_plugin

DECODER_PATH = ROOT / "experiments/EXP-0052-da02-level-gate/summarize_da02_initial.py"
STRUCTURAL = {"INDX", "QSDT", "CNAM", "TNAM", "NEXT", "ALST", "ALLS", "ALID", "CTDA", "SCHR", "VMAD"}


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def load_decoder():
    spec = importlib.util.spec_from_file_location("exp0052_ctda_decoder", DECODER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("existing EXP-0052 CTDA decoder is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decode_ctda


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transaction-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"TX-[0-9]{8}-[0-9]{4}", args.transaction_id):
        parser.error("transaction id has an invalid format")
    base = ROOT / ".local/alignment/transactions" / args.transaction_id
    capture = json.loads((base / "EV-0321-getlevel-census.json").read_text(encoding="utf-8"))
    if not capture.get("condition_census_complete"):
        raise RuntimeError("complete five-master condition census is required")

    expected_hashes = {row["plugin"]: row["sha256"] for row in capture["source_files"]}
    selected: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for hit in capture["getlevel_hits"]:
        if hit["record_signature"] in {"QUST", "PACK"}:
            selected[hit["source_plugin"]][hit["record_form_id"]].append(hit)
    config = read_local_config(ROOT)
    data_value = config.get("SKYRIM_DATA", "").strip()
    if not data_value:
        raise RuntimeError("configured official Data directory is unavailable")
    data_root = _native_path(data_value)
    decode_ctda = load_decoder()
    joined = []
    for plugin, targets in sorted(selected.items()):
        path = data_root / plugin
        if not path.is_file() or digest(path) != expected_hashes[plugin]:
            raise RuntimeError(f"official source identity changed since EV-0321: {plugin}")
        found_ids: set[str] = set()
        for record in read_plugin(path, include_subrecords=True):
            form_id = record["file_form_id"]
            if form_id not in targets or record["signature"] not in {"QUST", "PACK"}:
                continue
            found_ids.add(form_id)
            fields = record.get("subrecords", [])
            getlevel_rows = []
            for index, field in enumerate(fields):
                if field["signature"] != "CTDA":
                    continue
                raw = bytes.fromhex(field["value_hex"])
                decoded = decode_ctda(raw) if len(raw) == 32 else {"length": len(raw), "raw": raw.hex()}
                if decoded.get("function_index") != 80:
                    continue
                left = fields[max(0, index - 6):index]
                right = fields[index + 1:index + 7]
                getlevel_rows.append({
                    "subrecord_index": index,
                    "condition": decoded,
                    "previous_fields": [row["signature"] for row in left],
                    "next_fields": [row["signature"] for row in right],
                })
            joined.append({
                "plugin": plugin,
                "source_sha256": expected_hashes[plugin],
                "record_signature": record["signature"],
                "form_id": form_id,
                "origin_plugin": record["origin_plugin"],
                "editor_id": record["editor_id"],
                "record_offset": record["offset"],
                "subrecord_signature_sequence": [row["signature"] for row in fields],
                "structural_markers": [
                    {"index": index, "signature": row["signature"], "length": row["length"], "value_hex": row["value_hex"][:128]}
                    for index, row in enumerate(fields) if row["signature"] in STRUCTURAL
                ],
                "getlevel_conditions": getlevel_rows,
            })
        missing = set(targets) - found_ids
        if missing:
            raise RuntimeError(f"captured progression records were not re-found in {plugin}: {sorted(missing)}")

    output = {
        "capture_id": "EV-0321-progression-record-join",
        "source_capture": "EV-0321-getlevel-census.json",
        "source_identity_rechecked": True,
        "joined_record_count": len(joined),
        "target_condition_count": sum(len(row["getlevel_conditions"]) for row in joined),
        "records": sorted(joined, key=lambda row: (row["plugin"], row["record_signature"], row["form_id"])),
    }
    out_path = base / "EV-0321-progression-record-join.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "source_identity_rechecked": output["source_identity_rechecked"],
        "joined_record_count": output["joined_record_count"],
        "target_condition_count": output["target_condition_count"],
        "records": [
            {
                "plugin": row["plugin"],
                "signature": row["record_signature"],
                "form_id": row["form_id"],
                "editor_id": row["editor_id"],
                "getlevel_condition_count": len(row["getlevel_conditions"]),
                "getlevel_positions": [entry["subrecord_index"] for entry in row["getlevel_conditions"]],
                "markers": row["structural_markers"],
                "conditions": row["getlevel_conditions"],
            }
            for row in sorted(joined, key=lambda row: (row["plugin"], row["record_signature"], row["form_id"]))
        ],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
