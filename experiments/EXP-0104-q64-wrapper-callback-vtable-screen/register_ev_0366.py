#!/usr/bin/env python3
"""Register EV-0366's fixed/malleable wrapper and callback-offset screen."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = Path(__file__).resolve().parent
BIN = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = {
    "20261018T090112Z": ("requested_rva", "0xB48720"),
    "20261018T091218Z": ("requested_address_rva", "0xEF45CC"),
    "20261018T091331Z": ("requested_pointer_table_rva", "0x19EB9C0"),
    "20261018T091617Z": ("requested_pointer_table_rva", "0x19F50A8"),
    "20261018T091802Z": ("requested_rva", "0xEBEAA0"),
    "20261018T091929Z": ("requested_rva", "0xEBE4A0"),
    "20261018T092100Z": ("requested_rva", "0xECE1A0"),
    "20261018T092210Z": ("requested_rva", "0xECC300"),
    "20261018T092321Z": ("requested_rva", "0xEF47C0"),
    "20261018T092535Z": ("requested_rva", "0xEBE4F0"),
    "20261018T092642Z": ("requested_rva", "0xA89DA0"),
    "20261018T092746Z": ("requested_rva", "0xA89E60"),
    "20261018T092923Z": ("requested_search_displacement", "0x40"),
    "20261018T093218Z": ("requested_search_displacement", "0x48"),
    "20261018T093457Z": ("requested_rva", "0xB91BB0"),
    "20261018T093621Z": ("requested_rva", "0xB48A20"),
    "20261018T093733Z": ("requested_rva", "0xB48CB0"),
    "20261018T093901Z": ("requested_rva", "0xB62230"),
    "20261018T094041Z": ("requested_pointer_table_rva", "0x1973D58"),
}

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")

def main() -> None:
    captures = []
    for stamp, (field, expected) in CAPTURES.items():
        meta_path = GH / f"gog-query-{stamp}.meta.json"
        if not meta_path.is_file():
            raise SystemExit(f"missing metadata: {meta_path}")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        stdout_path = ROOT / meta["artifacts"]["stdout"]
        checks = meta.get("checks", {})
        valid = (
            meta.get("analysis_distribution") == "GOG"
            and meta.get("analysis_binary_product_version") == "1.6.1179"
            and meta.get("analysis_binary_sha256") == BIN
            and meta.get(field) == expected
            and meta.get("exit_code") == 0
            and meta.get("ok") is True
            and meta.get("read_only") is True
            and meta.get("auto_analysis_disabled") is True
            and meta.get("import_attempted") is False
            and meta.get("overwrite_attempted") is False
            and meta.get("program_executable_path_matches_gog_binary") is True
            and checks.get("program_identity_matches_gog_binary") is True
            and checks.get("script_no_error") is True
            and all(checks.values())
            and stdout_path.is_file()
            and digest(stdout_path) == meta.get("stdout_sha256")
        )
        if not valid:
            raise SystemExit(f"capture validation failed: {stamp}")
        raw = stdout_path.read_text(encoding="utf-8", errors="replace")
        captures.append((stamp, meta, meta_path, stdout_path, raw))

    by_stamp = {stamp: (meta, meta_path, stdout_path, raw) for stamp, meta, meta_path, stdout_path, raw in captures}
    required = {
        "20261018T091218Z": ["ADDRESS_CONTEXT_BEFORE=140ef45bb LEA LEA RAX,[0x1419eb9c0]", "ADDRESS_CONTEXT_INSTRUCTION=140ef465b LEA LEA RAX,[0x1419f50a8]", "140ef45cc -> 140ecdfc0", "140ef466c -> 140ecdfc0"],
        "20261018T091331Z": ["POINTER_TABLE_ENTRY=index:37", "value:0x140ECD680", "POINTER_TABLE_ENTRY=index:38", "value:0x140ECE1A0", "POINTER_TABLE_ENTRY=index:43", "value:0x140ECC300", "POINTER_TABLE_ENTRY=index:49", "value:0x140EBEAA0", "POINTER_TABLE_SCAN_COMPLETE=true"],
        "20261018T091617Z": ["POINTER_TABLE_ENTRY=index:37", "value:0x140ECD680", "POINTER_TABLE_ENTRY=index:38", "value:0x140ECE1A0", "POINTER_TABLE_ENTRY=index:43", "value:0x140EF47C0", "POINTER_TABLE_ENTRY=index:49", "value:0x140EBEAA0", "POINTER_TABLE_SCAN_COMPLETE=true"],
        "20261018T091802Z": ["(**(code **)(*param_1 + 0x158))(param_1,1);"],
        "20261018T091929Z": ["(**(code **)(*param_1 + 0x130))(param_1,0);", "param_1[2] = param_2;", "(**(code **)(*param_1 + 0x130))(param_1,1);"],
        "20261018T092100Z": ["*(longlong *)(*(longlong *)(param_1 + 0x10) + 0x58) = lVar1;", "FUN_140ebe4f0();"],
        "20261018T092210Z": ["*(undefined8 *)(param_1 + 0x18) = 0;"],
        "20261018T092321Z": ["*(undefined8 *)(param_1 + 0x18) = 0;"],
        "20261018T092535Z": ["FUN_140a89e60();", "FUN_140a89da0();"],
        "20261018T092642Z": ["TlsGetValue", "EnterCriticalSection", "TlsSetValue"],
        "20261018T092746Z": ["(**(code **)*param_1)(param_1,1);", "*(short *)((longlong)param_1 + 10) = sVar3 + -1;"],
        "20261018T092923Z": ["OFFSET_ACCESS_COUNT=28807", "OFFSET_WRITER_CANDIDATE_FUNCTION_COUNT=3136", "OFFSET_SCAN_COMPLETE=true", "OFFSET_WRITER_ANALYSIS_COMPLETE=true"],
        "20261018T093218Z": ["OFFSET_ACCESS_COUNT=14360", "OFFSET_WRITER_CANDIDATE_FUNCTION_COUNT=2301", "OFFSET_SCAN_COMPLETE=true", "OFFSET_WRITER_ANALYSIS_COMPLETE=true"],
        "20261018T093457Z": ["MOVAPS xmmword ptr [RAX + 0x40], XMM1", "*(longlong *)(lVar9 + 0x48) = lVar8;"],
        "20261018T093621Z": ["MOV qword ptr [RCX + 0x40], RDI", "MOV dword ptr [RCX + 0x48], 0x80000000", "hkpConstraintInstance::vftable"],
        "20261018T093733Z": ["MOVAPS xmmword ptr [R14 + 0x40], XMM0", "FUN_140b60230"],
        "20261018T093901Z": ["hkpSimpleConstraintContactMgr::vftable", "FUN_140b48a20(param_1 + 0xf,1);"],
        "20261018T094041Z": ["POINTER_TABLE_BASE_RVA=0x1973D58", "POINTER_TABLE_ENTRY=index:0", "POINTER_TABLE_ENTRY=index:49", "POINTER_TABLE_SCAN_COMPLETE=true"],
    }
    for stamp, needles in required.items():
        raw = by_stamp[stamp][3]
        missing = [needle for needle in needles if needle not in raw]
        if missing:
            raise SystemExit(f"capture markers missing for {stamp}: {missing}")

    ep = ROOT / "research/EVIDENCE.json"
    ev = json.loads(ep.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0366" for item in ev["items"]):
        raise SystemExit("EV-0366 already exists")
    claim_path = ROOT / "research/CLAIMS.md"
    claims = claim_path.read_text(encoding="utf-8")
    if "| CL-L206 |" in claims:
        raise SystemExit("CL-L206 already exists")

    note = TX / "EV-0366-note.md"
    write(note, f"""# EV-0366 — ProcessTrapHit wrapper callback setup and exact-offset screen

