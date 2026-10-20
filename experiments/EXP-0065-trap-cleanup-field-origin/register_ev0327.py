#!/usr/bin/env python3
"""Register Q-0064's bounded read-only GOG cleanup follow-up captures."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GHIDRA = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
BINARY_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"

# One bad RVA and one query with no indexed slot xref are retained and labeled.
CAPTURES = [
    ("225608", "address_context_query", "requested_address_rva", "0x7305EA", ["address_rva_requested", "address_in_program_memory", "address_context_complete", "script_no_error"], "ok"),
    ("225820", "address_context_query", "requested_address_rva", "0x130FEBF8", ["address_rva_requested", "script_no_error"], "bad_rva"),
    ("225929", "address_context_query", "requested_address_rva", "0x30FEBF8", ["address_rva_requested", "address_in_program_memory", "address_context_complete", "script_no_error"], "ok"),
    ("230102", "direct_call_edge_census", "requested_rva", "0x72ED70", ["function_lookup", "direct_call_edge_scan", "disassembly", "decompilation", "script_no_error"], "ok"),
    ("230228", "direct_call_edge_census", "requested_rva", "0x8E3F50", ["function_lookup", "direct_call_edge_scan", "disassembly", "decompilation", "script_no_error"], "ok"),
    ("230404", "pointer_table_query", "requested_pointer_table_rva", "0x18F0628", ["pointer_table_requested", "pointer_table_scan_complete", "pointer_table_xref_scan_complete", "script_no_error"], "ok"),
    ("230520", "direct_call_edge_census", "requested_rva", "0x8E8B50", ["function_lookup", "direct_call_edge_scan", "disassembly", "decompilation", "script_no_error"], "ok"),
    ("230645", "direct_call_edge_census", "requested_rva", "0x8E4070", ["function_lookup", "direct_call_edge_scan", "disassembly", "decompilation", "script_no_error"], "ok"),
    ("230849", "memory_displacement_search", "requested_search_displacement", "0x730", ["requested_displacement", "displacement_scan_complete", "writer_analysis_complete", "computed_writer_analysis_complete", "script_no_error"], "ok"),
    ("231250", "direct_call_edge_census", "requested_rva", "0x7373E0", ["function_lookup", "direct_call_edge_scan", "disassembly", "decompilation", "script_no_error"], "ok"),
    ("231531", "pointer_table_query", "requested_pointer_table_rva", "0x18AD228", ["pointer_table_requested", "pointer_table_scan_complete", "pointer_table_xref_scan_complete", "script_no_error"], "ok"),
    ("231643", "address_context_query", "requested_address_rva", "0x18AD220", ["address_rva_requested", "address_in_program_memory", "address_context_complete", "script_no_error"], "ok"),
    ("231756", "pointer_table_query", "requested_pointer_table_rva", "0x18AD220", ["pointer_table_requested", "pointer_table_scan_complete", "pointer_table_xref_scan_complete", "script_no_error"], "ok"),
    ("232152", "direct_call_edge_census", "requested_rva", "0x665950", ["function_lookup", "direct_call_edge_scan", "disassembly", "decompilation", "script_no_error"], "ok"),
    ("232342", "function_query", "requested_rva", "0x18ACD70", ["function_lookup", "vtable_slot_lookup", "disassembly", "decompilation", "script_no_error"], "slot_xref_limited"),
    ("232504", "memory_displacement_search", "requested_search_displacement", "0x4C0", ["requested_displacement", "displacement_scan_complete", "writer_analysis_complete", "computed_writer_analysis_complete", "script_no_error"], "ok"),
    ("232721", "direct_call_edge_census", "requested_rva", "0x737930", ["function_lookup", "direct_call_edge_scan", "disassembly", "decompilation", "script_no_error"], "ok"),
    ("232915", "direct_call_edge_census", "requested_rva", "0x75ECA0", ["function_lookup", "direct_call_edge_scan", "disassembly", "decompilation", "script_no_error"], "ok"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0327" for row in evidence["items"]):
        raise SystemExit("EV-0327 already exists; refusing duplicate registration")

    query_rows: list[dict] = []
    hashes: dict[str, str] = {}
    for stamp, mode, key, requested, required, status in CAPTURES:
        meta_path = GHIDRA / f"gog-query-20261017T{stamp}Z.meta.json"
        if not meta_path.is_file():
            raise SystemExit(f"missing metadata: {meta_path.name}")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        checks = meta.get("checks", {})
        if (
            meta.get("analysis_binary_sha256") != BINARY_SHA
            or meta.get("analysis_distribution") != "GOG"
            or meta.get("exit_code") != 0
            or meta.get("query_mode") != mode
            or meta.get(key) != requested
            or meta.get("read_only") is not True
            or meta.get("auto_analysis_disabled") is not True
            or meta.get("import_attempted") is not False
            or meta.get("overwrite_attempted") is not False
            or checks.get("program_identity_matches_gog_binary") is not True
        ):
            raise SystemExit(f"GOG identity/query mismatch: {stamp}")
        for name in required:
            expected = False if status == "bad_rva" and name == "address_in_program_memory" else True
            if checks.get(name) is not expected:
                raise SystemExit(f"unexpected {name} result for {stamp}: {checks.get(name)!r}")
        if status == "bad_rva":
            if checks.get("address_in_program_memory") is not False or meta.get("ok") is not False:
                raise SystemExit(f"bad RVA did not fail as expected: {stamp}")
        elif status == "slot_xref_limited":
            if meta.get("requested_vtable_slot") != "0x98" or checks.get("xref_call_edge") is not False or meta.get("ok") is not False:
                raise SystemExit("slot query limitation changed unexpectedly")
        elif meta.get("ok") is not True or checks.get("script_no_error") is not True:
            raise SystemExit(f"query not ok: {stamp}")

        files = {"metadata": meta_path}
        for artifact_kind, relative in meta.get("artifacts", {}).items():
            path = ROOT / relative
            if not path.is_file():
                raise SystemExit(f"missing {artifact_kind} capture: {relative}")
            files[artifact_kind] = path
        hashes.update({p.relative_to(ROOT).as_posix(): sha(p) for p in files.values()})
        query_rows.append({
            "stamp": stamp,
            "query_mode": mode,
            "request": {key: requested, **({"requested_vtable_slot": "0x98"} if status == "slot_xref_limited" else {})},
            "checks": checks,
            "ok": meta.get("ok"),
            "diagnostic": "bad RVA; excluded from positive claims" if status == "bad_rva" else (
                "vtable slot and body checks pass; no indexed code xref" if status == "slot_xref_limited" else None
            ),
            "stdout_sha256": meta.get("stdout_sha256"),
            "stderr_sha256": meta.get("stderr_sha256"),
            "adapter_sha256": meta.get("adapter_sha256"),
            "query_script_sha256": meta.get("query_script_sha256"),
        })

    tx_dir = TX
    note = tx_dir / "EV-0327-note.md"
    write(note, f"""# EV-0327 — PlayerCharacter cleanup field and camera callback follow-up

