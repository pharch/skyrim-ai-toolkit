#!/usr/bin/env python3
"""Register the ThirdPersonState +0xA0 pointer lifecycle traces."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0080-thirdperson-state-member-lifecycle"
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"

QUERIES = [
    ("20261018T044802Z", "memory_displacement_search", [
        "OFFSET_ACCESS_COUNT=4679", "OFFSET_MATCHED_FUNCTION_COUNT=3241",
        "OFFSET_WRITER_CANDIDATE_FUNCTION_COUNT=930", "OFFSET_VISITOR_SYMBOL_COUNT=0",
        "OFFSET_SCAN_COMPLETE=true", "OFFSET_WRITER_ANALYSIS_COMPLETE=true",
        "OFFSET_WRITER_CANDIDATE=FUN_1408e96d0", "OFFSET_WRITER_CANDIDATE=FUN_1408ea490"]),
    ("20261018T045011Z", "direct_call_edge_census", [
        "TARGET_RVA=0x8EA490", "OUTGOING_DIRECT_CALL_EDGE_COUNT=2",
        "INDIRECT_CALL_SITE_COUNT=1", "DECOMPILATION_BEGIN=FUN_1408ea490",
        "param_2 + 1", "plVar2 + 8"]),
    ("20261018T045118Z", "direct_call_edge_census", [
        "TARGET_RVA=0x8E6500", "OUTGOING_DIRECT_CALL_EDGE_COUNT=6",
        "INDIRECT_CALL_SITE_COUNT=4", "DECOMPILATION_BEGIN=FUN_1408e6500",
        "FUN_1408ea490(plVar2,uVar4,0)", "FUN_1408ea490(lVar1,uVar4,1)",
        "CALLER_DECOMPILATION_BEGIN=FUN_1407bca90"]),
    ("20261018T045238Z", "direct_call_edge_census", [
        "TARGET_RVA=0x8E96D0", "ThirdPersonState::vftable",
        "param_1[0x14] = 0", "OUTGOING_DIRECT_CALL_EDGE_COUNT=0",
        "INDIRECT_CALL_SITE_COUNT=0"]),
    ("20261018T045347Z", "direct_call_edge_census", [
        "TARGET_RVA=0x8E9840", "DECOMPILATION_BEGIN=FUN_1408e9840",
        "FUN_140cee3e0", "OUTGOING_DIRECT_CALL_EDGE_COUNT=3",
        "INDIRECT_CALL_SITE_COUNT=5", "local_res10[4] + 8"]),
    ("20261018T045454Z", "direct_call_edge_census", [
        "TARGET_RVA=0x8EA710", "DECOMPILATION_BEGIN=FUN_1408ea710",
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=2", "INDIRECT_CALL_SITE_COUNT=1",
        "FUN_140cee240", "plVar2 + 8"]),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def validate_query(stamp: str, expected_mode: str, markers: list[str]) -> tuple[dict, dict[str, str]]:
    metadata_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    common_ok = (
        meta.get("analysis_distribution") == "GOG"
        and meta.get("analysis_binary_product_version") == "1.6.1179"
        and meta.get("analysis_binary_sha256") == GOG_SHA
        and meta.get("program_executable_path_matches_gog_binary") is True
        and meta.get("exit_code") == 0
        and meta.get("ok") is True
        and meta.get("read_only") is True
        and meta.get("auto_analysis_disabled") is True
        and meta.get("import_attempted") is False
        and meta.get("overwrite_attempted") is False
    )
    if expected_mode == "memory_displacement_search":
        mode_ok = (
            meta.get("query_mode") == expected_mode
            and checks.get("requested_displacement") is True
            and checks.get("displacement_scan_complete") is True
            and checks.get("writer_analysis_complete") is True
            and checks.get("visitor_symbol_scan_complete") is True
            and checks.get("script_no_error") is True
        )
    else:
        mode_ok = (
            meta.get("query_mode") == expected_mode
            and checks.get("direct_call_edge_scan") is True
            and checks.get("decompilation") is True
            and checks.get("script_no_error") is True
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
        "query_mode": expected_mode,
        "requested_rva": meta.get("requested_rva"),
        "requested_search_displacement": meta.get("requested_search_displacement"),
        "checks": checks,
        "stdout_sha256": meta.get("stdout_sha256"),
        "stderr_sha256": meta.get("stderr_sha256"),
        "query_script_sha256": meta.get("query_script_sha256"),
    }
    return row, hashes


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0342" for row in evidence.get("items", [])):
        raise SystemExit("EV-0342 already registered")

    query_rows = []
    local_hashes: dict[str, str] = {}
    for stamp, mode, markers in QUERIES:
        row, hashes = validate_query(stamp, mode, markers)
        query_rows.append(row)
        local_hashes.update(hashes)

    note = TX / "EV-0342-note.md"
    put(note, f"""# EV-0342 — ThirdPersonState +0xA0 member lifecycle

