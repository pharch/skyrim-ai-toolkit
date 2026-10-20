#!/usr/bin/env python3
"""Register the PlayerCharacter context-receiver and camera-handler trace."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0082-playercharacter-context-owner-resolution"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = [
    {"stamp": "20261018T050454Z", "kind": "address", "markers": [
        "ADDRESS_RVA=0x3188918", "ADDRESS_TARGET_XREF_COUNT=2835",
        "from:14064cb6b type:WRITE function:FUN_14064cac0",
        "from:1401b9c38 type:WRITE function:FUN_1401b98e0"]},
    {"stamp": "20261018T050601Z", "kind": "calls", "markers": [
        "TARGET_RVA=0x1B98E0", "OUTGOING_DIRECT_CALL_EDGE_COUNT=48",
        "DAT_143188918 = 0;", "FUN_14064af30"]},
    {"stamp": "20261018T050722Z", "kind": "calls", "markers": [
        "TARGET_RVA=0x64CAC0", "FUN_14072ed70(local_res10);",
        "DAT_143188918 = plVar5;"]},
    {"stamp": "20261018T050928Z", "kind": "function", "markers": [
        "TARGET_RVA=0x72ED70", "LEA R8, [0x1418acd70]",
        "PlayerCharacter::vftable"]},
    {"stamp": "20261018T051031Z", "kind": "slot_diagnostic", "markers": [
        "VTABLE_BASE_RVA=0x18ACD70", "VTABLE_SLOT_INDEX=0x6F",
        "VTABLE_SLOT_TARGET_RVA=0x7371F0", "XREF_CALL_EDGE=NOT_FOUND_IN_ANALYZED_PROJECT"]},
    {"stamp": "20261018T051139Z", "kind": "calls", "markers": [
        "TARGET_RVA=0x2E55A0", "OUTGOING_DIRECT_CALL_EDGE_COUNT=0",
        "INDIRECT_CALL_SITE_COUNT=0", "XREF_CALL_COUNT=136",
        "param_1 == *(longlong *)(lVar1 + 0x5f8)",
        "*(undefined8 *)(*(longlong *)(param_1 + 0x68) + 0x68)"]},
    {"stamp": "20261018T051326Z", "kind": "pointer", "markers": [
        "POINTER_TABLE_BASE_RVA=0x18BB450", "POINTER_TABLE_SCAN_COMPLETE=true",
        "POINTER_TABLE_XREF_SCAN_COMPLETE=true",
        "POINTER_TABLE_ENTRY=index:1 address:1418bb458 value:0x1407BCA90 target:1407bca90 function:FUN_1407bca90"]},
    {"stamp": "20261018T051419Z", "kind": "calls", "markers": [
        "TARGET_RVA=0x7C21A0", "OUTGOING_DIRECT_CALL_EDGE_COUNT=2",
        "AnimatedCameraStartHandler::vftable", "XREF_CALL_COUNT=0"]},
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
        or meta.get("exit_code") != 0
        or meta.get("read_only") is not True
        or meta.get("auto_analysis_disabled") is not True
        or meta.get("import_attempted") is not False
        or meta.get("overwrite_attempted") is not False
        or checks.get("program_identity_matches_gog_binary") is not True
        or checks.get("script_no_error") is not True):
        raise SystemExit(f"identity/read-only/completion check failed: {stamp}")

    if spec["kind"] == "address":
        needed = ("address_in_program_memory", "address_context_complete")
        if meta.get("ok") is not True or any(checks.get(key) is not True for key in needed):
            raise SystemExit(f"address-context query incomplete: {stamp}")
    elif spec["kind"] == "slot_diagnostic":
        if (meta.get("ok") is not False
            or checks.get("vtable_slot_lookup") is not True
            or checks.get("xref_call_edge") is not False):
            raise SystemExit(f"expected vtable-slot/call-edge diagnostic changed: {stamp}")
    elif spec["kind"] == "pointer":
        needed = ("pointer_table_requested", "pointer_table_scan_complete", "pointer_table_xref_scan_complete")
        if meta.get("ok") is not True or any(checks.get(key) is not True for key in needed):
            raise SystemExit(f"pointer-table query incomplete: {stamp}")
    else:
        needed = ("function_lookup", "requested_rva_lookup", "decompilation")
        if meta.get("ok") is not True or any(checks.get(key) is not True for key in needed):
            raise SystemExit(f"function/call-edge query incomplete: {stamp}")
        if spec["kind"] == "calls" and checks.get("direct_call_edge_scan") is not True:
            raise SystemExit(f"direct-call census incomplete: {stamp}")

    stdout = ROOT / meta["artifacts"]["stdout"]
    raw = stdout.read_text(encoding="utf-8", errors="replace")
    if digest(stdout) != meta.get("stdout_sha256") or any(marker not in raw for marker in spec["markers"]):
        raise SystemExit(f"capture hash/marker validation failed: {stamp}")
    artifacts = [metadata_path] + [ROOT / relative for relative in meta["artifacts"].values()]
    if any(not path.is_file() for path in artifacts):
        raise SystemExit(f"capture artifact missing: {stamp}")
    hashes = {path.relative_to(ROOT).as_posix(): digest(path) for path in artifacts}
    row = {
        "stamp": stamp,
        "query_kind": spec["kind"],
        "query_mode": meta.get("query_mode"),
        "requested_rva": meta.get("requested_rva"),
        "requested_address_rva": meta.get("requested_address_rva"),
        "requested_vtable_slot": meta.get("requested_vtable_slot"),
        "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
        "checks": checks,
        "overall_ok": meta.get("ok"),
        "stdout_sha256": meta.get("stdout_sha256"),
        "stderr_sha256": meta.get("stderr_sha256"),
        "query_script_sha256": meta.get("query_script_sha256"),
    }
    return row, hashes


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0344" for row in evidence.get("items", [])):
        raise SystemExit("EV-0344 already registered")

    capture_rows: list[dict] = []
    local_hashes: dict[str, str] = {}
    for spec in CAPTURES:
        row, hashes = validate_capture(spec)
        capture_rows.append(row)
        local_hashes.update(hashes)

    note = TX / "EV-0344-note.md"
    put(note, f"""# EV-0344 — PlayerCharacter context receiver and camera-handler owner

