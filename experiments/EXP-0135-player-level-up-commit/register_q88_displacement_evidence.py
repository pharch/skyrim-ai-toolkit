#!/usr/bin/env python3
"""Register Q88's bounded +0x325 displacement/caller/vtable discrimination."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
GHIDRA = ROOT / ".local/ghidra"
RECOVERY = ROOT / "research/RECOVERY.json"
EVIDENCE = ROOT / "research/EVIDENCE.json"
SUMMARY = ROOT / ".local/alignment/transactions/TX-20261020-0007/q88-displacement-collision.json"
BUILD_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"

CAPTURES = {
    "displacement_scan": ("20261020T045649Z", "memory_displacement_search", "0x325"),
    "unbounded_store_context": ("20261020T045928Z", "address_context_query", "0x9628B9"),
    "set_true_wrapper_caller": ("20261020T050050Z", "direct_call_edge_census", "0x6C8D10"),
    "statsmenu_vtable_prefix_64": ("20261020T050410Z", "pointer_table_query", "0x19026C0"),
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def capture_manifest() -> tuple[dict, dict[str, str]]:
    manifests: dict[str, dict] = {}
    texts: dict[str, str] = {}
    for name, (stamp, mode, requested) in CAPTURES.items():
        stdout = GHIDRA / f"gog-query-{stamp}.stdout.raw"
        metadata_path = GHIDRA / f"gog-query-{stamp}.meta.json"
        metadata = load(metadata_path)
        checks = metadata.get("checks", {})
        if (metadata.get("ok") is not True or metadata.get("read_only") is not True or
                metadata.get("auto_analysis_disabled") is not True or
                metadata.get("analysis_binary_product_version") != "1.6.1179" or
                metadata.get("analysis_binary_sha256") != BUILD_SHA or
                metadata.get("query_mode") != mode or
                metadata.get("stdout_sha256") != digest(stdout) or
                not checks or not all(value is True for value in checks.values())):
            raise SystemExit(f"identity/read-only/hash/completion validation failed: {name}")
        if mode == "memory_displacement_search":
            if metadata.get("requested_search_displacement", "").lower() != requested.lower():
                raise SystemExit("displacement query mismatch")
        elif mode == "address_context_query":
            if metadata.get("requested_address_rva", "").lower() != requested.lower():
                raise SystemExit("address query mismatch")
        elif mode == "direct_call_edge_census":
            if metadata.get("requested_rva", "").lower() != requested.lower():
                raise SystemExit("caller query mismatch")
        elif mode == "pointer_table_query":
            if (metadata.get("requested_pointer_table_rva", "").lower() != requested.lower() or
                    metadata.get("requested_pointer_count") != 64):
                raise SystemExit("StatsMenu table query mismatch")
        manifests[name] = {
            "stdout": f"private-local:{stdout.relative_to(ROOT).as_posix()}",
            "stdout_sha256": digest(stdout),
            "metadata": f"private-local:{metadata_path.relative_to(ROOT).as_posix()}",
            "metadata_sha256": digest(metadata_path),
            "query_mode": mode,
            "requested": requested,
            "checks": checks,
        }
        texts[name] = stdout.read_text(encoding="utf-8", errors="replace")
    return manifests, texts


def main() -> None:
    recovery = load(RECOVERY)
    if (recovery.get("status"), recovery.get("transaction_id"), recovery.get("frontier_id")) != (
            "running", "TX-20261020-0007", "Q-0088"):
        raise SystemExit("Q88 is not the active transaction")

    manifests, texts = capture_manifest()
    scan = texts["displacement_scan"]
    address = texts["unbounded_store_context"]
    caller = texts["set_true_wrapper_caller"]
    table = texts["statsmenu_vtable_prefix_64"]

    required_scan = (
        "OFFSET_QUERY=0x325", "OFFSET_ACCESS_COUNT=5", "OFFSET_MATCHED_FUNCTION_COUNT=4",
        "OFFSET_WRITER_CANDIDATE=FUN_1406ebea0", "OFFSET_WRITER_CANDIDATE=FUN_140717c50",
        "OFFSET_ACCESS=address:14096216c rva:0x96216C function:FUN_1409611e0",
        "OFFSET_ACCESS=address:1409628b9 rva:0x9628B9 function:<no-function>",
        "OFFSET_SCAN_COMPLETE=true", "OFFSET_WRITER_ANALYSIS_COMPLETE=true",
    )
    if not all(marker in scan for marker in required_scan):
        raise SystemExit("the +0x325 scan contents or completion markers changed")
    required_address = (
        "ADDRESS_FUNCTION_LOOKUP=<no-function>", "ADDRESS_TARGET_XREF_COUNT=0",
        "ADDRESS_CONTEXT_INSTRUCTION=1409628b9 MOV MOV byte ptr [RAX + 0x325],0x1",
    )
    if not all(marker in address for marker in required_address):
        raise SystemExit("the unbounded +0x325 store context changed")
    required_caller = (
        "XREF_CALL_EDGE=1405d6441 -> 1406c8d10", "XREF_CALL_COUNT=1",
        "OUTGOING_DIRECT_CALL_EDGE=1406c8eef -> 140717c50",
        "char FUN_1406c8d10", "InventoryChanges::FindBestSoulGemVisitor::vftable",
        "You_have_captured_a_soul", "FUN_140717c50();",
    )
    if not all(marker in caller for marker in required_caller):
        raise SystemExit("the set-true wrapper caller no longer matches the bounded soul-capture trace")
    if "POINTER_TABLE_READ_COUNT=64" not in table or "POINTER_TABLE_SCAN_COMPLETE=true" not in table:
        raise SystemExit("the requested StatsMenu vtable prefix is incomplete")
    pointers = re.findall(r"POINTER_TABLE_ENTRY=.*?value:(0x[0-9a-fA-F]+)", table)
    if len(pointers) != 64 or any(value.lower() == "0x1409628b0" for value in pointers):
        raise SystemExit("StatsMenu vtable prefix contains the candidate or is incomplete")

    captured = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary = {
        "captured_utc": captured,
        "transaction": "TX-20261020-0007",
        "gog_build": {
            "product_version": "1.6.1179.0",
            "sha256": BUILD_SHA,
            "steam_rvas_used": False,
        },
        "captures": manifests,
        "bounded_observations": {
            "displacement_scan": "The complete analyzed-memory-operand scan found five +0x325 operands across four functions: byte-zero write at RVA 0x6EC2F4 in FUN_1406EBEA0; byte-one write at 0x717C59 in FUN_140717C50; compare in FUN_140717C70; StatsMenu ProcessMessage read at 0x96216C; and a byte-one write at 0x9628B9 with no function owner. Scan completion/candidate-analysis markers are true.",
            "set_true_writer_context": "FUN_140717C50's only analyzed direct caller is FUN_1406C8D10. That caller uses InventoryChanges::FindBestSoulGemVisitor in an inventory/soul-capture route and has Player-facing 'You have captured a soul' feedback. The capture does not identify the target object's dynamic class or prove that the +0x325 byte is the StatsMenu member.",
            "unbounded_store": "RVA 0x9628B9 loads a pointer through [RCX+0x18], checks it, stores byte 1 at [RAX+0x325], then returns. Ghidra reports no function owner and zero analyzed xrefs for the queried address. The store is not in the captured StatsMenu constructor body.",
            "statsmenu_vtable_prefix": "The 64 requested pointer values from the RTTI-identified StatsMenu table at RVA 0x19026C0 do not include candidate address 0x9628B0. The capture has no established table-end marker; this is only a prefix result and does not exclude a later slot, a nonvirtual helper, or indirect dispatch.",
        },
        "interpretation": "Numeric displacement matching merges accesses to object-local offsets without proving receiver identity. The soul-capture route and StatsMenu::ProcessMessage may use different objects even though both access offset +0x325. No producer for the StatsMenu instance's readiness byte is identified by this scan, and no timing relation between its kUpdate branch and user level-up input follows.",
        "limits": "GOG static evidence only; no Steam 1.6.1170.0 mapping or natural pending/interface-open/accepted observation. The two extra level-writer data-reference tables remain unclassified metadata candidates with no analyzed table-base refs; their runtime use is unresolved. The StatsMenu vtable read covers 64 entries, not a confirmed full table boundary.",
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    ledger = load(EVIDENCE)
    if any(row.get("id") == "EV-0695" for row in ledger.get("items", [])):
        raise SystemExit("EV-0695 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0695",
        "captured_utc": captured,
        "kind": "native",
        "source": "Identity-checked read-only GOG memory-displacement scan for +0x325, exact address context, complete direct caller census for the set-true candidate, and bounded 64-entry RTTI-identified StatsMenu vtable read.",
        "artifact": f"private-local:{SUMMARY.relative_to(ROOT).as_posix()}",
        "sha256": digest(SUMMARY),
        "edition": "AE",
        "runtime": "GOG analysis build only: ProductVersion 1.6.1179.0, executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Steam 1.6.1170.0 is separate [EV-0109]; no RVA transfer.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "python3 scripts/python_env.py run tools/ghidra_probe.py --search-displacement 0x325 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --address-rva 0x9628b9 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x6c8d10 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --pointer-table-rva 0x19026c0 --pointer-count 64 --timeout 600",
            "python3 scripts/python_env.py run experiments/EXP-0135-player-level-up-commit/register_q88_displacement_evidence.py",
        ],
        "coverage": "The GOG +0x325 scan and follow-up caller/vtable checks are bounded and complete for the requested scopes. A soul-capture-related direct caller reaches one set-true writer, but target-class identity is unresolved. The separate 0x9628B9 store has no analyzed function owner or xrefs and is absent from the first 64 values read from the StatsMenu vtable at RVA 0x19026C0.",
        "result": "PASS for the bounded candidate discrimination; no StatsMenu +0x325 field producer, level-up input relation, or earlier Player level writer is identified. Equal numeric offsets cannot be treated as one cross-object field. The remaining natural timing discriminator is EV-0260; unresolved data references for FUN_140355210/FUN_140356A10 remain open.",
        "local_hashes": {name: item["stdout_sha256"] for name, item in manifests.items()},
        "related_evidence": ["EV-0109", "EV-0260", "EV-0691", "EV-0692", "EV-0693"],
    })
    EVIDENCE.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0695", "summary_sha256": digest(SUMMARY), "captures": list(manifests)}, indent=2))


if __name__ == "__main__":
    main()
