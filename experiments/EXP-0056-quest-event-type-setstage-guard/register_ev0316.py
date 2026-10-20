from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TX = ROOT / ".local/alignment/transactions/TX-20261017-0003"
NOTE = TX / "EV-0316-note.md"
MANIFEST = TX / "EV-0316-capture-manifest.json"
REGISTER = ROOT / "research/EVIDENCE.json"
GHIDRA_STAMPS = (
    "20261017T151617Z",
    "20261017T152119Z",
    "20261017T152349Z",
    "20261017T152626Z",
    "20261017T152810Z",
    "20261017T153216Z",
)
GHIDRA_SUFFIXES = (
    ".stdout.raw",
    ".stderr.raw",
    ".log",
    ".script.log",
    ".meta.json",
)
TOOL_INPUTS = (
    "tools/ghidra_probe.py",
    "tools/ghidra_scripts/ReadOnlyTargetedQuery.java",
    "tools/address_library_probe.py",
    "tools/xedit_bridge.py",
    "tools/plugin_reader.py",
    "scripts/research_state.py",
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    captured = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    artifacts: set[Path] = set()
    for pattern in ("*.stdout.raw", "*.stderr.raw"):
        artifacts.update(TX.glob(pattern))

    ghidra_root = ROOT / ".local/ghidra"
    ghidra_queries = []
    for stamp in GHIDRA_STAMPS:
        base = f"gog-query-{stamp}"
        for suffix in GHIDRA_SUFFIXES:
            candidate = ghidra_root / f"{base}{suffix}"
            if candidate.is_file():
                artifacts.add(candidate)
        metadata_path = ghidra_root / f"{base}.meta.json"
        if metadata_path.is_file():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            ghidra_queries.append(
                {
                    "metadata": metadata_path.relative_to(ROOT).as_posix(),
                    "query_mode": metadata.get("query_mode"),
                    "requested_rva": metadata.get("requested_rva"),
                    "pointer_table_rva": metadata.get("requested_pointer_table_rva"),
                    "pointer_count": metadata.get("requested_pointer_count"),
                    "search_displacement": metadata.get("requested_search_displacement"),
                    "ok": metadata.get("ok"),
                    "elapsed_seconds": metadata.get("elapsed_seconds"),
                }
            )

    # Include raw products named by the direct-parser wrappers without exposing
    # their machine-specific source bindings in the tracked evidence ledger.
    for wrapper in TX.glob("*.stdout.raw"):
        try:
            value = json.loads(wrapper.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        raw_output = value.get("raw_output")
        if isinstance(raw_output, str):
            raw_path = ROOT / raw_output
            if raw_path.is_file():
                artifacts.add(raw_path)
            elif raw_path.is_dir():
                artifacts.update(path for path in raw_path.rglob("*") if path.is_file())

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
        "evidence_id": "EV-0316",
        "transaction_id": "TX-20261017-0003",
        "captured_utc": captured,
        "target_identity": {
            "analysis_distribution": "GOG",
            "program": "SkyrimSE.exe",
            "product_version": "1.6.1179.0",
            "sha256": "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f",
            "project_mode": "existing configured Ghidra project, WSL-native working copy, read-only, auto-analysis disabled",
        },
        "steam_scope_limit": "Installed Steam AE 1.6.1170.0 is separately identified by EV-0109; no code RVA or runtime behavior is transferred.",
        "record_route": "Strict-dispatcher direct read-only TES4 file parser; not xEdit and not an active-order winner.",
        "source_record_context_evidence": ["EV-0301", "EV-0306", "EV-0308", "EV-0310"],
        "tool_inputs_sha256": {
            relative: digest(ROOT / relative) for relative in TOOL_INPUTS
        },
        "ghidra_queries": ghidra_queries,
        "source_records": [
            {
                "plugin": "Skyrim.esm",
                "plugin_sha256": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
                "form_id": "0004D8D6",
                "editor_id": "DA02",
                "DNAM_hex": "000160000000000007000000",
                "flags_u16": "0x0100",
                "capture": ".local/alignment/transactions/TX-20261017-0003/da02-qust.stdout.raw",
            },
            {
                "plugin": "Skyrim.esm",
                "plugin_sha256": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
                "form_id": "0002D512",
                "editor_id": "DA04",
                "DNAM_hex": "11013c000000000007000000",
                "flags_u16": "0x0111",
                "capture": ".local/alignment/transactions/TX-20261017-0003/da04-qust.stdout.raw",
            },
            {
                "plugin": "Skyrim.esm",
                "plugin_sha256": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
                "form_id": "0003B681",
                "editor_id": "DA06",
                "DNAM_hex": "00013c000000000007000000",
                "flags_u16": "0x0100",
                "capture": ".local/alignment/transactions/TX-20261017-0003/da06-qust.stdout.raw",
            },
            {
                "plugin": "Update.esm",
                "plugin_sha256": "c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9",
                "origin_plugin": "Skyrim.esm",
                "form_id": "0004E4E1",
                "editor_id": "DA09",
                "DNAM_hex": "00013c000000000007000000",
                "flags_u16": "0x0100",
                "capture": ".local/alignment/transactions/TX-20261017-0003/da09-qust.stdout.raw",
            },
        ],
        "schema_source": {
            "project": "TES5Edit",
            "revision": "dev-4.1.6",
            "path": "Core/wbDefinitionsTES5.pas",
            "url": "https://raw.githubusercontent.com/TES5Edit/TES5Edit/dev-4.1.6/Core/wbDefinitionsTES5.pas",
            "retrieved_utc": "2026-10-17",
            "relevant_lines": "8405-8435",
            "interpretation": "QUST DNAM General begins with U16 Flags; bit 0 is Start Game Enabled.",
        },
        "artifacts": artifact_rows,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    items = register["items"]
    if any(row.get("id") == "EV-0316" for row in items):
        raise ValueError("EV-0316 already exists in research/EVIDENCE.json")
    local_hashes = {
        row["artifact"]: row["sha256"] for row in artifact_rows
    }
    local_hashes[MANIFEST.relative_to(ROOT).as_posix()] = digest(MANIFEST)
    evidence = {
        "id": "EV-0316",
        "kind": "native",
        "source": "Read-only GOG TESQuest QUST DNAM-to-readiness field trace and exact official-source DA02/DA04/DA06/DA09 flags with versioned TES5Edit schema mapping",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0003/EV-0316-note.md",
        "sha256": digest(NOTE),
        "captured_utc": captured,
        "edition": "AE",
        "runtime": "GOG AE 1.6.1179.0 identity is in the capture manifest. Steam AE 1.6.1170.0 is separately identified by EV-0109; no Steam RVA or runtime claim is made.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "tools/ghidra_probe.py through strict Python 3.12 dispatcher against the existing GOG project with -noanalysis and read-only mode",
            "tools/address_library_probe.py and tools/xedit_bridge.py through the strict dispatcher",
            "Direct TES4 official-master record parsing; not xEdit or an active-order winner",
            "TES5Edit dev-4.1.6 primary QUST schema source, QUST definition lines 8405-8435",
        ],
        "coverage": "GOG TESQuest constructor, QUST parser, two scoped +0xDC writers, vtable slot 19 mapping, and exact official-source QUST DNAM values for DA02, DA04, DA06, and DA09. Steam behavior, complete target order, later virtual-dispatch timing, runtime quest state, aliases, functional access, and gameplay are outside scope.",
        "result": "The GOG QUST parser writes DNAM.General.Flags U16 to TESQuest+0xDC, with schema bit 0 named Start Game Enabled. DA04 source flags set bit 0 while DA02/DA06/DA09 clear it. This supports serialized initialization of +0xDC.0 and falsifies an independent initialization model for the inspected GOG path. A separate TESQuest virtual method can later clear the bit; its dispatch timing remains unresolved.",
        "local_hashes": local_hashes,
    }
    items.append(evidence)
    REGISTER.write_text(json.dumps(register, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"registered EV-0316 with {len(artifact_rows)} hashed capture artifacts")


if __name__ == "__main__":
    main()
