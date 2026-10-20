#!/usr/bin/env python3
"""Register the exact empty-array initialization and first bhkRigidBody cleanup pass."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0092-q64-rigidbody-empty-initial-array"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
STAMPS = [
    "20261018T060141Z", "20261018T060608Z", "20261018T060800Z",
    "20261018T061115Z", "20261018T061221Z", "20261018T061438Z",
    "20261018T061531Z", "20261018T061628Z", "20261018T061842Z",
    "20261018T061940Z", "20261018T062102Z", "20261018T062213Z",
    "20261018T062317Z", "20261018T062415Z", "20261018T062624Z",
    "20261018T062727Z", "20261018T062830Z", "20261018T062934Z",
    "20261018T063035Z", "20261018T063134Z", "20261018T063239Z",
]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")

def load_capture(stamp: str, markers: list[str]) -> tuple[dict, Path, Path]:
    meta_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    stdout = ROOT / meta["artifacts"]["stdout"]
    valid = (
        meta.get("analysis_distribution") == "GOG"
        and meta.get("analysis_binary_product_version") == "1.6.1179"
        and meta.get("analysis_binary_sha256") == BINARY
        and meta.get("program_executable_path_matches_gog_binary") is True
        and meta.get("ok") is True
        and meta.get("exit_code") == 0
        and meta.get("read_only") is True
        and meta.get("auto_analysis_disabled") is True
        and meta.get("import_attempted") is False
        and meta.get("overwrite_attempted") is False
        and checks.get("program_identity_matches_gog_binary") is True
        and checks.get("script_no_error") is True
        and digest(stdout) == meta.get("stdout_sha256")
    )
    if not valid:
        raise SystemExit(f"capture identity/completion check failed: {stamp}")
    raw = stdout.read_text(errors="replace")
    if any(marker not in raw for marker in markers):
        raise SystemExit(f"capture marker check failed: {stamp}")
    return meta, meta_path, stdout

def main() -> None:
    expected = {
        "20261018T060141Z": [
            "OFFSET_ACCESS_COUNT=31281", "OFFSET_WRITER_CANDIDATE_FUNCTION_COUNT=4380",
            "OFFSET_WRITER_CANDIDATE=FUN_140550ff0 @ 140550ff0 RVA=0x550FF0",
        ],
        "20261018T060608Z": [
            "OFFSET_ACCESS_COUNT=2825", "function:FUN_1408e7230",
            "OFFSET_WRITER_CANDIDATE=FUN_1408e7230 @ 1408e7230 RVA=0x8E7230",
        ],
        "20261018T060800Z": [
            "DECOMPILATION_BEGIN=FUN_1408e7230",
            "FUN_1408e7230(DAT_1430febf8);", "bhkRigidBody::vftable",
            "*(longlong **)(param_1 + 0x128) = plVar12;",
        ],
        "20261018T061115Z": [
            "CALLEE_DECOMPILATION_BEGIN=FUN_140e92c60",
            "if (*(uint *)(param_1 + 7) != 0)",
            "(**(code **)(*plVar3 + 8))();",
        ],
        "20261018T061221Z": [
            "DECOMPILATION_BEGIN=FUN_140e93210",
            "(**(code **)(*param_1 + 0x128))(param_1,uVar9);",
            "(**(code **)(*param_1 + 0x188))(param_1,param_2);",
        ],
        "20261018T061438Z": [
            "POINTER_TABLE_BASE_RVA=0x17AFB18",
            "POINTER_TABLE_ENTRY=index:37 address:1417afc40 value:0x140EBE890",
            "POINTER_TABLE_ENTRY=index:38 address:1417afc48 value:0x140E84540",
            "POINTER_TABLE_ENTRY=index:42 address:1417afc68 value:0x140E94580",
            "POINTER_TABLE_ENTRY=index:49 address:1417afca0 value:0x140EBEAA0",
        ],
        "20261018T061531Z": [
            "DECOMPILATION_BEGIN=FUN_140ebe890",
            "param_1[2] != param_2", "FUN_140ebe4a0(param_1,param_2);",
        ],
        "20261018T061628Z": [
            "DECOMPILATION_BEGIN=FUN_140ebeaa0",
            "(**(code **)(*param_1 + 0x158))(param_1,1);",
        ],
        "20261018T061842Z": [
            "DECOMPILATION_BEGIN=FUN_140e94ab0",
            "undefined8 *param_2", "param_2[7] = 0;",
        ],
        "20261018T061940Z": [
            "DECOMPILATION_BEGIN=FUN_140e93000",
            "*(longlong *)(param_1 + 0x18)", "puVar8 + 0x24",
        ],
        "20261018T062102Z": [
            "DECOMPILATION_BEGIN=FUN_140e940f0",
            "*(undefined4 *)(lVar2 + 0x20) = 0;",
            "*(undefined8 *)(param_1 + 0x18) = 0;",
        ],
        "20261018T062213Z": [
            "DECOMPILATION_BEGIN=FUN_140ebe3e0",
            "param_1[2] = 0;", "bhkRefObject::vftable",
        ],
        "20261018T062317Z": [
            "DECOMPILATION_BEGIN=FUN_140ebe4a0",
            "(**(code **)(*param_1 + 0x130))(param_1,0);",
            "(**(code **)(*param_1 + 0x130))(param_1,1);",
        ],
        "20261018T062415Z": [
            "DECOMPILATION_BEGIN=FUN_140e84540",
            "(**(code **)(*param_1 + 0x150))();",
            "FUN_140ebe4f0(param_1,param_2);",
        ],
        "20261018T062624Z": [
            "DECOMPILATION_BEGIN=FUN_140e94580",
            "if (*(int *)(param_1 + 0x38) != 0)",
            "(**(code **)(**(longlong **)(*(longlong *)(param_1 + 0x28) + uVar3 * 8) + 0x150))();",
        ],
        "20261018T062727Z": [
            "DECOMPILATION_BEGIN=FUN_140cc82a0",
            "*param_1 = 0;",
        ],
        "20261018T062830Z": [
            "DECOMPILATION_BEGIN=FUN_140cc85e0",
            "*param_1 = 0;", "*(undefined4 *)(param_1 + 1) = 0;",
        ],
        "20261018T062934Z": [
            "DECOMPILATION_BEGIN=FUN_140e83cb0",
            "(*param_1 + 0x140)", "FUN_140e8beb0();", "FUN_140e8bed0();",
        ],
        "20261018T063035Z": [
            "DECOMPILATION_BEGIN=FUN_140e8beb0",
            "FUN_140ccac00(param_1 + 0xc598);",
        ],
        "20261018T063134Z": [
            "DECOMPILATION_BEGIN=FUN_140e8bed0",
            "FUN_140ccae50(param_1 + 0xc598);",
        ],
        "20261018T063239Z": [
            "DECOMPILATION_BEGIN=FUN_140e83e70",
            "*(longlong *)(param_1 + 0x10) + 0x10",
        ],
    }
    captures = {stamp: load_capture(stamp, expected[stamp]) for stamp in STAMPS}

    note = TX / "EV-0354-note.md"
    put(note, f"""# EV-0354 — The PlayerCamera rigid body's first child cleanup pass starts empty

