#!/usr/bin/env python3
"""Register the hkpSimulationIsland type correction and owner-list boundary."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = Path(__file__).resolve().parent
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
FRESH = {
    "20261018T082215Z": [
        "POINTER_TABLE_BASE_RVA=0x1977590",
        "POINTER_TABLE_ENTRY=index:0 address:141977590 value:0x140B60DF0",
        "POINTER_TABLE_ENTRY=index:1 address:141977598 value:0x140B60E10",
        "POINTER_TABLE_ENTRY=index:4 address:1419775b0 value:0x6C756D6953706B68",
        "POINTER_TABLE_XREF=entry_index:4 entry_address:1419775b0 from:1400d8ff1",
        "POINTER_TABLE_ENTRY=index:7 address:1419775c8 value:0x7450797469746E45",
    ],
    "20261018T082317Z": [
        "FUNCTION_LOOKUP=FUN_140b60e30",
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=0",
        "XREF_CALL_EDGE=NOT_FOUND_IN_ANALYZED_PROJECT",
        "*pbVar1 = *pbVar1 | param_3;",
    ],
    "20261018T082418Z": [
        "FUNCTION_LOOKUP=FUN_140b4c000",
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=0",
        "void FUN_140b4c000(void)",
        "return;",
    ],
    "20261018T082541Z": [
        "POINTER_TABLE_BASE_RVA=0x1977588",
        "POINTER_TABLE_ENTRY=index:0 address:141977588 value:0x140B60780",
        "POINTER_TABLE_ENTRY=index:1 address:141977590 value:0x140B60DF0",
        "POINTER_TABLE_ENTRY=index:2 address:141977598 value:0x140B60E10",
        "POINTER_TABLE_ENTRY=index:3 address:1419775a0 value:0x140B60E30",
        "POINTER_TABLE_ENTRY=index:4 address:1419775a8 value:0x140B4C000",
    ],
    "20261018T082702Z": [
        "OFFSET_QUERY=0x60",
        "OFFSET_ACCESS_COUNT=14003",
        "OFFSET_ACCESSES_PRINTED=2048",
        "OFFSET_ACCESS_OUTPUT_LIMIT=2048",
        "OFFSET_WRITER_ANALYSIS_COMPLETE=true",
    ],
    "20261018T083000Z": [
        "OFFSET_QUERY=0x68",
        "OFFSET_ACCESS_COUNT=8295",
        "OFFSET_ACCESSES_PRINTED=2048",
        "OFFSET_ACCESS_OUTPUT_LIMIT=2048",
        "OFFSET_WRITER_ANALYSIS_COMPLETE=true",
    ],
    "20261018T083226Z": [
        "STRING_QUERY=hkpSimulationIslandAndEntity",
        "STRING_MATCH_COUNT=0",
        "STRING_REFERENCE_SCAN_COMPLETE=true",
    ],
    "20261018T083331Z": [
        "TARGET_RVA=0xD8FE0",
        "DISASM=1400d8ff1 LEA RDX, [0x1419775b0]",
        'FUN_140a98d50(&DAT_1431bd310,"hkpSimulationIsland",&DAT_1431b2d80,0xb8',
        "INCOMING_CALLER_FUNCTION_COUNT=0",
    ],
}
REUSED = {
    "20261018T080315Z": [
        "POINTER_TABLE_BASE_RVA=0x1977590",
        "POINTER_TABLE_ENTRY=index:1 address:141977598 value:0x140B60E10",
        "POINTER_TABLE_XREF=entry_index:4 entry_address:1419775b0 from:1400d8ff1",
    ],
    "20261018T080431Z": [
        "DECOMPILATION_BEGIN=FUN_140b60780",
        '"EntityPtrs"',
        '"ConMstPtr"',
        '"ConInstance"',
        '"ConData"',
    ],
    "20261018T080106Z": [
        "DISASM=140b60e14 MOV RCX, qword ptr [RCX + 0x10]",
        "DISASM=140b60e18 JMP 0x140b439e0",
    ],
    "20261018T080209Z": [
        "DECOMPILATION_BEGIN=FUN_140f60440",
        "FUN_140b439e0",
    ],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def checked(stamp: str, markers: list[str]):
    meta_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    stdout_path = ROOT / meta["artifacts"]["stdout"]
    checks = meta.get("checks", {})
    valid = (
        meta.get("analysis_distribution") == "GOG"
        and meta.get("analysis_binary_product_version") == "1.6.1179"
        and meta.get("analysis_binary_sha256") == BINARY
        and meta.get("program_executable_path_matches_gog_binary") is True
        and meta.get("exit_code") == 0
        and meta.get("ok") is True
        and meta.get("read_only") is True
        and meta.get("auto_analysis_disabled") is True
        and meta.get("import_attempted") is False
        and meta.get("overwrite_attempted") is False
        and checks.get("program_identity_matches_gog_binary") is True
        and checks.get("script_no_error") is True
        and all(checks.values())
        and sha(stdout_path) == meta.get("stdout_sha256")
    )
    if not valid:
        raise SystemExit(f"capture identity/completion check failed: {stamp}")
    raw = stdout_path.read_text(errors="replace")
    missing = [marker for marker in markers if marker not in raw]
    if missing:
        raise SystemExit(f"capture marker missing: {stamp}: {missing}")
    return meta, meta_path, stdout_path, raw


def main() -> None:
    fresh = {stamp: checked(stamp, markers) for stamp, markers in FRESH.items()}
    reused = {stamp: checked(stamp, markers) for stamp, markers in REUSED.items()}
    displacement_scan_output = {}
    for stamp, displacement in (("20261018T082702Z", "0x60"), ("20261018T083000Z", "0x68")):
        raw = fresh[stamp][3]
        printed = [line for line in raw.splitlines() if "OFFSET_ACCESS=address:" in line]
        total = re.search(r"OFFSET_ACCESS_COUNT=(\d+)", raw)
        cap = re.search(r"OFFSET_ACCESS_OUTPUT_LIMIT=(\d+)", raw)
        displacement_scan_output[displacement] = {
            "total_matching_accesses": int(total.group(1)) if total else None,
            "printed_accesses": len(printed),
            "output_limit": int(cap.group(1)) if cap else None,
            "last_printed_access": printed[-1].split("OFFSET_ACCESS=", 1)[1] if printed else None,
        }

    # Append a durable erratum to the earlier interpretive note while retaining its original text.
    old_note = TX / "EV-0359-note.md"
    old_content = old_note.read_text(encoding="utf-8")
    erratum = """

