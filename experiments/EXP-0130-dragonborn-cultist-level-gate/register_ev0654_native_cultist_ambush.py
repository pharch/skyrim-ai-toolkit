#!/usr/bin/env python3
"""Validate and register the native five-master DLC2CultistAmbush QUST export."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/xedit-native/20261019T231902.999070Z"
RECEIPT = ROOT / ".local/xedit-native/latest.json"
LEDGER = ROOT / "research/EVIDENCE.json"
SUMMARY = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-cultist-ambush-native-summary.json"
OFFICIAL_PLUGINS = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]


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
    if receipt.get("status") != "PASS":
        raise SystemExit("native receipt did not pass integrity checks")
    if receipt.get("record", {}).get("source_plugin") != "Dragonborn.esm":
        raise SystemExit("native receipt source plugin mismatch")
    if receipt.get("record", {}).get("editor_id") != "DLC2CultistAmbush":
        raise SystemExit("native receipt EditorID mismatch")
    if result.get("plugins") != OFFICIAL_PLUGINS or result.get("loaded_files") != [
        "Skyrim.esm", "SkyrimSE.exe", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"
    ]:
        raise SystemExit("native result did not use the exact official five-master scope")
    if preflight.get("edition") != "AE" or preflight.get("runtime") != "1.6.1170":
        raise SystemExit("scoped preflight did not verify the configured Steam AE executable")
    if preflight.get("full_order_verified") is not False:
        raise SystemExit("unexpected profile-specific order claim in the scoped query")
    if digest(result_path) != receipt.get("result_json_sha256"):
        raise SystemExit("native result hash differs from the integrity receipt")
    if digest(tsv_path) != receipt.get("tsv_sha256"):
        raise SystemExit("native TSV hash differs from the integrity receipt")

    fields = result.get("fields", [])
    identities = {
        (field.get("source_plugin"), field.get("form_id"), field.get("editor_id"), field.get("signature"), field.get("winning_plugin"))
        for field in fields
    }
    if identities != {("Dragonborn.esm", "0403546D", "DLC2CultistAmbush", "QUST", "Dragonborn.esm")}:
        raise SystemExit("field rows do not consistently identify the requested QUST")
    functions = [
        field.get("value", "") for field in fields
        if str(field.get("field_path", "")).endswith(":Function")
    ]
    if len(fields) != 483 or len(functions) != 6 or "GetLevel" in functions:
        raise SystemExit("unexpected QUST field count or CTDA function coverage")
    if set(functions) != {"IsCommandedActor", "GetInFaction", "GetIsVoiceType", "LocationHasKeyword"}:
        raise SystemExit("unexpected conditional function set in the native QUST export")

    all_text = "\n".join(
        f"{field.get('field_path', '')}\t{field.get('value', '')}\t{field.get('links_to', '')}"
        for field in fields
    )
    markers = (
        "CLOC", "DLC2WE09ActorScript", "DLC2WECultistAmbushPlayerScript",
        "DLC2MQ01", "DLC2WE09Chance", "LocTypeHabitation", "CWCapital", "LocTypeTown",
    )
    if any(marker not in all_text for marker in markers):
        raise SystemExit("required event, script, property, or alias-condition marker is absent")

    summary = {
        "evidence_id": "EV-0654",
        "query": result.get("query"),
        "record": {"plugin": "Dragonborn.esm", "form_id": "0403546D", "editor_id": "DLC2CultistAmbush", "signature": "QUST"},
        "scope": {
            "official_plugins": result["plugins"],
            "loaded_files": result["loaded_files"],
            "winning_plugin_within_official_scope": "Dragonborn.esm",
            "profile_order_verified": False,
            "runtime": preflight,
        },
        "field_count": len(fields),
        "ctda_function_rows": functions,
        "quest_event": "CLOC",
        "stage_indexes": [
            int(field["value"]) for field in fields
            if str(field.get("field_path", "")).endswith("Quest Stage") and str(field.get("value", "")).isdigit()
        ],
        "attached_script_markers": ["DLC2WE09ActorScript", "DLC2WECultistAmbushPlayerScript"],
        "linked_ids": {"DLC2MQ01": "Dragonborn.esm:04017F8E", "DLC2WE09Chance": "Dragonborn.esm:04033C24"},
        "interpretation_limit": "No GetLevel appears among the six CTDA function rows in this QUST export; this does not exclude a script, story-manager, native, or profile-level gate outside the captured record.",
        "hashes": {
            "native_result": digest(result_path),
            "native_tsv": digest(tsv_path),
            "receipt": digest(RECEIPT),
            "scoped_preflight": digest(preflight_path),
            "session": digest(CAPTURE / "session.json"),
        },
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0654" for item in ledger["items"]):
        raise SystemExit("EV-0654 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0654",
        "captured_utc": receipt["completed_utc"],
        "kind": "tool",
        "source": "Fresh native SSEView 4.1.5f QUST export from the isolated official five-master Skyrim AE data view.",
        "artifact": "private-local:.local/alignment/xedit-native/20261019T231902.999070Z/native-result.json",
        "sha256": digest(result_path),
        "edition": "AE",
        "runtime": "Steam SkyrimSE.exe ProductVersion 1.6.1170.0, SHA-256 " + preflight["executable_sha256"] + "; WSL2 invoked configured Windows SSEView; no game process was launched.",
        "modified_state": True,
        "lane": "offline",
        "tools": [
            "python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature QUST --plugin Dragonborn.esm --editor-id DLC2CultistAmbush",
            "python3 scripts/python_env.py run tools/xedit_bridge.py doctor",
            "experiments/EXP-0130-dragonborn-cultist-level-gate/register_ev0654_native_cultist_ambush.py",
        ],
        "coverage": "Native five-master query returned 483 fields for Dragonborn.esm QUST DLC2CultistAmbush, FormID 0403546D. Loaded files were exactly Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm and Dragonborn.esm plus SkyrimSE.exe. The six QUST CTDA function rows are IsCommandedActor, GetInFaction, GetIsVoiceType and three LocationHasKeyword rows; no GetLevel appears in this record. The event is CLOC, stage indices are 1, 10 and 255, and attached alias scripts include DLC2WE09ActorScript and DLC2WECultistAmbushPlayerScript. Script properties link DLC2MQ01 (04017F8E) and DLC2WE09Chance (GLOB 04033C24). The winner is only within the official five-master view; no complete profile order or live transition is claimed.",
        "result": "PASS for native official-five-master QUST retrieval and bounded condition/script-reference screen. The lack of GetLevel in this one QUST's CTDAs does not exclude a level gate in attached Papyrus, story-manager nodes, native code or profile overrides; the shared DLC2WE09 links require follow-up.",
        "local_hashes": summary["hashes"],
        "related_evidence": ["EV-0207", "EV-0214", "EV-0260", "EV-0653"],
    })
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0654", "record": summary["record"], "field_count": len(fields), "ctda_functions": functions, "hashes": summary["hashes"]}, indent=2))


if __name__ == "__main__":
    main()
