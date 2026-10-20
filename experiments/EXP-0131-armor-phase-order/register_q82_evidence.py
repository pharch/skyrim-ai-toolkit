#!/usr/bin/env python3
"""Register the Q82 GOG call-path and official PERK record captures."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EVIDENCE = ROOT / "research/EVIDENCE.json"
GOG_DIR = ROOT / ".local/ghidra"
PERK_CAPTURE = ROOT / ".local/armor-entrypoint-screen/skyrim-esm-perk-entrypoints-20261020T005935Z.json"
SCREEN_SCRIPT = ROOT / "experiments/EXP-0131-armor-phase-order/screen_vanilla_perk_entries.py"
SOURCE_NOTE = ROOT / ".local/alignment/transactions/TX-20261020-0001/q82-commonlib-entrypoint-source-note.json"
EXPECTED_EXE_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def gog_bundle(ev_id: str, label: str, stamps: list[str], result: str, coverage: str,
               related: list[str]) -> dict:
    metas = []
    local_hashes: dict[str, str] = {}
    for stamp in stamps:
        raw = GOG_DIR / f"gog-query-{stamp}.stdout.raw"
        metadata = GOG_DIR / f"gog-query-{stamp}.meta.json"
        if not raw.is_file() or not metadata.is_file():
            raise SystemExit(f"missing Ghidra artifact for {stamp}")
        meta = json.loads(metadata.read_text(encoding="utf-8"))
        if (meta.get("analysis_binary_sha256") != EXPECTED_EXE_SHA or
                meta.get("analysis_binary_product_version") != "1.6.1179" or
                meta.get("program_executable_path_matches_gog_binary") is not True or
                meta.get("read_only") is not True or meta.get("auto_analysis_disabled") is not True or
                meta.get("ok") is not True):
            raise SystemExit(f"identity or read-only check failed for {stamp}")
        if meta.get("stdout_sha256") != digest(raw):
            raise SystemExit(f"stdout hash mismatch for {stamp}")
        metas.append(meta)
        local_hashes[f"{stamp}_stdout"] = digest(raw)
        local_hashes[f"{stamp}_metadata"] = digest(metadata)
        local_hashes[f"{stamp}_adapter"] = meta["adapter_sha256"]
        local_hashes[f"{stamp}_query_script"] = meta["query_script_sha256"]
    primary = GOG_DIR / f"gog-query-{stamps[0]}.stdout.raw"
    first = metas[0]
    commands = []
    for stamp, meta in zip(stamps, metas):
        parts = ["python3 scripts/python_env.py run tools/ghidra_probe.py"]
        if meta.get("requested_rva"):
            parts.extend(["--rva", meta["requested_rva"]])
        if meta.get("requested_pointer_table_rva"):
            parts.extend(["--pointer-table-rva", meta["requested_pointer_table_rva"]])
            parts.extend(["--pointer-count", str(meta["requested_pointer_count"])])
        if meta.get("requested_address_rva"):
            parts.extend(["--address-rva", meta["requested_address_rva"]])
        if meta.get("enumerate_call_edges"):
            parts.append("--list-call-edges")
        if meta.get("follow_incoming_calls"):
            parts.extend(["--follow-incoming-calls", str(meta["follow_incoming_calls"])])
        if meta.get("follow_direct_calls"):
            parts.extend(["--follow-direct-calls", str(meta["follow_direct_calls"])])
        parts.extend(["--timeout", "600"])
        commands.append(" ".join(parts))
    return {
        "id": ev_id,
        "captured_utc": max(meta["captured_utc"] for meta in metas),
        "kind": "tool",
        "source": f"{label}; existing configured GOG Ghidra project opened read-only with auto-analysis disabled.",
        "artifact": f"private-local:{primary.relative_to(ROOT).as_posix()}",
        "sha256": digest(primary),
        "edition": "AE",
        "runtime": f"GOG SkyrimSE.exe 1.6.1179.0, SHA-256 {EXPECTED_EXE_SHA}; no Steam RVA transfer.",
        "modified_state": False,
        "lane": "offline",
        "tools": commands + ["experiments/EXP-0131-armor-phase-order/register_q82_evidence.py"],
        "coverage": coverage,
        "result": result,
        "local_hashes": local_hashes,
        "related_evidence": related,
    }


def main() -> None:
    ledger = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    existing = {item["id"] for item in ledger["items"]}
    expected_ids = {f"EV-{i:04d}" for i in range(670, 677)}
    if existing & expected_ids:
        raise SystemExit("Q82 evidence IDs already exist; refusing duplicate registration")
    if max(int(item["id"].split("-")[1]) for item in ledger["items"]) != 669:
        raise SystemExit("evidence ledger no longer ends at EV-0669; reselect IDs before registration")

    entries = [
        gog_bundle(
            "EV-0670", "HitData builder/caller order through the actual player-receiver AV11/AV12 branch",
            ["20261020T003159Z", "20261020T003304Z", "20261020T003743Z", "20261020T003851Z"],
            "PASS for the bounded GOG source order: FUN_1407ddf50 snapshots physicalDamage before AV39/armor-factor reduction to totalDamage; builder wrappers then call geometry/flag helpers and return to FUN_1406bcaa0. The receiver's unblocked worn-ARMO AV11/AV12 scan and UseSkill call are in that same resolver; FUN_1406b9df0 is called later. No live protection, AVSK, Steam equivalence, or same-frame gameplay result is established.",
            "Four identity-checked GOG captures include the full direct-call edge scan for FUN_1407ddf50 and FUN_1406bcaa0, selected caller decompilation, and bounded decompilation of FUN_1407de5c0/FUN_1407df220. The builder snapshots totalDamage into physicalDamage, applies the AV39/armor factor to totalDamage, and the resolver performs the unblocked receiver equipment scan before its later FUN_1406b9df0 call. Indirect calls are retained as bounded residuals; no yield or user-input event is identified in this path.",
            ["EV-0222", "EV-0223", "EV-0261", "EV-0285", "EV-0286", "EV-0287"],
        ),
        gog_bundle(
            "EV-0671", "GOG synchronous perk-entry visitor and selector-ID call sites in the hit builder",
            ["20261020T003511Z", "20261020T003623Z", "20261020T003952Z", "20261020T004058Z", "20261020T004154Z"],
            "PASS for the bounded GOG visitor chain: FUN_1407ddf50 calls FUN_140386070 with selector values 0x25 and 0x27; the visitor synchronously checks the Actor gate and invokes the PlayerCharacter entrypoint-list virtual slot. The entry callback passes each entry's function ID and data to a separate dispatch helper. Selector bytes are not function IDs. No event queue or equipment mutation is shown in the visitor body; downstream dispatch is resolved separately in EV-0672.",
            "Captures contain complete FUN_140386070 call-edge census and disassembly/decompilation; PlayerCharacter vtable slots 0xFF/0x100; the concrete slot-0x100 entry-list walk FUN_14068f0c0; the entry callback FUN_1403861f0; and its single direct dispatch helper FUN_140386270. The vtable walk visits the selected actor entry array synchronously. The `FUN_1403861f0` visitor invokes one virtual gate and then reads function ID/data from the entry object before dispatch. Entry-point function-data methods and full runtime object types remain separately bounded.",
            ["EV-0222", "EV-0261"],
        ),
        gog_bundle(
            "EV-0672", "Perk selector and function-ID dispatch resolution for official SetValue/AddValue rows",
            ["20261020T010057Z", "20261020T010200Z", "20261020T005959Z", "20261020T005108Z", "20261020T004311Z", "20261020T004446Z", "20261020T004544Z", "20261020T004641Z", "20261020T004751Z"],
            "PASS for the bounded GOG dispatch: the per-entry function IDs 1 and 2 resolve to FUN_140386340 and FUN_1403863b0. The first writes the configured value to the numeric output when its gates pass; the second adds the configured float. Their complete direct-call scans have no direct engine/event/equipment calls, but each retains one virtual function-data predicate at object vtable +8. These results classify only the official selector/function pairs recorded in EV-0675 and do not prove all possible mods or runtime function-data subclasses.",
            "Captures distinguish selector-ID lookup from the separate function-ID dispatch table: selector values 0x25/0x27 are passed to the Actor visitor; the selected official record function IDs 1/2 index a 0x18-byte-stride handler table at GOG VA 0x141FF7D40, where entries resolve to FUN_140386340/0x1403863B0. The value at the table base itself and adjacent selector-map bytes were checked and not treated as the ID-1/ID-2 targets. Both handler bodies write only through the supplied numeric result pointer in their bounded decompilation; virtual data predicates remain unresolved.",
            ["EV-0222", "EV-0261"],
        ),
        gog_bundle(
            "EV-0673", "Separate FUN_1406b9df0 HandleHealthDamage/ProcessTrapHit continuation comparator",
            ["20261020T005306Z"],
            "PASS for the same-build bounded comparator query: FUN_1406b9df0 is a distinct post-resolver receiver/health-damage path with its own indirect sites and prior EV-0293/EV-0295 call-path evidence. It is not the direct pre-award AV11/AV12 selector. The query does not prove that every indirect descendant omits an armor award or that a trap hit produces positive live protection.",
            "Read-only direct-call edge census, disassembly, decompilation and up to eight incoming caller bodies for GOG FUN_1406b9df0 at RVA 0x6B9DF0. The selected call from FUN_1406bcaa0 occurs after the receiver skill branch; ProcessTrapHit enters the same function through a separate earlier builder path per EV-0293/EV-0295. Twenty-eight indirect sites remain within this function body.",
            ["EV-0222", "EV-0293", "EV-0295"],
        ),
        gog_bundle(
            "EV-0674", "PlayerCharacter UseSkill slot target referenced by the receiver award path",
            ["20261020T005408Z"],
            "PASS for the exact GOG vtable pointer: PlayerCharacter slot 0xF7 at table RVA 0x18AD528 resolves to FUN_140739050, consistent with EV-0221. In FUN_1406bcaa0 the attacker-side UseSkill call is conditional on the attacker being the player; for a normal player receiver hit that branch is not the armor-XP interposition point. The player receiver's own call remains after the worn-armor scan.",
            "One-qword read-only GOG vtable pointer query. This capture maps only the slot target; implementation behavior and its existing positive-points gate/progress helper are covered by EV-0221. It is not a Steam mapping or live callback trace.",
            ["EV-0219", "EV-0221", "EV-0222", "EV-0260"],
        ),
    ]

    if not PERK_CAPTURE.is_file():
        raise SystemExit("official PERK screen capture is missing")
    perk = json.loads(PERK_CAPTURE.read_text(encoding="utf-8"))
    expected_plugins = {"Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"}
    if set(perk.get("plugin_sha256", {})) != expected_plugins:
        raise SystemExit("official PERK screen did not cover the exact five-master set")
    if perk.get("coverage", {}).get("matching_entry_rows") != 23:
        raise SystemExit("unexpected target-selector entry count")
    selector_counts = perk["coverage"]["entrypoint_selector_counts"]
    if selector_counts.get("37") != 13 or selector_counts.get("39") != 10:
        raise SystemExit("unexpected official selector distribution")
    screen_hashes = {"capture_json": digest(PERK_CAPTURE), "screen_script": digest(SCREEN_SCRIPT)}
    screen_hashes.update({f"{plugin}_source": file_hash for plugin, file_hash in perk["plugin_sha256"].items()})
    entries.append({
        "id": "EV-0675",
        "captured_utc": perk["captured_utc"],
        "kind": "tool",
        "source": "Configured Steam AE official five-master files read with the retained direct read-only TES4 parser; no plugin mutation or winner resolution.",
        "artifact": f"private-local:{PERK_CAPTURE.relative_to(ROOT).as_posix()}",
        "sha256": digest(PERK_CAPTURE),
        "edition": "AE",
        "runtime": "Configured Steam Skyrim AE Data tree associated with the verified Steam 1.6.1170.0 five-master native session EV-0664; this direct parser screen does not resolve the active profile, load order, or winners.",
        "modified_state": False,
        "lane": "offline",
        "tools": [
            "python3 scripts/python_env.py run experiments/EXP-0131-armor-phase-order/screen_vanilla_perk_entries.py",
            "tools.plugin_reader.read_plugin via strict dispatcher",
            "experiments/EXP-0131-armor-phase-order/register_q82_evidence.py",
        ],
        "coverage": "All PERK records in Skyrim.esm (375), Update.esm (16), Dawnguard.esm (57), HearthFires.esm (1), and Dragonborn.esm (74) were parsed, covering 785 entrypoint DATA rows. The raw DATA first byte matches the documented selector layout in sampled records; 13 rows use selector 37 (kModTargetDamageResistance), and 10 use selector 39 (kModPercentBlocked). All 13 selector-37 rows use EPFT function byte 1; selector-39 rows use function byte 1 or 2. Duplicate/override records are preserved as file-level rows rather than resolved. No profile winners, Creation Club files, runtime use, hit, protection, or AVSK change is included.",
        "result": "PASS for a bounded official five-master source screen. The input rows that match the two hit-builder selectors use only function IDs 1 and 2; raw EPFD payloads are preserved. This narrows the synchronous vanilla entrypoint path to numeric SetValue/AddValue operations when interpreted with the source enum in EV-0676. It does not exclude other plugins, other selectors, or a runtime subclass side effect outside the captured call body.",
        "local_hashes": screen_hashes,
        "related_evidence": ["EV-0671", "EV-0672", "EV-0664"],
    })

    source_note = {
        "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": [
            {
                "url": "https://ng.commonlib.dev/_b_g_s_entry_point_8h_source.html",
                "header": "CommonLibSSE-NG/include/RE/B/BGSEntryPoint.h",
                "relevant_definition": "ENTRY_POINT assigns kModTargetDamageResistance = 37 and kModPercentBlocked = 39. This is an external generated source page; an exact repository commit was not captured.",
            },
            {
                "url": "https://ng.commonlib.dev/_b_g_s_entry_point_perk_entry_8h_source.html",
                "header": "CommonLibSSE-NG/include/RE/B/BGSEntryPointPerkEntry.h",
                "relevant_definition": "EntryData::Function assigns kSetValue = 1 and kAddValue = 2; EntryData stores the selected entry point and function fields. This is an external generated source page; an exact repository commit was not captured.",
            },
        ],
        "interpretation": "These source pages supply enum labels/layout context only. The GOG binary identity, call edges and handler bodies come from EV-0670 through EV-0674; the installed record bytes and five-master scope come from EV-0675.",
        "limitations": "Mutable generated documentation, retrieved 2026-10-20. It is not a GOG/Steam binary identity source, runtime trace, profile winner, or proof of general behavior beyond the referenced definitions.",
    }
    SOURCE_NOTE.parent.mkdir(parents=True, exist_ok=True)
    SOURCE_NOTE.write_text(json.dumps(source_note, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    entries.append({
        "id": "EV-0676",
        "captured_utc": source_note["retrieved_utc"],
        "kind": "source",
        "source": "CommonLibSSE-NG generated public source documentation for BGSEntryPoint and BGSEntryPointPerkEntry headers; mutable page, exact repository revision unavailable.",
        "artifact": f"private-local:{SOURCE_NOTE.relative_to(ROOT).as_posix()}",
        "sha256": digest(SOURCE_NOTE),
        "edition": "AE",
        "runtime": "External C++ reference headers, not an in-game executable or installed plugin source.",
        "modified_state": False,
        "lane": "offline",
        "tools": ["web retrieval on 2026-10-20", "experiments/EXP-0131-armor-phase-order/register_q82_evidence.py"],
        "coverage": "The source headers label selector IDs 37/39 as kModTargetDamageResistance/kModPercentBlocked and function IDs 1/2 as kSetValue/kAddValue. The captured GOG calls and handler functions are independent binary evidence; no RVA or runtime behavior is imported from CommonLib.",
        "result": "PASS as an enum/structure label reference with URL provenance. The documentation is mutable and not revision-pinned; it supports labels only and is paired with exact GOG binary and record-byte evidence.",
        "related_evidence": ["EV-0671", "EV-0672", "EV-0675"],
    })

    ledger["items"].extend(entries)
    EVIDENCE.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": [entry["id"] for entry in entries], "official_selector_rows": len(perk["entries"]), "source_note_sha256": digest(SOURCE_NOTE)}, indent=2))


if __name__ == "__main__":
    main()
