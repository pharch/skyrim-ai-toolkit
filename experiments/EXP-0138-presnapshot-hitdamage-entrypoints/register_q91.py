#!/usr/bin/env python3
"""Register Q91's bounded five-master selector screen and cross-source result."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TX = "TX-20261020-0010"
CAPTURE = ROOT / ".local/alignment/transactions" / TX / "q91"
EVIDENCE_PATH = ROOT / "research/EVIDENCE.json"
FRONTIER_PATH = ROOT / "research/FRONTIER.json"
BINARY_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
COMMONLIB_COMMIT = "b93280e832f263dbef44e44cbe2936622a02f91a"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def private(path: Path) -> str:
    return "private-local:" + path.relative_to(ROOT).as_posix()


def main() -> int:
    enum_path = CAPTURE / "commonlib-entrypoint-enum.json"
    screen_path = CAPTURE / "presnapshot-perk-screen.json"
    ref_path = CAPTURE / "candidate-perk-references.json"
    summary_path = CAPTURE / "presnapshot-candidate-summary.json"
    xedit_result = ROOT / ".local/xedit-authoritative-copy/out/xedit/20261020T060744.629620Z/native-result.json"
    xedit_tsv = xedit_result.parent / "native-records.tsv"
    uesp_path = CAPTURE / "uesp-light-armor.raw"
    inputs = (enum_path, screen_path, ref_path, summary_path, xedit_result, xedit_tsv, uesp_path)
    for path in inputs:
        if not path.is_file():
            raise SystemExit(f"required Q91 capture is missing: {path}")

    enum = json.loads(enum_path.read_text(encoding="utf-8"))
    screen = json.loads(screen_path.read_text(encoding="utf-8"))
    refs = json.loads(ref_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    xedit = json.loads(xedit_result.read_text(encoding="utf-8"))
    coverage = screen.get("coverage", {})
    if enum.get("source_commit") != COMMONLIB_COMMIT:
        raise SystemExit("unexpected CommonLib source commit")
    if coverage.get("all_PERK_entrypoint_DATA_rows") != 785 or coverage.get("selected_rows_total") != 160:
        raise SystemExit("Q91 five-master selector denominator changed")
    zero_rows = summary.get("all_nonpositive_EPFD_rows", [])
    if len(zero_rows) != 4 or sum(refs.get("matches_by_target", {}).values()) != 11:
        raise SystemExit("Q91 zero-row/reference counts changed")
    deft = next((row for row in zero_rows if row.get("form_id") == "00107831"), None)
    if not deft or deft.get("selector_name") != "kModIncomingDamage" or deft.get("handler_id") != 3 or deft.get("EPFD_float") != 0.0:
        raise SystemExit("Deft Movement candidate differs from expected selector/handler/data")
    if xedit.get("loader_status") != "Background Loader: finished" or xedit.get("record", {}).get("editor_id") != "DeftMovement" or xedit.get("field_count") != 147:
        raise SystemExit("native xEdit Deft Movement result did not validate")
    if len(xedit.get("plugins", [])) != 5 or len(xedit.get("native_data_files", [])) != 5:
        raise SystemExit("native xEdit result was not scoped to exactly five official masters")

    artifacts = {path.relative_to(ROOT).as_posix(): {"sha256": sha(path)} for path in inputs}
    manifest = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "transaction": TX,
        "frontier": "Q-0091",
        "scope": "Read-only CommonLib enum provenance, configured five-official-master source screen, native xEdit DeftMovement fields, and revision-pinned local UESP lead. No profile winner or runtime result.",
        "primary_source": {
            "commonlib_commit": COMMONLIB_COMMIT,
            "enum_source": enum.get("entrypoint_enum_blocks"),
            "enum_capture_sha256": sha(enum_path),
        },
        "record_scope": {
            "plugin_sha256": screen.get("plugin_sha256"),
            "perk_record_count_by_plugin": coverage.get("perk_record_count_by_plugin"),
            "all_entrypoint_data_rows": coverage.get("all_PERK_entrypoint_DATA_rows"),
            "selected_selector_rows": coverage.get("selected_rows_total"),
            "nonpositive_epfd_rows": zero_rows,
            "raw_reference_match_count": refs.get("match_count"),
            "raw_reference_matches_by_target": refs.get("matches_by_target"),
            "raw_reference_limit": refs.get("limit"),
        },
        "native_xedit": {
            "result": xedit_result.relative_to(ROOT).as_posix(),
            "result_sha256": sha(xedit_result),
            "tsv": xedit_tsv.relative_to(ROOT).as_posix(),
            "tsv_sha256": sha(xedit_tsv),
            "record": xedit.get("record"),
            "field_count": xedit.get("field_count"),
            "official_masters": xedit.get("native_data_files"),
            "profile_winner_resolution": False,
        },
        "uesp_secondary_lead": {
            "title": "Skyrim:Light Armor",
            "revision": 3602632,
            "revision_timestamp": "2026-08-03",
            "url": "https://en.uesp.net/w/index.php?title=Skyrim:Light_Armor&oldid=3602632",
            "raw_sha256": sha(uesp_path),
            "database": "uespwiki-2026-10-04-current.xml.bz2",
            "database_sha256": "b3ccaea9d10c653a1bf702d0da5d32c2bc9a5cafdcd374d258f5a063d6074ddb",
            "database_scope": "475228 pages; 17520 Skyrim pages; zero parser errors; completeness unverified.",
        },
        "related_evidence": ["EV-0109", "EV-0221", "EV-0260", "EV-0683", "EV-0699"],
        "artifacts": artifacts,
    }
    manifest_path = CAPTURE / "capture-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    existing = {item.get("id") for item in evidence.get("items", [])}
    if {"EV-0700", "EV-0701", "EV-0702"} & existing:
        raise SystemExit("Q91 evidence ID already exists")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    evidence["items"].extend([
        {
            "id": "EV-0700", "captured_utc": now, "kind": "record",
            "source": "CommonLibSSE EntryPoint enum at the pinned commit plus a read-only direct TES4 screen of all nine pre-snapshot selectors across the five official masters and raw candidate FormID-reference census.",
            "artifact": private(manifest_path), "sha256": sha(manifest_path), "edition": "AE",
            "runtime": "Official five-master source-file scope and CommonLib source commit only. No active profile winners, Creation Club coverage, or live runtime result.",
            "modified_state": False, "lane": "mechanism_inference",
            "tools": ["python3 scripts/python_env.py run experiments/EXP-0138-presnapshot-hitdamage-entrypoints/inspect_commonlib_enum.py", "python3 scripts/python_env.py run experiments/EXP-0138-presnapshot-hitdamage-entrypoints/screen_presnapshot_perk_entries.py", "python3 scripts/python_env.py run experiments/EXP-0138-presnapshot-hitdamage-entrypoints/scan_candidate_perk_references.py"],
            "coverage": "785 official PERK entry-point DATA rows; 160 rows across the nine selectors called before the HitData +0x54 snapshot; four rows have EPFD 0.0. Eleven raw exact FormID occurrences link to those four rows. CommonLib selector labels, parser outputs, five plugin hashes, and scan limitations are preserved in the private manifest.",
            "result": "A bounded official-source screen identifies DeftMovement as the only Player-applicable selector-0x24 zero row among the candidates. Other zero rows are tied to a quest phantom actor, carriage actors/horses, or companion safety content; the outgoing selector-0x23 row is not an incoming armor hit. Raw FormID-byte occurrences are candidate references, not semantic or runtime proof.",
            "related_evidence": ["EV-0109", "EV-0221", "EV-0260", "EV-0683", "EV-0699"],
        },
        {
            "id": "EV-0701", "captured_utc": now, "kind": "record",
            "source": "Accepted native xEdit/SSEView query for Skyrim.esm PERK EditorID DeftMovement in the official five-master data set.",
            "artifact": private(manifest_path), "sha256": sha(manifest_path), "edition": "AE",
            "runtime": "Native xEdit query loaded the five official masters only; exact profile order and any profile-specific winner remain unverified.",
            "modified_state": False, "lane": "mechanism_inference",
            "tools": ["python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature PERK --plugin Skyrim.esm --editor-id DeftMovement"],
            "coverage": "Accepted exact EditorID query, 147 fields exported, official five-master data files, selector-0x24 DATA row and decoded entry/record-level condition fields. Native result and TSV hashes are enumerated in the private manifest.",
            "result": "DeftMovement uses handler ID 3 / Multiply Value with zero float EPFD. Its entry conditions include GetRandomPercent <= 10 and worn Light Armor piece keywords. Record-level conditions include Light Armor 100 and Wind Walker/Matching Set perk checks; no logical grouping or level-one reachability is inferred beyond decoded condition flags.",
            "related_evidence": ["EV-0700", "EV-0699", "EV-0221", "EV-0260"],
        },
        {
            "id": "EV-0702", "captured_utc": now, "kind": "wiki",
            "source": "Revision-pinned local UESP Light Armor article captured from the local XML export; raw text and source database provenance are in the private transaction manifest.",
            "artifact": private(manifest_path), "sha256": sha(manifest_path), "edition": "AE",
            "runtime": "Local UESP export snapshot dated 2026-10-04; page revision 3602632 from 2026-08-03. This is secondary text, not an installed-build or gameplay observation.",
            "modified_state": False, "lane": "offline",
            "tools": ["python3 scripts/python_env.py run -m tools.uesp page --title 'Skyrim:Light Armor' --revision 3602632"],
            "coverage": "The page describes Deft Movement's Light Armor requirement and chance to avoid damage; local database parser reported zero errors but export completeness is unverified.",
            "result": "Secondary grounding only. It does not establish ActiveEffect/perk runtime state, level-one acquisition, armor-provided protection, or armor XP behavior.",
            "related_evidence": ["EV-0700", "EV-0701", "EV-0260"],
        },
    ])
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "CL-L486" in claims or "CL-L487" in claims:
        raise SystemExit("Q91 claim ID collision")
    claims += "\n| CL-L486 | Across the five official masters, the complete screen found 160 PERK rows across the nine pre-snapshot selectors and four zero-EPFD rows; DeftMovement is the only Player-applicable selector-0x24 zero row among those candidates. | supported within the official five-master source screen | [EV-0700], [EV-0701] | No exact profile winner, Creation Club coverage, active effect, or runtime application is established; raw FormID matches are candidate references only. |\n"
    claims += "| CL-L487 | In the captured GOG path, a successful DeftMovement selector-0x24 zero-multiplier application is predicted to make HitData +0x54 non-positive before the Player armor UseSkill guard, so that proc does not pass positive points to the captured skill-progress helper. | conditional cross-source static inference | [EV-0221], [EV-0699], [EV-0701] | This is not a live Steam result; DeftMovement is conditional, does not show armor-provided protection, may avoid all damage, and is not established as level-one reachable or as repeatable all-hit zero XP. |\n"
    claims_path.write_text(claims, encoding="utf-8")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8")
    if "M-0209" in mechanisms:
        raise SystemExit("M-0209 already exists")
    mechanisms += """

