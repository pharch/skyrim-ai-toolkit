#!/usr/bin/env python3
"""Register paired AnimatedCamera handler interface and argument-flow evidence."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0083-animated-camera-handler-contract"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = [
    {"stamp": "20261018T051918Z", "kind": "calls", "markers": [
        "TARGET_RVA=0x7C0F40", "IHandlerFunctor<class_Actor,class_BSFixedStringCI>::vftable",
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=1"]},
    {"stamp": "20261018T052037Z", "kind": "calls", "markers": [
        "TARGET_RVA=0x7C0EE0", "IHandlerFunctor<class_Actor,class_BSFixedStringCI>::vftable",
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=1"]},
    {"stamp": "20261018T052137Z", "kind": "calls", "markers": [
        "TARGET_RVA=0x7C20E0", "AnimatedCameraDeltaStartHandler::vftable",
        "LEA RCX, [0x1418bb468]", "OUTGOING_DIRECT_CALL_EDGE_COUNT=2"]},
    {"stamp": "20261018T052236Z", "kind": "calls", "markers": [
        "TARGET_RVA=0x7BCAC0", "FUN_1408e6500(DAT_1430febf8,param_3,1)",
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=1"]},
    {"stamp": "20261018T052403Z", "kind": "pointer", "markers": [
        "POINTER_TABLE_BASE_RVA=0x18BB468", "POINTER_TABLE_REQUESTED_COUNT=3",
        "POINTER_TABLE_SCAN_COMPLETE=true", "POINTER_TABLE_XREF_SCAN_COMPLETE=true",
        "POINTER_TABLE_ENTRY=index:1 address:1418bb470 value:0x1407BCAC0 target:1407bcac0 function:FUN_1407bcac0"]},
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def validate_capture(spec: dict) -> tuple[dict, dict[str, str]]:
    stamp = spec["stamp"]
    metadata_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    if (meta.get("analysis_distribution") != "GOG"
        or meta.get("analysis_binary_product_version") != "1.6.1179"
        or meta.get("analysis_binary_sha256") != BINARY
        or meta.get("program_executable_path_matches_gog_binary") is not True
        or meta.get("exit_code") != 0 or meta.get("ok") is not True
        or meta.get("read_only") is not True or meta.get("auto_analysis_disabled") is not True
        or meta.get("import_attempted") is not False or meta.get("overwrite_attempted") is not False
        or checks.get("program_identity_matches_gog_binary") is not True
        or checks.get("script_no_error") is not True):
        raise SystemExit(f"identity/read-only/completion check failed: {stamp}")
    if spec["kind"] == "pointer":
        needed = ("pointer_table_requested", "pointer_table_scan_complete", "pointer_table_xref_scan_complete")
    else:
        needed = ("function_lookup", "requested_rva_lookup", "direct_call_edge_scan", "decompilation")
    if any(checks.get(key) is not True for key in needed):
        raise SystemExit(f"required query component failed: {stamp}")
    stdout = ROOT / meta["artifacts"]["stdout"]
    raw = stdout.read_text(encoding="utf-8", errors="replace")
    if digest(stdout) != meta.get("stdout_sha256") or any(marker not in raw for marker in spec["markers"]):
        raise SystemExit(f"stdout hash/marker validation failed: {stamp}")
    files = [metadata_path] + [ROOT / relative for relative in meta["artifacts"].values()]
    if any(not path.is_file() for path in files):
        raise SystemExit(f"capture artifact missing: {stamp}")
    hashes = {path.relative_to(ROOT).as_posix(): digest(path) for path in files}
    row = {
        "stamp": stamp, "query_kind": spec["kind"], "query_mode": meta.get("query_mode"),
        "requested_rva": meta.get("requested_rva"),
        "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
        "requested_pointer_count": meta.get("requested_pointer_count"),
        "checks": checks, "overall_ok": meta.get("ok"),
        "stdout_sha256": meta.get("stdout_sha256"),
        "stderr_sha256": meta.get("stderr_sha256"),
        "query_script_sha256": meta.get("query_script_sha256"),
    }
    return row, hashes


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0345" for row in evidence.get("items", [])):
        raise SystemExit("EV-0345 already registered")
    rows: list[dict] = []
    local_hashes: dict[str, str] = {}
    for spec in CAPTURES:
        row, hashes = validate_capture(spec)
        rows.append(row)
        local_hashes.update(hashes)

    note = TX / "EV-0345-note.md"
    put(note, f"""# EV-0345 — AnimatedCamera handler interface and callback variants

