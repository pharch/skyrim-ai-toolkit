#!/usr/bin/env python3
"""Register direct source-file bytes for DLC2WE09's level/location CTDAs."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / ".local/alignment/xedit-bridge/20261020T000133.499045Z/stdout.raw"
SUMMARY = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-we09-raw-condition-summary.json"
LEDGER = ROOT / "research/EVIDENCE.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    records = json.loads(RAW.read_text(encoding="utf-8"))
    if isinstance(records, dict):
        records = [records]
    hits = [r for r in records if r.get("plugin") == "Dragonborn.esm" and r.get("signature") == "QUST" and r.get("editor_id") == "DLC2WE09"]
    if len(hits) != 1:
        raise SystemExit("expected exactly one direct-parser DLC2WE09 QUST record")
    record = hits[0]
    if (record.get("file_form_id"), record.get("local_form_id")) != ("020331C0", "0331C0"):
        raise SystemExit("source FormID identity mismatch")
    header: list[dict[str, str]] = []
    for subrecord in record.get("subrecords", []):
        if subrecord.get("signature") == "INDX":
            break
        if subrecord.get("signature") in {"CTDA", "NEXT"}:
            header.append(subrecord)
    ctda = [bytes.fromhex(item["hex"]) for item in header if item.get("signature") == "CTDA"]
    if len(ctda) != 6 or any(len(raw) != 32 for raw in ctda):
        raise SystemExit(f"expected six complete top-level QUST CTDAs; found {len(ctda)}")
    level_rows = [raw for raw in ctda if struct.unpack_from("<H", raw, 8)[0] == 80]
    loc_rows = [raw for raw in ctda if struct.unpack_from("<H", raw, 8)[0] == 359]
    if len(level_rows) != 1 or len(loc_rows) != 1:
        raise SystemExit("expected one GetLevel and one GetInCurrentLoc in top-level CTDAs")
    level, location = level_rows[0], loc_rows[0]
    if level[0] != 0x61 or struct.unpack_from("<f", level, 4)[0] != 25.0:
        raise SystemExit("unexpected raw GetLevel type/comparison")
    if location[0] != 0x01 or struct.unpack_from("<f", location, 4)[0] != 1.0:
        raise SystemExit("unexpected raw GetInCurrentLoc type/comparison")
    if not (level[0] & 1) or not (location[0] & 1):
        raise SystemExit("expected OR flag bit 0 in both rows")

    hashes = {"direct_parser_stdout": digest(RAW)}
    summary = {
        "evidence_id": "EV-0665",
        "record": {"plugin": record["plugin"], "signature": record["signature"], "editor_id": record["editor_id"], "file_form_id": record["file_form_id"], "plugin_local_form_id": record["local_form_id"]},
        "top_level_ctda_count": len(ctda),
        "get_level": {"function_index": 80, "raw_type_byte": f"0x{level[0]:02x}", "comparison_value": struct.unpack_from("<f", level, 4)[0], "or_flag_set": bool(level[0] & 1)},
        "get_in_current_loc": {"function_index": 359, "raw_type_byte": f"0x{location[0]:02x}", "comparison_value": struct.unpack_from("<f", location, 4)[0], "or_flag_set": bool(location[0] & 1)},
        "interpretation_limit": "These are raw source-file CTDA bytes, not a native xEdit winner or runtime evaluation. They show the OR flag bit on both the GetLevel and location predicates; the record alone does not establish how the engine groups or evaluates them.",
        "sha256": hashes["direct_parser_stdout"],
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0665" for item in ledger["items"]):
        raise SystemExit("EV-0665 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0665", "captured_utc": "2026-10-20T00:01:33.499045+00:00", "kind": "tool",
        "source": "Direct read-only TES4 parser stdout for Dragonborn.esm QUST DLC2WE09; raw serialized CTDA bytes.",
        "artifact": "private-local:.local/alignment/xedit-bridge/20261020T000133.499045Z/stdout.raw",
        "sha256": hashes["direct_parser_stdout"], "edition": "AE",
        "runtime": "Configured Steam Skyrim AE source tree associated with verified Steam 1.6.1170.0 identity EV-0109; this parser does not resolve winning overrides.",
        "modified_state": False, "lane": "offline",
        "tools": ["python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature QUST --plugin Dragonborn.esm --editor-id DLC2WE09", "experiments/EXP-0130-dragonborn-cultist-level-gate/register_ev0665_raw_we09_condition.py"],
        "coverage": "The direct source-file record is Dragonborn.esm QUST DLC2WE09, source FormID 020331C0/plugin-local 0331C0. Among six top-level CTDAs before the first INDX, GetLevel is function index 80 with comparison 25.0 and raw Type byte 0x61; GetInCurrentLoc is function index 359 with comparison 1.0 and raw Type byte 0x01. Both bytes have bit 0 set. Alias conditions and native winner resolution are outside this specific result.",
        "result": "PASS for exact direct-parser record retrieval and byte-level condition identification. The OR flag is present on both rows; grouping/evaluation semantics and runtime behavior are unresolved.",
        "local_hashes": hashes, "related_evidence": ["EV-0657", "EV-0664"],
    })
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0665", "condition_summary": summary, "sha256": hashes["direct_parser_stdout"]}, indent=2))


if __name__ == "__main__":
    main()
