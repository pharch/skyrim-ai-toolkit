#!/usr/bin/env python3
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
    "20261018T111130Z": {"requested_rva": "0xF28CB0"},
    "20261018T111254Z": {"requested_pointer_table_rva": "0x19F4408", "requested_pointer_count": 16},
    "20261018T111403Z": {"requested_pointer_table_rva": "0x19F4600", "requested_pointer_count": 16},
    "20261018T111542Z": {"requested_address_rva": "0x19F4408"},
    "20261018T111646Z": {"requested_address_rva": "0x19F4600"},
    "20261018T111846Z": {"requested_rva": "0xEF2720"},
    "20261018T112006Z": {"requested_string": "hkBallSocketChainCinfo"},
}
MARKERS = {
    "20261018T111130Z": ["XREF_CALL_COUNT=0", "INCOMING_CALLER_FUNCTION_COUNT=0", "XREF_ANY=1419f4410 -> 140f28cb0"],
    "20261018T111254Z": ["POINTER_TABLE_ENTRY=index:2 address:1419f4418 value:0x14153DB78", "POINTER_TABLE_XREF_COUNT=2"],
    "20261018T111403Z": ["POINTER_TABLE_ENTRY=index:2 address:1419f4610 value:0x140EF2720", "POINTER_TABLE_XREF_COUNT=0"],
    "20261018T111542Z": ["ADDRESS_TARGET_XREF_COUNT=0", "ADDRESS_CONTEXT_COMPLETE=true"],
    "20261018T111646Z": ["ADDRESS_TARGET_XREF_COUNT=0", "ADDRESS_CONTEXT_COMPLETE=true"],
    "20261018T111846Z": ["XREF_CALL_COUNT=0", "INCOMING_CALLER_FUNCTION_COUNT=0", "*puVar7 = hkBallSocketChainCinfo::vftable;"],
    "20261018T112006Z": ["STRING_MATCH_COUNT=1", "STRING_REFERENCE_COUNT=0", "STRING_REFERENCE_SCAN_COMPLETE=true"],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def append_once(path: Path, marker: str, body: str) -> None:
    old = path.read_text(encoding="utf-8")
    if marker in old:
        raise SystemExit("duplicate append: " + marker)
    write(path, old.rstrip() + "\n\n" + body.strip())


def load_capture(stamp: str, expected: dict[str, object]):
    meta_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    stdout = ROOT / meta["artifacts"]["stdout"]
    checks = meta.get("checks", {})
    valid = (
        meta.get("operation") == "existing_gog_project_read_only_query"
        and meta.get("analysis_distribution") == "GOG"
        and meta.get("analysis_binary_product_version") == "1.6.1179"
        and meta.get("analysis_binary_sha256") == BIN
        and meta.get("program") == "SkyrimSE.exe"
        and meta.get("program_executable_path_matches_gog_binary") is True
        and meta.get("exit_code") == 0
        and meta.get("ok") is True
        and meta.get("read_only") is True
        and meta.get("auto_analysis_disabled") is True
        and meta.get("import_attempted") is False
        and meta.get("overwrite_attempted") is False
        and meta.get("project_created") is False
        and bool(checks)
        and all(checks.values())
        and stdout.is_file()
        and sha(stdout) == meta.get("stdout_sha256")
        and all(meta.get(key) == value for key, value in expected.items())
    )
    if not valid:
        raise SystemExit(f"capture identity, policy, request, or hash failed: {stamp}")
    raw = stdout.read_text(encoding="utf-8", errors="replace")
    missing = [marker for marker in MARKERS[stamp] if marker not in raw]
    if missing:
        raise SystemExit(f"capture markers missing for {stamp}: {missing}")
    return stamp, meta, meta_path, stdout, raw


def main() -> None:
    captures = [load_capture(stamp, expected) for stamp, expected in CAPTURES.items()]
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0371" for item in evidence["items"]):
        raise SystemExit("EV-0371 already exists")
    claims_path = ROOT / "research/CLAIMS.md"
    note = TX / "EV-0371-note.md"
    write(note, f"""# EV-0371 — chain factory pointer-window ownership screen

## Build and method

Seven identity-checked queries use the existing GOG AE 1.6.1179.0 SkyrimSE.exe project in read-only/no-analysis mode; binary SHA-256 {BIN}. The queries cover FUN_140f28cb0, pointer windows at RVAs 0x19F4408 and 0x19F4600, references to both bases, FUN_140ef2720, and a literal initialized-memory search for hkBallSocketChainCinfo.

## Competing models and predicted discriminants

- H1: the chain factory or its table owner is in the ProcessTrapHit cleanup route.
- H2: the pointer window belongs to a separate Havok chain helper path.
- H1 predicts a direct incoming call/call-chain or an exact owner reference linking the factory to ProcessTrapHit. H2 predicts a separate table/method context. Table-base references, function-call edges, and exact receiver setup discriminate these models; symbol-like labels alone do not.

## Direct observations

- FUN_140f28cb0 has zero analyzed direct call xrefs and appears as a data pointer at index 1 in both queried 16-entry pointer windows. The windows differ at index 2: 0x19F4408 has `_purecall`; 0x19F4600 has FUN_140ef2720 [captures 20261018T111130Z, 20261018T111254Z, 20261018T111403Z].
- Address-context queries at both window bases report zero references [captures 20261018T111542Z, 20261018T111646Z]. This bounded result does not identify the table owner.
- FUN_140ef2720 has zero analyzed incoming code-call edges. Its data references include the index-2 pointer at 0x1419f4610. Its decompilation allocates a 0x48-byte object and assigns the labeled `hkBallSocketChainCinfo::vftable` at 0x1419f4468; the body stores the object-associated pointer at param_1+0x18 and conditionally invokes FUN_140f29440 [capture 20261018T111846Z]. These observations do not establish the runtime table type or a ProcessTrapHit path.
- The exact initialized-memory string search finds one `hkBallSocketChainCinfo` match in .data and zero references [capture 20261018T112006Z]. This is not independent RTTI or owner evidence.
- The previously mapped ProcessTrapHit fixed/malleable route reaches ordinary hkpConstraintInstance construction [EV-0365, EV-0366]. No call or owner edge from that route to this factory is established by this screen.

## Result and uncertainty

Neither model is selected. The queried helper is associated with a Havok chain-configuration label, but its pointer-window owner and relationship to ProcessTrapHit remain unresolved. The two zero-reference base screens and zero direct incoming-call counts are bounded to the existing analyzed GOG listing; they do not prove that no runtime indirect caller exists. No skill-progress or armor-XP behavior is tested here.

## Exact next action

Return to the exact hkpConstraintInstance callback producer question. Use the existing complete +0x40/+0x48 displacement-candidate outputs to select a candidate with receiver evidence matching hkpConstraintInstance, then query that candidate's constructor/writer and call context. Keep untyped same-offset candidates classified as unresolved.
""")

    docs = {
        "README.md": "# EXP-0109 — chain factory pointer-window owner screen\n\nTest whether the hkpConstraintChainInstance factory's analyzed owner/call context connects to ProcessTrapHit. The exact table owner remains unresolved.\n",
        "hypothesis.md": "# Competing models\n\n- H1: the chain factory or its table owner is part of the ProcessTrapHit cleanup route.\n- H2: the pointer window belongs to a separate Havok chain helper path.\n\nA direct call chain or exact owner reference is required to select H1.\n",
        "protocol.md": "# Protocol\n\nQuery the factory, both bounded pointer windows, both table-base addresses, and the index-2 method with the strict GOG read-only dispatcher. Search the initialized listing for the object's named label. Do not infer a runtime class from pointer-window contents alone.\n",
        "expected-discriminants.md": "# Expected discriminants\n\nA ProcessTrapHit-owned factory should have a direct analyzed incoming path or exact receiver/owner reference into the mapped cleanup route. Separate pointer-window contents, a helper-specific object label, or zero direct references leave ownership unresolved.\n",
        "results.md": "# Results\n\nThe factory has no analyzed direct-call xrefs and occurs in two pointer windows; their index-2 entries differ. Both base-address queries return zero xrefs. FUN_140ef2720 initializes an object labeled hkBallSocketChainCinfo but has no analyzed incoming code-call edges; the literal search yields no references. No ProcessTrapHit owner edge is established. See EV-0371.\n",
        "implications.md": "# Implications\n\nThis screen narrows the current ownership hypothesis without resolving runtime ownership or callback behavior. Continue with receiver-backed hkpConstraintInstance callback writers and keep the ProcessTrapHit connection open.\n",
    }
    for name, body in docs.items():
        write(EXP / name, body)

    manifest_path = TX / "EV-0371-capture-manifest.json"
    local_hashes: dict[str, str] = {}
    capture_summaries = []
    for stamp, meta, meta_path, stdout, _raw in captures:
        local_hashes[meta_path.relative_to(ROOT).as_posix()] = sha(meta_path)
        for artifact in meta.get("artifacts", {}).values():
            path = ROOT / artifact
            if path.is_file():
                local_hashes[path.relative_to(ROOT).as_posix()] = sha(path)
        capture_summaries.append({
            "stamp": stamp,
            "query_mode": meta.get("query_mode"),
            "requested_rva": meta.get("requested_rva"),
            "requested_address_rva": meta.get("requested_address_rva"),
            "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
            "requested_pointer_count": meta.get("requested_pointer_count"),
            "requested_string": meta.get("requested_string"),
            "checks": meta.get("checks"),
            "stdout_sha256": meta.get("stdout_sha256"),
            "read_only": meta.get("read_only"),
            "auto_analysis_disabled": meta.get("auto_analysis_disabled"),
        })
    local_hashes[note.relative_to(ROOT).as_posix()] = sha(note)
    local_hashes[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    for name in docs:
        path = EXP / name
        local_hashes[path.relative_to(ROOT).as_posix()] = sha(path)
    write(manifest_path, json.dumps({
        "evidence_id": "EV-0371",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BIN,
        "captures": capture_summaries,
        "registered_local_hashes": local_hashes,
    }, indent=2, ensure_ascii=False))
    local_hashes[manifest_path.relative_to(ROOT).as_posix()] = sha(manifest_path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0371",
        "kind": "native",
        "source": "Identity-checked read-only GOG Ghidra pointer-window and call-context screen for the hkpConstraintChainInstance factory path.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0371-note.md",
        "sha256": sha(note),
        "runtime": f"GOG AE 1.6.1179.0 static outputs; analysis binary SHA-256 {BIN}; no Steam runtime observation.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
        "coverage": "Factory direct-call xrefs, two pointer windows and their bases, index-2 helper body, and a bounded initialized-memory literal search.",
        "result": "The factory and index-2 helper have no analyzed direct incoming code calls; both pointer-window bases have zero references. FUN_140ef2720 initializes an object labeled hkBallSocketChainCinfo. No exact table owner or ProcessTrapHit edge is established.",
        "related_evidence": ["EV-0365", "EV-0366", "EV-0370"],
        "local_hashes": local_hashes,
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    if "| CL-L211 |" in claims_path.read_text(encoding="utf-8"):
        raise SystemExit("CL-L211 already exists")
    append_once(claims_path, "| CL-L211 |", "| CL-L211 | In the analyzed GOG AE 1.6.1179.0 project, FUN_140ef2720 has zero direct incoming call edges and is present as a pointer-window entry; its body initializes an object labeled hkBallSocketChainCinfo. Two queried window bases have zero references, and no ProcessTrapHit ownership edge is established by these bounded queries. | supported for the queried build/listing scope | [EV-0371], [EV-0365], [EV-0366] | Pointer-window owner, runtime indirect callers, callback population and Steam behavior remain unresolved. |")
    append_once(ROOT / "research/CONTRADICTIONS.md", "## C-OBJ2-Q64-CHAIN-OWNER", """## C-OBJ2-Q64-CHAIN-OWNER — chain factory ownership

- **Model A:** the chain factory or its table owner is reached from the ProcessTrapHit cleanup route.
- **Model B:** the queried pointer window belongs to a separate Havok chain helper path.
- **Evidence:** the factory has no analyzed direct incoming calls; its pointer-window bases have zero references; the differing index-2 helper initializes an object labeled hkBallSocketChainCinfo [EV-0371]. The mapped ProcessTrapHit route reaches ordinary hkpConstraintInstance construction [EV-0365, EV-0366].
- **Assessment:** neither model is selected. The captures establish no exact owner or cross-route call edge; zero Ghidra xrefs do not rule out runtime indirect dispatch.
- **Discriminant:** resolve the table owner or the exact callback writer and receiver on the ProcessTrapHit object before connecting these paths.""")
    append_once(ROOT / "research/KNOWLEDGE_GRAPH.md", "EV-0371 records no chain-factory owner edge", "EV-0371 adds bounded GOG call and pointer-window evidence for the hkpConstraintChainInstance factory. Because neither an exact owner nor a ProcessTrapHit call edge is identified, it adds no causal edge between the chain helper and the ProcessTrapHit cleanup path; keep the relationship unresolved [CL-L211], [C-OBJ2-Q64-CHAIN-OWNER].")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    question = next(item for item in frontier["items"] if item.get("id") == "Q-0064")
    if question.get("status") != "in_progress":
        raise SystemExit("Q-0064 is not active")
    if "EV-0371" not in question.setdefault("evidence", []):
        question["evidence"].append("EV-0371")
    for hypothesis in question.get("hypotheses", []):
        if "EV-0371" not in hypothesis.setdefault("evidence", []):
            hypothesis["evidence"].append("EV-0371")
    if "CL-L211" not in question.setdefault("linked_claims", []):
        question["linked_claims"].append("CL-L211")
    question["next_action"] = "Use the complete +0x40/+0x48 displacement-candidate outputs to select a candidate with receiver evidence matching hkpConstraintInstance; query its exact constructor/writer and call context. Keep untyped same-offset candidates unresolved, then trace the proven callback entry target toward AV11/AV12."
    question.setdefault("methods", []).append("EV-0371 found no exact owner or ProcessTrapHit edge for the chain factory; continue with receiver-backed hkpConstraintInstance callback writers.")
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))
    append_once(ROOT / "STATE.md", "Q-0064 / EV-0371", "- Q-0064 / EV-0371 screened the chain factory's two pointer windows and index-2 method. Table owners and a ProcessTrapHit link remain unresolved; zero direct xrefs are scoped to the analyzed GOG listing. Next, select a receiver-backed hkpConstraintInstance callback writer from the complete displacement scans.")
    append_once(ROOT / "ROADMAP.md", "EV-0371 screens the chain factory owner", "EV-0371 does not establish a ProcessTrapHit owner edge for the chain factory. Resume Q-0064 at the exact hkpConstraintInstance callback writer and keep the chain relation unresolved [CL-L211].")
    append_once(ROOT / "experiments/README.md", "EXP-0109 / EV-0371", "EXP-0109 / EV-0371 screens the chain factory's pointer-window and direct-call ownership context; no ProcessTrapHit edge is established, so Q-0064 continues at receiver-backed callback writers.")
    print("Registered EV-0371 / CL-L211; retained the no-edge rationale and advanced Q-0064 to receiver-backed callback-writer selection.")


if __name__ == "__main__":
    main()
