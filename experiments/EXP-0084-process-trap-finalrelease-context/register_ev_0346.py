#!/usr/bin/env python3
"""Register exact local contexts for the five omitted ProcessTrapHit cleanup sites."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0084-process-trap-finalrelease-context"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
STAMP = "20261018T052607Z"
MARKERS = [
    "ADDRESS_RVA=0x7305EA", "ADDRESS_FUNCTION_LOOKUP=FUN_14072fd60",
    "ADDRESS_CONTEXT_BEFORE=1407305ca MOV MOV RCX,qword ptr [RDI + 0x9d0]",
    "ADDRESS_CONTEXT_INSTRUCTION=1407305ea CALL CALL qword ptr [RAX + 0x8]",
    "ADDRESS_CONTEXT_INSTRUCTION=1407305ee MOV MOV RCX,qword ptr [RDI + 0x9a8]",
    "ADDRESS_CONTEXT_INSTRUCTION=140730609 CALL CALL qword ptr [RAX + 0x8]",
    "ADDRESS_CONTEXT_INSTRUCTION=14073060d MOV MOV RCX,qword ptr [RDI + 0x9a0]",
    "ADDRESS_CONTEXT_INSTRUCTION=140730628 CALL CALL qword ptr [RAX + 0x8]",
    "ADDRESS_CONTEXT_INSTRUCTION=14073062c MOV MOV RCX,qword ptr [RDI + 0x8f8]",
    "ADDRESS_CONTEXT_INSTRUCTION=140730647 CALL CALL qword ptr [RAX + 0x8]",
    "ADDRESS_CONTEXT_INSTRUCTION=140730695 MOV MOV RCX,qword ptr [RDI + 0x730]",
    "ADDRESS_CONTEXT_INSTRUCTION=1407306ae CALL CALL qword ptr [RAX + 0x8]",
    "ADDRESS_CONTEXT_COMPLETE=true",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    metadata_path = GH / f"gog-query-{STAMP}.meta.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    if (meta.get("analysis_distribution") != "GOG"
        or meta.get("analysis_binary_product_version") != "1.6.1179"
        or meta.get("analysis_binary_sha256") != BINARY
        or meta.get("program_executable_path_matches_gog_binary") is not True
        or meta.get("query_mode") != "address_context_query"
        or meta.get("exit_code") != 0 or meta.get("ok") is not True
        or meta.get("read_only") is not True or meta.get("auto_analysis_disabled") is not True
        or meta.get("import_attempted") is not False or meta.get("overwrite_attempted") is not False
        or checks.get("program_identity_matches_gog_binary") is not True
        or checks.get("address_context_complete") is not True
        or checks.get("script_no_error") is not True):
        raise SystemExit("address-context identity/read-only/completion validation failed")
    stdout = ROOT / meta["artifacts"]["stdout"]
    raw = stdout.read_text(encoding="utf-8", errors="replace")
    if digest(stdout) != meta.get("stdout_sha256") or any(marker not in raw for marker in MARKERS):
        raise SystemExit("address-context stdout hash/marker validation failed")
    capture_files = [metadata_path] + [ROOT / relative for relative in meta["artifacts"].values()]
    if any(not path.is_file() for path in capture_files):
        raise SystemExit("address-context artifact missing")
    local_hashes = {path.relative_to(ROOT).as_posix(): digest(path) for path in capture_files}
    capture = {
        "stamp": STAMP, "query_mode": meta.get("query_mode"),
        "requested_address_rva": meta.get("requested_address_rva"),
        "checks": checks, "stdout_sha256": meta.get("stdout_sha256"),
        "stderr_sha256": meta.get("stderr_sha256"),
        "query_script_sha256": meta.get("query_script_sha256"),
    }

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0346" for row in evidence.get("items", [])):
        raise SystemExit("EV-0346 already registered")
    note = TX / "EV-0346-note.md"
    put(note, f"""# EV-0346 — Exact ProcessTrapHit final-release site contexts

## Build and method

One identity-checked address-context query used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BINARY}, through the strict dispatcher in read-only/no-analysis mode. The query began at FUN_14072fd60 RVA 0x7305EA and captured a complete 128-instruction local window containing all five indirect sites previously outside EV-0325's fixed disassembly window. No GOG RVA is transferred to Steam AE 1.6.1170.0.

