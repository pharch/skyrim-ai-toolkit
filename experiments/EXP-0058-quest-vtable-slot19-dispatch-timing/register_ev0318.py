from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TX = ROOT / ".local/alignment/transactions/TX-20261017-0004"
NOTE = TX / "EV-0318-note.md"
MANIFEST = TX / "EV-0318-capture-manifest.json"
REGISTER = ROOT / "research/EVIDENCE.json"
CAPTURE_PREFIXES = (
    "gog-query-20261017T164931Z",  # load-manager callers and full type loop
    "gog-query-20261017T165240Z",  # per-file serialized record loop
    "gog-query-20261017T165454Z",  # generic record dispatcher and insertion path
    "gog-query-20261017T165755Z",  # TESQuest vtable entries 6 and 19
    "gog-query-20261017T170046Z",  # vtable+0x30 record-buffer register dataflow
    "gog-query-20261017T170335Z",  # bounded whole-program +0x30 scan
    "gog-query-20261017T164454Z",  # form-type registration helper context
)
TOOL_INPUTS = (
    "scripts/python_env.py",
    "scripts/research_state.py",
    "tools/ghidra_probe.py",
    "tools/ghidra_scripts/ReadOnlyTargetedQuery.java",
    "experiments/EXP-0058-quest-vtable-slot19-dispatch-timing/register_ev0318.py",
)
GOG_IDENTITY = {
    "analysis_distribution": "GOG",
    "program": "SkyrimSE.exe",
    "product_version": "1.6.1179.0",
    "sha256": "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f",
    "project_mode": "existing configured Ghidra project, WSL-native working copy, read-only, auto-analysis disabled",
}
SOURCE_URL = "https://github.com/ianpatt/skse64/blob/master/scripts/modified/FormType.psc#L615"

