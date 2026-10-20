#!/usr/bin/env python3
"""Register the argument and caller trace for the camera slot+0x150 lookup."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0081-camera-lookup-string-argument"
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
QUERIES = [
    ("20261018T045932Z", [
        "TARGET_RVA=0xCEE0A0", "OUTGOING_DIRECT_CALL_EDGE_COUNT=0",
        "INDIRECT_CALL_SITE_COUNT=0", "XREF_ANY_COUNT=1576",
        "DECOMPILATION_BEGIN=FUN_140cee0a0", "lVar1 + -0x10"]),
    ("20261018T050045Z", [
        "TARGET_RVA=0x7BCA90", "OUTGOING_DIRECT_CALL_EDGE_COUNT=1",
        "INDIRECT_CALL_SITE_COUNT=0", "INCOMING_CALLER_FUNCTION_COUNT=0",
        "FUN_1408e6500(DAT_1430febf8,param_3,0)",
        "XREF_ANY=1418bb458 -> 1407bca90 type=DATA"]),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def validate_query(stamp: str, markers: list[str]) -> tuple[dict, dict[str, str]]:
    metadata_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    if (
        meta.get("analysis_distribution") != "GOG"
        or meta.get("analysis_binary_product_version") != "1.6.1179"
        or meta.get("analysis_binary_sha256") != GOG_SHA
        or meta.get("program_executable_path_matches_gog_binary") is not True
        or meta.get("query_mode") != "direct_call_edge_census"
        or meta.get("exit_code") != 0
        or meta.get("ok") is not True
        or meta.get("read_only") is not True
        or meta.get("auto_analysis_disabled") is not True
        or meta.get("import_attempted") is not False
        or meta.get("overwrite_attempted") is not False
        or checks.get("direct_call_edge_scan") is not True
        or checks.get("decompilation") is not True
        or checks.get("script_no_error") is not True
    ):
        raise SystemExit(f"Ghidra query validation failed: {stamp}")
    stdout = ROOT / meta["artifacts"]["stdout"]
    raw = stdout.read_text(encoding="utf-8", errors="replace")
    if digest(stdout) != meta.get("stdout_sha256") or any(marker not in raw for marker in markers):
        raise SystemExit(f"Ghidra stdout hash/marker validation failed: {stamp}")
    files = [metadata_path] + [ROOT / relative for relative in meta["artifacts"].values()]
    if any(not path.is_file() for path in files):
        raise SystemExit(f"Ghidra artifact missing: {stamp}")
    hashes = {path.relative_to(ROOT).as_posix(): digest(path) for path in files}
    row = {
        "stamp": stamp,
        "requested_rva": meta.get("requested_rva"),
        "query_mode": meta.get("query_mode"),
        "follow_incoming_calls": meta.get("follow_incoming_calls"),
        "checks": checks,
        "stdout_sha256": meta.get("stdout_sha256"),
        "stderr_sha256": meta.get("stderr_sha256"),
        "query_script_sha256": meta.get("query_script_sha256"),
    }
    return row, hashes


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0343" for row in evidence.get("items", [])):
        raise SystemExit("EV-0343 already registered")

    query_rows = []
    local_hashes: dict[str, str] = {}
    for stamp, markers in QUERIES:
        row, hashes = validate_query(stamp, markers)
        query_rows.append(row)
        local_hashes.update(hashes)

    note = TX / "EV-0343-note.md"
    put(note, f"""# EV-0343 — Camera lookup argument and callback source

## Build and method

Two identity-checked queries used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {GOG_SHA}. Both used the strict dispatcher and Ghidra read-only/no-analysis mode. One query traced the argument wrapper used by FUN_1408e6500; the other traced its direct caller FUN_1407bca90 and incoming references. The wrapper handles a reference-counted pointer with a counter at offset -0x10. That is consistent with a string-reference copy, but Ghidra provides no native class name here. The GOG build is separate from Steam AE 1.6.1170.0; no addresses are transferred.

## Direct observations

- FUN_140cee0a0 copies the pointer stored in its second argument, increments the associated header counter at pointer-0x10 when applicable, writes the pointer to its first argument, and returns that destination. Its complete call census has zero direct and zero indirect outgoing sites; the analyzed program reports 1,576 references [capture 20261018T045932Z].
- FUN_1408e6500 calls FUN_140cee0a0 on its input argument before passing the copied value to the type-erased slot+0x150 call on the object returned by PlayerCharacter slot+0x378 [EV-0342, capture 20261018T045118Z].
- FUN_1407bca90 is a wrapper with one direct call to FUN_1408e6500, no indirect sites, and no direct code callers in the analyzed project. Its decompilation passes param_3 and the PlayerCamera global. Data references point to a callback-like function table at RVA 0x18BB450 and a second unclassified data location; neither establishes the runtime string value or the slot+0x378 receiver class [capture 20261018T050045Z].
- The GOG NiNode candidate implements slot+0x150 by trying a direct child lookup and, on a miss, recursively calling child slot+0x150 with the same opaque argument [EV-0334, EV-0336]. That behavior is compatible with the reference-counted argument and a named-child lookup, but no evidence shows that the PlayerCharacter slot+0x378 result has a NiNode vtable.

