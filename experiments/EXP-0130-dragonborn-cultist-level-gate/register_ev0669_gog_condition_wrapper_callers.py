#!/usr/bin/env python3
"""Register the read-only incoming-call census for the GOG condition wrapper."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "research/EVIDENCE.json"
STDOUT = ROOT / ".local/ghidra/gog-query-20261020T001940Z.stdout.raw"
META = ROOT / ".local/ghidra/gog-query-20261020T001940Z.meta.json"
NOTE = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-gog-condition-wrapper-callers.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    ids = {item["id"] for item in ledger["items"]}
    if not {"EV-0657", "EV-0667", "EV-0668"} <= ids:
        raise SystemExit("native condition and GOG evaluator evidence must exist first")
    if "EV-0669" in ids:
        raise SystemExit("EV-0669 already exists; refusing duplicate registration")
    meta = json.loads(META.read_text(encoding="utf-8"))
    expected_exe = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
    if meta.get("requested_rva") != "0x49FA30" or meta.get("analysis_binary_sha256") != expected_exe or not meta.get("ok"):
        raise SystemExit("wrapper caller census target or binary identity mismatch")
    if meta.get("incoming_callers") not in (None, 32) or not meta.get("read_only"):
        raise SystemExit("unexpected query cap or non-read-only mode")

    stdout_hash = digest(STDOUT)
    meta_hash = digest(META)
    note = {
        "captured_utc": meta["captured_utc"],
        "target": {"rva": "0x49FA30", "product_version": meta["analysis_binary_product_version"], "sha256": meta["analysis_binary_sha256"]},
        "query": {"mode": meta["query_mode"], "follow_incoming_calls": meta["follow_incoming_calls"], "incoming_caller_functions": 22, "complete_call_edge_census": meta["checks"]["incoming_call_trace"]},
        "wrapper_disassembly": {
            "artifact": ".local/ghidra/gog-query-20261020T001940Z.stdout.raw",
            "preserved_first_argument": "The wrapper does not overwrite RCX between entry and CALL 0x14049FBB0, so its first argument reaches the condition-list aggregator in the GOG disassembly.",
            "stack_context": "The wrapper stores RDX and R8 at [RSP+0x20] and [RSP+0x28], passes the stack address in RDX, and passes [RSP+0x78] in R8; these are the condition-evaluation context/output setup visible in the wrapper.",
            "decompiler_caveat": "The decompiler renders the aggregator's first argument as literal zero, which conflicts with the instruction sequence preserving RCX. Use the raw disassembly for this argument; do not rely on the decompiler expression at that call.",
        },
        "caller_review": {
            "direct_callers": [
                "FUN_1406e00a0", "FUN_1403b0b70", "FUN_14066e480", "FUN_140258bc0", "FUN_140310820", "FUN_140325aa0", "FUN_140325b00", "FUN_140346380", "FUN_14038f150", "FUN_1403b32a0", "FUN_1405aedc0", "FUN_140693f00", "FUN_14096a020", "FUN_140963830", "FUN_14096e2f0", "FUN_14096d7c0", "FUN_14096d970", "FUN_140a030f0", "FUN_140146130", "FUN_140258970", "FUN_14033ae20", "FUN_1403204d0"
            ],
            "bounded_result": "The incoming callers include generic condition checks in several engine/UI/action contexts. The capture does not bind any caller to DLC2WE09's record-specific condition list or establish the QUST evaluation timing.",
        },
        "interpretation_limit": "GOG 1.6.1179.0 static caller census only. It is not a Steam RVA mapping, runtime trace, quest-start result, or evidence that the QUST conditions are evaluated at a particular lifecycle point.",
        "hashes": {"stdout": stdout_hash, "metadata": meta_hash},
    }
    NOTE.parent.mkdir(parents=True, exist_ok=True)
    NOTE.write_text(json.dumps(note, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    note_hash = digest(NOTE)
    ledger["items"].append({
        "id": "EV-0669", "captured_utc": meta["captured_utc"], "kind": "tool",
        "source": "Existing configured GOG Ghidra project, read-only caller census and disassembly of Address Library-resolved TESCondition::IsTrue wrapper candidate RVA 0x49FA30.",
        "artifact": "private-local:.local/ghidra/gog-query-20261020T001940Z.stdout.raw",
        "sha256": stdout_hash, "edition": "AE", "runtime": "GOG SkyrimSE.exe 1.6.1179.0, SHA-256 " + expected_exe,
        "modified_state": False, "lane": "offline",
        "tools": ["python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x49FA30 --list-call-edges --follow-incoming-calls 32", "experiments/EXP-0130-dragonborn-cultist-level-gate/register_ev0669_gog_condition_wrapper_callers.py"],
        "coverage": "The exact GOG wrapper disassembly preserves RCX into its direct call to condition-list evaluator RVA 0x49FBB0; a decompiler literal-zero first argument is not consistent with this instruction sequence. The bounded incoming census has 22 direct callers. The captured caller bodies do not identify the DLC2WE09 QUST condition list or the point at which it is evaluated.",
        "result": "PASS for GOG wrapper disassembly and 22-caller census. The lifecycle point for DLC2WE09's conditions remains unresolved; this is an explicit no-edge result, not a global statement about all callers or another executable.",
        "local_hashes": {"stdout": stdout_hash, "metadata": meta_hash, "note": note_hash, "adapter": meta["adapter_sha256"], "query_script": meta["query_script_sha256"]},
        "related_evidence": ["EV-0657", "EV-0667", "EV-0668"],
    })
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0669", "stdout_sha256": stdout_hash, "metadata_sha256": meta_hash, "note_sha256": note_hash, "incoming_callers": 22}, indent=2))


if __name__ == "__main__":
    main()