## Build and method

Five bounded captures used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BINARY}, through the strict dispatcher in read-only/no-analysis mode. All requested function, edge-census, decompilation, or exact pointer-table components passed. The GOG image remains separate from Steam AE 1.6.1170.0.

## Direct observations

- FUN_1407c20e0 allocates a 0x10-byte handler and installs AnimatedCameraDeltaStartHandler::vftable at address 0x1418BB468 (RVA 0x18BB468) [capture 20261018T052137Z]. The complete three-entry table has FUN_1407c0ee0 at index 0, FUN_1407bcac0 at index 1, and an unresolved function pointer at index 2; its xref scan ties the base back to the factory [capture 20261018T052403Z].
- FUN_1407bcac0 has one direct call and no indirect sites. It forwards its third argument to FUN_1408e6500 with the PlayerCamera global and flag 1; it has no analyzed direct code caller [capture 20261018T052236Z].
- The adjacent handler cleanup functions FUN_1407c0f40 and FUN_1407c0ee0 install the named base vtable IHandlerFunctor<class Actor,class BSFixedStringCI>::vftable before optional deletion [captures 20261018T051918Z and 052037Z]. EV-0344 separately maps FUN_1407bca90 to AnimatedCameraStartHandler::vftable entry 1 and its call into FUN_1408e6500 with flag 0.
- Together, the named base interface and the two method bodies make BSFixedStringCI a type-consistent interpretation of their third argument, which is forwarded as FUN_1408e6500's lookup argument. The direct wrapper signatures remain untyped in Ghidra, and the runtime value is not recovered.
- FUN_1408e6500 uses the same PlayerCharacter slot +0x378 flag-zero context lookup for both flags, then applies different ThirdPersonState update branches [EV-0342]. No captured edge connects these camera-animation callbacks to ProcessTrapHit teardown or Actor::UseSkill AV11/AV12.

## Causal assessment

The fixed-string interface shape supports a named lookup interpretation for the slot +0x150 call, but it does not identify the lookup receiver's class or returned member. The two callback variants do not discriminate Q65-H1 from Q65-H2. Q64-H1/H2 remain proposed; no armor-skill exclusion or cross-objective edge is added.

## Exact next discriminant

