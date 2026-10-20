#!/usr/bin/env python3
"""Register the producer-backed PlayerCamera bhkRigidBody cleanup chain."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0091-q64-rigidbody-finalizer"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
STAMPS = [
    "20261018T060608Z", "20261018T060800Z", "20261018T060919Z",
    "20261018T061014Z", "20261018T061115Z", "20261018T061221Z",
]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")

def validate_capture(stamp: str, markers: list[str]) -> tuple[dict, Path, Path]:
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
        "20261018T060608Z": [
            "OFFSET_ACCESS_COUNT=2825",
            "OFFSET_ACCESS=address:1408e743b rva:0x8E743B function:FUN_1408e7230",
            "OFFSET_WRITER_CANDIDATE=FUN_1408e7230 @ 1408e7230 RVA=0x8E7230",
        ],
        "20261018T060800Z": [
            "DECOMPILATION_BEGIN=FUN_1408e7230",
            "XREF_CALL_EDGE=140737651 -> 1408e7230 caller=FUN_1407373e0",
            "FUN_1408e7230(DAT_1430febf8);",
            "bhkRigidBody::vftable",
            "*(longlong **)(param_1 + 0x128) = plVar12;",
        ],
        "20261018T060919Z": [
            "POINTER_TABLE_BASE_RVA=0x17AFB18",
            "POINTER_TABLE_ENTRY=index:0 address:1417afb18 value:0x1402F2D10",
            "POINTER_TABLE_ENTRY=index:1 address:1417afb20 value:0x140D28F40",
            "POINTER_TABLE_SCAN_COMPLETE=true",
        ],
        "20261018T061014Z": [
            "DECOMPILATION_BEGIN=FUN_140d28f40",
            "(**(code **)*param_1)(param_1,1);",
        ],
        "20261018T061115Z": [
            "DECOMPILATION_BEGIN=FUN_1402f2d10",
            "FUN_140e92c60();", "thunk_FUN_14011bbb0(param_1,0x40);",
            "DECOMPILATION_BEGIN=FUN_1402f2d10",
            "(**(code **)(*plVar3 + 8))();",
        ],
        "20261018T061221Z": [
            "DECOMPILATION_BEGIN=FUN_140e93210",
            "INDIRECT_CALL_SITE_COUNT=4",
            "(**(code **)(*param_1 + 0x128))(param_1,uVar9);",
            "(**(code **)(*param_1 + 0x188))(param_1,param_2);",
        ],
    }
    captures = {stamp: validate_capture(stamp, expected[stamp]) for stamp in STAMPS}

    note = TX / "EV-0353-note.md"
    put(note, f"""# EV-0353 — PlayerCamera +0x128 resolves to a bhkRigidBody finalizer

## Build and method

Identity-checked queries used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BINARY}, through the strict dispatcher in read-only/no-analysis mode. Six capture stamps are preserved in the manifest. No GOG RVA is transferred to Steam AE 1.6.1170.0.

## Direct observations

- The displacement scan includes FUN_1408e7230 as a candidate writer for its receiver+0x128 [capture 20261018T060608Z]. The decompilation shows its caller FUN_1407373e0 invokes FUN_1408e7230(DAT_1430febf8), tying that receiver to the PlayerCamera global [capture 20261018T060800Z].
- When PlayerCamera+0x128 is null, FUN_1408e7230 constructs an object, changes its table through bhkEntity to bhkRigidBody, increments the refcount, and stores the body at PlayerCamera+0x128. Thus the two destructor slot+8 calls on this owner member are data-selected to this constructed bhkRigidBody family when that value is present [capture 20261018T060800Z; EV-0352].
- The exact bhkRigidBody table at RVA 0x17AFB18 has slot 0 FUN_1402f2d10 and slot +8 FUN_140d28f40 [capture 20261018T060919Z]. FUN_140d28f40 redispatches slot 0 with flag 1. FUN_1402f2d10 calls FUN_140e92c60 and conditionally frees 0x40 bytes [captures 20261018T061014Z; 20261018T061115Z].
- FUN_140e92c60 resets the bhkRigidBody table, releases an owned pointer array from body+0x28 and count body+0x38, and at zero refcount calls each child object's slot +8. Its direct path contains no Actor::UseSkill/AV11/AV12 sink, but the child objects and their targets remain unresolved [capture 20261018T061115Z].
- The body initializer FUN_140e93210 is called on this body and has four further dynamic sites, including body-table slots +0x128 and +0x188. Their data-selected targets are not part of the destructor proof [capture 20261018T061221Z].

## Competing-model assessment

