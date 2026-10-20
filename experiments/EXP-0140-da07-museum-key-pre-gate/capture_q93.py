#!/usr/bin/env python3
"""Capture UESP leads and exact official-record sources for the DA07 key."""
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
from tools.ae_target import _native_path, assert_ae_target
from tools.plugin_reader import read_plugin
from tools.uesp.core import page as uesp_page

PLUGINS = ("Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm")
KEY_FORM = 0x000960F0
KEY_BYTES = struct.pack("<I", KEY_FORM)
TARGET_RECORDS = {
    ("KEYM", 0x000960F0),
    ("NPC_", 0x000240CC),
    ("ACHR", 0x000240CE),
    ("REFR", 0x000240CA),
    ("QUST", 0x000240B8),
    ("QUST", 0x00096FD7),
}
UESP_TITLES = (
    "Skyrim:Keys",
    "Skyrim:Pieces of the Past",
    "Skyrim:Silus Vesuius",
    "Skyrim:Silus Vesuius's House",
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _record_detail(row: dict) -> dict:
    subs = row.get("subrecords", [])
    return {
        "plugin": row["plugin"],
        "origin_plugin": row["origin_plugin"],
        "signature": row["signature"],
        "file_form_id": row["file_form_id"],
        "local_form_id": row["local_form_id"],
        "editor_id": row["editor_id"],
        "flags": row["flags"],
        "offset": row["offset"],
        "subrecords": subs,
    }


def _uesp_capture(database: Path, title: str) -> dict:
    result = uesp_page(database, title, raw=True)
    lines = str(result.get("content", "")).splitlines()
    if title == "Skyrim:Keys":
        needles = ("000960f0", "Silus Vesuius")
    elif title == "Skyrim:Pieces of the Past":
        needles = ("level 20", "at or above level 20", "museum")
    elif title == "Skyrim:Silus Vesuius":
        needles = ("|level=", "quest-related events", "key")
    else:
        needles = ("inaccessible until", "level 20", "key", "door")
    selected = [
        {"line": number, "text": line[:900]}
        for number, line in enumerate(lines, 1)
        if any(needle.casefold() in line.casefold() for needle in needles)
    ]
    return {
        "title": result.get("title"),
        "revision_id": result.get("revision_id"),
        "timestamp": result.get("timestamp"),
        "url": result.get("url"),
        "selected_lines": selected,
        "limits": "Local UESP export; secondary source, snapshot completeness unknown; a listed holder does not establish pre-gate inventory or in-game accessibility.",
    }


def main() -> int:
    config = read_local_config(ROOT)
    data_root = _native_path(config.get("SKYRIM_DATA", "").strip())
    target = assert_ae_target()
    if target.get("edition") != "AE" or int(str(target.get("version", "0")).split(".")[0]) != 1:
        raise SystemExit("configured target is not a verified AE 1.x runtime")
    if not data_root.is_dir():
        raise SystemExit("configured Skyrim Data directory is unavailable")

    plugin_hashes = {}
    key_reference_candidates = []
    records_by_id: dict[tuple[str, int], list[dict]] = {}
    signature_counts: dict[str, Counter[str]] = {name: Counter() for name in PLUGINS}
    for plugin in PLUGINS:
        path = data_root / plugin
        if not path.is_file():
            raise SystemExit(f"required official master is missing: {plugin}")
        plugin_hashes[plugin] = digest(path)
        for row in read_plugin(path, include_subrecords=True):
            signature_counts[plugin][row["signature"]] += 1
            local_form = int(row["local_form_id"], 16)
            if row["origin_plugin"] == "Skyrim.esm" and (row["signature"], local_form) in TARGET_RECORDS:
                records_by_id.setdefault((row["signature"], local_form), []).append(_record_detail(row))
            for sub_index, sub in enumerate(row.get("subrecords", [])):
                raw = bytes.fromhex(sub.get("value_hex", ""))
                start = 0
                while True:
                    offset = raw.find(KEY_BYTES, start)
                    if offset < 0:
                        break
                    key_reference_candidates.append({
                        "plugin": plugin,
                        "signature": row["signature"],
                        "local_form_id": row["local_form_id"],
                        "origin_plugin": row["origin_plugin"],
                        "editor_id": row["editor_id"],
                        "record_flags": row["flags"],
                        "subrecord": sub["signature"],
                        "subrecord_index": sub_index,
                        "subrecord_byte_offset": offset,
                        "subrecord_length": sub["length"],
                        "raw_value_hex": sub["value_hex"] if len(raw) <= 65536 else None,
                        "subrecord_sha256": hashlib.sha256(raw).hexdigest(),
                        "context_hex": raw[max(0, offset - 24):offset + 28].hex(),
                        "candidate_field_family": sub["signature"] in {"CNTO", "LVLO", "NAME", "XESP", "XLOC", "VMAD"},
                    })
                    start = offset + 1
        print(json.dumps({"screened_plugin": plugin, "record_count": sum(signature_counts[plugin].values()), "raw_key_candidates_so_far": len(key_reference_candidates)}), flush=True)

    exact_records = {
        f"{signature}:{form_id:08X}": records_by_id.get((signature, form_id), [])
        for signature, form_id in sorted(TARGET_RECORDS)
    }
    database = ROOT / ".local/uesp.sqlite3"
    uesp = [_uesp_capture(database, title) for title in UESP_TITLES]
    if not any(row.get("revision_id") for row in uesp):
        raise SystemExit("local UESP page capture failed")

    result = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "transaction": "TX-20261020-0012",
        "frontier": "Q-0093",
        "target": {
            "edition": target.get("edition"),
            "runtime": target.get("version"),
            "executable_sha256": hashlib.sha256(Path(target["executable"]).read_bytes()).hexdigest(),
            "full_active_order_verified": False,
        },
        "record_scope": {
            "plugins": list(PLUGINS),
            "plugin_sha256": plugin_hashes,
            "record_count_by_plugin": {name: sum(counts.values()) for name, counts in signature_counts.items()},
            "target_records": exact_records,
            "key_formid_little_endian_raw_candidate_hits": key_reference_candidates,
            "raw_scan_limit": "Four-byte occurrence search is a locator only. Its matches are not all typed FormID references; the record/subrecord schema and exact inventory/script structure must be interpreted separately.",
        },
        "uesp": uesp,
        "limits": "Installed official source records and local secondary source pages only. No selected profile winner, active alias state, live NPC inventory, pickpocket, door, trigger, quest, or level-one behavior was observed.",
    }
    out = ROOT / ".local/alignment/transactions/TX-20261020-0012/q93/key-source-screen.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "artifact": out.relative_to(ROOT).as_posix(),
        "sha256": digest(out),
        "runtime": result["target"]["runtime"],
        "executable_sha256": result["target"]["executable_sha256"],
        "plugin_sha256": plugin_hashes,
        "record_count_by_plugin": result["record_scope"]["record_count_by_plugin"],
        "target_record_counts": {key: len(rows) for key, rows in exact_records.items()},
        "raw_key_reference_candidate_count": len(key_reference_candidates),
        "candidate_locations": [
            {k: row[k] for k in ("plugin", "signature", "local_form_id", "editor_id", "subrecord", "subrecord_byte_offset", "candidate_field_family")}
            for row in key_reference_candidates
        ],
        "uesp_pages": [{k: row.get(k) for k in ("title", "revision_id", "timestamp", "url", "selected_lines")} for row in uesp],
        "limits": result["limits"],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
