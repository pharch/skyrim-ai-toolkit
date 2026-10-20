#!/usr/bin/env python3
"""Register the bounded PlayerCharacter slot+0x378 context-return trace."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0075-playercharacter-context-vtable"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"

CAPTURES = [
    {"stamp": "20261018T040648Z", "kind": "slot_diagnostic", "markers": [
        "VTABLE_BASE_RVA=0x18ACD70", "VTABLE_SLOT_INDEX=0x6F", "VTABLE_SLOT_TARGET_RVA=0x7371F0",
        "XREF_CALL_EDGE=NOT_FOUND_IN_ANALYZED_PROJECT"]},
    {"stamp": "20261018T040758Z", "kind": "pointer_table", "markers": [
        "POINTER_TABLE_BASE_RVA=0x18AD0E8", "POINTER_TABLE_SCAN_COMPLETE=true",
        "POINTER_TABLE_XREF_SCAN_COMPLETE=true",
        "POINTER_TABLE_ENTRY=index:0 address:1418ad0e8 value:0x1407371F0 target:1407371f0 function:FUN_1407371f0"]},
    {"stamp": "20261018T041145Z", "kind": "call_edges", "markers": [
        "TARGET_RVA=0x2E55A0", "OUTGOING_DIRECT_CALL_EDGE_COUNT=0", "INDIRECT_CALL_SITE_COUNT=0",
        "DIRECT_CALL_EDGE_SCAN_COMPLETE=true", "XREF_CALL_COUNT=136"]},
    {"stamp": "20261018T040909Z", "kind": "displacement_68", "markers": [
        "OFFSET_QUERY=0x68", "OFFSET_ACCESS_COUNT=8295", "OFFSET_MATCHED_FUNCTION_COUNT=5519",
        "OFFSET_WRITER_CANDIDATE_FUNCTION_COUNT=1594", "OFFSET_VISITOR_SYMBOL_COUNT=0", "OFFSET_SCAN_COMPLETE=true"]},
    {"stamp": "20261018T041253Z", "kind": "displacement_5f0", "markers": [
        "OFFSET_QUERY=0x5F0", "OFFSET_ACCESS_COUNT=25", "OFFSET_MATCHED_FUNCTION_COUNT=20",
        "OFFSET_WRITER_CANDIDATE_FUNCTION_COUNT=11", "OFFSET_VISITOR_SYMBOL_COUNT=0", "OFFSET_SCAN_COMPLETE=true"]},
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def validate_capture(spec: dict) -> tuple[dict, dict[str, str]]:
    stamp = spec["stamp"]
    metadata_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    if (meta.get("analysis_distribution") != "GOG"
        or meta.get("analysis_binary_product_version") != "1.6.1179"
        or meta.get("analysis_binary_sha256") != BINARY
        or meta.get("exit_code") != 0
        or meta.get("read_only") is not True
        or meta.get("auto_analysis_disabled") is not True
        or meta.get("import_attempted") is not False
        or meta.get("overwrite_attempted") is not False
        or checks.get("program_identity_matches_gog_binary") is not True
        or checks.get("script_no_error") is not True):
        raise SystemExit(f"identity/read-only/completion check failed: {stamp}")

    if spec["kind"] == "slot_diagnostic":
        if checks.get("vtable_slot_lookup") is not True or meta.get("ok") is not False or checks.get("xref_call_edge") is not False:
            raise SystemExit(f"expected slot-lookup/call-edge diagnostic status changed: {stamp}")
    elif spec["kind"] == "pointer_table":
        required = ["pointer_table_requested", "pointer_table_scan_complete", "pointer_table_xref_scan_complete"]
        if meta.get("ok") is not True or any(checks.get(key) is not True for key in required):
            raise SystemExit(f"pointer-table query incomplete: {stamp}")
    elif spec["kind"] == "call_edges":
        required = ["function_lookup", "requested_rva_lookup", "direct_call_edge_scan", "decompilation", "xref_call_edge"]
        if meta.get("ok") is not True or any(checks.get(key) is not True for key in required):
            raise SystemExit(f"call-edge query incomplete: {stamp}")
    else:
        required = ["requested_displacement", "displacement_scan_complete", "visitor_symbol_scan_complete",
                    "writer_analysis_complete", "computed_writer_analysis_complete", "visitor_method_analysis_complete"]
        if meta.get("ok") is not True or any(checks.get(key) is not True for key in required):
            raise SystemExit(f"displacement scan incomplete: {stamp}")

    stdout = ROOT / meta["artifacts"]["stdout"]
    raw = stdout.read_text(encoding="utf-8", errors="replace")
    if digest(stdout) != meta.get("stdout_sha256") or any(marker not in raw for marker in spec["markers"]):
        raise SystemExit(f"capture/hash/marker failure: {stamp}")
    files = [metadata_path] + [ROOT / path for path in meta["artifacts"].values()]
    if any(not path.is_file() for path in files):
        raise SystemExit(f"missing capture artifact: {stamp}")
    hashes = {path.relative_to(ROOT).as_posix(): digest(path) for path in files}
    row = {"stamp": stamp, "query_kind": spec["kind"], "query_mode": meta.get("query_mode"),
        "requested_rva": meta.get("requested_rva"), "requested_vtable_slot": meta.get("requested_vtable_slot"),
        "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
        "requested_search_displacement": meta.get("requested_search_displacement"), "checks": checks,
        "overall_ok": meta.get("ok"), "stdout_sha256": meta.get("stdout_sha256"),
        "stderr_sha256": meta.get("stderr_sha256"), "query_script_sha256": meta.get("query_script_sha256")}
    return row, hashes


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0337" for row in evidence.get("items", [])):
        raise SystemExit("EV-0337 already registered")
    capture_rows: list[dict] = []
    local_hashes: dict[str, str] = {}
    for spec in CAPTURES:
        row, hashes = validate_capture(spec)
        capture_rows.append(row)
        local_hashes.update(hashes)

    note = TX / "EV-0337-note.md"
    put(note, f"""# EV-0337 — PlayerCharacter flag-zero context return