## Build and method

The evidence uses the existing GOG AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BIN}, through the strict dispatcher in read-only/no-analysis mode. Nineteen targeted captures are identity checked and their raw stdout hashes match their metadata. The full +0x40 and +0x48 displacement scans completed, but their operand and writer candidate totals are broad and offset alone does not identify a receiver.

## Competing models

- H1: the fixed/malleable constraint wrapper setup path or its exact hkpConstraintInstance constructors populate the callback pointer/count after constructor initialization.
- H2: the traced setup path links the hkpConstraintInstance to wrapper state and adjusts references, while callback-array population requires a distinct writer or later event.

Exact receiver, vtable target and write semantics discriminate these models. Constructor initialization by itself does not prove later callback emptiness.

## Direct observations

- In FUN_140ef43b0, the fixed ProcessTrapHit branch selects table 0x1419eb9c0, while the malleable branch selects 0x1419f50a8; both branch to FUN_140ecdfc0 [captures 20261018T091218Z, 20261018T091331Z, 20261018T091617Z; factory context EV-0365].
- Both wrapper tables use the same +0x128 target FUN_140ecd680, +0x130 target FUN_140ece1a0 and +0x188 target FUN_140ebeaa0. Their +0x158 targets differ: fixed FUN_140ecc300 and malleable FUN_140ef47c0 [captures 20261018T091331Z, 20261018T091617Z].
- The +0x188 target forwards mode 1 to wrapper slot +0x158. Both concrete targets release a separate wrapper +0x18 object and clear that field; neither body writes the hkp callback fields +0x40/+0x48 [captures 20261018T091802Z, 20261018T092210Z, 20261018T092321Z].
- The +0x128 target swaps wrapper +0x10 through FUN_140ebe4a0. That helper notifies wrapper slot +0x130 with mode 0, replaces the pointer, then notifies with mode 1. The +0x130 target writes the child at wrapper +0x10's +0x58 back-pointer to either wrapper or null, then calls FUN_140ebe4f0 [captures 20261018T091929Z, 20261018T092100Z].
- FUN_140ebe4f0 selects generic reference-count release/acquire helpers FUN_140a89e60/FUN_140a89da0. The latter increment the short count at object +0x0a; the former decrements and may call the object's virtual finalizer on a terminal release. These helper bodies do not write the hkp callback array or contain an AV11/AV12 skill call [captures 20261018T092535Z, 20261018T092642Z, 20261018T092746Z]. The finalizer target remains type dependent.
- The exact hkpConstraintInstance constructor FUN_140b48720 initializes callback pointer +0x40 to null and +0x48 to 0x80000000 with low count bits zero [EV-0365]. Another constructor, FUN_140b48a20, writes the same empty values and uses the named hkpConstraintInstance vtable at 0x141973d58. Its callers include FUN_140b5d450, which replaces the vtable with hkpConstraintChainInstance, and FUN_140b62230, which constructs hkpSimpleConstraintContactMgr and embeds the instance at +0x78 [captures 20261018T093621Z, 20261018T093901Z].
- The +0x40 scan completed with 28,807 memory operand matches, 3,136 direct writer-candidate functions and 206 computed-writer candidates; printed access details are capped at 2,048. The +0x48 scan completed with 14,360 matches, 2,301 direct writer-candidate functions and 249 computed-writer candidates; it has the same access-output cap [captures 20261018T092923Z, 20261018T093218Z]. The named ProcessTrapHit constructor is a candidate in both scans. FUN_140b91bb0 appears as a +0x40 candidate, but its machine code copies a 16-byte vector at [RAX+0x40]; that covers bytes +0x40 through +0x4f and explains why the decompiler displays two qword assignments at +0x40 and +0x48 even though the machine code has no +0x48 displacement [EV-0365; capture 20261018T093457Z].
- A nearby +0x40-only candidate FUN_140b48cb0 is called as a member visitor from FUN_140b60230. Its +0x40 operations are vector data transfers; no receiver identity connects that serializer-like path to the ProcessTrapHit hkpConstraintInstance callback array [capture 20261018T093733Z].
- The exact hkpConstraintInstance vtable begins at 0x141973d58; a bounded 50-entry pointer-table read completed. The table provides targets for a subsequent method-by-method callback registration screen; this capture alone does not classify every slot [capture 20261018T094041Z].