## M-0209 — conditional Deft Movement zero before the armor-points snapshot (EV-0221, EV-0699–EV-0701)

In the GOG AE 1.6.1179.0 builder path, selector `0x24` is dispatched against HitData `+0x50` before the current value is copied to `+0x54` [EV-0699]. The official Skyrim.esm DeftMovement PERK row uses selector `0x24`, handler 3 / Multiply Value, and EPFD 0.0; native xEdit decodes a random-percent condition plus worn Light Armor conditions, with record-level Light Armor/perk conditions [EV-0701]. The PlayerCharacter UseSkill wrapper checks that points are strictly greater than zero before the skill-progress helper [EV-0221]. Therefore a successful Deft Movement application is statically predicted to pass zero points to that guard and skip progress for that proc [CL-L487].

This is a conditional cross-source mechanism inference, not a Steam or runtime observation. A zero-damage proc does not demonstrate positive armor-provided protection, and the record does not establish a level-one route or repeated zero XP across qualifying hits. The other official zero rows are tied to non-player actors/content in the bounded raw reference census [EV-0700]. No prize edge to OBJ-2 is added. Claims CL-L486–CL-L487; Q91.
"""
    mechanisms_path.write_text(mechanisms, encoding="utf-8")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    graph = graph_path.read_text(encoding="utf-8")
    graph += """

