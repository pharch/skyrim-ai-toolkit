#!/usr/bin/env python3
"""Validate and register the native official-five-master cultist SMQN node."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/xedit-native/20261019T234616.105878Z"
RECEIPT = ROOT / ".local/xedit-native/latest.json"
LEDGER = ROOT / "research/EVIDENCE.json"
SUMMARY = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-cultist-node-native-summary.json"
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
    if receipt.get("status") != "PASS" or receipt.get("record", {}).get("editor_id") != "DLC2CultistAmbushNode":
        raise SystemExit("native receipt did not pass for DLC2CultistAmbushNode")
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
    expected_identity = ("Dragonborn.esm", "04035472", "DLC2CultistAmbushNode", "SMQN", "Dragonborn.esm")
    if identities != {expected_identity} or len(fields) != 71:
        raise SystemExit("unexpected native node identity or field coverage")
    by_path = {field.get("field_path"): str(field.get("value", "")) for field in fields}
    expected = {
        "SMQN\\2:PNAM - Parent ": "[SMEN:0001320E]",
        "SMQN\\4:CITC - Condition Count": "4",
        "SMQN\\5:Conditions\\0:Condition\\0:CTDA - CTDA\\3:Function": "GetInCurrentLoc",
        "SMQN\\5:Conditions\\0:Condition\\0:CTDA - CTDA\\5:Parameter #1": "DLC2SolstheimLocation \"<Error: No strings file for lstring ID 0000007D>\" [LCTN:04016E2A]",
        "SMQN\\5:Conditions\\1:Condition\\0:CTDA - CTDA\\3:Function": "GetStage",
        "SMQN\\5:Conditions\\1:Condition\\0:CTDA - CTDA\\2:Comparison Value": "160.000000",
        "SMQN\\5:Conditions\\1:Condition\\0:CTDA - CTDA\\5:Parameter #1": "MQ105 \"<Error: No strings file for lstring ID 0000157A>\" [QUST:000242BA]",
        "SMQN\\5:Conditions\\2:Condition\\0:CTDA - CTDA\\3:Function": "GetStage",
        "SMQN\\5:Conditions\\2:Condition\\0:CTDA - CTDA\\2:Comparison Value": "5.000000",
        "SMQN\\5:Conditions\\2:Condition\\0:CTDA - CTDA\\5:Parameter #1": "DLC2MQ01 \"<Error: No strings file for lstring ID 00000611>\" [QUST:04017F8E]",
        "SMQN\\5:Conditions\\3:Condition\\0:CTDA - CTDA\\3:Function": "GetStageDone",
        "SMQN\\5:Conditions\\3:Condition\\0:CTDA - CTDA\\5:Parameter #1": "DLC2WE09 \"<Error: No strings file for lstring ID 000023BC>\" [QUST:040331C0]",
        "SMQN\\9:Quests\\0:Quest\\0:NNAM - Quest": "DLC2CultistAmbush [QUST:0403546D]",
    }
    if any(by_path.get(path) != value for path, value in expected.items()):
        raise SystemExit("unexpected native node parent, CTDA, or child quest fields")
    if any("GetLevel" == str(field.get("value", "")) for field in fields if str(field.get("field_path", "")).endswith(":Function")):
        raise SystemExit("unexpected GetLevel function in cultist node")

    summary = {
        "evidence_id": "EV-0660",
        "query": result.get("query"),
        "record": {"plugin": "Dragonborn.esm", "form_id": "04035472", "editor_id": "DLC2CultistAmbushNode", "signature": "SMQN"},
        "scope": {"official_plugins": result["plugins"], "loaded_files": result["loaded_files"], "winning_plugin_within_official_scope": "Dragonborn.esm", "profile_order_verified": False, "runtime": preflight},
        "field_count": len(fields),
        "native_fields": expected,
        "hashes": {"native_result": digest(result_path), "native_tsv": digest(tsv_path), "receipt": digest(RECEIPT), "scoped_preflight": digest(preflight_path), "session": digest(CAPTURE / "session.json")},
        "interpretation_limit": "The native official-five-master Story Manager node is a child of the Skyrim.esm CLOC parent, tests Solstheim location and quest-state CTDAs, and points to DLC2CultistAmbush. Its GetStageDone reference to DLC2WE09 shows node-level coordination with that quest, not a shared start event or a level predicate. CTDA operator semantics, full profile winners, attached PEX behavior, event dispatch, and vanilla level-one runtime initiation remain unresolved.",
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0660" for item in ledger["items"]):
        raise SystemExit("EV-0660 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0660",
        "captured_utc": receipt["completed_utc"],
        "kind": "tool",
        "source": "Fresh native SSEView 4.1.5f SMQN export from the isolated official five-master Skyrim AE data view.",
        "artifact": "private-local:.local/alignment/xedit-native/20261019T234616.105878Z/native-result.json",
        "sha256": digest(result_path),
        "edition": "AE",
        "runtime": "Steam SkyrimSE.exe ProductVersion 1.6.1170.0, SHA-256 " + preflight["executable_sha256"] + "; WSL2 invoked configured Windows SSEView; no game process was launched.",
        "modified_state": True,
        "lane": "offline",
        "tools": ["python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature SMQN --plugin Dragonborn.esm --editor-id DLC2CultistAmbushNode", "experiments/EXP-0130-dragonborn-cultist-level-gate/register_ev0660_native_cultist_node.py"],
        "coverage": "Native query returned 71 fields for Dragonborn.esm SMQN DLC2CultistAmbushNode (04035472). The official-five-master winner is Dragonborn.esm; loaded files were exactly the five official masters plus SkyrimSE.exe. The node's parent is Skyrim.esm SMEN 0001320E; its four CTDAs are GetInCurrentLoc for DLC2SolstheimLocation, GetStage MQ105 160, GetStage DLC2MQ01 5, and GetStageDone DLC2WE09 parameter 001. The child quest link is DLC2CultistAmbush QUST 0403546D. No GetLevel function occurs in this node. This is an official-scope record screen only.",
        "result": "PASS for native official-five-master SMQN retrieval and condition/link validation. The node shows separate CLOC branch plus a DLC2WE09 stage-state dependency; raw CTDA operator semantics and runtime pass/fail remain unresolved.",
        "local_hashes": summary["hashes"],
        "related_evidence": ["EV-0260", "EV-0654", "EV-0656", "EV-0657", "EV-0658", "EV-0659"],
    })
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0660", "record": summary["record"], "field_count": len(fields), "native_fields": expected, "hashes": summary["hashes"]}, indent=2))


if __name__ == "__main__":
    main()
