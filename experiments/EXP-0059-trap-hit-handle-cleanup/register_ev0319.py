from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TX = ROOT / ".local/alignment/transactions/TX-20261017-0005"
NOTE = TX / "EV-0319-note.md"
MANIFEST = TX / "EV-0319-capture-manifest.json"
REGISTER = ROOT / "research/EVIDENCE.json"
CAPTURE_PREFIXES = (
    "gog-query-20261017T172909Z",  # receiver first two cleanup sites
    "gog-query-20261017T173153Z",  # handle construction / generic handle helpers
    "gog-query-20261017T173441Z",  # HitData handle lookup
    "gog-query-20261017T173705Z",  # BSHandleRefObject vtable
    "gog-query-20261017T173914Z",  # PlayerCharacter primary-vtable references
    "gog-query-20261017T174103Z",  # PlayerCharacter constructor and secondary tables
    "gog-query-20261017T174305Z",  # PlayerCharacter secondary vtable slot 1
    "gog-query-20261017T174509Z",  # common slot-1 dispose thunk
    "gog-query-20261017T174707Z",  # PlayerCharacter slot-0 adjustor thunk
    "gog-query-20261017T174900Z",  # PlayerCharacter destructor and teardown census
    "gog-query-20261017T175129Z",  # ProcessTrapHit builder and caller
    "gog-query-20261015T202055Z",  # HitData initializer
    "gog-query-20261016T000347Z",  # first builder helper reads and writes
    "gog-query-20261016T001345Z",  # second builder helper reads and writes
)
GOG_IDENTITY = {
    "analysis_distribution": "GOG",
    "program": "SkyrimSE.exe",
    "product_version": "1.6.1179.0",
    "sha256": "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f",
    "project_mode": "existing configured Ghidra project, WSL-native working copy, read-only, auto-analysis disabled",
}
EXPERIMENT_FILES = (
    "experiments/EXP-0059-trap-hit-handle-cleanup/README.md",
    "experiments/EXP-0059-trap-hit-handle-cleanup/hypothesis.md",
    "experiments/EXP-0059-trap-hit-handle-cleanup/predicted-outcomes.md",
    "experiments/EXP-0059-trap-hit-handle-cleanup/expected-discriminants.md",
    "experiments/EXP-0059-trap-hit-handle-cleanup/protocol.md",
    "experiments/EXP-0059-trap-hit-handle-cleanup/results.md",
    "experiments/EXP-0059-trap-hit-handle-cleanup/implications.md",
)
TOOL_INPUTS = (
    "scripts/python_env.py",
    "scripts/research_state.py",
    "tools/ghidra_probe.py",
    "tools/ghidra_scripts/ReadOnlyTargetedQuery.java",
    "experiments/EXP-0059-trap-hit-handle-cleanup/register_ev0319.py",
    *EXPERIMENT_FILES,
)
NOTE_TEXT = """# EV-0319 — ProcessTrapHit handle cleanup and PlayerCharacter receiver teardown

- **Captured:** {captured}
- **Transaction:** TX-20261017-0005 / Q-0058
- **Lane:** GOG static native analysis, bounded mechanism inference
- **Native target:** GOG Skyrim AE `SkyrimSE.exe`, ProductVersion 1.6.1179.0, SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`.
- **Steam boundary:** installed Steam AE 1.6.1170.0 is separately identified by EV-0109. No GOG RVA is transferred and no Steam hit, protection, AVSK, or callback result is observed.
- **Capture integrity:** fresh metadata records match the GOG executable hash, `read_only=true`, and `auto_analysis_disabled=true`; the manifest hashes all available query outputs and metadata, this note, experiment protocol and tool inputs. Older initializer/helper captures are retained with their original metadata and raw output hashes.

## Rival models and discriminant

- **H1 — null HitData handle on the captured trap route:** initialization clears HitData `+0x18/+0x1C`, the builder writes its receiver-derived value only at `+0x1C`, and neither called helper changes `+0x18`. The first handle cleanup is consequently skipped on this path; the receiver cleanup is a separate conditional release.
- **H2 — helper supplies a HitData handle:** one of the builder helpers writes a nonzero value to `+0x18`, allowing the first cleanup to execute on this path.
- **Discriminant:** preserve the initialization, direct and helper writes, both first cleanup local sources, and the resolved receiver secondary-vtable targets. H2 requires a post-initialization write or nonzero value reaching the `+0x18` lookup.

## Direct observations

1. **Identity and scope.** All fresh Ghidra queries use the existing GOG AE 1.6.1179.0 project/program and binary hash above in read-only mode with auto-analysis disabled. These are static GOG results; the Steam executable identified by EV-0109 is a separate build.
2. **Builder context.** `FUN_140679da0` initializes HitData through `FUN_1407dcd60`, then calls `FUN_1407dd110` with the PlayerCharacter receiver in R8 / parameter 3. The initializer clears eight bytes starting at HitData `+0x18`. The builder stores a receiver-derived handle at `+0x1C` and does not write the low DWORD at `+0x18`.
3. **Called helpers.** Preserved decompilations of `FUN_1407ddf50` and `FUN_1407df220` read/resolve handles but do not write HitData `+0x18`. Therefore `+0x18` remains zero on this captured builder route.
4. **First cleanup.** In `FUN_1406b9df0`, the first of the two refcount-gated `+0x8` dispatches is at `0x1406BA047`, using `local_3c0`, which is resolved from HitData `+0x18`. The zero handle skips that conditional release on the captured ProcessTrapHit route.
5. **Receiver cleanup.** The second dispatch is at `0x1406BA070`, using a handle derived from receiver `param_1`. The generic handle table stores owner `+0x20`; the PlayerCharacter secondary table installed there at RVA `0x18AD6F0` uses `FUN_140d28f40` for slot 1 / byte offset `+0x8`.
6. **Resolved dispatch.** `FUN_140d28f40` tail-dispatches secondary slot 0 with the disposal flag. PlayerCharacter slot 0 is adjustor thunk `FUN_140758824`, which subtracts `0x20` then jumps to `FUN_140758a60`. That body calls `FUN_14072fd60` and conditionally frees the `0xBE8`-byte object. This is a conditional receiver teardown path, not an every-hit assertion.
7. **Award boundary.** The teardown body `FUN_14072fd60` has eight unresolved virtual sites. No direct armor skill award is shown in the resolved thunk/adjustor functions, but the indirect descendant boundary remains unresolved. No zero-XP claim follows.

## Assessment and limits

H1 is supported and H2 is falsified for the captured ProcessTrapHit construction route: the `+0x18` cleanup is skipped, while the receiver-side release can dispatch into PlayerCharacter teardown when its refcount branch is taken. The data do not establish whether an unresolved teardown descendant can reach armor skill progress, whether a qualifying trap hit reduces damage, Steam 1.6.1170.0 behavior, exact profile winners, or vanilla reproduction. The required Steam repeated positive-damage / effective-protection / raw-AVSK test remains open under EV-0260. No OBJ-1 causal edge is supported.

The next useful static discriminant is class/dataflow resolution of the eight virtual sites in `FUN_14072fd60`, bounded to this teardown chain. Do not turn unresolved dispatch into a global no-award claim.
"""


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    evidence_items = json.loads(REGISTER.read_text(encoding="utf-8")).get("items", [])
    if any(row.get("id") == "EV-0319" for row in evidence_items):
        raise ValueError("EV-0319 already exists in research/EVIDENCE.json")
    TX.mkdir(parents=True, exist_ok=True)
    captured = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    NOTE.write_text(NOTE_TEXT.format(captured=captured), encoding="utf-8")

    artifacts: set[Path] = {NOTE}
    ghidra_queries: list[dict[str, Any]] = []
    for prefix in CAPTURE_PREFIXES:
        base = ROOT / ".local/ghidra" / prefix
        meta_path = base.with_suffix(".meta.json")
        if not meta_path.is_file():
            raise FileNotFoundError(meta_path)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if not meta.get("ok") or meta.get("analysis_binary_sha256") != GOG_IDENTITY["sha256"]:
            raise ValueError(f"query metadata failed identity/completion check: {meta_path}")
        if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
            raise ValueError(f"query was not read-only/no-analysis: {meta_path}")
        for suffix in ("stdout.raw", "stderr.raw", "log", "script.log", "meta.json"):
            path = ROOT / ".local/ghidra" / f"{prefix}.{suffix}"
            if path.is_file():
                artifacts.add(path)
        ghidra_queries.append(
            {
                "captured_utc": meta.get("captured_utc"),
                "query_mode": meta.get("query_mode"),
                "requested_rva": meta.get("requested_rva"),
                "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
                "requested_search_displacement": meta.get("requested_search_displacement"),
                "elapsed_seconds": meta.get("elapsed_seconds"),
                "checks": meta.get("checks"),
                "stdout_sha256": meta.get("stdout_sha256"),
                "metadata": meta_path.relative_to(ROOT).as_posix(),
                "stdout": meta.get("artifacts", {}).get("stdout"),
            }
        )

    artifacts.update(ROOT / relative for relative in TOOL_INPUTS)
    artifact_rows = [
        {
            "artifact": path.relative_to(ROOT).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": digest(path),
        }
        for path in sorted(artifacts)
        if path.is_file()
    ]
    manifest = {
        "evidence_id": "EV-0319",
        "transaction_id": "TX-20261017-0005",
        "captured_utc": captured,
        "target_identity": GOG_IDENTITY,
        "steam_scope_limit": "Steam AE 1.6.1170.0 is separately identified by EV-0109; no GOG RVA or runtime claim is transferred.",
        "query_mode": "Existing GOG Ghidra project, read-only, auto-analysis disabled; call-edge, function, disassembly, decompilation, pointer-table, and handle-field queries.",
        "external_sources": [],
        "related_evidence": ["EV-0261", "EV-0293", "EV-0302", "EV-0315", "EV-0109", "EV-0260"],
        "coverage": {
            "builder": "FUN_140679da0 -> FUN_1407dcd60 initializer -> FUN_1407dd110 ProcessTrapHit builder; receiver is passed in R8/parameter 3.",
            "hitdata_fields": "Initializer clears HitData +0x18/+0x1C; builder writes receiver-derived handle at +0x1C; FUN_1407ddf50 and FUN_1407df220 do not write +0x18.",
            "first_cleanup": "FUN_1406b9df0 0x1406BA047 uses local_3c0 from HitData +0x18 and is skipped for this captured builder route.",
            "receiver_cleanup": "FUN_1406BA070 is receiver-derived; PlayerCharacter owner+0x20 secondary-table slot +0x8 reaches common thunk FUN_140d28f40 and PlayerCharacter teardown.",
            "limitations": "FUN_14072fd60 retains eight unresolved indirect sites; no Steam runtime, effective protection, raw AVSK, profile winner, or vanilla reproduction was measured.",
        },
        "tool_inputs_sha256": {relative: digest(ROOT / relative) for relative in TOOL_INPUTS},
        "ghidra_queries": sorted(ghidra_queries, key=lambda row: row["captured_utc"] or ""),
        "artifacts": artifact_rows,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    local_hashes = {row["artifact"]: row["sha256"] for row in artifact_rows}
    local_hashes[MANIFEST.relative_to(ROOT).as_posix()] = digest(MANIFEST)
    evidence = {
        "id": "EV-0319",
        "kind": "native",
        "source": "Read-only GOG AE ProcessTrapHit builder, HitData handle, first receiver cleanup and PlayerCharacter secondary-vtable teardown trace.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0005/EV-0319-note.md",
        "sha256": digest(NOTE),
        "captured_utc": captured,
        "edition": "AE",
        "runtime": "GOG AE 1.6.1179.0 static identity is in the capture manifest. Steam AE 1.6.1170.0 is separately identified by EV-0109; no GOG RVA or runtime claim is transferred.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "tools/ghidra_probe.py through the strict Python dispatcher against the existing GOG project, read-only and auto-analysis disabled",
            "tools/ghidra_scripts/ReadOnlyTargetedQuery.java",
            "preserved prior GOG query captures for FUN_1407dcd60, FUN_1407ddf50, and FUN_1407df220",
        ],
        "coverage": "On the captured ProcessTrapHit route, HitData +0x18 remains zero and the first conditional cleanup is skipped; the receiver cleanup conditionally dispatches to PlayerCharacter teardown. Eight indirect teardown sites, Steam behavior, protection, raw AVSK, profile winners, and vanilla reproduction remain unresolved.",
        "result": "The H1 null-handle model is supported and H2's helper-write model is falsified for this captured route. The receiver's owner+0x20 secondary table slot +0x8 reaches FUN_140d28f40, which dispatches PlayerCharacter slot 0 into its destructor chain under the refcount condition. No global zero-XP or effective-protection finding is established.",
        "related_evidence": ["EV-0261", "EV-0293", "EV-0302", "EV-0315", "EV-0109", "EV-0260"],
        "local_hashes": local_hashes,
    }
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    register["items"].append(evidence)
    REGISTER.write_text(json.dumps(register, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"registered EV-0319 with {len(artifact_rows)} hashed artifacts and {len(ghidra_queries)} Ghidra query captures")


if __name__ == "__main__":
    main()
