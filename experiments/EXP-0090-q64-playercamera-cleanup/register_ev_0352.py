#!/usr/bin/env python3
"""Register the PlayerCamera cleanup table and its unresolved child dispatches."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0090-q64-playercamera-cleanup"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
STAMPS = [
    "20261018T055330Z", "20261018T055432Z", "20261018T055524Z",
    "20261018T055626Z", "20261018T055735Z", "20261018T055848Z",
    "20261018T060042Z", "20261018T060141Z",
]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")

def capture(stamp: str, markers: list[str]) -> tuple[dict, Path, Path]:
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
        "20261018T055330Z": [
            "TARGET_RVA=0x8E3F50", "MOV qword ptr [0x1430febf8], RAX",
            "LEA RAX, [0x1418f0628]", "PlayerCamera::vftable",
            "XREF_CALL_EDGE=14072f791 -> 1408e3f50 caller=FUN_14072ed70",
        ],
        "20261018T055432Z": [
            "POINTER_TABLE_BASE_RVA=0x18F0628",
            "POINTER_TABLE_ENTRY=index:0 address:1418f0628 value:0x1408E8B50",
            "POINTER_TABLE_SCAN_COMPLETE=true",
        ],
        "20261018T055524Z": [
            "DECOMPILATION_BEGIN=FUN_1408e8b50", "FUN_1408e4070();",
            "thunk_FUN_14011bbb0(param_1,0x168);",
            "CALLEE_DECOMPILATION_BEGIN=FUN_1408e4070", "DAT_1430febf8 = 0;",
        ],
        "20261018T055626Z": [
            "DECOMPILATION_BEGIN=FUN_1408e4070", "INDIRECT_CALL_SITE_COUNT=5",
            "INDIRECT_CALL_SITE=1408e40a9 CALL qword ptr [RAX + 0x10]",
            "INDIRECT_CALL_SITE=1408e40df CALL qword ptr [RAX]",
            "INDIRECT_CALL_SITE=1408e4131 CALL qword ptr [RAX + 0x8]",
            "INDIRECT_CALL_SITE=1408e417f CALL qword ptr [RAX]",
            "INDIRECT_CALL_SITE=1408e41e6 CALL qword ptr [RAX + 0x8]",
        ],
        "20261018T055735Z": [
            "TARGET_RVA=0x5513A0", "OUTGOING_CALL_COUNT=0",
            "DECOMPILATION_BEGIN=FUN_1405513a0",
            "(**(code **)*puVar3)(puVar3,1);",
        ],
        "20261018T055848Z": [
            "DECOMPILATION_BEGIN=FUN_140550ff0",
            "*param_1 = TESCamera::vftable;", "param_1[5] = 0;",
        ],
        "20261018T060042Z": [
            "ADDRESS_RVA=0x8E87A0",
            "ADDRESS_CONTEXT_INSTRUCTION=1408e87a0 MOV MOV qword ptr [RCX],0x0",
            "ADDRESS_CONTEXT_INSTRUCTION=1408e87a7 MOV MOV RAX,RCX",
        ],
        "20261018T060141Z": [
            "OFFSET_INSTRUCTION_COUNT=5654579", "OFFSET_ACCESS_COUNT=31281",
            "OFFSET_WRITER_CANDIDATE_FUNCTION_COUNT=4380",
            "OFFSET_WRITER_CANDIDATE=FUN_140550ff0 @ 140550ff0 RVA=0x550FF0",
            "OFFSET_WRITER_ANALYSIS_COMPLETE=true",
        ],
    }
    captures = {stamp: capture(stamp, expected[stamp]) for stamp in STAMPS}

    note = TX / "EV-0352-note.md"
    put(note, f"""# EV-0352 — PlayerCamera global cleanup table and unresolved owned-object dispatches

## Build and method

Identity-checked queries used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BINARY}, through the strict dispatcher in read-only/no-analysis mode. Eight capture stamps are preserved in the manifest. No GOG RVA is transferred to installed Steam AE 1.6.1170.0.

## Direct observations

