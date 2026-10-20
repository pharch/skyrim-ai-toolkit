#!/usr/bin/env python3
"""Validate and register the native five-master DLC2MQ01 QUST export."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/xedit-native/20261019T232821.045502Z"
RECEIPT = ROOT / ".local/xedit-native/latest.json"
LEDGER = ROOT / "research/EVIDENCE.json"
SUMMARY = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-mq01-native-summary.json"
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
    if receipt.get("status") != "PASS" or receipt.get("record", {}).get("form_id") != "04017F8E":
        raise SystemExit("native receipt did not pass for DLC2MQ01")
    if receipt.get("record", {}).get("editor_id") != "DLC2MQ01" or receipt.get("record", {}).get("source_plugin") != "Dragonborn.esm":
        raise SystemExit("native receipt record identity mismatch")
    if result.get("plugins") != OFFICIAL_PLUGINS or result.get("loaded_files") != EXPECTED_LOADED:
        raise SystemExit("native result did not use the exact official five-master scope")
    if preflight.get("edition") != "AE" or preflight.get("runtime") != "1.6.1170":
        raise SystemExit("scoped preflight did not verify the configured Steam AE executable")
    if preflight.get("full_order_verified") is not False:
        raise SystemExit("unexpected profile-specific order claim in the scoped query")
    if digest(result_path) != receipt.get("result_json_sha256") or digest(tsv_path) != receipt.get("tsv_sha256"):
        raise SystemExit("native capture hash differs from the integrity receipt")

    fields = result.get("fields", [])
    identities = {
        (field.get("source_plugin"), field.get("form_id"), field.get("editor_id"), field.get("signature"), field.get("winning_plugin"))
        for field in fields
    }
    expected = {("Dragonborn.esm", "04017F8E", "DLC2MQ01", "QUST", "Dragonborn.esm")}
    if identities != expected or len(fields) != 675:
        raise SystemExit("unexpected DLC2MQ01 identity or field coverage")

    functions = [field.get("value", "") for field in fields if str(field.get("field_path", "")).endswith(":Function")]
    expected_functions = {"GetDisabled", "GetInCurrentLoc", "GetInFaction", "GetStageDone"}
    if len(functions) != 7 or set(functions) != expected_functions or "GetLevel" in functions:
        raise SystemExit("unexpected DLC2MQ01 CTDA function set")

    fragments: dict[int, dict[str, str]] = {}
    for field in fields:
        path = str(field.get("field_path", ""))
        marker = "Fragments\\"
        if marker not in path:
            continue
        suffix = path.rsplit(marker, 1)[1]
        match = re.match(r"(\d+):Fragment\\\d+:([^\\]+)$", suffix)
        if not match:
            continue
        index = int(match.group(1))
        leaf = match.group(2)
        if leaf in {"Quest Stage", "Quest Stage Index", "FragmentName"}:
            fragments.setdefault(index, {})[leaf] = str(field.get("value", ""))
    fragment_map = [
        {"quest_stage": int(row["Quest Stage"]), "quest_stage_index": int(row["Quest Stage Index"]), "fragment": row["FragmentName"]}
        for _, row in sorted(fragments.items())
        if all(key in row for key in ("Quest Stage", "Quest Stage Index", "FragmentName"))
    ]
    if len(fragment_map) != 11 or sum(item["quest_stage"] == 10 for item in fragment_map) != 3:
        raise SystemExit("unexpected stage-fragment binding coverage")

    summary = {
        "evidence_id": "EV-0655",
        "query": result.get("query"),
        "record": {"plugin": "Dragonborn.esm", "form_id": "04017F8E", "editor_id": "DLC2MQ01", "signature": "QUST"},
        "scope": {"official_plugins": result["plugins"], "loaded_files": result["loaded_files"], "winning_plugin_within_official_scope": "Dragonborn.esm", "profile_order_verified": False, "runtime": preflight},
        "field_count": len(fields),
        "ctda_function_rows": functions,
        "quest_stage_fragments": fragment_map,
        "interpretation_limit": "This main-quest QUST export has no GetLevel among its seven CTDA function rows. The record contains GetDisabled, GetInCurrentLoc, GetInFaction and GetStageDone checks, which apply to their recorded conditions; the export alone does not establish the upstream initiation trigger or a vanilla level-one route.",
        "hashes": {"native_result": digest(result_path), "native_tsv": digest(tsv_path), "receipt": digest(RECEIPT), "scoped_preflight": digest(preflight_path), "session": digest(CAPTURE / "session.json")},
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0655" for item in ledger["items"]):
        raise SystemExit("EV-0655 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0655",
        "captured_utc": receipt["completed_utc"],
        "kind": "tool",
        "source": "Fresh native SSEView 4.1.5f QUST export from the isolated official five-master Skyrim AE data view.",
        "artifact": "private-local:.local/alignment/xedit-native/20261019T232821.045502Z/native-result.json",
        "sha256": digest(result_path),
        "edition": "AE",
        "runtime": "Steam SkyrimSE.exe ProductVersion 1.6.1170.0, SHA-256 " + preflight["executable_sha256"] + "; WSL2 invoked configured Windows SSEView; no game process was launched.",
        "modified_state": True,
        "lane": "offline",
        "tools": ["python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature QUST --plugin Dragonborn.esm --form-id 04017F8E", "experiments/EXP-0130-dragonborn-cultist-level-gate/register_ev0655_native_dlc2mq01.py"],
        "coverage": "Native official-five-master query returned 675 fields for Dragonborn.esm QUST DLC2MQ01 (04017F8E). It includes 11 VMAD stage-fragment bindings, with three bindings on stage 10. The seven CTDA function rows are GetDisabled, three GetInCurrentLoc, two GetInFaction and GetStageDone; no GetLevel row appears in this QUST. Loaded files were exactly the five official masters plus SkyrimSE.exe. This is an isolated official-record view, not a complete profile winner or evidence of a level-one vanilla transition.",
        "result": "PASS for native official-five-master QUST retrieval and bounded condition/fragment screen. Upstream event or Story Manager gates, attached script behavior and profile overrides remain outside this record query.",
        "local_hashes": summary["hashes"],
        "related_evidence": ["EV-0260", "EV-0653", "EV-0654"],
    })
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0655", "record": summary["record"], "field_count": len(fields), "ctda_function_rows": functions, "quest_stage_fragments": fragment_map, "hashes": summary["hashes"]}, indent=2))


if __name__ == "__main__":
    main()
