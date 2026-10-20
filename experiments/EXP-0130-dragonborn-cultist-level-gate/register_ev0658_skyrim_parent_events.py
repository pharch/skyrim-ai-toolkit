#!/usr/bin/env python3
"""Register direct-parser Skyrim.esm event-parent records for Q81."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-skyrim-parent-events.json"
LEDGER = ROOT / "research/EVIDENCE.json"
OUTPUT = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-skyrim-parent-evidence.json"
RAW = {
    "SMQN": ROOT / ".local/alignment/xedit-bridge/20261019T234139.585732Z/stdout.raw",
    "SMEN": ROOT / ".local/alignment/xedit-bridge/20261019T234139.586660Z/stdout.raw",
    "SMBN": ROOT / ".local/alignment/xedit-bridge/20261019T234137.644340Z/stdout.raw",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    hashes = {signature: digest(path) for signature, path in RAW.items()}
    if hashes != summary.get("raw_capture_hashes"):
        raise SystemExit("Skyrim.esm parent-event capture hash mismatch")
    if summary.get("source_counts") != {"SMQN": 448, "SMEN": 24, "SMBN": 99}:
        raise SystemExit("unexpected Skyrim.esm Story Manager record counts")
    selected = summary.get("target_parent_events", [])
    observed = {(row.get("signature"), row.get("file_form_id"), tuple(row.get("event_codes_enam", [])), row.get("ctda_count")) for row in selected}
    expected = {("SMEN", "0001320E", ("CLOC",), 0), ("SMEN", "0001379A", ("SCPT",), 0)}
    if observed != expected or any(row.get("parent_form_ids") != ["0000005B"] for row in selected):
        raise SystemExit("unexpected Skyrim.esm event-parent identity or fields")

    evidence = {
        "id": "EV-0658",
        "captured_utc": "2026-10-19T23:41:39+00:00",
        "kind": "tool",
        "source": "Direct read-only TES4 parser captures of complete Skyrim.esm Story Manager source records.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261019-0002/q81-skyrim-parent-events.json",
        "sha256": digest(SUMMARY),
        "edition": "AE",
        "runtime": "Offline source-file screen in the configured Steam AE research workspace; no live game or profile-order result.",
        "modified_state": True,
        "lane": "offline",
        "tools": [
            "python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature SMQN --plugin Skyrim.esm",
            "python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature SMEN --plugin Skyrim.esm",
            "python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature SMBN --plugin Skyrim.esm",
            "experiments/EXP-0130-dragonborn-cultist-level-gate/summarize_q81_skyrim_parent_events.py",
        ],
        "coverage": "The direct parser captured 448 Skyrim.esm SMQN, 24 SMEN and 99 SMBN records. SMEN 0001320E is event CLOC and SMEN 0001379A is event SCPT; both have parent Root SMBN 0000005B and zero CTDA rows. EV-0656 maps Dragonborn DLC2CultistAmbushNode under 0001320E and DLC2WEPriorityQuests/DLC2WENode under 0001379A. This supports two distinct serialized Story Manager branches, subject to native field verification.",
        "result": "PASS for bounded parent-event source-file identification and parent-link screen. Event payload semantics, complete load-order winners and runtime behavior remain unresolved.",
        "local_hashes": hashes,
        "related_evidence": ["EV-0260", "EV-0654", "EV-0656", "EV-0657"],
    }
    OUTPUT.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0658" for item in ledger["items"]):
        raise SystemExit("EV-0658 already exists; refusing duplicate registration")
    ledger["items"].append(evidence)
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0658", "target_parent_events": selected, "hashes": hashes}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
