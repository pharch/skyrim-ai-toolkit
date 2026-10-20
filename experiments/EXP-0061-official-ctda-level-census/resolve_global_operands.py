#!/usr/bin/env python3
"""Resolve winning GLOB operands referenced by QUST/PACK GetLevel CTDAs."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import REQUIRED_AE_MASTERS, _native_path
from tools.plugin_reader import read_plugin, resolve_record_winner


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transaction-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"TX-[0-9]{8}-[0-9]{4}", args.transaction_id):
        parser.error("transaction id has an invalid format")
    base = ROOT / ".local/alignment/transactions" / args.transaction_id
    capture = json.loads((base / "EV-0321-getlevel-census.json").read_text(encoding="utf-8"))
    winner_result = json.loads((base / "EV-0321-official-winner-resolution.json").read_text(encoding="utf-8"))
    expected_hashes = {row["plugin"]: row["sha256"] for row in capture["source_files"]}
    targets = sorted({
        row["condition"]["operand_global"]
        for record in winner_result["winning_records"]
        if record["signature"] in {"QUST", "PACK"}
        for row in record["getlevel_conditions"]
        if row["condition"].get("use_global") and row["condition"].get("operand_global")
    })
    if not targets:
        raise RuntimeError("no GetLevel global operands were captured")
    config = read_local_config(ROOT)
    data_value = config.get("SKYRIM_DATA", "").strip()
    if not data_value:
        raise RuntimeError("configured official Data directory is unavailable")
    data_root = _native_path(data_value)
    copies: dict[str, list[dict]] = {form_id: [] for form_id in targets}

    for plugin in REQUIRED_AE_MASTERS:
        path = data_root / plugin
        if not path.is_file() or digest(path) != expected_hashes.get(plugin):
            raise RuntimeError(f"official source identity changed since EV-0321: {plugin}")
        for record in read_plugin(path, "GLOB", include_subrecords=True):
            if record["file_form_id"] not in copies:
                continue
            values = {
                sub["signature"]: bytes.fromhex(sub["value_hex"])
                for sub in record.get("subrecords", [])
            }
            raw_float = values.get("FLTV")
            copies[record["file_form_id"]].append({
                "signature": "GLOB",
                "plugin": plugin,
                "origin_plugin": record["origin_plugin"],
                "local_form_id": record["local_form_id"],
                "file_form_id": record["file_form_id"],
                "editor_id": record["editor_id"],
                "value": struct.unpack_from("<f", raw_float)[0] if raw_float and len(raw_float) == 4 else None,
                "value_raw_hex": raw_float.hex() if raw_float else None,
            })

    resolved = []
    for form_id in targets:
        candidates = copies[form_id]
        if not candidates:
            resolved.append({"form_id": form_id, "found": False, "copies": []})
            continue
        winner = resolve_record_winner(candidates, list(REQUIRED_AE_MASTERS))
        resolved.append({
            "form_id": form_id,
            "found": True,
            "winning_record": winner,
            "copies": [
                {"plugin": row["plugin"], "editor_id": row["editor_id"], "value": row["value"]}
                for row in sorted(candidates, key=lambda row: REQUIRED_AE_MASTERS.index(row["plugin"]))
            ],
        })
    result = {
        "capture_id": "EV-0321-getlevel-global-operand-resolution",
        "source_capture": "EV-0321-getlevel-census.json",
        "order_scope": "Fixed official-master source order only, not an active-profile winner.",
        "resolved_operands": resolved,
    }
    out = base / "EV-0321-global-operands.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
