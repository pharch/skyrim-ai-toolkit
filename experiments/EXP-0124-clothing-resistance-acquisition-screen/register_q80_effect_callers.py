#!/usr/bin/env python3
"""Register the bounded parent-context and shared-helper comparison."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "research" / "EVIDENCE.json"
RAW = ".local/ghidra/gog-query-20261019T230543Z.stdout.raw"
META = ".local/ghidra/gog-query-20261019T230543Z.meta.json"


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> None:
    raw = (ROOT / RAW).read_text(encoding="utf-8", errors="replace")
    meta = json.loads((ROOT / META).read_text(encoding="utf-8"))
    if meta.get("ok") is not True or meta.get("analysis_distribution") != "GOG":
        raise SystemExit("parent-context query is not a successful GOG capture")
    checks = meta.get("checks", {})
    for key in ("program_identity_matches_gog_binary", "requested_rva_lookup", "direct_call_edge_scan", "decompilation", "script_no_error"):
        if checks.get(key) is not True:
            raise SystemExit(f"parent-context query check failed: {key}")
    required = (
        "TARGET_RVA=0x7EE620",
        "OUTGOING_CALL_EDGE=1407ee740 -> 1406c68d0",
        "OUTGOING_CALL_EDGE=1407ee79e -> 1406be430",
        "XREF_CALL_EDGE=1407ee51e -> 1407ee620",
        "XREF_CALL_EDGE=1407ee541 -> 1407ee620",
        "XREF_CALL_EDGE=1407cbc11 -> 1407ee620",
        "XREF_CALL_EDGE=1407cfc95 -> 1407ee620",
    )
    if any(marker not in raw for marker in required):
        raise SystemExit("reviewed outgoing/incoming call edges are missing")

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    known = {item["id"] for item in ledger["items"]}
    if "EV-0652" not in known:
        ledger["items"].append({
            "id": "EV-0652",
            "captured_utc": meta["captured_utc"],
            "kind": "native",
            "source": "Read-only GOG Ghidra direct-call and incoming-caller census for FUN_1407ee620, a direct caller of the resistance scaling routine and shared vector helper.",
            "artifact": "private-local:" + RAW,
            "sha256": sha256(RAW),
            "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 " + meta["analysis_binary_sha256"] + "; no live runtime result or Steam RVA transfer.",
            "lane": "mechanism_inference",
            "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py bounded call-edge/decompilation query"],
            "coverage": "FUN_1407ee620 complete direct-call census and decompilation; four incoming call edges from three functions; selected caller and direct callees decompiled.",
            "result": "FUN_1407ee620 directly calls both FUN_1406c68d0 (the Actor::MagicTarget::CheckResistance effect-scaling routine) and FUN_1406be430. Its FUN_1406be430 arguments are plVar9, lVar8, a local scalar, a build-specific float, param_1+0xF8, param_3, and flags 1/0. EV-0600 documents the distinct argument shape from mapped HitData handler FUN_1406b9df0 and shows no direct AV11/AV12/UseSkill sink in the shared vector helper. FUN_1407ee620 has three direct caller functions: FUN_1407ee360 (two call edges), FUN_1407cb9d0, and FUN_1407cf710. The shared helper call is code reuse within a broader effect/Actor route; it does not show that CheckResistance is the same incoming-hit event or that armor XP is suppressed.",
            "local_hashes": {RAW: sha256(RAW), META: sha256(META)},
            "related_evidence": ["EV-0600", "EV-0651", "EV-0295", "EV-0296", "EV-0222", "EV-0260"],
            "modified_state": False,
        })
        LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"registered": "EV-0652", "count": len(ledger["items"]), "sha256": sha256(RAW)}, indent=2))
    else:
        print(json.dumps({"already_present": "EV-0652", "count": len(ledger["items"])}, indent=2))


if __name__ == "__main__":
    main()
