#!/usr/bin/env python3
"""Resolve the inline CommonLib TESActorBaseData::GetLevel AE relocation."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.address_library_probe import AddressLibraryProbeError, _legacy_decoder, _native_path
from tools.ae_target import MIN_AE_VERSION, TargetError, compare_version, parse_version, read_executable_version


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    config = read_local_config(ROOT)
    required = ("LEGACY_SKYRIM_REPO", "COMMONLIBSSE_ROOT", "GHIDRA_ANALYSIS_EXE_GOG")
    missing = [key for key in required if not config.get(key, "").strip()]
    if missing:
        raise SystemExit("missing configured bindings: " + ", ".join(missing))
    commonlib = _native_path(config["COMMONLIBSSE_ROOT"]).resolve()
    legacy = _native_path(config["LEGACY_SKYRIM_REPO"]).resolve()
    executable = _native_path(config["GHIDRA_ANALYSIS_EXE_GOG"]).resolve()
    header = commonlib / "include/RE/T/TESActorBaseData.h"
    if not commonlib.is_dir() or not legacy.is_dir() or not header.is_file():
        raise SystemExit("configured CommonLib or decoder inputs are unavailable")
    if not executable.is_file() or executable.name.casefold() != "skyrimse.exe":
        raise SystemExit("configured GOG SkyrimSE.exe is missing")

    product_version = read_executable_version(executable)
    version = parse_version(product_version)
    if version[0] != 1 or version[1] != 6 or compare_version(version, MIN_AE_VERSION) < 0:
        raise SystemExit("GOG executable is not a supported Skyrim AE 1.6.318+ build")
    version_parts = tuple(version) + (0,)
    version_file = "-".join(str(part) for part in version_parts)
    library = executable.parent / "Data/SKSE/Plugins" / f"versionlib-{version_file}.bin"
    if not library.is_file():
        raise SystemExit("matching GOG Address Library is missing")

    source = header.read_text(encoding="utf-8")
    method = re.search(
        r"GetLevel\s*\(\s*\)\s*const\s*\{(?P<body>.*?)\n\s*\}",
        source,
        re.DOTALL,
    )
    if not method:
        raise SystemExit("TESActorBaseData::GetLevel inline relocation was not found")
    relocation = re.search(r"RELOCATION_ID\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)", method.group("body"))
    if not relocation:
        raise SystemExit("TESActorBaseData::GetLevel relocation pair was not found")
    ae_id = int(relocation.group(2))

    decoder = _legacy_decoder(legacy / "scripts/address_library_lookup.py")
    library_version, mappings = decoder.decode(library)
    if tuple(library_version) != version_parts:
        raise SystemExit("Address Library internal version does not match the verified GOG executable")
    if ae_id not in mappings:
        raise SystemExit(f"CommonLib AE ID {ae_id} is absent from the matching GOG Address Library")

    print(json.dumps({
        "symbol": "TESActorBaseData::GetLevel",
        "commonlib_revision": subprocess.run(
            ["git", "-C", str(commonlib), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip(),
        "commonlib_header_alias": "include/RE/T/TESActorBaseData.h",
        "commonlib_header_sha256": sha(header),
        "commonlib_ae_id": ae_id,
        "analysis_distribution": "GOG",
        "analysis_binary_product_version": ".".join(str(part) for part in version_parts),
        "analysis_binary_sha256": sha(executable),
        "address_library_alias": f"GOG:Data/SKSE/Plugins/versionlib-{version_file}.bin",
        "address_library_sha256": sha(library),
        "address_library_internal_version": ".".join(str(part) for part in library_version),
        "address_library_rva": f"0x{mappings[ae_id]:X}",
        "read_only": True,
    }, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, AddressLibraryProbeError, TargetError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
