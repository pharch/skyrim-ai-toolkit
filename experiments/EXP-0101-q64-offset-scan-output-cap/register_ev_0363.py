#!/usr/bin/env python3
"""Correct EV-0362's interpretation of output-capped Ghidra displacement scans."""
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
SCANS = {
    "20261018T082702Z": {"displacement": "0x60", "total": 14003},
    "20261018T083000Z": {"displacement": "0x68", "total": 8295},
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def checked(stamp: str, expected: dict[str, str | int]):
    meta_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    raw_path = ROOT / meta["artifacts"]["stdout"]
    raw = raw_path.read_text(errors="replace")
    checks = meta.get("checks", {})
    valid = (
        meta.get("analysis_distribution") == "GOG"
        and meta.get("analysis_binary_product_version") == "1.6.1179"
        and meta.get("analysis_binary_sha256") == BINARY
        and meta.get("requested_search_displacement") == expected["displacement"]
        and meta.get("exit_code") == 0
        and meta.get("ok") is True
        and meta.get("read_only") is True
        and meta.get("auto_analysis_disabled") is True
        and meta.get("import_attempted") is False
        and meta.get("overwrite_attempted") is False
        and checks.get("program_identity_matches_gog_binary") is True
        and checks.get("displacement_scan_complete") is True
        and checks.get("writer_analysis_complete") is True
        and checks.get("script_no_error") is True
        and all(checks.values())
        and sha(raw_path) == meta.get("stdout_sha256")
    )
    markers = [
        f"OFFSET_QUERY={expected['displacement']}",
        f"OFFSET_ACCESS_COUNT={expected['total']}",
        "OFFSET_ACCESSES_PRINTED=2048",
        "OFFSET_ACCESS_OUTPUT_LIMIT=2048",
        "OFFSET_WRITER_FUNCTION_OUTPUT_LIMIT=16",
        "OFFSET_COMPUTED_WRITER_FUNCTION_OUTPUT_LIMIT=8",
    ]
    missing = [marker for marker in markers if marker not in raw]
    if not valid or missing:
        raise SystemExit(f"scan identity/cap check failed: {stamp}; missing={missing}")
    lines = [line for line in raw.splitlines() if "OFFSET_ACCESS=address:" in line]
    if len(lines) != 2048:
        raise SystemExit(f"printed access count mismatch: {stamp}: {len(lines)}")
    last = re.search(r"address:([^ ]+)", lines[-1])
    return {
        "meta": meta,
        "meta_path": meta_path,
        "raw_path": raw_path,
        "raw": raw,
        "displacement": expected["displacement"],
        "printed_accesses": len(lines),
        "total_matching_accesses": expected["total"],
        "last_printed_address": last.group(1) if last else "unknown",
        "stdout_sha256": meta["stdout_sha256"],
        "query_script_sha256": meta["query_script_sha256"],
    }


def main() -> None:
    scans = {stamp: checked(stamp, spec) for stamp, spec in SCANS.items()}
    query_source = ROOT / "tools/ghidra_scripts/ReadOnlyTargetedQuery.java"
    source = query_source.read_text(encoding="utf-8")
    source_marker = "final int accessOutputLimit = 2048;"
    if source_marker not in source:
        raise SystemExit("Ghidra query source no longer has the audited 2048 access output limit")
    query_source_hash = sha(query_source)
    if any(item["meta"].get("query_script_sha256") != query_source_hash for item in scans.values()):
        raise SystemExit("scan metadata query-script hash does not match the audited source")

    note = TX / "EV-0363-note.md"
    manifest = TX / "EV-0363-capture-manifest.json"
    stats = "\n".join(
        f"- Displacement {spec['displacement']}: {spec['total_matching_accesses']:,} total matching accesses; "
        f"2,048 printed; output limit 2,048; last printed instruction address {spec['last_printed_address']}."
        for _, spec in scans.items()
    )
    write(note, f"""# EV-0363 — displacement-scan output-cap correction

## Source and exact capture scope

This is a read-only audit of EV-0362's already captured GOG AE 1.6.1179.0 scans. The scan metadata confirms completion for each whole-program query. The raw output and `tools/ghidra_scripts/ReadOnlyTargetedQuery.java` are checked directly; the source sets `accessOutputLimit = 2048`, and each raw capture reports `OFFSET_ACCESS_OUTPUT_LIMIT=2048`. The script also caps detailed writer functions at 16 and computed-writer functions at 8. The query source SHA-256 is {query_source_hash}.

## Direct observations

{stats}

The full scans counted all matching operands, but the recorded instruction-level list ends before the 0x140b physics code. The first 2,048 printed accesses cannot establish whether later addresses contain +0x60/+0x68 writes. The detailed writer-function outputs are also capped. The prior EV-0362 sentence claiming zero 0x140b-range writers was unsupported and is withdrawn; no writer negative follows from these captures.

This correction does not affect EV-0362's independently supported type-name boundary (`hkpSimulationIsland`), table entries, or serializer field observations. Exact ProcessTrapHit owner/constraint membership and AV11/AV12 descendants remain unresolved.

## Exact next action

Trace the exact selected entity from FUN_140b678a0/FUN_140b43a20 into hkpSimulationIsland EntityPtrs (+0x60/+0x68), then its exact constraint through +0x100/+0x108 records. For a targeted writer search, first identify a producer or helper from that data flow; do not reuse the truncated broad list as a negative.
""")

    # Correct the earlier evidence note while retaining an explicit audit trail.
    ev0362_note = TX / "EV-0362-note.md"
    content = ev0362_note.read_text(encoding="utf-8")
    bad_fragment = "A direct-destination filter of the completed whole-program displacement scans returned 0 candidate writes in 0x140b-range functions for immediate +0x60 and 0 for immediate +0x68 [fresh captures 20261018T082702Z, 20261018T083000Z]. Generic array helpers, computed addressing and writers outside that address range remain possible."
    corrected_fragment = (
        "The whole-program scans count 14,003 (+0x60) and 8,295 (+0x68) matching accesses, but each prints only the first 2,048 and reports OFFSET_ACCESS_OUTPUT_LIMIT=2048. The printed ranges stop before the 0x140b physics functions, so these scans make no claim about writers to this owner [fresh captures 20261018T082702Z, 20261018T083000Z; output cap in ReadOnlyTargetedQuery.java]."
    )
    if bad_fragment in content:
        content = content.replace(bad_fragment, corrected_fragment)
    if "## Scan-output correction from EV-0363" not in content:
        content += """

## Scan-output correction from EV-0363

The previous note's statement that zero immediate +0x60/+0x68 destination writes occurred in 0x140b-range functions was unsupported. Each complete whole-program scan printed only the first 2,048 of 14,003 or 8,295 matching accesses, ending before that range. The writer and receiver question remains open.
"""
    write(ev0362_note, content)

    exp0100 = ROOT / "experiments/EXP-0100-q64-island-owner-type-correction"
    results_path = exp0100 / "results.md"
    results = results_path.read_text(encoding="utf-8")
    results = results.replace(
        "Whole-program +0x60/+0x68 scans returned no immediate writes in 0x140b-range bodies; shared helpers/computed addressing remain possible [EV-0362].",
        "Whole-program +0x60/+0x68 scans counted 14,003/8,295 accesses but printed only the first 2,048 each, stopping before the 0x140b physics functions; no B-range writer conclusion follows [EV-0362], [EV-0363].",
    )
    write(results_path, results)

    ev0362_manifest_path = TX / "EV-0362-capture-manifest.json"
    ev0362_manifest = json.loads(ev0362_manifest_path.read_text(encoding="utf-8"))
    ev0362_manifest.pop("b_range_direct_write_candidates_by_displacement", None)
    ev0362_manifest["displacement_scan_output"] = {
        key: {
            "total_matching_accesses": item["total_matching_accesses"],
            "printed_accesses": item["printed_accesses"],
            "output_limit": 2048,
            "last_printed_address": item["last_printed_address"],
            "b_range_writer_result": "unresolved because the printed access list stops before 0x140b",
        }
        for key, item in (("0x60", scans["20261018T082702Z"]), ("0x68", scans["20261018T083000Z"]))
    }
    ev0362_hashes = ev0362_manifest.setdefault("registered_local_hashes", {})
    ev0362_hashes[ev0362_note.relative_to(ROOT).as_posix()] = sha(ev0362_note)
    ev0362_hashes[results_path.relative_to(ROOT).as_posix()] = sha(results_path)
    ev0362_script = exp0100 / "register_ev_0362.py"
    ev0362_hashes[ev0362_script.relative_to(ROOT).as_posix()] = sha(ev0362_script)
    write(ev0362_manifest_path, json.dumps(ev0362_manifest, indent=2, ensure_ascii=False))

    docs = {
        "README.md": "# EXP-0101 — displacement scan output cap\n\nAudit the output cap on EV-0362's completed whole-program +0x60/+0x68 scans and withdraw any negative conclusion beyond the printed range.\n",
        "hypothesis.md": "# Competing interpretations\n\n- Model A: the completed whole-program count plus a missing printed candidate proves no owner-field writer exists.\n- Model B: the full operand count is complete, but the first-2,048 print cap prevents checking later physics addresses.\n\nThe raw completion marker and output-cap marker discriminate these readings.\n",
        "protocol.md": "# Protocol\n\nValidate GOG metadata, raw access counts, printed counts, cap markers, last printed addresses, and the exact query-source limit. Correct EV-0362's note, result and registered hashes; retain the prior assertion as an explicit correction.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. `OFFSET_ACCESS_COUNT` records the full scan total.\n2. `OFFSET_ACCESSES_PRINTED` and `OFFSET_ACCESS_OUTPUT_LIMIT` bound the visible candidate list.\n3. If the printed range ends before 0x140b, no B-range writer negative can be drawn.\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- A printed list that includes the target range allows candidate filtering within its stated limits.\n- A printed list capped before the target range leaves writer status unresolved despite complete scan counts.\n",
        "results.md": "# Results\n\nBoth broad scans completed their whole-program count, but each emitted only 2,048 access lines and stopped before the 0x140b physics range. The previous EV-0362 no-writer statement is withdrawn; no negative about the island fields follows [EV-0363].\n",
        "implications.md": "# Implications\n\nThe owner-list writer remains an actionable static question. Use exact producer lineage or a targeted query whose visible range includes the candidate functions.\n",
    }
    for name, body in docs.items():
        write(EXP / name, body)

    capture_hashes = {query_source.relative_to(ROOT).as_posix(): query_source_hash}
    captures = {}
    for stamp, item in scans.items():
        meta = item["meta"]
        captures[stamp] = {
            "query_mode": meta.get("query_mode"),
            "requested_search_displacement": meta.get("requested_search_displacement"),
            "total_matching_accesses": item["total_matching_accesses"],
            "printed_accesses": item["printed_accesses"],
            "output_limit": 2048,
            "last_printed_address": item["last_printed_address"],
            "stdout_sha256": item["stdout_sha256"],
            "query_script_sha256": item["query_script_sha256"],
            "checks": meta.get("checks"),
        }
        for p in (item["meta_path"], item["raw_path"]):
            capture_hashes[p.relative_to(ROOT).as_posix()] = sha(p)
    for p in (note, ev0362_note, ev0362_manifest_path, results_path, ev0362_script, *EXP.iterdir(), Path(__file__)):
        if p.is_file():
            capture_hashes[p.relative_to(ROOT).as_posix()] = sha(p)
    capture_hashes.pop(manifest.relative_to(ROOT).as_posix(), None)
    write(manifest, json.dumps({
        "evidence_id": "EV-0363",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY,
        "query_source_sha256": query_source_hash,
        "captures": captures,
        "registered_local_hashes": capture_hashes,
    }, indent=2, ensure_ascii=False))
    capture_hashes[manifest.relative_to(ROOT).as_posix()] = sha(manifest)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    ev0362 = next(item for item in evidence["items"] if item.get("id") == "EV-0362")
    ev0362["sha256"] = sha(ev0362_note)
    ev0362["result"] = "The exact referenced type-name is hkpSimulationIsland and its serializer exposes entity/constraint arrays; exact ProcessTrapHit membership remains unproven. The paired whole-program scans printed only the first 2,048 accesses each, so they provide no 0x140b-range writer result [EV-0363]."
    ev0362.setdefault("local_hashes", {})[ev0362_note.relative_to(ROOT).as_posix()] = sha(ev0362_note)
    ev0362["local_hashes"][ev0362_manifest_path.relative_to(ROOT).as_posix()] = sha(ev0362_manifest_path)
    ev0362["local_hashes"][results_path.relative_to(ROOT).as_posix()] = sha(results_path)
    ev0362["local_hashes"][ev0362_script.relative_to(ROOT).as_posix()] = sha(ev0362_script)
    if any(item.get("id") == "EV-0363" for item in evidence["items"]):
        raise SystemExit("EV-0363 already registered")
    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0363",
        "kind": "native",
        "source": "Read-only audit of EV-0362 GOG displacement-scan raw output and the exact Ghidra query-script output limits.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0363-note.md",
        "sha256": sha(note),
        "runtime": f"GOG AE 1.6.1179.0 static query outputs; analysis binary SHA-256 {BINARY}; no runtime observation.",
        "lane": "mechanism_inference",
        "tools": ["ReadOnlyTargetedQuery.java source audit", "strict-dispatcher query metadata/raw artifact audit"],
        "coverage": "Full scan totals, 2,048 access-output cap, last printed addresses, and writer-function output caps for the +0x60/+0x68 queries.",
        "result": "Both scans completed their counts but printed only 2,048 access lines, ending before the 0x140b physics range. The previous EV-0362 no-writer statement is withdrawn; the writer question remains unresolved.",
        "related_evidence": ["EV-0362", "EV-0360", "EV-0359"],
        "local_hashes": capture_hashes,
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L202 |" in claims:
        raise SystemExit("CL-L202 already registered")
    write(claims_path, claims.rstrip() + "\n| CL-L202 | The completed GOG +0x60/+0x68 displacement scans count all matching operands but expose only the first 2,048 access lines, which stop before the 0x140b physics range. | supported for the exact query-output scope | [EV-0363], [EV-0362] | The scans do not resolve whether hkpSimulationIsland EntityPtrs fields have writers in that range. |")

    contradiction_path = ROOT / "research/CONTRADICTIONS.md"
    contradiction = """

## C-OBJ2-HAVOK-OFFSET-SCAN-CAP — full displacement count versus truncated access output

- **Model A:** completed whole-program +0x60/+0x68 counts plus no printed 0x140b candidate show the island entity-list fields have no writers in that code range.
- **Model B:** the query prints only the first 2,048 accesses; those lines stop before 0x140b, so writer status there is unknown.
- **Source:** GOG scan outputs and completion/output-cap markers [EV-0362], plus the exact `accessOutputLimit = 2048` source and corrected raw-output audit [EV-0363].
- **Current assessment:** Model B is supported. The full access totals are 14,003 and 8,295, but the visible lists are capped at 2,048 and writer-function details are separately capped. EV-0362's earlier no-writer statement is withdrawn. No field-writer negative is established.
- **Discriminant:** trace the exact selected entity and constraint from FUN_140b678a0/FUN_140b43a20 into EntityPtrs and ConMstPtr, or run a targeted query that returns the relevant writer functions with complete receiver lineage.
"""
    contradiction_text = contradiction_path.read_text(encoding="utf-8")
    if "C-OBJ2-HAVOK-OFFSET-SCAN-CAP" not in contradiction_text:
        write(contradiction_path, contradiction_text.rstrip() + contradiction)

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    write(graph_path, graph_path.read_text(encoding="utf-8").rstrip() + "\n\nEV-0363 withdraws the EV-0362 +0x60/+0x68 writer negative because the access lists were capped at 2,048 lines before the physics functions. No causal edge to ProcessTrapHit owner membership or AV11/AV12 is added [CL-L202].\n")

    roadmap_path = ROOT / "research/ROADMAP.md"
    roadmap = roadmap_path.read_text(encoding="utf-8")
    old_roadmap_line = "EV-0362 corrects the island type label and maps EntityPtrs (+0x60/+0x68) to per-entity constraint records (+0x100/+0x108). Next trace the exact selected owner from FUN_140b678a0/FUN_140b43a20 into that list; the immediate displacement scans found no +0x60/+0x68 destination candidates in 0x140b-range bodies."
    new_roadmap_line = "EV-0362 corrects the island type label and maps EntityPtrs (+0x60/+0x68) to per-entity constraint records (+0x100/+0x108). EV-0363 shows the broad displacement scan output stopped before 0x140b, so writer status remains unresolved. Next trace the exact selected owner from FUN_140b678a0/FUN_140b43a20 into that list."
    if old_roadmap_line in roadmap:
        roadmap = roadmap.replace(old_roadmap_line, new_roadmap_line)
        write(roadmap_path, roadmap)

    index_path = ROOT / "experiments/README.md"
    write(index_path, index_path.read_text(encoding="utf-8").rstrip() + "\n\nEXP-0101 / EV-0363 withdraws the EV-0362 broad-scan writer negative because only the first 2,048 accesses were printed.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    question = next(item for item in frontier["items"] if item.get("id") == "Q-0064")
    for bucket in [question.setdefault("evidence", []), *(hyp.setdefault("evidence", []) for hyp in question.get("hypotheses", []))]:
        if "EV-0363" not in bucket:
            bucket.append("EV-0363")
    if "CL-L202" not in question.setdefault("linked_claims", []):
        question["linked_claims"].append("CL-L202")
    frontier_path.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    checkpoint_path = ROOT / "experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"
    checkpoint = checkpoint_path.read_text(encoding="utf-8")
    needle = "- Q-0064 / EV-0362 corrects the owner name to hkpSimulationIsland and maps its EntityPtrs-to-constraint serializer; exact factory-object membership remains unresolved.\n"
    addition = "- Q-0064 / EV-0363 withdraws the EV-0362 +0x60/+0x68 writer negative: both broad scans printed only the first 2,048 accesses and stopped before 0x140b.\n"
    if needle not in checkpoint:
        raise SystemExit("checkpoint helper lacks EV-0362 summary line")
    checkpoint_path.write_text(checkpoint.replace(needle, needle + addition), encoding="utf-8")
    print("registered EV-0363; withdrew the unsupported EV-0362 writer negative; Q-0064 remains active")


if __name__ == "__main__":
    main()
