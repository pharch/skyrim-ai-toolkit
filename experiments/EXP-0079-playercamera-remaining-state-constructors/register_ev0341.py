#!/usr/bin/env python3
"""Register the remaining PlayerCamera state constructor and callback traces."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0079-playercamera-remaining-state-constructors"
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"

QUERIES = [
    ("20261018T043420Z", ["DECOMPILATION_BEGIN=FUN_1408ebed0", "VATSCameraState::vftable",
     "CALLER_DECOMPILATION_BEGIN=FUN_1408e4240", "CALLER_DECOMPILATION_END=FUN_1408e4240"]),
    ("20261018T043526Z", ["POINTER_TABLE_ENTRY=index:2 address:1418f16f0 value:0x140244650",
     "POINTER_TABLE_READ_COUNT=12", "POINTER_TABLE_SCAN_COMPLETE=true"]),
    ("20261018T043626Z", ["DECOMPILATION_BEGIN=FUN_1408eb750", "TweenMenuCameraState::vftable",
     "CALLER_DECOMPILATION_BEGIN=FUN_1408e4240", "CALLER_DECOMPILATION_END=FUN_1408e4240"]),
    ("20261018T043731Z", ["POINTER_TABLE_ENTRY=index:2 address:1418f1678 value:0x1408EB830",
     "POINTER_TABLE_READ_COUNT=10", "POINTER_TABLE_SCAN_COMPLETE=true"]),
    ("20261018T043825Z", ["TARGET_RVA=0x8EB830", "MOV dword ptr [RDX + 0x13c], EAX",
     "OUTGOING_DIRECT_CALL_EDGE_COUNT=0", "INDIRECT_CALL_SITE_COUNT=0"]),
    ("20261018T043918Z", ["DECOMPILATION_BEGIN=FUN_1408e31b0", "HorseCameraState::vftable",
     "CALLER_DECOMPILATION_BEGIN=FUN_1408e4240", "CALLER_DECOMPILATION_END=FUN_1408e4240"]),
    ("20261018T044016Z", ["POINTER_TABLE_ENTRY=index:2 address:1418efb20 value:0x1408E3290",
     "POINTER_TABLE_READ_COUNT=10", "POINTER_TABLE_SCAN_COMPLETE=true"]),
    ("20261018T044110Z", ["TARGET_RVA=0x8E3290", "FUN_1408e9990",
     "OUTGOING_DIRECT_CALL_EDGE_COUNT=1", "INDIRECT_CALL_SITE_COUNT=0"]),
    ("20261018T044204Z", ["DECOMPILATION_BEGIN=FUN_1405549d0", "DragonCameraState::vftable",
     "CALLER_DECOMPILATION_BEGIN=FUN_1408e4240", "CALLER_DECOMPILATION_END=FUN_1408e4240"]),
    ("20261018T044305Z", ["POINTER_TABLE_ENTRY=index:2 address:141873ee0 value:0x140554AB0",
     "POINTER_TABLE_READ_COUNT=10", "POINTER_TABLE_SCAN_COMPLETE=true"]),
    ("20261018T044358Z", ["TARGET_RVA=0x554AB0", "FUN_1408e9990",
     "OUTGOING_DIRECT_CALL_EDGE_COUNT=1", "INDIRECT_CALL_SITE_COUNT=0"]),
    ("20261018T044454Z", ["TARGET_RVA=0x8E9990", "FUN_14079e850", "FUN_14079e5a0",
     "OUTGOING_DIRECT_CALL_EDGE_COUNT=2", "INDIRECT_CALL_SITE_COUNT=1",
     "plVar2 + 8"]),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def validate_query(stamp: str, markers: list[str]) -> tuple[dict, dict[str, str]]:
    metadata_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    mode = meta.get("query_mode")
    common_ok = (
        meta.get("analysis_distribution") == "GOG"
        and meta.get("analysis_binary_product_version") == "1.6.1179"
        and meta.get("analysis_binary_sha256") == GOG_SHA
        and meta.get("exit_code") == 0
        and meta.get("ok") is True
        and meta.get("read_only") is True
        and meta.get("auto_analysis_disabled") is True
        and meta.get("import_attempted") is False
        and meta.get("overwrite_attempted") is False
        and checks.get("program_identity_matches_gog_binary") is True
        and checks.get("script_no_error") is True
    )
    mode_ok = (
        checks.get("direct_call_edge_scan") is True and checks.get("decompilation") is True
        if mode == "direct_call_edge_census"
        else checks.get("pointer_table_scan_complete") is True
        and checks.get("pointer_table_xref_scan_complete") is True
        if mode == "pointer_table_query"
        else False
    )
    if not common_ok or not mode_ok:
        raise SystemExit(f"Ghidra query validation failed: {stamp}")
    stdout = ROOT / meta["artifacts"]["stdout"]
    raw = stdout.read_text(encoding="utf-8", errors="replace")
    if digest(stdout) != meta.get("stdout_sha256") or any(marker not in raw for marker in markers):
        raise SystemExit(f"Ghidra stdout hash/marker validation failed: {stamp}")
    files = [metadata_path] + [ROOT / relative for relative in meta["artifacts"].values()]
    if any(not path.is_file() for path in files):
        raise SystemExit(f"Ghidra artifact missing: {stamp}")
    hashes = {path.relative_to(ROOT).as_posix(): digest(path) for path in files}
    row = {
        "stamp": stamp,
        "query_mode": mode,
        "requested_rva": meta.get("requested_rva"),
        "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
        "requested_pointer_count": meta.get("requested_pointer_count"),
        "checks": checks,
        "stdout_sha256": meta.get("stdout_sha256"),
        "stderr_sha256": meta.get("stderr_sha256"),
        "query_script_sha256": meta.get("query_script_sha256"),
    }
    return row, hashes


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0341" for row in evidence.get("items", [])):
        raise SystemExit("EV-0341 already registered")

    query_rows = []
    local_hashes: dict[str, str] = {}
    for stamp, markers in QUERIES:
        row, hashes = validate_query(stamp, markers)
        query_rows.append(row)
        local_hashes.update(hashes)

    note = TX / "EV-0341-note.md"
    put(note, f"""# EV-0341 — Remaining PlayerCamera state callbacks

