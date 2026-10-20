#!/usr/bin/env python3
"""Register bounded FirstPerson and Bleedout camera callback traces."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0076-playercamera-state-callback-census"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
LIBRARY = "3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def validate_address_symbol(filename: str, symbol: str, ae_id: int, rva: str) -> tuple[dict, dict[str, str]]:
    path = GH / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    if (data.get("ok") is not True or data.get("symbol") != symbol or data.get("commonlib_ae_id") != ae_id
        or data.get("analysis_distribution") != "GOG" or data.get("analysis_binary_product_version") != "1.6.1179.0"
        or data.get("analysis_binary_sha256") != BINARY or data.get("address_library_internal_version") != "1.6.1179.0"
        or data.get("address_library_sha256") != LIBRARY or data.get("address_library_rva") != rva
        or data.get("read_only") is not True):
        raise SystemExit(f"Address Library identity/symbol check failed: {filename}")
    return data, {path.relative_to(ROOT).as_posix(): digest(path)}


def validate_ghidra(stamp: str, markers: list[str]) -> tuple[dict, dict[str, str]]:
    metadata_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    if (meta.get("analysis_distribution") != "GOG" or meta.get("analysis_binary_product_version") != "1.6.1179"
        or meta.get("analysis_binary_sha256") != BINARY or meta.get("exit_code") != 0 or meta.get("ok") is not True
        or meta.get("read_only") is not True or meta.get("auto_analysis_disabled") is not True
        or meta.get("import_attempted") is not False or meta.get("overwrite_attempted") is not False
        or checks.get("program_identity_matches_gog_binary") is not True or checks.get("script_no_error") is not True
        or checks.get("direct_call_edge_scan") is not True or checks.get("decompilation") is not True):
        raise SystemExit(f"Ghidra identity/read-only/call/decompilation check failed: {stamp}")
    stdout = ROOT / meta["artifacts"]["stdout"]
    raw = stdout.read_text(encoding="utf-8", errors="replace")
    if digest(stdout) != meta.get("stdout_sha256") or any(marker not in raw for marker in markers):
        raise SystemExit(f"Ghidra capture/hash/marker failure: {stamp}")
    files = [metadata_path] + [ROOT / relative for relative in meta["artifacts"].values()]
    if any(not path.is_file() for path in files):
        raise SystemExit(f"missing Ghidra artifact: {stamp}")
    hashes = {path.relative_to(ROOT).as_posix(): digest(path) for path in files}
    row = {"stamp": stamp, "query_mode": meta.get("query_mode"), "requested_rva": meta.get("requested_rva"),
        "requested_vtable_slot": meta.get("requested_vtable_slot"), "follow_direct_calls": meta.get("follow_direct_calls"),
        "checks": checks, "stdout_sha256": meta.get("stdout_sha256"), "stderr_sha256": meta.get("stderr_sha256"),
        "query_script_sha256": meta.get("query_script_sha256")}
    return row, hashes


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0338" for row in evidence.get("items", [])):
        raise SystemExit("EV-0338 already registered")

    address_rows = []
    local_hashes: dict[str, str] = {}
    for filename, symbol, ae_id, rva in [
        ("address-library-20261018-firstperson.stdout.raw", "VTABLE::FirstPersonState", 214855, "0x18F05A8"),
        ("address-library-20261018-bleedout.stdout.raw", "VTABLE::BleedoutCameraState", 214873, "0x18F0808"),
    ]:
        data, hashes = validate_address_symbol(filename, symbol, ae_id, rva)
        address_rows.append({"symbol": symbol, "commonlib_ae_id": ae_id, "rva": rva,
            "analysis_binary_sha256": data["analysis_binary_sha256"], "address_library_sha256": data["address_library_sha256"],
            "raw_artifact": f".local/ghidra/{filename}"})
        local_hashes.update(hashes)

    captures = [
        ("20261018T041941Z", ["VTABLE_BASE_RVA=0x18F05A8", "VTABLE_SLOT_INDEX=0x2",
         "VTABLE_SLOT_TARGET_RVA=0x8E0E70", "OUTGOING_DIRECT_CALL_EDGE_COUNT=1",
         "INDIRECT_CALL_SITE_COUNT=0", "FUN_1408e0e70"]),
        ("20261018T042053Z", ["VTABLE_BASE_RVA=0x18F0808", "VTABLE_SLOT_INDEX=0x2",
         "VTABLE_SLOT_TARGET_RVA=0x8E03D0", "OUTGOING_DIRECT_CALL_EDGE_COUNT=3",
         "INDIRECT_CALL_SITE_COUNT=1", "param_1 + 0x120"]),
        ("20261018T042154Z", ["TARGET_RVA=0x8E03D0",
         "CALLEE_DECOMPILATION_BEGIN=FUN_1407f5770", "CALLEE_DECOMPILATION_BEGIN=FUN_140cb0fe0",
         "CALLEE_DECOMPILATION_BEGIN=FUN_140920df0", "CALLEE_DECOMPILATION_END=FUN_140920df0"]),
    ]
    capture_rows = []
    for stamp, markers in captures:
        row, hashes = validate_ghidra(stamp, markers)
        capture_rows.append(row)
        local_hashes.update(hashes)

    note = TX / "EV-0338-note.md"
    put(note, f"""# EV-0338 — FirstPerson and Bleedout camera state callbacks