## Build and method

Six identity-checked queries used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {GOG_SHA}: one complete +0xA0 displacement search and five function-specific traces. Queries ran through the strict dispatcher with Ghidra read-only/no-analysis mode. The displacement result is a candidate inventory only: it spans 4,679 accesses across 3,241 functions, with 930 writer-candidate functions and no visitor symbol. Function-specific evidence is limited to the PlayerCamera/ThirdPersonState cluster. No GOG RVA is transferred to Steam AE 1.6.1170.0.

## Direct observations

- FUN_1408e96d0 constructs ThirdPersonState and initializes its member at +0xA0 to null. Its primary vtable begins at RVA 0x1873E18; its callers include HorseCameraState, DragonCameraState, and FUN_1408e4240.
- FUN_1408ea490 is the pointer setter for ThirdPersonState+0xA0. It increments the incoming object's refcount, replaces the member, decrements the previous object's refcount, and dispatches the old object's virtual slot +0x8 if that count reaches zero. It then derives a +0x10 member for a separate structure from the installed pointer.
- FUN_1408e6500 calls the PlayerCharacter virtual slot +0x378 accessor. If the returned object is non-null, it calls that object's virtual slot +0x150; the result is passed to FUN_1408ea490 and stored in ThirdPersonState+0xA0. The function has six direct calls and four indirect call sites. Its observed caller FUN_1407bca90 passes the PlayerCamera global and an argument into this routine.
- The PlayerCharacter +0x378 accessor is FUN_1407371f0 in the verified GOG build. EV-0337 and EV-0329 show that its flag-zero path delegates to FUN_1402e55a0 and may return a TLS or nested-field pointer; the concrete class remains unknown.
- FUN_1408e9840 is a ThirdPersonState lifecycle callback. When +0xA0 is null and a separate readiness check passes, it again obtains the PlayerCharacter +0x378 object and calls its slot +0x150, then installs the result in +0xA0. Replacing an old member invokes its virtual slot +0x8 on final release. This method also has a separate temporary object cleanup path with a slot +0x520 call and another dynamic finalizer.
- FUN_1408ea710 resets camera-state fields, clears +0xA0, decrements the old member, and may dispatch its virtual slot +0x8 finalizer. FUN_1408e9990 performs the same member clear/release behavior in the Horse/Dragon callback path [EV-0341].

## Causal assessment

The +0xA0 member is a refcounted object returned from a type-erased slot +0x150 call on the object obtained through PlayerCharacter slot +0x378. Its finalizer is virtual slot +0x8 and remains unresolved because the returned object's concrete vtable is not established. The owner/field lifecycle is now source-backed; the member class, getter branch at runtime, and connection to any of the eight ProcessTrapHit teardown call sites are not.

No captured method directly calls Actor::UseSkill with AV11/AV12. That absence is bounded static evidence and cannot resolve the remaining dynamic calls or prove the full armor-XP route. Q64-H1/H2 remain proposed. No causal edge to Actor::UseSkill or OBJ-1 is added.

