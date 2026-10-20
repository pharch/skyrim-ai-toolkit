#!/usr/bin/env python3
"""Register the bounded ThirdPersonState+0xA0 child-resource origin trace."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0074-thirdperson-child-resource-origin"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = {
    "20261018T034911Z": ["TARGET_RVA=0x79E850", "OUTGOING_DIRECT_CALL_EDGE_COUNT=0", "INDIRECT_CALL_SITE_COUNT=0"],
    "20261018T035006Z": ["TARGET_RVA=0x79E5A0", "OUTGOING_DIRECT_CALL_EDGE_COUNT=3", "INDIRECT_CALL_SITE_COUNT=0"],
    "20261018T035144Z": ["OFFSET_QUERY=0xA0", "OFFSET_SCAN_COMPLETE=true", "OFFSET_COMPUTED_WRITER_ANALYSIS_COMPLETE=true"],
    "20261018T035413Z": ["TARGET_RVA=0x8EA490", "param_1 + 0xa0", "FUN_140cee240", "INDIRECT_CALL_SITE_COUNT=1"],
    "20261018T035513Z": ["TARGET_RVA=0x8E6500", "FUN_1408ea490(plVar2,uVar4,0)", "INDIRECT_CALL_SITE_COUNT=4"],
    "20261018T035714Z": ["TARGET_RVA=0xD1F3C0", "FUN_140d1f3c0", "INDIRECT_CALL_SITE_COUNT=1"],
}

def h(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")

def check(stamp: str, markers: list[str]):
    mp = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(mp.read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    if (meta.get("analysis_distribution") != "GOG" or meta.get("analysis_binary_product_version") != "1.6.1179"
        or meta.get("analysis_binary_sha256") != BINARY or meta.get("exit_code") != 0 or meta.get("ok") is not True
        or meta.get("read_only") is not True or meta.get("auto_analysis_disabled") is not True
        or meta.get("import_attempted") is not False or meta.get("overwrite_attempted") is not False
        or checks.get("program_identity_matches_gog_binary") is not True or checks.get("script_no_error") is not True):
        raise SystemExit(f"identity/read-only/completion check failed: {stamp}")
    if meta.get("query_mode") == "memory_displacement_search":
        required = ["requested_displacement", "displacement_scan_complete", "visitor_symbol_scan_complete",
                    "writer_analysis_complete", "computed_writer_analysis_complete"]
    else:
        required = ["function_lookup", "requested_rva_lookup", "direct_call_edge_scan", "decompilation"]
    if any(checks.get(key) is not True for key in required):
        raise SystemExit(f"required query component failed: {stamp}")
    stdout = ROOT / meta["artifacts"]["stdout"]
    raw = stdout.read_text(encoding="utf-8", errors="replace")
    if h(stdout) != meta.get("stdout_sha256") or any(marker not in raw for marker in markers):
        raise SystemExit(f"capture/hash/marker failure: {stamp}")
    files = [mp] + [ROOT / relative for relative in meta["artifacts"].values()]
    if any(not path.is_file() for path in files):
        raise SystemExit(f"missing capture: {stamp}")
    return meta, {path.relative_to(ROOT).as_posix(): h(path) for path in files}

def main() -> None:
    ev_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(ev_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0336" for row in evidence["items"]):
        raise SystemExit("EV-0336 already registered")
    hashes, rows = {}, []
    for stamp, markers in CAPTURES.items():
        meta, local = check(stamp, markers)
        hashes.update(local)
        rows.append({"stamp": stamp, "query_mode": meta.get("query_mode"), "requested_rva": meta.get("requested_rva"),
            "requested_search_displacement": meta.get("requested_search_displacement"),
            "checks": meta.get("checks"), "stdout_sha256": meta.get("stdout_sha256"),
            "stderr_sha256": meta.get("stderr_sha256"), "query_script_sha256": meta.get("query_script_sha256")})

    note = TX / "EV-0336-note.md"
    put(note, f"""# EV-0336 — ThirdPersonState+0xA0 child-resource origin

## Build and method

Six identity-checked read-only captures used the existing GOG Skyrim AE 1.6.1179.0 project (analysis binary SHA-256 `{BINARY}`), with auto-analysis disabled and no import or overwrite. The displacement scan completed, but offset matches are treated only as candidate locations; exact ownership is established from FUN_1408ea490's receiver/data flow. The NiNode method comparison is conditional and does not identify the actual runtime receiver vtable. Capture hashes and query markers are in the private manifest. No GOG RVA is transferred to Steam 1.6.1170.0.

## Direct observations

