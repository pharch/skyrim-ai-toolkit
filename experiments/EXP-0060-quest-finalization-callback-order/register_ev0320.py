from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TX = ROOT / ".local/alignment/transactions/TX-20261017-0006"
NOTE = TX / "EV-0320-note.md"
MANIFEST = TX / "EV-0320-capture-manifest.json"
REGISTER = ROOT / "research/EVIDENCE.json"
CAPTURE_PREFIXES = (
    "gog-query-20261017T180424Z",  # second slot-19 caller/load path
    "gog-query-20261017T180712Z",  # only direct caller wrapper
)
PRIOR_MANIFESTS = (
    ".local/alignment/transactions/TX-20261016-0048/EV-0313-capture-manifest.json",
    ".local/alignment/transactions/TX-20261017-0004/EV-0318-capture-manifest.json",
)
PRIOR_NOTES = (
    ".local/alignment/transactions/TX-20261016-0048/EV-0313-note.md",
    ".local/alignment/transactions/TX-20261017-0004/EV-0318-note.md",
)
EXPERIMENT_FILES = (
    "experiments/EXP-0060-quest-finalization-callback-order/README.md",
    "experiments/EXP-0060-quest-finalization-callback-order/hypothesis.md",
    "experiments/EXP-0060-quest-finalization-callback-order/predicted-outcomes.md",
    "experiments/EXP-0060-quest-finalization-callback-order/expected-discriminants.md",
    "experiments/EXP-0060-quest-finalization-callback-order/protocol.md",
    "experiments/EXP-0060-quest-finalization-callback-order/results.md",
    "experiments/EXP-0060-quest-finalization-callback-order/implications.md",
)
GOG_IDENTITY = {
    "analysis_distribution": "GOG",
    "program": "SkyrimSE.exe",
    "product_version": "1.6.1179.0",
    "sha256": "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f",
    "project_mode": "existing configured Ghidra project, WSL-native working copy, read-only, auto-analysis disabled",
}
TOOL_INPUTS = (
    "scripts/python_env.py",
    "scripts/research_state.py",
    "tools/ghidra_probe.py",
    "tools/ghidra_scripts/ReadOnlyTargetedQuery.java",
    "experiments/EXP-0060-quest-finalization-callback-order/register_ev0320.py",
    *EXPERIMENT_FILES,
)
NOTE_TEXT = """# EV-0320 — QUST finalization callers and SetStage callback boundary

- **Captured:** {captured}
- **Transaction:** TX-20261017-0006 / Q-0059
- **Lane:** GOG static native analysis; bounded caller-path classification
- **Native target:** GOG Skyrim AE `SkyrimSE.exe`, ProductVersion 1.6.1179.0, SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`.
- **Steam boundary:** Steam AE 1.6.1170.0 is separately identified by EV-0109. No GOG RVA is transferred; no live callback, quest state, profile winner, or level-one result was captured.
- **Capture integrity:** both fresh query metadata records match the executable hash, `read_only=true`, and `auto_analysis_disabled=true`. The manifest hashes fresh raw query outputs and metadata, prior EV-0313/EV-0318 artifacts used for context, this note, experiment protocol, and tool inputs.

## Rival models and discriminant

- **H1 — finalization first:** natural `Quest.SetStage` callback delivery occurs after the loader returns from the QUST slot-19 sweep.
- **H2 — pre-finalization callback:** a natural event/callback chain can invoke the registered handler while records are processed or before the sweep.
- **Discriminant:** identify a build-attested callback target on a direct or class-resolved dispatch path and place it before or after `FUN_1401bdf20`; generic tables and untyped indirect sites are inconclusive.

## Direct observations

1. EV-0318's read-only GOG capture shows `FUN_1401b9510` completing its per-file `FUN_1401bb4f0` loop, calling `FUN_1401bdf20`, then performing post-pass bookkeeping and returning.
2. Fresh query of `FUN_1401be290` reports 90 direct and 12 indirect call sites. The function processes records through `FUN_1401bb4f0`, then directly calls `FUN_1401bdf20`. Its only analyzed direct code caller is `FUN_1403753b0`.
3. Fresh query of `FUN_1403753b0` reports three direct calls, zero indirect sites, and zero analyzed direct callers. It calls `FUN_14033e470`; on success it calls `FUN_1401be290` and then `FUN_1401bb490`. One data reference points into an unclassified metadata/table region. This does not establish scheduler type or lifecycle.
4. EV-0313 maps candidate GOG `Quest.SetStage` registration row data to `FUN_14034de90`, but the callback row has no indexed code xrefs. The fresh bounded loader captures identify no class-resolved natural callback dispatch from either file-processing chain.

## Assessment and limits

The two inspected loader paths perform their slot-19 sweep after per-file record processing. The result does not place the first natural `Quest.SetStage` callback relative to loader completion; H1 and H2 remain unresolved. A missing direct call is not a negative result because the native binding is dispatched through a generic table and the loader has unresolved indirect sites. No target-quest level-one route, Steam behavior, or functional access is established.

The remaining exact discriminator is a class-resolved startup/scheduler edge or a read-only exact-Steam observer recording post-load completion, the first natural callback target, `TESQuest+0xDC.0/+0xE0`, running/stage state, and aliases under a complete target order [EV-0260]. No OBJ-2 causal edge is added.
"""


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0320" for row in register.get("items", [])):
        raise ValueError("EV-0320 already exists in research/EVIDENCE.json")
    TX.mkdir(parents=True, exist_ok=True)
    captured = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    NOTE.write_text(NOTE_TEXT.format(captured=captured), encoding="utf-8")

    artifacts: set[Path] = {NOTE}
    query_rows: list[dict[str, Any]] = []
    for prefix in CAPTURE_PREFIXES:
        meta_path = ROOT / ".local/ghidra" / f"{prefix}.meta.json"
        if not meta_path.is_file():
            raise FileNotFoundError(meta_path)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if not meta.get("ok") or meta.get("analysis_binary_sha256") != GOG_IDENTITY["sha256"]:
            raise ValueError(f"query failed GOG identity/completion check: {meta_path}")
        if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
            raise ValueError(f"query was not read-only/no-analysis: {meta_path}")
        for suffix in ("stdout.raw", "stderr.raw", "log", "script.log", "meta.json"):
            path = ROOT / ".local/ghidra" / f"{prefix}.{suffix}"
            if path.is_file():
                artifacts.add(path)
        query_rows.append({
            "captured_utc": meta.get("captured_utc"),
            "query_mode": meta.get("query_mode"),
            "requested_rva": meta.get("requested_rva"),
            "elapsed_seconds": meta.get("elapsed_seconds"),
            "checks": meta.get("checks"),
            "stdout_sha256": meta.get("stdout_sha256"),
            "metadata": meta_path.relative_to(ROOT).as_posix(),
            "stdout": meta.get("artifacts", {}).get("stdout"),
        })

    prior_manifest_rows: list[dict[str, Any]] = []
    for relative in (*PRIOR_MANIFESTS, *PRIOR_NOTES):
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        artifacts.add(path)
    for relative in PRIOR_MANIFESTS:
        path = ROOT / relative
        data = json.loads(path.read_text(encoding="utf-8"))
        missing = []
        for row in data.get("artifacts", []):
            source = ROOT / row["artifact"]
            if source.is_file():
                artifacts.add(source)
            else:
                missing.append(row["artifact"])
        prior_manifest_rows.append({
            "manifest": relative,
            "manifest_sha256": digest(path),
            "declared_artifacts": len(data.get("artifacts", [])),
            "missing_declared_artifacts": missing,
        })

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
        "evidence_id": "EV-0320",
        "transaction_id": "TX-20261017-0006",
        "captured_utc": captured,
        "target_identity": GOG_IDENTITY,
        "steam_scope_limit": "Steam AE 1.6.1170.0 is separately identified by EV-0109; no GOG RVA or callback-order claim is transferred.",
        "query_mode": "Existing GOG Ghidra project, read-only, auto-analysis disabled; direct call-edge, caller, and decompilation queries.",
        "related_evidence": ["EV-0313", "EV-0318", "EV-0109", "EV-0260"],
        "prior_capture_manifests": prior_manifest_rows,
        "coverage": {
            "main_loader": "EV-0318 capture: FUN_1401b9510 calls FUN_1401bdf20 after per-file FUN_1401bb4f0 processing and before return.",
            "second_loader": "Fresh query: FUN_1401be290 calls FUN_1401bb4f0 and later FUN_1401bdf20; 90 direct and 12 indirect call sites; sole direct code caller FUN_1403753b0.",
            "wrapper": "Fresh query: FUN_1403753b0 has three direct calls, zero indirect calls, zero analyzed direct callers, and one data reference in an unclassified table/metadata region.",
            "callback_limit": "EV-0313 maps the SetStage binding row to FUN_14034de90 via data evidence, but no class-identified pre-finalization dispatch was traced. Exact first natural callback order remains unresolved.",
            "runtime_limit": "No Steam callback timestamp, quest state, active-profile winner, or level-one route was captured; EV-0260 lists missing observer/profile/save prerequisites.",
        },
        "tool_inputs_sha256": {relative: digest(ROOT / relative) for relative in TOOL_INPUTS},
        "ghidra_queries": sorted(query_rows, key=lambda row: row["captured_utc"] or ""),
        "artifacts": artifact_rows,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    local_hashes = {row["artifact"]: row["sha256"] for row in artifact_rows}
    local_hashes[MANIFEST.relative_to(ROOT).as_posix()] = digest(MANIFEST)
    evidence = {
        "id": "EV-0320",
        "kind": "native",
        "source": "Read-only GOG AE load-manager/finalization caller classification with separate Quest.SetStage binding evidence from EV-0313.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0006/EV-0320-note.md",
        "sha256": digest(NOTE),
        "captured_utc": captured,
        "edition": "AE",
        "runtime": "GOG AE 1.6.1179.0 static identity is in the capture manifest. Steam AE 1.6.1170.0 is separately identified by EV-0109; no GOG callback-order or runtime claim is transferred.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "tools/ghidra_probe.py through the strict dispatcher against the existing GOG project, read-only and auto-analysis disabled",
            "tools/ghidra_scripts/ReadOnlyTargetedQuery.java",
            "prior EV-0313 and EV-0318 capture manifests/notes and their available raw artifacts",
        ],
        "coverage": "Two GOG file-load paths place the slot-19 finalization sweep after per-file record processing. A class-identified natural Quest.SetStage dispatch is not resolved; the first callback order remains unknown. No level-one or Steam runtime result is established.",
        "result": "FUN_1401b9510 and FUN_1401be290 each call FUN_1401bdf20 after file-record work. FUN_1401be290 is directly called by FUN_1403753b0, which has no analyzed direct callers and an unclassified data reference. Neither bounded chain identifies a Quest.SetStage callback before finalization. This does not resolve H1/H2 because generic callback dispatch and indirect sites remain untyped.",
        "related_evidence": ["EV-0313", "EV-0318", "EV-0109", "EV-0260"],
        "local_hashes": local_hashes,
    }
    register["items"].append(evidence)
    REGISTER.write_text(json.dumps(register, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    missing_total = sum(len(row["missing_declared_artifacts"]) for row in prior_manifest_rows)
    print(f"registered EV-0320 with {len(artifact_rows)} hashed artifacts, {len(query_rows)} fresh queries, {missing_total} prior-manifest artifacts missing")


if __name__ == "__main__":
    main()
