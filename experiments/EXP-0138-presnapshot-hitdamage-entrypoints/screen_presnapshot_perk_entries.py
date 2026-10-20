#!/usr/bin/env python3
"""Screen official five-master PERK rows for HitData pre-snapshot selectors."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import _native_path
from tools.plugin_reader import read_plugin

PLUGINS = ("Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm")
SELECTORS = {0x1A, 0x1C, 0x00, 0x23, 0x24, 0x12, 0x01, 0x11, 0x02}
COMPARE = {0x0: "=", 0x2: "!=", 0x4: ">", 0x6: ">=", 0x8: "<", 0xA: "<="}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def decode_ctda(raw_hex: str) -> dict[str, object]:
    raw = bytes.fromhex(raw_hex)
    if len(raw) != 32:
        return {"raw_hex": raw_hex, "length": len(raw), "decoded": False}
    flags = raw[0]
    return {
        "raw_hex": raw_hex,
        "function_index": struct.unpack_from("<H", raw, 8)[0],
        "comparison": COMPARE.get((flags >> 4) & 0x0F, f"unknown:{(flags >> 4) & 0x0F}"),
        "comparison_float": None if (flags & 0x04) else struct.unpack_from("<f", raw, 4)[0],
        "or_flag": bool(flags & 1),
        "param1_u32": struct.unpack_from("<I", raw, 12)[0],
        "param2_u32": struct.unpack_from("<I", raw, 16)[0],
        "run_on": struct.unpack_from("<I", raw, 20)[0],
        "reference_form_id_u32": struct.unpack_from("<I", raw, 24)[0],
    }


def main() -> int:
    cfg = read_local_config(ROOT)
    configured = cfg.get("SKYRIM_DATA", "").strip()
    if not configured:
        raise SystemExit("SKYRIM_DATA is not configured")
    data_path = _native_path(configured)
    hashes: dict[str, str] = {}
    perk_count: Counter[str] = Counter()
    selected_perk_rows = []
    all_selector_counts: Counter[int] = Counter()
    handler_counts: Counter[int] = Counter()
    function_type_counts: Counter[str] = Counter()
    entrypoint_denominator = 0
    raw_reference_matches = []
    mgef_records_all = []

    for plugin_name in PLUGINS:
        plugin = data_path / plugin_name
        if not plugin.is_file():
            raise SystemExit(f"configured official master is missing: {plugin_name}")
        hashes[plugin_name] = digest(plugin)
        records = list(read_plugin(plugin, include_subrecords=True))
        mgef_records_all.extend(
            (plugin_name, record) for record in records if record.get("signature") == "MGEF"
        )
        for record in records:
            subrecords = record.get("subrecords", [])
            if record.get("signature") == "PERK":
                perk_count[plugin_name] += 1
                for index, subrecord in enumerate(subrecords):
                    if subrecord.get("signature") != "PRKE":
                        continue
                    end = next((i + 1 for i in range(index + 1, len(subrecords)) if subrecords[i]["signature"] == "PRKF"), len(subrecords))
                    entry = subrecords[index:end]
                    if not bytes.fromhex(subrecord["value_hex"]) or bytes.fromhex(subrecord["value_hex"])[0] != 2:
                        continue
                    data_sub = next((item for item in entry if item.get("signature") == "DATA"), None)
                    if data_sub is None:
                        continue
                    data = bytes.fromhex(data_sub["value_hex"])
                    if not data:
                        continue
                    entrypoint_denominator += 1
                    selector = data[0]
                    all_selector_counts[selector] += 1
                    if selector not in SELECTORS:
                        continue
                    handler = data[1] if len(data) > 1 else None
                    if handler is not None:
                        handler_counts[handler] += 1
                    epft_sub = next((item for item in entry if item.get("signature") == "EPFT"), None)
                    epfd_sub = next((item for item in entry if item.get("signature") == "EPFD"), None)
                    epft = None if epft_sub is None else epft_sub["value_hex"]
                    epfd_hex = None if epfd_sub is None else epfd_sub["value_hex"]
                    function_type_counts[str(epft)] += 1
                    epfd_float = None
                    if epfd_hex is not None:
                        raw_epfd = bytes.fromhex(epfd_hex)
                        if len(raw_epfd) == 4:
                            epfd_float = struct.unpack("<f", raw_epfd)[0]
                    selected_perk_rows.append({
                        "plugin": plugin_name,
                        "file_form_id": record["file_form_id"],
                        "local_form_id": record.get("local_form_id"),
                        "editor_id": record.get("editor_id"),
                        "entry_header_hex": subrecord["value_hex"],
                        "DATA_hex": data.hex(),
                        "selector_id": selector,
                        "handler_id_DATA_byte_1": handler,
                        "EPFT_hex": epft,
                        "EPFD_hex": epfd_hex,
                        "EPFD_float_if_4_bytes": epfd_float,
                        "CTDAs": [decode_ctda(item["value_hex"]) for item in entry if item.get("signature") == "CTDA"],
                        "entry_subrecords": [{"signature": item["signature"], "value_hex": item["value_hex"]} for item in entry],
                    })


    needles = {
        row["file_form_id"]: bytes.fromhex(row["file_form_id"])[::-1]
        for row in selected_perk_rows if row["file_form_id"]
    }
    for plugin_name, record in mgef_records_all:
        for sub in record.get("subrecords", []):
            blob = bytes.fromhex(sub["value_hex"])
            found = [form_id for form_id, needle in needles.items() if needle in blob]
            if found:
                raw_reference_matches.append({
                    "source_plugin": plugin_name,
                    "mgef_file_form_id": record.get("file_form_id"),
                    "mgef_editor_id": record.get("editor_id"),
                    "subrecord_signature": sub.get("signature"),
                    "matching_perk_ids": found,
                    "raw_subrecord_hex": sub["value_hex"],
                })

    selected_counts = Counter(row["selector_id"] for row in selected_perk_rows)
    result = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "Configured official five masters, read-only direct TES4 parser; source-file records only, not active profile winners.",
        "plugins": list(PLUGINS),
        "plugin_sha256": hashes,
        "coverage": {
            "perk_record_count_by_plugin": dict(perk_count),
            "all_PERK_entrypoint_DATA_rows": entrypoint_denominator,
            "all_selector_counts": {f"0x{key:02X}": value for key, value in sorted(all_selector_counts.items())},
            "selected_selector_counts": {f"0x{key:02X}": selected_counts.get(key, 0) for key in sorted(SELECTORS)},
            "selected_rows_total": len(selected_perk_rows),
            "handler_id_counts_DATA_byte_1": dict(handler_counts),
            "EPFT_hex_counts": dict(function_type_counts),
            "profile_winner_resolution": False,
            "runtime_behavior_tested": False,
        },
        "selected_selector_values": [f"0x{value:02X}" for value in sorted(SELECTORS)],
        "selected_PERK_rows": selected_perk_rows,
        "raw_MGEF_subrecord_reference_candidates": raw_reference_matches,
        "reference_scan_limit": "Exact raw little-endian PERK file FormID bytes in MGEF subrecords; candidate linkage only, not semantic field decoding or active effect application.",
    }
    target = ROOT / ".local/alignment/transactions/TX-20261020-0010/q91/presnapshot-perk-screen.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact": target.relative_to(ROOT).as_posix(),
        "sha256": digest(target),
        "plugin_sha256": hashes,
        "coverage": result["coverage"],
        "matching_MGEF_candidate_count": len(raw_reference_matches),
        "zero_or_nonpositive_EPFD_rows": [
            {"plugin": row["plugin"], "form_id": row["file_form_id"], "editor_id": row["editor_id"], "selector": f"0x{row['selector_id']:02X}", "handler": row["handler_id_DATA_byte_1"], "EPFT": row["EPFT_hex"], "EPFD": row["EPFD_float_if_4_bytes"], "CTDA_count": len(row["CTDAs"])}
            for row in selected_perk_rows if row["EPFD_float_if_4_bytes"] is not None and row["EPFD_float_if_4_bytes"] <= 0.0
        ],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
