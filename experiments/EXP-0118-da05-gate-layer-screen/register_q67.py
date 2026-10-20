from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TX_ID = "TX-20261018-0003"
TX = ROOT / ".local/alignment/transactions" / TX_ID
NOTE = TX / "EV-0383-0386-da05-source-screen.md"
MANIFEST = TX / "EV-0383-0386-capture-manifest.json"
EVIDENCE = ROOT / "research/EVIDENCE.json"
FRONTIER = ROOT / "research/FRONTIER.json"
CLAIMS = ROOT / "research/CLAIMS.md"
GRAPH = ROOT / "research/KNOWLEDGE_GRAPH.md"

CAPTURES = (
    ".local/alignment/transactions/TX-20261018-0003/uesp-da05-ill-met-page.stdout.raw",
    ".local/alignment/transactions/TX-20261018-0003/da05-dialogue-join.json",
    ".local/alignment/transactions/TX-20261018-0003/DA05QuestScript.pex",
    ".local/alignment/transactions/TX-20261018-0003/DA05QuestScript.disassembly.raw",
    ".local/alignment/transactions/TX-20261018-0003/DA05SindingScript.pex",
    ".local/alignment/transactions/TX-20261018-0003/DA05SindingScript.disassembly.raw",
    ".local/alignment/transactions/TX-20261018-0003/QF_DA05_0002A49A.pex",
    ".local/alignment/transactions/TX-20261018-0003/QF_DA05_0002A49A.disassembly.raw",
    ".local/alignment/transactions/TX-20261018-0003/TIF__00095585.pex",
    ".local/alignment/transactions/TX-20261018-0003/TIF__00095585.disassembly.raw",
    ".local/alignment/transactions/TX-20261018-0003/QF_dunBloatedMansGrottoQST_000955CF.pex",
    ".local/alignment/transactions/TX-20261018-0003/QF_dunBloatedMansGrottoQST_000955CF.disassembly.raw",
    ".local/alignment/xedit-bridge/20261018T131108.365179Z/stdout.raw",
    ".local/alignment/xedit-bridge/20261018T131221.234271Z/stdout.raw",
    ".local/alignment/xedit-bridge/20261018T131222.015276Z/stdout.raw",
    ".local/alignment/xedit-bridge/20261018T131222.016602Z/stdout.raw",
    ".local/alignment/xedit-bridge/20261018T132340.031277Z/stdout.raw",
    ".local/alignment/xedit-bridge/20261018T132641.801711Z/stdout.raw",
    ".local/alignment/xedit-bridge/20261018T132658.766597Z/stdout.raw",
    ".local/alignment/xedit-bridge/20261018T132718.052377Z/stdout.raw",
    ".local/alignment/xedit-bridge/20261018T132916.216104Z/stdout.raw",
    ".local/alignment/xedit-bridge/20261018T133801.415402Z/stdout.raw",
    ".local/alignment/xedit-bridge/20261018T133803.349361Z/stdout.raw",
    ".local/alignment/xedit-native/20261018T131313.273694Z/native-result.json",
    ".local/alignment/xedit-native/20261018T131313.273694Z/native-records.tsv",
    ".local/alignment/xedit-native/20261018T131654.561286Z/native-result.json",
    ".local/alignment/xedit-native/20261018T131654.561286Z/native-records.tsv",
    ".local/alignment/xedit-native/20261018T132023.950262Z/native-result.json",
    ".local/alignment/xedit-native/20261018T132023.950262Z/native-records.tsv",
)
INPUTS = (
    "scripts/python_env.py",
    "scripts/research_state.py",
    "scripts/research_transactions.py",
    "tools/xedit_bridge.py",
    "tools/plugin_reader.py",
    "tools/papyrus_pex.py",
    "tools/uesp/__main__.py",
    "tools/uesp/core.py",
    "experiments/EXP-0052-da02-level-gate/summarize_da02_initial.py",
    "experiments/EXP-0118-da05-gate-layer-screen/README.md",
    "experiments/EXP-0118-da05-gate-layer-screen/hypothesis.md",
    "experiments/EXP-0118-da05-gate-layer-screen/protocol.md",
    "experiments/EXP-0118-da05-gate-layer-screen/expected-discriminants.md",
    "experiments/EXP-0118-da05-gate-layer-screen/results.md",
    "experiments/EXP-0118-da05-gate-layer-screen/implications.md",
    "experiments/EXP-0118-da05-gate-layer-screen/join_da05_dialogue.py",
    "experiments/EXP-0118-da05-gate-layer-screen/register_q67.py",
)


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


