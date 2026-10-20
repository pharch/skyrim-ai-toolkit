#!/usr/bin/env python3
"""Register GOG Address Library identity and read-only condition evaluator evidence."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "research/EVIDENCE.json"
ADDRESS_RESULT = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-condition-evaluator-gog-addresses.json"
GHIDRA_STDOUT = ROOT / ".local/ghidra/gog-query-20261020T001354Z.stdout.raw"
GHIDRA_META = ROOT / ".local/ghidra/gog-query-20261020T001354Z.meta.json"
NOTE = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-gog-condition-evaluator-note.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    known = {item["id"] for item in ledger["items"]}
    if not {"EV-0657", "EV-0665", "EV-0666"} <= known:
        raise SystemExit("record bytes, native conditions, and CTDA schema evidence must be registered first")
    if {"EV-0667", "EV-0668"} & known:
        raise SystemExit("refusing duplicate evidence registration")

    address = json.loads(ADDRESS_RESULT.read_text(encoding="utf-8"))
    meta = json.loads(GHIDRA_META.read_text(encoding="utf-8"))
    expected_exe = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
    expected_lib = "3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e"
    if address.get("gog_product_version") != "1.6.1179.0" or address.get("gog_executable_sha256") != expected_exe:
        raise SystemExit("Address Library resolver is not bound to the expected GOG executable")
    if address.get("address_library_sha256") != expected_lib or address.get("address_library_internal_version") != "1.6.1179.0":
        raise SystemExit("Address Library identity mismatch")
    if address.get("symbols", {}).get("TESCondition::IsTrue") != {"ae_id": 29888, "rva": "0x49FA30"}:
        raise SystemExit("TESCondition::IsTrue symbol resolution mismatch")
    if address.get("symbols", {}).get("TESConditionItem::IsTrue") != {"ae_id": 29924, "rva": "0x4A0720"}:
        raise SystemExit("TESConditionItem::IsTrue symbol resolution mismatch")
    if meta.get("requested_rva") != "0x49FBB0" or meta.get("analysis_binary_sha256") != expected_exe or not meta.get("ok"):
        raise SystemExit("Ghidra query identity, target, or completion mismatch")
    if not meta.get("program_executable_path_matches_gog_binary") or not meta.get("read_only"):
        raise SystemExit("Ghidra query is not a read-only query of the matching GOG program")

    captured = datetime.now(timezone.utc).isoformat()
    address_hash = digest(ADDRESS_RESULT)
    stdout_hash = digest(GHIDRA_STDOUT)
    meta_hash = digest(GHIDRA_META)
    note = {
        "captured_utc": captured,
        "address_resolution": {
            "artifact": ".local/alignment/transactions/TX-20261019-0002/q81-condition-evaluator-gog-addresses.json",
            "sha256": address_hash,
            "gog_product_version": address["gog_product_version"],
            "gog_executable_sha256": address["gog_executable_sha256"],
            "address_library_internal_version": address["address_library_internal_version"],
            "address_library_sha256": address["address_library_sha256"],
            "symbols": address["symbols"],
            "symbol_name_source": address["symbol_source"],
            "symbol_name_source_revision": "Unpinned CommonLibSSE-NG main branch at capture; used only as an address-label lead, not as evaluator-body evidence.",
        },
        "ghidra_query": {
            "stdout_artifact": ".local/ghidra/gog-query-20261020T001354Z.stdout.raw",
            "stdout_sha256": stdout_hash,
            "metadata_artifact": ".local/ghidra/gog-query-20261020T001354Z.meta.json",
            "metadata_sha256": meta_hash,
            "rva": "0x49FBB0",
            "program_identity": {"product_version": meta["analysis_binary_product_version"], "sha256": meta["analysis_binary_sha256"]},
            "query_mode": meta["query_mode"],
            "read_only": meta["read_only"],
            "auto_analysis_disabled": meta["auto_analysis_disabled"],
            "direct_caller": "TESCondition::IsTrue address-library candidate wrapper at RVA 0x49FA30, with a direct call into 0x49FBB0; GOG build only.",
        },
        "observed_code": {
            "function": "FUN_14049fbb0 at RVA 0x49FBB0",
            "condition_eval_callee": "FUN_1404a0720 at RVA 0x4A0720; two direct call sites in the queried body",
            "linked_list_iteration": "The body follows the item next pointer and tests bit 0 at condition data offset 0x30.",
            "or_group_behavior": "A condition with bit 0 set opens/continues a pending OR run. The evaluator may short-circuit later terms once a term succeeds; it closes the run before AND-combining it with the prior accumulator when it reaches an unflagged item or the list end.",
            "record_application": "The five QUST\\9 Conditions rows in EV-0657 are GetRandomPercent, GetStage MQ105, GetStage DLC2MQ06, GetLevel, and GetInCurrentLoc. In EV-0665, only GetLevel (0x61) and the following location predicate (0x01) set bit 0; the list ends after the location row. Under the captured GOG evaluator, those two rows form a trailing OR run, separate from and AND-combined with earlier unflagged conditions.",
        },
        "interpretation_limits": [
            "The query is from GOG AE 1.6.1179.0 and its RVAs are not transferred to Steam AE 1.6.1170.0.",
            "The Steam native official-five-master record is not a profile-specific winner; the complete selected profile order is unavailable.",
            "This identifies condition-list grouping, not when DLC2WE09 Conditions are evaluated, whether the quest starts at level one, or whether a vanilla event occurred.",
            "The CommonLib symbol label comes from an unpinned main branch; the Ghidra function body and GOG binary identity are preserved independently.",
        ],
        "source_urls": [
            "https://github.com/CharmedBaryon/CommonLibSSE-NG/blob/main/src/RE/T/TESCondition.cpp#L493-L500",
            "https://github.com/TES5Edit/TES5Edit/blob/f8b209cb5bc9efcb2cd8c4aa8694de3227c3d783/Core/wbDefinitionsCommon.pas#L3254-L3332",
        ],
    }
    NOTE.parent.mkdir(parents=True, exist_ok=True)
    NOTE.write_text(json.dumps(note, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    note_hash = digest(NOTE)
    ledger["items"].extend([
        {
            "id": "EV-0667", "captured_utc": captured, "kind": "tool",
            "source": "Matching GOG Address Library 1.6.1179.0 decoded with the repository's retained legacy Address Library resolver; function-name association cross-checked against CommonLibSSE-NG TESCondition.cpp (mutable main branch, used only as a label lead).",
            "artifact": "private-local:.local/alignment/transactions/TX-20261019-0002/q81-condition-evaluator-gog-addresses.json",
            "sha256": address_hash, "edition": "AE", "runtime": "GOG SkyrimSE.exe 1.6.1179.0, SHA-256 " + expected_exe,
            "modified_state": False, "lane": "offline",
            "tools": ["experiments/EXP-0130-dragonborn-cultist-level-gate/resolve_q81_condition_evaluator.py", "experiments/EXP-0130-dragonborn-cultist-level-gate/register_ev0667_ev0668_gog_condition_evaluator.py"],
            "coverage": "Address Library internal version and SHA-256 are recorded. AE IDs 29888 and 29924 resolve, for GOG build only, to RVAs 0x49FA30 and 0x4A0720. CommonLib source names are not treated as proof of function body semantics.",
            "result": "PASS for exact GOG Address Library identity and address resolution. No Steam RVA or Steam function identity is inferred.",
            "local_hashes": {"resolver_result": address_hash, "address_library": expected_lib},
            "related_evidence": ["EV-0657", "EV-0665"],
        },
        {
            "id": "EV-0668", "captured_utc": meta["captured_utc"], "kind": "tool",
            "source": "Existing configured GOG Ghidra project, read-only targeted disassembly/decompilation of RVA 0x49FBB0 in SkyrimSE.exe 1.6.1179.0.",
            "artifact": "private-local:.local/ghidra/gog-query-20261020T001354Z.stdout.raw",
            "sha256": stdout_hash, "edition": "AE", "runtime": "GOG SkyrimSE.exe 1.6.1179.0, SHA-256 " + expected_exe,
            "modified_state": False, "lane": "offline",
            "tools": ["python3 scripts/python_env.py run tools/ghidra_probe.py query --rva 0x49FBB0 --edges all", "experiments/EXP-0130-dragonborn-cultist-level-gate/register_ev0667_ev0668_gog_condition_evaluator.py"],
            "coverage": "The identity-checked GOG function FUN_14049fbb0 iterates condition-list nodes, tests the OR flag bit, calls FUN_1404a0720 for item evaluation, accumulates consecutive OR-flagged terms as a pending OR group, and combines that group with earlier unflagged conditions. The capture includes disassembly, decompilation, direct caller/callee edges and metadata; GOG build only.",
            "result": "PASS for the bounded GOG condition-list evaluator behavior. Applied to EV-0657/EV-0665, the GetLevel >=25 row and following GetInCurrentLoc row form a trailing OR group in GOG 1.6.1179.0. This is mechanism inference for those serialized rows, not a Steam runtime or quest-start result.",
            "local_hashes": {"stdout": stdout_hash, "metadata": meta_hash, "adapter": meta["adapter_sha256"], "query_script": meta["query_script_sha256"], "address_resolution": address_hash, "note": note_hash},
            "related_evidence": ["EV-0657", "EV-0658", "EV-0660", "EV-0661", "EV-0665", "EV-0666", "EV-0667"],
        },
    ])
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": ["EV-0667", "EV-0668"], "note_sha256": note_hash, "address_sha256": address_hash, "ghidra_stdout_sha256": stdout_hash, "ghidra_metadata_sha256": meta_hash}, indent=2))


if __name__ == "__main__":
    main()