## Build identity and scope

The queried program is the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, executable SHA-256 `{BINARY_SHA}`. All 18 requests used the strict read-only adapter with automatic analysis disabled. Metadata, stdout, stderr, headless logs, and script logs are hashed in the manifest. One bad-address request (`0x130FEBF8` treated as an RVA) is retained for provenance and excluded from positive claims. The exact PlayerCharacter vtable slot query reports no indexed code xref; its slot lookup, target function, disassembly, and decompilation checks passed.

## Direct observations

1. The PlayerCharacter teardown site's slot-0 call at RVA `0x730282` uses global pointer `0x1430FEBF8` (RVA `0x30FEBF8`). The corrected query reports 218 references, including six writes. Setup `FUN_14072ed70` lazily initializes the global through `FUN_1408e3f50`; that factory writes `PlayerCamera::vftable` at RVA `0x18F0628`. Slot 0 resolves to `FUN_1408e8b50`, which calls cleanup `FUN_1408e4070`.
2. `FUN_1408e4070` has five indirect resource calls. Its captured body has no direct edge to the mapped skill-progress routine, but those indirect targets and descendants remain unresolved.
3. EV-0261 maps the primary PlayerCharacter vtable to GOG RVA `0x18ACD70`. The exact slot query resolves byte offset `+0x4C0` (slot `0x98`) to `FUN_1407373e0`. This method reads `PlayerCharacter+0x730` (`param_1[0xE6]`); on its null-second-argument branch it may call inner-interface slot `+0x1C0` through the field object's `+0x30`, clears the field, and conditionally invokes the object's refcount-final slot `+0x8`.
4. `FUN_140737930` is the captured cell/location transition helper context for `FUN_1407373e0`; its direct callers are `FUN_140743ab0` and `FUN_140734890`. The complete `+0x730` scan reports 67 operands, 13 writer functions, and complete direct/computed writer analysis. On PlayerCharacter-attributed accesses it found null initialization and clearing but no non-null direct or computed writer. The same displacement occurs in unrelated structures, so unattributed matches are excluded.
5. `FUN_14075eca0`, called by setup and cleanup, is a thread-safe static-local initializer for separate storage and does not provide the missing `+0x730` producer. A pointer subrange at RVA `0x18AD228` was not the primary PlayerCharacter vtable base; the exact table base and slot mapping are EV-0261 plus this query.