NOTE_TEXT = """# EV-0383–EV-0386 — DA05 source screen

- **Transaction:** TX-20261018-0003 / Q-0067
- **Lane:** fixed official-master record screen, group-aware Skyrim.esm DIAL/INFO join, local UESP revision, bounded base-Misc-BSA PEX inspection
- **Target identity:** Steam AE 1.6.1170.0 is identified separately in EV-0109. The prepared official five-master order and Skyrim.esm source hash are in the manifest. No target profile winner or live state is established.
- **Archive identity:** `Skyrim - Misc.bsa`, SHA-256 `ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d`.

## Competing models and outcome

- **Q67-H1:** every ordinary DA05 initiation path has a necessary above-one level predicate. Falsified within the screened source scope.
- **Q67-H2:** a level-gated dispatch coexists with an independent Sinding/Mathies dialogue start. Falsified within the screened source scope because no level gate was found in the covered route.
- **Q67-H3:** the covered official source path contains no above-one player-level predicate. Supported within scope; ordinary level-one actor availability and progression were not observed.

## Direct observations

1. The local UESP page `Skyrim:Ill Met By Moonlight`, revision 3628445, timestamp 2026-09-06T11:44:57Z, lists Mathies or Sinding as quest givers and has no `ReqLevel` field. It is secondary-source context only.
2. Native xEdit used the fixed official five-master view. `QUST 0002A49A DA05` resolves to Update.esm in that scope, is marked Start Game Enabled, and has no exported `GetLevel` field. This is not a profile-specific winner. Skyrim.esm `SMQN 0005D331 DA05LocationCheckNode` has `GetEventData` for Falkreath location plus `GetStage` on DA05; neither is `GetLevel`.
3. The source-group join verified Skyrim.esm SHA-256 `2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107`, walked 869,688 records, and read 15,037 DIALs. It found 38 DA05-owned DIALs with 51 linked INFO children and zero function-index-80 conditions. Across all 31,465 INFOs, the 30 with a direct DA05 QUST reference in CTDA/VMAD also have zero function-index-80 conditions. The joined families include the Sinding start and Mathies funeral topics. EV-0214 supplies the `GetLevel` function-index schema.
4. The bounded script screen found no textual `GetLevel` in `QF_DA05_0002A49A`, `DA05QuestScript`, or `DA05SindingScript`. Separately, `INFO 00095585` belongs to `DIAL 00095582` under `QUST 000955CF dunBloatedMansGrottoQST`; its `TIF__00095585` `Fragment_0` calls `DA05.SetStage(20)` and sets `DA05QuestScript.PlayerTalkedToHunter`. This is a stage writer, not proof of main quest start or of being available before DA05 stage 20. Its INFO/alias availability and fresh-state startup effect remain unresolved.

## Boundaries and synthesis

No level-one gameplay, actor/topic availability, quest-state transition, useful progression, profile-specific winner, or vanilla reproduction was observed. The dialogue join covers source-group ancestry and direct DA05 references; it does not exclude every native, indirect, loose-file, or profile-specific writer. EV-0260 records missing live-test prerequisites. No shared native call, ActorValue, HitData field, callback owner, or serialization field connects these DA05 records/scripts to the OBJ-2 armor XP path. The grotto `SetStage(20)` callback is retained as a distinct follow-up question.
"""