- FUN_1408e9990 clears `ThirdPersonState+0xA0` and releases its old value through that object's vtable slot +0x8 when its reference count reaches zero [EV-0335]. FUN_1408ea490 is the writer: it increments a replacement pointer, stores it at receiver+0xA0, final-releases a replaced pointer through slot+0x8, derives the member pointer at object+0x10, and calls FUN_140cee240 with receiver+0xA8 and that derived pointer [capture 20261018T035413Z].
- FUN_1408e6500 obtains a pointer via PlayerCharacter virtual slot +0x378 with flag 0, converts its input through FUN_140cee0a0, and calls slot +0x150 on the returned pointer. The returned value is passed to FUN_1408ea490 for the ThirdPersonState object at PlayerCamera+0xF8 or the current state, depending on control flow [capture 20261018T035513Z].
- EV-0329 maps PlayerCharacter slot +0x378 to FUN_1407371f0; flag 0 routes through FUN_1402e55a0 and a thread-local or nested PlayerCharacter field path. The exact runtime receiver type and its slot+0x150 target are not observed [EV-0329].
- The NiNode table at RVA 0x19AC3F0 maps slot +0x150 (index 42) to FUN_140d1f3c0 [EV-0334]. That method first calls FUN_140d1daa0; if the result is null, it walks a child array at receiver+0x118 and calls each child slot+0x150 with the same argument until one returns non-null [capture 20261018T035714Z]. This is a conditional NiNode comparator only; the PlayerCharacter-returned object's actual vtable is not known.
- The two direct helpers called by FUN_1408e9990 are also mapped. FUN_14079e850 scans a pointer array for a matching member and has no outgoing direct or indirect calls [capture 20261018T034911Z]. FUN_14079e5a0 removes or inserts the member across pointer arrays and calls three direct container helpers, with no indirect sites in its body [capture 20261018T035006Z]. Neither body contains a direct Actor::UseSkill/AV11/AV12 sink, but their direct descendants and the +0xA0 finalizer remain open.
- The completed +0xA0 displacement scan found many same-offset candidates across the executable, including nearby ThirdPersonState methods. It does not by itself prove the member's class; the exact setter and owner are established from the direct FUN_1408ea490 trace [capture 20261018T035144Z].

## Cross-domain synthesis

ThirdPersonState+0xA0 is a data-selected child/resource candidate obtained through PlayerCharacter slot+0x378 and another object's slot+0x150. NiNode implements that slot as a recursive child lookup, which creates a falsifiable NiAVObject-family hypothesis but not a confirmed type edge. Compare it with the PlayerCharacter+0x730 scene-child lifecycle [EV-0334], the conditional +0x8F8 NiNode candidate [EV-0331], and the data-selected +0x9A0/+0x9A8 model resources [EV-0333]. Q-0065 is expanded to include this fourth path. No causal edge to Actor::UseSkill AV11/AV12 or OBJ-1 is added; the actual receiver vtable, nested finalizer, and state selected at teardown remain unknown.

## Exact next discriminant