## Result and uncertainty

H2 is supported for the traced wrapper setup methods: they attach the exact instance, update its +0x58 wrapper backlink, adjust references and release separate wrapper data. They do not directly populate callback fields +0x40/+0x48. Both mapped constructor families start those fields empty. The broad displacement scans expose thousands of unrelated offsets and do not prove that no callback writer exists elsewhere. The terminal refcount finalizer and later simulation/world events remain open; no AV11/AV12 conclusion and no zero-armor-XP or live Steam result follows.

## Exact next action

Use the vtable at 0x141973d58 and the shared exact-offset writer candidates to identify producer-backed hkpConstraintInstance callback registration methods. Verify each candidate's receiver and callers, then follow actual callback entries through add/remove slots +0x8/+0x10 and finalizers to Actor::UseSkill AV11/AV12. Keep the exact Steam positive-damage, effective-protection and raw-AVSK discriminator separate.
""")

    docs = {
        "README.md": "# EXP-0104 — wrapper callback and callback-offset screen\n\nResolve the exact ProcessTrapHit fixed/malleable setup slots, discriminate same-offset callback writer candidates by receiver and machine code, and preserve later finalizer uncertainty.\n",
        "hypothesis.md": "# Competing models\n\n- H1: wrapper setup or its exact hkpConstraintInstance constructors populate callback pointer/count after initialization.\n- H2: the traced path links wrapper state and adjusts references; callback population requires a distinct writer or later event.\n\nReceiver identity and exact machine-level write semantics discriminate these models.\n",
        "protocol.md": "# Protocol\n\nUse identity-checked read-only GOG queries. Resolve the actual fixed/malleable vtables at FUN_140ecdfc0, trace slots +0x128/+0x130/+0x158/+0x188 and called helpers, and compare exact hkpConstraintInstance callback fields against full displacement scans. Interpret vector stores by machine operands and retain caps, receiver ambiguity, finalizers and Steam runtime limits.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Resolve each wrapper vtable slot to an exact function.\n2. Follow pointer setter, observer, reference operations and finalizer without conflating wrapper data with the hkp instance.\n3. Distinguish direct +0x48 writes from vector copies beginning at +0x40.\n4. Confirm whether exact hkp constructors initialize or populate callback entries.\n5. Preserve unknown global writers and later finalizer paths.\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- A concrete setup method writing the exact instance callback pointer/count supports H1.\n- Wrapper backlink/refcount updates with empty constructor fields support H2 for that mapped path only.\n- Broad displacement matches without receiver identity remain unresolved.\n",
        "results.md": "# Results\n\nFixed and malleable wrappers share +0x128/+0x130/+0x188 targets; their +0x158 targets both release wrapper +0x18 data. The setup path stores a wrapper backlink at hkpConstraintInstance +0x58 and adjusts references, without direct +0x40/+0x48 callback writes. Two constructor families initialize those callback fields empty. Broad scans are capped and remain receiver ambiguous [EV-0366].\n",
        "implications.md": "# Implications\n\nThe ProcessTrapHit setup route is narrowed, but later callback producers and terminal finalizers remain unresolved. Next inspect the exact hkpConstraintInstance vtable and type-backed writer callers; do not infer callback emptiness from offsets alone.\n",
    }
    for filename, content in docs.items():
        write(EXP / filename, content)

    manifest = TX / "EV-0366-capture-manifest.json"
    local_hashes = {}
    capture_summaries = []
    for stamp, meta, meta_path, stdout_path, _raw in captures:
        local_hashes[meta_path.relative_to(ROOT).as_posix()] = digest(meta_path)
        for artifact in meta.get("artifacts", {}).values():
            path = ROOT / artifact
            if path.is_file():
                local_hashes[path.relative_to(ROOT).as_posix()] = digest(path)
        capture_summaries.append({
            "stamp": stamp,
            "query_mode": meta.get("query_mode"),
            "requested_rva": meta.get("requested_rva"),
            "requested_address_rva": meta.get("requested_address_rva"),
            "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
            "requested_search_displacement": meta.get("requested_search_displacement"),
            "checks": meta.get("checks"),
            "stdout_sha256": meta.get("stdout_sha256"),
            "read_only": meta.get("read_only"),
            "auto_analysis_disabled": meta.get("auto_analysis_disabled"),
        })
    local_hashes[note.relative_to(ROOT).as_posix()] = digest(note)
    local_hashes[Path(__file__).relative_to(ROOT).as_posix()] = digest(Path(__file__))
    for filename in docs:
        path = EXP / filename
        local_hashes[path.relative_to(ROOT).as_posix()] = digest(path)
    manifest_content = {
        "evidence_id": "EV-0366",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BIN,
        "captures": capture_summaries,
        "registered_local_hashes": local_hashes,
    }
    write(manifest, json.dumps(manifest_content, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)

    ev["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0366",
        "kind": "native",
        "source": "Identity-checked read-only GOG Ghidra wrapper vtable, callback-offset and hkpConstraintInstance constructor screen.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0366-note.md",
        "sha256": digest(note),
        "runtime": f"GOG AE 1.6.1179.0 static outputs; analysis binary SHA-256 {BIN}; no Steam runtime observation.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
        "coverage": "Nineteen identity-checked captures: fixed/malleable wrapper tables and setup callees, reference helpers, full +0x40/+0x48 displacement scans, exact vector-copy discrepancy, second hkpConstraintInstance constructor family, and a bounded hkpConstraintInstance vtable table.",
        "result": "The mapped ProcessTrapHit wrapper path attaches the exact hkpConstraintInstance, maintains a +0x58 wrapper backlink and reference counts, and releases separate wrapper data; it does not directly populate callback fields +0x40/+0x48. Two constructors initialize callback pointer/count empty. Broad offset scans include thousands of receiver-ambiguous candidates; FUN_140b91bb0's decompiler +0x48 assignment is part of a machine-level 16-byte copy beginning at +0x40.",
        "related_evidence": ["EV-0355", "EV-0358", "EV-0360", "EV-0364", "EV-0365"],
        "local_hashes": local_hashes,
    })
    write(ep, json.dumps(ev, indent=2, ensure_ascii=False))

    claims += "\n| CL-L206 | In GOG AE 1.6.1179.0, the mapped ProcessTrapHit fixed/malleable wrapper slots +0x128/+0x130/+0x188 and their traced helpers attach the exact hkpConstraintInstance, update its +0x58 wrapper back-pointer, adjust references and release separate wrapper data; these methods do not directly write callback fields +0x40/+0x48. Both mapped hkpConstraintInstance constructor families initialize the callback pointer/count empty. | supported for the traced setup methods and constructors | [EV-0366], [EV-0365], [EV-0364] | Broad displacement candidates, later world events and terminal finalizers remain unresolved. |\n"
    write(claim_path, claims)

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8")
    mechanisms += """