def add_frontier_items(frontier: dict[str, Any]) -> None:
    items = frontier["items"]
    current = next(item for item in items if item.get("id") == "Q-0067")
    if current.get("status") != "in_progress":
        raise ValueError("Q-0067 is not the active in-progress frontier item")
    current["question"] = "For DA05, Ill Met by Moonlight, does the fixed official source path contain an above-one player-level gate on initiation, and what remains unproven about its ordinary dialogue and grotto entry routes?"
    current["next_action"] = "Complete the bounded source decision, keep the clean natural level-one dialogue and Grotto state test as an open runtime discriminator, then start Q-0068 WE13 for the level-12 troll-cave encounter gate."
    current["cross_source_assessment"] = "The fixed official source screen and linked PEX do not expose a GetLevel gate on DA05 QUST, its location node, or the joined Sinding/Mathies dialogue families. A separate Bloated Man's Grotto INFO callback writes stage 20, but its availability and fresh-state startup effect are unresolved. No profile winner, natural level-one progress, or OBJ-2 causal edge is established."
    current["linked_claims"] = list(dict.fromkeys([*current.get("linked_claims", []), "CL-L221", "CL-L222"]))
    for hypothesis in current["hypotheses"]:
        if hypothesis["id"] == "Q67-H1":
            hypothesis["status"] = "falsified"
            hypothesis["evidence"] = ["EV-0384", "EV-0385", "EV-0386"]
        elif hypothesis["id"] == "Q67-H2":
            hypothesis["status"] = "falsified"
            hypothesis["evidence"] = ["EV-0384", "EV-0385", "EV-0386"]
        elif hypothesis["id"] == "Q67-H3":
            hypothesis["status"] = "supported"
            hypothesis["evidence"] = ["EV-0384", "EV-0385"]
            hypothesis["model"] = "Within the fixed official source path screened here, DA05 has no above-one player-level predicate; ordinary level-one actor availability and useful progression remain unobserved."
    if any(item.get("id") == "Q-0068" for item in items):
        raise ValueError("Q-0068 already exists")
    if any(item.get("id") == "Q-0069" for item in items):
        raise ValueError("Q-0069 already exists")
    items.extend([
        {
            "id": "Q-0068",
            "objective": "OBJ-1",
            "kind": "mechanism",
            "status": "open",
            "question": "Does WE13's GetLevel >= LevelGateTrollCave (12) condition gate quest startup and alias fill in its script event path, or only a narrower troll-cave encounter branch—and can a level-one player reach the same content by ordinary exploration or another trigger?",
            "hypotheses": [
                {"id": "Q68-H1", "model": "The level-12 condition is a necessary WE13 start gate, so the scripted troll-cave encounter and its quest aliases cannot run below level 12.", "predicted_discriminant": "Trace the QUST condition into the exact Story Manager/script event parent and observe that the required Trigger and creature/location aliases depend on this start; no independent trigger or encounter dispatch reaches the content.", "status": "proposed", "evidence": []},
                {"id": "Q68-H2", "model": "The condition gates only one scheduling or alias-fill branch; ordinary cave entry or another source path can expose the same content below level 12.", "predicted_discriminant": "Find an independent package, placement, quest writer, or event path that reaches the same troll-cave content without evaluating the QUST level condition, then preserve the clean level-one discriminator.", "status": "proposed", "evidence": []},
                {"id": "Q68-H3", "model": "WE13 is a script-triggered wilderness encounter, but the current record name/condition alone cannot identify the gated transition or establish player access to a cave.", "predicted_discriminant": "Map ENAM, Story Manager parent/child records, the WEScript/parent and alias scripts, location aliases, and encounter placements; distinguish event scheduling from physical cave access.", "status": "proposed", "evidence": []}
            ],
            "methods": [
                "Reconcile the EV-0321 full official GetLevel census and source-layer winner with exact WE13 QUST and LevelGateTrollCave records.",
                "Trace the script event through its Story Manager parent/child node, WEScript and alias PEX, quest aliases, packages, and location/encounter references.",
                "Separate quest startup, alias fill, random encounter scheduling, location access, and encounter progression; keep the clean level-one test separate."
            ],
            "blocked_by": [],
            "evidence": ["EV-0321", "EV-0109", "EV-0260"],
            "priority": 0.99,
            "information_gain": 0.99,
            "next_action": "Trace QUST WE13 (0009F32F), its GetLevel >= LevelGateTrollCave condition and aliases into the exact script event, Story Manager parent, WEScript/alias PEX, and source placement chain; state whether the level condition gates startup, alias fill, or only encounter scheduling.",
            "linked_claims": [],
            "successors": [],
            "attempts": [],
            "cross_source_assessment": "EV-0321 is a complete five-official-master CTDA census plus fixed official-source-layer comparison, not a profile winner. The lead does not establish which transition WE13's condition gates or whether any physical location is inaccessible below level 12. Keep it independent of armor XP absent a shared call/state edge."
        },
        {
            "id": "Q-0069",
            "objective": "OBJ-1",
            "kind": "mechanism",
            "status": "open",
            "question": "Can the Bloated Man's Grotto INFO 00095585 callback call DA05.SetStage(20) before ordinary DA05 initiation, or is it available only after DA05 has already reached the Sinding stage?",
            "hypotheses": [
                {"id": "Q69-H1", "model": "The grotto dialogue callback is downstream of the normal DA05 start and only advances an already-running quest.", "predicted_discriminant": "Its INFO conditions or owning-quest state require an existing DA05 stage/alias and the callback does not create a fresh quest start.", "status": "proposed", "evidence": []},
                {"id": "Q69-H2", "model": "The independent grotto quest can make the INFO available and its stage-20 call starts or advances DA05 without the normal Sinding/Mathies start route.", "predicted_discriminant": "A clean record path shows the INFO available before DA05 starts and the SetStage call reaches Quest startup for DA05 without a level gate.", "status": "proposed", "evidence": []},
                {"id": "Q69-H3", "model": "The callback's trigger condition remains unresolved from the bounded INFO/PEX evidence, so neither start model is currently supported.", "predicted_discriminant": "Resolve the remaining condition function, owning-quest state, and SetStage startup guard without inferring a gameplay result from the script body alone.", "status": "proposed", "evidence": []}
            ],
            "methods": ["Resolve INFO 00095585 CTDA and parent DIAL/QUST gates", "Trace the script callback into the mapped Quest.SetStage startup guard", "Retain a natural level-one interaction and no-contact control"],
            "blocked_by": ["Q-0067"],
            "evidence": ["EV-0384", "EV-0386", "EV-0260"],
            "priority": 0.88,
            "information_gain": 0.92,
            "next_action": "After the WE13 gate-layer pass, decode INFO 00095585's remaining condition and owning quest, then compare its SetStage(20) callback with the mapped Quest startup guard and the DA05 running/stage requirements.",
            "linked_claims": ["CL-L222"],
            "successors": [],
            "attempts": [],
            "cross_source_assessment": "The TIF body is source evidence for a SetStage call only. INFO availability, fresh-state startup, player reachability, profile winner, and actual progress are unobserved. No causal link to OBJ-2 is supported."
        }
    ])
    frontier["session_next_action"] = "Complete Q-0067 as a bounded no-level-gate source screen; then trace WE13's level-12 troll-cave condition through its script event, Story Manager parent, aliases, and placements under Q-0068."
    frontier["session_checkpoint"] = {
        "timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "task": "Q-0067 source screen is assembled and ready for durable evidence registration and bounded closure; a full level-one test is still open.",
        "next_action": "Close Q-0067 with EV-0383–EV-0386, preserve the DA05 no-level-gate finding and grotto stage-writer follow-up, then begin Q-0068 on WE13's LevelGateTrollCave condition."
    }
    frontier["last_session_checkpoint"] = {
        "recorded_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "next_action": frontier["session_checkpoint"]["next_action"],
        "active_process": "TX-20261018-0003 running on Q-0067; close the bounded DA05 source screen, then start Q-0068 WE13."
    }
    frontier["next_action"] = frontier["session_checkpoint"]["next_action"]