## Build and method

Twelve targeted queries used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {GOG_SHA}. The queries inspected the four helper-created states at indices 2, 7, 10, and 12 in FUN_1408e4240, read their constructor-established primary vtables, mapped slot +0x10 (index 2), and traced the shared Horse/Dragon callback helper. Every query used the retained strict dispatcher with Ghidra read-only/no-analysis mode. The GOG build is distinct from installed Steam AE 1.6.1170.0; no addresses are transferred between them. Raw output, metadata, query checks, and hashes are in the private capture manifest.

## Direct observations

- PlayerCamera state index 2 is constructed by FUN_1408ebed0, which writes VATSCameraState::vftable at RVA 0x18F16E0. Vtable slot +0x10 resolves to FUN_140244650, whose body has zero direct and indirect call sites. This is also the slot+0x10 target already mapped for IronSightsState and PlayerCameraTransitionState [EV-0335, EV-0339, EV-0340].
- State index 7 is constructed by FUN_1408eb750 as TweenMenuCameraState with primary vtable RVA 0x18F1668. Its slot+0x10 target is FUN_1408eb830, which copies a dword from state+0x30 to the owner/context field at +0x13C. The complete census has zero direct and indirect calls.
- State index 10 is constructed by FUN_1408e31b0 as HorseCameraState with primary vtable RVA 0x18EFB10 and a secondary table at RVA 0x18EFB98. Its slot+0x10 target is FUN_1408e3290; that callback invokes FUN_1408e9990 and clears a byte at state+0xF0.
- State index 12 is constructed by FUN_1405549d0 as DragonCameraState with primary vtable RVA 0x1873ED0 and a secondary table at RVA 0x1873F58. Its slot+0x10 target is FUN_140554ab0; that callback also invokes FUN_1408e9990 and clears state+0xF0.
- FUN_1408e9990 updates/reset camera-state fields, may call FUN_14079e850 and conditionally FUN_14079e5a0 on the object at +0x20, then clears and releases the member at +0xA0. If that member reaches refcount zero, the helper may call its virtual slot +0x8. The helper census has two direct calls and one unresolved indirect finalizer site.
- The full FUN_1408e4240 body constructs camera state indices 0 through 12. The four previously unknown helper-created classes at indices 2, 7, 10, and 12 are now identified. This does not resolve which state is selected by the ProcessTrapHit cleanup chain.