## Direct observations

- Site RVA 0x7305EA loads PlayerCharacter field +0x9D0, tests it for null, atomically decrements its object refcount at +0x8, and calls the loaded object's vtable slot +0x8 only when the prior count is one.
- Site RVA 0x730609 repeats the same refcount-final slot +0x8 pattern for PlayerCharacter field +0x9A8.
- Site RVA 0x730628 repeats it for PlayerCharacter field +0x9A0.
- Site RVA 0x730647 repeats it for PlayerCharacter field +0x8F8.
- Site RVA 0x7306AE repeats it for PlayerCharacter field +0x730.
- The same local window shows adjacent direct helper work and confirms each call is on the PlayerCharacter teardown path FUN_14072fd60 [capture 20261018T052607Z]. EV-0325's complete census identifies the other three sites: +0x730/+0x30 parent interface slot +0x1C0 and child slot +0x8 release; the global pointer's slot-0 call [EV-0325], [EV-0327]. Together, the eight sites have exact field/receiver or interface-field contexts.
- EV-0332, EV-0329/0333, EV-0331, and EV-0334 map separate candidate producer paths for +0x9D0, +0x9A0/+0x9A8, +0x8F8, and +0x730. Those sources do not yet supply a concrete runtime class for every stored object. EV-0334's NiNode parent-child behavior and EV-0331's NiNode resource candidate remain conditional.
- EV-0344 resolves DAT_143188918 as a PlayerCharacter construction path, superseding EV-0329's earlier unresolved global-class limit. The fields released above still have distinct producer/type gaps.

## Causal assessment

This completes the missing local callsite-context capture and classifies all five omitted sites as conditional refcount-final destructor dispatches on PlayerCharacter fields. It does not resolve the dynamic slot +0x8 implementations or their descendants, and it does not show any path to Actor::UseSkill AV11/AV12. Q64-H1 and Q64-H2 remain proposed. No no-skill conclusion or OBJ-1 edge is added.

## Exact next discriminant

