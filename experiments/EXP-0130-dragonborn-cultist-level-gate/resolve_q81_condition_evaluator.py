#!/usr/bin/env python3
"""Resolve CommonLib's TESCondition evaluator IDs in the verified GOG library."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.local_config import read_local_config  # noqa: E402
from tools.ae_target import _native_path, parse_version, read_executable_version  # noqa: E402

SUMMARY = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-condition-evaluator-gog-addresses.json"
COMMONLIB_SOURCE = "https://github.com/CharmedBaryon/CommonLibSSE-NG/blob/main/src/RE/T/TESCondition.cpp#L493-L500"
SYMBOL_IDS = {"TESCondition::IsTrue": 29888, "TESConditionItem::IsTrue": 29924}
EXPECTED_VERSION = (1, 6, 1179, 0)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    config = read_local_config(ROOT)
    required = ("LEGACY_SKYRIM_REPO", "GHIDRA_ANALYSIS_EXE_GOG")
    missing = [key for key in required if not config.get(key, "").strip()]
    if missing:
        raise SystemExit("missing bindings: " + ", ".join(missing))
    legacy = _native_path(config["LEGACY_SKYRIM_REPO"]).resolve()
    executable = _native_path(config["GHIDRA_ANALYSIS_EXE_GOG"]).resolve()
    version = parse_version(read_executable_version(executable))
    version_parts = tuple(version) + (0,)
    if version_parts != EXPECTED_VERSION:
        raise SystemExit("GOG executable ProductVersion is not exactly 1.6.1179.0")
    address_library = executable.parent / "Data" / "SKSE" / "Plugins" / "versionlib-1-6-1179-0.bin"
    decoder_path = legacy / "scripts" / "address_library_lookup.py"
    if not address_library.is_file() or not decoder_path.is_file():
        raise SystemExit("the matching GOG Address Library or legacy decoder is unavailable")
    spec = importlib.util.spec_from_file_location("q81_address_library_decoder", decoder_path)
    if spec is None or spec.loader is None:
        raise SystemExit("could not load configured Address Library decoder")
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    library_version, mappings = decoder.decode(address_library)
    if tuple(library_version) != EXPECTED_VERSION:
        raise SystemExit("Address Library internal version does not match GOG executable")
    addresses = {}
    for symbol, ae_id in SYMBOL_IDS.items():
        if ae_id not in mappings:
            raise SystemExit(f"AE relocation ID {ae_id} is absent from the matching GOG database")
        addresses[symbol] = {"ae_id": ae_id, "rva": f"0x{int(mappings[ae_id]):X}"}
    result = {
        "gog_product_version": ".".join(map(str, version_parts)),
        "gog_executable_sha256": digest(executable),
        "address_library_sha256": digest(address_library),
        "address_library_internal_version": ".".join(map(str, library_version)),
        "symbol_source": COMMONLIB_SOURCE,
        "symbols": addresses,
        "scope": "GOG 1.6.1179.0 only; addresses are not Steam 1.6.1170.0 RVAs.",
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
