#!/usr/bin/env python3
"""Validate and register the native five-master DLC2WENode export."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/xedit-native/20261020T000055.697203Z"
RECEIPT = ROOT / ".local/xedit-native/latest.json"
LEDGER = ROOT / "research/EVIDENCE.json"
SUMMARY = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-we-node-native-summary.json"
OFFICIAL = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]
LOADED = ["Skyrim.esm", "SkyrimSE.exe", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    result_path = CAPTURE / "native-result.json"
    tsv_path = CAPTURE / "native-records.tsv"
    preflight_path = CAPTURE / "scoped-preflight.stdout.raw"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    if receipt.get("status") != "PASS" or receipt.get("record", {}).get("form_id") != "0401E7D9":
        raise SystemExit("native receipt did not pass for SMBN 0401E7D9")
    if receipt.get("record", {}).get("editor_id") != "DLC2WENode" or receipt.get("record", {}).get("signature") != "SMBN":
        raise SystemExit("native receipt identity mismatch")
    if result.get("plugins") != OFFICIAL or result.get("loaded_files") != LOADED:
        raise SystemExit("native result did not load the exact official-five-master scope")
    if preflight.get("edition") != "AE" or preflight.get("runtime") != "1.6.1170" or preflight.get("full_order_verified") is not False:
        raise SystemExit("unexpected runtime or profile scope")
    if digest(result_path) != receipt.get("result_json_sha256") or digest(tsv_path) != receipt.get("tsv_sha256"):
        raise SystemExit("native capture hashes differ from the receipt")

    fields = result.get("fields", [])
    identities = {(f.get("source_plugin"), f.get("form_id"), f.get("editor_id"), f.get("signature"), f.get("winning_plugin")) for f in fields}
    if identities != {("Dragonborn.esm", "0401E7D9", "DLC2WENode", "SMBN", "Dragonborn.esm")} or len(fields) != 52:
        raise SystemExit("unexpected node identity or field coverage")
    by_path = {str(f.get("field_path", "")): str(f.get("value", "")) for f in fields}
    expected_record = {
        "SMBN\\2:PNAM - Parent ": "[SMEN:0001379A]",
        "SMBN\\3:SNAM - Previous Sibling ": "WEQuestNode [SMBN:000896A8]",
        "SMBN\\4:CITC - Condition Count": "3",
    }
    if any(by_path.get(path) != value for path, value in expected_record.items()):
        raise SystemExit("unexpected SMBN parent/sibling/condition count")
    conditions: list[dict[str, str]] = []
    for i in range(3):
        prefix = f"SMBN\\5:Conditions\\{i}:Condition\\0:CTDA - CTDA\\"
        row = {str(f["field_path"])[len(prefix):]: str(f.get("value", "")) for f in fields if str(f.get("field_path", "")).startswith(prefix)}
        if not row:
            raise SystemExit(f"condition {i} missing")
        conditions.append(row)
    expected = [
        ("10000000", "GetGlobalValue", "WEEnabled [GLOB:000B8EC1]"),
        ("10010000", "GetEventData", "GetIsID:Keyword", "DLC2WEStart [KYWD:0401AA2B]"),
        ("10010000", "GetEventData", "GetIsID:Keyword", "DLC2WERoadStart [KYWD:0401AA2A]"),
    ]
    for row, spec in zip(conditions, expected, strict=True):
        actual = (row.get("0:Type"), row.get("3:Function"), row.get("5:Parameter #1"), row.get("6:Parameter #2")) if len(spec) == 4 else (row.get("0:Type"), row.get("3:Function"), row.get("5:Parameter #1"))
        if actual != spec:
            raise SystemExit(f"unexpected SMBN condition values: {actual}")
    if any(row.get("2:Comparison Value") != "1.000000" for row in conditions):
        raise SystemExit("unexpected SMBN condition comparison value")

    hashes = {
        "native_result": digest(result_path), "native_tsv": digest(tsv_path),
        "receipt": digest(RECEIPT), "scoped_preflight": digest(preflight_path),
        "session": digest(CAPTURE / "session.json"),
    }
    summary = {
        "evidence_id": "EV-0664",
        "record": {"plugin": "Dragonborn.esm", "form_id": "0401E7D9", "editor_id": "DLC2WENode", "signature": "SMBN"},
        "parent": "Skyrim.esm:0001379A SMEN (Script Event)",
        "previous_sibling": "Dragonborn.esm:000896A8 WEQuestNode SMBN",
        "scope": {"official_plugins": result["plugins"], "loaded_files": result["loaded_files"], "winner_within_scope": "Dragonborn.esm", "profile_order_verified": False, "runtime": preflight},
        "field_count": len(fields),
        "conditions": [{k: row.get(k, "") for k in ["0:Type", "2:Comparison Value", "3:Function", "5:Parameter #1", "6:Parameter #2"]} for row in conditions],
        "interpretation_limit": "The isolated official-five-master native record is an SMBN child of the world Script Event, with one WEEnabled condition and two GetEventData/GetIsID keyword conditions. The Type encodings are preserved as displayed but no evaluator grouping or runtime event dispatch is inferred. No active-profile winner or live encounter is established.",
        "hashes": hashes,
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0664" for item in ledger["items"]):
        raise SystemExit("EV-0664 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0664", "captured_utc": receipt["completed_utc"], "kind": "tool",
        "source": "Fresh native SSEView 4.1.5f SMBN export from the isolated official five-master Skyrim AE data view.",
        "artifact": "private-local:.local/alignment/xedit-native/20261020T000055.697203Z/native-result.json",
        "sha256": hashes["native_result"], "edition": "AE",
        "runtime": "Steam SkyrimSE.exe ProductVersion 1.6.1170.0, SHA-256 " + preflight["executable_sha256"] + "; WSL2 invoked configured Windows SSEView; no game process was launched.",
        "modified_state": True, "lane": "offline",
        "tools": ["python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature SMBN --plugin Dragonborn.esm --form-id 0401E7D9", "experiments/EXP-0130-dragonborn-cultist-level-gate/register_ev0664_native_we_branch.py"],
        "coverage": "Native official-five-master query returned 52 fields for Dragonborn.esm SMBN DLC2WENode (0401E7D9). Parent is Skyrim.esm SMEN 0001379A; previous sibling is Dragonborn.esm SMBN 000896A8 WEQuestNode. Its three conditions are GetGlobalValue WEEnabled, then GetEventData/GetIsID:Keyword for DLC2WEStart and DLC2WERoadStart; each comparison is 1.0. Exactly the five official masters plus SkyrimSE.exe were loaded.",
        "result": "PASS for native record retrieval and bounded condition screen. Condition group semantics, script-event evaluation, active profile overrides, and actual world-encounter initiation remain unverified.",
        "local_hashes": hashes, "related_evidence": ["EV-0656", "EV-0661", "EV-0662", "EV-0663"],
    })
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0664", "record": summary["record"], "conditions": summary["conditions"], "hashes": hashes}, indent=2))


if __name__ == "__main__":
    main()