## Build and method

Two CommonLib Address Library symbol probes and three bounded Ghidra queries used the matching GOG Skyrim AE 1.6.1179.0 executable (SHA-256 `{BINARY}`) and Address Library (SHA-256 `{LIBRARY}`). Queries used the existing project in read-only mode with auto-analysis disabled. The Address Library maps `VTABLE::FirstPersonState` to RVA `0x18F05A8` and `VTABLE::BleedoutCameraState` to RVA `0x18F0808`. Both vtable slot `+0x10` entries were queried together with complete direct/indirect call-site censuses; Bleedout's three direct targets were followed in a bounded query. The private manifest records the raw symbol outputs and all Ghidra capture hashes. No GOG RVA is transferred to Steam 1.6.1170.0.

## Direct observations

- `FirstPersonState` is installed at PlayerCamera state index 0 by `FUN_1408e4240` [EV-0335]. Its vtable slot `+0x10` resolves to `FUN_1408e0e70` (RVA `0x8E0E70`). That method clears `FirstPersonState+0x68`, then conditionally calls `FUN_14079e5a0(global, state+0x20)`. Its complete body census has one direct call and zero indirect sites [capture 20261018T041941Z]. `FUN_14079e5a0` is the array insert/remove helper already mapped in EV-0336; its deeper generic container descendants are not resolved here.
- `BleedoutCameraState` is installed at PlayerCamera state index 11 by `FUN_1408e4240` [EV-0335]. Its vtable slot `+0x10` resolves to `FUN_1408e03d0` (RVA `0x8E03D0`). The method clears `BleedoutCameraState+0x120`, decrements the old member's reference count, and calls its dynamic slot `+0x8` if final. It then makes three direct calls and has one indirect call site total [capture 20261018T042053Z].
- The three direct Bleedout callees are captured: `FUN_1407f5770` updates a float pair and conditionally calls `FUN_140ccb2a0`; `FUN_140cb0fe0` updates a small state and calls `FUN_140cb1f50` and `FUN_140cb3290`; `FUN_140920df0` delegates the `"VATSPlayback"` string to `FUN_140922090` [capture 20261018T042154Z]. These bodies contain no direct Actor::UseSkill/AV11/AV12 call. The displayed descendants are bounded to the three direct callees; their own further descendants and the +0x120 finalizer remain open.
- Neither state callback establishes a direct causal path to armor skill credit. FirstPerson's shared array helper, Bleedout's +0x120 finalizer, and the transitive helper descendants remain unresolved. The teardown-selected state is still dynamic under the PlayerCamera transition contract [EV-0335].

## Causal assessment

The PlayerCamera state interface now has three separately mapped `+0x10` branches: AutoVanity from EV-0330, ThirdPerson from EV-0335, and FirstPerson/Bleedout from this evidence. Their target bodies perform distinct HUD, camera, array, playback/event, or member-release work. This does not establish that every initialized state is covered, that a particular one is selected by ProcessTrapHit, or that all relevant descendants avoid AV11/AV12. Q64-H1/H2 remain proposed; no causal edge to Actor::UseSkill or OBJ-1 is added.