## M-0085 — ProcessTrapHit constraint wrapper callback setup boundary (Q-0064)

The fixed and malleable wrappers share +0x128 FUN_140ecd680, +0x130 FUN_140ece1a0 and +0x188 FUN_140ebeaa0. The setter updates wrapper +0x10 and the observer sets the hkpConstraintInstance +0x58 backlink while generic reference-count helpers acquire/release the object. Slot +0x188 forwards mode 1 to class-specific +0x158 cleanup that releases separate wrapper +0x18 data. Neither traced branch writes callback fields +0x40/+0x48. FUN_140b48720 and FUN_140b48a20 initialize callback pointer/count empty; the latter also seeds hkpConstraintChainInstance and hkpSimpleConstraintContactMgr constructions. The two whole-program offset scans remain receiver ambiguous and do not establish global callback emptiness or no AV11/AV12 path [EV-0366]. Claim CL-L206 -> M-0085.
"""
    write(mechanisms_path, mechanisms)

    contradictions_path = ROOT / "research/CONTRADICTIONS.md"
    contradictions = contradictions_path.read_text(encoding="utf-8")
    marker = "## C-OBJ2-Q64-CALLBACK-OFFSET-ALIAS — same-offset data fields versus callback array"
    start = contradictions.find(marker)
    if start < 0:
        raise SystemExit("missing callback offset contradiction")
    tail = contradictions[start:]
    if "[EV-0366]" not in tail:
        contradictions += "\nEV-0366 confirms the wrapper setup path itself does not directly write the exact callback fields. The apparent FUN_140b91bb0 +0x48 decompilation store comes from one 16-byte machine copy at +0x40, which covers payload bytes +0x40 through +0x4f; receiver ambiguity and later writers remain open [EV-0366].\n"
    write(contradictions_path, contradictions)

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    graph = graph_path.read_text(encoding="utf-8")
    graph += """

