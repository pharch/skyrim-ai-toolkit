#!/usr/bin/env python3
"""Register direct-parser Dragonborn Story Manager records relevant to Q81."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-storymanager-summary.json"
LEDGER = ROOT / "research/EVIDENCE.json"
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-storymanager-evidence.json"
RAW = {
    "SMEN": ROOT / ".local/alignment/xedit-bridge/20261019T233633.938231Z/stdout.raw",
    "SMBN": ROOT / ".local/alignment/xedit-bridge/20261019T233633.938793Z/stdout.raw",
    "SMQN": ROOT / ".local/alignment/xedit-bridge/20261019T233633.940124Z/stdout.raw",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    actual_hashes = {signature: digest(path) for signature, path in RAW.items()}
    if actual_hashes != summary.get("raw_capture_hashes"):
        raise SystemExit("raw Story Manager capture hash mismatch")
    if summary.get("counts") != {"SMEN": 2, "SMBN": 15, "SMQN": 43}:
        raise SystemExit("unexpected Dragonborn Story Manager record counts")
    linked = summary.get("story_records_with_nnam_child_matching_target_quest", [])
    expected = {
        ("SMQN", "02035472", "DLC2CultistAmbushNode", "0203546D"),
        ("SMQN", "020331C1", "DLC2WEPriorityQuests", "020331C0"),
    }
    observed = {
        (row.get("signature"), row.get("file_form_id"), row.get("editor_id"), child)
        for row in linked for child in row.get("matched_quest_children", [])
    }
    if observed != expected:
        raise SystemExit("unexpected Dragonborn Story Manager child links")
    if any(condition.get("function_index") == 80 for row in linked for condition in row.get("conditions", [])):
        raise SystemExit("GetLevel is present in one of the captured child nodes")

    evidence = {
        "evidence_id": "EV-0656",
        "captured_utc": "2026-10-19T23:36:33Z",
        "kind": "tool",
        "route": "Direct read-only TES4 file parser, strict-dispatcher captures of serialized Dragonborn.esm SMEN, SMQN and SMBN records.",
        "counts": summary["counts"],
        "target_links": linked,
        "raw_capture_hashes": actual_hashes,
        "scope_limit": summary["interpretation_limit"],
    }
    OUTPUT.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0656" for item in ledger["items"]):
        raise SystemExit("EV-0656 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0656",
        "captured_utc": evidence["captured_utc"],
        "kind": "tool",
        "source": "Direct read-only TES4 parser captures of Dragonborn.esm Story Manager source-file records.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261019-0002/q81-storymanager-summary.json",
        "sha256": digest(SUMMARY),
        "edition": "AE",
        "runtime": "Official Dragonborn.esm source-file screen scoped to the configured Steam AE 1.6.1170 research setup; no game process or native xEdit session involved.",
        "modified_state": True,
        "lane": "offline",
        "tools": [
            "python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature SMQN --plugin Dragonborn.esm",
            "python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature SMEN --plugin Dragonborn.esm",
            "python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature SMBN --plugin Dragonborn.esm",
            "experiments/EXP-0130-dragonborn-cultist-level-gate/summarize_q81_storymanager_inputs.py",
        ],
        "coverage": "The direct parser captured 43 Dragonborn.esm SMQN, two SMEN and 15 SMBN records. SMQN 02035472 DLC2CultistAmbushNode has NNAM child 0203546D (DLC2CultistAmbush); SMQN 020331C1 DLC2WEPriorityQuests has NNAM child 020331C0 (DLC2WE09). These child nodes have no CTDA function index 80 (GetLevel). Their respective parent form IDs are 0001320E and 0001379A. The SMBN DLC2WENode is a separate branch record under 0001379A. Raw condition bytes and capture hashes are preserved in the local summary.",
        "result": "PASS for bounded source-file record retrieval and exact child-link screening. This does not decode every function name, establish the parent records' gates, resolve active-profile winners, or prove runtime initiation.",
        "local_hashes": actual_hashes,
        "related_evidence": ["EV-0260", "EV-0653", "EV-0654", "EV-0655"],
    })
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0656", "counts": evidence["counts"], "target_links": linked, "hashes": actual_hashes}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