def main() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    existing_ids = {row.get("id") for row in evidence.get("items", [])}
    if any(f"EV-{number}" in existing_ids for number in ("0383", "0384", "0385", "0386")):
        raise ValueError("one or more EV-0383–EV-0386 entries already exist")
    for relative in (*CAPTURES, *INPUTS):
        if not (ROOT / relative).is_file():
            raise FileNotFoundError(ROOT / relative)

    NOTE.write_text(NOTE_TEXT, encoding="utf-8", newline="\n")
    artifact_paths = sorted({ROOT / relative for relative in (*CAPTURES, *INPUTS)} | {NOTE})
    artifact_rows = [
        {"artifact": path.relative_to(ROOT).as_posix(), "size_bytes": path.stat().st_size, "sha256": digest(path)}
        for path in artifact_paths
    ]
    manifest = {
        "evidence_ids": ["EV-0383", "EV-0384", "EV-0385", "EV-0386"],
        "transaction_id": TX_ID,
        "frontier_id": "Q-0067",
        "captured_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "target": {"distribution": "Steam", "product_version": "1.6.1170.0", "identity_evidence": "EV-0109"},
        "source_scope": "Fixed official five-master xEdit view and prepared Skyrim.esm direct parser source; no target profile winner or live state.",
        "skyrim_esm_sha256": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
        "uesp_page": {"title": "Skyrim:Ill Met By Moonlight", "revision_id": 3628445, "timestamp": "2026-09-06T11:44:57Z", "url": "https://en.uesp.net/w/index.php?title=Skyrim:Ill_Met_By_Moonlight&oldid=3628445"},
        "pex_archive": {"filename": "Skyrim - Misc.bsa", "sha256": "ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d", "scope": "bounded base-Misc-BSA extraction only"},
        "captures": artifact_rows,
        "limits": ["No full active order or profile winner", "No clean level-one live session", "Not a vanilla reproduction", "PEX inspection is bounded classic PEX bytecode, not a complete decompilation"]
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    local_hashes = {row["artifact"]: row["sha256"] for row in artifact_rows}
    local_hashes[MANIFEST.relative_to(ROOT).as_posix()] = digest(MANIFEST)

    common = {
        "captured_utc": manifest["captured_utc"],
        "edition": "AE",
        "runtime": "Installed Steam SkyrimSE.exe ProductVersion 1.6.1170.0 is identified by EV-0109; no live game state was inspected.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": ["strict Python 3.12 dispatcher", "native SSEView five-master export", "tools.plugin_reader", "tools.papyrus_pex.py", "local tools.uesp revision capture"],
        "related_evidence": ["EV-0109", "EV-0214", "EV-0260"],
        "local_hashes": local_hashes,
        "artifact": f"private-local:{NOTE.relative_to(ROOT).as_posix()}",
        "sha256": digest(NOTE)
    }
    evidence["items"].extend([
        {**common, "id": "EV-0383", "kind": "source", "source": "Local UESP capture of Skyrim:Ill Met By Moonlight revision 3628445", "coverage": "Exact local page revision and raw JSON capture; secondary-source grounding only.", "result": "The page names Mathies or Sinding as quest givers and has no ReqLevel field. This does not establish the engine start gate or level-one availability."},
        {**common, "id": "EV-0384", "kind": "record", "source": "Native xEdit fixed official-five-master exports plus direct Skyrim.esm DA05 record captures", "coverage": "QUST 0002A49A DA05, SMQN 0005D331 DA05LocationCheckNode, and DIAL 0007933A DA05SindingStart; QUST is Update.esm winner within official-five scope.", "result": "The QUST is Start Game Enabled and has no exported GetLevel field. The location node uses GetEventData and GetStage, not GetLevel. The Sinding start DIAL's linked INFO has no function-index-80 condition."},
        {**common, "id": "EV-0385", "kind": "record", "source": "Hash-verified full Skyrim.esm GRUP ancestry join for DA05 DIAL/INFO records", "coverage": "38 DA05-owned DIALs, 51 linked INFO children, all 31,465 INFO records, and 30 INFOs with a direct DA05 QUST reference in CTDA/VMAD; source hash is fixed Skyrim.esm only.", "result": "Zero function-index-80 conditions occur in the 51 linked INFOs or in the 30 direct-DA05 INFO references. The Sinding and Mathies dialogue branches are included. This bounded source join does not prove topic/actor availability or profile winners."},
        {**common, "id": "EV-0386", "kind": "script", "source": "Bounded classic PEX 3.2 extraction from Skyrim - Misc.bsa", "coverage": "DA05 quest/sinding scripts and QF fragments plus INFO 00095585 TIF and its separate Bloated Man's Grotto quest fragments; raw PEX/disassembly hashes are in the manifest.", "result": "No textual GetLevel occurs in the bounded DA05 scripts. TIF__00095585 Fragment_0 calls DA05.SetStage(20) and sets PlayerTalkedToHunter. The owning INFO/alias availability and whether this starts a fresh DA05 remain unresolved; it is a distinct stage-writer lead, not a vanilla reproduction."}
    ])
    EVIDENCE.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    claims_text = CLAIMS.read_text(encoding="utf-8")
    if "CL-L221" in claims_text or "CL-L222" in claims_text:
        raise ValueError("Q67 claims already exist")
    claims_text += "\n| CL-L221 | Within the screened fixed official source path, DA05 QUST 0002A49A, SMQN 0005D331, 38 DA05-owned DIALs, 51 linked INFOs and 30 INFOs with a direct DA05 QUST reference contain no function-index-80 GetLevel condition. | supported within the scanned source scope | [EV-0384], [EV-0385], [EV-0214] | Natural level-one actor/topic availability, all indirect writers, a profile winner, and quest progress remain unobserved. |\n\n"
    claims_text += "| CL-L222 | INFO 00095585 under the separate dunBloatedMansGrottoQST has a bounded TIF Fragment_0 that calls DA05.SetStage(20) and sets PlayerTalkedToHunter; this is a separate stage writer whose INFO availability and fresh-state startup effect are unresolved. | supported for the mapped source callback | [EV-0386], [EV-0384] | It does not prove a level-one start or bypass; resolve INFO/alias conditions and the Quest.SetStage startup guard. |\n"
    CLAIMS.write_text(claims_text, encoding="utf-8", newline="\n")

    graph_text = GRAPH.read_text(encoding="utf-8")
    if "Q-0067 — DA05" in graph_text:
        raise ValueError("Q67 knowledge graph section already exists")
    graph_text += "\n## Q-0067 — DA05 Ill Met by Moonlight\n\n"
    graph_text += "Fixed official-five-master QUST/Story Manager exports and a source-hash-verified Skyrim.esm group join find no GetLevel condition in DA05 QUST 0002A49A, location node 0005D331, the 38 DA05-owned DIALs/51 linked INFOs, or the 30 INFOs with a direct DA05 reference [EV-0384, EV-0385, EV-0214]. UESP revision 3628445 names Mathies/Sinding but supplies no ReqLevel field [EV-0383]. Keep this as a bounded no-level-gate result; the fixed source scope is not a profile winner and no clean level-one dialogue/progression result exists [EV-0260]. The separate grotto INFO 00095585 TIF calls DA05.SetStage(20) and sets a quest-script property, but availability and fresh-state startup remain unresolved [EV-0386, CL-L222]. No shared native call, ActorValue, HitData field, callback owner, or serialization edge to the OBJ-2 armor XP path is supported [CL-L221].\n"
    GRAPH.write_text(graph_text, encoding="utf-8", newline="\n")

    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    add_frontier_items(frontier)
    FRONTIER.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"registered": ["EV-0383", "EV-0384", "EV-0385", "EV-0386"], "manifest": MANIFEST.relative_to(ROOT).as_posix(), "capture_count": len(artifact_rows), "new_frontier_items": ["Q-0068", "Q-0069"]}, indent=2))


if __name__ == "__main__":
    main()