## Exact next discriminant

Map slot `+0x10` callbacks for the remaining initialized PlayerCamera state vtables, starting with FreeCameraState and IronSightsState, and screen their direct bodies and bounded descendants for Actor::UseSkill AV11/AV12. Keep the state selected at teardown dynamic until its runtime/data selection is established.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = digest(note)

    docs = {
        "README.md": "# EXP-0076 — PlayerCamera state callback census\n\nMap FirstPersonState and BleedoutCameraState slot+0x10 targets and screen bounded descendants. Other initialized state vtables and teardown selection remain open.\n",
        "hypothesis.md": "# Competing models\n\n- Q64-H1: none of the state callback descendants selected during ProcessTrapHit routes AV11/AV12 into skill progress.\n- Q64-H2: at least one selected callback/finalizer reaches Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.\n\nFirstPerson and Bleedout have distinct callback shapes. Neither callback selection nor all other state implementations are established.\n",
        "protocol.md": "# Protocol\n\nResolve each vtable from a fresh GOG-matched Address Library probe, query slot+0x10 in the existing GOG project read-only/no-analysis, and retain direct/indirect call-site census. Follow only bounded direct callees. Do not transfer GOG RVAs to Steam or generalize the sampled states to the whole camera state array.\n",
        "results.md": "# Results\n\nFirstPersonState slot+0x10 maps to FUN_1408e0e70, which clears +0x68 and calls the mapped array helper; its body has zero indirect sites. BleedoutCameraState slot+0x10 maps to FUN_1408e03d0, which final-releases +0x120 through an unresolved slot+0x8 and calls three playback/event helpers. No direct AV11/AV12 sink appears in the captured callback bodies or three direct Bleedout callees. Other descendants, the finalizer, and teardown state selection remain open [EV-0338].\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- A resolved selected-state target/finalizer path with Actor::UseSkill and AV11/AV12 supports Q64-H2.\n- Exact selected-state paths without a skill sink narrow Q64-H1 only for those states and descendants screened.\n- Unresolved finalizers, helper descendants, or state selection remain inconclusive.\n",
        "implications.md": "# Implications\n\nPlayerCamera state callbacks are class-specific; the FirstPerson, ThirdPerson, AutoVanity, and Bleedout bodies cannot be collapsed into one cleanup mechanism. A no-direct-sink result for a callback does not exclude its finalizer or an unexamined state.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Enumerate the remaining state vtables constructed by FUN_1408e4240.\n2. Resolve each slot+0x10 callback and bounded direct descendants.\n3. Identify finalizer targets for state members released through slot+0x8.\n4. Establish which state is selected in the ProcessTrapHit teardown context before making a route-wide conclusion.\n",
    }
    for name, content in docs.items():
        put(EXP / name, content)

    manifest = TX / "EV-0338-capture-manifest.json"
    put(manifest, json.dumps({"evidence_id": "EV-0338", "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY, "address_library_sha256": LIBRARY,
        "address_library_symbols": address_rows, "ghidra_captures": capture_rows}, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)
    local_hashes[(EXP / "register_ev0338.py").relative_to(ROOT).as_posix()] = digest(EXP / "register_ev0338.py")
    for path in EXP.iterdir():
        if path.is_file() and path.name != "register_ev0338.py":
            local_hashes[path.relative_to(ROOT).as_posix()] = digest(path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "edition": "AE",
        "modified_state": False, "id": "EV-0338", "kind": "native",
        "source": "GOG-matched Address Library and read-only Ghidra traces of FirstPersonState and BleedoutCameraState slot+0x10 callbacks.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0338-note.md",
        "sha256": digest(note), "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference", "tools": ["tools/address_library_probe.py", "tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Two fresh GOG-matched vtable symbols, two complete slot+0x10 callback censuses, and a bounded follow of three Bleedout direct callees. The other initialized camera states, transitive helper descendants, the Bleedout member finalizer, and teardown-selected state remain unresolved.",
        "result": "FirstPersonState slot+0x10 maps to FUN_1408e0e70 (one direct helper, no indirect sites); BleedoutCameraState slot+0x10 maps to FUN_1408e03d0 (three direct helpers and one +0x8 member finalizer). No direct Actor::UseSkill/AV11/AV12 sink appears in the captured bodies. Q64-H1/H2 remain proposed.",
        "related_evidence": ["EV-0330", "EV-0335", "EV-0336", "EV-0337"], "local_hashes": local_hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L170 |" in claims or "| CL-L171 |" in claims:
        raise SystemExit("camera-state claims already exist")
    put(claims_path, claims.rstrip()
        + "\n| CL-L170 | In GOG AE 1.6.1179.0, FirstPersonState vtable slot +0x10 maps to FUN_1408e0e70, which clears +0x68 and conditionally calls FUN_14079e5a0; its complete callback body has no indirect sites. | supported (bounded vtable and call trace) | [EV-0338], [EV-0335], [EV-0336] | The helper's deeper container descendants and teardown state selection remain unresolved; no Q64-H1/H2 result or AV11/AV12 exclusion follows. |"
        + "\n| CL-L171 | In GOG AE 1.6.1179.0, BleedoutCameraState vtable slot +0x10 maps to FUN_1408e03d0, which clears/refcount-releases +0x120 through a dynamic slot +0x8, then calls three playback/event helpers. | supported (bounded vtable and direct-callee trace) | [EV-0338], [EV-0335] | The +0x120 finalizer, deeper helper descendants, and teardown-selected state remain unresolved; no Q64-H1/H2 result or AV11/AV12 exclusion follows. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    put(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0338 extends M-0064 with two state-specific slot+0x10 callbacks. FirstPersonState clears +0x68 and calls the shared array helper; BleedoutCameraState releases +0x120 through slot+0x8 and calls playback/event helpers. Their callback bodies have no direct Actor::UseSkill AV11/AV12 sink, but the Bleedout finalizer, shared helper descendants, other initialized states, and state selection remain open. Claims CL-L170 and CL-L171 -> M-0064.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph_path, graph_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0338 maps FirstPersonState and BleedoutCameraState slot+0x10 targets under the PlayerCamera transition interface [EV-0335]. FirstPerson performs a field clear and array update; Bleedout releases a +0x120 member through a dynamic finalizer and runs playback/event helpers. These are distinct per-state cleanup branches; the selected state, Bleedout finalizer, and further descendants remain open. No causal edge to Actor::UseSkill AV11/AV12 or OBJ-1 is added. Claims CL-L170 and CL-L171 -> M-0064.\n")

    index_path = ROOT / "experiments/README.md"
    put(index_path, index_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEXP-0076 / EV-0338 maps FirstPersonState and BleedoutCameraState slot+0x10 callbacks. Other camera states, the Bleedout finalizer, and teardown state selection remain open.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    if "EV-0338" not in q64.setdefault("evidence", []): q64["evidence"].append("EV-0338")
    for claim_id in ("CL-L170", "CL-L171"):
        if claim_id not in q64.setdefault("linked_claims", []): q64["linked_claims"].append(claim_id)
    for hypothesis in q64.get("hypotheses", []):
        if "EV-0338" not in hypothesis.setdefault("evidence", []): hypothesis["evidence"].append("EV-0338")
    q64["next_action"] = ("Resolve slot+0x10 callbacks for remaining PlayerCamera states initialized by FUN_1408e4240, starting with "
        "FreeCameraState and IronSightsState; screen their bodies and bounded descendants for Actor::UseSkill AV11/AV12. "
        "Keep all unresolved member finalizers and the ProcessTrapHit-selected state dynamic.")
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    with (ROOT / "research/SESSION_LOG.md").open("a", encoding="utf-8") as stream:
        stream.write("\n- " + datetime.now(timezone.utc).isoformat(timespec="seconds")
            + " TX-20261017-0011 research update: EV-0338 / CL-L170 / CL-L171 registered. FirstPersonState slot+0x10 clears +0x68 and calls the array helper with no indirect site; BleedoutCameraState slot+0x10 releases +0x120 through a dynamic +0x8 finalizer and calls bounded playback/event helpers. No direct AV11/AV12 sink appears in these callback bodies. Q64-H1/H2 remain proposed. Next: map FreeCameraState and IronSightsState slot+0x10 callbacks.\n")
    print("registered EV-0338 / CL-L170 / CL-L171; Q-0064 remains open")


if __name__ == "__main__":
    main()
