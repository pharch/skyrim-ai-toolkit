#!/usr/bin/env python3
"""Register the exact hkpConstraintInstance final-release descendant trace."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0095-q64-hkp-finalizer-descendants"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
NEW_EXPECTED = {
    "20261018T071634Z": [
        "DECOMPILATION_BEGIN=FUN_140b3a830",
        "CALLEE_DECOMPILATION_BEGIN=FUN_140a89e60",
        "(**(code **)*param_1)(param_1,1)",
    ],
    "20261018T071909Z": [
        "DECOMPILATION_BEGIN=FUN_140b36b20",
        "INDIRECT_CALL_SITE_COUNT=1",
        "DIRECT_CALL_EDGE_SCAN_COMPLETE=true",
    ],
    "20261018T072054Z": [
        "DECOMPILATION_BEGIN=FUN_140b487e0",
        "CALLEE_DECOMPILATION_BEGIN=FUN_140b674a0",
        "TtconDeletedCb",
        "FUN_140a89e60",
    ],
}
REUSED_EXPECTED = [
    "POINTER_TABLE_BASE_RVA=0x1973D58",
    "POINTER_TABLE_ENTRY=index:0 address:141973d58 value:0x140B36B20 target:140b36b20 function:FUN_140b36b20",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def checked_capture(stamp: str, expected: list[str], require_complete: bool = True):
    meta_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    raw_path = ROOT / meta["artifacts"]["stdout"]
    checks = meta.get("checks", {})
    valid = (
        meta.get("analysis_distribution") == "GOG"
        and meta.get("analysis_binary_product_version") == "1.6.1179"
        and meta.get("analysis_binary_sha256") == BINARY
        and meta.get("program_executable_path_matches_gog_binary") is True
        and meta.get("exit_code") == 0
        and meta.get("read_only") is True
        and meta.get("auto_analysis_disabled") is True
        and meta.get("import_attempted") is False
        and meta.get("overwrite_attempted") is False
        and checks.get("program_identity_matches_gog_binary") is True
        and checks.get("script_no_error") is True
        and sha(raw_path) == meta.get("stdout_sha256")
    )
    if require_complete:
        valid = valid and meta.get("ok") is True and all(checks.values())
    if not valid:
        raise SystemExit(f"capture identity/completion check failed: {stamp}")
    raw = raw_path.read_text(errors="replace")
    if any(marker not in raw for marker in expected):
        raise SystemExit(f"capture marker missing: {stamp}")
    return meta, meta_path, raw_path


def main() -> None:
    fresh = {stamp: checked_capture(stamp, markers) for stamp, markers in NEW_EXPECTED.items()}
    reused_meta, reused_meta_path, reused_raw_path = checked_capture(
        "20261018T070746Z", REUSED_EXPECTED
    )
    note = TX / "EV-0357-note.md"
    manifest = TX / "EV-0357-capture-manifest.json"

    write(note, f"""# EV-0357 — hkpConstraintInstance final-release descendants

## Build and method

Three fresh identity-checked queries used the existing GOG Skyrim AE 1.6.1179.0 project through the strict dispatcher in read-only/no-analysis mode. A previously registered EV-0356 pointer-table capture supplies the exact slot-0 entry. The analysis binary SHA-256 is {BINARY}. GOG RVAs are not transferred to Steam AE 1.6.1170.0.

## Direct observations

