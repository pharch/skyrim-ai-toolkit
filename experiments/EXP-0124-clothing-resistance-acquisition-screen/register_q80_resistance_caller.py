#!/usr/bin/env python3
"""Register the verified GOG Actor::MagicTarget resistance call path."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "research" / "EVIDENCE.json"
RAW = ".local/ghidra/gog-query-20261019T230225Z.stdout.raw"
META = ".local/ghidra/gog-query-20261019T230225Z.meta.json"


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> None:
    raw = (ROOT / RAW).read_text(encoding="utf-8", errors="replace")
    meta = json.loads((ROOT / META).read_text(encoding="utf-8"))
    if meta.get("ok") is not True or meta.get("analysis_distribution") != "GOG":
        raise SystemExit("GOG caller query failed or belongs to another build")
    if meta.get("program_executable_path_matches_gog_binary") is not True:
        raise SystemExit("Ghidra program path does not match the identity-checked GOG image")
    checks = meta.get("checks", {})
    for key in ("program_identity_matches_gog_binary", "requested_rva_lookup", "direct_call_edge_scan", "decompilation", "script_no_error"):
        if checks.get(key) is not True:
            raise SystemExit(f"GOG caller query check failed: {key}")
    required = (
        "TARGET_RVA=0x6C68D0",
        "INDIRECT_CALL_SITE=1406c6aeb CALL qword ptr [RAX + 0x50]",
        "XREF_CALL_EDGE=1407ee740 -> 1406c68d0",
        "XREF_CALL_EDGE=140764e99 -> 1406c68d0",
        "XREF_CALL_EDGE=140765253 -> 1406c68d0",
        "param_1[0x14] + 0x50",
        "param_1 + 0x14,param_3,lVar9,0",
    )
    if any(marker not in raw for marker in required):
        raise SystemExit("reviewed target callsite or direct-caller records are missing")

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    known = {item["id"] for item in ledger["items"]}
    if "EV-0651" not in known:
        ledger["items"].append({
            "id": "EV-0651",
            "captured_utc": meta["captured_utc"],
            "kind": "native",
            "source": "Read-only GOG Ghidra decompilation and exact direct-call graph for FUN_1406c68d0, the slot+0x50 candidate from EV-0650.",
            "artifact": "private-local:" + RAW,
            "sha256": sha256(RAW),
            "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 " + meta["analysis_binary_sha256"] + "; no Steam RVA transfer or live runtime observation.",
            "lane": "mechanism_inference",
            "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py exact-RVA call-edge and decompilation query"],
            "coverage": "Function RVA 0x6C68D0; indirect call at 0x6C6AEB; three direct call edges from two caller functions; target function and one caller body decompiled; exact executable/project identity checks.",
            "result": "FUN_1406c68d0 loops target effect entries and at RVA 0x6C6AEB dispatches vtable slot +0x50 with this=param_1+0xA0, the item/effect arguments, and a null third argument. It scales accumulated effect values by that return and then queries ActorValueOwner-shaped storage at param_1+0xB8. The +0xA0 MagicTarget and +0xB8 ActorValueOwner layout matches the previously RTTI/CommonLib-mapped Actor subobjects; this is strong static evidence that the dispatch is Actor::MagicTarget::CheckResistance. Three direct incoming edges are from FUN_1407ee620 (one) and FUN_140764c30 (two). It is an effect-target resistance calculation, not evidence of a particular live attack, health-damage delta, physical HitData event, armor protection, or AVSK result.",
            "local_hashes": {RAW: sha256(RAW), META: sha256(META)},
            "related_evidence": ["EV-0400", "EV-0401", "EV-0402", "EV-0600", "EV-0650", "EV-0222", "EV-0260"],
            "modified_state": False,
        })
        LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"registered": "EV-0651", "count": len(ledger["items"]), "sha256": sha256(RAW)}, indent=2))
    else:
        print(json.dumps({"already_present": "EV-0651", "count": len(ledger["items"])}, indent=2))


if __name__ == "__main__":
    main()