## Type-name correction from EV-0362

The earlier interpretation above combined adjacent bytes and called this `hkpSimulationIslandAndEntity`. EV-0362 resolves the referenced type-name at address 0x1419775b0 as `hkpSimulationIsland`: FUN_1400d8fe0 passes that address to FUN_140a98d50 and its decompilation prints the exact name and size 0xb8. The following `EntityPtrs` and `ConMstPtr` labels belong to serialized fields. The prior combined type label is superseded. The entity collection and exact ProcessTrapHit instance membership remain separate questions.
"""
    if "## Type-name correction from EV-0362" not in old_content:
        write(old_note, old_content + erratum)
    old_manifest = TX / "EV-0359-capture-manifest.json"
    old_manifest_data = json.loads(old_manifest.read_text(encoding="utf-8"))
    old_hashes = old_manifest_data.setdefault("registered_local_hashes", {})
    old_hashes[old_note.relative_to(ROOT).as_posix()] = sha(old_note)
    write(old_manifest, json.dumps(old_manifest_data, indent=2, ensure_ascii=False))

    note = TX / "EV-0362-note.md"
    manifest = TX / "EV-0362-capture-manifest.json"
    write(note, f"""# EV-0362 — hkpSimulationIsland owner table and type-name correction

## Build and method

Eight fresh identity-checked GOG AE 1.6.1179.0 queries used the existing project through the strict dispatcher in read-only/no-analysis mode. Four earlier captures are reused from EV-0359. Analysis binary SHA-256: {BINARY}. No GOG address is transferred to Steam AE 1.6.1170.0.

## Direct observations