Resolve concrete object classes and slot +0x8 targets for the data-selected fields. Start with the +0x8F8 first-person skeleton resource and +0x730 NiAVObject/NiNode candidate using supported read-only source evidence; then compare +0x9D0 and +0x9A0/+0x9A8 metadata/model outputs. Screen every concrete finalizer descendant against the mapped AV11/AV12 sink.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = digest(note)
    manifest = TX / "EV-0346-capture-manifest.json"
    put(manifest, json.dumps({"evidence_id": "EV-0346", "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY, "capture": capture}, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)
    docs = {
        "README.md": "# EXP-0084 — ProcessTrapHit final-release contexts\n\nRecover exact local instruction context for every previously omitted indirect callsite in the FUN_14072fd60 PlayerCharacter cleanup path.\n",
        "hypothesis.md": "# Competing models\n\n- Q64-H1: the mapped refcount-final calls and their concrete descendants do not reach AV11/AV12 skill progress.\n- Q64-H2: at least one dynamically selected finalizer descendant routes an armor ActorValue into skill progress.\n\nSite-level refcount logic alone does not distinguish these models.\n",
        "protocol.md": "# Protocol\n\nUse build-attested GOG address-context captures through the strict dispatcher in read-only/no-analysis mode. Verify each call's receiver field, null/refcount guard, and vtable slot. Resolve dynamic targets through exact producer tables or source classes; never treat a slot +0x8 release shape as a no-skill proof.\n",
        "results.md": "# Results\n\nThe five formerly omitted sites in FUN_14072fd60 are refcount-final calls on fields +0x9D0, +0x9A8, +0x9A0, +0x8F8, and +0x730. Each calls dynamic slot +0x8 only when the old refcount is one. Combined with EV-0325/0327, all eight callsites now have field/interface context, while their concrete targets and descendants remain unresolved [EV-0346].\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- Concrete finalizer descendants that avoid the mapped Actor::UseSkill AV11/AV12 sink support Q64-H1 for those resolved branches.\n- Any finalizer path carrying AV11/AV12 into the skill-progress sink supports Q64-H2.\n- A generic vtable slot +0x8 or unresolved loaded resource is inconclusive.\n",
        "implications.md": "# Implications\n\nThis removes the missing-instruction-context gap for the five cleanup sites. It narrows the remaining Q64 uncertainty to the concrete classes and descendants selected by four resource/scene fields plus the global camera callback.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Recover concrete vtable and slot +0x8 target for each stored object.\n2. Follow nested releases and indirect descendants.\n3. Compare each path to Actor::UseSkill with AV11/AV12.\n4. Preserve untyped or profile-dependent objects as unresolved.\n",
    }
    for name, content in docs.items():
        put(EXP / name, content)
    script_path = EXP / "register_ev_0346.py"
    local_hashes[script_path.relative_to(ROOT).as_posix()] = digest(script_path)
    for path in EXP.iterdir():
        if path.is_file():
            local_hashes[path.relative_to(ROOT).as_posix()] = digest(path)
    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE", "modified_state": False, "id": "EV-0346", "kind": "native",
        "source": "Exact local GOG Ghidra address context for the five omitted FUN_14072fd60 cleanup sites.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0346-note.md",
        "sha256": digest(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Complete local instruction window for five indirect destructor sites in FUN_14072fd60; earlier EV-0325/0327 captures map the other three. Concrete per-field vtables and finalizer descendants remain unresolved.",
        "result": "The five sites are refcount-final virtual slot +0x8 calls on PlayerCharacter fields +0x9D0, +0x9A8, +0x9A0, +0x8F8, and +0x730. All eight callsites now have field/interface contexts, but no concrete target/descendant reaches or is excluded from AV11/AV12 by this evidence.",
        "related_evidence": ["EV-0325", "EV-0327", "EV-0328", "EV-0329", "EV-0331", "EV-0332", "EV-0333", "EV-0334"],
        "local_hashes": local_hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    old = "| CL-L161 | In GOG AE 1.6.1179.0, PlayerCharacter teardown releases pointer fields +0x9A0 and +0x9A8 through refcount-final vtable slot +0x8. FUN_1407445d0 stores values at the same offsets; its direct callers pass DAT_143188918, whose runtime class is not identified. FUN_140744180 is called from FUN_140738380 and uses primary PlayerCharacter vtable accessors for +0x8F8/+0x8F0 on that helper path. | supported (bounded build-attested GOG decompilation and vtable mapping) | [EV-0329] | The setter global and stored resource-derived object remain dynamically untyped; no finalizer descendant or AV11/AV12 skill award is mapped. This does not establish zero armor XP, Steam behavior, or vanilla reproduction. No OBJ-1 edge is supported. |"
    new = "| CL-L161 | In GOG AE 1.6.1179.0, PlayerCharacter teardown releases pointer fields +0x9A0 and +0x9A8 through refcount-final vtable slot +0x8. FUN_1407445d0 stores values at the same offsets; its direct callers pass DAT_143188918, whose PlayerCharacter construction path is resolved by FUN_14064cac0/FUN_14072ed70. FUN_140744180 is called from FUN_140738380 and uses primary PlayerCharacter vtable accessors for +0x8F8/+0x8F0 on that helper path. | supported (bounded build-attested GOG decompilation and constructor/vtable mapping) | [EV-0329], [EV-0344] | The stored resource-derived objects and their finalizer descendants remain dynamically untyped; no AV11/AV12 skill award is mapped. This does not establish zero armor XP, Steam behavior, or vanilla reproduction. No OBJ-1 edge is supported. |"
    if old not in claims:
        raise SystemExit("expected historical CL-L161 wording not found")
    claims = claims.replace(old, new)
    if "| CL-L184 |" in claims:
        raise SystemExit("CL-L184 already exists")
    put(claims_path, claims.rstrip()
        + "\n| CL-L184 | In GOG AE 1.6.1179.0, the five previously uncaptured FUN_14072fd60 indirect sites at RVAs 0x7305EA, 0x730609, 0x730628, 0x730647 and 0x7306AE are refcount-final vtable slot +0x8 calls on PlayerCharacter fields +0x9D0, +0x9A8, +0x9A0, +0x8F8 and +0x730 respectively. | supported (complete build-attested local instruction context) | [EV-0346], [EV-0325] | Concrete object vtables, slot +0x8 implementations and descendants remain unresolved; no Q64-H1/H2 resolution or AV11/AV12 exclusion follows. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8")
    old_m58 = "PlayerCharacter teardown FUN_14072fd60 decrements the references stored at +0x9A0/+0x9A8 and calls each object's vtable slot +0x8 when the old count is one. FUN_1407445d0 stores a candidate value into those offsets and uses the same final-release shape for replaced values. Its direct callers pass DAT_143188918, whose runtime class is not identified. A related FUN_140744180 path uses primary PlayerCharacter vtable accessors for +0x8F8/+0x8F0. FUN_140216b40 produces a resource-derived value via generic loading and dynamic object calls, but its class and finalizer target remain unresolved [EV-0329]. Claim CL-L161 -> M-0058. No ActorValue/skill sink edge is supported or excluded; no OBJ-1 edge is supported."
    new_m58 = "PlayerCharacter teardown FUN_14072fd60 decrements the references stored at +0x9A0/+0x9A8 and calls each object's vtable slot +0x8 when the old count is one. FUN_1407445d0 stores candidate values into those offsets; its direct callers pass DAT_143188918, now resolved as the PlayerCharacter object constructed by FUN_14064cac0/FUN_14072ed70 [EV-0344]. The stored resource-derived values and finalizer targets remain unresolved [EV-0329]. Claim CL-L161 -> M-0058. No ActorValue/skill sink edge is supported or excluded; no OBJ-1 edge is supported."
    if old_m58 not in mechanisms:
        raise SystemExit("expected M-0058 wording not found")
    mechanisms = mechanisms.replace(old_m58, new_m58)
    put(mechanisms_path, mechanisms.rstrip()
        + "\n\n## M-0066 — ProcessTrapHit PlayerCharacter final-release site map (Q-0064)\n\nThe complete FUN_14072fd60 census has eight indirect sites. Five formerly missing contexts are conditional refcount-final slot +0x8 calls on PlayerCharacter fields +0x9D0, +0x9A8, +0x9A0, +0x8F8, and +0x730 [EV-0346]. The other three are the +0x730/+0x30 interface slot +0x1C0, its child slot +0x8 release, and the PlayerCamera global slot-0 cleanup [EV-0325], [EV-0327]. The site fields are mapped, but the resource-selected vtables and destructor descendants remain unresolved; this is not a no-skill result. Claim CL-L184 -> M-0066.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    graph = graph_path.read_text(encoding="utf-8")
    old_graph = "EV-0329 maps PlayerCharacter teardown fields +0x9A0/+0x9A8 to refcount-final virtual slot +0x8 calls and traces a shared setter plus a resource-derived non-null value producer. The related FUN_140744180 helper path uses exact primary PlayerCharacter vtable accessors for +0x8F8/+0x8F0. The setter's global receiver and stored object's dynamic class/finalizer remain unresolved, so no edge to Actor::UseSkill or AV11/AV12 skill progress is added or excluded. Claim CL-L161 -> M-0058; Q-0064 remains active. No edge to OBJ-1 is supported [EV-0329]."
    new_graph = "EV-0329 maps PlayerCharacter teardown fields +0x9A0/+0x9A8 to refcount-final virtual slot +0x8 calls and traces a shared setter plus a resource-derived non-null value producer. The related FUN_140744180 helper path uses exact primary PlayerCharacter vtable accessors for +0x8F8/+0x8F0. EV-0344 resolves the setter's DAT_143188918 receiver as a PlayerCharacter construction path; the stored resource object's class/finalizer remains unresolved, so no edge to Actor::UseSkill or AV11/AV12 skill progress is added or excluded. Claim CL-L161 -> M-0058; Q-0064 remains active. No edge to OBJ-1 is supported [EV-0329], [EV-0344]."
    if old_graph not in graph:
        raise SystemExit("expected EV-0329 graph wording not found")
    graph = graph.replace(old_graph, new_graph)
    graph = graph.rstrip() + "\n\nEV-0346 supplies the local contexts missing from EV-0325: the five late FUN_14072fd60 calls release fields +0x9D0, +0x9A8, +0x9A0, +0x8F8, and +0x730 through dynamic slot +0x8 when each refcount reaches its final release. Combined with the first three callsite contexts in EV-0325/0327, all eight sites are field/interface-mapped, but none of the five new object finalizer tables is concrete. EV-0344 resolves the shared global receiver class without resolving stored resource types. No edge to AV11/AV12 or OBJ-1 is added; Q64-H1/H2 remain proposed. Claim CL-L184 -> M-0066 [EV-0346].\n"
    put(graph_path, graph)

    index_path = ROOT / "experiments/README.md"
    put(index_path, index_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEXP-0084 / EV-0346 captures the five formerly omitted PlayerCharacter cleanup callsites; all eight indirect sites now have field/interface context, while dynamic target tables remain unresolved.\n")
    roadmap_path = ROOT / "research/ROADMAP.md"
    put(roadmap_path, roadmap_path.read_text(encoding="utf-8").rstrip()
        + "EV-0346 completes the local contexts for all eight FUN_14072fd60 indirect sites. Five are refcount-final releases of +0x9D0/+0x9A8/+0x9A0/+0x8F8/+0x730; concrete tables and descendants remain open. The global DAT_143188918 class is resolved by EV-0344, while the resource values are not. Next, identify exact source-backed vtables/finalizers, starting with the +0x8F8 skeleton and +0x730 scene-object paths. Claim CL-L184 -> M-0066.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    q65 = next(row for row in frontier["items"] if row.get("id") == "Q-0065")
    for row in (q64, q65):
        if "EV-0346" not in row.setdefault("evidence", []):
            row["evidence"].append("EV-0346")
        for hypothesis in row.get("hypotheses", []):
            if "EV-0346" not in hypothesis.setdefault("evidence", []):
                hypothesis["evidence"].append("EV-0346")
    if "CL-L184" not in q64.setdefault("linked_claims", []):
        q64["linked_claims"].append("CL-L184")
    q64["next_action"] = (
        "Identify concrete vtables and slot +0x8 finalizers for the data-selected +0x8F8 first-person skeleton, "
        "+0x730 scene object, +0x9D0 metadata output, and +0x9A0/+0x9A8 model outputs. Start with supported "
        "read-only source evidence for the exact skeleton/scene resources, then screen each finalizer descendant "
        "for Actor::UseSkill AV11/AV12. Keep untyped objects unresolved."
    )
    q65["next_action"] = (
        "Compare exact producer-backed vtables/finalizers across +0x730, +0x8F8, +0x9A0/+0x9A8, and ThirdPersonState+0xA0. "
        "The shared refcount slot +0x8 is only ABI evidence; matching concrete tables support Q65-H1, while distinct tables support Q65-H2."
    )
    q64.setdefault("attempts", []).append({
        "action_key": "q64-five-remaining-cleanup-site-contexts",
        "outcome": "EV-0346 captures all five late FUN_14072fd60 sites. They are refcount-final slot +0x8 calls on fields +0x9D0, +0x9A8, +0x9A0, +0x8F8, and +0x730. Combined with EV-0325/0327, all eight indirect sites have field/interface context, but dynamic object vtables and descendants remain unresolved.",
        "evidence": ["EV-0346"],
        "new_discriminant": "Concrete loaded-resource vtables and slot +0x8 targets, especially for +0x8F8 and +0x730, can now be compared against exact cleanup sites and screened for AV11/AV12.",
        "next_action": q64["next_action"],
    })
    q65.setdefault("attempts", []).append({
        "action_key": "q65-finalrelease-fields-mapped",
        "outcome": "EV-0346 shows five independent fields all use the generic final-release slot +0x8 ABI; EV-0344 resolves the global receiver but not resource values. This does not establish a shared NiNode family.",
        "evidence": ["EV-0346", "EV-0344"],
        "new_discriminant": "Only matching concrete producer-backed vtables/finalizers across fields supports a common class family; differing tables falsify it.",
        "next_action": q65["next_action"],
    })
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))
    print("registered EV-0346 / CL-L184 / M-0066; all eight callsites have context, target types remain unresolved")


if __name__ == "__main__":
    main()