This resolves the PlayerCamera+0x128 branch through the bhkRigidBody destructor and narrows its immediate cleanup path away from a direct skill-progress sink. The body-owned child array still dispatches unknown slot+8 targets, so Q64-H1/H2 remain proposed. No causal edge to OBJ-1 or armor XP is added.

## Exact next discriminant

Trace the bhkRigidBody body+0x28 child-array producers from its exact construction and initialization path. Resolve concrete child vtables and their slot+8 descendants, screening each resolved path for AV11/AV12.
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
    manifest = TX / "EV-0353-capture-manifest.json"
    put(manifest, json.dumps({
        "evidence_id": "EV-0353",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY,
        "captures": rows,
    }, indent=2))
    docs = {
        "README.md": "# EXP-0091 — PlayerCamera rigid-body finalizer\n\nResolve the producer-backed +0x128 cleanup branch and identify any remaining inner child dispatches.\n",
        "hypothesis.md": "# Competing models\n\n- Q64-H1: the resolved cleanup descendants avoid AV11/AV12 skill progress.\n- Q64-H2: a concrete descendant routes an armor ActorValue into skill progress.\n\nUnknown bhkRigidBody child targets do not discriminate the models.\n",
        "protocol.md": "# Protocol\n\nUse the existing GOG AE 1.6.1179.0 project read-only. Link a member to a vtable only through its exact producer and owner. Resolve slot +8 through the installed table, and preserve further dynamic children as unknown.\n",
        "results.md": "# Results\n\nFUN_1407373e0 passes DAT_1430febf8 to FUN_1408e7230, which stores a constructed bhkRigidBody at PlayerCamera+0x128. The installed table slot +8 is FUN_140d28f40, which dispatches the slot-0 destructor FUN_1402f2d10 -> FUN_140e92c60. The destructor releases a body+0x28 child array through unresolved slot+8 targets [EV-0353].\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- A concrete body child table and slot+8 path reaching AV11/AV12 supports Q64-H2 for that path.\n- Resolved children avoiding that sink narrow Q64-H1 only for those concrete branches.\n- Unresolved body child tables remain inconclusive.\n",
        "implications.md": "# Implications\n\nThe PlayerCamera+0x128 owner member is no longer untyped: its producer installs bhkRigidBody. That destructor's body+0x28 child array is still dynamic.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Identify producers that populate bhkRigidBody+0x28 and count +0x38.\n2. Recover exact child vtables and slot +8 functions.\n3. Trace their direct descendants and test for AV11/AV12.\n",
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
        "evidence_id": "EV-0353",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY,
        "captures": rows,
        "registered_local_hashes": hashes,
    }, indent=2))
    hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0353" for item in evidence["items"]):
        raise SystemExit("EV-0353 already registered")
    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0353",
        "kind": "native",
        "source": "Read-only GOG Ghidra queries of the PlayerCamera +0x128 producer, bhkRigidBody function table and deleting destructor, and body initializer.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0353-note.md",
        "sha256": digest(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Concrete owner call, PlayerCamera+0x128 allocation/table write, exact bhkRigidBody table slots 0 and +8, slot+8 wrapper, direct destructor and body+0x28 child cleanup. Child-array member producers and target tables remain unresolved.",
        "result": "FUN_1407373e0 calls FUN_1408e7230(DAT_1430febf8), which stores a constructed bhkRigidBody at PlayerCamera+0x128. Its slot+8 finalizer resolves through FUN_140d28f40 to FUN_1402f2d10 -> FUN_140e92c60. The latter releases a child pointer array through unresolved slot+8 calls. No direct AV11/AV12 sink is established in the resolved path; Q64-H1/H2 remain proposed.",
        "related_evidence": ["EV-0325", "EV-0327", "EV-0352"],
        "local_hashes": hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims = ROOT / "research/CLAIMS.md"
    text = claims.read_text(encoding="utf-8")
    if "| CL-L191 |" in text:
        raise SystemExit("CL-L191 already exists")
    put(claims, text.rstrip() + "\n| CL-L191 | On the captured GOG PlayerCamera cell-transition path, FUN_1408e7230 stores a bhkRigidBody at PlayerCamera+0x128; its slot +8 resolves through FUN_140d28f40 to FUN_1402f2d10 and FUN_140e92c60, whose body+0x28 child array still dispatches unknown slot +8 targets. | supported for bounded producer and destructor path | [EV-0353], [EV-0352], [EV-0327] | Child object classes and AV11/AV12 reachability remain unresolved. |")

    mechanisms = ROOT / "research/MECHANISMS.md"
    put(mechanisms, mechanisms.read_text(encoding="utf-8").rstrip() + "\n\n## M-0073 — PlayerCamera cell-transition bhkRigidBody cleanup (Q-0064)\n\nFUN_1407373e0 passes DAT_1430febf8 to FUN_1408e7230, which creates a bhkRigidBody and stores it at PlayerCamera+0x128. That member's slot+8 path resolves through the exact bhkRigidBody table to FUN_140d28f40 -> FUN_1402f2d10 -> FUN_140e92c60. The body destructor releases a body+0x28 pointer array through dynamic slot+8 calls. No direct AV11/AV12 sink is established, but the child targets remain unresolved [EV-0353]. Claim CL-L191 -> M-0073.\n")

    graph = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph, graph.read_text(encoding="utf-8").rstrip() + "\n\nEV-0353 resolves PlayerCamera+0x128 to a constructed bhkRigidBody and its slot+8 deleting-destructor chain. The body destructor exposes a child-array slot+8 frontier, so this result narrows one owned-object class without resolving Q64-H1/H2 or adding an AV11/AV12 edge. Claim CL-L191 -> M-0073.\n")

    index = ROOT / "experiments/README.md"
    put(index, index.read_text(encoding="utf-8").rstrip() + "\n\nEXP-0091 / EV-0353 resolves PlayerCamera+0x128 to bhkRigidBody and its slot+8 destructor; the body's child array remains unresolved.\n")

    roadmap = ROOT / "research/ROADMAP.md"
    put(roadmap, roadmap.read_text(encoding="utf-8").rstrip() + "\n\nEV-0353 resolves the PlayerCamera+0x128 bhkRigidBody destructor path to FUN_140e92c60; its body+0x28 child array still dispatches unknown slot+8 targets. Next recover the child-array producers and tables. Claim CL-L191 -> M-0073.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(item for item in frontier["items"] if item.get("id") == "Q-0064")
    q65 = next(item for item in frontier["items"] if item.get("id") == "Q-0065")
    for item in (q64, q65):
        if "EV-0353" not in item.setdefault("evidence", []):
            item["evidence"].append("EV-0353")
        if "CL-L191" not in item.setdefault("linked_claims", []):
            item["linked_claims"].append("CL-L191")
        for hypothesis in item.get("hypotheses", []):
            if "EV-0353" not in hypothesis.setdefault("evidence", []):
                hypothesis["evidence"].append("EV-0353")
    q64["next_action"] = "Trace the bhkRigidBody destructor's body+0x28 child-array producers from the exact constructor and initialization path. Resolve each concrete child vtable and slot+8 descendant, screening for AV11/AV12. Do not generalize this resolved PlayerCamera+0x128 branch to the five other destructor dispatches."
    q65["next_action"] = "Compare producer-backed vtables for +0x730, +0x8F8, +0x9D0, +0x9A0/+0x9A8, ThirdPersonState+0xA0, and PlayerCamera-owned cleanup objects. EV-0353 resolves PlayerCamera+0x128 to bhkRigidBody; its body+0x28 child targets remain unresolved."
    q65.setdefault("attempts", []).append({
        "action_key": "q65-playercamera-rigidbody-child-array",
        "outcome": "EV-0353 identifies bhkRigidBody at PlayerCamera+0x128 and resolves its slot+8 destructor to FUN_140e92c60; the body+0x28 child table remains data-dependent.",
        "evidence": ["EV-0353"],
        "new_discriminant": "Concrete producer-backed child vtables determine whether this cleanup family shares a scene-resource finalizer or remains a separate physics path.",
        "next_action": q65["next_action"],
    })
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    checkpoint = ROOT / "experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"
    source = checkpoint.read_text(encoding="utf-8")
    needle = "- Q-0064 / EV-0352 maps the PlayerCamera global table and slot-0 destructor; five owned-object calls remain dynamic and the broad +0x28 scan finds no object-specific non-null writer. The next branch is +0x128.\n"
    addition = "- Q-0064 / EV-0353 resolves PlayerCamera+0x128 to bhkRigidBody and its slot+8 destructor to FUN_140e92c60; that body's +0x28 child array still dispatches unresolved slot+8 targets. The next branch traces those child producers.\n"
    if needle not in source:
        raise SystemExit("checkpoint EV-0352 line missing")
    put(checkpoint, source.replace(needle, needle + addition))

    print("registered EV-0353 / CL-L191 / M-0073; Q-0064 continues on bhkRigidBody child-array producers")
if __name__ == "__main__":
    main()