- The type-name address at 0x1419775b0 is passed by FUN_1400d8fe0 to FUN_140a98d50; the decompilation renders it as `hkpSimulationIsland` and passes size 0xb8. The direct pointer-table scan shows the following data begins with the separate field label `EntityPtrs`; FUN_140b60780 references that label and `ConMstPtr`, `ConInstance`, and `ConData` [fresh captures 20261018T082215Z, 20261018T083331Z; reused capture 20261018T080431Z]. The earlier EV-0359 interpretation `hkpSimulationIslandAndEntity` combined adjacent bytes and is superseded by this direct name boundary.
- The consecutive function entries at table base RVA 0x1977588 are FUN_140b60780, FUN_140b60df0, FUN_140b60e10, FUN_140b60e30, and FUN_140b4c000 [fresh capture 20261018T082541Z]. Existing captures map b60780 to the field serializer; b60df0 to add-notification through b439a0; and b60e10 to its receiver+0x10 thunk into b439e0 [fresh capture 20261018T082215Z; reused captures 20261018T080106Z, 20261018T080209Z].
- FUN_140b60e30 only ORs a supplied byte into the payload flag at `*(param_2+0x60)+0x22`; the query finds no direct callers in the analyzed project [fresh capture 20261018T082317Z]. FUN_140b4c000 is an empty return function and has no direct call edges [fresh capture 20261018T082418Z].
- The serializer walks an entity pointer collection at object +0x60 with count +0x68; for each listed entity it walks the entity's +0x100/+0x108 constraint records and emits ConInstance/ConData fields. The whole-program scans count 14,003 (+0x60) and 8,295 (+0x68) matching accesses, but each prints only the first 2,048 and reports OFFSET_ACCESS_OUTPUT_LIMIT=2048. The printed ranges stop before the 0x140b physics functions, so these scans make no claim about writers to this owner [fresh captures 20261018T082702Z, 20261018T083000Z; tool source ReadOnlyTargetedQuery.java accessOutputLimit].
- A separate exact string search found no defined `hkpSimulationIslandAndEntity` string object [fresh capture 20261018T083226Z]. This result is supplementary; the correction rests on FUN_1400d8fe0's direct type-name argument.
- The table/serializer schema is not proof that the exact ProcessTrapHit-created hkpConstraintInstance is in this island's entity or constraint lists. No AV11/AV12 descendant is identified.

## Competing models and result

- Q64-H1 predicts the exact factory instance's eventual callbacks/members do not dispatch AV11/AV12 skill progress.
- Q64-H2 predicts a producer-backed callback/member target reaches Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.

The prior table type-name interpretation is corrected to `hkpSimulationIsland`. Its serializer exposes a plausible owner route through EntityPtrs to per-entity constraint records, but exact ProcessTrapHit object membership and skill descendants remain unresolved. The displacement scans do not provide a B-range writer result because of their output cap. Q64-H1/H2 stay proposed.

## Scope and exact next action

