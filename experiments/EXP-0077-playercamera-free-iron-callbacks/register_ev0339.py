#!/usr/bin/env python3
"""Register bounded FreeCamera and IronSights state callback traces."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0077-playercamera-free-iron-callbacks"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
LIBRARY = "3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def validate_symbol(filename: str, symbol: str, ae_id: int, rva: str) -> tuple[dict, dict[str, str]]:
    path = GH / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    if (data.get("ok") is not True or data.get("symbol") != symbol or data.get("commonlib_ae_id") != ae_id
        or data.get("analysis_distribution") != "GOG" or data.get("analysis_binary_product_version") != "1.6.1179.0"
        or data.get("analysis_binary_sha256") != BINARY or data.get("address_library_internal_version") != "1.6.1179.0"
        or data.get("address_library_sha256") != LIBRARY or data.get("address_library_rva") != rva
        or data.get("read_only") is not True):
        raise SystemExit(f"Address Library symbol validation failed: {filename}")
    return data, {path.relative_to(ROOT).as_posix(): digest(path)}


def validate_query(stamp: str, markers: list[str]) -> tuple[dict, dict[str, str]]:
    metadata_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    if (meta.get("analysis_distribution") != "GOG" or meta.get("analysis_binary_product_version") != "1.6.1179"
        or meta.get("analysis_binary_sha256") != BINARY or meta.get("exit_code") != 0 or meta.get("ok") is not True
        or meta.get("read_only") is not True or meta.get("auto_analysis_disabled") is not True
        or meta.get("import_attempted") is not False or meta.get("overwrite_attempted") is not False
        or checks.get("program_identity_matches_gog_binary") is not True or checks.get("script_no_error") is not True
        or checks.get("direct_call_edge_scan") is not True or checks.get("decompilation") is not True):
        raise SystemExit(f"Ghidra query validation failed: {stamp}")
    stdout = ROOT / meta["artifacts"]["stdout"]
    raw = stdout.read_text(encoding="utf-8", errors="replace")
    if digest(stdout) != meta.get("stdout_sha256") or any(marker not in raw for marker in markers):
        raise SystemExit(f"Ghidra stdout hash/marker validation failed: {stamp}")
    files = [metadata_path] + [ROOT / relative for relative in meta["artifacts"].values()]
    if any(not path.is_file() for path in files):
        raise SystemExit(f"Ghidra artifact missing: {stamp}")
    hashes = {path.relative_to(ROOT).as_posix(): digest(path) for path in files}
    row = {"stamp": stamp, "query_mode": meta.get("query_mode"), "requested_rva": meta.get("requested_rva"),
        "requested_vtable_slot": meta.get("requested_vtable_slot"), "checks": checks,
        "stdout_sha256": meta.get("stdout_sha256"), "stderr_sha256": meta.get("stderr_sha256"),
        "query_script_sha256": meta.get("query_script_sha256")}
    return row, hashes


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0339" for row in evidence.get("items", [])):
        raise SystemExit("EV-0339 already registered")

    symbols = []
    local_hashes: dict[str, str] = {}
    for filename, symbol, ae_id, rva in [
        ("address-library-20261018-freecamera.stdout.raw", "VTABLE::FreeCameraState", 214863, "0x18F0698"),
        ("address-library-20261018-ironsights.stdout.raw", "VTABLE::IronSightsState", 214867, "0x18F0718"),
    ]:
        data, hashes = validate_symbol(filename, symbol, ae_id, rva)
        symbols.append({"symbol": symbol, "commonlib_ae_id": ae_id, "rva": rva,
            "analysis_binary_sha256": data["analysis_binary_sha256"], "address_library_sha256": data["address_library_sha256"],
            "raw_artifact": f".local/ghidra/{filename}"})
        local_hashes.update(hashes)

    query_specs = [
        ("20261018T042444Z", ["VTABLE_BASE_RVA=0x18F0698", "VTABLE_SLOT_INDEX=0x2",
         "VTABLE_SLOT_TARGET_RVA=0x8E2480", "OUTGOING_DIRECT_CALL_EDGE_COUNT=2", "INDIRECT_CALL_SITE_COUNT=0",
         "FUN_14079e5a0", "FUN_140cd7210"]),
        ("20261018T042540Z", ["VTABLE_BASE_RVA=0x18F0718", "VTABLE_SLOT_INDEX=0x2",
         "VTABLE_SLOT_TARGET_RVA=0x244650", "OUTGOING_DIRECT_CALL_EDGE_COUNT=0", "INDIRECT_CALL_SITE_COUNT=0",
         "void FUN_140244650(void)"]),
        ("20261018T042644Z", ["TARGET_RVA=0xCD7210", "OUTGOING_DIRECT_CALL_EDGE_COUNT=0",
         "INDIRECT_CALL_SITE_COUNT=0", "DIRECT_CALL_EDGE_SCAN_COMPLETE=true",
         "*(undefined4 *)(param_1 + 0x120) = param_2", "*(undefined4 *)(param_1 + 0x124) = param_3"]),
    ]
    query_rows = []
    for stamp, markers in query_specs:
        row, hashes = validate_query(stamp, markers)
        query_rows.append(row)
        local_hashes.update(hashes)

    note = TX / "EV-0339-note.md"
    put(note, f"""# EV-0339 — FreeCamera and IronSights state callbacks

