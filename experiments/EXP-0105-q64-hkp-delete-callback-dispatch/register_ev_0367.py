#!/usr/bin/env python3
"""Register EV-0367's exact hkpConstraintInstance deletion callback dispatch."""
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
    "20261018T094041Z": ("requested_pointer_table_rva", "0x1973D58"),
    "20261018T094449Z": ("requested_rva", "0xB36B20"),
    "20261018T094551Z": ("requested_rva", "0xB487E0"),
    "20261018T094655Z": ("requested_rva", "0xB674A0"),
    "20261018T094809Z": ("requested_rva", "0xB49390"),
    "20261018T094906Z": ("requested_rva", "0xB493A0"),
    "20261018T095008Z": ("requested_rva", "0xB493D0"),
    "20261018T095107Z": ("requested_rva", "0xB37A30"),
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
            raise SystemExit(f"missing metadata: {stamp}")
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
        captures.append((stamp, meta, meta_path, stdout_path, stdout_path.read_text(encoding="utf-8", errors="replace")))
    by_stamp = {stamp: (meta, meta_path, stdout_path, raw) for stamp, meta, meta_path, stdout_path, raw in captures}
    required = {
        "20261018T094041Z": ["POINTER_TABLE_BASE_RVA=0x1973D58", "POINTER_TABLE_ENTRY=index:0", "value:0x140B36B20", "POINTER_TABLE_ENTRY=index:4", "value:0x140B493A0", "POINTER_TABLE_SCAN_COMPLETE=true"],
        "20261018T094449Z": ["FUN_140b487e0();", "FUN_140fb9950(param_1,0x70);"],
        "20261018T094551Z": ["FUN_140b674a0();", "FUN_140a8eec0(param_1 + 10);", "uVar4 = param_1[8];", "(uVar1 & 0x3fff) * 8"],
        "20261018T094655Z": ["TtconDeletedCb", "(**(code **)(*plVar2 + 0x18))(plVar2,param_1);", "*(longlong *)(*(longlong *)(param_1 + 0x40) + lVar7 * 8)", "*(ushort *)(param_1 + 0x48)"],
        "20261018T094809Z": ["void FUN_140b49390(void)", "return;"],
        "20261018T094906Z": ["FUN_140b43ab0(*(undefined8 *)(param_2 + 0x10),param_1,1);"],
        "20261018T095008Z": ["void FUN_140b493d0(void)", "return;"],
        "20261018T095107Z": ["undefined8 FUN_140b37a30(void)", "return 0;"],
    }
    for stamp, needles in required.items():
        raw = by_stamp[stamp][3]
        missing = [needle for needle in needles if needle not in raw]
        if missing:
            raise SystemExit(f"capture markers missing for {stamp}: {missing}")

    ep = ROOT / "research/EVIDENCE.json"
    ev = json.loads(ep.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0367" for item in ev["items"]):
        raise SystemExit("EV-0367 already exists")
    claim_path = ROOT / "research/CLAIMS.md"
    claims = claim_path.read_text(encoding="utf-8")
    if "| CL-L207 |" in claims:
        raise SystemExit("CL-L207 already exists")

    note = TX / "EV-0367-note.md"
    write(note, f"""# EV-0367 — hkpConstraintInstance destruction callback dispatch

## Build and method

Eight targeted captures use the existing GOG AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BIN}, through the strict dispatcher in read-only/no-analysis mode. Each capture has a passing program identity check and raw stdout matching its recorded SHA-256. The hkpConstraintInstance primary vtable table at 0x141973d58 comes from EV-0366's bounded 50-entry pointer-table capture.

## Competing models

- H1: at least one non-null hkpConstraintInstance deletion callback can route its virtual slot +0x18 call into Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.
- H2: the callback entries only notify constraint-deletion cleanup and do not award armor skill progress.

The exact callback entry class, producer and slot +0x18 target discriminate these models. A callback invocation without receiver and argument provenance is not enough to choose either model.

## Direct observations

- The exact primary hkpConstraintInstance vtable at 0x141973d58 maps slot 0 to FUN_140b36b20. Its destructor calls FUN_140b487e0 and conditionally releases the 0x70-byte object through the TLS heap interface [captures 20261018T094041Z, 20261018T094449Z].
- FUN_140b487e0 resets the instance vtable, calls FUN_140b674a0, releases referenced members and its +0x50 helper, then examines the encoded callback count flag at +0x4a. If the high flag is clear, it frees the pointer array at +0x40 using a size derived from the low count bits. It finally restores the hkBaseObject vtable [capture 20261018T094551Z].
- FUN_140b674a0 walks the callback array at instance +0x40 using the count at +0x48. For each non-null entry it emits the literal trace tag TtconDeletedCb and invokes entry vtable slot +0x18 with the hkpConstraintInstance pointer. It then compacts null array members and reduces the count. No entry vtable target is resolved by this capture [capture 20261018T094655Z].
- The mapped primary vtable methods at slots +0x18, +0x28 and +0x30 are no-ops or a zero return. Slot +0x20 delegates through FUN_140b43ab0 when instance +0x10 is non-null; the entity-detach and callback notification route is separately mapped in EV-0364. These methods do not register entries in the deletion-callback array [captures 20261018T094809Z, 20261018T094906Z, 20261018T095008Z, 20261018T095107Z].
- The wrapper setup path from EV-0366 does not directly populate +0x40/+0x48. The destructor confirms those fields are a live callback array used on final release, so callback population must come from another exact writer, a later world event or an aliasing producer. No AV11/AV12 sink or Steam runtime result follows from the consumer alone [EV-0366].

## Result and uncertainty

The destruction path does invoke non-null hkpConstraintInstance deletion callbacks through entry slot +0x18 and later frees the array. This identifies a concrete callback consumer missed by the wrapper setup screen. The callback entry class, array producer and virtual target remain unresolved; therefore neither H1 nor H2 is selected. Callback emptiness after later world setup is not established.

## Exact next action

Cross-screen the completed +0x40/+0x48 writer candidate sets with hkpConstraintInstance constructor, vtable and world-attach provenance. Start with hkp-region overlapping candidates FUN_140b57860 and FUN_140b58550, identify exact receivers and callsites, and find the producer that supplies entries consumed by FUN_140b674a0. Then resolve each entry's slot +0x18 target and its argument flow to Actor::UseSkill AV11/AV12.
""")

    docs = {
        "README.md": "# EXP-0105 — hkpConstraintInstance deletion callback dispatch\n\nTrace the exact instance destructor, callback-array consumer and primary vtable to establish the next writer and callback-entry discriminants.\n",
        "hypothesis.md": "# Competing models\n\n- H1: a deletion callback entry reaches Actor::UseSkill or the skill-progress sink with AV11/AV12.\n- H2: deletion callback entries only process constraint cleanup and do not award armor skill progress.\n\nResolve the exact entry class, producer and slot +0x18 target before choosing.\n",
        "protocol.md": "# Protocol\n\nUse identity-checked read-only GOG queries. Trace hkpConstraintInstance primary slot 0 through its destructor helpers; verify callback pointer/count semantics at +0x40/+0x48 and exact entry dispatch. Identify entry classes from receiver-backed writers and callers before following vtable slot +0x18. Preserve unresolved edges and the Steam runtime discriminator.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Verify slot-0 destructor reaches the exact callback-array consumer.\n2. Map callback array pointer/count and deletion slot +0x18 precisely.\n3. Identify producer-backed callback entry types and exact virtual targets.\n4. Follow the callback instance argument toward AV11/AV12 skill progress.\n5. Keep unresolved entry types unresolved.\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- An entry target plus ActorValue flow to Actor::UseSkill supports H1.\n- Exact cleanup-only entry targets without skill progress support H2 for that route.\n- A generic callback slot with unknown class or argument flow is inconclusive.\n",
        "results.md": "# Results\n\nThe hkpConstraintInstance destructor calls FUN_140b674a0, which iterates non-null entries from +0x40/+0x48 and invokes each entry vtable slot +0x18 with the instance before compacting nulls. The finalizer then frees the callback array. Entry class, writer and slot target remain unresolved [EV-0367].\n",
        "implications.md": "# Implications\n\nThe callback array is a real finalization callback route, so the constructor-empty result is not enough to conclude zero armor XP. Find the exact entry producer and target; do not infer behavior from the TtconDeletedCb trace tag alone.\n",
    }
    for filename, content in docs.items():
        write(EXP / filename, content)

    manifest = TX / "EV-0367-capture-manifest.json"
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
            "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
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
        "evidence_id": "EV-0367",
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
        "id": "EV-0367",
        "kind": "native",
        "source": "Identity-checked read-only GOG Ghidra hkpConstraintInstance vtable and finalizer callback consumer trace.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0367-note.md",
        "sha256": digest(note),
        "runtime": f"GOG AE 1.6.1179.0 static outputs; analysis binary SHA-256 {BIN}; no Steam runtime observation.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
        "coverage": "Exact hkpConstraintInstance primary vtable methods, slot-0 finalizer, callback-array pointer/count consumer, slot +0x18 deletion dispatch and array compaction/free.",
        "result": "FUN_140b674a0 iterates non-null entries at hkpConstraintInstance +0x40/+0x48 and calls each entry vtable slot +0x18 with the instance, then compacts null entries. The slot-0 finalizer later frees the array. Entry class, producer, slot target behavior and any AV11/AV12 relation remain unknown.",
        "related_evidence": ["EV-0358", "EV-0364", "EV-0365", "EV-0366"],
        "local_hashes": local_hashes,
    })
    write(ep, json.dumps(ev, indent=2, ensure_ascii=False))

    claims += "\n| CL-L207 | In GOG AE 1.6.1179.0, hkpConstraintInstance finalization calls FUN_140b674a0, which iterates non-null entries in the exact +0x40/+0x48 callback array and invokes each entry vtable slot +0x18 with the instance pointer before compacting null entries; the destructor later frees the array. | supported for the mapped consumer and finalizer bodies | [EV-0367], [EV-0366] | Entry types, producers, slot targets and AV11/AV12 skill flow remain unresolved. |\n"
    write(claim_path, claims)

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8")
    mechanisms += """

## M-0086 — hkpConstraintInstance deletion callback dispatch (Q-0064)

The exact hkpConstraintInstance slot-0 destructor calls FUN_140b487e0, which invokes FUN_140b674a0 before freeing callback storage. FUN_140b674a0 walks non-null entries at instance +0x40 with count +0x48, invokes entry vtable slot +0x18 with the instance pointer, compacts null entries and decrements the count. The destructor frees the pointer array according to its encoded count/capacity bits. The entry class, producer, target and any Actor::UseSkill AV11/AV12 path remain unresolved [EV-0367]. Claim CL-L207 -> M-0086.
"""
    write(mechanisms_path, mechanisms)

    contradictions_path = ROOT / "research/CONTRADICTIONS.md"
    contradictions = contradictions_path.read_text(encoding="utf-8")
    contradictions += """

## C-OBJ2-Q64-INSTANCE-DELETE-CALLBACK — finalization callback and armor skill progress

- **Model A:** at least one hkpConstraintInstance deletion callback reaches Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.
- **Model B:** the deletion entries perform constraint cleanup without armor skill progress.
- **Source:** exact slot-0 finalizer and callback-array consumer show a +0x18 virtual call on each non-null entry [EV-0367].
- **Current assessment:** neither model is selected. The entry class, producer, virtual target and ActorValue arguments are unresolved. The TtconDeletedCb trace tag does not identify the concrete target.
- **Discriminant:** resolve receiver-backed writers of the exact +0x40/+0x48 array, identify each entry vtable and slot +0x18 target, and trace its instance/ActorValue arguments to the skill sink.
"""
    write(contradictions_path, contradictions)

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    graph = graph_path.read_text(encoding="utf-8")
    graph += """

EV-0367 adds a concrete callback edge: hkpConstraintInstance slot-0 finalization -> FUN_140b487e0 -> FUN_140b674a0 -> each non-null callback entry slot +0x18 with the instance pointer; null entries are compacted and callback storage is later freed. Entry class, producer and Actor::UseSkill AV11/AV12 descendants are not identified, so no edge to armor skill progress is added [CL-L207], [M-0086].
"""
    write(graph_path, graph)

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    question = next(item for item in frontier["items"] if item.get("id") == "Q-0064")
    if "EV-0367" not in question.setdefault("evidence", []):
        question["evidence"].append("EV-0367")
    for hypothesis in question.get("hypotheses", []):
        if "EV-0367" not in hypothesis.setdefault("evidence", []):
            hypothesis["evidence"].append("EV-0367")
    if "CL-L207" not in question.setdefault("linked_claims", []):
        question["linked_claims"].append("CL-L207")
    question["next_action"] = "Cross-screen the completed +0x40/+0x48 writer candidate sets with hkpConstraintInstance constructor, vtable and world-attach provenance. Start with hkp-region overlapping candidates FUN_140b57860 and FUN_140b58550, identify exact receivers and callsites, and find the producer that supplies entries consumed by FUN_140b674a0. Then resolve each entry slot +0x18 target and trace arguments to Actor::UseSkill AV11/AV12; preserve the Steam positive-damage/effective-protection/raw-AVSK discriminator."
    question.setdefault("methods", []).append("EV-0367 establishes that exact hkpConstraintInstance destruction invokes each non-null deletion callback through entry vtable slot +0x18. Resolve entry producers and concrete targets before selecting Q64-H1 or Q64-H2.")
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    state += "\n- Q-0064 / EV-0367 resolves the exact callback consumer: hkpConstraintInstance slot-0 destruction calls each non-null +0x40/+0x48 entry's vtable slot +0x18, compacts null entries and later frees the array. Entry class, producer and AV11/AV12 route remain unresolved; next identify writer receivers and callback targets.\n"
    write(state_path, state)

    roadmap_path = ROOT / "ROADMAP.md"
    roadmap = roadmap_path.read_text(encoding="utf-8")
    roadmap += "\nEV-0367 confirms that hkpConstraintInstance slot-0 finalization dispatches every non-null +0x40/+0x48 callback entry through entry slot +0x18, compacts nulls and frees the array. No concrete entry class or AV11/AV12 descendant is identified. Cross-screen exact writer candidates and world-attach provenance next. Claim CL-L207 -> M-0086.\n"
    write(roadmap_path, roadmap)

    exp_index = ROOT / "experiments/README.md"
    index = exp_index.read_text(encoding="utf-8")
    index += "\nEXP-0105 / EV-0367 maps hkpConstraintInstance finalization and deletion callback dispatch at entry slot +0x18; callback entry producers and targets remain open.\n"
    write(exp_index, index)

    print("Registered EV-0367 and CL-L207/M-0086; Q-0064 remains active on callback entry producers and targets.")

if __name__ == "__main__":
    main()