## Build and method

Five bounded queries used the existing GOG Skyrim AE 1.6.1179.0 project (analysis binary SHA-256 `{BINARY}`) through the strict dispatcher with auto-analysis disabled and read-only mode. One vtable-slot query resolved the requested entry but reported `xref_call_edge=false`; that capture is used only for its explicitly successful slot-lookup component. A separate exact-entry pointer-table query independently returned the same target. Both displacement scans completed but are interpreted only as candidate inventories. Capture hashes, checks, and the partial-query limitation are in the private manifest. No GOG RVA is transferred to Steam 1.6.1170.0.

## Direct observations

- The PlayerCharacter vtable base previously attributed at RVA `0x18ACD70` has byte offset `+0x378` at slot index `0x6F`. The slot-specific query returns `FUN_1407371f0` at RVA `0x7371F0`; its `vtable_slot_lookup` check passed, while the query's call-edge check failed because the method has no analyzed direct caller edge [capture 20261018T040648Z]. A bounded one-entry pointer-table scan at RVA `0x18AD0E8` independently returns the function pointer `FUN_1407371f0` and completes its scan [capture 20261018T040758Z; EV-0329].
- EV-0329's decompilation of `FUN_1407371f0` shows that a nonzero flag returns `param_1+0x8F8`; flag zero instead calls `FUN_1402e55a0`. That helper reads a TLS-indexed context slot and returns TLS field `+0x5F0` when its input matches TLS field `+0x5F8`; otherwise, if `param_1+0x68` is non-null, it returns the nested object's field at `+0x68`, or null. The current output's concrete class is not established [EV-0329].
- A fresh complete direct-call census of `FUN_1402e55a0` reports zero outgoing direct calls and zero indirect call sites, with 136 incoming direct call references [capture 20261018T041145Z]. The helper itself therefore has no call path to Actor::UseSkill, but that result does not screen the dynamically returned object's consumers.
- In the ThirdPersonState producer path, the pointer returned by PlayerCharacter slot `+0x378` is passed to a dynamic slot `+0x150` call, and its result is stored at ThirdPersonState `+0xA0` [EV-0336]. NiNode's slot `+0x150` is a recursive child traversal candidate, but no evidence ties the flag-zero context result to that vtable [EV-0334].
- A complete `+0x68` scan found 8,295 accesses across 5,519 functions, 1,594 writer candidates, and no visitor symbol. It cannot assign the nested field to this PlayerCharacter/context path [capture 20261018T040909Z]. A complete direct-displacement `+0x5F0` scan found 25 accesses across 20 functions and 11 writer candidates, with no visitor symbol or vtable. The helper constructs its TLS field address through a loaded offset register, so these ordinary displacement matches do not identify a TLS-slot writer [capture 20261018T041253Z].

## Model assessment