## Build and method

Two fresh Address Library probes and three bounded Ghidra queries used the existing GOG Skyrim AE 1.6.1179.0 project (analysis binary SHA-256 `{BINARY}`) and matching Address Library (SHA-256 `{LIBRARY}`). The probes map `VTABLE::FreeCameraState` to RVA `0x18F0698` and `VTABLE::IronSightsState` to RVA `0x18F0718`. Both slot `+0x10` callbacks were queried with complete direct/indirect call-site censuses; the FreeCamera callback's `FUN_140cd7210` helper was separately traced. All Ghidra queries used read-only/no-analysis mode. Raw outputs and hashes are in the private manifest. No GOG RVA is transferred to Steam 1.6.1170.0.

## Direct observations

- `FUN_1408e4240` installs FreeCameraState at PlayerCamera state index 3 [EV-0335]. Its vtable slot `+0x10` maps to `FUN_1408e2480` (RVA `0x8E2480`). The method conditionally calls the shared array helper `FUN_14079e5a0` with `state+0x20`, writes two globals, and conditionally calls `FUN_140cd7210`. Its complete body has two direct calls and no indirect sites [capture 20261018T042444Z].
- `FUN_140cd7210` has zero outgoing direct calls and zero indirect sites. Its body stores the two supplied 32-bit values at receiver offsets `+0x120` and `+0x124`; it does not call a skill-progress routine [capture 20261018T042644Z]. The array helper was previously mapped in EV-0336; its deeper generic container descendants remain unresolved.
- `FUN_1408e4240` installs IronSightsState at PlayerCamera state index 4 [EV-0335]. Its vtable slot `+0x10` maps to `FUN_140244650` (RVA `0x244650`), whose body is a return-only no-op with zero direct and indirect call sites [capture 20261018T042540Z].
- Neither captured callback body has a direct Actor::UseSkill/AV11/AV12 call. This does not resolve other state classes, the PlayerCamera state selected by ProcessTrapHit, or descendants of shared helpers such as `FUN_14079e5a0`.

## Causal assessment

FreeCamera and IronSights add two more distinct callbacks to the PlayerCamera slot `+0x10` interface [EV-0335]. Their bounded bodies do not explain armor skill credit. Together with AutoVanity, ThirdPerson, FirstPerson, and Bleedout, they narrow only the sampled state branches. Q64-H1/H2 remain proposed; no route-wide no-skill conclusion or causal edge to OBJ-1 is established.

## Exact next discriminant