No captured callback or bounded helper body directly calls Actor::UseSkill with AV11/AV12. FUN_14079e850, FUN_14079e5a0, the +0xA0 member's concrete type/finalizer, and the ProcessTrapHit-to-camera-state connection remain unresolved. This is bounded static evidence, not proof that the full cleanup route lacks skill credit. Q64-H1 and Q64-H2 remain proposed; no causal edge to Actor::UseSkill or OBJ-1 is added.

## Exact next discriminant

Trace writers of the ThirdPersonState member at +0xA0 through its concrete vtable and slot +0x8 finalizer. Then establish whether that receiver/path is reachable from one of the eight ProcessTrapHit teardown sites, preserving state selection and unresolved descendants as unknown.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = digest(note)

    manifest = TX / "EV-0341-capture-manifest.json"
    put(manifest, json.dumps({
        "evidence_id": "EV-0341",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": GOG_SHA,
        "ghidra_captures": query_rows,
    }, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)

    docs = {
        "README.md": """# EXP-0079 — Remaining PlayerCamera state callbacks

Resolve the helper-created states at indices 2, 7, 10, and 12 in FUN_1408e4240; map their primary vtables and slot+0x10 callbacks; trace the shared Horse/Dragon helper. The +0xA0 member finalizer and connection to ProcessTrapHit remain open.
""",
        "hypothesis.md": """# Competing models

- Q64-H1: the ProcessTrapHit-selected cleanup callbacks and relevant descendants do not dispatch AV11/AV12 skill progress.
- Q64-H2: a selected callback or finalizer can route an armor ActorValue into skill progress.

No callback selection is tied to the ProcessTrapHit chain yet. The shared Horse/Dragon helper contains an unresolved +0x8 finalizer.
""",
        "protocol.md": """# Protocol

Use only the existing GOG AE 1.6.1179.0 Ghidra project through the strict dispatcher in read-only/no-analysis mode. Retain constructor and vtable raw captures; map only observed vtable addresses. Query slot+0x10 and complete call-site censuses; follow the shared helper only to the observed depth. Do not transfer GOG RVAs to Steam or treat missing direct calls as proof about unresolved dynamic targets.
""",
        "results.md": """# Results

State indices 2, 7, 10, and 12 resolve as VATSCameraState, TweenMenuCameraState, HorseCameraState, and DragonCameraState. Their slot+0x10 methods are respectively the previously observed no-op FUN_140244650, a field-copy FUN_1408eb830, and two wrappers that share FUN_1408e9990. The shared helper releases a +0xA0 member and may call its virtual +0x8 finalizer. No direct AV11/AV12 skill sink appears in the captured bodies [EV-0341].
""",
        "predicted-outcomes.md": """# Predicted outcomes

- A concrete +0xA0 member finalizer or descendant reaching Actor::UseSkill with AV11/AV12 supports Q64-H2.
- A fully resolved callback path without that sink narrows Q64-H1 only for that path.
- Unknown member types, unresolved dynamic targets, or unestablished ProcessTrapHit reachability remain inconclusive.
""",
        "implications.md": """# Implications

The constructor's four unresolved state classes are now named and their primary +0x10 callbacks are bounded. VATS shares the established no-op target; TweenMenu copies a field; Horse and Dragon share a third-person cleanup helper. The helper retains one dynamic finalizer, and static state selection remains unlinked to ProcessTrapHit.
""",
        "expected-discriminants.md": """# Expected discriminants

1. Identify writers and concrete type for the ThirdPersonState member at +0xA0.
2. Resolve its slot+0x8 target and bounded descendants.
3. Determine whether the member/callback is reachable from a ProcessTrapHit teardown site.
4. Preserve unknowns until the path and any ActorValue argument are concrete.
""",
    }
    for name, content in docs.items():
        put(EXP / name, content)
    for path in EXP.iterdir():
        if path.is_file():
            local_hashes[path.relative_to(ROOT).as_posix()] = digest(path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0341",
        "kind": "native",
        "source": "Build-matched read-only Ghidra traces of the remaining PlayerCamera state constructors, primary vtables, slot+0x10 callbacks, and shared Horse/Dragon helper.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0341-note.md",
        "sha256": digest(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {GOG_SHA}; static only.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Four previously unknown PlayerCamera constructor helper states at indices 2, 7, 10, and 12; four primary vtables and slot+0x10 methods; bounded shared FUN_1408e9990 helper. Its +0xA0 member type/finalizer and ProcessTrapHit state reachability remain unresolved.",
        "result": "States identify as VATS, TweenMenu, Horse, and Dragon camera states. Their slot+0x10 targets are respectively a zero-call no-op, a field copy, and two wrappers around a shared helper. The shared helper clears/releases a +0xA0 member and may dispatch its unresolved virtual +0x8 finalizer. No direct AV11/AV12 skill sink appears in captured bodies; Q64-H1/H2 remain proposed.",
        "related_evidence": ["EV-0335", "EV-0337", "EV-0338", "EV-0339", "EV-0340"],
        "local_hashes": local_hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L176 |" in claims or "| CL-L177 |" in claims:
        raise SystemExit("EV-0341 claims already exist")
    put(claims_path, claims.rstrip()
        + "\n| CL-L176 | In GOG AE 1.6.1179.0, PlayerCamera state indices 2, 7, 10, and 12 are VATS, TweenMenu, Horse, and Dragon camera states; their primary slot+0x10 callbacks map to FUN_140244650, FUN_1408eb830, FUN_1408e3290, and FUN_140554ab0. | supported (constructor and primary vtable traces) | [EV-0341], [EV-0335] | GOG-only; no GOG RVA transfers to Steam. ProcessTrapHit state selection remains unknown. |"
        + "\n| CL-L177 | In GOG AE 1.6.1179.0, Horse and Dragon camera slot+0x10 callbacks share FUN_1408e9990, which releases the member at +0xA0 and may dispatch its unresolved virtual slot+0x8 finalizer. | supported (bounded helper trace) | [EV-0341] | The +0xA0 member type, finalizer descendants, and connection to ProcessTrapHit remain unresolved; no route-wide AV11/AV12 conclusion follows. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    put(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0341 extends M-0064 with the four helper-created PlayerCamera states. VATS uses a shared no-op slot+0x10 target, TweenMenu copies one state field, and Horse/Dragon share FUN_1408e9990. That helper releases a +0xA0 member and may dispatch its dynamic slot+0x8 finalizer. Neither concrete finalizer type nor ProcessTrapHit reachability is established. Claims CL-L176 and CL-L177 -> M-0064.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph_path, graph_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0341 resolves PlayerCamera state indices 2, 7, 10, and 12 and maps their slot+0x10 callbacks. Horse and Dragon share a helper that releases a +0xA0 member through an unresolved virtual slot+0x8 finalizer. No direct AV11/AV12 sink or causal edge to Actor::UseSkill or OBJ-1 is supported; ProcessTrapHit state reachability remains unknown. Claims CL-L176 and CL-L177 -> M-0064.\n")

    index_path = ROOT / "experiments/README.md"
    put(index_path, index_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEXP-0079 / EV-0341 resolves PlayerCamera constructor states 2, 7, 10, and 12 and their slot+0x10 callbacks; the shared +0xA0 member finalizer and ProcessTrapHit reachability remain open.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    if "EV-0341" not in q64.setdefault("evidence", []):
        q64["evidence"].append("EV-0341")
    for claim_id in ("CL-L176", "CL-L177"):
        if claim_id not in q64.setdefault("linked_claims", []):
            q64["linked_claims"].append(claim_id)
    for hypothesis in q64.get("hypotheses", []):
        if "EV-0341" not in hypothesis.setdefault("evidence", []):
            hypothesis["evidence"].append("EV-0341")
    q64["next_action"] = (
        "Trace writers and the concrete type of the ThirdPersonState member at +0xA0 released by FUN_1408e9990; "
        "resolve its virtual slot+0x8 finalizer, then establish whether that receiver/path is reachable from any "
        "of the eight ProcessTrapHit teardown sites. Keep state selection and unresolved descendants unknown."
    )
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    with (ROOT / "research/SESSION_LOG.md").open("a", encoding="utf-8") as stream:
        stream.write("\n- " + datetime.now(timezone.utc).isoformat(timespec="seconds")
            + " TX-20261017-0011 research update: EV-0341 / CL-L176 / CL-L177 registered. PlayerCamera state indices 2, 7, 10, and 12 resolve as VATS, TweenMenu, Horse, and Dragon; Horse/Dragon share FUN_1408e9990, which may dispatch an unresolved +0x8 finalizer through its +0xA0 member. No direct AV11/AV12 sink or ProcessTrapHit state link is shown. Next: resolve that member's producer/type/finalizer and test reachability to the eight teardown sites.\n")
    print("registered EV-0341 / CL-L176 / CL-L177; Q-0064 remains open")


if __name__ == "__main__":
    main()
