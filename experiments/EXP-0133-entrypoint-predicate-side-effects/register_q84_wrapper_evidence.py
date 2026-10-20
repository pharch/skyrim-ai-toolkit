#!/usr/bin/env python3
"""Register the receiver-level correction for Q84 and the Q82 PERK screen."""
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
    if "EV-0683" in existing:
        raise SystemExit("EV-0683 already exists; refusing duplicate registration")
    if max(int(item["id"].split("-")[1]) for item in ledger["items"]) != 682:
        raise SystemExit("evidence ledger no longer ends at EV-0682; reselect ID")

    stamps = ["20261020T021244Z", "20261020T021533Z", "20261020T021635Z"]
    local_hashes: dict[str, str] = {}
    captured: list[str] = []
    for stamp in stamps:
        raw = GOG / f"gog-query-{stamp}.stdout.raw"
        meta_path = GOG / f"gog-query-{stamp}.meta.json"
        if not raw.is_file() or not meta_path.is_file():
            raise SystemExit(f"missing wrapper capture or metadata: {stamp}")
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
            raise SystemExit(f"GOG identity/read-only/hash validation failed: {stamp}")
        captured.append(meta["captured_utc"])
        local_hashes[f"{stamp}_stdout"] = raw_hash
        local_hashes[f"{stamp}_metadata"] = digest(meta_path)
        local_hashes[f"{stamp}_adapter"] = meta["adapter_sha256"]
        local_hashes[f"{stamp}_query_script"] = meta["query_script_sha256"]

    address = GOG / "address-library-vtable-bgsep-perk-entry-20261020T021436Z.stdout.raw"
    address_data = json.loads(address.read_text(encoding="utf-8"))
    if (
        address_data.get("analysis_binary_sha256") != EXPECTED_EXE_SHA
        or address_data.get("analysis_binary_product_version") != "1.6.1179.0"
        or address_data.get("address_library_sha256") != EXPECTED_LIB_SHA
        or address_data.get("address_library_rva") != "0x17DE680"
        or address_data.get("read_only") is not True
    ):
        raise SystemExit("BGSEntryPointPerkEntry Address Library identity check failed")
    local_hashes["20261020T021436Z_address_library_stdout"] = digest(address)

    primary = GOG / "gog-query-20261020T021244Z.stdout.raw"
    entry = {
        "id": "EV-0683",
        "captured_utc": max(captured),
        "kind": "tool",
        "source": "Exact GOG BGSEntryPointPerkEntry RTTI/vtable targets and the synchronous entry callback's register/disassembly/data-flow path.",
        "artifact": f"private-local:{primary.relative_to(ROOT).as_posix()}",
        "sha256": digest(primary),
        "edition": "AE",
        "runtime": f"GOG SkyrimSE.exe 1.6.1179.0, SHA-256 {EXPECTED_EXE_SHA}; matching GOG Address Library SHA-256 {EXPECTED_LIB_SHA}; no Steam RVA transfer.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "python3 scripts/python_env.py run tools/address_library_probe.py --symbol VTABLE::BGSEntryPointPerkEntry",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x3861F0 --list-call-edges --follow-incoming-calls 8 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x17DE680 --vtable-slot 1 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x17DE680 --vtable-slot 2 --timeout 600",
            "GOG PERK loader/factory capture EV-0682; raw official five-master PERK bytes EV-0675",
            "experiments/EXP-0133-entrypoint-predicate-side-effects/register_q84_wrapper_evidence.py",
        ],
        "coverage": "GOG RTTI identifies the wrapper as BGSEntryPointPerkEntry. Its virtual slot +8 returns byte [entry+0x11], and slot +0x10 returns pointer [entry+0x18]. The synchronous FUN_1403861f0 callback calls these as separate virtuals and passes their returned values separately as handler ID and function-data pointer. The GOG record loader stores the three-byte DATA record at entry+0x10 and separately creates/stores functionData at entry+0x18 using EPFT [EV-0682]. Therefore the handler function selector comes from DATA[1], while EPFT selects the function-data class. Across the 23 official five-master rows for selector 37/39, DATA[1] values are 1 (one row), 3 (19 rows), and 14 (three file-level rows); EPFT values are 1/2 [EV-0675]. EV-0675's raw capture remains valid; its earlier coverage/result interpreted EPFT as the operation ID and is superseded on that point by this correction. This evidence does not resolve the implementations of handlers 3/14 or Steam/runtime equivalence.",
        "result": "PASS for the receiver/field distinction. EPFT is not the handler ID for these entries: the wrapper's GetFunction method reads the second DATA byte, and GetFunctionData returns the separately stored pointer. The previously inferred ID-2/TwoValue handler mismatch was based on conflating the wrapper function ID with the function-data EPFT class and must not be retained.",
        "local_hashes": local_hashes,
        "related_evidence": ["EV-0671", "EV-0672", "EV-0675", "EV-0681", "EV-0682"],
    }
    ledger["items"].append(entry)
    EVIDENCE.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": entry["id"], "wrapper_vtable_rva": "0x17DE680", "matched_row_count": 23}, indent=2))


if __name__ == "__main__":
    main()