## Q-0091 synthesis — one conditional player-side zero before the armor points snapshot (EV-0700–EV-0702)

The five-master selector screen found one Player-applicable zero row in the pre-snapshot incoming-damage path: DeftMovement. If its conditions hold, selector `0x24` multiplies HitData `+0x50` by zero before the builder copies that value to `+0x54`; the PlayerCharacter UseSkill wrapper rejects non-positive points [EV-0221], [EV-0699], [EV-0701]. This supports a conditional static edge from DeftMovement entry-point data to the armor points input and then to the positive-points guard.

The route is intermittent and is described as damage avoidance. It does not show a qualifying hit where worn armor supplied positive protection, repeated zero Heavy/Light AVSK, or level-one acquisition. The raw five-master reference scan attaches the other zero rows to non-player actor/content candidates [EV-0700]. No causal edge from this finding to OBJ-1, positive armor protection, or a completed OBJ-2 solution is added. A distinct next question is whether the downstream `Mod Skill Use` route can zero skill credit after a positive hit-points input while remaining separate from the protection calculation. Claims CL-L486–CL-L487 -> M-0209.
"""
    graph_path.write_text(graph, encoding="utf-8")

    frontier = json.loads(FRONTIER_PATH.read_text(encoding="utf-8"))
    items = frontier["items"]
    q91 = next(item for item in items if item.get("id") == "Q-0091")
    q91["question"] = "Can any official pre-snapshot PERK entry point zero incoming HitData before the +0x54 armor-points snapshot, and does a Player-applicable row preserve the level-one, qualifying-hit, and armor-protection requirements?"
    q91["evidence"] = list(dict.fromkeys([*q91.get("evidence", []), "EV-0700", "EV-0701", "EV-0702"]))
    q91["linked_claims"] = ["CL-L486", "CL-L487"]
    q91["hypotheses"] = [
        {"id": "Q-0091-H1", "model": "At least one official selector row can zero the incoming HitData value before the +0x54 copy when its conditions hold.", "predicted_discriminant": "The exact selector call precedes the copy, the complete five-master screen finds a zero-capable row, and the Player positive-points guard follows the snapshot.", "status": "supported", "evidence": ["EV-0221", "EV-0699", "EV-0700", "EV-0701"]},
        {"id": "Q-0091-H2", "model": "No Player-applicable zero row exists among the official pre-snapshot selectors.", "predicted_discriminant": "Complete selector denominator and source-owner/condition review show only non-player zero rows or positive amounts.", "status": "falsified", "evidence": ["EV-0700", "EV-0701"]},
        {"id": "Q-0091-H3", "model": "The DeftMovement zero row alone meets OBJ-2 by keeping functional worn-armor protection while suppressing armor XP on qualifying hits at level one.", "predicted_discriminant": "A natural level-one sequence reproduces qualifying hits with measurable armor protection and unchanged AV11/AV12 progress across repeated trials.", "status": "proposed", "evidence": ["EV-0701", "EV-0702", "EV-0260"]},
    ]
    q91["attempts"].append({
        "action_key": "q91-register-selector-screen-and-deftmovement-path",
        "outcome": "Registered the five-master PERK screen, CommonLib selector mapping, raw-reference census, accepted native xEdit DeftMovement fields, and revision-pinned local UESP lead. One Player-applicable selector-0x24 zero row is statically predicted to make the later +0x54 points input zero on a successful condition check; it is stochastic and does not establish a qualifying protected hit or level-one route.",
        "evidence": ["EV-0700", "EV-0701", "EV-0702"],
        "new_discriminant": "The PlayerCharacter progression helper calls the `Mod Skill Use` selector on the points value after the positive-input guard; identify its exact build-attested dataflow and screen the corresponding official source rows for any zero-capable award-side suppression route.",
        "recorded_utc": now,
    })
    if any(item.get("id") == "Q-0092" for item in items):
        raise SystemExit("Q-0092 already exists")
    items.append({
        "id": "Q-0092", "objective": "OBJ-2", "kind": "mechanism", "status": "open",
        "question": "Can the PlayerCharacter Mod Skill Use path or a skill-use ActorValue suppress AV11/AV12 credit after a positive HitData points input, independently of physical armor protection, through an official player-applicable source?",
        "hypotheses": [
            {"id": "Q-0092-H1", "model": "The PlayerCharacter progression helper applies a selector-0x16/Mod Skill Use transformation to positive hit points before AVSK progress is committed, and an official player-applicable record can reduce the result to zero.", "predicted_discriminant": "Identity-checked GOG dataflow shows selector 0x16 operates on the credit float before progress addition, while a complete official PERK/MGEF/AVIF screen finds a zero-capable AV11/AV12 source.", "status": "proposed", "evidence": ["EV-0221", "EV-0262"]},
            {"id": "Q-0092-H2", "model": "The captured helper applies only positive or nonzero scaling, and the official five-master skill-use record sources have no player-applicable zero-capable AV11/AV12 path.", "predicted_discriminant": "The exact selector call/dataflow and complete selector/ActorValue source screens contain no non-positive award modifier for AV11 or AV12.", "status": "proposed", "evidence": ["EV-0221", "EV-0262", "EV-0260"]},
        ],
        "methods": [
            "Freshly query GOG AE 1.6.1179.0 FUN_14077d090 and its caller FUN_140739050 read-only; verify selector 0x16, credit-float mutation order, AVSK progress stores, and any skill-use ActorValue reads without transferring RVAs to Steam.",
            "Map selector 0x16 and all relevant Heavy/Light skill-use ActorValue identifiers from the pinned CommonLib source, then screen exact official PERK entry-point and MGEF/AVIF fields that can modify the credit or its multipliers.",
            "Cross-reference the prior EP22/Mod Skill Use screen EV-0262; preserve exact five-master denominators, conditions and positive/zero/negative amounts, with no active-profile winner claim.",
            "Keep the downstream credit path separate from HitData mitigation and retain EV-0260 for a future matched Steam hit with positive armor protection and numeric AVSK controls.",
        ],
        "blocked_by": [], "evidence": ["EV-0221", "EV-0262", "EV-0260"],
        "priority": 0.99, "information_gain": 0.96,
        "next_action": "Freshly query the identity-checked GOG FUN_14077d090 credit helper and FUN_140739050 positive-input caller; test whether selector 0x16 changes the points float before the AVSK progress write, then resolve the exact Light/Heavy skill-use ActorValues from CommonLib before screening official records.",
        "linked_claims": ["CL-L092", "CL-L487"], "successors": [], "attempts": [],
    })
    FRONTIER_PATH.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"registered": ["EV-0700", "EV-0701", "EV-0702"], "manifest": private(manifest_path), "manifest_sha256": sha(manifest_path), "claims": ["CL-L486", "CL-L487"], "mechanism": "M-0209", "successor": "Q-0092"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