- FUN_140b3a830 unconditionally calls FUN_140a89e60 on its third argument after the guarded physics registration and list updates. The reference helper decrements the object's count and dispatches its slot 0 with deletion flag 1 when the old count is one [fresh capture 20261018T071634Z].
- EV-0356 traces the ProcessTrapHit constraint factory through FUN_140ecdfc0/FUN_140b48720 and maps the factory-created hkpConstraintInstance vtable at RVA 0x1973D58. The captured table's index 0 points to FUN_140b36b20 [EV-0356 pointer-table capture 20261018T070746Z].
- A complete call-edge census of FUN_140b36b20 shows three direct calls and one indirect allocator call. The body first invokes FUN_140b487e0; on its deleting path it releases the 0x70-byte object through a TLS allocator slot +0x10, or uses FUN_140fb9950 on the alternate flag path [fresh capture 20261018T071909Z].
- FUN_140b487e0 invokes FUN_140b674a0, releases member references at object offsets +0x28, +0x30 and +0x18 through FUN_140a89e60, frees its callback and array storage, then restores hkBaseObject::vftable. FUN_140b674a0 can dispatch callbacks stored in an array at +0x40 through slot +0x18. The constructor FUN_140b48720 initializes that array pointer to zero and the count/flags word at +0x48 to 0x80000000; later writers and runtime population remain unverified [fresh capture 20261018T072054Z; constructor context in EV-0356].
- No direct Actor::UseSkill call or AV11/AV12 argument appears in the captured finalizer bodies. The callback slot +0x18 targets and the three member-reference classes/finalizers are unresolved, so this is not a transitive no-skill result.

## Competing models and result

- Q64-H1 predicts the producer-backed callbacks and member finalizers stay outside AV11/AV12 skill progress.
- Q64-H2 predicts one resolved callback/member descendant reaches Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.

The exact hkpConstraintInstance branch is narrowed toward physics-object ownership cleanup: its finalizer is a deleting destructor with member, callback-array, and allocator handling, with no direct skill-credit call. The unresolved callback and member types leave Q64-H1/H2 proposed.

## Scope and exact next action

