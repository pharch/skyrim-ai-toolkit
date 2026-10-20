#!/usr/bin/env python3
"""Derive the uninspected direct callers from preserved EV-0397 Ghidra output."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / ".local/ghidra/gog-query-20261018T155745Z.stdout.raw"
EXPECTED_SHA256 = "91678d35f4e216b1a4b6fccf71ac5dde7a857e988b3030b6ff6225f8eb3bbfc7"
IMAGE_BASE = 0x140000000
TARGET_VA = "14065b800"
XREF = re.compile(r"XREF_CALL_EDGE=.*?->\s*([0-9A-Fa-f]+)\s+caller=(FUN_[0-9A-Fa-f]+)\s*@\s*([0-9A-Fa-f]+)")
CALLER_DECOMPILED = re.compile(
    r"(?m)^.*?>\s*CALLER_DECOMPILATION_BEGIN=(FUN_[0-9A-Fa-f]+)\s*@\s*([0-9A-Fa-f]+)"
)
INCOMING_DECOMPILED = re.compile(
    r"(?m)^.*?>\s*INCOMING_CALLER_DECOMPILATION_BEGIN=(FUN_[0-9A-Fa-f]+)\s*@\s*([0-9A-Fa-f]+)"
)
XREF_TOTAL = re.compile(r"(?m)^.*?>\s*XREF_CALL_COUNT=(\d+)")
CALLER_ARRAY_COUNT = re.compile(r"(?m)^.*?>\s*INCOMING_CALLER_FUNCTION_COUNT=(\d+)")
INCOMING_DECOMPILED_TOTAL = re.compile(r"(?m)^.*?>\s*INCOMING_CALLER_DECOMPILED_COUNT=(\d+)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.input if args.input.is_absolute() else ROOT / args.input
    output = args.output if args.output.is_absolute() else ROOT / args.output
    local = (ROOT / ".local").resolve()
    output = output.resolve()
    if output != local and local not in output.parents:
        raise SystemExit("output must remain below ignored .local/")

    source_hash = sha256(source)
    if source_hash != EXPECTED_SHA256:
        raise SystemExit(f"EV-0397 caller capture hash mismatch: {source_hash}")
    text = source.read_text(encoding="utf-8", errors="replace")
    xrefs: dict[tuple[str, str], int] = {}
    for match in XREF.finditer(text):
        target, symbol, address = match.groups()
        if target.lower() == TARGET_VA:
            key = (symbol, address.lower())
            xrefs[key] = xrefs.get(key, 0) + 1
    caller_decompiled = {
        (symbol, address.lower())
        for symbol, address in CALLER_DECOMPILED.findall(text)
    }
    incoming_decompiled = {
        (symbol, address.lower())
        for symbol, address in INCOMING_DECOMPILED.findall(text)
    }
    decompiled = caller_decompiled | incoming_decompiled
    xref_total_match = XREF_TOTAL.search(text)
    array_count_match = CALLER_ARRAY_COUNT.search(text)
    incoming_decompiled_match = INCOMING_DECOMPILED_TOTAL.search(text)
    if not (xref_total_match and array_count_match and incoming_decompiled_match):
        raise SystemExit("EV-0397 is missing one or more caller coverage markers")
    xref_total = int(xref_total_match.group(1))
    caller_array_count = int(array_count_match.group(1))
    incoming_decompiled_total = int(incoming_decompiled_match.group(1))
    callers = [
        {
            "symbol": symbol,
            "va": "0x" + address,
            "rva": "0x" + format(int(address, 16) - IMAGE_BASE, "x"),
            "direct_callsite_count": count,
            "previously_decompiled": (symbol, address) in decompiled,
        }
        for (symbol, address), count in sorted(xrefs.items(), key=lambda row: int(row[0][1], 16))
    ]
    remaining = [row for row in callers if not row["previously_decompiled"]]
    if (
        len(xrefs) != 95
        or sum(xrefs.values()) != xref_total
        or len(callers) != 95
        or len(caller_decompiled) != 1
        or len(incoming_decompiled) != 32
        or len(decompiled) != 33
        or caller_array_count != 64
        or incoming_decompiled_total != 32
        or len(remaining) != 62
    ):
        raise SystemExit(
            "unexpected coverage: "
            f"xref_rows={len(xrefs)}, xref_total={xref_total}, unique_callers={len(callers)}, "
            f"array_count={caller_array_count}, caller_decompiled={len(caller_decompiled)}, "
            f"incoming_decompiled={len(incoming_decompiled)}, "
            f"incoming_decompiled_total={incoming_decompiled_total}, "
            f"decompiled_union={len(decompiled)}, remaining={len(remaining)}"
        )
    report = {
        "source": ".local/ghidra/gog-query-20261018T155745Z.stdout.raw",
        "source_sha256": source_hash,
        "target_function": "FUN_14065b800",
        "target_rva": "0x65b800",
        "xref_callsite_count": xref_total,
        "unique_direct_caller_count": len(callers),
        "reported_incoming_caller_array_count": caller_array_count,
        "reported_incoming_caller_array_count_interpretation": "storage cap from Function[64], not the complete direct caller count",
        "decompiled_first_caller_count": len(caller_decompiled),
        "decompiled_incoming_caller_count": len(incoming_decompiled),
        "previously_decompiled_count": len(decompiled),
        "remaining_caller_count": len(remaining),
        "callers": callers,
        "remaining_callers": remaining,
        "scope": "Exact direct xrefs in the captured GOG 1.6.1179.0 query. The query stores at most 64 unique caller functions, then decompiles the separately selected first caller plus at most 32 stored callers. The capture exposes 95 xref callers, 33 decompiled caller bodies, and 62 uninspected bodies. This inventory does not classify event semantics or ordinary-hit coverage.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output.relative_to(ROOT)), "sha256": sha256(output),
                      "remaining_callers": len(remaining)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
