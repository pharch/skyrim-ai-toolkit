#!/usr/bin/env python3
"""Register Q84's GOG function-data class, factory, and gate captures."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "research/EVIDENCE.json"
GOG = ROOT / ".local/ghidra"
EXPECTED_EXE_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
EXPECTED_LIB_SHA = "3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ledger = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    existing = {item["id"] for item in ledger["items"]}
    if existing & {"EV-0681", "EV-0682"}:
        raise SystemExit("Q84 evidence IDs already exist; refusing duplicate registration")
    if max(int(item["id"].split("-")[1]) for item in ledger["items"]) != 680:
        raise SystemExit("evidence ledger no longer ends at EV-0680; reselect IDs")

    stamps = [
        "20261020T015941Z",  # OneValue GetType, slot +8
        "20261020T020130Z",  # OneValue LoadFunctionData, slot +0x10
        "20261020T020522Z",  # TwoValue GetType, slot +8
        "20261020T020624Z",  # TwoValue LoadFunctionData, slot +0x10
        "20261020T020858Z",  # PERK loader and function-data factory
    ]
    metadata_by_stamp: dict[str, dict] = {}
    hashes: dict[str, str] = {}
    for stamp in stamps:
        raw = GOG / f"gog-query-{stamp}.stdout.raw"
        meta_path = GOG / f"gog-query-{stamp}.meta.json"
        if not raw.is_file() or not meta_path.is_file():
            raise SystemExit(f"missing Ghidra capture or metadata: {stamp}")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        raw_hash = digest(raw)
        if (
            meta.get("analysis_binary_sha256") != EXPECTED_EXE_SHA
            or meta.get("analysis_binary_product_version") != "1.6.1179"
            or meta.get("program_executable_path_matches_gog_binary") is not True
            or meta.get("read_only") is not True
            or meta.get("auto_analysis_disabled") is not True
            or meta.get("ok") is not True
            or meta.get("stdout_sha256") != raw_hash
        ):
            raise SystemExit(f"GOG identity, read-only, or capture-hash check failed: {stamp}")
        metadata_by_stamp[stamp] = meta
        hashes[f"{stamp}_stdout"] = raw_hash
        hashes[f"{stamp}_metadata"] = digest(meta_path)
        hashes[f"{stamp}_adapter"] = meta["adapter_sha256"]
        hashes[f"{stamp}_query_script"] = meta["query_script_sha256"]

    address_files = {
        "base": "address-library-vtable-bgsep-function-data-20261020T020446Z.stdout.raw",
        "onevalue": "address-library-vtable-bgsep-function-data-onevalue-20261020T020446Z.stdout.raw",
        "twovalue": "address-library-vtable-bgsep-function-data-twovalue-20261020T020446Z.stdout.raw",
    }
    address_payloads: dict[str, dict] = {}
    for key, name in address_files.items():
        path = GOG / name
        payload = json.loads(path.read_text(encoding="utf-8"))
        if (
            payload.get("analysis_binary_sha256") != EXPECTED_EXE_SHA
            or payload.get("analysis_binary_product_version") != "1.6.1179.0"
            or payload.get("address_library_sha256") != EXPECTED_LIB_SHA
            or payload.get("read_only") is not True
            or payload.get("ok") is not True
        ):
            raise SystemExit(f"Address Library build/hash check failed: {name}")
        address_payloads[key] = payload
        hashes[f"20261020T020446Z_{key}_address_library_stdout"] = digest(path)

    if (
        address_payloads["base"].get("address_library_rva") != "0x17DBEE8"
        or address_payloads["onevalue"].get("address_library_rva") != "0x17DBF30"
        or address_payloads["twovalue"].get("address_library_rva") != "0x17DBF78"
    ):
        raise SystemExit("unexpected GOG function-data vtable relocation")

    primary = GOG / "gog-query-20261020T020858Z.stdout.raw"
    captured = max(meta["captured_utc"] for meta in metadata_by_stamp.values())
    runtime = (
        f"GOG SkyrimSE.exe 1.6.1179.0, SHA-256 {EXPECTED_EXE_SHA}; "
        "matching GOG Address Library SHA-256 " + EXPECTED_LIB_SHA + "; no Steam RVA transfer."
    )
    entries = [
        {
            "id": "EV-0681",
            "captured_utc": captured,
            "kind": "tool",
            "source": "GOG Address Library vtable resolution and existing read-only Ghidra RTTI, vtable-slot, disassembly, decompilation captures for BGSEntryPointFunctionDataOneValue and BGSEntryPointFunctionDataTwoValue.",
            "artifact": f"private-local:{primary.relative_to(ROOT).as_posix()}",
            "sha256": digest(primary),
            "edition": "AE",
            "runtime": runtime,
            "modified_state": False,
            "lane": "offline",
            "tools": [
                "python3 scripts/python_env.py run tools/address_library_probe.py --symbol VTABLE::BGSEntryPointFunctionData",
                "python3 scripts/python_env.py run tools/address_library_probe.py --symbol VTABLE::BGSEntryPointFunctionDataOneValue",
                "python3 scripts/python_env.py run tools/address_library_probe.py --symbol VTABLE::BGSEntryPointFunctionDataTwoValue",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x17DBF30 --vtable-slot 1 --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x17DBF30 --vtable-slot 2 --list-call-edges --follow-direct-calls 8 --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x17DBF78 --vtable-slot 1 --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x17DBF78 --vtable-slot 2 --list-call-edges --follow-direct-calls 8 --timeout 600",
                "experiments/EXP-0133-entrypoint-predicate-side-effects/register_q84_evidence.py",
            ],
            "coverage": "Exact GOG build and matching Address Library resolve base, OneValue, and TwoValue vtables. RTTI identifies both concrete classes. Their slot +8 methods return constant type codes 1 and 2; their slot +0x10 loaders require four and eight bytes respectively, read form data, and store value floats at object +8 (and +0xC for TwoValue). Raw captures include full target disassembly/decompilation and load-reader call edges. This covers the concrete classes used by the later captured factory for EPFT IDs 1/2; it is not a global census of third-party code or runtime-modified objects.",
            "result": "PASS for the bounded GOG implementations. Slot +8 is a pure type-code getter for these two classes, not an equipment, HitData, ActorValue, or event mutation callback. Slot +0x10 is a load-time form-data reader with exact four/eight-byte length gates. The result supports no synchronous side effect from these virtual implementations within the captured code.",
            "local_hashes": hashes,
            "related_evidence": ["EV-0670", "EV-0671", "EV-0672", "EV-0675"],
        },
        {
            "id": "EV-0682",
            "captured_utc": metadata_by_stamp["20261020T020858Z"]["captured_utc"],
            "kind": "tool",
            "source": "GOG PERK entry form-data loader, EPFT class factory, and the function-data virtual dispatch/gate chain in the exact 1.6.1179.0 executable.",
            "artifact": f"private-local:{primary.relative_to(ROOT).as_posix()}",
            "sha256": digest(primary),
            "edition": "AE",
            "runtime": runtime,
            "modified_state": False,
            "lane": "mechanism_inference",
            "tools": [
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x387170 --list-call-edges --follow-direct-calls 8 --follow-incoming-calls 8 --timeout 600",
                "GOG source captures for FUN_1403861f0/FUN_140386270 and SetValue/AddValue handlers EV-0671/EV-0672",
                "official five-master PERK byte screen EV-0675",
                "experiments/EXP-0133-entrypoint-predicate-side-effects/register_q84_evidence.py",
            ],
            "coverage": "The captured FUN_14038f4d0 record loader reads the one-byte EPFT value and passes it to FUN_140387170, whose cases 1 and 2 install the OneValue and TwoValue vtables; the EPFD path invokes the object's load virtual. The same object GetType value selects the handler table [EV-0671], and both numeric handlers gate their result update on GetType()==1 [EV-0672]. The official five-master selector screen contains two file-level EPFT-2 rows with eight-byte EPFD payloads (AlchemySkillBoosts and PerkSkillBoosts, the latter duplicated across Skyrim.esm/Update.esm) and four-byte EPFT-1 rows [EV-0675]. This is a GOG-code/official-record-byte comparison, not a Steam runtime or active-profile winner result.",
            "result": "PASS for the captured static mapping and mismatch: GOG EPFT type 2 creates a TwoValue object whose GetType returns 2, which selects the ID-2 AddValue handler; that handler's inner gate accepts only type 1, so the bounded handler leaves the numeric result unchanged for a type-2 object. This is a strong static no-op inference for matching official rows if their runtime bytes and GOG code path correspond. It does not prove live effect behavior, Steam equivalence, protection, or armor XP.",
            "local_hashes": {
                "20261020T020858Z_stdout": hashes["20261020T020858Z_stdout"],
                "20261020T020858Z_metadata": hashes["20261020T020858Z_metadata"],
                "20261020T020858Z_adapter": hashes["20261020T020858Z_adapter"],
                "20261020T020858Z_query_script": hashes["20261020T020858Z_query_script"],
                "20261020T010057Z_handler1_stdout": "c8c2e026561e24e58cf7d126f61e6df41808f8ceb8288320e15bfbfa3144fe47",
                "20261020T010200Z_handler2_stdout": "3ad2c5b93c31c8b2afe6a08841fbb160bf3dd827f1f8768d43df6a6d3f07f8a1",
            },
            "related_evidence": ["EV-0671", "EV-0672", "EV-0675", "EV-0676", "EV-0681"],
        },
    ]
    ledger["items"].extend(entries)
    EVIDENCE.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": [entry["id"] for entry in entries], "verified_ghidra_captures": len(stamps)}, indent=2))


if __name__ == "__main__":
    main()
