#!/usr/bin/env python3
"""Register Q69's corrected Grotto dialogue trace and durable captures."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TX_ID = "TX-20261018-0005"
TX = ROOT / ".local/alignment/transactions" / TX_ID
NOTE = TX / "EV-0391-0394-da05-grotto-source-screen.md"
MANIFEST = TX / "EV-0391-0394-capture-manifest.json"
EVIDENCE = ROOT / "research/EVIDENCE.json"
FRONTIER = ROOT / "research/FRONTIER.json"
CLAIMS = ROOT / "research/CLAIMS.md"
MECHANISMS = ROOT / "research/MECHANISMS.md"
GRAPH = ROOT / "research/KNOWLEDGE_GRAPH.md"
CONTRADICTIONS = ROOT / "research/CONTRADICTIONS.md"

CAPTURE_TREES = [
    TX,
    ROOT / ".local/alignment/xedit-native/20261018T144726.275658Z",
]
NATIVE_SESSIONS = [
    "20261018T144324.911664Z",  # helper QUST 000955CF
    "20261018T145119.084872Z",  # INFO 00095585
    "20261018T145441.538217Z",  # DIAL 00095582
    "20261018T150644.529204Z",  # REFR 000C198B
    "20261018T151022.399353Z",  # REFR 000955D9
    "20261018T151433.267665Z",  # REFR 0010AA3E (v5 VMAD cross-check)
]
NATIVE_FILES = [
    "manifest.json",
    "native-loaded-files.txt",
    "native-query-status.txt",
    "native-records.tsv",
    "native-result.json",
]
PRIOR_CAPTURES = [
    ".local/xedit-authoritative-copy/out/xedit/20261018T131654.106360Z/native-records.tsv",
    ".local/alignment/transactions/TX-20261018-0003/TIF__00095585.pex",
    ".local/alignment/transactions/TX-20261018-0003/TIF__00095585.disassembly.raw",
    ".local/alignment/transactions/TX-20261018-0003/QF_DA05_0002A49A.pex",
    ".local/alignment/transactions/TX-20261018-0003/QF_DA05_0002A49A.disassembly.raw",
    ".local/alignment/transactions/TX-20261018-0003/QF_dunBloatedMansGrottoQST_000955CF.pex",
    ".local/alignment/transactions/TX-20261018-0003/QF_dunBloatedMansGrottoQST_000955CF.disassembly.raw",
    ".local/alignment/transactions/TX-20261018-0003/DA05QuestScript.disassembly.raw",
    ".local/alignment/transactions/TX-20261018-0003/EV-0383-0386-da05-source-screen.md",
]
TRACKED_INPUTS = [
    "docs/LOCAL_RUNTIME_CONTRACT.md",
    "docs/HARNESS_READINESS.md",
    "protocols/TOOL_ROUTING.md",
    "tools/xedit_bridge.py",
    "tools/xedit_scripts/native_record_query.pas.tpl",
    "tools/plugin_reader.py",
    "tools/papyrus_pex.py",
    "scripts/research_state.py",
    "experiments/EXP-0120-da05-grotto-stage20/README.md",
    "experiments/EXP-0120-da05-grotto-stage20/hypothesis.md",
    "experiments/EXP-0120-da05-grotto-stage20/expected-discriminants.md",
    "experiments/EXP-0120-da05-grotto-stage20/protocol.md",
    "experiments/EXP-0120-da05-grotto-stage20/results.md",
    "experiments/EXP-0120-da05-grotto-stage20/implications.md",
    "experiments/EXP-0120-da05-grotto-stage20/scan_helper_references.py",
    "experiments/EXP-0120-da05-grotto-stage20/triage_helper_vmad_candidates.py",
    "experiments/EXP-0120-da05-grotto-stage20/decode_helper_trigger_vmad.py",
    "experiments/EXP-0120-da05-grotto-stage20/capture_archive_metadata.py",
    "experiments/EXP-0120-da05-grotto-stage20/register_q69.py",
]

NOTE_TEXT = """# EV-0391–EV-0394 — corrected DA05 Grotto callback trace