Resolve the dynamic object returned by PlayerCharacter slot +0x378 in the TLS and nested-field branches, then match its exact slot +0x150 table and returned member finalizer. Separately capture local contexts for the five omitted indirect cleanup sites in FUN_14072fd60; only an exact shared target or data-flow edge can connect this camera branch to ProcessTrapHit.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = digest(note)
    manifest = TX / "EV-0345-capture-manifest.json"
    put(manifest, json.dumps({"evidence_id": "EV-0345", "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY, "captures": rows}, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)

    docs = {
        "README.md": "# EXP-0083 — AnimatedCamera handler interface\n\nMap the paired AnimatedCameraStartHandler and AnimatedCameraDeltaStartHandler methods that forward their event argument into the PlayerCharacter context lookup.\n",
        "hypothesis.md": "# Competing models\n\n- Q65-H1: the callback's BSFixedStringCI argument selects a named child on an NiNode-compatible context object.\n- Q65-H2: the same fixed-string-like input is consumed by a different slot +0x150 interface.\n\nThe interface name supports the argument shape, not the receiver class.\n",
        "protocol.md": "# Protocol\n\nUse the existing GOG project through the strict dispatcher in read-only/no-analysis mode. Confirm each factory-installed vtable and exact slot pointer, then inspect the corresponding wrapper call. Do not infer receiver type or runtime argument value from a handler name. Keep all GOG RVAs build-specific.\n",
        "results.md": "# Results\n\nAnimatedCameraStartHandler entry 1 forwards its third argument into FUN_1408e6500 with flag 0 [EV-0344]. AnimatedCameraDeltaStartHandler entry 1 forwards its third argument into the same helper with flag 1. Their cleanup functions identify the base interface as IHandlerFunctor<Actor,BSFixedStringCI>, making a fixed-string argument interpretation consistent but not runtime-observed. The slot +0x150 receiver and returned member type remain unknown [EV-0345].\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- An exact context vtable whose slot +0x150 matches the NiNode child traversal supports Q65-H1.\n- A different exact slot table supports Q65-H2.\n- A named handler or fixed-string interface alone is not class evidence.\n",
        "implications.md": "# Implications\n\nThe two callback variants share a PlayerCharacter context lookup but differ in their ThirdPersonState update flag. Their static path has no established connection to ProcessTrapHit or AV11/AV12 skill progress.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Resolve the object returned by the PlayerCharacter flag-zero context getter.\n2. Map its exact slot +0x150 implementation and returned object vtable.\n3. Identify the returned object's slot +0x8 finalizer.\n4. Compare concrete targets against the five omitted cleanup sites and the full eight-site ProcessTrapHit chain.\n",
    }
    for name, content in docs.items():
        put(EXP / name, content)
    script_path = EXP / "register_ev_0345.py"
    local_hashes[script_path.relative_to(ROOT).as_posix()] = digest(script_path)
    for path in EXP.iterdir():
        if path.is_file():
            local_hashes[path.relative_to(ROOT).as_posix()] = digest(path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE", "modified_state": False, "id": "EV-0345", "kind": "native",
        "source": "Read-only GOG Ghidra traces of the AnimatedCameraStartHandler and AnimatedCameraDeltaStartHandler vtable methods, base interface, and callback argument flow.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0345-note.md",
        "sha256": digest(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Five bounded captures map the delta handler factory and table, its wrapper, and both base-interface cleanup methods. The runtime argument value, selected context object's concrete class, slot +0x150 target, returned finalizer, and ProcessTrapHit linkage remain unresolved.",
        "result": "AnimatedCameraStartHandler and AnimatedCameraDeltaStartHandler methods forward their third argument to FUN_1408e6500 with flags 0 and 1. Their base interface is named IHandlerFunctor<Actor,BSFixedStringCI>, making a BSFixedStringCI argument type-consistent but not runtime-observed. No AV11/AV12 or ProcessTrapHit edge is shown.",
        "related_evidence": ["EV-0342", "EV-0343", "EV-0344"],
        "local_hashes": local_hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L183 |" in claims:
        raise SystemExit("CL-L183 already exists")
    put(claims_path, claims.rstrip()
        + "\n| CL-L183 | In GOG AE 1.6.1179.0, AnimatedCameraStartHandler and AnimatedCameraDeltaStartHandler wrappers forward their third argument to FUN_1408e6500 with flags 0 and 1; their cleanup methods name the base IHandlerFunctor<Actor,BSFixedStringCI> interface. | supported for table and call flow; argument type is a source-based inference | [EV-0345], [EV-0344], [EV-0342] | The runtime argument value, PlayerCharacter context result class, slot +0x150 target, returned finalizer, and ProcessTrapHit reachability remain unknown. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    put(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0345 refines M-0065: paired AnimatedCameraStartHandler/AnimatedCameraDeltaStartHandler methods forward a BSFixedStringCI-type-consistent argument into FUN_1408e6500 with flags 0/1. This supports a named-lookup interpretation but not a NiNode receiver match; the concrete slot +0x150 target and returned member finalizer remain unresolved. Claim CL-L183 -> M-0065.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph_path, graph_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0345 maps paired AnimatedCamera callback wrappers into FUN_1408e6500 with flags 0/1 and identifies their base interface as IHandlerFunctor<Actor,BSFixedStringCI>. The fixed-string type shape is compatible with named lookup but does not establish a NiNode receiver or connect this path to ProcessTrapHit or Actor::UseSkill AV11/AV12. Q64-H1/H2 and Q65-H1/H2 remain unresolved. Claim CL-L183 -> M-0065; no causal edge is added.\n")

    index_path = ROOT / "experiments/README.md"
    put(index_path, index_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEXP-0083 / EV-0345 maps the two AnimatedCamera handler wrappers and their BSFixedStringCI-type-consistent argument flow into FUN_1408e6500; the lookup receiver class remains unknown.\n")
    roadmap_path = ROOT / "research/ROADMAP.md"
    put(roadmap_path, roadmap_path.read_text(encoding="utf-8").rstrip()
        + "EV-0345 bounds the AnimatedCameraStart/DeltaStart callback branch: the wrappers share FUN_1408e6500 and an IHandlerFunctor<Actor,BSFixedStringCI>-named base, but the lookup receiver and returned member remain untyped. Continue with the five missing ProcessTrapHit cleanup-site contexts; do not convert this camera branch's unresolved relation into a negative armor-XP claim. Claim CL-L183 -> M-0065.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    q65 = next(row for row in frontier["items"] if row.get("id") == "Q-0065")
    for row in (q64, q65):
        if "EV-0345" not in row.setdefault("evidence", []):
            row["evidence"].append("EV-0345")
        for hypothesis in row.get("hypotheses", []):
            if "EV-0345" not in hypothesis.setdefault("evidence", []):
                hypothesis["evidence"].append("EV-0345")
    for row in (q64, q65):
        if "CL-L183" not in row.setdefault("linked_claims", []):
            row["linked_claims"].append("CL-L183")
    next_action = (
        "Return to the complete FUN_14072fd60 ProcessTrapHit census and query the five omitted indirect cleanup "
        "sites individually at RVAs 0x7305EA, 0x730609, 0x730628, 0x730647, and 0x7306AE. Recover each "
        "receiver and exact slot/finalizer context, then compare any matched target with the bounded camera branch. "
        "Do not treat the missing camera-to-trap edge as a no-skill negative."
    )
    q64["next_action"] = next_action
    q64.setdefault("attempts", []).append({
        "action_key": "q64-animated-camera-handler-argument-contract",
        "outcome": "EV-0345 maps the AnimatedCameraStart and DeltaStart handler wrappers to FUN_1408e6500 with flags 0 and 1. Their base interface is IHandlerFunctor<Actor,BSFixedStringCI>, consistent with a fixed-string lookup argument. The runtime value, selected context class, slot +0x150 target/finalizer, and ProcessTrapHit connection remain unresolved.",
        "evidence": ["EV-0345"],
        "new_discriminant": "The camera callback is a fixed-string-type-consistent named-lookup candidate; only an exact receiver vtable or shared finalizer can distinguish Q65 models or connect to ProcessTrapHit.",
        "next_action": next_action,
    })
    q65["next_action"] = (
        "Resolve the TLS +0x5F0 and nested PC +0x68/+0x68 alternatives selected by FUN_1402e55a0; map the exact "
        "slot +0x150 receiver/result vtables and compare each returned +0x8 finalizer with the NiNode candidate. "
        "The BSFixedStringCI interface supports the lookup shape but not its receiver class."
    )
    q65.setdefault("attempts", []).append({
        "action_key": "q65-animated-camera-handler-interface-screen",
        "outcome": "EV-0345 identifies the paired callback interface and fixed-string-type-consistent argument flow but does not identify the slot +0x150 receiver class. Q65-H1/H2 remain proposed.",
        "evidence": ["EV-0345"],
        "new_discriminant": "Recover exact vtable and returned member finalizer; do not promote a named-child hypothesis from argument type alone.",
        "next_action": q65["next_action"],
    })
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))
    print("registered EV-0345 / CL-L183; Q-0064 and Q-0065 remain unresolved")


if __name__ == "__main__":
    main()
