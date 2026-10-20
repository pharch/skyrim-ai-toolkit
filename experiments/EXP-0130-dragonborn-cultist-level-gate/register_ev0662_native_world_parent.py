#!/usr/bin/env python3
"""Validate and register the native official-five-master SCPT parent event."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/xedit-native/20261019T235346.267538Z"
RECEIPT = ROOT / ".local/xedit-native/latest.json"
LEDGER = ROOT / "research/EVIDENCE.json"
SUMMARY = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-world-parent-native-summary.json"
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
    if receipt.get("status") != "PASS" or receipt.get("record", {}).get("form_id") != "0001379A":
        raise SystemExit("native receipt did not pass for SMEN 0001379A")
    if receipt.get("record", {}).get("source_plugin") != "Skyrim.esm" or receipt.get("record", {}).get("signature") != "SMEN":
        raise SystemExit("native receipt identity mismatch")
    if receipt.get("record", {}).get("winning_plugin_within_official_five_master_scope") != "HearthFires.esm":
        raise SystemExit("unexpected official-five-master winner")
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
    if identities != {("Skyrim.esm", "0001379A", "", "SMEN", "HearthFires.esm")} or len(fields) != 15:
        raise SystemExit("unexpected native parent event identity or field coverage")
    by_path = {str(field.get("field_path", "")): str(field.get("value", "")) for field in fields}
    expected = {
        "SMEN\\1:PNAM - Parent ": "Root [SMBN:0000005B]",
        "SMEN\\3:CITC - Condition Count": "0",
        "SMEN\\6:ENAM - Type": "Script Event",
    }
    if any(by_path.get(path) != value for path, value in expected.items()):
        raise SystemExit("unexpected native SCPT parent event fields")
    if any(str(field.get("field_path", "")).endswith(":Function") for field in fields):
        raise SystemExit("unexpected CTDA function in parent event")

    summary = {
        "evidence_id": "EV-0662",
        "query": result.get("query"),
        "record": {"plugin": "Skyrim.esm", "form_id": "0001379A", "editor_id": "", "signature": "SMEN"},
        "scope": {"official_plugins": result["plugins"], "loaded_files": result["loaded_files"], "winning_plugin_within_official_scope": "HearthFires.esm", "profile_order_verified": False, "runtime": preflight},
        "field_count": len(fields),
        "native_fields": expected,
        "hashes": {"native_result": digest(result_path), "native_tsv": digest(tsv_path), "receipt": digest(RECEIPT), "scoped_preflight": digest(preflight_path), "session": digest(CAPTURE / "session.json")},
        "interpretation_limit": "The native official-five-master winner for Skyrim.esm SMEN 0001379A is HearthFires.esm and displays Script Event, Root parent, and zero CTDA rows. This verifies the event record in the isolated official-master view only; a complete active profile order, runtime event dispatch, and downstream world-encounter conditions remain unverified.",
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0662" for item in ledger["items"]):
        raise SystemExit("EV-0662 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0662",
        "captured_utc": receipt["completed_utc"],
        "kind": "tool",
        "source": "Fresh native SSEView 4.1.5f SMEN export from the isolated official five-master Skyrim AE data view.",
        "artifact": "private-local:.local/alignment/xedit-native/20261019T235346.267538Z/native-result.json",
        "sha256": digest(result_path),
        "edition": "AE",
        "runtime": "Steam SkyrimSE.exe ProductVersion 1.6.1170.0, SHA-256 " + preflight["executable_sha256"] + "; WSL2 invoked configured Windows SSEView; no game process was launched.",
        "modified_state": True,
        "lane": "offline",
        "tools": ["python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature SMEN --plugin Skyrim.esm --form-id 0001379A", "experiments/EXP-0130-dragonborn-cultist-level-gate/register_ev0662_native_world_parent.py"],
        "coverage": "Native query returned 15 fields for Skyrim.esm SMEN 0001379A. Its official-five-master winner is HearthFires.esm, the parent is Root SMBN 0000005B, Condition Count is zero, and Type is Script Event. Loaded files were exactly the five official masters plus SkyrimSE.exe. This is not a complete active-profile winner or runtime event observation.",
        "result": "PASS for native official-five-master parent retrieval. The world branch's parent event is a zero-condition Script Event in this scope; event payload and child-node scheduling are not resolved.",
        "local_hashes": summary["hashes"],
        "related_evidence": ["EV-0656", "EV-0658", "EV-0659", "EV-0661"],
    })
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0662", "record": summary["record"], "official_scope_winner": "HearthFires.esm", "native_fields": expected, "hashes": summary["hashes"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
