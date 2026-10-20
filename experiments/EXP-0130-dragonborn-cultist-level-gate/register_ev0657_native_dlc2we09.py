#!/usr/bin/env python3
"""Validate and register the native five-master DLC2WE09 QUST export."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / ".local/alignment/xedit-native/20261019T233530.299420Z"
RECEIPT = ROOT / ".local/xedit-native/latest.json"
LEDGER = ROOT / "research/EVIDENCE.json"
SUMMARY = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-we09-native-summary.json"
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
    if receipt.get("status") != "PASS" or receipt.get("record", {}).get("editor_id") != "DLC2WE09":
        raise SystemExit("native receipt did not pass for DLC2WE09")
    if receipt.get("record", {}).get("source_plugin") != "Dragonborn.esm" or receipt.get("record", {}).get("signature") != "QUST":
        raise SystemExit("native receipt record identity mismatch")
    if result.get("plugins") != OFFICIAL_PLUGINS or result.get("loaded_files") != EXPECTED_LOADED:
        raise SystemExit("native result did not use the exact official five-master scope")
    if preflight.get("edition") != "AE" or preflight.get("runtime") != "1.6.1170" or preflight.get("full_order_verified") is not False:
        raise SystemExit("native scope/runtime preflight mismatch")
    if digest(result_path) != receipt.get("result_json_sha256") or digest(tsv_path) != receipt.get("tsv_sha256"):
        raise SystemExit("native capture hash differs from the integrity receipt")

    fields = result.get("fields", [])
    identities = {
        (field.get("source_plugin"), field.get("form_id"), field.get("editor_id"), field.get("signature"), field.get("winning_plugin"))
        for field in fields
    }
    if identities != {("Dragonborn.esm", "040331C0", "DLC2WE09", "QUST", "Dragonborn.esm")} or len(fields) != 742:
        raise SystemExit("unexpected DLC2WE09 identity or field coverage")

    functions = [field.get("value", "") for field in fields if str(field.get("field_path", "")).endswith(":Function")]
    expected_functions = Counter({
        "GetIsVoiceType": 1, "GetRandomPercent": 1, "GetStage": 3, "GetLevel": 1,
        "GetInCurrentLoc": 1, "GetIsReference": 4, "IsLinkedTo": 2, "HasRefType": 2,
    })
    if Counter(functions) != expected_functions:
        raise SystemExit("unexpected DLC2WE09 CTDA function coverage")

    level_path = next(
        str(field["field_path"]) for field in fields
        if str(field.get("field_path", "")).endswith(":Function") and field.get("value") == "GetLevel"
    )
    condition_prefix = level_path.rsplit("\\", 1)[0]
    sibling_values = {
        str(field.get("field_path", ""))[len(condition_prefix) + 1:]: str(field.get("value", ""))
        for field in fields if str(field.get("field_path", "")).startswith(condition_prefix + "\\")
    }
    if sibling_values.get("2:Comparison Value") != "25.000000" or sibling_values.get("0:Type") != "11010000":
        raise SystemExit("unexpected GetLevel condition value or raw Type bytes")
    if sibling_values.get("7:Run On") != "Reference" or "PlayerRef [PLYR:00000014]" not in sibling_values.get("8:Reference", ""):
        raise SystemExit("GetLevel condition is not explicitly bound to PlayerRef")

    fragments: dict[int, dict[str, str]] = {}
    for field in fields:
        path = str(field.get("field_path", ""))
        marker = "Fragments\\"
        if marker not in path:
            continue
        match = re.match(r"(\d+):Fragment\\\d+:([^\\]+)$", path.rsplit(marker, 1)[1])
        if match and match.group(2) in {"Quest Stage", "Quest Stage Index", "FragmentName"}:
            fragments.setdefault(int(match.group(1)), {})[match.group(2)] = str(field.get("value", ""))
    fragment_map = [
        {"quest_stage": int(row["Quest Stage"]), "quest_stage_index": int(row["Quest Stage Index"]), "fragment": row["FragmentName"]}
        for _, row in sorted(fragments.items())
        if all(key in row for key in ("Quest Stage", "Quest Stage Index", "FragmentName"))
    ]
    if len(fragment_map) != 4 or not any(row == {"quest_stage": 10, "quest_stage_index": 0, "fragment": "Fragment_5"} for row in fragment_map):
        raise SystemExit("unexpected DLC2WE09 stage-fragment mapping")

    summary = {
        "evidence_id": "EV-0657",
        "query": result.get("query"),
        "record": {"plugin": "Dragonborn.esm", "form_id": "040331C0", "editor_id": "DLC2WE09", "signature": "QUST"},
        "scope": {"official_plugins": result["plugins"], "loaded_files": result["loaded_files"], "winning_plugin_within_official_scope": "Dragonborn.esm", "profile_order_verified": False, "runtime": preflight},
        "field_count": len(fields),
        "ctda_function_rows": functions,
        "level_condition": {"field_path": level_path, "comparison_value": sibling_values["2:Comparison Value"], "raw_type": sibling_values["0:Type"], "run_on": sibling_values["7:Run On"], "reference": sibling_values["8:Reference"], "operator": "not decoded in this registration"},
        "quest_level_conditions": {
            "GetRandomPercent": "comparison operand DLC2WE09Chance GLOB 04033C24",
            "GetStage": ["160.000000 on MQ105 QUST 000242BA (Update.esm)", "550.000000 on DLC2MQ06 QUST 040179D7 (Dragonborn.esm)"],
            "GetInCurrentLoc": "DLC2SolstheimLocation LCTN 04016E2A",
        },
        "quest_stage_fragments": fragment_map,
        "event_type": "SCPT",
        "interpretation_limit": "The native official-five-master QUST export contains one GetLevel condition with comparison value 25.000000, raw Type 11010000 and explicit PlayerRef reference. This registration preserves the raw Type but does not decode its comparator or prove when QUST Conditions are evaluated on a natural start. It is not a profile-specific winner or vanilla runtime result.",
        "hashes": {"native_result": digest(result_path), "native_tsv": digest(tsv_path), "receipt": digest(RECEIPT), "scoped_preflight": digest(preflight_path), "session": digest(CAPTURE / "session.json")},
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0657" for item in ledger["items"]):
        raise SystemExit("EV-0657 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0657",
        "captured_utc": "2026-10-19T23:35:30.299420+00:00",
        "kind": "tool",
        "source": "Fresh native SSEView 4.1.5f QUST export from the isolated official five-master Skyrim AE data view.",
        "artifact": "private-local:.local/alignment/xedit-native/20261019T233530.299420Z/native-result.json",
        "sha256": digest(result_path),
        "edition": "AE",
        "runtime": "Steam SkyrimSE.exe ProductVersion 1.6.1170.0, SHA-256 " + preflight["executable_sha256"] + "; WSL2 invoked configured Windows SSEView; no game process was launched.",
        "modified_state": True,
        "lane": "offline",
        "tools": ["python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature QUST --plugin Dragonborn.esm --editor-id DLC2WE09", "experiments/EXP-0130-dragonborn-cultist-level-gate/register_ev0657_native_dlc2we09.py"],
        "coverage": "Native official-five-master query returned 742 fields for Dragonborn.esm QUST DLC2WE09, FormID 040331C0. Its one GetLevel condition is in QUST\\9 Conditions: Comparison Value 25.000000, raw Type 11010000, Run On Reference, Reference PlayerRef. Other quest conditions include GetRandomPercent using DLC2WE09Chance (04033C24), GetStage on MQ105 at 160 and DLC2MQ06 at 550, plus GetInCurrentLoc for DLC2SolstheimLocation. Stage 10 index 0 maps to Fragment_5. Native scope loaded exactly five official masters plus SkyrimSE.exe; no complete profile order or live start was captured.",
        "result": "PASS for native official-five-master QUST retrieval and bounded level-condition screen. The comparator encoded by raw Type 11010000 and the runtime evaluation point of QUST Conditions remain unresolved.",
        "local_hashes": summary["hashes"],
        "related_evidence": ["EV-0260", "EV-0653", "EV-0654", "EV-0655", "EV-0656"],
    })
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0657", "record": summary["record"], "field_count": len(fields), "ctda_function_counts": dict(Counter(functions)), "level_condition": summary["level_condition"], "quest_stage_fragments": fragment_map, "hashes": summary["hashes"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
