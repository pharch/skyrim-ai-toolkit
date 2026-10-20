#!/usr/bin/env python3
"""Validate and register the native official-five-master world SMQN node."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/xedit-native/20261019T235027.111238Z"
RECEIPT = ROOT / ".local/xedit-native/latest.json"
LEDGER = ROOT / "research/EVIDENCE.json"
SUMMARY = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-we-priority-node-native-summary.json"
OFFICIAL_PLUGINS = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]
EXPECTED_LOADED = ["Skyrim.esm", "SkyrimSE.exe", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    result_path = CAPTURE / "native-result.json"
    tsv_path = CAPTURE / "native-records.tsv"
    preflight_path = CAPTURE / "scoped-preflight.stdout.raw"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    if receipt.get("status") != "PASS" or receipt.get("record", {}).get("editor_id") != "DLC2WEPriorityQuests":
        raise SystemExit("native receipt did not pass for DLC2WEPriorityQuests")
    if receipt.get("record", {}).get("source_plugin") != "Dragonborn.esm" or receipt.get("record", {}).get("signature") != "SMQN":
        raise SystemExit("native receipt identity mismatch")
    if result.get("plugins") != OFFICIAL_PLUGINS or result.get("loaded_files") != EXPECTED_LOADED:
        raise SystemExit("native result did not use the exact official five-master scope")
    if preflight.get("edition") != "AE" or preflight.get("runtime") != "1.6.1170" or preflight.get("full_order_verified") is not False:
        raise SystemExit("native preflight scope/runtime mismatch")
    if digest(result_path) != receipt.get("result_json_sha256") or digest(tsv_path) != receipt.get("tsv_sha256"):
        raise SystemExit("native capture hash differs from receipt")

    fields = result.get("fields", [])
    identities = {
        (field.get("source_plugin"), field.get("form_id"), field.get("editor_id"), field.get("signature"), field.get("winning_plugin"))
        for field in fields
    }
    if identities != {("Dragonborn.esm", "040331C1", "DLC2WEPriorityQuests", "SMQN", "Dragonborn.esm")} or len(fields) != 82:
        raise SystemExit("unexpected native world node identity or field coverage")

    by_path = {str(field.get("field_path", "")): str(field.get("value", "")) for field in fields}
    conditions = []
    for index in range(5):
        prefix = f"SMQN\\5:Conditions\\{index}:Condition\\0:CTDA - CTDA\\"
        conditions.append({
            "type": by_path.get(prefix + "0:Type"),
            "comparison_value": by_path.get(prefix + "2:Comparison Value"),
            "function": by_path.get(prefix + "3:Function"),
            "parameter_1": by_path.get(prefix + "5:Parameter #1"),
            "parameter_2": by_path.get(prefix + "6:Parameter #2"),
            "run_on": by_path.get(prefix + "7:Run On"),
        })
    expected_functions = ["GetGlobalValue", "GetEventData", "GetEventData", "GetEventData", "GetEventData"]
    if [row["function"] for row in conditions] != expected_functions:
        raise SystemExit("unexpected condition functions in DLC2WEPriorityQuests")
    if by_path.get("SMQN\\2:PNAM - Parent ") != "[SMEN:0001379A]" or by_path.get("SMQN\\4:CITC - Condition Count") != "5":
        raise SystemExit("unexpected parent link or condition count")
    if by_path.get("SMQN\\9:Quests\\0:Quest\\0:NNAM - Quest") != "DLC2WE09 \"<Error: No strings file for lstring ID 000023BC>\" [QUST:040331C0]":
        raise SystemExit("unexpected world quest child link")
    if conditions[0]["parameter_1"] != "WEEnabled [GLOB:000B8EC1]" or conditions[0]["comparison_value"] != "1.000000":
        raise SystemExit("unexpected WEEnabled gate fields")
    expected_keywords = ["WEStart [KYWD:0004A600]", "WERoadStart [KYWD:001027A6]", "DLC2WEStart [KYWD:0401AA2B]", "DLC2WERoadStart [KYWD:0401AA2A]"]
    if [row["parameter_2"] for row in conditions[1:]] != expected_keywords:
        raise SystemExit("unexpected event keyword alternatives")
    if any(row["function"] == "GetLevel" for row in conditions):
        raise SystemExit("unexpected GetLevel function in world node")

    summary = {
        "evidence_id": "EV-0661",
        "query": result.get("query"),
        "record": {"plugin": "Dragonborn.esm", "form_id": "040331C1", "editor_id": "DLC2WEPriorityQuests", "signature": "SMQN"},
        "scope": {"official_plugins": result["plugins"], "loaded_files": result["loaded_files"], "winning_plugin_within_official_scope": "Dragonborn.esm", "profile_order_verified": False, "runtime": preflight},
        "field_count": len(fields),
        "native_fields": {"parent": "SMEN:0001379A", "condition_count": 5, "conditions": conditions, "child_quest": "DLC2WE09 QUST:040331C0", "max_concurrent_quests": by_path.get("SMQN\\7:XNAM - Max concurrent quests")},
        "hashes": {"native_result": digest(result_path), "native_tsv": digest(tsv_path), "receipt": digest(RECEIPT), "scoped_preflight": digest(preflight_path), "session": digest(CAPTURE / "session.json")},
        "interpretation_limit": "The native official-five-master SMQN node under Skyrim SMEN 0001379A selects DLC2WE09 and has a WEEnabled global condition plus four GetEventData/GetIsID keyword rows for vanilla and Dragonborn world/road start keywords. No GetLevel occurs in this node. These fields establish event/keyword routing, not the runtime condition-group semantics, parent callback behavior, quest start timing, a profile-specific winner, or the level comparator in DLC2WE09.",
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0661" for item in ledger["items"]):
        raise SystemExit("EV-0661 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0661",
        "captured_utc": receipt["completed_utc"],
        "kind": "tool",
        "source": "Fresh native SSEView 4.1.5f SMQN export from the isolated official five-master Skyrim AE data view.",
        "artifact": "private-local:.local/alignment/xedit-native/20261019T235027.111238Z/native-result.json",
        "sha256": digest(result_path),
        "edition": "AE",
        "runtime": "Steam SkyrimSE.exe ProductVersion 1.6.1170.0, SHA-256 " + preflight["executable_sha256"] + "; WSL2 invoked configured Windows SSEView; no game process was launched.",
        "modified_state": True,
        "lane": "offline",
        "tools": ["python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature SMQN --plugin Dragonborn.esm --editor-id DLC2WEPriorityQuests", "experiments/EXP-0130-dragonborn-cultist-level-gate/register_ev0661_native_we_priority_node.py"],
        "coverage": "Native query returned 82 fields for Dragonborn.esm SMQN DLC2WEPriorityQuests (040331C1). The node's parent is Skyrim.esm SMEN 0001379A, it selects DLC2WE09 QUST 040331C0, and it contains five CTDAs: GetGlobalValue WEEnabled comparison 1, followed by four GetEventData/GetIsID:Keyword rows targeting WEStart, WERoadStart, DLC2WEStart, and DLC2WERoadStart keywords. No GetLevel occurs in the node. The official-five-master view loaded exactly the five official masters plus SkyrimSE.exe; no full profile order or live event was captured.",
        "result": "PASS for native official-five-master world-node retrieval and record-field validation. The query identifies an SCPT-branch keyword dispatcher to DLC2WE09; parent callback and CTDA comparator/runtime semantics remain unresolved.",
        "local_hashes": summary["hashes"],
        "related_evidence": ["EV-0260", "EV-0656", "EV-0657", "EV-0658", "EV-0660"],
    })
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0661", "record": summary["record"], "field_count": len(fields), "native_fields": summary["native_fields"], "hashes": summary["hashes"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