- Transaction: TX-20261018-0005 / Q-0069
- Scope: fixed official five-master source view plus bounded Skyrim - Misc.bsa PEX extraction. Steam AE 1.6.1170.0 identity is EV-0109; no live state or profile winner was observed.
- Correction: TIF__00095585 calls TopicInfo.GetOwningQuest().SetStage(20) on helper QUST 000955CF. Its stage-20 fragment kills alias Hunter00_JKier and requests main DA05 stage 60. The TIF's DA05 property separately sets PlayerTalkedToHunter.
- The prior direct-main-stage-20 interpretation is superseded. Papyrus API documentation says TopicInfo.GetOwningQuest returns the quest that owns the TopicInfo; the INFO is under DIAL 00095582, owned by helper QUST 000955CF.
- The ordinary main DA05 stage-50 fragment requests helper stage 10. The helper is not Start Game Enabled. Dialogue availability, alias fill, fresh-state Steam startup and player access remain unobserved.
- No OBJ-1/OBJ-2 causal edge is supported.
"""


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def rows(paths: list[Path]) -> list[dict[str, Any]]:
    result = []
    for path in sorted(set(paths)):
        if not path.is_file():
            raise FileNotFoundError(path.relative_to(ROOT).as_posix())
        result.append({
            "artifact": path.relative_to(ROOT).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": digest(path),
        })
    return result


def main() -> int:
    TX.mkdir(parents=True, exist_ok=True)
    if any(item.get("id") in {"EV-0391", "EV-0392", "EV-0393", "EV-0394"}
           for item in json.loads(EVIDENCE.read_text(encoding="utf-8"))["items"]):
        raise ValueError("one or more Q69 evidence IDs already exist")
    if "CL-L226" in CLAIMS.read_text(encoding="utf-8"):
        raise ValueError("Q69 claims already exist")
    if "M-0093" in MECHANISMS.read_text(encoding="utf-8"):
        raise ValueError("M-0093 already exists")

    NOTE.write_text(NOTE_TEXT, encoding="utf-8")
    capture_paths: list[Path] = []
    for tree in CAPTURE_TREES:
        if tree.is_dir():
            capture_paths.extend(path for path in tree.rglob("*") if path.is_file())
    for stamp in NATIVE_SESSIONS:
        folder = ROOT / ".local/xedit-authoritative-copy/out/xedit" / stamp
        capture_paths.extend(folder / name for name in NATIVE_FILES if (folder / name).is_file())
    capture_paths.extend(ROOT / path for path in PRIOR_CAPTURES)
    capture_files = rows(capture_paths)
    tracked_inputs = rows([ROOT / path for path in TRACKED_INPUTS])

    scan = json.loads((TX / "da05-helper-reference-screen.json").read_text(encoding="utf-8"))
    archive = json.loads((TX / "misc-bsa-metadata.json").read_text(encoding="utf-8"))
    manifest = {
        "evidence_ids": ["EV-0391", "EV-0392", "EV-0393", "EV-0394"],
        "transaction_id": TX_ID,
        "frontier_id": "Q-0069",
        "captured_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "target": {"distribution": "Steam", "product_version": "1.6.1170.0", "identity_evidence": "EV-0109"},
        "source_scope": "Fixed official five-master SSEView and exact-byte source scan; no active-profile winner or live query.",
        "official_master_hashes_and_record_counts": scan["sources"],
        "exact_reference_census": {
            "records_parsed": scan["record_count"],
            "raw_byte_hits": scan["raw_reference_match_count"],
            "unique_candidate_records": scan["unique_candidate_record_count"],
            "warning": scan["warning"],
        },
        "archive": archive,
        "external_sources": [
            {"title": "TES5Edit wbDefinitionsTES5.pas", "revision": "dev-4.1.6", "url": "https://github.com/TES5Edit/TES5Edit/blob/dev-4.1.6/Core/wbDefinitionsTES5.pas#L3083-L3086", "observed": "GetIsAliasRef function index 566 takes an alias parameter."},
            {"title": "GetOwningQuest — TopicInfo", "url": "https://papyrus.bellcube.dev/skyrimse/script/topicinfo/function/getowningquest/", "observed": "Documentation says the method returns the quest that owns the TopicInfo; the page links the Creation Kit Wiki source."},
            {"title": "Creation Kit Wiki GetOwningQuest — TopicInfo", "url": "https://ck.uesp.net/wiki/GetOwningQuest_-_TopicInfo", "observed": "Direct page fetch returned 403 during this capture; Papyrus Index mirror retained above."},
        ],
        "capture_files": capture_files,
        "tracked_inputs": tracked_inputs,
        "limits": [
            "No active profile order or profile winner",
            "No clean level-one save, read-only Observer, dialogue availability, alias fill, or live quest transition",
            "Five-master exact-byte scan is not a global archive, loose-file, native-caller, or runtime negative",
            "GOG AE 1.6.1179.0 SetStage evidence is not transferred to Steam AE 1.6.1170.0",
            "Not a vanilla reproduction",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    local_hashes = {item["artifact"]: item["sha256"] for item in capture_files + tracked_inputs}
    local_hashes[MANIFEST.relative_to(ROOT).as_posix()] = digest(MANIFEST)
    stamp = manifest["captured_utc"]
    common = {
        "captured_utc": stamp,
        "edition": "AE",
        "runtime": "Steam SkyrimSE.exe ProductVersion 1.6.1170.0 identity is EV-0109; no live game state was inspected.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "strict Python 3.12 dispatcher",
            "native SSEView 4.1.5f fixed-five-master FormID exports",
            "tools.plugin_reader exact record parser",
            "source-hash-verified FormID/VMAD census and v4/v5 decoder",
            "bounded classic PEX extraction/disassembly from Skyrim - Misc.bsa",
        ],
        "related_evidence": ["EV-0109", "EV-0260", "EV-0313", "EV-0380", "EV-0384", "EV-0386"],
        "local_hashes": local_hashes,
        "artifact": f"private-local:{NOTE.relative_to(ROOT).as_posix()}",
        "sha256": digest(NOTE),
    }
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    evidence["items"].extend([
        {
            **common,
            "id": "EV-0391",
            "kind": "record",
            "source": "Native SSEView exports and direct Skyrim.esm record parsing in the fixed official five-master scope",
            "coverage": "INFO 00095585, DIAL 00095582, helper QUST 000955CF, main DA05 QUST 0002A49A, and helper alias/stage fields; no profile-specific winner.",
            "result": "INFO 00095585 is the only INFO child of DIAL 00095582, owned by helper QUST 000955CF. Its sole condition uses function 566, alias parameter 57, comparison 1.0, Run On Subject; helper alias 57 is forced to DA05JKierREF in BloatedMansGrottoWorld. Helper Start Game Enabled is clear. TES5Edit dev-4.1.6 maps function 566 to GetIsAliasRef with a ptAlias parameter.",
        },
        {
            **common,
            "id": "EV-0392",
            "kind": "source_screen",
            "source": "Hash-verified fixed official-five-master exact little-endian FormID-byte census and bounded VMAD decoding",
            "coverage": "1,178,548 parsed records; 142 raw hits across 70 unique candidate records; 24 VMAD candidates including 18 Skyrim.esm REFR records. Both supported VMAD formats were decoded; zero errors. Native xEdit cross-checks include REFR 000955D9 and 0010AA3E.",
            "result": "The only distinct external QUST-level target in the candidate set is main DA05 0002A49A; helper QUST 000955CF also appears in self-references. All decoded placed setter references have configured helper-stage prerequisites; the attached scripts check those prerequisites before setting their target stage. This is a bounded candidate census, not a global writer negative.",
        },
        {
            **common,
            "id": "EV-0393",
            "kind": "script",
            "source": "Bounded classic PEX 3.2 extraction from Skyrim - Misc.bsa plus TopicInfo.GetOwningQuest API documentation",
            "coverage": "TIF__00095585 Fragment_0, helper QF stage 20 Fragment_2, main DA05 QF stage 50 Fragment_7, helper/main QUST stage-fragment mappings, and separate DA05 quest-script property.",
            "result": "TIF__00095585 extends TopicInfo. Fragment_0 calls GetOwningQuest().SetStage(20), then separately sets DA05.PlayerTalkedToHunter=True. GetOwningQuest returns the quest owning the TopicInfo; DIAL 00095582's owner is helper QUST 000955CF, so stage 20 targets the helper. Helper stage 20 maps to Fragment_2, which kills alias Hunter00_JKier and requests main DA05.SetStage(60). Main DA05 stage 50 maps to Fragment_7 and requests helper SetStage(10). This corrects the earlier direct-main-stage-20 interpretation.",
        },
        {
            **common,
            "id": "EV-0394",
            "kind": "script_and_placement",
            "source": "Hash-verified classic PEX attachments and native fixed-five-master reference exports",
            "coverage": "All 18 REFR candidates with exact helper QUST bytes; decoded trigger scripts include dunBloatedManSetStageOnActivate, defaultSetStageTRIGSpecificActor, dunBloatedManSetStageOnLoad, and defaultStartSceneTrigScript.",
            "result": "Each decoded setter placement configures a prerequisite helper stage and the attached activation/trigger script calls GetStageDone before SetStage unless the optional stage is -1. The OnLoad script reads main DA05 stages 50/100 and only requests helper stage 105 at the latter threshold. The placement and script screen supports the mapped downstream route but does not establish all possible entry sources or runtime availability.",
        },
    ])
    EVIDENCE.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    claims = CLAIMS.read_text(encoding="utf-8")
    old_claim = next((line for line in claims.splitlines() if line.startswith("| CL-L222 |")), None)
    if old_claim is None:
        raise ValueError("CL-L222 row not found")
    corrected_old_claim = "| CL-L222 | The original direct-main-stage-20 interpretation for INFO 00095585 is corrected by CL-L226: its TIF sets the owning helper quest to stage 20, then the helper fragment requests main DA05 stage 60. | corrected from the mapped callback trace | [EV-0386], [EV-0391], [EV-0393] | The original wording mistook the separate DA05.PlayerTalkedToHunter property for the stage-call receiver; fresh-state availability and Steam behavior remain unobserved. |"
    claims = claims.replace(old_claim, corrected_old_claim)
    claims += "\n\n| CL-L226 | INFO 00095585's TopicInfo callback sets its owning helper QUST 000955CF to stage 20; helper stage-20 Fragment_2 kills alias Hunter00_JKier and requests main DA05.SetStage(60), while the TIF separately sets DA05.PlayerTalkedToHunter. | supported for the mapped source callback | [EV-0391], [EV-0393] | No dialogue availability, alias fill, fresh-state startup, level-one interaction, or Steam runtime result is established. |\n"
    claims += "\n| CL-L227 | In the fixed five-master source scope, main DA05 stage 50 requests helper stage 10; the helper quest is not Start Game Enabled, and all 18 decoded attached REFR VMAD candidates are accounted for with their configured stage prerequisites. | supported for the bounded source path | [EV-0391], [EV-0392], [EV-0394] | This does not exclude unscanned archives, loose scripts, native or runtime-indirect sources, profile overrides, or a natural helper start. |\n"
    CLAIMS.write_text(claims, encoding="utf-8")

    mechanisms = MECHANISMS.read_text(encoding="utf-8")
    mechanisms += "\n\n## M-0093 — Grotto TopicInfo helper-to-main stage chain (Q-0069)\n\n"
    mechanisms += "INFO 00095585 is owned through DIAL 00095582 by helper QUST 000955CF and is conditioned on alias 57 (`Hunter00_JKier`) [EV-0391]. Its TIF extends TopicInfo and calls `GetOwningQuest().SetStage(20)`, which targets that helper quest; the TIF separately sets `DA05.PlayerTalkedToHunter` through its main-quest property [EV-0393]. Helper stage 20 maps to a fragment that kills the Hunter alias and requests main DA05.SetStage(60). In the ordinary route, main DA05 stage 50 requests helper stage 10; helper Start Game Enabled is clear, and the bounded placed setter candidates have prior helper-stage conditions [EV-0391], [EV-0392], [EV-0394]. This supports downstream source sequencing but leaves independent helper availability and Steam fresh-state SetStage behavior open. The GOG AE 1.6.1179.0 callback is not transferred to Steam AE 1.6.1170.0 [EV-0313], [EV-0380]. No OBJ-2 edge is justified: no shared native call, ActorValue, HitData field, callback owner, or serialized state is identified [CL-L226], [CL-L227].\n"
    MECHANISMS.write_text(mechanisms, encoding="utf-8")

    graph = GRAPH.read_text(encoding="utf-8")
    old_sentence = "The separate grotto INFO 00095585 TIF calls DA05.SetStage(20) and sets a quest-script property, but availability and fresh-state startup remain unresolved [EV-0386, CL-L222]."
    new_sentence = "The separate grotto INFO 00095585 TIF sets its TopicInfo-owning helper QUST 000955CF to stage 20; helper Fragment_2 kills alias Hunter00_JKier and requests main DA05 stage 60, while the TIF separately sets DA05.PlayerTalkedToHunter [EV-0391, EV-0393, CL-L226]. Availability and fresh-state startup remain unresolved."
    if old_sentence not in graph:
        raise ValueError("Q69 sentence in the prior DA05 graph section not found")
    graph = graph.replace(old_sentence, new_sentence)
    graph += "\n\n## Q-0069 — corrected Grotto helper dialogue route\n\n"
    graph += "INFO 00095585 belongs to helper QUST 000955CF through DIAL 00095582 and requires alias 57 on Subject [EV-0391]. The TIF calls its owning helper quest SetStage(20), not main DA05.SetStage(20); helper Fragment_2 kills the Hunter alias and requests main DA05.SetStage(60), while the separate DA05 property marks PlayerTalkedToHunter [EV-0393]. The mapped ordinary route is main DA05 stage 50 -> helper stage 10; fixed-source census and placed trigger checks support that route but do not establish exclusivity [EV-0392], [EV-0394], [CL-L226], [CL-L227]. Retain a clean level-one pre-stage-50 dialogue test as Q-0071; reopen Q-0070 for static physical cave/door mapping before its exact runtime discriminator [EV-0260]. No OBJ-1/OBJ-2 edge is supported.\n"
    GRAPH.write_text(graph, encoding="utf-8")

    contradictions = CONTRADICTIONS.read_text(encoding="utf-8")
    if "C-OBJ1-Q69-TIF-STAGE-RECEIVER" not in contradictions:
        contradictions += "\n\n## C-OBJ1-Q69-TIF-STAGE-RECEIVER — TopicInfo stage receiver\n\n"
        contradictions += "- **Earlier model:** TIF__00095585 directly requests main DA05.SetStage(20), based on its separate `DA05` quest property.\n"
        contradictions += "- **Corrected model:** the TIF calls `TopicInfo.GetOwningQuest().SetStage(20)`. The API returns the quest owning the TopicInfo; INFO 00095585 is under DIAL 00095582, owned by helper QUST 000955CF. Helper stage 20 maps to Fragment_2, which kills alias Hunter00_JKier and requests main DA05.SetStage(60). The TIF separately writes DA05.PlayerTalkedToHunter.\n"
        contradictions += "- **Evidence:** native INFO/DIAL/QUST owner and alias fields, QF stage-fragment maps, and the TIF/helper/main QF disassemblies [EV-0391], [EV-0393]. Papyrus API description: https://papyrus.bellcube.dev/skyrimse/script/topicinfo/function/getowningquest/ .\n"
        contradictions += "- **Assessment:** corrected source receiver and requested main stage are supported. Whether the INFO is available before main DA05 stage 50, and how Steam AE starts a stopped quest from this callback, remain unresolved.\n"
        contradictions += "- **Discriminant:** clean level-one pre-stage-50 no-contact control followed by natural INFO interaction with read-only capture of both quest states, alias 57, actor state, callback result, and player level.\n"
    CONTRADICTIONS.write_text(contradictions, encoding="utf-8")

    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    items = frontier["items"]
    q69 = next(item for item in items if item.get("id") == "Q-0069")
    q70 = next(item for item in items if item.get("id") == "Q-0070")
    if any(item.get("id") == "Q-0071" for item in items):
        raise ValueError("Q-0071 already exists")
    q69["question"] = "Can INFO 00095585 be naturally available before main DA05 stage 50, and can its helper-stage-20 callback reach main DA05 stage 60 from that state?"
    q69["next_action"] = "Q-0071 preserves the clean level-one discriminator: before main DA05 stage 50, observe helper running/stage state, alias 57, INFO availability, and the natural helper-stage-20 to main-stage-60 transition. Steam profile/order, save, and read-only observer are missing, so continue with static Q-0070 cave mapping."
    q69["cross_source_assessment"] = "The mapped ordinary source path is main DA05 stage 50 -> helper stage 10. INFO 00095585's TIF sets its owning helper quest to stage 20; helper Fragment_2 kills Hunter00_JKier and requests main DA05 stage 60. The DA05 property separately sets PlayerTalkedToHunter. This supports ordinary downstream sequencing but does not establish independent helper startup, runtime dialogue availability, or Steam fresh-state SetStage behavior. No OBJ-2 causal edge is supported."
    q69["linked_claims"] = list(dict.fromkeys([*q69.get("linked_claims", []), "CL-L222", "CL-L226", "CL-L227"]))
    q69["evidence"] = list(dict.fromkeys([*q69.get("evidence", []), "EV-0391", "EV-0392", "EV-0393", "EV-0394"]))
    q69["successors"] = list(dict.fromkeys([*q69.get("successors", []), "Q-0071"]))
    models = {
        "Q69-H1": ("supported", ["EV-0391", "EV-0393", "EV-0394"], "The mapped ordinary route requests helper stage 10 from main DA05 stage 50. The helper quest is not Start Game Enabled; its INFO condition uses forced alias 57. The callback's helper stage 20 then kills that alias and requests main DA05 stage 60. This supports downstream sequencing within the mapped source path, not runtime exclusivity."),
        "Q69-H2": ("proposed", ["EV-0392", "EV-0394"], "A natural independent helper start could expose the INFO before main DA05 stage 50 and request main DA05 stage 60, but no such source is established by the bounded census and runtime availability is unknown."),
        "Q69-H3": ("proposed", ["EV-0313", "EV-0380", "EV-0393"], "The helper callback requests main DA05 stage 60, but the Steam AE fresh-state startup/readiness outcome remains unknown; the separate GOG SetStage trace is not build-transfer evidence."),
    }
    for hypothesis in q69["hypotheses"]:
        status, evidence_ids, model = models[hypothesis["id"]]
        hypothesis.update(status=status, evidence=evidence_ids, model=model)
    q69["attempts"].append({
        "action_key": "q69-owning-quest-stage-receiver-correction",
        "outcome": "The TIF's GetOwningQuest().SetStage(20) targets helper QUST 000955CF because TopicInfo.GetOwningQuest returns the quest owning INFO 00095585. Helper stage 20 maps to Fragment_2, which kills alias Hunter00_JKier and requests main DA05 stage 60. The TIF's DA05 property separately sets PlayerTalkedToHunter; the previous direct-main-stage-20 interpretation is corrected.",
        "evidence": ["EV-0391", "EV-0393"],
        "new_discriminant": "Test natural INFO availability before main DA05 stage 50; capture helper running/stage and alias 57, then determine whether the callback's helper stage 20 and main stage 60 request complete on verified Steam AE without intervention.",
        "recorded_utc": stamp,
    })

    q70["status"] = "open"
    q70["next_action"] = "Map the exact troll-cave location, entrance door/reference, destination cell, and nearby WE13 trigger/encounter placements from local UESP and fixed official-master records. Keep physical traversal, Story Manager scheduling, quest startup, aliases, and spawn as distinct states; then retain the clean level-one Observer test as blocked by EV-0260."
    q70["cross_source_assessment"] = "The level-one runtime discriminator remains unavailable under EV-0260, but static location, door, and placement mapping is ready. This reopening selects that offline subtask; it does not claim physical traversal or a level-one result."
    q70["methods"] = list(dict.fromkeys([*q70["methods"], "Use local UESP grounding and fixed official-master location, door, REFR, and encounter records to map the physical route; do not infer player access from a placed reference alone."]))

    items.append({
        "id": "Q-0071",
        "objective": "OBJ-1",
        "kind": "experiment",
        "status": "blocked_environment",
        "question": "On a clean verified Steam AE level-one state before main DA05 stage 50, can INFO 00095585 expose the Grotto helper and drive helper stage 20 to the main DA05 stage-60 request?",
        "hypotheses": [
            {"id": "Q71-H1", "model": "INFO 00095585 remains unavailable until the ordinary main DA05 route starts helper QUST 000955CF at stage 10.", "predicted_discriminant": "Before stage 50, a natural clean-state capture shows helper stopped, alias 57 unfilled, and INFO unavailable; after ordinary DA05 initiation the helper and INFO become available.", "status": "proposed", "evidence": ["EV-0391", "EV-0393", "EV-0394", "EV-0260"]},
            {"id": "Q71-H2", "model": "A natural level-one route makes the INFO available before main DA05 stage 50; its callback sets helper stage 20 and requests main DA05 stage 60.", "predicted_discriminant": "Without console commands, injected scripts, plugin edits, or save edits, a pre-stage-50 interaction changes helper/main quest state and hunter state while player level remains 1.", "status": "proposed", "evidence": ["EV-0391", "EV-0393", "EV-0260"]},
            {"id": "Q71-H3", "model": "The callback runs but Steam AE's SetStage startup/readiness path does not fully start or initialize stopped main DA05.", "predicted_discriminant": "A callback capture shows helper stage 20 and alias state change but distinguishes main DA05 running state, current/completed stage 60, required aliases, and functional progression.", "status": "proposed", "evidence": ["EV-0313", "EV-0380", "EV-0393", "EV-0260"]},
        ],
        "methods": [
            "Verify the exact Steam SkyrimSE.exe ProductVersion and complete target order; if MO2-managed, use the selected profile's explicit full plugins.txt.",
            "Use a clean disposable numeric level-one save and a read-only observer for level, both quest running/stage states, helper alias 57, INFO availability, actor state, and callback outcome.",
            "Capture a no-contact control before main DA05 stage 50, then attempt only the natural dialogue route; do not force stages, inject scripts, edit plugins, or alter the save.",
            "If the callback runs, distinguish main DA05 start state, stage 60 completion, aliases, and actual progression from a request alone.",
        ],
        "blocked_by": [],
        "evidence": ["EV-0109", "EV-0260", "EV-0313", "EV-0380", "EV-0391", "EV-0393", "EV-0394"],
        "priority": 0.96,
        "information_gain": 0.98,
        "next_action": "EV-0260 records no verified complete target order, clean level-one save, or deployed read-only Observer. Keep this runtime discriminator blocked while pursuing Q-0070's static cave/door route map.",
        "linked_claims": ["CL-L226", "CL-L227"],
        "successors": [],
        "attempts": [],
        "cross_source_assessment": "The static route is corrected and bounded by EV-0391–EV-0394. A clean pre-stage-50 Steam AE interaction is still required; GOG SetStage behavior is not substituted for Steam runtime evidence.",
    })

    next_action = q70["next_action"]
    frontier["session_checkpoint"] = {
        "timestamp_utc": stamp.replace("+00:00", "Z"),
        "task": "Q-0069 source trace corrected and registered; Q-0071 preserves the blocked clean dialogue test; Q-0070 reopened for static cave access mapping.",
        "next_action": next_action,
    }
    frontier["last_session_checkpoint"] = {
        "recorded_utc": stamp,
        "next_action": next_action,
        "active_process": "TX-20261018-0005 / Q-0069 is ready to close; Q-0070 is the next static P0 source question.",
    }
    frontier["next_action"] = next_action
    FRONTIER.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "registered": ["EV-0391", "EV-0392", "EV-0393", "EV-0394"],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "capture_file_count": len(capture_files),
        "tracked_input_count": len(tracked_inputs),
        "corrected_stage_route": "TIF -> helper 000955CF stage 20 -> main DA05 stage 60",
        "next_frontier": "Q-0070",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