## Assessment and limits

This resolves the PlayerCharacter global slot-0 callback to a PlayerCamera cleanup path and maps the `+0x730` cleanup to primary PlayerCharacter slot `0x98`. It narrows Q-0064 but does not prove that the teardown route cannot award AV11/AV12: the non-null origin and dynamic type of `+0x730`, its inner slot `+0x1C0` target, five PlayerCamera cleanup indirect sites, and four other PlayerCharacter final-release fields remain unresolved. Alias or whole-object-copy writes are not excluded. No Steam runtime result, profile winner, positive damage, effective protection, or vanilla reproduction is established. The next discriminant is to attribute writers/readers for PlayerCharacter fields `+0x9D0`, `+0x9A8`, `+0x9A0`, and `+0x8F8`, then type only observed producer paths.

No causal edge to OBJ-1 is supported. This remains an OBJ-2 mechanism investigation.
""")
    hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    manifest_path = tx_dir / "EV-0327-capture-manifest.json"
    write(manifest_path, json.dumps({
        "evidence_id": "EV-0327",
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "analysis_binary": {"product_version": "1.6.1179.0", "distribution": "GOG", "sha256": BINARY_SHA},
        "project_mode": {"existing_project": True, "read_only": True, "auto_analysis_disabled": True, "import_attempted": False, "overwrite_attempted": False},
        "capture_count": len(query_rows),
        "queries": query_rows,
        "private_hashes": hashes,
        "limitations": ["Bad RVA request is diagnostic only.", "Slot 0x98 has a valid target despite no indexed code xref.", "No GOG RVA is transferred to Steam.", "The +0x730 producer/type and inner slot +0x1C0 remain unknown.", "Five PlayerCamera cleanup indirects and four other PlayerCharacter release fields remain unresolved."],
    }, indent=2, ensure_ascii=False))
    hashes[manifest_path.relative_to(ROOT).as_posix()] = sha(manifest_path)

    exp = ROOT / "experiments/EXP-0065-trap-cleanup-field-origin"
    write(exp / "README.md", """# EXP-0065 — Trap cleanup field origin and callback typing