This is static GOG metadata, table, field-schema and operand-scan evidence only. It does not establish runtime membership, callback population, positive final damage, effective armor protection, raw AVSK, or Steam behavior. Trace the exact selected owner from FUN_140b678a0/FUN_140b43a20 into the hkpSimulationIsland EntityPtrs and its +0x100/+0x108 constraint records; if identity cannot be resolved, checkpoint the static lane and retain the matched Steam discriminator.
""")

    docs = {
        "README.md": "# EXP-0100 — island owner type correction\n\nResolve the type-name boundary around the hkpSimulationIsland function table, map its entity/constraint serializer, and test whether direct +0x60/+0x68 writers are visible.\n",
        "hypothesis.md": "# Competing models\n\n- Q64-H1: the ProcessTrapHit instance's owner and descendants do not dispatch AV11/AV12 skill progress.\n- Q64-H2: a producer-backed owner callback/member reaches AV11/AV12 progress.\n\nThe table name and field schema are not object-membership evidence.\n",
        "protocol.md": "# Protocol\n\nValidate exact GOG query identities and hashes; inspect the full function table, direct name reference, serializer labels, and direct displacement writers for owner +0x60/+0x68. Preserve the earlier misreading as an explicit correction rather than deleting provenance.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Resolve the exact owner pointer selected during hkpConstraintInstance attachment.\n2. Tie that pointer to an entry in hkpSimulationIsland EntityPtrs (+0x60/+0x68).\n3. Tie the exact constraint pointer to that entity's +0x100/+0x108 record.\n4. Follow producer-backed callback/member targets to AV11/AV12; table shape alone is inconclusive.\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- An exact factory-instance edge into an island entity and its constraint record enables callback/member tracing.\n- A producer-backed non-skill chain supports Q64-H1 only for the resolved route.\n- Unresolved entity-list writer or object identity leaves Q64-H1/H2 open.\n",
        "results.md": "# Results\n\nThe earlier `hkpSimulationIslandAndEntity` label was a boundary error. FUN_1400d8fe0 passes the exact name `hkpSimulationIsland`; adjacent bytes are separate field labels. Its table includes an entity/constraint serializer and add/remove callback bridges, but the exact ProcessTrapHit instance is not proven to enter the island list. Whole-program +0x60/+0x68 scans counted 14,003/8,295 accesses but printed only the first 2,048 each, ending before the 0x140b physics functions; no B-range writer conclusion follows [EV-0362].\n",
        "implications.md": "# Implications\n\nCorrecting the owner type improves caller attribution without resolving the runtime identity edge. Preserve the candidate serializer path and keep both AV11/AV12 models open.\n",
    }
    for name, content in docs.items():
        write(EXP / name, content)

    capture_rows = {}
    local_hashes = {}
    for stamp, (meta, meta_path, stdout_path, _) in {**fresh, **reused}.items():
        capture_rows[stamp] = {
            "query_mode": meta.get("query_mode"),
            "requested_rva": meta.get("requested_rva"),
            "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
            "requested_search_displacement": meta.get("requested_search_displacement"),
            "requested_string": meta.get("requested_string"),
            "checks": meta.get("checks"),
            "stdout_sha256": meta.get("stdout_sha256"),
            "stderr_sha256": meta.get("stderr_sha256"),
            "reused": stamp in reused,
        }
        for artifact in (meta_path, stdout_path, *(ROOT / p for p in meta["artifacts"].values())):
            if artifact.is_file():
                local_hashes[artifact.relative_to(ROOT).as_posix()] = sha(artifact)
    for artifact in (note, old_note, old_manifest, *EXP.iterdir(), Path(__file__)):
        if artifact.is_file():
            local_hashes[artifact.relative_to(ROOT).as_posix()] = sha(artifact)
    local_hashes.pop(manifest.relative_to(ROOT).as_posix(), None)
    write(manifest, json.dumps({
        "evidence_id": "EV-0362",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY,
        "corrects": "EV-0359 hkpSimulationIslandAndEntity interpretation",
        "captures": capture_rows,
        "displacement_scan_output": displacement_scan_output,
        "registered_local_hashes": local_hashes,
    }, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = sha(manifest)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0362" for item in evidence["items"]):
        raise SystemExit("EV-0362 already registered")
    old_ev = next(item for item in evidence["items"] if item.get("id") == "EV-0359")
    old_ev["sha256"] = sha(old_note)
    old_ev.setdefault("local_hashes", {})[old_note.relative_to(ROOT).as_posix()] = sha(old_note)
    old_ev["local_hashes"][old_manifest.relative_to(ROOT).as_posix()] = sha(old_manifest)
    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0362",
        "kind": "native",
        "source": "Identity-checked read-only GOG Ghidra table, type-name, serializer, and whole-program displacement traces; explicit correction to EV-0359's adjacent-byte interpretation.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0362-note.md",
        "sha256": sha(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
        "coverage": "The hkpSimulationIsland type-name address, adjacent method table, EntityPtrs/constraint serializer labels, paired +0x60/+0x68 direct displacement writer candidates, and correction of EV-0359 class-name parsing.",
        "result": "The exact referenced type-name is hkpSimulationIsland, not the previously combined hkpSimulationIslandAndEntity label. The island serializer traverses entity and per-entity constraint arrays; exact ProcessTrapHit instance membership remains unproven. Whole-program +0x60/+0x68 scans print only the first 2,048 accesses each and stop before the 0x140b physics functions, so they provide no B-range writer result.",
        "related_evidence": ["EV-0359", "EV-0360", "EV-0361", "EV-0358"],
        "local_hashes": local_hashes,
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    old_claim = "| CL-L198 | In GOG AE 1.6.1179.0, FUN_140b439e0 has three analyzed direct caller functions: an hkpConstraintChainInstance override, an hkpSimulationIslandAndEntity bridge, and a post-collision command-record loop. | supported for the mapped caller classes/records | [EV-0359], [EV-0358] | The factory-created hkpConstraintInstance is not tied to the island collection or type-1 record; runtime membership and callback/member descendants remain unresolved. |"
    corrected_claim = "| CL-L198 | In GOG AE 1.6.1179.0, FUN_140b439e0 has three analyzed direct caller functions: an hkpConstraintChainInstance override, an hkpSimulationIsland method-table path, and a post-collision command-record loop. EV-0362 corrects the earlier adjacent-byte interpretation of the island type name. | supported for the mapped caller functions and corrected type-name boundary | [EV-0359], [EV-0362], [EV-0358] | The factory-created hkpConstraintInstance is not tied to the island EntityPtrs/ConMstPtr entries or type-1 record; runtime membership and callback/member descendants remain unresolved. |"
    if old_claim not in claims:
        raise SystemExit("CL-L198 prior text not found for correction")
    claims = claims.replace(old_claim, corrected_claim)
    if "| CL-L201 |" in claims:
        raise SystemExit("CL-L201 already registered")
    write(claims_path, claims.rstrip() + "\n| CL-L201 | In GOG AE 1.6.1179.0, the referenced type-name adjacent to the owner method table is `hkpSimulationIsland`; its serializer enumerates EntityPtrs and each entity's +0x100/+0x108 constraint records. | supported for the static name/table/serializer path | [EV-0362], [EV-0359] | The exact ProcessTrapHit instance's membership in EntityPtrs or ConMstPtr is unresolved; no AV11/AV12 result follows. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8")
    prior = "FUN_140b439e0 is called through three routes: hkpConstraintChainInstance slot +0x8, hkpSimulationIslandAndEntity slot +0x8, and a type-1 post-collision command record. The chain override is a different vtable from the ProcessTrapHit factory class. The island/entity serializer exposes a constraint collection, and the post-collision record carries a data-selected pointer; neither is yet tied to the exact factory object. No AV11/AV12 conclusion follows [EV-0359], [EV-0356]. Claim CL-L198 -> M-0079."
    revised = "FUN_140b439e0 is called through three routes: hkpConstraintChainInstance table entry +0x8, the hkpSimulationIsland method-table cleanup entry, and a type-1 post-collision command record. EV-0362 corrects the earlier adjacent-byte interpretation of the island name. Its serializer enumerates EntityPtrs and per-entity constraint records; the exact factory object is not tied to those entries or the command record. No AV11/AV12 conclusion follows [EV-0359], [EV-0362], [EV-0356]. Claim CL-L198 -> M-0079."
    if prior not in mechanisms:
        raise SystemExit("M-0079 prior text not found for correction")
    mechanisms = mechanisms.replace(prior, revised)
    write(mechanisms_path, mechanisms.rstrip() + "\n\n## M-0082 — hkpSimulationIsland entity/constraint collection (Q-0064)\n\nThe direct type-name handoff identifies `hkpSimulationIsland` (size 0xb8) adjacent to a method table whose serializer enumerates EntityPtrs at +0x60/+0x68 and each listed entity's +0x100/+0x108 constraint records. The table also contains add/remove callback bridge functions. This supplies a candidate owner route for the ProcessTrapHit constraint, but exact entity membership and AV11/AV12 descendants are unresolved [EV-0362]. Claim CL-L201 -> M-0082.\n")

    contradiction_path = ROOT / "research/CONTRADICTIONS.md"
    contradiction = """