## Build and method

Identity-checked queries used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BINARY}, through the strict dispatcher in read-only/no-analysis mode. Twenty-one capture stamps are preserved in the manifest. No GOG RVA is transferred to Steam AE 1.6.1170.0.

## Direct observations

- FUN_1407373e0 calls FUN_1408e7230(DAT_1430febf8). That constructor installs bhkRigidBody::vftable and stores the body at PlayerCamera+0x128 [EV-0353; capture 20261018T060800Z].
- The exact bhkRigidBody table maps byte slots +0x128, +0x130, +0x150, and +0x188 to FUN_140ebe890, FUN_140e84540, FUN_140e94580, and FUN_140ebeaa0 respectively [capture 20261018T061438Z].
- The allocation constructor FUN_140e83c30 calls base FUN_140ebe3e0, which sets body[2] (body+0x10) to null. It then initializes body+0x28 with FUN_140cc85e0 and body+0x38 with FUN_140cc82a0; those helpers set the pointer and count fields to zero [captures 20261018T062213Z; 20261018T062727Z; 20261018T062830Z].
- FUN_140e93210 calls body slot +0x128 with a newly created state pointer. FUN_140ebe890 routes that change through FUN_140ebe4a0, which calls slot +0x130 first with 0 and then with 1. Slot +0x130 is FUN_140e84540. On the zero call it dispatches body slot +0x150, FUN_140e94580 [captures 20261018T061221Z; 20261018T061531Z; 20261018T062317Z; 20261018T062415Z; 20261018T061438Z].
- FUN_140e94580 checks body+0x38 before iterating body+0x28 and dispatching each child object's slot +0x150. Because this constructor initialized the count to zero and the captured setter does not itself write body+0x38, the first initializer-driven cleanup pass performs zero child iterations [captures 20261018T062624Z; 20261018T062727Z; 20261018T062830Z].
- The later bhkRigidBody destructor FUN_140e92c60 also loops the same child count before slot +8 releases. This evidence bounds the initial construction/clear pass only; it does not prove no later method or Havok path populates the array [EV-0353; capture 20261018T061115Z].
- Several +0x28 displacement candidates were false positives: FUN_140e94ab0 writes an output structure through param_2, and FUN_140e93000 fills a separate physics configuration; neither establishes a body+0x28 child insertion [captures 20261018T061842Z; 20261018T061940Z].
- FUN_140e83cb0 reads the current body state and conditionally calls helpers that write a large state field at +0xC598. The captured helpers do not write the body+0x28/+0x38 child vector [captures 20261018T062934Z; 20261018T063035Z; 20261018T063134Z].