This bounded static follow-up to Q-0064 traces the PlayerCharacter cleanup global slot-0 callback, confirms primary vtable slot `0x98`, and searches the complete GOG operand space for writers of `+0x730`. It does not transfer GOG addresses to Steam or claim a gameplay result. EV-0327 and the exact raw-capture manifest are registered in the ledgers; raw files remain in ignored `.local/`.
""")
    write(exp / "hypothesis.md", """# Competing models

Q-0064 remains open.

- **H1:** relevant teardown descendants do not award AV11/AV12 skill progress. Prediction: resolved targets and arguments avoid Actor::UseSkill slot `0xF7` and the mapped skill sink.
- **H2:** at least one teardown callback can route AV11/AV12 into skill progress. Prediction: a concrete descendant reaches that sink with AV11 or AV12.

An unresolved field producer or generic indirect call is inconclusive. A missing direct/computed writer does not exclude alias or whole-object-copy propagation.
""")
    write(exp / "protocol.md", """# Protocol

Query only the configured GOG AE 1.6.1179.0 Ghidra project through `tools/ghidra_probe.py` and the strict dispatcher with `-noanalysis -readOnly`. Verify the binary SHA-256 in every metadata record. Hash stdout, stderr, logs, and metadata. Trace only observed table/function targets. Label bad requests as diagnostics; never reinterpret GOG RVAs as Steam AE 1.6.1170.0 addresses. No live-game mutation or altered plugin is part of this static work.
""")
    write(exp / "predicted-outcomes.md", """# Predicted outcomes

- **H1:** concrete teardown targets and ActorValue arguments resolve away from AV11/AV12 sinks; unresolved branches remain listed.
- **H2:** a concrete callback descendant reaches the mapped skill sink with AV11 or AV12.
- **Inconclusive:** dynamic types, field producers, or indirect descendants stay unresolved. EV-0327 is inconclusive for Q-0064 overall.
""")
    write(exp / "results.md", """# Results — PlayerCharacter cleanup field and camera callback

EV-0327 resolves the PlayerCharacter teardown's global slot-0 callback through `PlayerCamera::vftable` to `FUN_1408e8b50` -> `FUN_1408e4070`. The camera cleanup body retains five indirect resource calls. The primary PlayerCharacter vtable query maps slot `0x98` (byte offset `+0x4C0`) to `FUN_1407373e0`; its cell/location transition path reads/clears `PlayerCharacter+0x730`, may call inner slot `+0x1C0`, and conditionally releases through slot `+0x8`.

The complete GOG `+0x730` displacement scan reports 67 operands, 13 writer functions, and complete direct/computed writer analysis. Attributed PlayerCharacter paths show null initialization and clearing; no non-null direct or computed writer was identified. Alias/copy writes and the field's dynamic type remain unknown. The same displacement occurs on unrelated structures.

Q-0064 H1/H2 remain unresolved. The inner target, five PlayerCamera indirect sites, and four other PlayerCharacter final-release fields remain open. No Steam runtime, positive-damage/protection result, or raw AVSK capture exists [EV-0327], [EV-0325], [EV-0319], [EV-0324], [EV-0261], [EV-0260].
""")
    write(exp / "implications.md", """# Implications

