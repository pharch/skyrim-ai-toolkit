#!/usr/bin/env python3
"""Register the revision-pinned Q-0080 local and static evidence captures."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "research" / "EVIDENCE.json"


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> None:
    captured = datetime.now(timezone.utc).isoformat(timespec="seconds")
    page_paths = {
        "generic_magic_apparel": ".local/uesp/q80/generic-magic-apparel.raw.json",
        "leveled_lists": ".local/uesp/q80/leveled-lists.raw.json",
        "madesi": ".local/uesp/q80/madesi.raw.json",
    }
    pages = {name: json.loads((ROOT / path).read_text(encoding="utf-8")) for name, path in page_paths.items()}
    artifact_paths = {
        "lvli_refs": ".local/alignment/transactions/TX-20261019-0001/armocandidate-lvli-reference-scan.json",
        "lvli_chain": ".local/alignment/transactions/TX-20261019-0001/armocandidate-lvli-parent-chain.schema-checked.json",
        "lvli_owners": ".local/alignment/transactions/TX-20261019-0001/armocandidate-lvli-owners.json",
        "npc_levels": ".local/alignment/transactions/TX-20261019-0001/citizen-inventory-npc-levels.corrected.json",
        "native_result": ".local/xedit-authoritative-copy/out/xedit/20261019T223022.406639Z/native-result.json",
        "native_tsv": ".local/xedit-authoritative-copy/out/xedit/20261019T223022.406639Z/native-records.tsv",
        "ghidra_callers": ".local/ghidra/gog-query-20261019T224226Z.stdout.raw",
        "ghidra_meta": ".local/ghidra/gog-query-20261019T224226Z.meta.json",
    }
    hashes = {key: digest(path) for key, path in artifact_paths.items()}
    payloads = {key: json.loads((ROOT / artifact_paths[key]).read_text(encoding="utf-8")) for key in ("lvli_refs", "lvli_chain", "lvli_owners", "npc_levels", "native_result", "ghidra_meta")}
    if pages["generic_magic_apparel"].get("revision_id") != 3602607 or pages["leveled_lists"].get("revision_id") != 3484019 or pages["madesi"].get("revision_id") != 3579880:
        raise SystemExit("local UESP page revisions differ from the screened inputs")
    if payloads["npc_levels"].get("owner_record_count") != 421:
        raise SystemExit("corrected NPC owner scan does not contain the expected record count")
    if payloads["native_result"].get("loader_status") != "Background Loader: finished":
        raise SystemExit("native SSEView result did not finish loading")
    ghidra_checks = payloads["ghidra_meta"].get("checks", {})
    if payloads["ghidra_meta"].get("ok") is not True or ghidra_checks.get("program_identity_matches_gog_binary") is not True:
        raise SystemExit("GOG caller capture is not identity-checked")

    common = {
        "captured_utc": captured,
        "edition": "AE",
        "modified_state": False,
    }
    items = [
        {
            **common,
            "id": "EV-0645",
            "kind": "wiki",
            "source": "Local UESP SQLite payloads, each revision-pinned: Skyrim:Generic Magic Apparel rev 3602607; Skyrim:Leveled Lists rev 3484019; Skyrim:Madesi rev 3579880. Local corpus completeness remains unverified.",
            "artifact": "private-local:" + page_paths["generic_magic_apparel"],
            "sha256": digest(page_paths["generic_magic_apparel"]),
            "runtime": "Secondary-source grounding only; no live Skyrim runtime observation.",
            "lane": "offline",
            "tools": ["strict Python 3.12 dispatcher", "tools.uesp local page lookup"],
            "coverage": "Item table row/form ID and listed base level for ARMO 000FC061; general leveled-list request and flags description; Madesi page level, location, and merchant identity.",
            "result": "The local UESP pages identify ARMO 000FC061 as a level-8 Gold Jeweled Necklace of Resist Magic; describe list requests as usually using player level, possibly modified by encounter-zone level; and list Madesi as a level-8 Riften NPC. These are revision-pinned leads, not engine or runtime proof.",
            "local_hashes": {path: digest(path) for path in page_paths.values()},
            "related_evidence": ["EV-0398", "EV-0260"],
        },
        {
            **common,
            "id": "EV-0646",
            "kind": "record",
            "source": "Read-only TES4 parsing and reference scans across the exact five official masters, with source SHA-256 values preserved in each capture. LVLO field offsets cross-checked against the configured legacy xEdit schema tmp/wbDefinitionsTES5.pas, SHA-256 a148b391f175d5cd6af102d6fbb8594e19dcd92916802fe1086eda1fc873356b.",
            "artifact": "private-local:" + artifact_paths["lvli_chain"],
            "sha256": hashes["lvli_chain"],
            "runtime": "Official Skyrim AE source-record scope only; no profile-specific winning-plugin claim or live inventory observation.",
            "lane": "offline",
            "tools": ["strict Python 3.12 dispatcher", "tools.plugin_reader direct TES4 parser", "read-only five-master LVLI scans"],
            "coverage": "ARMO 000FC061 LVLI membership and parent-list reachability; NPC_/LVLI raw references to citizen pocket lists; LVLO u16 Level and Count decoding with unknown bytes preserved.",
            "result": "The exact official source records place ARMO 000FC061 in LItemEnchNecklaceResistMagic at Level 8, with the same object repeated at Levels 9–11. Parent lists reach this table through LItemEnchNecklaceAll and LootCitizenNecklaceList; LootCitizenPocketsCommon directly references LootCitizenNecklaceList25. The all-record scan found 341 NPC_ references to LootCitizenPocketsCommon, 79 to LootCitizenPocketsRich, and one NPC_ reference to LootCitizenNecklaceList (Brelas). This proves list membership and nesting only, not a runtime requested level, list roll, actor inventory, or player acquisition.",
            "local_hashes": {artifact_paths[k]: hashes[k] for k in ("lvli_refs", "lvli_chain", "lvli_owners")},
            "related_evidence": ["EV-0398", "EV-0403", "EV-0404", "EV-0405", "EV-0406", "EV-0645"],
        },
        {
            **common,
            "id": "EV-0647",
            "kind": "record",
            "source": "Native SSEView -view query using the original Apply Script field walker, exact Skyrim.esm LVLI LootCitizenPocketsCommon, and an explicit official five-master loaded-file inventory.",
            "artifact": "private-local:" + artifact_paths["native_result"],
            "sha256": hashes["native_result"],
            "runtime": "Native SSEView source inspection on the configured Windows environment; loaded Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm, and Dragonborn.esm plus SkyrimSE.exe. Profile-specific overrides are not established.",
            "lane": "offline",
            "tools": ["strict Python 3.12 dispatcher", "tools/xedit_bridge.py native-query", "SSEView native field walker"],
            "coverage": "78 decoded fields for LVLI 001046D1; LVLF Use All; eight level-1 children including LootCitizenNecklaceList25; native TSV and source file hashes.",
            "result": "Native xEdit labels LootCitizenPocketsCommon LVLF as Use All and shows its necklace branch points to LootCitizenNecklaceList25 at Level 1. This list-level flag returns its listed children; it does not establish the nested target item's runtime requested level or actual roll.",
            "local_hashes": {artifact_paths["native_result"]: hashes["native_result"], artifact_paths["native_tsv"]: hashes["native_tsv"]},
            "related_evidence": ["EV-0398", "EV-0645", "EV-0646"],
        },
        {
            **common,
            "id": "EV-0648",
            "kind": "record",
            "source": "Read-only TES4 NPC_ record screen for all official records referencing the target pocket/necklace lists; ACBS offsets decoded against the hash-identified configured xEdit schema.",
            "artifact": "private-local:" + artifact_paths["npc_levels"],
            "sha256": hashes["npc_levels"],
            "runtime": "Official five-master NPC record scope only; ACBS fields are not an observed runtime leveled-list request parameter.",
            "lane": "offline",
            "tools": ["strict Python 3.12 dispatcher", "tools/plugin_reader direct TES4 parser", "configured xEdit schema reference"],
            "coverage": "421 NPC_ owner records: 341 common-pocket, 79 rich-pocket, one direct necklace-list owner; raw ACBS fields including Madesi's level and PCLevelMult flag.",
            "result": "Madesi (Skyrim.esm:0001B072) directly references LootCitizenPocketsCommon. Its ACBS record has PCLevelMult off and Level 8. The record is a concrete actor-level candidate, but neither this source nor the NPC owner scan establishes whether a nested NPC inventory list receives the actor level or the player's/encounter-zone level.",
            "local_hashes": {artifact_paths["npc_levels"]: hashes["npc_levels"]},
            "related_evidence": ["EV-0645", "EV-0646"],
        },
        {
            **common,
            "id": "EV-0649",
            "kind": "native",
            "source": "Fresh read-only GOG Ghidra direct-call census for the previously RTTI- and Address-Library-mapped MagicTarget::CheckResistance target FUN_1406c45a0.",
            "artifact": "private-local:" + artifact_paths["ghidra_callers"],
            "sha256": hashes["ghidra_callers"],
            "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing project read-only, auto-analysis disabled, separate from verified Steam AE 1.6.1170.0.",
            "lane": "mechanism_inference",
            "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py direct call-edge census"],
            "coverage": "Exact function RVA 0x6C45A0, seven internal indirect call sites, direct incoming call and xref counts, project/executable identity checks.",
            "result": "The target query is identity-checked on the GOG 1.6.1179.0 image and finds zero direct code callers/xref call edges plus seven indirect calls inside the function. This is consistent with virtual dispatch and does not establish that virtual callsites are absent; the receiver/callsite mapping remains open.",
            "local_hashes": {artifact_paths[k]: hashes[k] for k in ("ghidra_callers", "ghidra_meta")},
            "related_evidence": ["EV-0400", "EV-0401", "EV-0402", "EV-0222", "EV-0260"],
        },
    ]

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    known = {item["id"] for item in ledger["items"]}
    missing = [item for item in items if item["id"] not in known]
    unexpected = sorted(known.intersection(item["id"] for item in items))
    if unexpected and len(unexpected) != len(items):
        raise SystemExit("partial Q-0080 evidence registration found; inspect the ledger before retrying")
    if not unexpected:
        ledger["items"].extend(missing)
        LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": [item["id"] for item in items if item["id"] not in known], "already_present": unexpected, "count": len(ledger["items"])}, indent=2))


if __name__ == "__main__":
    main()