- FUN_1408e3f50 writes its receiver to DAT_1430febf8 and installs PlayerCamera::vftable at receiver+0; its only analyzed caller is FUN_14072ed70 [capture 20261018T055330Z].
- The first 16 entries at vftable address 0x1418F0628 were read. Slot 0 is FUN_1408e8b50 [0x1408e8b50]. The wrapper calls FUN_1408e4070, then conditionally frees 0x168 bytes when its flags argument has bit 0 set [capture 20261018T055432Z; 20261018T055524Z].
- FUN_1408e4070 reinstalls PlayerCamera::vftable while tearing down, releases owned references, calls direct helpers, and clears DAT_1430febf8. Its complete bounded call census has five unresolved indirect call sites: receiver+0x28 vtable slot +0x10; refcounted pointer-array slot 0; receiver+0x128 vtable slot +0x8 (two sites); and an inline pointer-array slot 0 [capture 20261018T055626Z].
- The 13 pointer entries at receiver+0xB8 through +0x118 use generic FUN_1405513a0 release. That callback only decrements a refcount and, at zero, dispatches the object's slot 0; it does not identify the object class [capture 20261018T055735Z].
- The PlayerCamera base helper FUN_140550ff0 installs TESCamera::vftable and initializes its +0x28 member to null. The array constructor callback at 0x1408e87a0 likewise stores null to each 8-byte entry and returns [captures 20261018T055848Z; 20261018T060042Z].
- A whole-program +0x28 displacement scan returned 31,281 operand accesses, 18,434 functions, and 4,380 candidate writer functions. It includes FUN_140550ff0, but this broad offset-only result does not identify a PlayerCamera-specific non-null producer [capture 20261018T060141Z].

## Competing-model assessment

No direct AV11/AV12 skill-progress sink appears in the captured PlayerCamera destructor or generic release callback. Five descendant dispatches remain data-dependent, so this is not a negative for Q64-H1 and does not establish Q64-H2. Q64-H1/H2 remain proposed. No causal edge to OBJ-1 or armor XP is added.

## Exact next discriminant

