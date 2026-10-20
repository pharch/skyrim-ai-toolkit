#!/usr/bin/env python3
"""Verify the corrected EV-0397 caller partition against a fresh Ghidra capture."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
IMAGE_BASE = 0x140000000
TARGET_VA = "14065b800"
XREF = re.compile(r"XREF_CALL_EDGE=.*?->\s*([0-9A-Fa-f]+)\s+caller=(FUN_[0-9A-Fa-f]+)\s*@\s*([0-9A-Fa-f]+)")
FIRST_CALLER = re.compile(
    r"(?m)^.*?>\s*CALLER_DECOMPILATION_BEGIN=(FUN_[0-9A-Fa-f]+)\s*@\s*([0-9A-Fa-f]+)"
)
INCOMING_CALLER = re.compile(
    r"(?m)^.*?>\s*INCOMING_CALLER_DECOMPILATION_BEGIN=(FUN_[0-9A-Fa-f]+)\s*@\s*([0-9A-Fa-f]+)"
)
MARKER = {
    "xrefs": re.compile(r"(?m)^.*?>\s*XREF_CALL_COUNT=(\d+)"),
    "stored": re.compile(r"(?m)^.*?>\s*INCOMING_CALLER_FUNCTION_COUNT=(\d+)"),
    "incoming_decompiled": re.compile(r"(?m)^.*?>\s*INCOMING_CALLER_DECOMPILED_COUNT=(\d+)"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def caller_set(raw: str) -> tuple[list[tuple[str, str]], set[tuple[str, str]]]:
    rows: list[tuple[str, str]] = []
    for target, symbol, va in XREF.findall(raw):
        if target.lower() == TARGET_VA:
            rows.append((symbol, va.lower()))
    return rows, set(rows)


def body_set(pattern: re.Pattern[str], raw: str) -> set[tuple[str, str]]:
    return {(symbol, va.lower().removeprefix("0x")) for symbol, va in pattern.findall(raw)}


def marker_value(name: str, raw: str) -> int:
    match = MARKER[name].search(raw)
    if not match:
        raise SystemExit(f"missing fresh query marker: {name}")
    return int(match.group(1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-raw", type=Path, required=True)
    parser.add_argument("--fresh-raw", type=Path, required=True)
    parser.add_argument("--fresh-meta", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--query-source", type=Path, default=Path("tools/ghidra_scripts/ReadOnlyTargetedQuery.java"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    original_path, fresh_path = resolve(args.original_raw), resolve(args.fresh_raw)
    meta_path, inventory_path = resolve(args.fresh_meta), resolve(args.inventory)
    query_source, output = resolve(args.query_source), resolve(args.output)
    local = (ROOT / ".local").resolve()
    if output != local and local not in output.parents:
        raise SystemExit("output must remain below ignored .local/")

    original_raw = original_path.read_text(encoding="utf-8", errors="replace")
    fresh_raw = fresh_path.read_text(encoding="utf-8", errors="replace")
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    old_rows, old_callers = caller_set(original_raw)
    fresh_rows, fresh_callers = caller_set(fresh_raw)
    first = body_set(FIRST_CALLER, fresh_raw)
    incoming = body_set(INCOMING_CALLER, fresh_raw)
    decompiled = first | incoming
    inventory_callers = {
        (row["symbol"], row["va"].lower().removeprefix("0x")) for row in inventory["callers"]
    }
    inventory_remaining = {
        (row["symbol"], row["va"].lower().removeprefix("0x")) for row in inventory["remaining_callers"]
    }
    inventory_previously_decompiled = {
        (row["symbol"], row["va"].lower().removeprefix("0x"))
        for row in inventory["callers"]
        if row["previously_decompiled"]
    }
    xref_count = marker_value("xrefs", fresh_raw)
    stored_count = marker_value("stored", fresh_raw)
    incoming_decompiled_count = marker_value("incoming_decompiled", fresh_raw)
    metadata_checks = (
        metadata.get("ok") is True
        and metadata.get("read_only") is True
        and metadata.get("auto_analysis_disabled") is True
        and metadata.get("program_executable_path_matches_gog_binary") is True
        and metadata.get("analysis_distribution") == "GOG"
        and metadata.get("analysis_binary_product_version") == "1.6.1179"
        and metadata.get("requested_rva", "").lower() == "0x65b800"
        and metadata.get("query_script_sha256") == digest(query_source)
        and metadata.get("stdout_sha256") == digest(fresh_path)
    )
    if not metadata_checks:
        raise SystemExit("fresh Ghidra metadata does not attest the requested read-only GOG query/source hashes")

    checks = {
        "original_xref_rows": len(old_rows),
        "fresh_xref_rows": len(fresh_rows),
        "fresh_xref_marker": xref_count,
        "original_unique_callers": len(old_callers),
        "fresh_unique_callers": len(fresh_callers),
        "fresh_stored_caller_count": stored_count,
        "fresh_first_caller_bodies": len(first),
        "fresh_incoming_caller_bodies": len(incoming),
        "fresh_incoming_decompiled_marker": incoming_decompiled_count,
        "fresh_union_decompiled": len(decompiled),
        "inventory_callers": len(inventory_callers),
        "inventory_previously_decompiled": len(inventory_previously_decompiled),
        "inventory_remaining": len(inventory_remaining),
        "old_fresh_xref_sets_equal": old_callers == fresh_callers,
        "inventory_fresh_caller_sets_equal": inventory_callers == fresh_callers,
        "inventory_fresh_decompiled_sets_equal": inventory_previously_decompiled == decompiled,
        "inventory_exact_remaining_partition": inventory_remaining == fresh_callers - decompiled,
        "fresh_caller_and_remaining_partition": fresh_callers == decompiled | inventory_remaining,
        "decompiled_remaining_disjoint": not (decompiled & inventory_remaining),
        "reported_64_is_capped_storage": stored_count == 64 and len(fresh_callers) == 95,
    }
    if (
        len(old_rows) != 95
        or len(fresh_rows) != 95
        or xref_count != 95
        or len(old_callers) != 95
        or len(fresh_callers) != 95
        or stored_count != 64
        or len(first) != 1
        or len(incoming) != 32
        or incoming_decompiled_count != 32
        or len(decompiled) != 33
        or len(inventory_remaining) != 62
        or not all(value for key, value in checks.items() if isinstance(value, bool))
    ):
        raise SystemExit("caller set coverage mismatch: " + json.dumps(checks, sort_keys=True))

    report = {
        "target_function": "FUN_14065b800",
        "target_rva": "0x65B800",
        "identity": {
            "distribution": metadata["analysis_distribution"],
            "product_version": metadata["analysis_binary_product_version"],
            "binary_sha256": metadata["analysis_binary_sha256"],
            "read_only": metadata["read_only"],
            "auto_analysis_disabled": metadata["auto_analysis_disabled"],
            "query_script_sha256": metadata["query_script_sha256"],
        },
        "checks": checks,
        "interpretation": "The reported count 64 is the query's caller-storage cap. The fresh identity-checked capture lists 95 direct caller functions and decompiles the separately selected caller plus 32 stored incoming callers, leaving 62 exact caller bodies uninspected.",
        "source_artifacts": {
            str(original_path.relative_to(ROOT)): digest(original_path),
            str(fresh_path.relative_to(ROOT)): digest(fresh_path),
            str(meta_path.relative_to(ROOT)): digest(meta_path),
            str(inventory_path.relative_to(ROOT)): digest(inventory_path),
            str(query_source.relative_to(ROOT)): digest(query_source),
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output.relative_to(ROOT)), "sha256": digest(output), "checks": checks}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
