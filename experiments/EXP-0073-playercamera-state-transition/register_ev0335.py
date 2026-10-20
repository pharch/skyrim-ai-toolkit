#!/usr/bin/env python3
"""Register the bounded PlayerCamera active-state callback trace."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0073-playercamera-state-transition"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = {
    "20261018T010702Z": ["TARGET_RVA=0x8E8E00", "FUN_140551300(param_1,uVar1)"],
    "20261018T010916Z": ["TARGET_RVA=0x551300", "param_1 + 0x28", "param_1 + 0x10"],
    "20261018T033451Z": ["TARGET_RVA=0x550FF0", "param_1[5] = 0"],
    "20261018T034210Z": ["TARGET_RVA=0x8E96D0", "ThirdPersonState::vftable", "0x141873e18"],
    "20261018T034304Z": ["POINTER_TABLE_BASE_RVA=0x1873E18", "POINTER_TABLE_ENTRY=index:2", "function:FUN_1408e9990"],
    "20261018T034358Z": ["TARGET_RVA=0x8E9990", "OUTGOING_DIRECT_CALL_EDGE_COUNT=2", "INDIRECT_CALL_SITE_COUNT=1", "FUN_14079e850"],
    "20261018T034526Z": ["POINTER_TABLE_BASE_RVA=0x18F0628", "POINTER_TABLE_ENTRY=index:1", "function:FUN_1408e4240"],
}
DIAGNOSTIC = "20261018T033844Z"

def h(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def put(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")

def capture(stamp: str, markers: list[str], *, diagnostic: bool = False):
    mp = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(mp.read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    required = ["program_identity_matches_gog_binary", "script_no_error"]
    if diagnostic:
        required += ["function_lookup", "requested_rva_lookup", "disassembly", "decompilation"]
    else:
        required += ["requested_rva_lookup"] if meta.get("requested_rva") else []
        required += ["pointer_table_scan_complete", "pointer_table_xref_scan_complete"] if meta.get("query_mode") == "pointer_table_query" else []
        required += ["direct_call_edge_scan", "decompilation"] if meta.get("query_mode") == "direct_call_edge_census" else []
        required += ["decompilation"] if meta.get("query_mode") == "function_query" else []
        if meta.get("ok") is not True:
            raise SystemExit(f"positive capture did not pass all query checks: {stamp}")
    if (meta.get("analysis_distribution") != "GOG" or meta.get("analysis_binary_product_version") != "1.6.1179"
        or meta.get("analysis_binary_sha256") != BINARY or meta.get("exit_code") != 0
        or meta.get("read_only") is not True or meta.get("auto_analysis_disabled") is not True
        or meta.get("import_attempted") is not False or meta.get("overwrite_attempted") is not False
        or any(checks.get(name) is not True for name in required)):
        raise SystemExit(f"identity/read-only/completion check failed: {stamp}")
    if diagnostic and (meta.get("ok") is not False or checks.get("xref_call_edge") is not False):
        raise SystemExit("expected 0x8E4240 data-table-only diagnostic boundary changed")
    stdout = ROOT / meta["artifacts"]["stdout"]
    raw = stdout.read_text(encoding="utf-8", errors="replace")
    if h(stdout) != meta.get("stdout_sha256") or any(marker not in raw for marker in markers):
        raise SystemExit(f"capture/hash/marker failure: {stamp}")
    paths = [mp] + [ROOT / relative for relative in meta["artifacts"].values()]
    if any(not path.is_file() for path in paths):
        raise SystemExit(f"missing raw capture: {stamp}")
    return meta, {path.relative_to(ROOT).as_posix(): h(path) for path in paths}

def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0335" for row in evidence["items"]):
        raise SystemExit("EV-0335 already registered")
    hashes, manifest_rows = {}, []
    for stamp, markers in CAPTURES.items():
        meta, local = capture(stamp, markers)
        hashes.update(local)
        manifest_rows.append({"stamp": stamp, "query_mode": meta.get("query_mode"),
            "requested_rva": meta.get("requested_rva"), "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
            "requested_pointer_count": meta.get("requested_pointer_count"), "checks": meta.get("checks"),
            "stdout_sha256": meta.get("stdout_sha256"), "stderr_sha256": meta.get("stderr_sha256"),
            "query_script_sha256": meta.get("query_script_sha256")})
    diagnostic_meta, local = capture(DIAGNOSTIC, ["TARGET_RVA=0x8E4240", "DECOMPILATION_BEGIN=FUN_1408e4240"], diagnostic=True)
    hashes.update(local)
    manifest_rows.append({"stamp": DIAGNOSTIC, "diagnostic_only": True, "ok": diagnostic_meta.get("ok"),
        "checks": diagnostic_meta.get("checks"), "stdout_sha256": diagnostic_meta.get("stdout_sha256"),
        "note": "Function lookup, disassembly, decompilation, and PlayerCamera-table entry are preserved; xref_call_edge=false, so no direct-call edge is claimed."})

    note = TX / "EV-0335-note.md"
    put(note, f"""# EV-0335 — PlayerCamera active-state transition callback

