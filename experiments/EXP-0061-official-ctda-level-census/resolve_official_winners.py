#!/usr/bin/env python3
"""Resolve GetLevel candidate records in the fixed official-master order."""
from __future__ import annotations

from collections import Counter, defaultdict
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
from tools.ae_target import REQUIRED_AE_MASTERS, _native_path
from tools.plugin_reader import read_plugin, resolve_record_winner

DECODER_PATH = ROOT / "experiments/EXP-0052-da02-level-gate/summarize_da02_initial.py"


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
    target_keys = {
        (row["record_signature"], row["record_origin_plugin"], row["record_form_id"][-6:])
        for row in capture["getlevel_hits"]
    }
    config = read_local_config(ROOT)
    data_value = config.get("SKYRIM_DATA", "").strip()
    if not data_value:
        raise RuntimeError("configured official Data directory is unavailable")
    data_root = _native_path(data_value)
    decode_ctda = load_decoder()
    candidate_rows: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    parsed_plugin_hashes = {}

    for plugin in REQUIRED_AE_MASTERS:
        path = data_root / plugin
        if not path.is_file() or digest(path) != expected_hashes.get(plugin):
            raise RuntimeError(f"official source identity changed since EV-0321: {plugin}")
        parsed_plugin_hashes[plugin] = expected_hashes[plugin]
        for record in read_plugin(path, include_subrecords=True):
            key = (record["signature"], record["origin_plugin"], record["local_form_id"])
            if key not in target_keys:
                continue
            conditions = []
            ctda_count = 0
            for index, subrecord in enumerate(record.get("subrecords", [])):
                if subrecord["signature"] != "CTDA":
                    continue
                ctda_count += 1
                raw = bytes.fromhex(subrecord["value_hex"])
                decoded = decode_ctda(raw) if len(raw) == 32 else {"length": len(raw), "raw": raw.hex()}
                if decoded.get("function_index") == 80:
                    conditions.append({"subrecord_index": index, "condition": decoded})
            candidate_rows[key].append({
                "signature": record["signature"],
                "plugin": plugin,
                "origin_plugin": record["origin_plugin"],
                "local_form_id": record["local_form_id"],
                "file_form_id": record["file_form_id"],
                "editor_id": record["editor_id"],
                "record_offset": record["offset"],
                "ctda_count": ctda_count,
                "getlevel_conditions": conditions,
            })

    missing_keys = target_keys - set(candidate_rows)
    if missing_keys:
        raise RuntimeError(f"captured candidate records not found in official masters: {sorted(missing_keys)}")

    winners = []
    superseded = []
    for key, candidates in sorted(candidate_rows.items()):
        winner = resolve_record_winner(candidates, list(REQUIRED_AE_MASTERS))
        kept = {**winner, "source_copies": [
            {
                "plugin": row["plugin"],
                "file_form_id": row["file_form_id"],
                "editor_id": row["editor_id"],
                "getlevel_condition_count": len(row["getlevel_conditions"]),
            }
            for row in sorted(candidates, key=lambda row: REQUIRED_AE_MASTERS.index(row["plugin"]))
        ]}
        if winner["getlevel_conditions"]:
            winners.append(kept)
        elif any(row["getlevel_conditions"] for row in candidates):
            superseded.append(kept)

    by_signature = Counter(row["signature"] for row in winners for _ in row["getlevel_conditions"])
    by_winner_plugin = Counter(row["plugin"] for row in winners for _ in row["getlevel_conditions"])
    result = {
        "capture_id": "EV-0321-official-master-winner-resolution",
        "source_capture": "EV-0321-getlevel-census.json",
        "order_scope": "Fixed official-master source order only: Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm, Dragonborn.esm. Not an active-profile winner.",
        "parser": "tools.plugin_reader.read_plugin and resolve_record_winner",
        "source_identity_rechecked": parsed_plugin_hashes,
        "physical_condition_count": len(capture["getlevel_hits"]),
        "physical_logical_record_key_count": len(target_keys),
        "candidate_key_count": len(candidate_rows),
        "winning_condition_count": sum(by_signature.values()),
        "winning_record_count": len(winners),
        "winning_conditions_by_signature": dict(sorted(by_signature.items())),
        "winning_conditions_by_source_plugin": dict(sorted(by_winner_plugin.items())),
        "superseded_condition_record_count": len(superseded),
        "winning_records": winners,
        "superseded_records_without_getlevel": superseded,
    }
    out_path = base / "EV-0321-official-winner-resolution.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        key: result[key] for key in (
            "source_identity_rechecked", "physical_condition_count", "physical_logical_record_key_count",
            "candidate_key_count", "winning_condition_count", "winning_record_count",
            "winning_conditions_by_signature", "winning_conditions_by_source_plugin",
            "superseded_condition_record_count",
        )
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