## Competing-model assessment

This removes child slot +0x150 dispatch from the first PlayerCamera rigid-body setup pass, but later population and destruction remain unresolved. No direct AV11/AV12 skill-progress sink appears in the resolved code. Q64-H1/H2 remain proposed; this bounded first-pass result does not prove armor XP suppression or a vanilla trap exploit. No causal edge to OBJ-1 or armor XP is added.

## Exact next discriminant

Inspect FUN_140ebf0b0, called immediately after the body+0x28 child loop, then trace producer-backed writes to body+0x28 and +0x38 after initialization. Resolve any populated child table and slot +0x150 descendants before excluding the remaining cleanup path.
""")
    rows = {}
    for stamp, (meta, _, _) in captures.items():
        rows[stamp] = {
            "query_mode": meta.get("query_mode"),
            "requested_rva": meta.get("requested_rva"),
            "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
            "requested_search_displacement": meta.get("requested_search_displacement"),
            "checks": meta.get("checks"),
            "stdout_sha256": meta.get("stdout_sha256"),
            "stderr_sha256": meta.get("stderr_sha256"),
            "query_script_sha256": meta.get("query_script_sha256"),
        }
    manifest = TX / "EV-0354-capture-manifest.json"
    put(manifest, json.dumps({
        "evidence_id": "EV-0354",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY,
        "captures": rows,
    }, indent=2))
    docs = {
        "README.md": "# EXP-0092 — Empty initial rigid-body child array\n\nTrace the exact initial child-array state through the first PlayerCamera rigid-body cleanup pass.\n",
        "hypothesis.md": "# Competing models\n\n- Q64-H1: concrete teardown descendants avoid AV11/AV12 skill progress.\n- Q64-H2: a later populated body child reaches armor skill credit.\n\nAn empty first cleanup pass narrows only the constructor path.\n",
        "protocol.md": "# Protocol\n\nUse exact producer and initializer captures from the read-only GOG project. Keep offset-only candidates separate from receiver-proven writes. Resolve children only from a concrete populated table.\n",
        "results.md": "# Results\n\nThe body+0x28 pointer and +0x38 count initialize to zero. Its first initializer-driven cleanup calls FUN_140e94580, whose loop skips all child entries at count zero. Later child-array writes remain unresolved [EV-0354].\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- A producer that sets body+0x38 and a concrete child table reaching AV11/AV12 supports Q64-H2 for that later branch.\n- If all reachable producers keep the count zero or resolve children away from skill progress, Q64-H1 narrows for this branch only.\n- No writer source remains inconclusive.\n",
        "implications.md": "# Implications\n\nThe initial body setup has no child slot +0x150 dispatch. This does not constrain later body use or other PlayerCamera-owned objects.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Resolve FUN_140ebf0b0 and its child-vector effects.\n2. Find exact post-constructor writers of body+0x28 and +0x38.\n3. Map each populated child's slot +0x150 target and descendants.\n4. Screen concrete targets for AV11/AV12.\n",
    }
    for name, body in docs.items():
        put(EXP / name, body)

    hashes = {}
    for stamp, (meta, meta_path, stdout) in captures.items():
        for path in [meta_path, stdout] + [ROOT / value for value in meta["artifacts"].values()]:
            if path.is_file():
                hashes[path.relative_to(ROOT).as_posix()] = digest(path)
    for path in [note, manifest] + list(EXP.iterdir()) + [Path(__file__)]:
        if path.is_file():
            hashes[path.relative_to(ROOT).as_posix()] = digest(path)
    put(manifest, json.dumps({
        "evidence_id": "EV-0354",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY,
        "captures": rows,
        "registered_local_hashes": hashes,
    }, indent=2))
    hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0354" for item in evidence["items"]):
        raise SystemExit("EV-0354 already registered")
    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0354",
        "kind": "native",
        "source": "Read-only GOG Ghidra queries of the PlayerCamera bhkRigidBody table, exact child-vector initializer, state setter, first cleanup loop, and constructor-path helpers.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0354-note.md",
        "sha256": digest(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Exact PlayerCamera body producer and vftable methods; null body state; body+0x28 pointer and +0x38 count initializers; the slot+0x150 loop reached on initial state install; bounded setup helpers and two false-positive writer candidates. Later child-array population remains unresolved.",
        "result": "PlayerCamera+0x128 is a constructed bhkRigidBody. Its child-array pointer at +0x28 and count at +0x38 initialize to zero. During the first state install, slot+0x130 dispatches slot+0x150, whose function loops only while +0x38 is nonzero, so the initial cleanup pass performs zero child iterations. Later writers remain unresolved; Q64-H1/H2 stay proposed.",
        "related_evidence": ["EV-0325", "EV-0327", "EV-0352", "EV-0353"],
        "local_hashes": hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims = ROOT / "research/CLAIMS.md"
    claim_text = claims.read_text(encoding="utf-8")
    if "| CL-L192 |" in claim_text:
        raise SystemExit("CL-L192 already exists")
    put(claims, claim_text.rstrip() + "\n| CL-L192 | On the captured PlayerCamera bhkRigidBody construction path, the body+0x28 child pointer and +0x38 count initialize to zero; its first slot+0x150 cleanup loop therefore performs zero child iterations. | supported for the captured initial setup pass | [EV-0354], [EV-0353] | Later child-array producers, populated children, and AV11/AV12 reachability remain unresolved. |")

    mechanisms = ROOT / "research/MECHANISMS.md"
    put(mechanisms, mechanisms.read_text(encoding="utf-8").rstrip() + "\n\n## M-0074 — Empty initial bhkRigidBody child cleanup (Q-0064)\n\nThe PlayerCamera+0x128 bhkRigidBody initializes body+0x28 to null and body+0x38 to zero. Its first state install calls slot+0x150 FUN_140e94580, whose loop is guarded by the +0x38 count and dispatches child slot +0x150; the initial pass executes no child iteration. Later producers and the terminal bhkRigidBody cleanup remain unresolved [EV-0354], [EV-0353]. Claim CL-L192 -> M-0074.\n")

    graph = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph, graph.read_text(encoding="utf-8").rstrip() + "\n\nEV-0354 narrows the PlayerCamera rigid-body branch: the +0x28 child pointer and +0x38 count initialize to zero, so the first slot+0x150 cleanup loop has no entries. This is an initial-state result only; later producers remain open and no AV11/AV12 edge is added. Claim CL-L192 -> M-0074.\n")

    index = ROOT / "experiments/README.md"
    put(index, index.read_text(encoding="utf-8").rstrip() + "\n\nEXP-0092 / EV-0354 proves the initial PlayerCamera rigid-body child array is empty during its first slot+0x150 cleanup pass; later population remains unresolved.\n")

    roadmap = ROOT / "research/ROADMAP.md"
    put(roadmap, roadmap.read_text(encoding="utf-8").rstrip() + "\n\nEV-0354 bounds the first PlayerCamera rigid-body cleanup pass to an empty body+0x28/+0x38 child vector. Next resolve FUN_140ebf0b0 and any post-constructor vector writers. Claim CL-L192 -> M-0074.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(item for item in frontier["items"] if item.get("id") == "Q-0064")
    q65 = next(item for item in frontier["items"] if item.get("id") == "Q-0065")
    for item in (q64, q65):
        if "EV-0354" not in item.setdefault("evidence", []):
            item["evidence"].append("EV-0354")
        if "CL-L192" not in item.setdefault("linked_claims", []):
            item["linked_claims"].append("CL-L192")
        for hypothesis in item.get("hypotheses", []):
            if "EV-0354" not in hypothesis.setdefault("evidence", []):
                hypothesis["evidence"].append("EV-0354")
    q64["next_action"] = "Inspect FUN_140ebf0b0, called after the body+0x28 child loop, then trace exact post-constructor writes to body+0x28 and +0x38. Resolve any populated child table and its slot+0x150 descendants before excluding the remaining cleanup path."
    q65["next_action"] = "Compare producer-backed vtables for +0x730, +0x8F8, +0x9D0, +0x9A0/+0x9A8, ThirdPersonState+0xA0, and PlayerCamera-owned cleanup objects. EV-0354 bounds only the initial bhkRigidBody child cleanup pass; later population remains unresolved."
    q65.setdefault("attempts", []).append({
        "action_key": "q65-rigidbody-empty-initial-child-pass",
        "outcome": "EV-0354 proves the initial PlayerCamera bhkRigidBody child pointer/count are zero and its first slot+0x150 loop skips; later population remains unknown.",
        "evidence": ["EV-0354"],
        "new_discriminant": "A post-constructor count/pointer writer with a producer-backed child table is required to compare this branch with resource finalizers.",
        "next_action": q65["next_action"],
    })
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    checkpoint = ROOT / "experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"
    source = checkpoint.read_text(encoding="utf-8")
    needle = "- Q-0064 / EV-0353 resolves PlayerCamera+0x128 to bhkRigidBody and its slot+8 destructor to FUN_140e92c60; that body's +0x28 child array still dispatches unresolved slot+8 targets. The next branch traces those child producers.\n"
    addition = "- Q-0064 / EV-0354 proves the rigid body's +0x28 pointer and +0x38 count start zero, so its first slot+0x150 loop skips; later vector population is still unknown. The next query is FUN_140ebf0b0 and post-constructor writers.\n"
    if needle not in source:
        raise SystemExit("checkpoint EV-0353 line missing")
    put(checkpoint, source.replace(needle, needle + addition))

    print("registered EV-0354 / CL-L192 / M-0074; Q-0064 continues on rigid-body child-vector writers")
if __name__ == "__main__":
    main()