## Build and method

Eight bounded queries used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BINARY}, through the strict dispatcher in read-only/no-analysis mode. The PlayerCharacter slot query resolved its requested entry, but its overall query status was false because there is no direct-call xref from a static caller; only the successful vtable-slot component is used. Separate constructor and pointer-table captures corroborate the table and target. The GOG build remains separate from Steam AE 1.6.1170.0; no RVA is transferred.

## Direct observations

- The address-context capture for global DAT_143188918 reports 2,835 analyzed references. Its two observed writes are FUN_14064cac0 (replace with the newly constructed object) and FUN_1401b98e0 (clear during teardown) [capture 20261018T050454Z]. FUN_14064cac0 allocates 0xBE8 bytes, calls FUN_14072ed70, and stores that returned pointer in DAT_143188918 [capture 20261018T050722Z].
- FUN_14072ed70 installs PlayerCharacter::vftable at the primary object base; the constructor disassembly loads address 0x1418ACD70, GOG RVA 0x18ACD70 [capture 20261018T050928Z]. Thus the constructed object placed in the global is a PlayerCharacter in this initialization path. The global is subsequently cleared by the teardown writer [captures 20261018T050601Z and 050454Z].
- PlayerCharacter primary vtable base RVA 0x18ACD70, slot index 0x6F (byte offset +0x378), returns FUN_1407371F0 at RVA 0x7371F0 [capture 20261018T051031Z; corroborated by EV-0337]. FUN_1408e6500 calls this slot on DAT_143188918 with flag zero before invoking the returned object's dynamic slot +0x150 [EV-0342].
- FUN_1407371F0 returns PC+0x8F8 for a nonzero flag. With flag zero, it delegates to FUN_1402e55a0. The helper compares the PlayerCharacter pointer with the current TLS object's +0x5F8 field; if equal, it returns TLS +0x5F0. Otherwise it returns the nested field at (PC+0x68)+0x68 when PC+0x68 is non-null, or null [EV-0337; capture 20261018T051139Z]. Its complete call census has no outgoing direct or indirect calls, which does not screen the dynamic consumer.
- The callback wrapper FUN_1407BCA90 is entry index 1 at GOG RVA 0x18BB458 within the four-entry table at RVA 0x18BB450 [capture 20261018T051326Z]. FUN_1407C21A0 allocates a 0x10-byte handler and installs AnimatedCameraStartHandler::vftable, whose table base is that address; the function has no analyzed direct code caller [capture 20261018T051419Z]. The wrapper passes its third argument and the PlayerCamera global to FUN_1408E6500 [EV-0343]. This identifies the callback owner, but not the runtime argument value or the class returned by the PlayerCharacter context getter.
- The context getter result's concrete vtable, slot +0x150 target, returned member class, and slot +0x8 finalizer remain unresolved. No captured evidence connects this AnimatedCameraStartHandler path to a ProcessTrapHit teardown site or Actor::UseSkill AV11/AV12.