This result applies to the factory-created hkpConstraintInstance path only. It does not classify other FUN_140b3a830 callers, the remaining PlayerCharacter cleanup sites, the exact PlayerCamera-instance relation, live armor protection, final hit damage, raw AVSK deltas, or Steam behavior. Continue by tracing post-constructor writers to callback array +0x40/count +0x48 and identifying producer classes for the +0x18/+0x28/+0x30 member references; follow any populated callback slot +0x18 or final-release slot 0 against AV11/AV12.
""")

    captures = {}
    for stamp, (meta, _meta_path, _raw_path) in fresh.items():
        captures[stamp] = {
            "query_mode": meta.get("query_mode"),
            "requested_rva": meta.get("requested_rva"),
            "checks": meta.get("checks"),
            "stdout_sha256": meta.get("stdout_sha256"),
            "stderr_sha256": meta.get("stderr_sha256"),
            "query_script_sha256": meta.get("query_script_sha256"),
        }
    captures["20261018T070746Z-reused-from-EV-0356"] = {
        "query_mode": reused_meta.get("query_mode"),
        "requested_pointer_table_rva": reused_meta.get("requested_pointer_table_rva"),
        "checks": reused_meta.get("checks"),
        "stdout_sha256": reused_meta.get("stdout_sha256"),
        "source_evidence": "EV-0356",
    }
    write(manifest, json.dumps({
        "evidence_id": "EV-0357",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY,
        "captures": captures,
    }, indent=2))

    docs = {
        "README.md": "# EXP-0095 — hkpConstraintInstance finalizer descendants\n\nResolve whether the factory-created ProcessTrapHit physics constraint final-release callbacks can reach AV11/AV12 skill progress.\n",
        "hypothesis.md": "# Competing models\n\n- Q64-H1: the exact constraint finalizer and producer-backed descendants stay outside AV11/AV12 skill progress.\n- Q64-H2: a concrete callback or member finalizer reaches Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.\n\nUnresolved virtual targets remain inconclusive.\n",
        "protocol.md": "# Protocol\n\nUse the EV-0356 factory/vtable provenance, resolve slot 0, census its direct and indirect edges, then trace only producer-backed callback/member sources. Keep the GOG binary separate from Steam runtime claims.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Confirm the exact vtable slot-0 target for the factory-created hkpConstraintInstance.\n2. Map callback-array and member-reference writers for offsets +0x40/+0x48 and +0x18/+0x28/+0x30.\n3. Follow producer-backed callback slot +0x18 or member slot 0 targets to Actor::UseSkill and inspect the ActorValue argument.\n4. Treat an unresolved callback, member class, or finalizer as inconclusive.\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- A concrete AV11/AV12 skill-credit edge supports Q64-H2 for this branch.\n- Producer-backed physics/allocator/reference cleanup without a skill sink strengthens Q64-H1 only for resolved descendants.\n- An unresolved callback or member finalizer does not decide Q64-H1/H2.\n",
        "results.md": "# Results\n\nThe factory-created hkpConstraintInstance slot 0 resolves to FUN_140b36b20, which calls its member cleanup helper and TLS allocator. That helper can dispatch callbacks from the +0x40 array through slot +0x18 and releases three member references through the generic refcount helper. No direct Actor::UseSkill call appears, but callback/member types remain unresolved [EV-0357].\n",
        "implications.md": "# Implications\n\nThe exact constraint finalizer is bounded to ownership and callback cleanup at the direct-body level. Continue through the callback-array/member producers before counting this branch as away from AV11/AV12.\n",
    }
    for name, body in docs.items():
        write(EXP / name, body)

    local_hashes = {}
    for meta, meta_path, raw_path in fresh.values():
        for path in [meta_path, raw_path, *(ROOT / item for item in meta["artifacts"].values())]:
            if path.is_file():
                local_hashes[path.relative_to(ROOT).as_posix()] = sha(path)
    for path in [reused_meta_path, reused_raw_path, note, *EXP.iterdir(), Path(__file__)]:
        if path.is_file():
            local_hashes[path.relative_to(ROOT).as_posix()] = sha(path)
    local_hashes.pop(manifest.relative_to(ROOT).as_posix(), None)
    write(manifest, json.dumps({
        "evidence_id": "EV-0357",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY,
        "captures": captures,
        "registered_local_hashes": local_hashes,
    }, indent=2))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = sha(manifest)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0357" for item in evidence["items"]):
        raise SystemExit("EV-0357 is already registered")
    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0357",
        "kind": "native",
        "source": "Identity-checked read-only GOG Ghidra traces of the ProcessTrapHit physics-helper refcount release and factory-created hkpConstraintInstance deleting destructor.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0357-note.md",
        "sha256": sha(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
        "coverage": "The exact FUN_140b3a830 final-reference release, hkpConstraintInstance slot-0 destructor, direct helper census, and producer-initialized callback/member fields.",
        "result": "The factory-created hkpConstraintInstance slot 0 resolves to FUN_140b36b20 and FUN_140b487e0. Direct bodies release callback/member storage and use a TLS allocator, with no direct Actor::UseSkill call. Callback +0x18 targets and member classes/finalizers remain unresolved; Q64 stays open.",
        "related_evidence": ["EV-0355", "EV-0356", "EV-0324"],
        "local_hashes": local_hashes,
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L196 |" in claims:
        raise SystemExit("CL-L196 is already registered")
    write(claims_path, claims.rstrip() + "\n| CL-L196 | In GOG AE 1.6.1179.0, the factory-created hkpConstraintInstance final-reference path maps slot 0 to FUN_140b36b20 and FUN_140b487e0, whose direct bodies perform callback/member ownership cleanup and TLS allocator release without a direct Actor::UseSkill call. | supported for the exact class and mapped direct bodies | [EV-0357], [EV-0356] | Callback slot +0x18 targets, member classes/finalizers, runtime refcount state, other helper callers, and AV11/AV12 transitive reachability remain unresolved. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    write(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip() + "\n\n## M-0077 — hkpConstraintInstance final-release callback and member cleanup (Q-0064)\n\nFor the factory-created constraint passed through FUN_140b3a830, its generic reference release may dispatch slot 0 when the count reaches one. The exact hkpConstraintInstance table maps that slot to FUN_140b36b20 and its body to FUN_140b487e0. The destructor walks a callback array at +0x40 through slot +0x18, releases member references at +0x18/+0x28/+0x30, frees storage through a TLS allocator, and restores hkBaseObject::vftable. The constructor starts the callback pointer null and low count zero, but later callback writers and member classes/finalizers are unresolved; no transitive no-skill result follows [EV-0357], [EV-0356]. Claim CL-L196 -> M-0077.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    write(graph_path, graph_path.read_text(encoding="utf-8").rstrip() + "\n\nEV-0357 extends the bounded ProcessTrapHit physics path from FUN_140b3a830's refcount release to the factory-created hkpConstraintInstance slot-0 deleting destructor. Its mapped direct body performs callback/member cleanup and TLS allocator release; callback slot +0x18 and embedded member finalizers remain dynamic. No edge to AV11/AV12 is established, and no new edge to the EV-0326 quest route is supported [CL-L194], [CL-L196].\n")

    roadmap_path = ROOT / "research/ROADMAP.md"
    write(roadmap_path, roadmap_path.read_text(encoding="utf-8").rstrip() + "\n\nEV-0357 resolves the factory-created hkpConstraintInstance slot-0 cleanup body, but its callback array and member finalizers remain open. Next identify writers to +0x40/+0x48 and producer classes at +0x18/+0x28/+0x30, then screen their targets against AV11/AV12. Keep Steam hit/protection/raw-AVSK measurements separate.\n")

    index_path = ROOT / "experiments/README.md"
    write(index_path, index_path.read_text(encoding="utf-8").rstrip() + "\n\nEXP-0095 / EV-0357 maps the factory-created hkpConstraintInstance slot-0 finalizer to callback/member cleanup and TLS allocation. Its callback and embedded member descendants remain unresolved.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(item for item in frontier["items"] if item.get("id") == "Q-0064")
    next_action = "Trace post-constructor writers to the hkpConstraintInstance callback array +0x40/count +0x48 and identify producer classes for its +0x18/+0x28/+0x30 member references; follow any populated callback slot +0x18 or final-release slot 0 descendant against Actor::UseSkill AV11/AV12."
    evidence_buckets = [q64.setdefault("evidence", [])]
    evidence_buckets.extend(hypothesis.setdefault("evidence", []) for hypothesis in q64.get("hypotheses", []))
    for bucket in evidence_buckets:
        if "EV-0357" not in bucket:
            bucket.append("EV-0357")
    if "CL-L196" not in q64.setdefault("linked_claims", []):
        q64["linked_claims"].append("CL-L196")
    q64["next_action"] = next_action
    q64.setdefault("attempts", []).append({
        "action_key": "q64-hkp-finalizer-descendant-census",
        "outcome": "EV-0357 maps the factory-created hkpConstraintInstance slot-0 deleting destructor to callback/member ownership cleanup and TLS allocator release; callback targets and member classes remain unresolved.",
        "evidence": ["EV-0357", "EV-0356"],
        "new_discriminant": "The hkpConstraintInstance constructor starts its callback array empty, but a later writer may populate +0x40/+0x48; producer-backed member refs at +0x18/+0x28/+0x30 may also supply independent slot-0 descendants.",
        "next_action": next_action,
    })
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    checkpoint_path = ROOT / "experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"
    checkpoint_source = checkpoint_path.read_text(encoding="utf-8")
    needle = "- Q-0064 / EV-0356 maps the factory-created child payload as hkpConstraintInstance; its slot +0x30 returns zero, bypassing one conditional list-removal branch. CL-L194 records no supported causal edge between the EV-0326 Fort stage-request route and this OBJ-2 physics path; a shared call/state dependency would falsify it.\n"
    addition = "- Q-0064 / EV-0357 resolves the factory-created hkpConstraintInstance slot-0 finalizer to callback/member ownership cleanup and TLS allocation; callback +0x18 targets and member classes remain unresolved.\n"
    if needle not in checkpoint_source:
        raise SystemExit("checkpoint helper lacks EV-0356 summary line")
    checkpoint_source = checkpoint_source.replace(needle, needle + addition)
    checkpoint_source = checkpoint_source.replace(
        "Q-0064 remains active on PlayerCharacter cleanup dispatches for the OBJ-2 physical-trap route.",
        "Q-0064 remains active on the ProcessTrapHit cleanup descendants for the OBJ-2 physical-trap route.",
    )
    write(checkpoint_path, checkpoint_source)
    print("registered EV-0357 / CL-L196 / M-0077; Q-0064 remains active")


if __name__ == "__main__":
    main()
