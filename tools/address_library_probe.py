#!/usr/bin/env python3
"""Resolve a CommonLib AE relocation through the matching local GOG Address Library."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config  # noqa: E402
from tools.ae_target import MIN_AE_VERSION, TargetError, _native_path, compare_version, parse_version, read_executable_version  # noqa: E402


class AddressLibraryProbeError(RuntimeError):
    """A build-matched Address Library lookup could not be verified."""


def commonlib_ae_id(offsets_header: Path, symbol: str, *, vtable_index: int = 0) -> int:
    """Read an AE ID from a CommonLib relocation or named vtable declaration."""
    if "::" not in symbol:
        raise AddressLibraryProbeError("symbol must use Namespace::Name form")
    namespace, name = symbol.rsplit("::", 1)
    if namespace == "VTABLE":
        offsets_vtable = offsets_header.with_name("Offsets_VTABLE.h")
        if not offsets_vtable.is_file():
            raise AddressLibraryProbeError("CommonLib vtable declarations are missing")
        source = offsets_vtable.read_text(encoding="utf-8")
        declaration = re.search(
            rf"\bstd::array\s*<\s*REL::VariantID\s*,\s*(\d+)\s*>\s+"
            rf"VTABLE_{re.escape(name)}\s*\{{(?P<body>[^}}]*)\}}\s*;",
            source,
        )
        if not declaration:
            raise AddressLibraryProbeError(f"CommonLib vtable not found: {symbol}")
        variants = re.findall(
            r"REL::VariantID\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(0x[0-9A-Fa-f]+|\d+)\s*\)",
            declaration.group("body"),
        )
        expected_count = int(declaration.group(1))
        if len(variants) != expected_count or not variants:
            raise AddressLibraryProbeError(f"CommonLib vtable variants are incomplete: {symbol}")
        if not 0 <= vtable_index < len(variants):
            raise AddressLibraryProbeError(
                f"CommonLib vtable index {vtable_index} is outside the {len(variants)} entries for {symbol}"
            )
        # Each array entry identifies a distinct class subobject vtable. The
        # AE component is resolved independently against the verified GOG library.
        return int(variants[vtable_index][1])
    if vtable_index != 0:
        raise AddressLibraryProbeError("--vtable-index applies only to VTABLE symbols")
    source = offsets_header.read_text(encoding="utf-8")
    namespace_match = next(
        (
            match
            for match in re.finditer(r"\bnamespace\s+([\w:]+)\s*\{", source)
            if match.group(1) == namespace
        ),
        None,
    )
    if namespace_match is None:
        raise AddressLibraryProbeError(f"CommonLib namespace not found: {namespace}")
    body_start = namespace_match.end()
    depth = 1
    body_end = body_start
    while body_end < len(source) and depth:
        if source[body_end] == "{":
            depth += 1
        elif source[body_end] == "}":
            depth -= 1
        body_end += 1
    if depth:
        raise AddressLibraryProbeError(f"CommonLib namespace is unterminated: {namespace}")
    body = source[body_start:body_end - 1]
    declaration = re.search(
        rf"\b{re.escape(name)}\s*=\s*RELOCATION_ID\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)",
        body,
    )
    if not declaration:
        raise AddressLibraryProbeError(f"CommonLib AE relocation not found: {symbol}")
    return int(declaration.group(2))


def _legacy_decoder(path: Path):
    if not path.is_file():
        raise AddressLibraryProbeError("legacy Address Library decoder is missing")
    spec = importlib.util.spec_from_file_location("legacy_address_library_lookup", path)
    if spec is None or spec.loader is None:
        raise AddressLibraryProbeError("could not load the existing Address Library decoder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "decode", None)):
        raise AddressLibraryProbeError("legacy Address Library decoder has no decode(path) entrypoint")
    return module


def _legacy_mapping(path: Path, symbol: str) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    for row in data.get("symbols", []):
        if row.get("n") == symbol:
            return row
    return None


def probe(
    *, root: Path = ROOT, config: dict[str, str] | None = None, symbol: str,
    vtable_index: int = 0,
) -> dict[str, object]:
    config = read_local_config(root) if config is None else config
    required = ("LEGACY_SKYRIM_REPO", "COMMONLIBSSE_ROOT", "GHIDRA_ANALYSIS_EXE_GOG")
    missing = [key for key in required if not config.get(key, "").strip()]
    if missing:
        raise AddressLibraryProbeError("missing local bindings in config/local.env: " + ", ".join(missing))
    legacy = _native_path(config["LEGACY_SKYRIM_REPO"]).resolve()
    commonlib = _native_path(config["COMMONLIBSSE_ROOT"]).resolve()
    executable = _native_path(config["GHIDRA_ANALYSIS_EXE_GOG"]).resolve()
    if not legacy.is_dir():
        raise AddressLibraryProbeError("configured LEGACY_SKYRIM_REPO is inaccessible")
    if not commonlib.is_dir():
        raise AddressLibraryProbeError("configured COMMONLIBSSE_ROOT is inaccessible")
    if not executable.is_file() or executable.name.casefold() != "skyrimse.exe":
        raise AddressLibraryProbeError("configured GOG SkyrimSE.exe is missing")

    try:
        product_version = read_executable_version(executable)
        version = parse_version(product_version)
    except (TargetError, OSError, UnicodeError) as exc:
        raise AddressLibraryProbeError("could not read GOG executable ProductVersion") from exc
    if version[0] != 1 or version[1] != 6 or compare_version(version, MIN_AE_VERSION) < 0:
        raise AddressLibraryProbeError("GOG executable is not a supported Skyrim AE 1.6.318+ build")
    version_parts = tuple(version) + (0,)
    version_file = "-".join(str(part) for part in version_parts)
    address_library = executable.parent / "Data" / "SKSE" / "Plugins" / f"versionlib-{version_file}.bin"
    if not address_library.is_file():
        raise AddressLibraryProbeError("matching GOG Address Library file is missing for the verified ProductVersion")

    offsets_header = commonlib / "include" / "RE" / "Offsets.h"
    symbol_id = commonlib_ae_id(offsets_header, symbol, vtable_index=vtable_index)
    decoder = _legacy_decoder(legacy / "scripts" / "address_library_lookup.py")
    try:
        library_version, mappings = decoder.decode(address_library)
    except (OSError, EOFError, ValueError, KeyError) as exc:
        raise AddressLibraryProbeError("the configured GOG Address Library could not be decoded") from exc
    if tuple(library_version) != version_parts:
        raise AddressLibraryProbeError(
            "Address Library internal version does not match the verified GOG executable ProductVersion"
        )
    if symbol_id not in mappings:
        raise AddressLibraryProbeError(f"CommonLib AE ID {symbol_id} is absent from the matching GOG database")

    legacy_row = _legacy_mapping(
        legacy / "out" / "ghidra" / "symbols_ae_relevant.json",
        symbol,
    )
    rva = int(mappings[symbol_id])
    legacy_rva = int(legacy_row["rva"]) if legacy_row and isinstance(legacy_row.get("rva"), int) else None
    product_text = ".".join(str(part) for part in version_parts)
    return {
        "ok": True,
        "symbol": symbol,
        "commonlib_symbol_kind": "vtable_array_entry" if symbol.startswith("VTABLE::") else "relocation",
        "commonlib_vtable_index": vtable_index if symbol.startswith("VTABLE::") else None,
        "commonlib_ae_id": symbol_id,
        "analysis_distribution": "GOG",
        "analysis_binary_product_version": product_text,
        "analysis_binary_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
        "address_library_alias": f"GOG:Data/SKSE/Plugins/versionlib-{version_file}.bin",
        "address_library_sha256": hashlib.sha256(address_library.read_bytes()).hexdigest(),
        "address_library_internal_version": ".".join(str(part) for part in library_version),
        "address_library_rva": f"0x{rva:X}",
        "read_only": True,
        "legacy_map": {
            "alias": "legacy:out/ghidra/symbols_ae_relevant.json",
            "target": legacy_row.get("target") if legacy_row else None,
            "rva": f"0x{legacy_rva:X}" if legacy_rva is not None else None,
            "runtime_provenance_present": bool(legacy_row and legacy_row.get("runtime")),
            "matches_current_gog_address_library": legacy_rva == rva if legacy_rva is not None else None,
            "accepted_as_current_build_evidence": bool(legacy_row and legacy_row.get("runtime") == product_text and legacy_rva == rva),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbol", required=True, help="CommonLib symbol as Namespace::Name")
    parser.add_argument(
        "--vtable-index", type=int, default=0,
        help="zero-based CommonLib subobject-vtable entry (default: 0; VTABLE symbols only)",
    )
    args = parser.parse_args(argv)
    try:
        result = probe(symbol=args.symbol, vtable_index=args.vtable_index)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, AddressLibraryProbeError, TargetError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
