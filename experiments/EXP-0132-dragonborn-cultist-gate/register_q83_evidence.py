#!/usr/bin/env python3
"""Validate and register the Q83 cultist record/template source captures."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EVIDENCE_PATH = ROOT / "research/EVIDENCE.json"
RECOVERY_PATH = ROOT / "research/RECOVERY.json"
EXP_DIR = ROOT / "experiments/EXP-0132-dragonborn-cultist-gate"
LOCAL_TX = ROOT / ".local/alignment/transactions/TX-20261020-0002"
EXPECTED_GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"

DIRECT = {
    "root_summoner": ROOT / ".local/alignment/xedit-bridge/20261020T012712.381097Z/stdout.raw",
    "root_cultist": ROOT / ".local/alignment/xedit-bridge/20261020T012815.534288Z/stdout.raw",
    "npcs": ROOT / ".local/alignment/xedit-bridge/20261020T012835.409048Z/stdout.raw",
    "leveled_lists": ROOT / ".local/alignment/xedit-bridge/20261020T012850.951267Z/stdout.raw",
}
GOG_STAMPS = [
    "20261020T013551Z",
    "20261020T013647Z",
    "20261020T013803Z",
    "20261020T013943Z",
    "20261020T014050Z",
    "20261020T014203Z",
]
ADDRESS_FILES = {
    "TESActorBaseData_vtable_index0": ROOT / ".local/ghidra/address-library-vtable-tesactorbasedata-20261020.stdout.raw",
    "TESNPC_vtable_index0": ROOT / ".local/ghidra/address-library-vtable-tesnpc-index0-20261020.stdout.raw",
    "TESNPC_vtable_index1": ROOT / ".local/ghidra/address-library-vtable-tesnpc-index1-20261020.stdout.raw",
}
UESP_FILES = {
    "cultist": ROOT / ".local/uesp/q83/cultist.raw.json",
    "dragonborn_quest": ROOT / ".local/uesp/q83/dragonborn-quest.raw.json",
    "way_of_the_voice": ROOT / ".local/uesp/q83/way-of-the-voice.raw.json",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_lines(path: Path):
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def find_record(path: Path, form_id: str, signature: str) -> dict:
    matches = [row for row in json_lines(path)
               if row.get("file_form_id") == form_id and row.get("signature") == signature]
    if len(matches) != 1:
        raise SystemExit(f"expected one {signature} {form_id} in {path}, found {len(matches)}")
    return matches[0]


def subrecords(record: dict, signature: str) -> list[bytes]:
    return [bytes.fromhex(row["hex"]) for row in record.get("subrecords", [])
            if row.get("signature") == signature]


def one_subrecord(record: dict, signature: str) -> bytes:
    values = subrecords(record, signature)
    if len(values) != 1:
        raise SystemExit(f"expected one {signature} in {record.get('file_form_id')}, found {len(values)}")
    return values[0]


def parse_lvln(record: dict) -> dict:
    lvlf = one_subrecord(record, "LVLF")
    entries = []
    for raw in subrecords(record, "LVLO"):
        if len(raw) < 12:
            raise SystemExit(f"short LVLO in {record.get('file_form_id')}")
        level = struct.unpack_from("<H", raw, 0)[0]
        form_id = struct.unpack_from("<I", raw, 4)[0]
        count = struct.unpack_from("<I", raw, 8)[0]
        entries.append({"level": level, "form_id": f"{form_id:08X}", "count": count})
    return {
        "form_id": record["file_form_id"],
        "editor_id": record.get("editor_id"),
        "lvlf_raw": lvlf.hex(),
        "lvlf": int.from_bytes(lvlf, "little"),
        "entries": entries,
    }


def parse_npc(record: dict) -> dict:
    acbs = one_subrecord(record, "ACBS")
    if len(acbs) < 20:
        raise SystemExit(f"short ACBS in {record.get('file_form_id')}")
    flags = struct.unpack_from("<I", acbs, 0)[0]
    level = struct.unpack_from("<H", acbs, 8)[0]
    min_level = struct.unpack_from("<H", acbs, 10)[0]
    max_level = struct.unpack_from("<H", acbs, 12)[0]
    template_use_flags = struct.unpack_from("<H", acbs, 18)[0]
    tplt_rows = subrecords(record, "TPLT")
    tplt = None if not tplt_rows else f"{int.from_bytes(tplt_rows[0], 'little'):08X}"
    if len(tplt_rows) > 1:
        raise SystemExit(f"multiple TPLT rows in {record.get('file_form_id')}")
    return {
        "form_id": record["file_form_id"],
        "editor_id": record.get("editor_id"),
        "acbs_raw": acbs.hex(),
        "actor_base_flags": f"0x{flags:08X}",
        "pc_level_mult": bool(flags & 0x80),
        "uses_template": bool(flags & 0x100),
        "actor_level": level,
        "calc_min_level": min_level,
        "calc_max_level": max_level,
        "template_use_flags": f"0x{template_use_flags:04X}",
        "tplt": tplt,
    }


def verify_raw_inputs() -> None:
    for path in [*DIRECT.values(), *UESP_FILES.values(), *ADDRESS_FILES.values()]:
        if not path.is_file():
            raise SystemExit(f"required local capture missing: {path}")
    for stamp in GOG_STAMPS:
        raw = ROOT / f".local/ghidra/gog-query-{stamp}.stdout.raw"
        meta_path = ROOT / f".local/ghidra/gog-query-{stamp}.meta.json"
        if not raw.is_file() or not meta_path.is_file():
            raise SystemExit(f"missing GOG output/metadata for {stamp}")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if (not str(meta.get("analysis_binary_product_version", "")).startswith("1.6.1179") or
                meta.get("analysis_binary_sha256") != EXPECTED_GOG_SHA or
                meta.get("program_executable_path_matches_gog_binary") is not True or
                meta.get("read_only") is not True or
                meta.get("auto_analysis_disabled") is not True or
                meta.get("ok") is not True or
                meta.get("stdout_sha256") != digest(raw)):
            raise SystemExit(f"GOG identity/read-only/hash check failed for {stamp}")
    expected_addresses = {
        "TESActorBaseData_vtable_index0": "0x17806D8",
        "TESNPC_vtable_index0": "0x17E6020",
        "TESNPC_vtable_index1": "0x17E62E0",
    }
    for key, path in ADDRESS_FILES.items():
        row = json.loads(path.read_text(encoding="utf-8"))
        if (row.get("ok") is not True or row.get("analysis_binary_sha256") != EXPECTED_GOG_SHA or
                row.get("address_library_internal_version") != "1.6.1179.0" or
                row.get("address_library_rva") != expected_addresses[key]):
            raise SystemExit(f"GOG Address Library identity check failed for {key}")


def build_record_summary() -> dict:
    npc_file = DIRECT["npcs"]
    lvln_file = DIRECT["leveled_lists"]
    npc_count = sum(1 for _ in json_lines(npc_file))
    lvln_count = sum(1 for _ in json_lines(lvln_file))
    if npc_count != 713 or lvln_count != 60:
        raise SystemExit(f"unexpected census sizes: NPC_={npc_count}, LVLN={lvln_count}")
    records = {
        "0203564D": find_record(DIRECT["root_summoner"], "0203564D", "LVLN"),
        "02030CDC": find_record(DIRECT["root_cultist"], "02030CDC", "LVLN"),
        "020365F5": find_record(lvln_file, "020365F5", "LVLN"),
        "02030CD7": find_record(lvln_file, "02030CD7", "LVLN"),
    }
    lists = {key: parse_lvln(value) for key, value in records.items()}
    expected_entries = {
        "0203564D": [(1, "020365F5"), (19, "0203564E"), (27, "0203564F"), (36, "02035657"), (46, "02035658")],
        "02030CDC": [(1, "02030CD7"), (18, "02030CD8"), (19, "02030CD8"), (27, "02030CD9"), (36, "02030CDA"), (46, "02030CDB")],
        "020365F5": [(1, "020365F4"), (1, "020365F3")],
        "02030CD7": [(1, "02034FBA"), (1, "02034FBB"), (1, "02034FB9")],
    }
    for form_id, expected in expected_entries.items():
        actual = [(row["level"], row["form_id"]) for row in lists[form_id]["entries"]]
        if actual != expected:
            raise SystemExit(f"unexpected LVLO chain for {form_id}: {actual}")
    for form_id in ("0203564D", "02030CDC", "020365F5", "02030CD7"):
        if lists[form_id]["lvlf"] != 3:
            raise SystemExit(f"unexpected LVLF for {form_id}: {lists[form_id]['lvlf_raw']}")

    npc_ids = [
        "020365F6", "0203564C", "02035475", "0201CE00",
        "020365F4", "020365F3", "02034FBA", "02034FBB", "02034FB9",
    ]
    npcs = {form_id: parse_npc(find_record(npc_file, form_id, "NPC_")) for form_id in npc_ids}
    expected_tplt = {
        "020365F6": "0203564C", "0203564C": "0203564D",
        "02035475": "0201CE00", "0201CE00": "02030CDC",
        "02034FBA": "02030CD1", "02034FBB": "02030CD1", "02034FB9": "02030CD1",
    }
    for form_id, target in expected_tplt.items():
        if npcs[form_id]["tplt"] != target:
            raise SystemExit(f"unexpected TPLT for {form_id}: {npcs[form_id]['tplt']}")
    for form_id in ("020365F6", "0203564C", "02035475", "0201CE00"):
        row = npcs[form_id]
        if (row["actor_base_flags"] != "0x00000000" or row["pc_level_mult"] or
                row["uses_template"] or row["actor_level"] != 1):
            raise SystemExit(f"unexpected alias/template ACBS for {form_id}: {row}")
    for form_id in ("02034FBA", "02034FBB", "02034FB9"):
        if npcs[form_id]["actor_level"] != 12:
            raise SystemExit(f"unexpected level-one leaf actor level for {form_id}")

    capture_hashes = {key: digest(path) for key, path in DIRECT.items()}
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "Dragonborn.esm direct TES4 parser output; configured Steam Data tree; no xEdit winner/profile resolution.",
        "scope": {
            "npc_record_census": npc_count,
            "leveled_npc_record_census": lvln_count,
            "winner_resolution": False,
            "source_file_plugin": "Dragonborn.esm",
            "related_identity_evidence": ["EV-0109", "EV-0654", "EV-0664"],
        },
        "captures": {
            key: {"artifact": f"private-local:{path.relative_to(ROOT).as_posix()}", "sha256": capture_hashes[key]}
            for key, path in DIRECT.items()
        },
        "leveled_lists": lists,
        "npc_templates": npcs,
        "interpretation_limit": "The captures establish serialized LVLN/TPLT/ACBS links only. They do not prove runtime resolution, the actor base filled into either CLOC alias, Steam code equivalence, a profile winner, or natural level-one initiation.",
    }


def build_uesp_manifest() -> dict:
    expected = {
        "cultist": (3586604, "Skyrim:Cultist"),
        "dragonborn_quest": (3632370, "Skyrim:Dragonborn (quest)"),
        "way_of_the_voice": (3587321, "Skyrim:The Way of the Voice"),
    }
    pages = {}
    for key, path in UESP_FILES.items():
        page = json.loads(path.read_text(encoding="utf-8"))
        revision, title = expected[key]
        if page.get("revision_id") != revision or page.get("title") != title:
            raise SystemExit(f"unexpected UESP page identity for {key}")
        pages[key] = {
            "title": title,
            "revision_id": revision,
            "timestamp": page.get("timestamp"),
            "url": page.get("url"),
            "artifact": f"private-local:{path.relative_to(ROOT).as_posix()}",
            "sha256": digest(path),
        }
    return {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pages": pages,
        "assessment": "Secondary-source grounding only: the cultist pair follows The Way of the Voice, while the level-25 note concerns random encounters; the records and engine evidence remain primary for the mechanism.",
    }


def build_schema_note() -> dict:
    return {
        "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": [
            {
                "url": "https://github.com/TES5Edit/TES5Edit/blob/dev-4.1.6/Core/wbDefinitionsTES5.pas",
                "region": "LVLN at source lines 7743-7759; NPC_ ACBS/TPLT at 8009-8073",
                "definitions": "LVLN is Leveled NPC; LVLF bit 0x01 is Calculate from all levels <= player's level; bit 0x02 is Calculate for each item in count; LVLN entries accept [LVLN,NPC_]. NPC_ ACBS labels 0x80 PC Level Mult and 0x100 Use Template?; TPLT accepts [LVLN,NPC_].",
            },
            {
                "url": "https://github.com/TES5Edit/TES5Edit/blob/dev-4.1.6/Core/wbDefinitionsCommon.pas",
                "region": "wbLeveledListEntry at source lines 8499-8520",
                "definitions": "LVLO stores Level as uint16, two unused bytes, the object FormID, and Count.",
            },
            {
                "url": "https://ng.commonlib.dev/_t_e_s_actor_base_data_8h_source.html",
                "region": "ACTOR_BASE_DATA flags/fields, TESActorBaseData virtual slot, and TESNPC override",
                "definitions": "Generated public headers label kPCLevelMult=1<<7, kUsesTemplate=1<<8, actorData at TESActorBaseData+0x08, baseTemplateForm at +0x30, templateUseFlags at actorData+0x12, and CopyFromTemplateForms virtual slot 0x04 with a TESNPC override.",
            },
        ],
        "interpretation": "The source pages label record fields and object layout; the GOG binary capture independently supplies build-specific code behavior. These mutable/generated references are not Steam executable evidence and do not prove the exact CLOC alias runtime selection.",
    }


def gog_bundle() -> dict:
    metas = []
    local_hashes = {}
    for stamp in GOG_STAMPS:
        raw = ROOT / f".local/ghidra/gog-query-{stamp}.stdout.raw"
        meta_path = ROOT / f".local/ghidra/gog-query-{stamp}.meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        metas.append(meta)
        local_hashes[f"{stamp}_stdout"] = digest(raw)
        local_hashes[f"{stamp}_metadata"] = digest(meta_path)
        local_hashes[f"{stamp}_adapter"] = meta["adapter_sha256"]
        local_hashes[f"{stamp}_query_script"] = meta["query_script_sha256"]
    for key, path in ADDRESS_FILES.items():
        local_hashes[key] = digest(path)
    primary = ROOT / ".local/ghidra/gog-query-20261020T013803Z.stdout.raw"
    commands = [
        "python3 scripts/python_env.py run tools/address_library_probe.py --symbol 'VTABLE::TESActorBaseData'",
        "python3 scripts/python_env.py run tools/address_library_probe.py --symbol 'VTABLE::TESNPC' --vtable-index 1",
        "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x17806D8 --vtable-slot 4 --timeout 600",
        "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x17E6020 --vtable-slot 4 --timeout 600",
        "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x17E62E0 --vtable-slot 4 --timeout 600",
        "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x1D7260 --list-call-edges --follow-incoming-calls 8 --timeout 600",
        "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x3BF2D0 --list-call-edges --follow-incoming-calls 8 --timeout 600",
        "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x1D7290 --list-call-edges --follow-incoming-calls 8 --timeout 600",
    ]
    return {
        "id": "EV-0678",
        "captured_utc": "2026-10-20T01:42:51+00:00",
        "kind": "tool",
        "source": "Build-identified read-only GOG Ghidra and matching GOG Address Library; all queries used the existing project with auto-analysis disabled.",
        "artifact": f"private-local:{primary.relative_to(ROOT).as_posix()}",
        "sha256": digest(primary),
        "edition": "AE",
        "runtime": f"GOG SkyrimSE.exe 1.6.1179.0, SHA-256 {EXPECTED_GOG_SHA}; separate from installed Steam 1.6.1170.0; no RVA transfer.",
        "modified_state": False,
        "lane": "offline",
        "tools": commands + ["experiments/EXP-0132-dragonborn-cultist-gate/register_q83_evidence.py"],
        "coverage": "Address Library resolves TESActorBaseData vtable RVA 0x17806D8 and TESNPC vtable entries 0x17E6020/0x17E62E0. RTTI identifies the TESNPC index-1 table as subobject offset 0x30; its slot 4 resolves FUN_1403baeb0, matching the TESActorBaseData CopyFromTemplateForms virtual slot and TESNPC override. The bounded body reads the base-template pointer, checks per-field template-use bits, and branches on ACBS flag bit 0x100. FUN_1401d7290 reads the base-template pointer; FUN_1401d7260 tests the word mask; FUN_1403bf2d0 can set the bit and create cached template-chain state. Base-slot and primary-table probes are retained to disambiguate the override. All six metadata captures verify GOG identity, read-only mode, disabled auto-analysis, and stdout hash.",
        "result": "PASS for the bounded GOG template-copy mechanism. It shows general TESNPC template-data handling, not that the CLOC alias records resolve these LVLN lists at runtime, which NPC base is filled into an alias, Steam 1.6.1170.0 equivalence, or a natural level-one event.",
        "local_hashes": local_hashes,
        "related_evidence": ["EV-0654", "EV-0656", "EV-0660", "EV-0677", "EV-0680", "EV-0260"],
    }


def main() -> None:
    recovery = json.loads(RECOVERY_PATH.read_text(encoding="utf-8"))
    if (recovery.get("status") != "running" or
            recovery.get("transaction_id") != "TX-20261020-0002" or
            recovery.get("frontier_id") != "Q-0083"):
        raise SystemExit("Q83 is not the active transaction; refusing evidence registration")
    verify_raw_inputs()
    LOCAL_TX.mkdir(parents=True, exist_ok=True)

    record_summary = build_record_summary()
    record_path = LOCAL_TX / "q83-cultist-actor-chain-summary.json"
    record_path.write_text(json.dumps(record_summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    uesp_manifest = build_uesp_manifest()
    uesp_path = LOCAL_TX / "q83-uesp-cultist-page-manifest.json"
    uesp_path.write_text(json.dumps(uesp_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    schema_note = build_schema_note()
    schema_path = LOCAL_TX / "q83-template-schema-note.json"
    schema_path.write_text(json.dumps(schema_note, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    direct_hashes = {key: digest(path) for key, path in DIRECT.items()}
    address_hashes = {key: digest(path) for key, path in ADDRESS_FILES.items()}
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    existing_ids = {row["id"] for row in evidence["items"]}
    new_ids = {"EV-0677", "EV-0678", "EV-0679", "EV-0680"}
    if existing_ids & new_ids:
        raise SystemExit("Q83 evidence IDs already exist; refusing duplicate registration")
    if max(int(row["id"].split("-")[1]) for row in evidence["items"]) != 676:
        raise SystemExit("evidence ledger no longer ends at EV-0676; reselect IDs")

    common = {
        "edition": "AE",
        "modified_state": False,
        "lane": "offline",
    }
    entries = [
        {
            **common,
            "id": "EV-0677",
            "captured_utc": "2026-10-20T01:28:50+00:00",
            "kind": "record",
            "source": "Configured Steam AE Dragonborn.esm records parsed directly with the retained read-only TES4 parser; no xEdit winner resolution.",
            "artifact": f"private-local:{record_path.relative_to(ROOT).as_posix()}",
            "sha256": digest(record_path),
            "runtime": "Configured Steam Skyrim AE Data tree associated with verified SkyrimSE.exe 1.6.1170.0 [EV-0109]; profile/load order and winning records are not resolved.",
            "tools": [
                "python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature LVLN --plugin Dragonborn.esm --form-id 03564D",
                "python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature LVLN --plugin Dragonborn.esm --form-id 030CDC",
                "python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature NPC_ --plugin Dragonborn.esm",
                "python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature LVLN --plugin Dragonborn.esm",
                "experiments/EXP-0132-dragonborn-cultist-gate/register_q83_evidence.py",
            ],
            "coverage": "The direct parser captures contain 713 Dragonborn.esm NPC_ records and 60 LVLN records plus exact root-list queries. The selected graph covers both DLC2CultistAmbush aliases, their intermediate NPC_ TPLT records, root LVLN records, level-1 nested LVLNs, and the selected leaf NPC records. Raw LVLO and ACBS bytes are retained and decoded in the private summary. No profile winner, runtime actor fill, or Steam gameplay trace is included.",
            "result": "PASS for serialized record linkage: the CLOC alias NPCs point through DLC2LvlCultist* records to LVLN roots with thresholds 1–46 and LVLF 0x03. The alias/intermediate NPC ACBS actor flags are zero, leaving PCLevelMult and UsesTemplate clear, while TPLT and template-use mask fields are present. The record chain is a level-variant candidate, not proof of runtime resolution.",
            "local_hashes": direct_hashes,
            "related_evidence": ["EV-0654", "EV-0656", "EV-0660", "EV-0663", "EV-0260"],
        },
        gog_bundle(),
        {
            **common,
            "id": "EV-0679",
            "captured_utc": "2026-10-20T01:28:50+00:00",
            "kind": "wiki",
            "source": "Revision-cited local UESP copies for Skyrim:Cultist, Skyrim:Dragonborn (quest), and Skyrim:The Way of the Voice.",
            "artifact": f"private-local:{uesp_path.relative_to(ROOT).as_posix()}",
            "sha256": digest(uesp_path),
            "runtime": "Secondary reference pages only; no executable, installed plugin, or gameplay observation.",
            "tools": ["python3 scripts/python_env.py run -m tools.uesp page --db .local/uesp.sqlite3 <title> --raw", "experiments/EXP-0132-dragonborn-cultist-gate/register_q83_evidence.py"],
            "coverage": "Three local pages are revision-pinned and each source raw JSON SHA-256 is recorded in the private manifest: Cultist rev 3586604, Dragonborn quest rev 3632370, and The Way of the Voice rev 3587321. The pages distinguish the pair sent after the main-quest milestone from level-25 random Skyrim encounters; they are used as grounding only.",
            "result": "PASS as secondary-source grounding. The wiki statements do not establish a native predicate, runtime timing, a CLOC alias actor base, or a level-one reproduction.",
            "local_hashes": {key: digest(path) for key, path in UESP_FILES.items()},
            "related_evidence": ["EV-0653", "EV-0654", "EV-0656", "EV-0677", "EV-0260"],
        },
        {
            **common,
            "id": "EV-0680",
            "captured_utc": schema_note["retrieved_utc"],
            "kind": "source",
            "source": "TES5Edit dev-4.1.6 source definitions and generated CommonLibSSE-NG public header documentation; mutable references, CommonLib commit unavailable.",
            "artifact": f"private-local:{schema_path.relative_to(ROOT).as_posix()}",
            "sha256": digest(schema_path),
            "runtime": "External format/layout reference only; not an installed plugin winner or target executable.",
            "tools": ["web retrieval on 2026-10-20", "experiments/EXP-0132-dragonborn-cultist-gate/register_q83_evidence.py"],
            "coverage": "TES5Edit source defines LVLN flag meanings, LVLO fields, NPC_ ACBS bit labels, and the TPLT union; CommonLib header labels the corresponding actor-data flags/layout and CopyFromTemplateForms virtual slot. The exact GOG executable body is independently captured in EV-0678. CommonLib generated docs are mutable and have no captured repository commit.",
            "result": "PASS as record-schema and class-layout context. These references label bytes and virtual-slot roles; they do not independently prove runtime semantics, list selection, or Steam/GOG equivalence.",
            "local_hashes": address_hashes,
            "related_evidence": ["EV-0677", "EV-0678", "EV-0654", "EV-0656"],
        },
    ]
    evidence["items"].extend(entries)
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": [row["id"] for row in entries],
                      "record_summary_sha256": digest(record_path),
                      "uesp_manifest_sha256": digest(uesp_path),
                      "schema_note_sha256": digest(schema_path)}, indent=2))


if __name__ == "__main__":
    main()
