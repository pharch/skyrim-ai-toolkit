#!/usr/bin/env python3
"""Register exact-build Q84 handler and ActorValue-cache findings."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "research/EVIDENCE.json"
GOG = ROOT / ".local/ghidra"
EXE_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
LIB_SHA = "3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e"
HANDLER_STAMPS = ["20261020T022050Z", "20261020T022150Z", "20261020T022256Z", "20261020T022400Z"]
CACHE_STAMPS = [
    "20261020T022712Z", "20261020T022848Z", "20261020T022954Z",
    "20261020T023408Z", "20261020T023507Z", "20261020T023713Z",
    "20261020T023828Z", "20261020T023933Z", "20261020T024104Z",
    "20261020T024205Z", "20261020T024454Z",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_capture(stamp: str) -> tuple[dict, dict[str, str]]:
    raw = GOG / f"gog-query-{stamp}.stdout.raw"
    meta_path = GOG / f"gog-query-{stamp}.meta.json"
    if not raw.is_file() or not meta_path.is_file():
        raise SystemExit(f"missing query capture or metadata: {stamp}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    raw_hash = digest(raw)
    if (
        meta.get("analysis_binary_sha256") != EXE_SHA
        or meta.get("analysis_binary_product_version") != "1.6.1179"
        or meta.get("program_executable_path_matches_gog_binary") is not True
        or meta.get("read_only") is not True
        or meta.get("auto_analysis_disabled") is not True
        or meta.get("ok") is not True
        or meta.get("stdout_sha256") != raw_hash
    ):
        raise SystemExit(f"identity/read-only/hash validation failed: {stamp}")
    hashes = {
        f"{stamp}_stdout": raw_hash,
        f"{stamp}_metadata": digest(meta_path),
        f"{stamp}_adapter": meta["adapter_sha256"],
        f"{stamp}_query_script": meta["query_script_sha256"],
    }
    return meta, hashes


def main() -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    existing = {item["id"] for item in ledger["items"]}
    if existing & {"EV-0684", "EV-0685"}:
        raise SystemExit("Q84 evidence already registered; refusing duplicate IDs")
    if max(int(item["id"].split("-")[1]) for item in ledger["items"]) != 683:
        raise SystemExit("evidence ledger changed; reselect IDs")

    handler_hashes: dict[str, str] = {}
    handler_metas = []
    for stamp in HANDLER_STAMPS:
        meta, hashes = verify_capture(stamp)
        handler_metas.append(meta)
        handler_hashes.update(hashes)

    cache_hashes: dict[str, str] = {}
    cache_metas = []
    for stamp in CACHE_STAMPS:
        meta, hashes = verify_capture(stamp)
        cache_metas.append(meta)
        cache_hashes.update(hashes)

    address_path = GOG / "address-library-vtable-bgsep-perk-entry-20261020T021436Z.stdout.raw"
    address = json.loads(address_path.read_text(encoding="utf-8"))
    if (
        address.get("analysis_binary_sha256") != EXE_SHA
        or address.get("analysis_binary_product_version") != "1.6.1179.0"
        or address.get("address_library_sha256") != LIB_SHA
        or address.get("read_only") is not True
        or address.get("address_library_rva") != "0x17DE680"
    ):
        raise SystemExit("entry-wrapper Address Library identity check failed")
    handler_hashes["20261020T021436Z_address_library_stdout"] = digest(address_path)

    runtime = (
        f"GOG SkyrimSE.exe 1.6.1179.0, SHA-256 {EXE_SHA}; matching GOG Address Library "
        f"SHA-256 {LIB_SHA}; no Steam RVA transfer."
    )
    handler_primary = GOG / "gog-query-20261020T022400Z.stdout.raw"
    cache_primary = GOG / "gog-query-20261020T022712Z.stdout.raw"
    captured_handler = max(meta["captured_utc"] for meta in handler_metas)
    captured_cache = max(meta["captured_utc"] for meta in cache_metas)

    entries = [
        {
            "id": "EV-0684",
            "captured_utc": captured_handler,
            "kind": "tool",
            "source": (
                "Exact GOG handler-table slots selected by BGSEntryPointPerkEntry DATA[1], "
                "their bounded bodies, EPFT data-class gates, and reconciliation with the official "
                "five-master selector 37/39 screen."
            ),
            "artifact": f"private-local:{handler_primary.relative_to(ROOT).as_posix()}",
            "sha256": digest(handler_primary),
            "edition": "AE",
            "runtime": runtime,
            "modified_state": False,
            "lane": "mechanism_inference",
            "tools": [
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x1FF7D88 --pointer-table-rva 0x1FF7D88 --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x386420 --list-call-edges --follow-incoming-calls 8 --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x1FF7E90 --pointer-table-rva 0x1FF7E90 --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x386870 --list-call-edges --follow-incoming-calls 8 --timeout 600",
                "BGSEntryPointPerkEntry wrapper mapping EV-0683 and official PERK bytes EV-0675",
                "experiments/EXP-0133-entrypoint-predicate-side-effects/register_q84_final_evidence.py",
            ],
            "coverage": (
                "EV-0683 separates the handler selector DATA[1] from EPFT, which selects the function-data class. "
                "The exact official five-master selector-37/39 file rows use handler IDs 1 (one row), 3 (19 rows), "
                "and 14 (three file rows), with EPFT class IDs 1/2 [EV-0675], [EV-0683]. Handler 3 at GOG RVA "
                "0x386420 requires the captured type-1 virtual result and multiplies the numeric result by the "
                "OneValue float at +8. Handler 14 at RVA 0x386870 requires type 2, reads the TwoValue float at +8 "
                "as an ActorValue index and +0xC as a coefficient, calls ActorValueOwner slot +8, then applies "
                "(ActorValue*coefficient + a constant) to the numeric result. The three file rows for handler 14 "
                "are AlchemySkillBoosts/PerkSkillBoosts selector-39 records, including a PerkSkillBoosts duplicate "
                "in Update.esm; DATA is 27 0e 01 and EPFD is 00 00 0a 43 0a d7 23 3c. The payload encodes numeric "
                "index 138 and coefficient approximately 0.01. CommonLibSSE ActorValues.h labels index 138 "
                "BlockPowerModifier (mutable main-branch reference retrieved 2026-10-20; label only, no pinned "
                "commit): https://github.com/Ryan-rsm-McKenzie/CommonLibSSE/blob/master/include/RE/A/ActorValues.h. "
                "The handler bodies explicitly write the numeric entrypoint result; handler 14's getter cache path "
                "is bounded separately in EV-0685. Gates and file-level counts do not resolve a profile winner or "
                "establish which actor context is live in Steam."
            ),
            "result": (
                "PASS for the corrected bounded mapping. IDs 3 and 14 are the actual selected handlers for most "
                "matching rows, not EPFT IDs. Their direct writes are numeric result writes; ID 14 also calls the "
                "ActorValue getter and may update derived-value caches on a miss [EV-0685]. No equipment, HitData, "
                "skill-progress, or event submission write appears in the captured handler bodies. This does not "
                "exclude all indirect callbacks, other selectors/plugins, Steam-specific behavior, or a live result."
            ),
            "local_hashes": handler_hashes,
            "related_evidence": ["EV-0670", "EV-0671", "EV-0672", "EV-0675", "EV-0681", "EV-0682", "EV-0683"],
        },
        {
            "id": "EV-0685",
            "captured_utc": captured_cache,
            "kind": "tool",
            "source": (
                "Exact GOG ActorValue getter and its captured derived-value and ActiveEffect cache read/write "
                "helpers, plus the ActorValueInfo default-value callback branch."
            ),
            "artifact": f"private-local:{cache_primary.relative_to(ROOT).as_posix()}",
            "sha256": digest(cache_primary),
            "edition": "AE",
            "runtime": runtime,
            "modified_state": False,
            "lane": "mechanism_inference",
            "tools": [
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x189F6A0 --vtable-slot 1 --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x7283D0 --list-call-edges --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x728400 --list-call-edges --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x6D2120 --list-call-edges --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x6D2C30 --list-call-edges --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x189F6A0 --vtable-slot 3 --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x6D2510 --list-call-edges --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x6D25B0 --list-call-edges --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x43C190 --list-call-edges --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x43C270 --list-call-edges --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --pointer-table-rva 0x20F7710 --pointer-count 1 --timeout 600",
                "experiments/EXP-0133-entrypoint-predicate-side-effects/register_q84_final_evidence.py",
            ],
            "coverage": (
                "The Actor secondary vtable at RVA 0x189F6A0, RTTI .?AVActor@@ and subobject offset +0xB8, maps "
                "slot 1 to FUN_1406B4460 [raw capture 20261020T022712Z]. The getter first checks an ActiveEffect "
                "derived-value cache through FUN_1407283D0; on a miss it calls the ActorValueOwner base-value virtual, "
                "sums three modifier floats via FUN_1406D2120, then writes the result into the ActiveEffect cache "
                "through FUN_140728400. That helper stores a float at manager+0x30 indexed by the ActorValueInfo "
                "table and clears the adjacent byte flag. The base-value virtual target FUN_1406B46A0 also reads and "
                "writes an Actor-side per-value cache at Actor+0x150 through FUN_1406D2510/FUN_1406D25B0. "
                "FUN_1406D2C30 resolves the modifier-array slot under synchronized lock helpers. The captured "
                "direct writes in these helpers are to derived-value caches, lock bookkeeping, or output parameters; "
                "no direct permanent/temporary/damage ActorValue setter, equipment writer, HitData writer, "
                "UseSkill/AVSK sink, or event submission was identified in this bounded path. FUN_14043C270 "
                "contains an indirect ActorValueInfo+0x68 callback; the exact runtime target for index 138 is not "
                "resolved because the global ActorValueInfo table pointer at RVA 0x20F7710 is zero in the static "
                "image. This is not evidence that the callback or runtime target is absent."
            ),
            "result": (
                "PASS for identifying cache-only direct writes on the captured GOG miss path. Handler 14 is not "
                "purely read-only at the memory level: a cache miss can populate Actor+0x150 and ActiveEffect "
                "manager+0x30 derived-value caches. The captured body does not directly mutate the underlying "
                "permanent/temporary/damage values or armor/equipment/HitData/skill-progress state. A runtime "
                "ActorValueInfo callback target remains unresolved, so this is a bounded static result, not a "
                "transitive negative or a Steam/runtime claim."
            ),
            "local_hashes": cache_hashes,
            "related_evidence": ["EV-0670", "EV-0671", "EV-0675", "EV-0683", "EV-0684"],
        },
    ]
    ledger["items"].extend(entries)
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": [item["id"] for item in entries], "handler_captures": len(HANDLER_STAMPS), "cache_captures": len(CACHE_STAMPS)}, indent=2))


if __name__ == "__main__":
    main()