NOTE_TEXT = """# EV-0318 — TESQuest slot-19 dispatch in GOG file-load finalization

- **Captured:** 2026-10-17
- **Transaction:** TX-20261017-0004 / Q-0057
- **Lane:** GOG static native analysis, mechanism-inference boundary
- **Native target:** GOG Skyrim AE `SkyrimSE.exe`, ProductVersion 1.6.1179.0, SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`.
- **Steam boundary:** Steam AE 1.6.1170.0 is separately identified by EV-0109. No GOG RVA is transferred and no Steam runtime field or callback was observed.
- **External FormType source:** SKSE `FormType.psc`, branch `master`, retrieved 2026-10-17 at {source_url}. The source defines `kQuest = 77` (decimal), i.e. `0x4D`. This is a mutable branch URL; the browser could not resolve an immutable commit hash during this capture.
- **Capture integrity:** The manifest lists and hashes the raw Ghidra stdout, stderr, logs, metadata, tool inputs, and this note. Ghidra opened the configured existing GOG project read-only with auto-analysis disabled; each query metadata record matches the exact executable hash above.

## Rival models and discriminant

- **H1 — load/finalization:** TESQuest slot 19 is invoked during file load or post-load finalization after the QUST parser and before a natural `Quest.SetStage` callback reads `TESQuest+0xDC.0`.
- **H2 — later lifecycle only:** slot 19 runs only on a later quest transition, allowing an earlier natural callback to read the loaded flag first.
- **Discriminant:** bind the object vtable slots to the QUST parser and slot-19 method, preserve the record-buffer argument through the parser call, identify the FormType-indexed array containing QUST, and order that sweep after the source-file record loop. Then assess the remaining native callback-order boundary separately.

## Direct observations

1. **Build identity and project mode.** Every new Ghidra query is for the existing GOG AE 1.6.1179.0 project/program and binary hash above, with `read_only=true` and `auto_analysis_disabled=true`; the adapter reports no import, overwrite, or project creation. These are static GOG findings, not Steam RVA or runtime results.
2. **QUST FormType.** SKSE `FormType.psc` maps `kQuest` to decimal 77 (`0x4D`) [external source URL above]. The manager loop's excluded values are `0x13`, `0x47`, and `0x5B`, so `0x4D` is included.
3. **TESQuest vtable.** The bounded table read at RVA `0x17E7D10` resolves entry 6 at `0x17E7D40` to `FUN_1403c7a50` (RVA `0x3C7A50`), the QUST parser already characterized in EV-0316. Entry 19 at `0x17E7DA8` resolves to `FUN_1403c8420` (RVA `0x3C8420`), the conditional `TESQuest+0xDC.0` clear routine already characterized in EV-0316.
4. **Record parser call.** `FUN_1401bb4f0` iterates source-file records and calls `FUN_1401bb8d0`. The new-form branch of `FUN_1401bb8d0` calls `FUN_1401b1020(form, recordBuffer)` and then `FUN_1401b12f0(manager, form)` to register the form. In `FUN_1401b1020`, disassembly at `0x1401b1034–0x1401b1041` loads the form vtable, preserves the record-buffer `RDX` value, leaves the form in `RCX`, and executes `CALL qword ptr [RAX + 0x30]`. This is TESQuest vtable entry 6 with the record buffer passed to `FUN_1403c7a50` before registration.
5. **Ordering of per-file loads and finalization.** `FUN_1401b9510` invokes `FUN_1401bb4f0` for its eligible source-file nodes, completes that loop, and then calls `FUN_1401bdf20`. In `FUN_1401bdf20`, the type-indexed pass iterates `bVar8` from 0 through `0x89`; for each non-skipped type it walks the corresponding manager array at `param_1 + bVar8*0x18` and calls every object's vtable `+0x98`. Since QUST is `0x4D`, the pass includes registered TESQuest objects and invokes their slot 19 after the per-file record loop.
6. **Causal interpretation.** Together, the captured record-buffer call, registration, and main file-loader ordering support H1's GOG load/finalization component and rule out the version of H2 that says slot 19 is called only by later quest lifecycle transitions. The slot-19 sweep follows QUST parsing in this static load path.
7. **Bounded `+0x30` census.** The whole-program screen reports 27,290 object-relative accesses and 63,355 stack-relative accesses, with all scan completion markers true. It prints only the first 2,048 object-relative matches; therefore it is not a complete callsite classification and supplies no global negative. The specific parser callsite above is established independently by the function and vtable captures.

## Assessment and limits

Q-0057's main static discriminant is resolved for GOG AE 1.6.1179.0: parsed QUST forms are registered in the FormType-indexed manager, and the post-file-load `FUN_1401bdf20` sweep dispatches TESQuest vtable slot 19. This makes the `FUN_1403c8420` bit clear a load/finalization operation for registered quests.

The captures do **not** directly show when the first natural `Quest.SetStage` callback is delivered relative to this load-manager return, whether a particular target quest is naturally active/reachable at level 1, or whether Steam AE 1.6.1170.0 has the same code path. Treat “before the first natural SetStage guard” as a load-order inference pending a read-only observer on the exact Steam target with complete active order. No console stage/level forcing, altered plugin, injected script, or runtime intervention was used. No OBJ-2 armor/XP causal edge is supported.
"""


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    if any(row.get("id") == "EV-0318" for row in json.loads(REGISTER.read_text(encoding="utf-8")).get("items", [])):
        raise ValueError("EV-0318 already exists in research/EVIDENCE.json")
    captured = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    NOTE.write_text(NOTE_TEXT.format(source_url=SOURCE_URL), encoding="utf-8")

    artifacts: set[Path] = {NOTE}
    ghidra_queries: list[dict[str, Any]] = []
    for prefix in CAPTURE_PREFIXES:
        meta_path = ROOT / ".local/ghidra" / f"{prefix}.meta.json"
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
        "evidence_id": "EV-0318",
        "transaction_id": "TX-20261017-0004",
        "captured_utc": captured,
        "target_identity": GOG_IDENTITY,
        "steam_scope_limit": "Steam AE 1.6.1170.0 is separately identified by EV-0109. No GOG RVA is transferred and no Steam runtime claim is made.",
        "query_mode": "Existing GOG Ghidra project, read-only, auto-analysis disabled; function, call-edge, pointer-table, and displacement queries.",
        "external_sources": [
            {
                "url": SOURCE_URL,
                "source_identity": "SKSE ianpatt/skse64 scripts/modified/FormType.psc on branch master",
                "retrieved_utc": "2026-10-17",
                "claim": "kQuest maps to decimal 77 / 0x4D",
                "revision_limit": "The browser did not resolve an immutable commit hash; URL is branch-relative.",
            }
        ],
        "related_evidence": ["EV-0316", "EV-0317", "EV-0313", "EV-0109"],
        "coverage": {
            "formtype_pass": "FUN_1401bdf20 iterates 0..0x89 excluding 0x13, 0x47, 0x5B and calls each registered object's vtable+0x98; SKSE source maps QUST to included index 0x4D.",
            "parse_and_registration": "FUN_1401bb4f0 -> FUN_1401bb8d0 -> FUN_1401b1020 virtual +0x30 with form in RCX and record buffer retained in RDX -> FUN_1401b12f0 registration.",
            "load_order": "FUN_1401b9510 completes per-file FUN_1401bb4f0 calls before invoking FUN_1401bdf20.",
            "displacement_screen": "0x30 scan found 27,290 object-relative accesses and 63,355 stack accesses; only the first 2,048 object-relative lines were printed. This is not a complete global callsite classification.",
            "limitations": "Exact order against the first natural Quest.SetStage callback, target-quest runtime reachability/state, Steam code equivalence, and vanilla level-one progression remain unobserved.",
        },
        "tool_inputs_sha256": {relative: digest(ROOT / relative) for relative in TOOL_INPUTS},
        "ghidra_queries": sorted(ghidra_queries, key=lambda row: row["captured_utc"] or ""),
        "artifacts": artifact_rows,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    local_hashes = {row["artifact"]: row["sha256"] for row in artifact_rows}
    local_hashes[MANIFEST.relative_to(ROOT).as_posix()] = digest(MANIFEST)
    evidence = {
        "id": "EV-0318",
        "kind": "native",
        "source": "Read-only GOG AE TESQuest record-load, FormType-indexed registration, and slot-19 load-finalization trace; QUST index corroborated by SKSE FormType.psc (master branch, retrieved 2026-10-17).",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0004/EV-0318-note.md",
        "sha256": digest(NOTE),
        "captured_utc": captured,
        "edition": "AE",
        "runtime": "GOG AE 1.6.1179.0 static identity is in the capture manifest. Steam AE 1.6.1170.0 is separately identified by EV-0109; no GOG RVA or runtime claim is transferred.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "tools/ghidra_probe.py through the strict Python 3.12 dispatcher against the existing GOG project, read-only and auto-analysis disabled",
            "tools/ghidra_scripts/ReadOnlyTargetedQuery.java",
            "SKSE ianpatt/skse64 FormType.psc, branch master, retrieved 2026-10-17",
        ],
        "coverage": "GOG QUST parser/registration path and post-file-load type-indexed slot-19 pass. H1's load/finalization component is supported; ordering against first natural Quest.SetStage callback remains a load-order inference. The +0x30 global scan is capped at 2,048 printed lines, and Steam/runtime/target-quest behavior is unobserved.",
        "result": "The QUST parser is TESQuest vtable slot 6/FUN_1403c7a50; the per-record helper calls slot 6 with the record buffer. Parsed forms are registered before the main file loader calls FUN_1401bdf20, whose unskipped FormType 0x4D pass dispatches slot 19/FUN_1403c8420. This supports post-parse load-finalization dispatch on registered quests and rejects an only-later-lifecycle model for GOG. No vanilla level-one progression or OBJ-2 edge is established.",
        "related_evidence": ["EV-0316", "EV-0317", "EV-0313", "EV-0109"],
        "local_hashes": local_hashes,
    }
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    register["items"].append(evidence)
    REGISTER.write_text(json.dumps(register, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"registered EV-0318 with {len(artifact_rows)} hashed artifacts and {len(ghidra_queries)} Ghidra query captures")


if __name__ == "__main__":
    main()
