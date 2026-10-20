#!/usr/bin/env python3
"""Capture all GetLevel CTDA records across the five official AE masters."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
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
from tools.ae_target import REQUIRED_AE_MASTERS, _native_path, read_executable_version
from tools.plugin_reader import PluginFormatError, read_plugin

EXPECTED_VERSION = "1.6.1170.0"
EXPECTED_EXE_SHA256 = "c434208894f07f604b852f29b8edc3a58c4de63de783373733e72b2b73f33be9"
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transaction-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"TX-[0-9]{8}-[0-9]{4}", args.transaction_id):
        parser.error("transaction id has an invalid format")

    config = read_local_config(ROOT)
    exe_value = config.get("SKYRIM_EXE_PATH", "").strip()
    data_value = config.get("SKYRIM_DATA", "").strip()
    if not exe_value or not data_value:
        raise RuntimeError("configured Skyrim executable or Data directory is unavailable")
    exe_path = _native_path(exe_value)
    data_root = _native_path(data_value)
    if not exe_path.is_file() or not data_root.is_dir():
        raise RuntimeError("configured Skyrim target is inaccessible")

    version = read_executable_version(exe_path)
    exe_sha256 = digest(exe_path)
    if version != EXPECTED_VERSION or exe_sha256 != EXPECTED_EXE_SHA256:
        raise RuntimeError("installed executable does not match the EV-0109 Steam AE identity")

    decode_ctda = load_decoder()
    output_dir = ROOT / ".local/alignment/transactions" / args.transaction_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "EV-0321-getlevel-census.json"
    capture = {
        "capture_id": "EV-0321-source-capture",
        "transaction_id": args.transaction_id,
        "captured_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "target_identity": {
            "distribution": "Steam",
            "program": "SkyrimSE.exe",
            "product_version": version,
            "sha256": exe_sha256,
            "expected_evidence": "EV-0109",
        },
        "scope": "The five official masters only; source-file census, not active-order winner selection.",
        "parser": "tools.plugin_reader.read_plugin; read-only mmap traversal including compressed-record subrecords.",
        "decoder": {
            "source": "experiments/EXP-0052-da02-level-gate/summarize_da02_initial.py::decode_ctda",
            "sha256": digest(DECODER_PATH),
            "function_index": 80,
            "function_name": "GetLevel",
        },
        "scan_complete": False,
        "condition_census_complete": False,
        "ctda_length_anomalies": [],
        "getlevel_hits": [],
        "source_files": [],
    }

    def checkpoint() -> None:
        output_path.write_text(json.dumps(capture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    checkpoint()
    try:
        for master in REQUIRED_AE_MASTERS:
            path = data_root / master
            if not path.is_file():
                raise FileNotFoundError(f"required official master is unavailable: {master}")
            file_info = {
                "plugin": master,
                "sha256": digest(path),
                "size_bytes": path.stat().st_size,
                "parse_complete": False,
                "record_count": 0,
                "subrecord_count": 0,
                "ctda_count": 0,
                "signature_counts": {},
                "ctda_length_counts": {},
            }
            capture["source_files"].append(file_info)
            signatures: Counter[str] = Counter()
            ctda_lengths: Counter[int] = Counter()
            for record in read_plugin(path, include_subrecords=True):
                file_info["record_count"] += 1
                signatures[record["signature"]] += 1
                for subrecord_index, subrecord in enumerate(record.get("subrecords", [])):
                    file_info["subrecord_count"] += 1
                    if subrecord["signature"] != "CTDA":
                        continue
                    file_info["ctda_count"] += 1
                    raw = bytes.fromhex(subrecord["value_hex"])
                    ctda_lengths[len(raw)] += 1
                    provenance = {
                        "source_plugin": master,
                        "source_sha256": file_info["sha256"],
                        "record_signature": record["signature"],
                        "record_form_id": record["file_form_id"],
                        "record_origin_plugin": record["origin_plugin"],
                        "record_editor_id": record["editor_id"],
                        "record_offset": record["offset"],
                        "subrecord_index": subrecord_index,
                    }
                    if len(raw) != 32:
                        capture["ctda_length_anomalies"].append({
                            **provenance,
                            "length": len(raw),
                            "raw": raw.hex(),
                            "function_index_interpretation": "unknown; existing decoder requires 32 bytes",
                        })
                        continue
                    decoded = decode_ctda(raw)
                    if decoded.get("function_index") == 80:
                        capture["getlevel_hits"].append({**provenance, "condition": decoded})
            file_info["signature_counts"] = dict(sorted(signatures.items()))
            file_info["ctda_length_counts"] = {str(length): count for length, count in sorted(ctda_lengths.items())}
            file_info["parse_complete"] = True
            checkpoint()

        capture["scan_complete"] = all(row["parse_complete"] for row in capture["source_files"])
        capture["condition_census_complete"] = (
            capture["scan_complete"]
            and len(capture["source_files"]) == len(REQUIRED_AE_MASTERS)
            and not capture["ctda_length_anomalies"]
        )
        capture["summary"] = {
            "master_count": len(capture["source_files"]),
            "record_count": sum(row["record_count"] for row in capture["source_files"]),
            "ctda_count": sum(row["ctda_count"] for row in capture["source_files"]),
            "getlevel_hit_count": len(capture["getlevel_hits"]),
            "ctda_length_anomaly_count": len(capture["ctda_length_anomalies"]),
        }
        checkpoint()
    except (OSError, PluginFormatError, ValueError, RuntimeError) as exc:
        capture["error"] = {"type": type(exc).__name__, "message": str(exc)}
        checkpoint()
        print(json.dumps({"ok": False, "capture": "EV-0321-getlevel-census.json", "error": capture["error"]}, ensure_ascii=False), file=sys.stderr)
        return 2

    print(json.dumps({
        "ok": capture["scan_complete"],
        "condition_census_complete": capture["condition_census_complete"],
        "capture": "EV-0321-getlevel-census.json",
        "target_product_version": version,
        "target_sha256": exe_sha256,
        "summary": capture["summary"],
        "per_master": [
            {
                "plugin": row["plugin"],
                "sha256": row["sha256"],
                "record_count": row["record_count"],
                "ctda_count": row["ctda_count"],
                "parse_complete": row["parse_complete"],
            }
            for row in capture["source_files"]
        ],
    }, indent=2))
    return 0 if capture["condition_census_complete"] else 3


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, PluginFormatError, ValueError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
