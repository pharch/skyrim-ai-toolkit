#!/usr/bin/env python3
"""Register bounded Furniture and transition camera callback traces."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0078-playercamera-furniture-transition"
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"


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
        or data.get("analysis_binary_sha256") != GOG_SHA or data.get("address_library_internal_version") != "1.6.1179.0"
        or data.get("address_library_sha256") != "3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e"
        or data.get("address_library_rva") != rva or data.get("read_only") is not True):
        raise SystemExit(f"Address Library symbol validation failed: {filename}")
    return data, {path.relative_to(ROOT).as_posix(): digest(path)}


def validate_query(stamp: str, markers: list[str]) -> tuple[dict, dict[str, str]]:
    metadata_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    if (meta.get("analysis_distribution") != "GOG" or meta.get("analysis_binary_product_version") != "1.6.1179"
        or meta.get("analysis_binary_sha256") != GOG_SHA or meta.get("exit_code") != 0 or meta.get("ok") is not True
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
        "requested_vtable_slot": meta.get("requested_vtable_slot"), "follow_direct_calls": meta.get("follow_direct_calls"),
        "checks": checks, "stdout_sha256": meta.get("stdout_sha256"), "stderr_sha256": meta.get("stderr_sha256"),
        "query_script_sha256": meta.get("query_script_sha256")}
    return row, hashes


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0340" for row in evidence.get("items", [])):
        raise SystemExit("EV-0340 already registered")

    symbols = []
    local_hashes: dict[str, str] = {}
    for filename, symbol, ae_id, rva in [
        ("address-library-20261018-furniture.stdout.raw", "VTABLE::FurnitureCameraState", 214869, "0x18F0768"),
        ("address-library-20261018-transition.stdout.raw", "VTABLE::PlayerCameraTransitionState", 214871, "0x18F07B8"),
    ]:
        data, hashes = validate_symbol(filename, symbol, ae_id, rva)
        symbols.append({"symbol": symbol, "commonlib_ae_id": ae_id, "rva": rva,
            "analysis_binary_sha256": data["analysis_binary_sha256"], "address_library_sha256": data["address_library_sha256"],
            "raw_artifact": f".local/ghidra/{filename}"})
        local_hashes.update(hashes)

    query_specs = [
        ("20261018T042907Z", ["VTABLE_BASE_RVA=0x18F0768", "VTABLE_SLOT_INDEX=0x2",
         "VTABLE_SLOT_TARGET_RVA=0x8E2DC0", "OUTGOING_DIRECT_CALL_EDGE_COUNT=3", "INDIRECT_CALL_SITE_COUNT=1",
         "FUN_1408e2dc0"]),
        ("20261018T043006Z", ["TARGET_RVA=0x8E2DC0", "CALLEE_DECOMPILATION_BEGIN=FUN_1408e5690",
         "CALLEE_DECOMPILATION_BEGIN=FUN_1408e7770", "CALLEE_DECOMPILATION_BEGIN=FUN_140682620",
         "CALLEE_DECOMPILATION_END=FUN_140682620", "FUN_1402ea5c0", "FUN_140712b20"]),
        ("20261018T043113Z", ["VTABLE_BASE_RVA=0x18F07B8", "VTABLE_SLOT_INDEX=0x2",
         "VTABLE_SLOT_TARGET_RVA=0x244650", "OUTGOING_DIRECT_CALL_EDGE_COUNT=0",
         "INDIRECT_CALL_SITE_COUNT=0", "void FUN_140244650(void)"]),
    ]
    query_rows = []
    for stamp, markers in query_specs:
        row, hashes = validate_query(stamp, markers)
        query_rows.append(row)
        local_hashes.update(hashes)

    note = TX / "EV-0340-note.md"
    put(note, f"""# EV-0340 — Furniture and transition camera callbacks

## Build and method

Two fresh Address Library probes and three bounded Ghidra queries used the existing GOG Skyrim AE 1.6.1179.0 project (analysis binary SHA-256 `{GOG_SHA}`) and matching Address Library (SHA-256 `3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e`). The probes map `VTABLE::FurnitureCameraState` to RVA `0x18F0768` and `VTABLE::PlayerCameraTransitionState` to RVA `0x18F07B8`. Their slot `+0x10` callbacks were queried with complete call-site censuses. Furniture's three direct callees were followed with a bounded query. All Ghidra queries used read-only/no-analysis mode. Raw outputs and hashes are in the private manifest; no GOG RVA is transferred to Steam 1.6.1170.0.

## Direct observations

