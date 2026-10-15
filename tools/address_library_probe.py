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


def commonlib_ae_id(offsets_header: Path, symbol: str) -> int:
    """Read the AE ID from CommonLibSSE-NG's named relocation declaration."""
    if "::" not in symbol:
        raise AddressLibraryProbeError("symbol must use Namespace::Name form")
    namespace, name = symbol.rsplit("::", 1)
    source = offsets_header.read_text(encoding="utf-8")
    namespace_match = re.search(
        rf"\bnamespace\s+{re.escape(namespace)}\s*\{{(?P<body>.*?)^\s*\}}",
        source,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not namespace_match:
        raise AddressLibraryProbeError(f"CommonLib namespace not found: {namespace}")
    declaration = re.search(
        rf"\b{re.escape(name)}\s*=\s*RELOCATION_ID\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)",
        namespace_match.group("body"),
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
    symbol_id = commonlib_ae_id(offsets_header, symbol)
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
    args = parser.parse_args(argv)
    try:
        result = probe(symbol=args.symbol)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, AddressLibraryProbeError, TargetError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