EV-0327 narrows Q-0064 but does not eliminate hidden skill progress. Next, scan PlayerCharacter final-release fields `+0x9D0`, `+0x9A8`, `+0x9A0`, and `+0x8F8` for receiver-attributed writers/readers; then query the strongest observed producer and dynamic type. Keep both Q64 models proposed while the `+0x730` object and PlayerCamera indirect descendants remain unresolved. No cross-objective edge to OBJ-1 is supported. Steam protection and raw AVSK measurements remain required under EV-0260.
""")
    for path in exp.iterdir():
        if path.is_file():
            hashes[path.relative_to(ROOT).as_posix()] = sha(path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "edition": "AE", "modified_state": False,
        "id": "EV-0327", "kind": "native",
        "source": "Fresh GOG SkyrimSE.exe v1.6.1179.0 read-only Ghidra queries for PlayerCharacter +0x730, primary-vtable slot 0x98, PlayerCamera global callback, and cleanup descendants.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0327-note.md", "sha256": sha(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 project; analysis binary SHA-256 {BINARY_SHA}. Steam AE 1.6.1170.0 is separate.",
        "lane": "mechanism_inference", "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly", "EV-0261 pinned PlayerCharacter vtable mapping"],
        "coverage": "18 query requests: full +0x730 scan, exact PC slot 0x98 lookup, global camera factory/slot-0 trace, transition caller context, initializer trace; bad-RVA request retained as diagnostic only.",
        "result": "The global slot-0 callback resolves to PlayerCamera cleanup, which retains five indirect resource calls. Primary PC slot 0x98 targets FUN_1407373e0, a transition method that reads/clears +0x730 and may dispatch inner slot +0x1C0. The complete scan found no non-null direct/computed PlayerCharacter +0x730 writer; alias/copy writes remain possible. Q-0064 hypotheses remain unresolved.",
        "related_evidence": ["EV-0325", "EV-0319", "EV-0324", "EV-0261", "EV-0260"], "local_hashes": hashes,
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L158 |" in claims or "| CL-L159 |" in claims:
        raise SystemExit("CL-L158/CL-L159 already exists; refusing duplicate claims")
    write(claims_path, claims.rstrip() + """
| CL-L158 | In GOG AE 1.6.1179.0, the primary PlayerCharacter vtable at RVA `0x18ACD70` maps slot `0x98` to `FUN_1407373e0`, whose cell/location transition path reads and clears field `+0x730`, may dispatch through an inner interface at `+0x1C0`, and conditionally releases the object through slot `+0x8`. The complete `+0x730` scan found no non-null direct or computed PlayerCharacter writer; alias or whole-object-copy writes remain possible. | supported (bounded build-attested vtable and complete displacement scan) | [EV-0327], [EV-0261] | The field's producer and dynamic type, inner slot target, skill-sink reachability, Steam behavior, and armor-XP result remain unknown. No OBJ-1 edge is supported. |
| CL-L159 | In GOG AE 1.6.1179.0, the PlayerCharacter cleanup's global slot-0 call uses a global initialized through `FUN_1408e3f50` with `PlayerCamera::vftable`; slot 0 resolves to `FUN_1408e8b50`, which calls `FUN_1408e4070`. The camera cleanup body has five indirect resource calls and no direct mapped skill-progress edge in the captured census. | supported (bounded build-attested global, vtable, and cleanup trace) | [EV-0327], [EV-0325] | The five indirect targets and descendants remain unresolved; this is not evidence of a complete no-award path. No Steam behavior or vanilla reproduction is established. No OBJ-1 edge is supported. |
""")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8").rstrip() + """

## M-0055 — PlayerCharacter cell-change cleanup of `+0x730` (Q-0064)

Primary PlayerCharacter vtable slot `0x98` at GOG RVA `0x18ACD70` resolves to `FUN_1407373e0`. Its transition path reads field `+0x730`, may invoke inner slot `+0x1C0`, clears the field, and conditionally invokes refcount-final slot `+0x8` [EV-0327]. Complete displacement and writer analysis found no non-null direct/computed PlayerCharacter writer; alias/copy propagation remains untested. Field type and skill-award reachability remain unresolved. No OBJ-1 edge is supported. Claim CL-L158 -> M-0055.

## M-0056 — PlayerCharacter global callback reaches PlayerCamera cleanup (Q-0064)

The PlayerCharacter cleanup's global slot-0 callback uses the global initialized through `FUN_1408e3f50` with a `PlayerCamera::vftable` object. Slot 0 targets `FUN_1408e8b50` -> `FUN_1408e4070`; that cleanup body retains five indirect resource calls and has no direct mapped skill-progress edge in the captured census [EV-0327], [EV-0325]. Dynamic targets and descendants remain unresolved. No OBJ-1 edge is supported. Claim CL-L159 -> M-0056.
"""
    write(mechanisms_path, mechanisms)

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    graph = graph_path.read_text(encoding="utf-8").rstrip() + """