## Causal assessment

The global receiver class is resolved to PlayerCharacter, and the wrapper's owner is resolved to AnimatedCameraStartHandler. This narrows the producer and use context for ThirdPersonState+0xA0, but neither competing class-family hypothesis is distinguished: a matching NiNode vtable could support Q65-H1; a different receiver table would support Q65-H2. Q64-H1/H2 remain proposed. No causal edge to ProcessTrapHit, armor skill progress, or OBJ-1 is added.

## Exact next discriminant

Trace both possible context sources: the TLS +0x5F0 object guarded by owner pointer +0x5F8, and the nested PlayerCharacter +0x68 then +0x68 member. Recover the concrete receiver vtable at FUN_1408E6500's slot +0x150 call, the result class/finalizer, and any match to one of the eight ProcessTrapHit teardown sites. Keep the AnimatedCameraStartHandler argument value dynamic until its producer is identified.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = digest(note)

    manifest = TX / "EV-0344-capture-manifest.json"
    put(manifest, json.dumps({
        "evidence_id": "EV-0344",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY,
        "captures": capture_rows,
    }, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)

    docs = {
        "README.md": "# EXP-0082 — PlayerCharacter context receiver and callback owner\n\nResolve the global PlayerCharacter receiver used by the slot+0x378 context getter and identify the owner of the wrapper that calls the ThirdPersonState slot+0x150 lookup. Keep the selected context class and returned member finalizer unresolved until a concrete table is matched.\n",
        "hypothesis.md": "# Competing models\n\n- Q65-H1: the selected context object belongs to an NiAVObject/NiNode family and slot +0x150 performs child lookup.\n- Q65-H2: the selected context object has a distinct interface implementation that shares a generic slot layout.\n\nThe callback owner is AnimatedCameraStartHandler, but both TLS and nested PlayerCharacter context sources remain possible.\n",
        "protocol.md": "# Protocol\n\nUse only the existing GOG AE 1.6.1179.0 project through the strict dispatcher with read-only/no-analysis mode. Verify the global constructor path, then accept the vtable-slot mapping only from its successful component and compare it with the independent EV-0337 table scan. Preserve the callback-table lookup as owner evidence, not as the runtime value of the selected context. Do not transfer GOG RVAs to Steam.\n",
        "results.md": "# Results\n\nFUN_14064cac0 installs a PlayerCharacter constructed by FUN_14072ed70 into DAT_143188918. PlayerCharacter slot +0x378 maps to FUN_1407371f0; its flag-zero branch selects TLS +0x5F0 when TLS +0x5F8 is the receiver, otherwise the nested PC +0x68 then +0x68 member. FUN_1407bca90 is entry 1 of AnimatedCameraStartHandler::vftable and forwards its third argument into FUN_1408e6500. The selected context class, its slot +0x150 implementation, and returned member finalizer remain unknown [EV-0344], [EV-0342], [EV-0343].\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- Matching the selected context object's concrete slot +0x150 implementation to the GOG NiNode table supports Q65-H1.\n- A different concrete table and return/finalizer family supports Q65-H2.\n- A finalizer descendant reaching Actor::UseSkill with AV11/AV12 supports Q64-H2.\n- The AnimatedCameraStartHandler label, argument refcounting, or generic slot layout alone remains inconclusive.\n",
        "implications.md": "# Implications\n\nThe slot +0x378 receiver is the constructed PlayerCharacter global, and the indirect caller is an AnimatedCameraStartHandler method. This narrows the source context but does not identify the selected object or establish a connection to physical-trap cleanup or armor skill awards.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Identify the TLS +0x5F0 object and its owner comparison at +0x5F8, or the nested PC +0x68/+0x68 member.\n2. Match the object present at FUN_1408E6500's slot +0x150 call to an exact vtable.\n3. Identify the returned member's concrete class and slot +0x8 finalizer.\n4. Compare that finalizer with the eight ProcessTrapHit teardown sites and screen resolved descendants for AV11/AV12.\n",
    }
    for name, content in docs.items():
        put(EXP / name, content)

    script_path = EXP / "register_ev_0344.py"
    local_hashes[script_path.relative_to(ROOT).as_posix()] = digest(script_path)
    for path in EXP.iterdir():
        if path.is_file():
            local_hashes[path.relative_to(ROOT).as_posix()] = digest(path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0344",
        "kind": "native",
        "source": "Read-only GOG Ghidra traces of DAT_143188918 construction, the PlayerCharacter context getter, and the AnimatedCameraStartHandler callback table.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0344-note.md",
        "sha256": digest(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Eight identity-checked query captures map the global writer/constructor path, primary PlayerCharacter slot 0x6F, TLS/nested getter, and AnimatedCameraStartHandler vtable entry. One slot query has an expected failed direct-call-xref check; its successful slot-lookup component is independently corroborated by EV-0337. The selected context/result types and runtime value remain unresolved.",
        "result": "DAT_143188918 receives an object initialized with PlayerCharacter::vftable. Its slot +0x378 flag-zero getter selects a TLS or nested PlayerCharacter field. FUN_1407bca90 is entry 1 of AnimatedCameraStartHandler::vftable and calls FUN_1408e6500 with the PlayerCamera global and its third argument. The slot +0x150 receiver class, return/finalizer, AV11/AV12 reachability, and ProcessTrapHit link remain unknown.",
        "related_evidence": ["EV-0337", "EV-0342", "EV-0343"],
        "local_hashes": local_hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L181 |" in claims or "| CL-L182 |" in claims:
        raise SystemExit("EV-0344 claims already exist")
    put(claims_path, claims.rstrip()
        + "\n| CL-L181 | In GOG AE 1.6.1179.0, FUN_14064cac0 installs an object initialized by FUN_14072ed70 with PlayerCharacter::vftable into DAT_143188918; slot +0x378 flag zero returns TLS +0x5F0 when TLS +0x5F8 matches the PlayerCharacter, otherwise a nested PlayerCharacter +0x68/+0x68 member. | supported (bounded constructor, slot, and helper trace) | [EV-0344], [EV-0342], [EV-0337] | The selected object's concrete class and slot +0x150 target remain unresolved; no AV11/AV12 result, ProcessTrapHit edge, Steam behavior, or vanilla reproduction follows. |"
        + "\n| CL-L182 | In GOG AE 1.6.1179.0, FUN_1407bca90 is entry 1 of the table at RVA 0x18BB450 installed as AnimatedCameraStartHandler::vftable by FUN_1407c21a0; it forwards its third argument to FUN_1408e6500 with the PlayerCamera global. | supported (bounded handler-vtable and caller trace) | [EV-0344], [EV-0343] | The runtime argument value and PlayerCharacter context result type remain unknown; this does not connect the callback to ProcessTrapHit or Actor::UseSkill. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    put(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0344 refines M-0065: FUN_1408e6500's slot +0x378 receiver is the PlayerCharacter global constructed by FUN_14064cac0/FUN_14072ed70. Its flag-zero getter selects a TLS +0x5F0 member guarded by owner +0x5F8, or a nested PlayerCharacter +0x68/+0x68 member. The caller wrapper is entry 1 of AnimatedCameraStartHandler::vftable. The selected object's concrete type and its slot +0x150 target remain unresolved. Claims CL-L181 and CL-L182 refine the provenance; no trap-cleanup or skill-XP edge is added.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph_path, graph_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0344 resolves the FUN_1408e6500 slot +0x378 receiver as the PlayerCharacter global and its wrapper as entry 1 of AnimatedCameraStartHandler::vftable. The flag-zero result selects TLS +0x5F0 when its +0x5F8 owner matches the PlayerCharacter, or a nested +0x68/+0x68 path. This narrows the source but leaves the slot +0x150 receiver/result class, finalizer, and ProcessTrapHit reachability unknown; neither Q64 hypothesis is resolved and Q65's NiNode comparison stays conditional. No edge to Actor::UseSkill or OBJ-1 is added. Claims CL-L181/182 -> M-0065.\n")

    index_path = ROOT / "experiments/README.md"
    put(index_path, index_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEXP-0082 / EV-0344 resolves the PlayerCharacter global receiver and AnimatedCameraStartHandler callback owner for the slot +0x150 lookup; the selected context class and returned member finalizer remain unknown.\n")

    roadmap_path = ROOT / "research/ROADMAP.md"
    put(roadmap_path, roadmap_path.read_text(encoding="utf-8").rstrip()
        + "\nEV-0344 resolves the lookup receiver to the constructed PlayerCharacter global and the wrapper to AnimatedCameraStartHandler entry 1. Its flag-zero result still selects a TLS or nested field; the selected object's vtable and returned finalizer are open. Q-0064 remains active; follow both context producers to their concrete slot+0x150 target, then reselect the P0 armor and quest-runtime lanes. Claims CL-L181/182 -> M-0065.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    q65 = next(row for row in frontier["items"] if row.get("id") == "Q-0065")
    for row in (q64, q65):
        if "EV-0344" not in row.setdefault("evidence", []):
            row["evidence"].append("EV-0344")
        for hypothesis in row.get("hypotheses", []):
            if "EV-0344" not in hypothesis.setdefault("evidence", []):
                hypothesis["evidence"].append("EV-0344")
    if "CL-L181" not in q64.setdefault("linked_claims", []):
        q64["linked_claims"].append("CL-L181")
    for claim in ("CL-L181", "CL-L182"):
        if claim not in q65.setdefault("linked_claims", []):
            q65["linked_claims"].append(claim)
    next_action = (
        "Trace both PlayerCharacter slot+0x378 flag-zero sources: the TLS +0x5F0 object guarded by owner +0x5F8, "
        "and the nested PC +0x68/+0x68 member. Recover the concrete receiver vtable at FUN_1408e6500 slot +0x150, "
        "its result class/finalizer, and any match to the eight ProcessTrapHit teardown sites. Keep the "
        "AnimatedCameraStartHandler argument value dynamic until its producer is identified."
    )
    q64["next_action"] = next_action
    q65["next_action"] = (
        "Trace the TLS +0x5F0 and nested PC +0x68/+0x68 alternatives selected by FUN_1402e55a0; map the exact "
        "slot +0x150 receiver/result vtables and compare each returned +0x8 finalizer with the NiNode candidate."
    )
    q64.setdefault("attempts", []).append({
        "action_key": "q64-playercharacter-context-global-and-handler-owner",
        "outcome": "EV-0344 maps the global receiver to the PlayerCharacter object constructed by FUN_14064cac0/FUN_14072ed70, confirms slot +0x378 flag zero, and identifies FUN_1407bca90 as AnimatedCameraStartHandler vtable entry 1. The helper selects TLS +0x5F0 when owner +0x5F8 is the PlayerCharacter, otherwise nested PC +0x68/+0x68. The concrete selected class, slot +0x150 implementation, returned finalizer, and ProcessTrapHit reachability remain unresolved.",
        "evidence": ["EV-0344"],
        "new_discriminant": "The exact context source is now narrowed to two branches; identify their concrete producers and compare the selected receiver's slot +0x150 table against NiNode before promoting Q65-H1 or H2.",
        "next_action": next_action,
    })
    q65.setdefault("attempts", []).append({
        "action_key": "q65-playercharacter-context-receiver-origin",
        "outcome": "EV-0344 identifies the PlayerCharacter global and AnimatedCameraStartHandler caller, but it does not distinguish a NiNode-compatible result from a different interface class. Both Q65 models remain proposed.",
        "evidence": ["EV-0344"],
        "new_discriminant": "Trace TLS +0x5F0/+0x5F8 and nested PC +0x68/+0x68 to the selected object's exact slot +0x150 and returned-object finalizer.",
        "next_action": q65["next_action"],
    })
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))
    print("registered EV-0344 / CL-L181-182; Q-0064 and Q-0065 remain unresolved")


if __name__ == "__main__":
    main()