- `FUN_1408e4240` installs FurnitureCameraState at PlayerCamera state index 5 [EV-0335]. Its vtable slot `+0x10` maps to `FUN_1408e2dc0` (RVA `0x8E2DC0`). The callback calls `FUN_1408e5690` on the object at state+0x10, resolves a handle through `FUN_1408e7770`, calls `FUN_140682620` on the resolved pointer, then decrements that pointer's reference count and may dispatch its nested vtable slot `+0x8`. The callback census records three direct calls and one indirect site [capture 20261018T042907Z].
- The three direct callees are bounded in the follow query. `FUN_1408e5690` sets a byte at receiver+0x160 based on its flag and global state. `FUN_1408e7770` resolves a handle at receiver+0x3C through `FUN_14018a7e0`. `FUN_140682620` computes/clamps a float from object flags, calls `FUN_1402ea5c0`, conditionally calls `FUN_140712b20`, and releases a nested member through slot+0x8 [capture 20261018T043006Z]. No direct Actor::UseSkill/AV11/AV12 call appears in these bounded bodies; nested finalizers and further descendants are unresolved.
- `FUN_1408e4240` installs PlayerCameraTransitionState at state index 6 [EV-0335]. Its vtable slot `+0x10` maps to return-only `FUN_140244650` (RVA `0x244650`), with zero direct and indirect call sites [capture 20261018T043113Z]. This is the same target mapped for IronSightsState slot+0x10 [EV-0339].

## Causal assessment

Furniture adds a refcounted handle cleanup path with nested dynamic slot `+0x8`; the transition state shares a no-op callback with IronSights. Neither result identifies which state is selected during ProcessTrapHit or resolves the Furniture member's finalizer. The state-specific callback bodies show no direct Actor::UseSkill AV11/AV12 sink at the captured level. Q64-H1/H2 remain proposed; no causal edge to Actor::UseSkill or OBJ-1 is added.

## Exact next discriminant