EV-0327 adds two bounded OBJ-2 cleanup observations. PlayerCharacter primary slot `0x98` -> `FUN_1407373e0` reads/clears `+0x730`, may call nested slot `+0x1C0`, and releases through slot `+0x8`; the complete direct/computed scan found no non-null PlayerCharacter writer, leaving producer/type unknown. The teardown global slot-0 dispatch resolves through `PlayerCamera::vftable` to `FUN_1408e8b50` -> `FUN_1408e4070`, whose five indirect resource calls remain unresolved. These observations narrow Q-0064 but do not establish a no-award or positive-award result. Claims CL-L158 -> M-0055 and CL-L159 -> M-0056; Q-0064 remains active. No OBJ-1 edge is supported [EV-0327].
"""
    write(graph_path, graph)

    contradiction_path = ROOT / "research/CONTRADICTIONS.md"
    contradictions = contradiction_path.read_text(encoding="utf-8")
    heading = "## C-OBJ2-TRAP-DIRECT-ROUTE"
    start = contradictions.find(heading)
    end = contradictions.find("\n## ", start + len(heading))
    if start < 0:
        raise SystemExit("missing C-OBJ2-TRAP-DIRECT-ROUTE")
    if end < 0:
        end = len(contradictions)
    section = contradictions[start:end]
    if "[EV-0327]" not in section:
        section = section.replace("[EV-0325], [EV-0324]", "[EV-0327], [EV-0325], [EV-0324]", 1)
        section = section.replace(
            "Model A is supported as a bounded GOG 1.6.1179.0 path comparison; Model B remains unresolved because FUN_1406b9df0 has 28 indirect sites and no matched live Steam result.",
            "Model A is supported as a bounded GOG 1.6.1179.0 path comparison. EV-0327 resolves the PlayerCharacter global callback to PlayerCamera cleanup, which retains five indirect calls; the primary PlayerCharacter slot 0x98 also reads/clears +0x730, whose producer and dynamic type remain unknown. Model B remains unresolved because the main receiver has 28 indirect sites, teardown descendants remain open, and no matched live Steam result exists."
        )
        write(contradiction_path, contradictions[:start] + section + contradictions[end:])

    index_path = ROOT / "experiments/README.md"
    write(index_path, index_path.read_text(encoding="utf-8").rstrip() + "\n\n`EXP-0065` / EV-0327 follows Q-0064's PlayerCharacter cleanup global to PlayerCamera teardown, maps primary slot 0x98 to the transition handler for +0x730, and records the complete direct/computed writer scan with unknown origin/type limits. Indirect descendants and Steam protection/AVSK behavior remain unresolved.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0327"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L158", "CL-L159"]))
    item["methods"].append("Use EV-0327's exact slot and complete +0x730 scan as baseline; attribute writers/readers for remaining PlayerCharacter final-release fields +0x9D0, +0x9A8, +0x9A0, and +0x8F8 before expanding descendants.")
    item["next_action"] = "Scan PlayerCharacter final-release fields +0x9D0, +0x9A8, +0x9A0, and +0x8F8 through the complete read-only GOG displacement route; identify receiver-attributed writers, then query the strongest observed producer/type path. Keep Q64-H1/H2 proposed while the +0x730 object and PlayerCamera indirect descendants remain unresolved."
    frontier["session_next_action"] = item["next_action"]
    frontier["next_action"] = item["next_action"]
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    print(f"registered EV-0327 from {len(query_rows)} read-only GOG query requests")
    print(f"note sha256={sha(note)}; manifest sha256={sha(manifest_path)}")


if __name__ == "__main__":
    main()