## Build and method

Seven identity-checked read-only captures used the existing GOG Skyrim AE 1.6.1179.0 project (analysis binary SHA-256 `{BINARY}`), with auto-analysis disabled and no import or overwrite. A separate 0x8E4240 query had valid function lookup, disassembly, and decompilation but `xref_call_edge=false`; it is retained only as a function-body diagnostic. A complete pointer-table query independently places FUN_1408e4240 in the PlayerCamera table. Capture hashes and query checks are in the private manifest. No GOG RVA is transferred to Steam 1.6.1170.0.

## Direct observations

- PlayerCamera construction calls the TESCamera base initializer, which clears the field at +0x28. `FUN_140551300` treats PlayerCamera+0x28 as the current state pointer: it calls that object's slot +0x10 before replacing the pointer, increments the incoming reference, stores it, releases the previous reference through slot +0x8 if final, then calls slot +0x8 on the new current state [captures 20261018T033451Z, 20261018T010916Z].
- `FUN_1408e8e00` selects a state pointer from the PlayerCamera state array and routes a changed state through `FUN_140551300` [capture 20261018T010702Z]. The PlayerCamera function table at RVA 0x18F0628 contains FUN_1408e4240 at entry index 1 and is referenced by its constructor and cleanup body [capture 20261018T034526Z; existing teardown trace EV-0327]. The body capture for FUN_1408e4240 shows an index-9 `ThirdPersonState` stored at +0x100 via FUN_1408e96d0; this specific body capture is diagnostic for direct-call xrefs, not for its valid function body [capture 20261018T033844Z].
- FUN_1408e96d0 installs `ThirdPersonState::vftable` at RVA 0x1873E18. A complete 12-entry table scan maps slot index 2 (byte offset +0x10) to FUN_1408e9990 [captures 20261018T034210Z, 20261018T034304Z].
- FUN_1408e9990 resets ThirdPersonState camera fields, calls FUN_14079e850 and FUN_14079e5a0 conditionally, then clears and final-releases a member at +0xA0 through that member's slot +0x8; its direct-call census records two direct edges and one unresolved indirect site [capture 20261018T034358Z]. No direct Actor::UseSkill/AV11/AV12 sink appears in this callback body.
- The concrete state selected at PlayerCamera teardown is dynamic. Other state vtables, the two helper descendants, and the +0xA0 member destructor remain untraced. The no-direct-sink observation therefore narrows one state branch only and does not resolve Q64-H1/H2 [EV-0327, EV-0330].

## Cross-domain synthesis