Screen PlayerCamera offset +0x128 writers using the tested displacement scan; relate any candidate to FUN_1408e3f50/FUN_1408e4070, then resolve the +0x8 destructor only if an object-specific producer is recovered. Keep all dynamic targets unresolved absent that producer.
""")
    capture_rows = {}
    for stamp, (meta, meta_path, stdout) in captures.items():
        capture_rows[stamp] = {
            "query_mode": meta.get("query_mode"),
            "requested_rva": meta.get("requested_rva"),
            "requested_address_rva": meta.get("requested_address_rva"),
            "requested_search_displacement": meta.get("requested_search_displacement"),
            "checks": meta.get("checks"),
            "stdout_sha256": meta.get("stdout_sha256"),
            "stderr_sha256": meta.get("stderr_sha256"),
            "query_script_sha256": meta.get("query_script_sha256"),
        }
    manifest = TX / "EV-0352-capture-manifest.json"
    put(manifest, json.dumps({
        "evidence_id": "EV-0352",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY,
        "captures": capture_rows,
    }, indent=2))
    exp_docs = {
        "README.md": "# EXP-0090 — PlayerCamera cleanup table\n\nResolve the factory-installed table for the PlayerCamera cleanup site and bound its owned-object finalizer path.\n",
        "hypothesis.md": "# Competing models\n\n- Q64-H1: resolved teardown descendants do not dispatch AV11/AV12 skill progress.\n- Q64-H2: at least one concrete PlayerCamera-owned descendant dispatches an armor ActorValue into skill progress.\n\nA generic refcount callback or untyped virtual site does not discriminate these models.\n",
        "protocol.md": "# Protocol\n\nUse the exact installed GOG AE 1.6.1179.0 project through the strict dispatcher in read-only/no-analysis mode. Tie virtual slots to factory-installed tables and producer-backed objects. Preserve dynamic unknowns; do not infer runtime targets from a slot number.\n",
        "results.md": "# Results\n\nFUN_1408e3f50 stores PlayerCamera in DAT_1430febf8 and installs the table at RVA 0x18F0628. Slot 0 is FUN_1408e8b50, which calls FUN_1408e4070 before optional 0x168-byte deallocation [EV-0352]. The destructor has five unresolved indirect sites; its 13-entry array callback is generic refcount release. The TESCamera +0x28 base member and array entries start null. No object-specific non-null producer was recovered.\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- A concrete +0x128 writer and exact slot +8 target reaching AV11/AV12 supports Q64-H2 for that branch.\n- A concrete target avoiding the skill sink narrows Q64-H1 to that branch only.\n- Offset-only candidates or data-selected virtual targets are inconclusive.\n",
        "implications.md": "# Implications\n\nThe global cleanup owner and its slot-0 deleting destructor are mapped. This narrows ownership context, while five descendant virtual dispatches remain unresolved. No causal edge to either bounty objective is supported.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Recover an object-specific producer for PlayerCamera +0x128.\n2. Read the exact installed table of that producer.\n3. Resolve its final slot +8 target and descendants.\n4. Screen only concrete paths for AV11/AV12 skill credit.\n",
    }
    for name, content in exp_docs.items():
        put(EXP / name, content)

    hashes = {}
    for stamp, (meta, meta_path, stdout) in captures.items():
        for path in [meta_path, stdout] + [ROOT / value for value in meta["artifacts"].values()]:
            if path.is_file():
                hashes[path.relative_to(ROOT).as_posix()] = digest(path)
    for path in [note, manifest] + list(EXP.iterdir()) + [Path(__file__)]:
        if path.is_file():
            hashes[path.relative_to(ROOT).as_posix()] = digest(path)
    put(manifest, json.dumps({
        "evidence_id": "EV-0352",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY,
        "captures": capture_rows,
        "registered_local_hashes": hashes,
    }, indent=2))
    hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0352" for item in evidence["items"]):
        raise SystemExit("EV-0352 already registered")
    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0352",
        "kind": "native",
        "source": "Read-only GOG Ghidra queries of the PlayerCamera global factory, installed function table, deleting destructor, TESCamera base initializer, generic release callback, constructor callback address, and bounded +0x28 displacement scan.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0352-note.md",
        "sha256": digest(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Factory and first 16 table entries; exact slot-0 wrapper and PlayerCamera destructor; full direct/indirect call census; generic array callback; TESCamera +0x28 initializer; null array-entry initializer; broad +0x28 operand scan. Descendant object-specific producers and all five dynamic targets remain unresolved.",
        "result": "The factory installs PlayerCamera::vftable into DAT_1430febf8; slot 0 is FUN_1408e8b50, which calls FUN_1408e4070. The destructor clears the global and has five unresolved dynamic calls. Its 13-entry pointer array uses generic refcount release; TESCamera +0x28 and array entries initialize null. No direct AV11/AV12 sink or object-specific non-null writer is established. Q64-H1/H2 remain proposed.",
        "related_evidence": ["EV-0325", "EV-0327", "EV-0344", "EV-0351"],
        "local_hashes": hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims = ROOT / "research/CLAIMS.md"
    claim_text = claims.read_text(encoding="utf-8")
    if "| CL-L190 |" in claim_text:
        raise SystemExit("CL-L190 already exists")
    put(claims, claim_text.rstrip() + "\n| CL-L190 | In GOG AE 1.6.1179.0, the PlayerCamera factory stores its receiver in DAT_1430febf8 and installs a table whose slot 0 calls the PlayerCamera destructor; that destructor has five unresolved owned-object dispatches. | supported for bounded table and cleanup flow | [EV-0352], [EV-0325], [EV-0327] | The five dynamic targets and any AV11/AV12 reachability remain unresolved. |")

    mechanisms = ROOT / "research/MECHANISMS.md"
    put(mechanisms, mechanisms.read_text(encoding="utf-8").rstrip() + "\n\n## M-0072 — PlayerCamera cleanup object dispatch (Q-0064)\n\nFUN_1408e3f50 stores PlayerCamera in DAT_1430febf8 and installs the table whose slot 0 is the deleting-destructor wrapper FUN_1408e8b50. Its destructor FUN_1408e4070 clears the global and releases owned references through five unresolved indirect calls. The 13-entry pointer array uses generic refcount release; the TESCamera +0x28 member and array entries initialize null. No AV11/AV12 edge is established or excluded [EV-0352], [EV-0325], [EV-0327]. Claim CL-L190 -> M-0072.\n")

    graph = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph, graph.read_text(encoding="utf-8").rstrip() + "\n\nEV-0352 links the PlayerCamera global used in the ProcessTrapHit cleanup census to a factory-installed table and deleting-destructor path. The owner is identified, but its five child dispatches remain data-dependent, so no AV11/AV12 edge is added. Claim CL-L190 -> M-0072; Q64-H1/H2 remain unresolved.\n")

    index = ROOT / "experiments/README.md"
    put(index, index.read_text(encoding="utf-8").rstrip() + "\n\nEXP-0090 / EV-0352 maps the PlayerCamera global table and destructor; five owned-object dispatches remain unresolved.\n")

    roadmap = ROOT / "research/ROADMAP.md"
    put(roadmap, roadmap.read_text(encoding="utf-8").rstrip() + "\n\nEV-0352 identifies the PlayerCamera slot-0 deleting destructor and five unresolved child dispatches. Next screen the +0x128 producer path; the broad +0x28 scan does not identify a concrete object writer. Claim CL-L190 -> M-0072.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(item for item in frontier["items"] if item.get("id") == "Q-0064")
    q65 = next(item for item in frontier["items"] if item.get("id") == "Q-0065")
    for item in (q64, q65):
        if "EV-0352" not in item.setdefault("evidence", []):
            item["evidence"].append("EV-0352")
        if "CL-L190" not in item.setdefault("linked_claims", []):
            item["linked_claims"].append("CL-L190")
        for hypothesis in item.get("hypotheses", []):
            if "EV-0352" not in hypothesis.setdefault("evidence", []):
                hypothesis["evidence"].append("EV-0352")
    q64["next_action"] = "Screen PlayerCamera offset +0x128 writers using the tested displacement scan; relate any candidate to FUN_1408e3f50/FUN_1408e4070, then resolve the +0x8 destructor only if an object-specific producer is recovered. Keep all dynamic targets unresolved absent that producer."
    q65["next_action"] = "Compare producer-backed vtables for +0x730, +0x8F8, +0x9D0, +0x9A0/+0x9A8, ThirdPersonState+0xA0, and PlayerCamera-owned cleanup objects. EV-0352 identifies the PlayerCamera owner but not its five child target classes."
    q65.setdefault("attempts", []).append({
        "action_key": "q65-playercamera-owner-table",
        "outcome": "EV-0352 resolves the PlayerCamera owner table and destructor but not its five child classes; Q65-H1/H2 remain unresolved.",
        "evidence": ["EV-0352"],
        "new_discriminant": "Producer-backed owned-object vtables can distinguish shared resource finalizers from independent cleanup families.",
        "next_action": q65["next_action"],
    })
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    checkpoint = ROOT / "experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"
    source = checkpoint.read_text(encoding="utf-8")
    needle = "- Q-0064 / EV-0351 confirms the +0x730 helper returns a data-selected value at cell+0x130+8; class and non-null writer remain unknown. The next branch is the PlayerCamera global cleanup.\n"
    addition = "- Q-0064 / EV-0352 maps the PlayerCamera global table and slot-0 destructor; five owned-object calls remain dynamic and the broad +0x28 scan finds no object-specific non-null writer. The next branch is +0x128.\n"
    if needle not in source:
        raise SystemExit("checkpoint EV-0351 line missing")
    put(checkpoint, source.replace(needle, needle + addition))

    print("registered EV-0352 / CL-L190 / M-0072; Q-0064 continues on the PlayerCamera +0x128 producer")
if __name__ == "__main__":
    main()