Resolve the concrete return type and vtable for PlayerCharacter slot+0x378 with flag 0 in this call context, then identify that object's slot+0x150 target. Recover the returned member's exact slot+0x8 finalizer and screen it for the mapped Actor::UseSkill AV11/AV12 sink. Do not equate the NiNode comparator table with a runtime target without matching vtable evidence.
""")
    hashes[note.relative_to(ROOT).as_posix()] = h(note)

    docs = {
        "README.md": "# EXP-0074 — ThirdPersonState child-resource origin\n\nTrace the value stored at ThirdPersonState+0xA0 through its writer, PlayerCharacter slot+0x378, and a conditional NiNode slot+0x150 comparator. The runtime receiver vtable and finalizer remain unknown.\n",
        "hypothesis.md": "# Competing models\n\n- H1: PlayerCharacter slot+0x378 flag 0 returns a NiAVObject/NiNode-compatible root; slot+0x150 selects a child stored at ThirdPersonState+0xA0.\n- H2: the returned object is another interface implementation sharing slot+0x150; NiNode is only a structural comparator.\n- Q64-H1: no resolved descendant reaches AV11/AV12 skill progress.\n- Q64-H2: a resolved descendant reaches that sink.\n\nThe code path supports a named-object/child-resource candidate, but no dynamic vtable or child finalizer is selected.\n",
        "protocol.md": "# Protocol\n\nUse only identity-checked GOG AE 1.6.1179.0 read-only/no-analysis Ghidra captures through the strict dispatcher. Treat same-offset scan hits and matching slot offsets as candidate relationships. Require exact receiver vtable/target evidence before assigning NiNode or NiAVObject type; do not transfer RVAs to Steam.\n",
        "results.md": "# Results\n\nEV-0336 maps ThirdPersonState+0xA0 through its setter FUN_1408ea490. FUN_1408e6500 obtains a receiver through PlayerCharacter slot+0x378, calls its slot+0x150 with a converted input, and stores the returned pointer in a ThirdPersonState. NiNode slot+0x150 maps to FUN_140d1f3c0, which performs recursive child-array traversal, but the actual receiver vtable is unknown. FUN_1408e9990 releases +0xA0 through slot+0x8 when final; that finalizer is unresolved. The mapped helper bodies contain no direct skill-progress sink, but Q64-H1/H2 remain open [EV-0336], [EV-0335], [EV-0329], [EV-0334].\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- A matching runtime/static receiver vtable at the callsite and a NiNode/NiAVObject slot+0x150 implementation supports H1.\n- A distinct concrete class with a different slot+0x150 implementation supports H2.\n- A resolved member finalizer reaching Actor::UseSkill with AV11/AV12 supports Q64-H2.\n- Missing receiver or finalizer evidence is inconclusive.\n",
        "implications.md": "# Implications\n\nThe camera-state member may be a named child object, which could connect the PlayerCamera cleanup branch to scene-graph ownership. Slot similarity does not establish that connection. Preserve the +0x730, +0x8F8, +0x9A0/+0x9A8, and +0xA0 paths as separate until matching class evidence exists.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Recover the actual receiver class/vtable for PlayerCharacter slot+0x378 flag 0 in FUN_1408e6500.\n2. Map that receiver's slot+0x150 and compare with the conditional NiNode method FUN_140d1f3c0.\n3. Identify the returned +0xA0 member's exact vtable and slot+0x8 finalizer.\n4. Screen resolved descendants against Actor::UseSkill AV11/AV12.\n"
    }
    for name, content in docs.items():
        put(EXP / name, content)
    manifest = TX / "EV-0336-capture-manifest.json"
    put(manifest, json.dumps({"evidence_id": "EV-0336", "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY, "captures": rows}, indent=2, ensure_ascii=False))
    hashes[manifest.relative_to(ROOT).as_posix()] = h(manifest)
    hashes[(EXP / "register_ev0336.py").relative_to(ROOT).as_posix()] = h(EXP / "register_ev0336.py")
    for path in EXP.iterdir():
        if path.is_file() and path.name != "register_ev0336.py":
            hashes[path.relative_to(ROOT).as_posix()] = h(path)
    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "edition": "AE",
        "modified_state": False, "id": "EV-0336", "kind": "native",
        "source": "Identity-checked GOG Skyrim AE 1.6.1179.0 ThirdPersonState+0xA0 writer, caller, helper, and conditional NiNode slot+0x150 method traces.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0336-note.md",
        "sha256": h(note), "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference", "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Six complete identity-checked captures trace two ThirdPersonState transition helpers, the +0xA0 displacement, exact pointer writer, non-null value producer, and a conditional NiNode slot+0x150 comparator.",
        "result": "FUN_1408ea490 writes/refcounts ThirdPersonState+0xA0. FUN_1408e6500 gets a receiver through PlayerCharacter vtable+0x378, calls its slot+0x150, and stores the result in a ThirdPersonState. NiNode slot+0x150 maps to recursive child traversal, but the actual dynamic receiver and returned member class/finalizer remain unknown. No direct AV11/AV12 sink appears in the mapped callback/helper bodies; Q64-H1/H2 remain unresolved.",
        "related_evidence": ["EV-0329", "EV-0334", "EV-0335", "EV-0217", "EV-0223", "EV-0280", "EV-0281"],
        "local_hashes": hashes,
    })
    put(ev_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L168 |" in claims: raise SystemExit("CL-L168 already exists")
    put(claims_path, claims.rstrip() + "\n| CL-L168 | In GOG AE 1.6.1179.0, FUN_1408ea490 writes/refcounts ThirdPersonState+0xA0; FUN_1408e6500 supplies its value by calling slot+0x150 on an object returned by PlayerCharacter slot+0x378. NiNode's same-offset slot maps to recursive child traversal, making an NiAVObject child a candidate. | supported (bounded producer trace; conditional class inference) | [EV-0336], [EV-0329], [EV-0334] | The actual receiver vtable, returned member class, slot+0x8 finalizer, and teardown-selected camera state are unknown. No Q64-H1/H2 result, global AV11/AV12 exclusion, Steam behavior, or vanilla reproduction follows. No OBJ-1 edge is supported. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8")
    if "## M-0065 —" in mechanisms: raise SystemExit("M-0065 already exists")
    put(mechanisms_path, mechanisms.rstrip() + "\n\n## M-0065 — ThirdPersonState+0xA0 named-child resource candidate (Q-0064)\n\nFUN_1408ea490 stores and refcounts ThirdPersonState+0xA0. FUN_1408e6500 obtains an object through PlayerCharacter vtable+0x378, calls that object's slot+0x150 with a converted input, and passes the result into the state setter. NiNode slot+0x150 maps to FUN_140d1f3c0 recursive child traversal, but the actual receiver vtable and returned member finalizer are unresolved [EV-0336], [EV-0329], [EV-0334]. This is a conditional NiAVObject-family candidate only; no causal edge or AV11/AV12 result is established. Claim CL-L168 -> M-0065.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph_path, graph_path.read_text(encoding="utf-8").rstrip() + "\n\nEV-0336 expands the PlayerCamera cleanup model: ThirdPersonState+0xA0 receives a value from PlayerCharacter vtable+0x378 followed by a dynamic slot+0x150 lookup. NiNode's slot+0x150 recursively searches child nodes, making a shared NiAVObject path with the +0x730 scene child [EV-0334] and conditional +0x8F8 skeleton [EV-0331] testable. The receiver vtable is not mapped, so no edge to NiNode is drawn; +0x9A0/+0x9A8 remain separate data-selected model resources [EV-0333]. No causal edge to Actor::UseSkill AV11/AV12 or OBJ-1 is added. Claim CL-L168 -> M-0065.\n")

    index_path = ROOT / "experiments/README.md"
    put(index_path, index_path.read_text(encoding="utf-8").rstrip() + "\n\nEXP-0074 / EV-0336 traces ThirdPersonState+0xA0 through PlayerCharacter slot+0x378 and a dynamic slot+0x150 lookup. NiNode's same-offset method is only a conditional comparator; the runtime receiver and member finalizer remain unresolved.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    q65 = next(row for row in frontier["items"] if row.get("id") == "Q-0065")
    if "EV-0336" not in q64.setdefault("evidence", []): q64["evidence"].append("EV-0336")
    if "CL-L168" not in q64.setdefault("linked_claims", []): q64["linked_claims"].append("CL-L168")
    q64["next_action"] = "Resolve the concrete return type and vtable for PlayerCharacter slot+0x378 with flag 0 in FUN_1408e6500; then identify that object's slot+0x150 target and the returned member's slot+0x8 finalizer. Screen the resolved path for Actor::UseSkill AV11/AV12 and retain the teardown-selected camera state as dynamic."
    q65["question"] = "Do PlayerCharacter+0x730 cell-scene child, +0x8F8 first-person skeleton, +0x9A0/+0x9A8 model outputs, and ThirdPersonState+0xA0 named-child candidate converge on a shared NiAVObject/NiNode finalizer family, or are they distinct resource classes?"
    if "EV-0336" not in q65.setdefault("evidence", []): q65["evidence"].append("EV-0336")
    if "CL-L168" not in q65.setdefault("linked_claims", []): q65["linked_claims"].append("CL-L168")
    for hypothesis in q65.get("hypotheses", []):
        if "EV-0336" not in hypothesis.setdefault("evidence", []): hypothesis["evidence"].append("EV-0336")
    q65["next_action"] = "Compare exact producer and runtime vtable evidence for PlayerCharacter+0x730, +0x8F8, +0x9A0/+0x9A8, and ThirdPersonState+0xA0. Confirm or falsify a common NiAVObject/NiNode vtable/finalizer; do not infer identity from matching slot offsets."
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    roadmap = ROOT / "ROADMAP.md"
    put(roadmap, roadmap.read_text(encoding="utf-8").rstrip() + "\n\nEV-0336 maps ThirdPersonState+0xA0 to a dynamic child-resource lookup via PlayerCharacter slot+0x378 and the returned object's slot+0x150. NiNode implements the same slot as recursive child traversal, creating a conditional common-family hypothesis with +0x730 and +0x8F8; the actual receiver and member finalizer are still unknown. Q-0065 now includes this fourth candidate. Q-0064 remains active on the exact receiver/finalizer and AV11/AV12 path.\n")
    with (ROOT / "research/SESSION_LOG.md").open("a", encoding="utf-8") as stream:
        stream.write("\n- " + datetime.now(timezone.utc).isoformat(timespec="seconds") + " TX-20261017-0011 research update: EV-0336 / CL-L168 / M-0065 registered. ThirdPersonState+0xA0 receives a result from a PlayerCharacter slot+0x378 then dynamic slot+0x150 lookup. NiNode has recursive child traversal at the same slot, but actual receiver/finalizer are untyped; Q-0065 expanded as a testable cross-field candidate. No causal edge to Actor::UseSkill or OBJ-1 is added.\n")
    print("registered EV-0336 / CL-L168 / M-0065; Q-0064 remains open; Q-0065 expanded")

if __name__ == "__main__":
    main()
