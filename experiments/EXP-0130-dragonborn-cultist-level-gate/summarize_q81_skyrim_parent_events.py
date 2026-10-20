#!/usr/bin/env python3
"""Resolve the Skyrim.esm event records that parent the Dragonborn Q81 nodes."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
CAPTURES = {
    "SMQN": ROOT / ".local/alignment/xedit-bridge/20261019T234139.585732Z/stdout.raw",
    "SMEN": ROOT / ".local/alignment/xedit-bridge/20261019T234139.586660Z/stdout.raw",
    "SMBN": ROOT / ".local/alignment/xedit-bridge/20261019T234137.644340Z/stdout.raw",
}
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-skyrim-parent-events.json"
TARGET_IDS = {"0001320E", "0001379A"}
EXPECTED_COUNTS = {"SMQN": 448, "SMEN": 24, "SMBN": 99}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_records(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def hex_refs(record: dict, signature: str) -> list[str]:
    return [
        f"{int.from_bytes(bytes.fromhex(row['hex']), 'little'):08X}"
        for row in record.get("subrecords", [])
        if row.get("signature") == signature and len(bytes.fromhex(row["hex"])) == 4
    ]


def main() -> None:
    tables = {signature: read_records(path) for signature, path in CAPTURES.items()}
    for signature, rows in tables.items():
        if len(rows) != EXPECTED_COUNTS[signature] or any(row.get("plugin") != "Skyrim.esm" for row in rows):
            raise SystemExit(f"unexpected {signature} source-file capture scope or count")

    selected = []
    for signature, rows in tables.items():
        for row in rows:
            if row.get("file_form_id", "").upper() not in TARGET_IDS:
                continue
            events = [bytes.fromhex(sub["hex"]).decode("ascii", errors="replace") for sub in row.get("subrecords", []) if sub.get("signature") == "ENAM"]
            conditions = [sub["hex"] for sub in row.get("subrecords", []) if sub.get("signature") == "CTDA"]
            selected.append({
                "signature": signature,
                "file_form_id": row["file_form_id"],
                "editor_id": row.get("editor_id"),
                "parent_form_ids": hex_refs(row, "PNAM"),
                "snam_form_ids": hex_refs(row, "SNAM"),
                "event_codes_enam": events,
                "ctda_count": len(conditions),
                "ctda_raw": conditions,
            })
    expected = {
        ("SMEN", "0001320E", "CLOC"),
        ("SMEN", "0001379A", "SCPT"),
    }
    observed = {
        (row["signature"], row["file_form_id"], row["event_codes_enam"][0])
        for row in selected if row["event_codes_enam"]
    }
    if observed != expected or any(row["ctda_count"] != 0 for row in selected):
        raise SystemExit("unexpected parent event records or condition rows")
    if any(row["parent_form_ids"] != ["0000005B"] for row in selected):
        raise SystemExit("unexpected parent-of-parent for target event records")

    result = {
        "evidence_id_candidate": "EV-0658",
        "route": "direct read-only TES4 parser of complete Skyrim.esm SMQN/SMEN/SMBN source records",
        "source_counts": EXPECTED_COUNTS,
        "target_parent_events": selected,
        "raw_capture_hashes": {signature: digest(path) for signature, path in CAPTURES.items()},
        "linked_dragonborn_nodes_from_EV-0656": {
            "SMEN:0001320E:CLOC": ["Dragonborn.esm SMQN 02035472 DLC2CultistAmbushNode -> QUST 0203546D DLC2CultistAmbush"],
            "SMEN:0001379A:SCPT": ["Dragonborn.esm SMQN 020331C1 DLC2WEPriorityQuests -> QUST 020331C0 DLC2WE09", "Dragonborn.esm SMBN 0201E7D9 DLC2WENode"],
        },
        "interpretation_limit": "This maps serialized source-file event and parent references only. It does not establish which event data fires during natural play, native merged winners, script effects, or level-one runtime behavior.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