EV-0366 narrows the ProcessTrapHit hkpConstraintInstance setup route: fixed/malleable wrappers share pointer-setter and observer methods, store an instance +0x58 backlink, and update reference counts without directly writing callback fields +0x40/+0x48. Both mapped constructors start the callback pointer/count empty. The displacement scans are broad and receiver ambiguous; the decompiled +0x48 store in FUN_140b91bb0 comes from a 16-byte vector copy beginning at +0x40. No edge to Actor::UseSkill AV11/AV12 is established; inspect exact vtable methods next [CL-L206], [M-0085].
"""
    write(graph_path, graph)

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    question = next(item for item in frontier["items"] if item.get("id") == "Q-0064")
    for key in ("evidence",):
        if "EV-0366" not in question.setdefault(key, []):
            question[key].append("EV-0366")
    for hypothesis in question.get("hypotheses", []):
        if "EV-0366" not in hypothesis.setdefault("evidence", []):
            hypothesis["evidence"].append("EV-0366")
    if "CL-L206" not in question.setdefault("linked_claims", []):
        question["linked_claims"].append("CL-L206")
    question["next_action"] = "Use the hkpConstraintInstance vtable at 0x141973d58 and the shared exact-offset writer candidates to identify callback registration methods. Verify receiver/caller provenance, then follow actual callback entries through add/remove slots +0x8/+0x10 and finalizers to Actor::UseSkill AV11/AV12; preserve the exact Steam positive-damage/effective-protection/raw-AVSK discriminator."
    question.setdefault("methods", []).append("EV-0366 resolves the wrapper setup and two empty constructor families, but full +0x40/+0x48 scans are receiver-ambiguous. Inspect the hkpConstraintInstance vtable at 0x141973d58 and exact overlapping writer candidates before following any callback entry.")
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    state += "\n- Q-0064 / EV-0366 maps fixed/malleable ProcessTrapHit wrapper slots and two empty callback constructors. The setup stores an hkpConstraintInstance +0x58 backlink and adjusts references but does not directly populate +0x40/+0x48; broad scans are receiver ambiguous. Next inspect vtable 0x141973d58 and callback writer callers.\n"
    write(state_path, state)

    roadmap_path = ROOT / "ROADMAP.md"
    roadmap = roadmap_path.read_text(encoding="utf-8")
    roadmap += "\nEV-0366 resolves the ProcessTrapHit fixed/malleable setup slots through pointer/backlink/refcount behavior and confirms two hkpConstraintInstance constructor families start callback arrays empty. Whole-program +0x40/+0x48 scans are broad; FUN_140b91bb0's apparent +0x48 field is part of one 16-byte copy from +0x40. Inspect the exact hkpConstraintInstance vtable 0x141973d58 and overlapping writer callers next; later callbacks/finalizers and AV11/AV12 remain open. Claim CL-L206 -> M-0085.\n"
    write(roadmap_path, roadmap)

    exp_index = ROOT / "experiments/README.md"
    index = exp_index.read_text(encoding="utf-8")
    index += "\nEXP-0104 / EV-0366 maps ProcessTrapHit constraint wrapper setup, two empty callback constructors and the bounded hkpConstraintInstance vtable. Callback writer candidates and terminal finalizers remain unresolved.\n"
    write(exp_index, index)

    print("Registered EV-0366 and CL-L206/M-0085; Q-0064 remains active on vtable-backed callback writers.")

if __name__ == "__main__":
    main()