This `+0x28` callback is a state-transition interface, distinct from the PlayerCharacter scene-child candidate at +0x730 [EV-0334] and data-selected model/skeleton resource releases at +0x8F8/+0x9A0/+0x9A8 [EV-0328, EV-0329, EV-0331, EV-0333]. EV-0330 independently maps an AutoVanity state callback to a HUD path. The evidence supports no causal edge from the ThirdPersonState transition body to Actor::UseSkill AV11/AV12; its direct helpers and nested finalizer remain open. No edge to OBJ-1 is supported.

## Exact next discriminant

Trace FUN_14079e850, FUN_14079e5a0, and the concrete destructor for ThirdPersonState+0xA0; then map slot +0x10 for the other PlayerCamera state vtables initialized by FUN_1408e4240. Screen every resolved descendant against the mapped Actor::UseSkill AV11/AV12 sink. Keep the teardown-selected state unknown until runtime/data selection is established.
""")
    hashes[note.relative_to(ROOT).as_posix()] = h(note)

    docs = {
        "README.md": "# EXP-0073 — PlayerCamera state transition\n\nTrace PlayerCamera+0x28 from active-state replacement into the index-9 ThirdPersonState slot+0x10 callback. The callback has two direct helpers and one nested refcount release still to screen. EV-0335 narrows one teardown branch; Q-0064 remains open.\n",
        "hypothesis.md": "# Competing models\n\n- State model A: PlayerCamera+0x28 is the active camera-state pointer; slot+0x10 is a state transition-out hook and its target depends on the selected state.\n- State model B: +0x28 is a generic object callback with no state-array ownership.\n- Q64-H1: no cleanup descendant reaches AV11/AV12 skill progress.\n- Q64-H2: at least one cleanup descendant reaches AV11/AV12.\n\nEV-0335 supports State model A for the mapped setter and index-9 ThirdPersonState. It does not identify the state selected at teardown or decide Q64-H1/H2.\n",
        "protocol.md": "# Protocol\n\nUse identity-checked GOG AE 1.6.1179.0 Ghidra queries through the strict dispatcher in existing-project read-only/no-analysis mode. Treat pointer-table targets as build-specific. Preserve the 0x8E4240 missing direct-xref check as a diagnostic boundary; its function body is usable only alongside the successful PlayerCamera table scan. Do not transfer any RVA to Steam AE 1.6.1170.0.\n",
        "results.md": "# Results\n\nEV-0335 maps PlayerCamera+0x28 as the active camera-state pointer updated by FUN_140551300, which calls state slot+0x10 before replacing it. State-array selection routes through FUN_1408e8e00. Index 9 is constructed as ThirdPersonState at PlayerCamera+0x100; its vtable slot+0x10 is FUN_1408e9990. That callback resets camera fields, conditionally invokes two direct helpers, and final-releases its +0xA0 member through an unresolved slot+0x8 target. No direct AV11/AV12 sink appears in this one body; the helpers, nested finalizer, other states, and teardown-selected state remain unresolved. Q64-H1/H2 are unchanged [EV-0335], [EV-0327].\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- A selected state's slot+0x10 target with no route to Actor::UseSkill narrows that state branch only.\n- A helper or nested finalizer reaching Actor::UseSkill with AV11/AV12 supports Q64-H2.\n- Matching callback targets across all possible states support a bounded common-handler result; different targets require separate screening.\n- Missing selected-state/runtime evidence is inconclusive.\n",
        "implications.md": "# Implications\n\nThe PlayerCamera+0x28 path is stateful rather than a single statically fixed callback. The ThirdPersonState target is one constructor-selected candidate; PlayerCamera can route other state objects through the same transition helper. Keep every unresolved descendant open and do not generalize the bounded callback body to all teardown paths or to zero armor XP.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Resolve FUN_14079e850 and FUN_14079e5a0 and the +0xA0 member's exact vtable/finalizer.\n2. Map each state-array constructor/vtable and slot+0x10 target, especially states reachable during teardown.\n3. Search resolved bodies and descendants for the mapped Actor::UseSkill AV11/AV12 sink.\n4. A direct skill sink supports Q64-H2; complete per-state paths with no such sink only narrow the corresponding branches.\n"
    }
    for filename, content in docs.items():
        put(EXP / filename, content)
    manifest = TX / "EV-0335-capture-manifest.json"
    put(manifest, json.dumps({"evidence_id": "EV-0335", "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY, "captures": manifest_rows}, indent=2, ensure_ascii=False))
    hashes[manifest.relative_to(ROOT).as_posix()] = h(manifest)
    hashes[(EXP / "register_ev0335.py").relative_to(ROOT).as_posix()] = h(EXP / "register_ev0335.py")
    for path in EXP.iterdir():
        if path.is_file() and path.name != "register_ev0335.py":
            hashes[path.relative_to(ROOT).as_posix()] = h(path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "edition": "AE",
        "modified_state": False, "id": "EV-0335", "kind": "native",
        "source": "Identity-checked GOG Skyrim AE 1.6.1179.0 PlayerCamera active-state setter, state array, ThirdPersonState vtable, and slot+0x10 callback traces.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0335-note.md",
        "sha256": h(note), "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference", "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Seven successful identity-checked captures map PlayerCamera+0x28 state replacement, index-9 ThirdPersonState construction, vtable slot+0x10, and the handler's direct/indirect descendants; one function-body query with xref_call_edge=false is explicitly diagnostic.",
        "result": "FUN_140551300 uses PlayerCamera+0x28 as the active camera-state pointer and calls its slot+0x10 before replacement. Index-9 ThirdPersonState slot+0x10 maps to FUN_1408e9990, which resets camera fields, calls two helpers, and final-releases a +0xA0 member. No direct AV11/AV12 sink appears in this callback body; the helpers, nested finalizer, other states, and teardown-selected state remain unresolved.",
        "related_evidence": ["EV-0327", "EV-0330", "EV-0334", "EV-0217", "EV-0223", "EV-0280", "EV-0281"],
        "local_hashes": hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claim_path = ROOT / "research/CLAIMS.md"
    claims = claim_path.read_text(encoding="utf-8")
    if "| CL-L167 |" in claims:
        raise SystemExit("CL-L167 already exists")
    put(claim_path, claims.rstrip() + "\n| CL-L167 | In GOG AE 1.6.1179.0, PlayerCamera+0x28 is used as the active camera-state pointer by FUN_140551300; its slot+0x10 is invoked before replacement. The index-9 ThirdPersonState at PlayerCamera+0x100 maps that slot to FUN_1408e9990, which resets camera fields and final-releases a +0xA0 member after two conditional helper calls. | supported (bounded build-attested state and vtable trace) | [EV-0335] | The state selected at teardown, other state slot+0x10 targets, both helper descendants, and the nested +0xA0 finalizer remain unresolved. No Q64-H1/H2 result or global AV11/AV12 exclusion follows. No Steam runtime or vanilla reproduction is established. No OBJ-1 edge is supported. |")
    mechanism_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanism_path.read_text(encoding="utf-8")
    if "## M-0064 —" in mechanisms:
        raise SystemExit("M-0064 already exists")
    put(mechanism_path, mechanisms.rstrip() + "\n\n## M-0064 — PlayerCamera active-state transition callback (Q-0064)\n\nFUN_140551300 invokes the current PlayerCamera+0x28 state's slot+0x10 before swapping the state pointer, then balances references through slot+0x8. State-array selection is routed by FUN_1408e8e00. The index-9 ThirdPersonState vtable maps slot+0x10 to FUN_1408e9990; that body resets camera fields, conditionally calls two helpers, and final-releases a member at +0xA0 through an unresolved slot+0x8 target [EV-0335]. No direct AV11/AV12 sink is present in this body; all descendants and other state targets remain open. Claim CL-L167 -> M-0064.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph_path, graph_path.read_text(encoding="utf-8").rstrip() + "\n\nEV-0335 identifies PlayerCamera+0x28 as an active-state interface and maps the index-9 ThirdPersonState slot+0x10 callback to camera-field reset and conditional helper/refcount work. This is structurally distinct from the +0x730 scene-child candidate [EV-0334] and the +0x8F8/+0x9A0 resource-release candidates [EV-0328], [EV-0329], [EV-0331], [EV-0333]. EV-0330 separately maps an AutoVanity callback to a HUD branch. Do not infer a shared cleanup class or a global no-skill result: the teardown-selected state, other state tables, helper descendants, and nested finalizer are unresolved. No causal edge to Actor::UseSkill AV11/AV12 or OBJ-1 is added [EV-0335]. Claim CL-L167 -> M-0064.\n")

    experiment_index = ROOT / "experiments/README.md"
    put(experiment_index, experiment_index.read_text(encoding="utf-8").rstrip() + "\n\nEXP-0073 / EV-0335 maps PlayerCamera+0x28 as the active camera-state pointer and the index-9 ThirdPersonState slot+0x10 callback. Two helper descendants, the +0xA0 finalizer, other state targets, and the selected teardown state remain open; Q-0064 is unresolved.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    if "EV-0335" not in q.setdefault("evidence", []): q["evidence"].append("EV-0335")
    if "CL-L167" not in q.setdefault("linked_claims", []): q["linked_claims"].append("CL-L167")
    q["next_action"] = "Resolve FUN_14079e850 and FUN_14079e5a0 plus the ThirdPersonState+0xA0 member's exact slot+0x8 finalizer; then map slot+0x10 for the other initialized PlayerCamera states and screen every descendant for Actor::UseSkill AV11/AV12. Keep the teardown-selected state dynamic until data/runtime selection is established."
    q.setdefault("attempts", []).append({
        "action_key": "q64-playercamera-current-state-slot10-thirdperson",
        "outcome": "EV-0335 identifies PlayerCamera+0x28 as the active camera-state pointer and maps index-9 ThirdPersonState slot+0x10 to FUN_1408e9990. The handler resets camera fields, calls two direct helpers, and final-releases its +0xA0 member through an unresolved slot+0x8 target. No direct AV11/AV12 sink appears in this one body; the other state targets and descendants remain unresolved. Q64-H1/H2 remain proposed.",
        "evidence": ["EV-0335", "EV-0327", "EV-0330"],
        "new_discriminant": "Trace FUN_14079e850, FUN_14079e5a0, and the +0xA0 member's concrete finalizer; then map each reachable PlayerCamera state's slot+0x10 callback and screen descendants against the known Actor::UseSkill AV11/AV12 sink.",
        "recorded_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    roadmap = ROOT / "ROADMAP.md"
    put(roadmap, roadmap.read_text(encoding="utf-8").rstrip() + "\n\nEV-0335 maps PlayerCamera+0x28 as the active state pointer and resolves the index-9 ThirdPersonState slot+0x10 callback to FUN_1408e9990. This is a camera-state transition path, distinct from the NiNode candidate at +0x730 and model/skeleton resource paths at +0x8F8/+0x9A0/+0x9A8. Two direct helpers, the nested +0xA0 finalizer, other state callbacks, and the teardown-selected state remain unresolved. Continue Q-0064; do not infer a global no-skill result.\n")

    with (ROOT / "research/SESSION_LOG.md").open("a", encoding="utf-8") as stream:
        stream.write("\n- " + datetime.now(timezone.utc).isoformat(timespec="seconds") + " TX-20261017-0011 checkpoint: EV-0335 / CL-L167 / M-0064 registered. PlayerCamera+0x28 is an active-state pointer; index-9 ThirdPersonState slot+0x10 maps to FUN_1408e9990, whose direct helpers and +0xA0 finalizer remain open. Other states and teardown selection remain dynamic; Q64-H1/H2 unchanged. Next: resolve both helpers and the nested finalizer, then map remaining state callbacks.\n")
    print("registered EV-0335 / CL-L167 / M-0064; Q-0064 remains open")

if __name__ == "__main__":
    main()
