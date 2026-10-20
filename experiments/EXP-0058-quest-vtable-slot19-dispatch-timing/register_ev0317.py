from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TX = ROOT / ".local/alignment/transactions/TX-20261017-0004"
NOTE = TX / "EV-0317-note.md"
MANIFEST = TX / "EV-0317-capture-manifest.json"
REGISTER = ROOT / "research/EVIDENCE.json"
TOOL_INPUTS = (
    "tools/ghidra_probe.py",
    "tools/ghidra_scripts/ReadOnlyTargetedQuery.java",
    "scripts/research_state.py",
)
GOG_IDENTITY = {
    "analysis_distribution": "GOG",
    "program": "SkyrimSE.exe",
    "product_version": "1.6.1179.0",
    "sha256": "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f",
    "project_mode": "existing configured Ghidra project, WSL-native working copy, read-only, auto-analysis disabled",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def local_paths(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, str) and value.startswith(".local/"):
        found.add(value)
    elif isinstance(value, dict):
        for child in value.values():
            found.update(local_paths(child))
    elif isinstance(value, list):
        for child in value:
            found.update(local_paths(child))
    return found


def main() -> None:
    captured = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    wrappers = sorted([*TX.glob("*.stdout.raw"), *TX.glob("*.stderr.raw")])
    artifacts: set[Path] = set(wrappers)
    ghidra_queries: list[dict[str, Any]] = []

    for wrapper in TX.glob("*.stdout.raw"):
        try:
            value = json.loads(wrapper.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        for relative in local_paths(value):
            candidate = ROOT / relative
            if candidate.is_file():
                artifacts.add(candidate)
        if value.get("operation") == "existing_gog_project_read_only_query":
            artifacts_list = value.get("artifacts", {})
            ghidra_queries.append(
                {
                    "wrapper": wrapper.relative_to(ROOT).as_posix(),
                    "captured_utc": value.get("captured_utc"),
                    "query_mode": value.get("query_mode"),
                    "requested_rva": value.get("requested_rva"),
                    "requested_address_rva": value.get("requested_address_rva"),
                    "search_displacement": value.get("requested_search_displacement"),
                    "ok": value.get("ok"),
                    "elapsed_seconds": value.get("elapsed_seconds"),
                    "ghidra_stdout": artifacts_list.get("stdout"),
                    "ghidra_metadata": value.get("metadata_artifact"),
                }
            )

    artifacts.add(NOTE)
    artifact_rows = []
    for path in sorted(artifacts):
        if not path.is_file():
            continue
        artifact_rows.append(
            {
                "artifact": path.relative_to(ROOT).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": digest(path),
            }
        )

    manifest = {
        "evidence_id": "EV-0317",
        "transaction_id": "TX-20261017-0004",
        "captured_utc": captured,
        "target_identity": GOG_IDENTITY,
        "steam_scope_limit": "Steam AE 1.6.1170.0 is separately identified by EV-0109. No GOG RVA is transferred and no Steam runtime claim is made.",
        "query_mode": "Existing GOG Ghidra project, read-only, auto-analysis disabled; targeted address-context, displacement, vtable-entry and direct-call-edge queries.",
        "related_evidence": ["EV-0316", "EV-0313", "EV-0314"],
        "coverage": {
            "whole_program_displacement": "0x98; adapter completed with all markers true; 4,307 operand accesses, 996 writer-candidate functions.",
            "indirect_sites": "212 indirect CALL/JMP sites across the program; 11 selected by absolute code address in 0x140300000-0x140400000.",
            "candidate_functions_queried": [
                "FUN_140305e80",
                "FUN_140306880",
                "FUN_14030cc70",
                "FUN_140311820",
                "FUN_140322e10",
                "FUN_140323680",
                "FUN_14033c450",
                "FUN_1403a2820",
                "FUN_1403b16a0",
                "FUN_1403e6e60",
                "FUN_1403e6fb0",
            ],
            "omissions": "Indirect sites outside the selected code-address range were not individually classified. Class-unresolved receivers and the packed relative-data table remain unresolved; no query establishes runtime execution or Steam behavior.",
        },
        "tool_inputs_sha256": {relative: digest(ROOT / relative) for relative in TOOL_INPUTS},
        "ghidra_queries": sorted(ghidra_queries, key=lambda row: row["captured_utc"] or ""),
        "artifacts": artifact_rows,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    items = register["items"]
    if any(row.get("id") == "EV-0317" for row in items):
        raise ValueError("EV-0317 already exists in research/EVIDENCE.json")
    local_hashes = {row["artifact"]: row["sha256"] for row in artifact_rows}
    local_hashes[MANIFEST.relative_to(ROOT).as_posix()] = digest(MANIFEST)
    evidence = {
        "id": "EV-0317",
        "kind": "native",
        "source": "Read-only GOG TESQuest vtable slot-19 dispatch screen and bounded classification of all 11 indirect +0x98 candidates in code range 0x140300000-0x140400000",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0004/EV-0317-note.md",
        "sha256": digest(NOTE),
        "captured_utc": captured,
        "edition": "AE",
        "runtime": "GOG AE 1.6.1179.0 identity is in the capture manifest. Steam AE 1.6.1170.0 is separately identified by EV-0109; no Steam RVA or runtime claim is made.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "tools/ghidra_probe.py through the strict Python 3.12 dispatcher against the existing GOG project, read-only and auto-analysis disabled",
            "tools/ghidra_scripts/ReadOnlyTargetedQuery.java direct-call-edge and address-context queries",
        ],
        "coverage": "GOG vtable slot-19 entry and secondary packed data reference, whole-program +0x98 displacement screen (4,307 accesses, 212 indirect CALL/JMP sites), and all 11 sites in the selected 0x140300000-0x140400000 code range. Other code ranges, class-unresolved receivers, runtime execution, Steam behavior, and call order against actual target quest callbacks remain outside or unresolved.",
        "result": "Two candidate receivers are RTTI-resolved as BGSSoundCategory and one is a Papyrus parser/compiler object; remaining calls are generic object/factory/fix-up/array paths without TESQuest receiver provenance. No analyzed reference to the vtable slot cell or candidate call edge orders TESQuest slot 19 relative to QUST parsing and Quest.SetStage. H1/H2 timing remains unresolved; this is not evidence that the virtual method is never called.",
        "local_hashes": local_hashes,
    }
    items.append(evidence)
    REGISTER.write_text(json.dumps(register, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"registered EV-0317 with {len(artifact_rows)} hashed capture artifacts and {len(ghidra_queries)} Ghidra query wrappers")


if __name__ == "__main__":
    main()