Resolve the slot `+0x10` callbacks for the remaining PlayerCamera states initialized by `FUN_1408e4240`, prioritizing FurnitureCameraState and PlayerCameraTransitionState, then cover unnamed constructor helpers by their exact installed vtables. Keep the ProcessTrapHit-selected state and unresolved shared-helper descendants dynamic.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = digest(note)

    docs = {
        "README.md": "# EXP-0077 — FreeCamera and IronSights callbacks\n\nMap the FreeCameraState and IronSightsState slot+0x10 targets and screen their bounded direct bodies. Other PlayerCamera states and teardown selection remain open.\n",
        "hypothesis.md": "# Competing models\n\n- Q64-H1: the ProcessTrapHit-selected PlayerCamera callback and its descendants do not route AV11/AV12 into skill progress.\n- Q64-H2: at least one selected callback/finalizer reaches Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.\n\nThe two callbacks mapped here show no direct skill sink; selection and unexamined descendants remain unresolved.\n",
        "protocol.md": "# Protocol\n\nResolve vtables through the fresh GOG-matched Address Library. Query slot+0x10 and a complete call-site census in the existing GOG project read-only/no-analysis. Follow only direct descendants required to screen a callback. Do not transfer RVAs to Steam or generalize sampled states to all of PlayerCamera.\n",
        "results.md": "# Results\n\nFreeCameraState slot+0x10 maps to FUN_1408e2480, with two direct calls and no indirect sites. Its FUN_140cd7210 helper only writes +0x120/+0x124 and itself has no calls. IronSightsState slot+0x10 maps to return-only FUN_140244650 with no calls. The shared array helper's descendants, other states, and teardown selection remain open [EV-0339].\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- A selected state callback/finalizer reaching Actor::UseSkill with AV11/AV12 supports Q64-H2.\n- No skill sink in a fully resolved selected-state path narrows Q64-H1 for that state only.\n- Unresolved shared helper descendants or unknown state selection remain inconclusive.\n",
        "implications.md": "# Implications\n\nThe sampled state callbacks continue to show per-class behavior. The FreeCamera and IronSights bodies do not add a direct path to armor skill progress, but neither result can substitute for the state actually selected during ProcessTrapHit.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Map FurnitureCameraState and PlayerCameraTransitionState slot+0x10 targets.\n2. Recover exact vtables installed by the remaining state constructor helpers.\n3. Screen shared helper descendants and member finalizers for AV11/AV12.\n4. Identify the state selected at the trap teardown callsite before making a route-wide conclusion.\n",
    }
    for name, content in docs.items():
        put(EXP / name, content)

    manifest = TX / "EV-0339-capture-manifest.json"
    put(manifest, json.dumps({"evidence_id": "EV-0339", "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY, "address_library_sha256": LIBRARY,
        "address_library_symbols": symbols, "ghidra_captures": query_rows}, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)
    local_hashes[(EXP / "register_ev0339.py").relative_to(ROOT).as_posix()] = digest(EXP / "register_ev0339.py")
    for path in EXP.iterdir():
        if path.is_file() and path.name != "register_ev0339.py":
            local_hashes[path.relative_to(ROOT).as_posix()] = digest(path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "edition": "AE",
        "modified_state": False, "id": "EV-0339", "kind": "native",
        "source": "GOG-matched Address Library and read-only Ghidra traces of FreeCameraState and IronSightsState slot+0x10 callbacks.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0339-note.md",
        "sha256": digest(note), "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference", "tools": ["tools/address_library_probe.py", "tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Two fresh GOG-matched state vtables, two complete slot+0x10 callback censuses, and one complete direct/indirect census of the FreeCamera field-store helper. Unexamined state callbacks and shared array-helper descendants remain open.",
        "result": "FreeCameraState slot+0x10 maps to FUN_1408e2480 (two direct calls, zero indirect sites); FUN_140cd7210 only stores fields +0x120/+0x124 and has zero calls. IronSightsState slot+0x10 maps to no-op FUN_140244650. No direct AV11/AV12 sink appears in these bodies. Q64-H1/H2 remain proposed.",
        "related_evidence": ["EV-0335", "EV-0336", "EV-0338"], "local_hashes": local_hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L172 |" in claims or "| CL-L173 |" in claims:
        raise SystemExit("FreeCamera/IronSights claims already exist")
    put(claims_path, claims.rstrip()
        + "\n| CL-L172 | In GOG AE 1.6.1179.0, FreeCameraState vtable slot +0x10 maps to FUN_1408e2480, which calls the mapped array helper and a no-call field-store helper FUN_140cd7210; the callback body has no indirect sites. | supported (bounded vtable and helper trace) | [EV-0339], [EV-0335], [EV-0336] | Shared array-helper descendants and ProcessTrapHit state selection remain unresolved; no Q64-H1/H2 result follows. |"
        + "\n| CL-L173 | In GOG AE 1.6.1179.0, IronSightsState vtable slot +0x10 maps to return-only FUN_140244650, with zero direct and indirect call sites. | supported (bounded vtable and call trace) | [EV-0339], [EV-0335] | Other PlayerCamera state callbacks and ProcessTrapHit state selection remain unresolved; no route-wide AV11/AV12 exclusion follows. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    put(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0339 extends M-0064 with FreeCameraState and IronSightsState callbacks. FreeCamera updates its state arrays and two fields through a no-call helper; IronSights uses a return-only slot+0x10 target. Neither sampled body contains a direct AV11/AV12 sink. Other state classes, shared array-helper descendants, member finalizers, and teardown selection remain open. Claims CL-L172 and CL-L173 -> M-0064.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph_path, graph_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0339 maps FreeCameraState and IronSightsState slot+0x10 callbacks under the PlayerCamera transition interface [EV-0335]. FreeCamera's `FUN_140cd7210` descendant only stores two fields; IronSights' callback is a no-op. These branches add no direct edge to Actor::UseSkill AV11/AV12, while the shared array helper, other state callbacks, and state selection remain unresolved. No edge to OBJ-1 is added. Claims CL-L172 and CL-L173 -> M-0064.\n")

    index_path = ROOT / "experiments/README.md"
    put(index_path, index_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEXP-0077 / EV-0339 maps FreeCameraState and IronSightsState slot+0x10 callbacks; shared helpers and remaining camera states are still open.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    if "EV-0339" not in q64.setdefault("evidence", []): q64["evidence"].append("EV-0339")
    for claim_id in ("CL-L172", "CL-L173"):
        if claim_id not in q64.setdefault("linked_claims", []): q64["linked_claims"].append(claim_id)
    for hypothesis in q64.get("hypotheses", []):
        if "EV-0339" not in hypothesis.setdefault("evidence", []): hypothesis["evidence"].append("EV-0339")
    q64["next_action"] = ("Resolve slot+0x10 callbacks for remaining PlayerCamera states initialized by FUN_1408e4240, "
        "prioritizing FurnitureCameraState and PlayerCameraTransitionState; recover exact vtables for unnamed constructor "
        "helpers. Screen callbacks and bounded descendants for Actor::UseSkill AV11/AV12 while keeping teardown selection dynamic.")
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    with (ROOT / "research/SESSION_LOG.md").open("a", encoding="utf-8") as stream:
        stream.write("\n- " + datetime.now(timezone.utc).isoformat(timespec="seconds")
            + " TX-20261017-0011 research update: EV-0339 / CL-L172 / CL-L173 registered. FreeCameraState slot+0x10 has two direct calls and no indirect sites; its second helper only writes +0x120/+0x124. IronSightsState slot+0x10 is a no-op. No direct AV11/AV12 sink appears in the sampled bodies; Q64-H1/H2 remain proposed. Next: FurnitureCameraState and PlayerCameraTransitionState callbacks.\n")
    print("registered EV-0339 / CL-L172 / CL-L173; Q-0064 remains open")


if __name__ == "__main__":
    main()