H1 remains that this call context returns an NiAVObject/NiNode-compatible root and slot `+0x150` selects a child. H2 remains that it returns another interface implementation and the NiNode match is only a comparator. The new evidence maps the getter and its context-selection logic but does not distinguish the concrete returned class, resolve the slot `+0x150` dispatch, or identify the returned member's slot `+0x8` finalizer. Q64-H1/H2 remain proposed. No causal edge to Actor::UseSkill AV11/AV12 or OBJ-1 is added.

## Exact next discriminant

Trace the remaining PlayerCamera state vtables initialized by `FUN_1408e4240`, prioritizing their slot `+0x10` callbacks and direct descendants for Actor::UseSkill AV11/AV12. Keep this flag-zero context branch dynamic until its selected object vtable is matched by source or exact-runtime evidence.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = digest(note)

    docs = {
        "README.md": "# EXP-0075 — PlayerCharacter flag-zero context object\n\nMap PlayerCharacter vtable slot +0x378 and trace its flag-zero context getter. Exact slot mapping is corroborated by an independent pointer-table query; the returned object's runtime/static class remains unknown.\n",
        "hypothesis.md": "# Competing models\n\n- H1: PlayerCharacter slot +0x378 with flag zero returns an NiAVObject/NiNode-compatible context root; slot +0x150 performs named-child lookup.\n- H2: the context getter returns another interface implementation sharing a slot layout; NiNode is only a comparator.\n\nThe captured getter selects either a TLS context field or a nested +0x68 field. Neither branch supplies a concrete class.\n",
        "protocol.md": "# Protocol\n\nUse the identity-checked GOG AE 1.6.1179.0 project through the strict dispatcher in read-only/no-analysis mode. Accept the vtable target only from the successful slot-lookup component and its independent exact-entry pointer-table query; retain the failed call-edge check. Treat displacement scans as candidate inventories, not type attribution. Do not transfer RVAs to Steam.\n",
        "results.md": "# Results\n\nEV-0337 maps PlayerCharacter slot +0x378 to FUN_1407371f0 and confirms the flag-zero branch delegates to a generic TLS/nested-field accessor. FUN_1402e55a0 has zero outgoing direct and indirect call sites, but the returned object's class and its dynamic slot +0x150 target remain unknown. The +0x68 and +0x5F0 displacement scans do not identify the context field's owner or a TLS writer. Q64-H1/H2 remain proposed [EV-0337], [EV-0336], [EV-0329].\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- An exact vtable or constructor match for the flag-zero result, with slot +0x150 matching the NiNode/NiAVObject family, supports H1.\n- A different concrete result vtable and slot +0x150 target supports H2.\n- A returned-member finalizer reaching Actor::UseSkill with AV11/AV12 supports Q64-H2.\n- Generic displacement matches, the getter body alone, or a same-offset NiNode method remain inconclusive.\n",
        "implications.md": "# Implications\n\nThe slot +0x378 getter is now mapped, but it conditionally returns a context-selected pointer. This narrows the source side of the ThirdPersonState+0xA0 path without establishing a shared scene-graph class or an AV11/AV12 result. Preserve the +0x730, +0x8F8, +0x9A0/+0x9A8, and +0xA0 paths separately until exact class evidence exists.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Identify the source/type of the TLS-selected object or nested `param_1+0x68` object's `+0x68` member.\n2. Match the actual returned object's vtable at the `FUN_1408e6500` slot +0x150 callsite.\n3. Identify the returned member's exact slot +0x8 finalizer.\n4. Screen the resolved descendant path against Actor::UseSkill AV11/AV12.\n",
    }
    for name, contents in docs.items():
        put(EXP / name, contents)

    manifest = TX / "EV-0337-capture-manifest.json"
    put(manifest, json.dumps({"evidence_id": "EV-0337", "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY, "captures": capture_rows}, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)
    local_hashes[(EXP / "register_ev0337.py").relative_to(ROOT).as_posix()] = digest(EXP / "register_ev0337.py")
    for path in EXP.iterdir():
        if path.is_file() and path.name != "register_ev0337.py":
            local_hashes[path.relative_to(ROOT).as_posix()] = digest(path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "edition": "AE",
        "modified_state": False, "id": "EV-0337", "kind": "native",
        "source": "Identity-checked GOG Skyrim AE 1.6.1179.0 PlayerCharacter slot+0x378, context helper, and bounded field-displacement traces.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0337-note.md",
        "sha256": digest(note), "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference", "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Five fresh query captures: one component-scoped vtable-slot mapping with a failed call-edge check, an independent exact-entry table scan, the context helper's complete call-edge census, and complete +0x68/+0x5F0 displacement scans. The latter scans do not type the returned context object.",
        "result": "PlayerCharacter vtable slot+0x378 maps to FUN_1407371f0. Its flag-zero branch delegates to FUN_1402e55a0, which selects a TLS or nested-field pointer and has no outgoing calls. In the FUN_1408e6500 path, that pointer's slot+0x150 target and returned member finalizer remain unresolved. No direct skill sink is established in the getter/helper; Q64-H1/H2 remain proposed.",
        "related_evidence": ["EV-0329", "EV-0334", "EV-0336"], "local_hashes": local_hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L169 |" in claims:
        raise SystemExit("CL-L169 already exists")
    put(claims_path, claims.rstrip() + "\n| CL-L169 | In GOG AE 1.6.1179.0, PlayerCharacter vtable slot +0x378 maps to FUN_1407371f0; with flag zero it returns a context-selected pointer through FUN_1402e55a0, whose output is drawn from TLS or a nested +0x68 field. | supported (bounded build-attested slot and helper trace) | [EV-0337], [EV-0329] | The context object's concrete class and dynamic slot +0x150 target in FUN_1408e6500 remain unknown; a NiNode same-slot comparator is conditional. The helper's no-call census does not screen consumers of its result. No Q64-H1/H2 resolution, AV11/AV12 exclusion, Steam behavior, vanilla reproduction, or OBJ-1 edge follows. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    put(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0337 refines M-0065: PlayerCharacter slot +0x378 is FUN_1407371f0, whose flag-zero branch selects either a TLS context field or a nested +0x68 member through FUN_1402e55a0. The helper has no outgoing call sites, but its returned class and the consumer's slot +0x150 target remain unresolved. The exact slot mapping does not establish a NiNode edge. Claim CL-L169 -> M-0065.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph_path, graph_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0337 maps the PlayerCharacter +0x378 flag-zero getter to a TLS/nested-field context accessor. This improves source provenance for the ThirdPersonState+0xA0 named-object candidate [EV-0336], but the selected object class, slot +0x150 target, and member finalizer remain untyped; the NiNode comparison stays conditional. `FUN_1402e55a0` has no outgoing calls, which adds no edge to Actor::UseSkill AV11/AV12 and does not exclude downstream dispatch. The +0x68/+0x5F0 scans are broad or fail to expose the TLS-indexed writer. No causal edge to OBJ-1 is added. Claim CL-L169 -> M-0065.\n")

    index_path = ROOT / "experiments/README.md"
    put(index_path, index_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEXP-0075 / EV-0337 maps PlayerCharacter slot +0x378 to a TLS/nested-field context getter; its returned class, slot +0x150 target, and finalizer remain unknown.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    q65 = next(row for row in frontier["items"] if row.get("id") == "Q-0065")
    for row in (q64, q65):
        if "EV-0337" not in row.setdefault("evidence", []): row["evidence"].append("EV-0337")
        if "CL-L169" not in row.setdefault("linked_claims", []): row["linked_claims"].append("CL-L169")
        for hypothesis in row.get("hypotheses", []):
            if "EV-0337" not in hypothesis.setdefault("evidence", []): hypothesis["evidence"].append("EV-0337")
    q64["next_action"] = ("Map the slot+0x10 callbacks for the other PlayerCamera state vtables initialized by FUN_1408e4240, "
        "prioritizing FirstPersonState and BleedoutCameraState; screen each body and bounded descendants for "
        "Actor::UseSkill AV11/AV12. Keep the slot+0x378 flag-zero context result dynamic until its selected "
        "object vtable is matched by source or exact-runtime evidence.")
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    with (ROOT / "research/SESSION_LOG.md").open("a", encoding="utf-8") as stream:
        stream.write("\n- " + datetime.now(timezone.utc).isoformat(timespec="seconds")
            + " TX-20261017-0011 research update: EV-0337 / CL-L169 registered. PlayerCharacter slot+0x378 flag zero returns a TLS/nested-field context pointer through a helper with no outgoing calls; the selected class, slot+0x150 target, and member finalizer remain unknown. Two completed displacement scans do not identify the TLS writer. Q64-H1/H2 remain proposed; no causal edge to Actor::UseSkill or OBJ-1 is added. Next: map other PlayerCamera state slot+0x10 callbacks, starting with FirstPersonState and BleedoutCameraState.\n")
    print("registered EV-0337 / CL-L169; Q-0064 remains open; camera-state callbacks are next")


if __name__ == "__main__":
    main()
