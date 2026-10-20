#!/usr/bin/env python3
"""Register the identity-checked, uncapped targeted slot-call context scan."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "research" / "EVIDENCE.json"
RAW = ".local/ghidra/gog-query-20261019T225937Z.stdout.raw"
META = ".local/ghidra/gog-query-20261019T225937Z.meta.json"


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> None:
    raw = (ROOT / RAW).read_text(encoding="utf-8", errors="replace")
    meta = json.loads((ROOT / META).read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    required = {
        "program_identity_matches_gog_binary": True,
        "requested_displacement": True,
        "displacement_scan_complete": True,
        "script_no_error": True,
    }
    if meta.get("ok") is not True or meta.get("analysis_distribution") != "GOG":
        raise SystemExit("capture is not a successful GOG query")
    if any(checks.get(key) is not value for key, value in required.items()):
        raise SystemExit("GOG identity or full displacement scan check failed")
    if meta.get("requested_search_displacement") != "0x50":
        raise SystemExit("capture is not the requested slot +0x50 scan")
    if "OFFSET_INSTRUCTION_COUNT=5654579" not in raw or "OFFSET_ACCESS_COUNT=17530" not in raw:
        raise SystemExit("full scan counters differ from the reviewed output")
    if "OFFSET_ACCESSES_PRINTED=2048" not in raw or "OFFSET_ACCESS_OUTPUT_LIMIT=2048" not in raw:
        raise SystemExit("regular offset output cap differs from the reviewed output")
    context_count = raw.count("OFFSET_INDIRECT_CALLSITE_CONTEXT=")
    if context_count != 2400:
        raise SystemExit(f"targeted call context count changed: {context_count}")
    candidate = "rva:0x6C6AEB function:FUN_1406c68d0"
    if candidate not in raw or "LEA RCX,[RSI + 0xa0]" not in raw:
        raise SystemExit("reviewed candidate MagicTarget-shaped call context is missing")

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    known = {item["id"] for item in ledger["items"]}
    if "EV-0650" not in known:
        ledger["items"].append({
            "id": "EV-0650",
            "captured_utc": meta["captured_utc"],
            "kind": "native",
            "source": "Read-only whole-program GOG memory-displacement scan for slot offset +0x50, extended to emit linear context for every matched indirect call operand.",
            "artifact": "private-local:" + RAW,
            "sha256": sha256(RAW),
            "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 " + meta["analysis_binary_sha256"] + "; separate from verified Steam AE 1.6.1170.0.",
            "lane": "mechanism_inference",
            "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py", "existing GOG project read-only query"],
            "coverage": "Complete 5,654,579-instruction displacement scan; 17,530 matching memory operands across 11,187 functions; 2,400 uncapped linear contexts for matched indirect call operands across 1,400 functions. General operand detail remains capped at 2,048 entries.",
            "result": "The identity-checked scan finds a candidate at RVA 0x6C6AEB in FUN_1406c68d0: the linear context forms RCX from RSI+0xA0, loads its vtable, and calls slot +0x50. This matches the shape of Actor::MagicTarget slot 0x0A mapped to CheckResistance, but RSI's receiver type and the caller's runtime role are not established here. The search is a candidate census, not a global negative for other call forms or Steam behavior.",
            "local_hashes": {RAW: sha256(RAW), META: sha256(META)},
            "related_evidence": ["EV-0400", "EV-0401", "EV-0402", "EV-0649", "EV-0260"],
            "modified_state": False,
        })
        LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"registered": "EV-0650", "count": len(ledger["items"]), "sha256": sha256(RAW)}, indent=2))
    else:
        print(json.dumps({"already_present": "EV-0650", "count": len(ledger["items"])}, indent=2))


if __name__ == "__main__":
    main()