## Exact next discriminant

Resolve the concrete object returned by the PlayerCharacter +0x378 getter and its slot +0x150 implementation/return vtable. Then match its +0x8 finalizer to a specific ProcessTrapHit teardown site, retaining getter branch and state selection as unknown until evidence distinguishes them.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = digest(note)

    manifest = TX / "EV-0342-capture-manifest.json"
    put(manifest, json.dumps({
        "evidence_id": "EV-0342",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": GOG_SHA,
        "ghidra_captures": query_rows,
    }, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)

    docs = {
        "README.md": """# EXP-0080 — ThirdPersonState member lifecycle

Trace the source and cleanup for ThirdPersonState+0xA0, the returned type behind PlayerCharacter slot+0x378 and its slot+0x150 method, and the member's slot+0x8 finalizer. The class and ProcessTrapHit reachability remain unresolved.
""",
        "hypothesis.md": """# Competing models

- Q64-H1: the type-erased object and its +0xA0 result/finalizer do not route AV11/AV12 into skill progress on the ProcessTrapHit route.
- Q64-H2: one dynamic method or finalizer reaches an armor skill-progress sink.

The PlayerCamera/ThirdPersonState structural path is established; concrete target types and ProcessTrapHit reachability are not.
""",
        "protocol.md": """# Protocol

Use the complete GOG +0xA0 displacement search only to nominate candidates. Trace the exact ThirdPersonState writer, owner, constructor, reset, and destructor in the existing GOG project using the strict dispatcher and read-only/no-analysis mode. Retain unknown virtual targets and do not infer the returned type from a matching NiNode method or a shared offset.
""",
        "results.md": """# Results

ThirdPersonState initializes +0xA0 to null. FUN_1408e6500 obtains an object through PlayerCharacter slot+0x378, calls that object's slot+0x150, and stores the return through FUN_1408ea490. Lifecycle functions release the member through its slot+0x8 if the refcount reaches zero. The member's concrete vtable and connection to the eight ProcessTrapHit sites remain unresolved [EV-0342].
""",
        "predicted-outcomes.md": """# Predicted outcomes

- A concrete slot+0x150 return vtable whose +0x8 finalizer reaches Actor::UseSkill with AV11/AV12 supports Q64-H2.
- A fully resolved finalizer path without that sink narrows Q64-H1 for that object and route only.
- Unknown receiver/return types, branch selection, or ProcessTrapHit reachability remain inconclusive.
""",
        "implications.md": """# Implications

The ThirdPersonState member lifecycle is now structurally clear, but its type depends on an indirect getter and a second indirect method call. The broad displacement inventory did not assign a class; it must not be used to resolve the virtual target.
""",
        "expected-discriminants.md": """# Expected discriminants

1. Determine which branch of PlayerCharacter slot+0x378 supplies the receiver.
2. Establish the receiver's concrete vtable and slot+0x150 implementation.
3. Resolve the returned object's concrete vtable and slot+0x8 finalizer.
4. Link the exact receiver/finalizer path to a specific one of the eight ProcessTrapHit teardown sites.
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
        "id": "EV-0342",
        "kind": "native",
        "source": "Complete GOG +0xA0 displacement search and read-only Ghidra traces of ThirdPersonState member setter, producer, constructor, lifecycle callback, and reset.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0342-note.md",
        "sha256": digest(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {GOG_SHA}; static only.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "A complete +0xA0 displacement inventory plus exact ThirdPersonState +0xA0 initialization, source setter, PlayerCamera producer, destructor, and reset. The returned member vtable/finalizer and linkage to the eight ProcessTrapHit sites remain unresolved.",
        "result": "The ThirdPersonState+0xA0 member is installed from a type-erased slot+0x150 return on the PlayerCharacter slot+0x378 result and is released through virtual slot+0x8. Its concrete class and ProcessTrapHit reachability are unknown. No direct AV11/AV12 sink appears in sampled bodies; Q64-H1/H2 remain proposed.",
        "related_evidence": ["EV-0329", "EV-0337", "EV-0341"],
        "local_hashes": local_hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L178 |" in claims or "| CL-L179 |" in claims:
        raise SystemExit("EV-0342 claims already exist")
    put(claims_path, claims.rstrip()
        + "\n| CL-L178 | In GOG AE 1.6.1179.0, FUN_1408e6500 obtains an object through PlayerCharacter slot +0x378, calls its slot +0x150, and stores the return in ThirdPersonState+0xA0 through FUN_1408ea490. | supported (bounded source/setter trace) | [EV-0342], [EV-0337], [EV-0329] | The getter receiver branch, returned object's concrete type, and ProcessTrapHit reachability remain unresolved. |"
        + "\n| CL-L179 | In GOG AE 1.6.1179.0, ThirdPersonState+0xA0 is refcounted and its reset/destruction paths may dispatch the old object's virtual slot +0x8 finalizer. | supported (bounded member lifecycle trace) | [EV-0342], [EV-0341] | The finalizer target/type is unresolved; no route-wide AV11/AV12 conclusion follows. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    put(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0342 extends M-0064: ThirdPersonState+0xA0 receives the return of a type-erased slot+0x150 call on the PlayerCharacter slot+0x378 result. Setter/reset/destructor paths refcount and may finalize the prior object through slot+0x8. The getter branch, concrete return type/finalizer, and ProcessTrapHit reachability remain unknown. Claims CL-L178 and CL-L179 -> M-0064.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph_path, graph_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0342 establishes a structural path: PlayerCharacter slot+0x378 result -> virtual slot+0x150 result -> ThirdPersonState+0xA0 -> refcounted virtual slot+0x8 cleanup. These are GOG AE 1.6.1179.0 source links. The returned type/finalizer and any connection to ProcessTrapHit remain unsupported; no causal edge to Actor::UseSkill or OBJ-1 is added. Claims CL-L178 and CL-L179 -> M-0064.\n")

    index_path = ROOT / "experiments/README.md"
    put(index_path, index_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEXP-0080 / EV-0342 traces ThirdPersonState+0xA0 from a type-erased slot+0x150 producer to refcounted slot+0x8 cleanup; the member type and ProcessTrapHit link remain open.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    if "EV-0342" not in q64.setdefault("evidence", []):
        q64["evidence"].append("EV-0342")
    for claim_id in ("CL-L178", "CL-L179"):
        if claim_id not in q64.setdefault("linked_claims", []):
            q64["linked_claims"].append(claim_id)
    for hypothesis in q64.get("hypotheses", []):
        if "EV-0342" not in hypothesis.setdefault("evidence", []):
            hypothesis["evidence"].append("EV-0342")
    q64["next_action"] = (
        "Resolve the concrete object returned by the PlayerCharacter +0x378 getter and its slot +0x150 "
        "implementation/return vtable. Match that returned object's +0x8 finalizer to a specific one of the "
        "eight ProcessTrapHit teardown sites, keeping getter branch and state selection unknown until evidence distinguishes them."
    )
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    with (ROOT / "research/SESSION_LOG.md").open("a", encoding="utf-8") as stream:
        stream.write("\n- " + datetime.now(timezone.utc).isoformat(timespec="seconds")
            + " TX-20261017-0011 research update: EV-0342 / CL-L178 / CL-L179 registered. The ThirdPersonState+0xA0 member is installed from a type-erased slot+0x150 return on the PlayerCharacter slot+0x378 result and may be released through slot+0x8. A complete displacement scan is generic; exact GOG function traces establish the field lifecycle but not the member type or ProcessTrapHit link. Next: resolve the getter receiver/result vtables and tie the finalizer to one teardown site.\n")
    print("registered EV-0342 / CL-L178 / CL-L179; Q-0064 remains open")


if __name__ == "__main__":
    main()
