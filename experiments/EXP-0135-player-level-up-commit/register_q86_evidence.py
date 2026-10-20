#!/usr/bin/env python3
"""Validate and register Q86's revision-pinned UESP and GOG source captures."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TX = "TX-20261020-0005"
LOCAL = ROOT / ".local/uesp/q86"
GHIDRA = ROOT / ".local/ghidra"
EVIDENCE_PATH = ROOT / "research/EVIDENCE.json"
RECOVERY_PATH = ROOT / "research/RECOVERY.json"
COMMONLIB_CAPTURE = LOCAL / "commonlib-level-api.stdout.raw"
UESP_CAPTURE = LOCAL / "leveling.raw.json"
ADDRESS_CAPTURES = {
    "actor_getlevel": LOCAL / "address-actor-getlevel.json",
    "base_data_getlevel": LOCAL / "address-tesactorbasedata-getlevel.json",
    "levelup_menu_vtable": LOCAL / "address-levelup-menu-vtable.json",
    "levelup_callback_vtable": LOCAL / "address-levelup-callback-vtable.json",
}
GHIDRA_CAPTURES = {
    "actor_getlevel_thunk": ("20261020T032733Z", "0x668F30"),
    "base_data_getlevel_body": ("20261020T033105Z", "0x1D7B20"),
    "levelup_rtti": ("20261020T033402Z", None),
    "levelup_menu_vtable": ("20261020T033507Z", None),
    "levelup_callback_vtable": ("20261020T033610Z", None),
    "levelup_attribute_callback": ("20261020T033709Z", "0x936740"),
    "skill_progress_threshold": ("20261020T033913Z", "0x77D090"),
    "skill_level_event_wrapper": ("20261020T034020Z", "0x72A650"),
    "skill_level_event_dispatch": ("20261020T034134Z", "0x72ACC0"),
    "skill_level_event_source": ("20261020T034749Z", "0x72AFF0"),
    "skill_event_listener_registration": ("20261020T034903Z", "0x72A5F0"),
    "skill_event_listener_object": ("20261020T035056Z", None),
    "skill_event_listener_rtti": ("20261020T035153Z", None),
    "skill_event_listener_vtable": ("20261020T035254Z", None),
    "skill_event_listener_callback": ("20261020T035353Z", "0x65CD60"),
    "levelup_menu_accept": ("20261020T034535Z", "0x936510"),
    "levelup_apply_helper": ("20261020T035505Z", "0x77D700"),
    "levelup_profile_interface": ("20261020T035624Z", "0xCDBEE0"),
    "broad_offset40_scan": ("20261020T034248Z", None),
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def main() -> None:
    recovery = read_json(RECOVERY_PATH)
    if (recovery.get("status"), recovery.get("transaction_id"), recovery.get("frontier_id")) != (
        "running", TX, "Q-0086"
    ):
        raise SystemExit("Q86 is not active; refusing evidence registration")

    page = read_json(UESP_CAPTURE)
    if (page.get("title"), page.get("revision_id")) != ("Skyrim:Leveling", 3636185):
        raise SystemExit("unexpected UESP page identity")
    if not str(page.get("url", "")).endswith("oldid=3636185"):
        raise SystemExit("UESP capture is not revision pinned")
    content = str(page.get("content", ""))
    required_phrases = ("eligible to level up", "When you accept the new level", "highest level")
    if not all(phrase.casefold() in content.casefold() for phrase in required_phrases):
        raise SystemExit("UESP page lacks the expected pending/acceptance statements")
    if not COMMONLIB_CAPTURE.is_file():
        raise SystemExit("CommonLib source capture is missing")
    commonlib_text = COMMONLIB_CAPTURE.read_text(encoding="utf-8")
    if ("b93280e832f263dbef44e44cbe2936622a02f91a" not in commonlib_text or
            "level;             // 08" not in commonlib_text or
            "RELOCATION_ID(14262, 14384)" not in commonlib_text or
            "AddSkillExperience" not in commonlib_text):
        raise SystemExit("CommonLib capture lacks the expected declarations or revision")

    for name, path in ADDRESS_CAPTURES.items():
        data = read_json(path)
        if not data.get("ok", data.get("read_only") is True) and not data.get("read_only"):
            raise SystemExit(f"Address Library capture failed: {name}")
        if data.get("read_only") is not True or data.get("analysis_binary_product_version") != "1.6.1179.0":
            raise SystemExit(f"Address Library identity/read-only gate failed: {name}")
    if read_json(ADDRESS_CAPTURES["actor_getlevel"]).get("address_library_rva") != "0x668F30":
        raise SystemExit("Actor::GetLevel mapping changed")
    if read_json(ADDRESS_CAPTURES["base_data_getlevel"]).get("address_library_rva") != "0x1D7B20":
        raise SystemExit("TESActorBaseData::GetLevel mapping changed")
    for name, path in ADDRESS_CAPTURES.items():
        if not read_json(path).get("ok", True):
            raise SystemExit(f"Address Library capture reported failure: {name}")

    query_manifest: dict[str, dict] = {}
    local_hashes: dict[str, str] = {
        "uesp-leveling.raw.json": sha(UESP_CAPTURE),
        "commonlib-level-api.stdout.raw": sha(COMMONLIB_CAPTURE),
    }
    for name, path in ADDRESS_CAPTURES.items():
        local_hashes[path.name] = sha(path)
    for name, (stamp, expected_rva) in GHIDRA_CAPTURES.items():
        stdout = GHIDRA / f"gog-query-{stamp}.stdout.raw"
        metadata_path = GHIDRA / f"gog-query-{stamp}.meta.json"
        metadata = read_json(metadata_path)
        if not stdout.is_file() or metadata.get("ok") is not True or metadata.get("read_only") is not True:
            raise SystemExit(f"Ghidra query missing or failed: {name}")
        if metadata.get("analysis_binary_product_version") != "1.6.1179" or metadata.get("analysis_binary_sha256") != "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f":
            raise SystemExit(f"Ghidra build identity mismatch: {name}")
        if metadata.get("stdout_sha256") != sha(stdout):
            raise SystemExit(f"Ghidra stdout hash mismatch: {name}")
        if expected_rva and str(metadata.get("requested_rva", "")).lower() != expected_rva.lower():
            raise SystemExit(f"Ghidra requested RVA mismatch: {name}")
        query_manifest[name] = {
            "metadata_artifact": f"private-local:{metadata_path.relative_to(ROOT).as_posix()}",
            "metadata_sha256": sha(metadata_path),
            "stdout_artifact": f"private-local:{stdout.relative_to(ROOT).as_posix()}",
            "stdout_sha256": sha(stdout),
            "requested_rva": metadata.get("requested_rva"),
            "query_mode": metadata.get("query_mode"),
            "checks": metadata.get("checks"),
        }
        local_hashes[f"{stamp}.meta.json"] = sha(metadata_path)
        local_hashes[f"{stamp}.stdout.raw"] = sha(stdout)

    captured = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary = {
        "captured_utc": captured,
        "transaction": TX,
        "target_separation": {
            "runtime_target": "Steam SkyrimSE.exe 1.6.1170.0 [EV-0109]",
            "analysis_target": "GOG SkyrimSE.exe 1.6.1179.0; executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f",
            "address_library_sha256": "3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e",
            "rvas_transferred": False,
        },
        "commonlib": {
            "revision": "b93280e832f263dbef44e44cbe2936622a02f91a",
            "capture_artifact": f"private-local:{COMMONLIB_CAPTURE.relative_to(ROOT).as_posix()}",
            "capture_sha256": sha(COMMONLIB_CAPTURE),
            "header_hashes_and_source_lines": "The capture records relative header names and file hashes. TESActorBaseData::GetLevel uses AE ID 14384; ACTOR_BASE_DATA.level is at offset 0x08 within actorData; LevelUpMenu registers attribute callbacks; PlayerCharacter::AddSkillExperience and Actor::UseSkill declarations are retained.",
        },
        "uesp": {
            "title": page["title"], "revision_id": page["revision_id"],
            "timestamp": page["timestamp"], "url": page["url"],
            "artifact": f"private-local:{UESP_CAPTURE.relative_to(ROOT).as_posix()}",
            "sha256": sha(UESP_CAPTURE),
            "corpus_limit": "Local corpus acquisition/completeness/license provenance is unverified; secondary grounding only.",
        },
        "address_library": {
            name: read_json(path) for name, path in ADDRESS_CAPTURES.items()
        },
        "ghidra_queries": query_manifest,
        "bounded_findings": [
            "Actor::GetLevel thunk at GOG RVA 0x668F30 forwards to CommonLib TESActorBaseData::GetLevel AE ID 14384 at fresh Address Library RVA 0x1D7B20. The helper reads the 16-bit actor-data level field; the PCLevelMult branch applies a multiplier and min/max clamps when the NPC flag is set.",
            "PlayerCharacter UseSkill vtable slot 0xF7 reaches skill progress RVA 0x77D090. On skill-level threshold the function advances skill actor values, accumulates separate character-level XP, and dispatches the skill-level event source.",
            "The single statically identified skill-event registration is SkillIncreaseToMiscStatHandler. Its callback reads the skill AV and updates a misc statistic; no direct level-field write appears in that resolved body.",
            "RTTI identifies LevelUpMenu and ConfirmLevelUpAttributeCallback. LevelUpMenu Accept registers addHealth/addMagicka/addStamina and sound callbacks. The attribute callback calls helper RVA 0x77D700; that helper applies attribute/threshold updates and reads GetLevel for display/profile processing, with no direct base-level store in the captured body.",
            "The exact Player base-data level writer and the threshold-versus-acceptance timing remain unresolved. No designated disposable Steam save/profile/order/Observer is configured [EV-0260].",
        ],
        "scan_limits": {
            "displacement_0x40_scan": "Completed 5,654,579 instruction scan; 28,807 matching object accesses; 3,136 writer-candidate functions. Adapter capped decompilation at first 16 writer functions. It is an exploratory breadth result and does not rule out or identify the Player level writer.",
            "failed_address_query": "The attempted function-boundary query for static callback address RVA 0x936670 found no existing function; it is not treated as behavioral evidence.",
        },
        "raw_hashes": local_hashes,
    }
    transaction_dir = ROOT / ".local/alignment/transactions" / TX
    transaction_dir.mkdir(parents=True, exist_ok=True)
    summary_path = transaction_dir / "q86-source-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    evidence = read_json(EVIDENCE_PATH)
    existing = {row["id"] for row in evidence["items"]}
    max_id = max(int(row["id"].split("-")[1]) for row in evidence["items"])
    if existing.intersection({"EV-0688", "EV-0689"}) or max_id != 687:
        raise SystemExit("evidence IDs moved or Q86 evidence already exists; reselect IDs")
    items = [
        {
            "id": "EV-0688", "captured_utc": captured, "kind": "wiki",
            "source": "Local revision-pinned UESP page Skyrim:Leveling rev 3636185; raw page response captured from the configured local corpus.",
            "artifact": f"private-local:{UESP_CAPTURE.relative_to(ROOT).as_posix()}", "sha256": sha(UESP_CAPTURE), "edition": "AE",
            "runtime": "Secondary-source page only; no executable, plugin winner, save, or gameplay observation.",
            "modified_state": False, "lane": "offline",
            "tools": [
                "python3 scripts/python_env.py run -m tools.uesp page --db .local/uesp.sqlite3 'Skyrim:Leveling' --raw",
                "python3 scripts/python_env.py run experiments/EXP-0135-player-level-up-commit/inspect_uesp_leveling.py",
                "python3 scripts/python_env.py run experiments/EXP-0135-player-level-up-commit/register_q86_evidence.py",
            ],
            "coverage": f"The raw response retains title, revision ID, timestamp, oldid URL, and content; capture SHA-256 {sha(UESP_CAPTURE)}. The corpus doctor did not verify dump acquisition/completeness/license provenance. The page describes skill level-ups contributing character XP, pending notification, and acceptance updating the highest level earned; it does not identify native GetLevel storage or prove the Steam timing behavior.",
            "result": "PASS as secondary grounding for a distinction between earned/pending level-ups and accepted levels. This page alone does not establish which value GetLevel reads at threshold or acceptance, nor a level-one quest bypass.",
            "local_hashes": {"leveling.raw.json": sha(UESP_CAPTURE)},
            "related_evidence": ["EV-0109", "EV-0260"],
        },
        {
            "id": "EV-0689", "captured_utc": captured, "kind": "native",
            "source": "Read-only existing GOG Skyrim AE 1.6.1179.0 Ghidra project and matching Address Library, correlated with CommonLibSSE-NG source revision b93280e832f263dbef44e44cbe2936622a02f91a.",
            "artifact": f"private-local:{summary_path.relative_to(ROOT).as_posix()}", "sha256": sha(summary_path), "edition": "AE",
            "runtime": "GOG analysis build only: ProductVersion 1.6.1179.0, executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f, Address Library SHA-256 3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e. Steam 1.6.1170.0 is separate [EV-0109]; no RVA transfer.",
            "modified_state": False, "lane": "mechanism_inference",
            "tools": [
                "python3 scripts/python_env.py run tools/address_library_probe.py --symbol 'Actor::GetLevel'",
                "python3 scripts/python_env.py run experiments/EXP-0135-player-level-up-commit/resolve_inline_relocation.py",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --rva <RVA> --list-call-edges --follow-incoming-calls 8 --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --vtable-rtti-rvas <RVA,...> --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --pointer-table-rva <RVA> --pointer-count <N> --timeout 600",
                "python3 scripts/python_env.py run tools/ghidra_probe.py --search-displacement 0x40 --timeout 600",
                "CommonLibSSE-NG source capture and strict Python dispatcher",
                "python3 scripts/python_env.py run experiments/EXP-0135-player-level-up-commit/register_q86_evidence.py",
            ],
            "coverage": "All Ghidra captures and metadata in the summary passed executable identity and read-only checks; auto-analysis was disabled. CommonLib and fresh Address Library mappings identify Actor::GetLevel at RVA 0x668F30 and TESActorBaseData::GetLevel AE ID 14384 at RVA 0x1D7B20. The bounded source path maps the level getter, PlayerCharacter skill-progress/threshold helper, skill-level event source/listener, LevelUpMenu/attribute callback, and acceptance helper. Direct stores, field identity, and all indirect callbacks beyond the captured paths are not exhaustively resolved; the exploratory 0x40 scan hit its writer output cap. The Player-level writer and threshold-versus-accept timing remain unknown; live Steam verification is EV-0260.",
            "result": "PASS for the bounded GOG static source map. GetLevel reads a 16-bit actor-data level field, with a flagged PCLevelMult scale/clamp branch. Skill XP and cumulative character-level XP are separate in the resolved progress routine; its statically identified event listener updates a misc statistic. The resolved LevelUpMenu acceptance path applies attribute/threshold updates and reads GetLevel for display/profile processing but contains no direct base-level store. This narrows the models but does not decide whether the Player level field changes at threshold or only on acceptance. It establishes no OBJ-2 armor-XP edge and no vanilla level-one reproduction.",
            "local_hashes": local_hashes,
            "related_evidence": ["EV-0109", "EV-0217", "EV-0221", "EV-0260", "EV-0280"],
        },
    ]
    evidence["items"].extend(items)
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": [row["id"] for row in items], "summary": f"private-local:{summary_path.relative_to(ROOT).as_posix()}", "summary_sha256": sha(summary_path)}, indent=2))


if __name__ == "__main__":
    main()