Resolve vtables and slot `+0x10` callbacks for the remaining constructor helpers in `FUN_1408e4240`, specifically state indices 2, 7, 10, and 12. Screen each callback and bounded descendants, and keep the ProcessTrapHit-selected state dynamic.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = digest(note)

    docs = {
        "README.md": "# EXP-0078 — Furniture and transition state callbacks\n\nMap FurnitureCameraState and PlayerCameraTransitionState slot+0x10 callbacks; track Furniture's nested handle finalizers and the shared transition/IronSights no-op. Remaining state constructor helpers are open.\n",
        "hypothesis.md": "# Competing models\n\n- Q64-H1: the ProcessTrapHit-selected PlayerCamera callback and descendants avoid AV11/AV12 skill progress.\n- Q64-H2: at least one selected callback or finalizer reaches Actor::UseSkill with AV11/AV12.\n\nFurniture has a dynamic nested finalizer; the transition callback is a shared no-op with IronSights. State selection remains unknown.\n",
        "protocol.md": "# Protocol\n\nUse fresh GOG-matched Address Library vtable symbols, query each slot+0x10 and complete call-site census read-only/no-analysis, and follow only bounded direct callees. Retain unresolved slot+0x8 finalizers and do not transfer GOG RVAs to Steam.\n",
        "results.md": "# Results\n\nFurnitureCameraState slot+0x10 maps to FUN_1408e2dc0 with three direct helpers and a nested +0x8 finalizer; bounded direct callees update flags, resolve handles, and compute camera floats. PlayerCameraTransitionState slot+0x10 maps to the same no-op FUN_140244650 used by IronSightsState. No direct AV11/AV12 sink appears in the captured bodies [EV-0340].\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- A selected Furniture finalizer/descendant reaching Actor::UseSkill with AV11/AV12 supports Q64-H2.\n- A fully resolved selected callback path without that sink narrows Q64-H1 only for the sampled state.\n- Unresolved finalizers, descendants, or state selection remain inconclusive.\n",
        "implications.md": "# Implications\n\nFurniture introduces another data-selected refcount/finalizer path in the state interface. The transition state shares IronSights' no-op method; neither implies that either is active during trap teardown.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Resolve the installed vtables for state indices 2, 7, 10, and 12.\n2. Map their slot+0x10 callbacks and bounded direct descendants.\n3. Identify Furniture's nested slot+0x8 target and returned member type.\n4. Establish the state selected by ProcessTrapHit before a route-wide conclusion.\n",
    }
    for name, content in docs.items():
        put(EXP / name, content)

    manifest = TX / "EV-0340-capture-manifest.json"
    put(manifest, json.dumps({"evidence_id": "EV-0340", "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": GOG_SHA, "address_library_sha256": "3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e",
        "address_library_symbols": symbols, "ghidra_captures": query_rows}, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)
    local_hashes[(EXP / "register_ev0340.py").relative_to(ROOT).as_posix()] = digest(EXP / "register_ev0340.py")
    for path in EXP.iterdir():
        if path.is_file() and path.name != "register_ev0340.py":
            local_hashes[path.relative_to(ROOT).as_posix()] = digest(path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "edition": "AE",
        "modified_state": False, "id": "EV-0340", "kind": "native",
        "source": "GOG-matched Address Library and read-only Ghidra traces of FurnitureCameraState and PlayerCameraTransitionState slot+0x10 callbacks.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0340-note.md",
        "sha256": digest(note), "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {GOG_SHA}; static only.",
        "lane": "mechanism_inference", "tools": ["tools/address_library_probe.py", "tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Two fresh GOG-matched state vtables, two complete slot+0x10 callback censuses, and a bounded follow of three Furniture direct callees. Furniture nested slot+0x8 finalizers, deeper helper descendants, remaining constructor helper states, and teardown selection remain unresolved.",
        "result": "FurnitureCameraState slot+0x10 maps to FUN_1408e2dc0 with three direct calls and one dynamic finalizer; bounded helpers perform flag, handle, and float work. PlayerCameraTransitionState slot+0x10 maps to no-op FUN_140244650, shared with IronSightsState. No direct AV11/AV12 sink appears in the sampled callback bodies. Q64-H1/H2 remain proposed.",
        "related_evidence": ["EV-0335", "EV-0338", "EV-0339"], "local_hashes": local_hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L174 |" in claims or "| CL-L175 |" in claims:
        raise SystemExit("Furniture/transition claims already exist")
    put(claims_path, claims.rstrip()
        + "\n| CL-L174 | In GOG AE 1.6.1179.0, FurnitureCameraState vtable slot +0x10 maps to FUN_1408e2dc0, which invokes three direct helpers and releases a resolved handle-derived member through a dynamic nested slot +0x8. | supported (bounded vtable and direct-callee trace) | [EV-0340], [EV-0335] | The nested finalizer, further descendants, and ProcessTrapHit state selection remain unresolved; no Q64-H1/H2 result follows. |"
        + "\n| CL-L175 | In GOG AE 1.6.1179.0, PlayerCameraTransitionState vtable slot +0x10 maps to return-only FUN_140244650, the same no-op target used by IronSightsState. | supported (bounded vtable trace) | [EV-0340], [EV-0339], [EV-0335] | Other state callbacks and ProcessTrapHit state selection remain unresolved; no route-wide AV11/AV12 exclusion follows. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    put(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0340 extends M-0064 with FurnitureCameraState and PlayerCameraTransitionState. Furniture resolves a handle, applies a bounded float update, and performs a nested slot+0x8 finalizer; transition reuses the no-op callback shared with IronSights. Furniture's exact finalizer and state selection remain open. Claims CL-L174 and CL-L175 -> M-0064.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph_path, graph_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0340 maps FurnitureCameraState slot+0x10 to a handle-derived float/update path with a nested dynamic finalizer. PlayerCameraTransitionState shares the no-op FUN_140244650 target with IronSightsState [EV-0339]. No direct AV11/AV12 edge is added; Furniture's finalizer, remaining state callbacks, and teardown selection remain unresolved. No edge to OBJ-1 is supported. Claims CL-L174 and CL-L175 -> M-0064.\n")

    index_path = ROOT / "experiments/README.md"
    put(index_path, index_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEXP-0078 / EV-0340 maps FurnitureCameraState and PlayerCameraTransitionState slot+0x10 callbacks; Furniture's nested finalizer and state indices 2, 7, 10, and 12 remain open.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    if "EV-0340" not in q64.setdefault("evidence", []): q64["evidence"].append("EV-0340")
    for claim_id in ("CL-L174", "CL-L175"):
        if claim_id not in q64.setdefault("linked_claims", []): q64["linked_claims"].append(claim_id)
    for hypothesis in q64.get("hypotheses", []):
        if "EV-0340" not in hypothesis.setdefault("evidence", []): hypothesis["evidence"].append("EV-0340")
    q64["next_action"] = ("Resolve the vtables and slot+0x10 callbacks for the remaining constructor helpers in FUN_1408e4240, "
        "specifically state indices 2, 7, 10, and 12. Screen each callback and bounded descendants, and keep the "
        "ProcessTrapHit-selected state and unresolved member finalizers dynamic.")
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    with (ROOT / "research/SESSION_LOG.md").open("a", encoding="utf-8") as stream:
        stream.write("\n- " + datetime.now(timezone.utc).isoformat(timespec="seconds")
            + " TX-20261017-0011 research update: EV-0340 / CL-L174 / CL-L175 registered. FurnitureCameraState slot+0x10 resolves a handle and applies float/state helpers before a dynamic nested +0x8 finalizer; PlayerCameraTransitionState shares IronSights' no-op callback. No direct AV11/AV12 sink is shown; Q64-H1/H2 remain proposed. Next: resolve state indices 2, 7, 10, and 12 from the PlayerCamera initializer.\n")
    print("registered EV-0340 / CL-L174 / CL-L175; Q-0064 remains open")


if __name__ == "__main__":
    main()