## C-OBJ2-HAVOK-ISLAND-TYPE-BOUNDARY — island owner type label versus adjacent field names

- **Model A:** the table owner is `hkpSimulationIslandAndEntity`, as the earlier EV-0359 note read the adjacent bytes.
- **Model B:** the referenced type-name is `hkpSimulationIsland`; `EntityPtrs` and `ConMstPtr` are following field labels.
- **Source:** table and caller capture [EV-0359], full table, direct type-name address/decompilation, serializer fields, and paired displacement scans [EV-0362].
- **Current assessment:** Model B is supported for the referenced name boundary. FUN_1400d8fe0 passes address 0x1419775b0 to FUN_140a98d50, whose decompilation prints `hkpSimulationIsland` and size 0xb8. EV-0359's prior combined label is superseded. The table's entity/constraint array schema is supported, but whether the exact ProcessTrapHit instance occupies it remains unresolved.
- **Discriminant:** trace the selected entity pointer from FUN_140b678a0/FUN_140b43a20 into the island EntityPtrs list and its per-entity ConMstPtr records. If static identity cannot be resolved, keep the owner route as a candidate and use the exact Steam matched hit/armor/raw-AVSK experiment.
"""
    contradiction_text = contradiction_path.read_text(encoding="utf-8")
    if "C-OBJ2-HAVOK-ISLAND-TYPE-BOUNDARY" not in contradiction_text:
        write(contradiction_path, contradiction_text.rstrip() + contradiction)

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    write(graph_path, graph_path.read_text(encoding="utf-8").rstrip() + "\n\nEV-0362 corrects the EV-0359 adjacent-byte class label to `hkpSimulationIsland` and maps its entity/constraint serializer. This correction adds no edge from the exact ProcessTrapHit instance to EntityPtrs/ConMstPtr or to Actor::UseSkill AV11/AV12; membership remains unresolved [CL-L198], [CL-L201].\n")

    roadmap_path = ROOT / "research/ROADMAP.md"
    write(roadmap_path, roadmap_path.read_text(encoding="utf-8").rstrip() + "\n\nEV-0362 corrects the island type label and maps EntityPtrs (+0x60/+0x68) to per-entity constraint records (+0x100/+0x108). Next trace the exact selected owner from FUN_140b678a0/FUN_140b43a20 into that list; the immediate displacement scans found no +0x60/+0x68 destination candidates in 0x140b-range bodies.\n")

    index_path = ROOT / "experiments/README.md"
    write(index_path, index_path.read_text(encoding="utf-8").rstrip() + "\n\nEXP-0100 / EV-0362 corrects the island owner type label and maps its serialized entity/constraint collections; factory-object membership remains unresolved.\n")

    action = "Trace whether the exact ProcessTrapHit-selected entity from FUN_140b678a0/FUN_140b43a20 enters hkpSimulationIsland EntityPtrs (+0x60/+0x68), then whether the exact constraint enters that entity's +0x100/+0x108 records; follow any producer-backed callback/member target to AV11/AV12 and preserve the Steam hit/protection/raw-AVSK discriminator."
    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    question = next(item for item in frontier["items"] if item.get("id") == "Q-0064")
    for bucket in [question.setdefault("evidence", []), *(hyp.setdefault("evidence", []) for hyp in question.get("hypotheses", []))]:
        if "EV-0362" not in bucket:
            bucket.append("EV-0362")
    if "CL-L201" not in question.setdefault("linked_claims", []):
        question["linked_claims"].append("CL-L201")
    question["next_action"] = action
    frontier_path.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    checkpoint_path = ROOT / "experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"
    checkpoint = checkpoint_path.read_text(encoding="utf-8")
    needle = "- Q-0064 / EV-0361 maps the exact add/remove callback consumer slots and two add-wrapper caller functions; the hkpConstraintListener string has no analyzed references and no producer/class is identified.\n"
    addition = "- Q-0064 / EV-0362 corrects the owner name to hkpSimulationIsland and maps its EntityPtrs-to-constraint serializer; exact factory-object membership remains unresolved.\n"
    if needle not in checkpoint:
        raise SystemExit("checkpoint helper lacks EV-0361 summary line")
    checkpoint = checkpoint.replace(needle, needle + addition)
    checkpoint = checkpoint.replace(
        "trace exact-instance membership through island/entity and type-1 command routes, then resolve producer-backed callback/member descendants against AV11/AV12.",
        "trace whether the exact selected entity enters hkpSimulationIsland EntityPtrs and whether its exact constraint enters ConMstPtr; then follow producer-backed callbacks/members to AV11/AV12.",
    )
    checkpoint = checkpoint.replace(
        "resolve exact +0x40/+0x48 callback writers/classes and follow attach/remove callback and member descendants against AV11/AV12.",
        "trace whether the exact selected entity enters hkpSimulationIsland EntityPtrs and whether its exact constraint enters ConMstPtr; then follow producer-backed callbacks/members to AV11/AV12.",
    )
    checkpoint_path.write_text(checkpoint, encoding="utf-8")
    print("registered EV-0362 / CL-L201 / M-0082; corrected EV-0359 type label; Q-0064 remains active")


if __name__ == "__main__":
    main()