## Causal assessment

The argument's reference-count behavior strengthens the named-child interpretation of the slot+0x150 call. The returned object's class remains unresolved; NiNode stays a candidate rather than a matched implementation. The wrapper has no direct caller from which to recover the string value. This does not identify the +0xA0 member's concrete vtable or slot+0x8 finalizer, and does not connect the path to one of the eight ProcessTrapHit teardown sites. No Actor::UseSkill AV11/AV12 sink is shown in the bounded traces.

## Exact next discriminant

Identify the concrete object selected by PlayerCharacter slot+0x378 in this call context and the exact implementation of its slot+0x150. A matching concrete NiNode vtable would support Q65-H1; a distinct implementation/table would support Q65-H2. Keep the returned member finalizer and ProcessTrapHit linkage unresolved until those identities are established.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = digest(note)

    manifest = TX / "EV-0343-capture-manifest.json"
    put(manifest, json.dumps({
        "evidence_id": "EV-0343",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": GOG_SHA,
        "ghidra_captures": query_rows,
    }, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)

    docs = {
        "README.md": """# EXP-0081 — Slot+0x150 argument and caller trace

Trace the wrapper argument and direct callback source for the PlayerCharacter+0x378 / slot+0x150 lookup. Compare its reference-count behavior with the conditional NiNode candidate while retaining the missing concrete vtable as a decisive gap.
""",
        "hypothesis.md": """# Competing models

- Q65-H1: the PlayerCharacter slot+0x378 result is a NiNode-compatible object and slot+0x150 performs a named-child lookup.
- Q65-H2: the getter returns another interface object with its own slot+0x150 behavior.

The argument is a reference-counted pointer copy, but the receiver vtable and runtime value remain unknown.
""",
        "protocol.md": """# Protocol

Query the exact argument wrapper and its observed caller in the GOG AE 1.6.1179.0 project through the strict dispatcher in read-only/no-analysis mode. Compare the argument/call shape with the captured NiNode slot+0x150 implementation only as a discriminant. Do not promote a class match without the exact receiver vtable or equivalent build-attested evidence.
""",
        "results.md": """# Results

FUN_140cee0a0 copies a pointer and increments a header counter at offset -0x10. FUN_1408e6500 passes that copied value to slot+0x150 on the PlayerCharacter slot+0x378 result. The direct callback wrapper has no code callers from which to recover its string value. NiNode recursively searches children with the same opaque argument, making it compatible but not identified [EV-0343], [EV-0336].
""",
        "predicted-outcomes.md": """# Predicted outcomes

- Matching the concrete slot+0x150 implementation to the GOG NiNode vtable supports Q65-H1.
- A concrete different receiver table/implementation supports Q65-H2.
- Argument shape alone, common slot offsets, or a missing runtime class remains inconclusive.
""",
        "implications.md": """# Implications

The lookup receives a refcounted pointer-like argument consistent with a name reference. Its caller and runtime string value are not recovered, and the actual receiver class remains type-erased.
""",
        "expected-discriminants.md": """# Expected discriminants

1. Resolve the object returned by PlayerCharacter slot+0x378 for this call context.
2. Map that object's concrete slot+0x150 implementation.
3. Compare the exact vtable and result class against the NiNode candidate.
4. Keep the returned object's slot+0x8 finalizer and ProcessTrapHit reachability separate until matched.
""",
    }
    for name, content in docs.items():
        put(EXP / name, content)
    for path in EXP.iterdir():
        if path.is_file():
            local_hashes[path.relative_to(ROOT).as_posix()] = digest(path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0343",
        "kind": "native",
        "source": "Read-only GOG Ghidra traces of the reference-counted argument wrapper and the direct caller of the PlayerCamera slot+0x150 lookup.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0343-note.md",
        "sha256": digest(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {GOG_SHA}; static only.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Complete direct-call census and decompilation of FUN_140cee0a0 plus wrapper FUN_1407bca90; the exact slot+0x378 receiver vtable, runtime argument value, slot+0x150 implementation, and returned member type remain unresolved.",
        "result": "FUN_140cee0a0 copies a pointer with a header refcount at offset -0x10, and FUN_1408e6500 passes that copied value to slot+0x150 on the PlayerCharacter slot+0x378 result. This supports but does not prove a named-child/NiNode interpretation. No direct AV11/AV12 sink or ProcessTrapHit linkage is shown.",
        "related_evidence": ["EV-0336", "EV-0337", "EV-0342"],
        "local_hashes": local_hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L180 |" in claims:
        raise SystemExit("EV-0343 claim already exists")
    put(claims_path, claims.rstrip()
        + "\n| CL-L180 | In GOG AE 1.6.1179.0, FUN_1408e6500 passes a reference-counted pointer copy from FUN_140cee0a0 to slot +0x150 on the object returned by PlayerCharacter slot +0x378; this is compatible with, but does not identify, the NiNode child-lookup candidate. | supported for argument flow; class match remains a hypothesis | [EV-0343], [EV-0342], [EV-0336] | The receiver vtable, runtime argument value, returned object type, and ProcessTrapHit reachability are unresolved. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    put(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0343 refines M-0065: the PlayerCharacter slot+0x378 / slot+0x150 path receives a pointer whose wrapper performs header refcounting, consistent with a string reference. NiNode recursively searches children with an opaque argument at the same slot, so the named-child model is compatible but not a class identity. CL-L180 -> M-0065.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph_path, graph_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0343 shows that the slot+0x150 argument is copied with a refcounted pointer header; this is compatible with a named-child lookup and NiNode's recursive same-slot behavior [EV-0336]. The actual receiver vtable and result class remain unmatched, so Q65-H1 is not promoted and no causal edge to Actor::UseSkill or OBJ-1 is added. A different concrete slot+0x150 table would falsify the NiNode-family hypothesis. Claim CL-L180 -> M-0065.\n")

    index_path = ROOT / "experiments/README.md"
    put(index_path, index_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEXP-0081 / EV-0343 maps the reference-counted argument and wrapper caller for the PlayerCharacter+0x378 slot+0x150 lookup; the receiver class remains unresolved.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    q65 = next(row for row in frontier["items"] if row.get("id") == "Q-0065")
    for row in [q64, q65]:
        if "EV-0343" not in row.setdefault("evidence", []):
            row["evidence"].append("EV-0343")
    for row in [*q64.get("hypotheses", []), *q65.get("hypotheses", [])]:
        if "EV-0343" not in row.setdefault("evidence", []):
            row["evidence"].append("EV-0343")
    if "CL-L180" not in q64.setdefault("linked_claims", []):
        q64["linked_claims"].append("CL-L180")
    if "CL-L180" not in q65.setdefault("linked_claims", []):
        q65["linked_claims"].append("CL-L180")
    q64["next_action"] = (
        "Resolve the concrete object returned by PlayerCharacter slot +0x378 in the FUN_1408e6500 call context and "
        "its slot +0x150 implementation/return vtable. The refcounted argument is compatible with a named-child lookup "
        "but does not identify the receiver. Match the returned object's +0x8 finalizer to one of the eight "
        "ProcessTrapHit teardown sites."
    )
    q65["next_action"] = (
        "Match the concrete receiver vtable and slot +0x150 implementation for PlayerCharacter slot +0x378 against "
        "the NiNode candidate; the refcounted argument is compatible with child lookup but not class evidence. A distinct "
        "table/implementation falsifies the shared-family model; compare exact returned vtables/finalizers across fields."
    )
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    if "EV-0343" not in state:
        state = state.replace(
            "- Q-0064 / EV-0341–EV-0342 maps the remaining PlayerCamera callbacks and the ThirdPersonState+0xA0 ownership path. A type-erased PlayerCharacter slot +0x378 result receives a virtual +0x150 call whose return is refcounted and released through virtual +0x8. Its concrete class and link to the eight trap-cleanup sites remain unknown; no direct AV11/AV12 sink appears in the sampled bodies.",
            "- Q-0064 / EV-0341–EV-0343 maps the remaining PlayerCamera callbacks and the ThirdPersonState+0xA0 ownership path. A type-erased PlayerCharacter slot +0x378 result receives a virtual +0x150 call with a refcounted pointer argument; its return is released through virtual +0x8. This is compatible with a named-child lookup but does not establish a NiNode class or link to the eight trap-cleanup sites; no direct AV11/AV12 sink appears in the sampled bodies."
        )
        put(state_path, state)

    with (ROOT / "research/SESSION_LOG.md").open("a", encoding="utf-8") as stream:
        stream.write("\n- " + datetime.now(timezone.utc).isoformat(timespec="seconds")
            + " TX-20261017-0011 research update: EV-0343 / CL-L180 registered. FUN_140cee0a0 copies a pointer with a header refcount at -0x10, and FUN_1407bca90 passes its third argument through FUN_1408e6500 to the type-erased slot+0x150 call. This is compatible with NiNode child lookup but not a receiver class match; the wrapper has no direct code callers. Q64/Q65 remain unresolved. Next: identify the PlayerCharacter slot+0x378 receiver and slot+0x150 implementation, then match the returned +0x8 finalizer.\n")
    print("registered EV-0343 / CL-L180; Q-0064 and Q-0065 remain open")


if __name__ == "__main__":
    main()
