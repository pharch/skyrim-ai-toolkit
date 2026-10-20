from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TX_ID = "TX-20261018-0004"
TX = ROOT / ".local/alignment/transactions" / TX_ID
NOTE = TX / "EV-0387-0390-we13-source-screen.md"
MANIFEST = TX / "EV-0387-0390-capture-manifest.json"
EVIDENCE = ROOT / "research/EVIDENCE.json"
FRONTIER = ROOT / "research/FRONTIER.json"
CLAIMS = ROOT / "research/CLAIMS.md"
MECHANISMS = ROOT / "research/MECHANISMS.md"
GRAPH = ROOT / "research/KNOWLEDGE_GRAPH.md"

CAPTURES = [
    ".local/alignment/transactions/TX-20261018-0004/we13-parent-scan.json",
    ".local/alignment/transactions/TX-20261018-0004/we13-source-scan.json",
    ".local/alignment/transactions/TX-20261018-0004/we-trigger-placements.json",
    ".local/alignment/transactions/TX-20261018-0004/WETriggerScript.pex",
    ".local/alignment/transactions/TX-20261018-0004/WETriggerScript.disassembly.raw",
    ".local/alignment/transactions/TX-20261018-0004/WEScript.pex",
    ".local/alignment/transactions/TX-20261018-0004/WEScript.disassembly.raw",
    ".local/alignment/transactions/TX-20261018-0004/WEParentScript.pex",
    ".local/alignment/transactions/TX-20261018-0004/WEParentScript.disassembly.raw",
    ".local/alignment/transactions/TX-20261018-0004/QF_WE13_0009F32F.pex",
    ".local/alignment/transactions/TX-20261018-0004/QF_WE13_0009F32F.disassembly.raw",
    ".local/alignment/xedit-bridge/20261018T134544.245146Z/stdout.raw",
]
for stamp in (
    "20261018T135534.995326Z",
    "20261018T135832.692085Z",
    "20261018T140101.799697Z",
    "20261018T140514.852391Z",
    "20261018T141352.130361Z",
    "20261018T141650.426014Z",
    "20261018T141949.084986Z",
):
    CAPTURES.extend([
        f".local/alignment/xedit-native/{stamp}/native-result.json",
        f".local/alignment/xedit-native/{stamp}/native-records.tsv",
    ])

INPUTS = [
    "experiments/EXP-0119-we13-gate-layer-screen/README.md",
    "experiments/EXP-0119-we13-gate-layer-screen/hypothesis.md",
    "experiments/EXP-0119-we13-gate-layer-screen/protocol.md",
    "experiments/EXP-0119-we13-gate-layer-screen/expected-discriminants.md",
    "experiments/EXP-0119-we13-gate-layer-screen/results.md",
    "experiments/EXP-0119-we13-gate-layer-screen/implications.md",
    "experiments/EXP-0119-we13-gate-layer-screen/scan_we13_sources.py",
    "experiments/EXP-0119-we13-gate-layer-screen/extract_we_trigger_placements.py",
    "experiments/EXP-0119-we13-gate-layer-screen/register_q68.py",
    "scripts/research_state.py",
    "scripts/research_transactions.py",
    "tools/plugin_reader.py",
    "tools/papyrus_pex.py",
    "tools/xedit_bridge.py",
]


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def metadata(paths: list[str]) -> list[dict[str, Any]]:
    rows = []
    for relative in paths:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(relative)
        rows.append({
            "artifact": relative,
            "size_bytes": path.stat().st_size,
            "sha256": digest(path),
        })
    return rows


NOTE_TEXT = """# EV-0387–EV-0390 — WE13 source screen

- Transaction: TX-20261018-0004 / Q-0068
- Target identity: Steam AE 1.6.1170.0 is established separately by EV-0109. The exports and scan use the fixed official five-master scope; no active-profile winner or live state is established.
- Archive identity: Skyrim - Misc.bsa, SHA-256 ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d; four PEX files are a bounded extraction.

## Competing models and outcome

- Q68-H1 is supported within the two mapped Story Manager paths: both selectors converge on WE13 QUST 0009F32F, whose serialized top-level condition is GetLevel >= LevelGateTrollCave (12). This does not exclude an unscanned direct caller.
- Q68-H2 remains proposed: no independent direct WE13 start/stage path was identified in the fixed five-master exact-reference scan or four linked PEX files, but physical cave access, other archives, loose scripts, native writers, and profile-specific overrides were not tested.
- Q68-H3 is supported: Story Manager scheduling, WE13 eligibility, alias fill, actor spawn, and physical cave access are distinct transitions; this record trace cannot establish cave accessibility.

## Direct evidence

1. The ordinary path is WEStart/WERoadStart -> SMEN 0001379A -> SMBN WEQuestNode 000896A8 -> SMQN WEQuests 0004A601 -> WE13 QUST 0009F32F. The Solstheim path is SMEN 0001379A -> SMBN DLC2WENode 0401E7D9 -> SMBN DLC2WERegionNorthNode 0401E7DF -> SMQN DLC2WERegionNorthQuestNode 0401E7E1 -> the same WE13 QUST. Solstheim additionally requires WEEnabled, DLC2 event keywords, and DLC2RegionNorthLocation.
2. WE13 has ENAM SCPT, the GetLevel condition from EV-0321, and trigger/location/troll/spriggan aliases. Four tested classic PEX 3.2 files show trigger event dispatch; WEScript and WEParentScript do not directly call StartQuest or SetStage; the WE13 startup fragment is a no-op and another fragment cleans up encounter actors.
3. The fixed-five-master scan verified all five plugin hashes, parsed 1,178,548 records, and retained 12 raw WE13 FormID-byte candidates. Native field exports validate the two Story Manager selectors. Other candidates are the QUST VMAD and two quest-owned PACK records. The scan does not cover every Papyrus EditorID lookup or native caller.
4. The placement extractor found 167 direct REFR WETriggerScript source records resolving to 158 logical references: 148 WETrigger, 7 WETriggerOnLoad, and 12 DLC2WETrigger. It decoded all 167 REFR VMADs after schema-order correction. Four base ACTIs define the event keywords; instance properties select load and road-event behavior. Flags are 0x400 and EV-0275 supplies the Persistent/Initially Disabled mapping. Placement does not prove loaded state or cave access.

## Boundaries and cross-domain result

The five-master exports are not profile winners. The source scans do not cover every archive, loose file, or native writer. No ordinary level-one test, quest state, stage, alias fill, encounter spawn, or physical cave traversal was observed; EV-0260 records the unavailable full order, clean save, and observer. This is mechanism inference, not a vanilla reproduction. No OBJ-1/OBJ-2 edge is justified: no shared native call, ActorValue, HitData field, callback owner, or serialized state links WE13 to armor XP.
"""


def main() -> int:
    TX.mkdir(parents=True, exist_ok=True)
    if not NOTE.exists():
        NOTE.write_text(NOTE_TEXT, encoding="utf-8")
    captured = metadata(CAPTURES)
    inputs = metadata(INPUTS)
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest = {
        "evidence_ids": ["EV-0387", "EV-0388", "EV-0389", "EV-0390"],
        "transaction_id": TX_ID,
        "frontier_id": "Q-0068",
        "captured_utc": stamp,
        "target": {"distribution": "Steam", "product_version": "1.6.1170.0", "identity_evidence": "EV-0109"},
        "source_scope": "Fixed official five-master source view and seven native SSEView exports; no profile winner or live query.",
        "official_master_hashes": {
            "Dawnguard.esm": "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4",
            "Dragonborn.esm": "5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b",
            "HearthFires.esm": "ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97",
            "Skyrim.esm": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
            "Update.esm": "c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9",
        },
        "pex_archive": {"filename": "Skyrim - Misc.bsa", "sha256": "ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d", "scope": "bounded four-file extraction only"},
        "captures": captured,
        "inputs": inputs,
        "limits": ["No complete active profile order or profile winner", "No clean level-one live session", "Not a vanilla reproduction", "No complete archive or loose-script census", "Physical cave access is not established"],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    local_hashes = {row["artifact"]: row["sha256"] for row in captured + inputs}
    local_hashes[MANIFEST.relative_to(ROOT).as_posix()] = digest(MANIFEST)
    common = {
        "captured_utc": stamp,
        "edition": "AE",
        "runtime": "Steam SkyrimSE.exe ProductVersion 1.6.1170.0 identity is EV-0109; no live game state was inspected.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": ["strict Python 3.12 dispatcher", "native SSEView official-five-master export", "tools.plugin_reader", "bounded classic PEX extractor", "source-hash-verified FormID/VMAD scanner"],
        "related_evidence": ["EV-0109", "EV-0214", "EV-0260", "EV-0275", "EV-0321"],
        "local_hashes": local_hashes,
        "artifact": f"private-local:{NOTE.relative_to(ROOT).as_posix()}",
        "sha256": digest(NOTE),
    }
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    existing = {item.get("id") for item in evidence["items"]}
    if existing.intersection({"EV-0387", "EV-0388", "EV-0389", "EV-0390"}):
        raise ValueError("one or more Q68 evidence IDs already exist")
    evidence["items"].extend([
        {**common, "id": "EV-0387", "kind": "record", "source": "Seven native SSEView xEdit exports in the fixed official five-master scope plus direct Skyrim.esm WE13 capture", "coverage": "QUST WE13 0009F32F; SMEN 0001379A; SMBN WEQuestNode 000896A8; SMQN WEQuests 0004A601; and three Dragonborn DLC2 event/region nodes. No target profile winner.", "result": "The ordinary WEStart/WERoadStart route and Solstheim DLC2 event/location route both select WE13 QUST 0009F32F. Its serialized top-level GetLevel >= LevelGateTrollCave condition is 12. The Solstheim branch is a second scheduling context, not a demonstrated bypass."},
        {**common, "id": "EV-0388", "kind": "record", "source": "Hash-verified fixed official-five-master record/reference census", "coverage": "1,178,548 parsed records across Dawnguard.esm, Dragonborn.esm, HearthFires.esm, Skyrim.esm, and Update.esm; raw FormID-byte candidates and group ancestry are preserved.", "result": "The scan found 12 raw WE13 FormID-byte candidates: Story Manager selector records, the QUST VMAD self-reference, and quest-owned PACK references. Native exports validate the selector semantics. This exact-reference census does not cover every Papyrus EditorID lookup, loose script, archive, native writer, or active profile."},
        {**common, "id": "EV-0389", "kind": "placement", "source": "Hash-verified official-master VMAD attachment and trigger-placement extraction", "coverage": "167 direct REFR WETriggerScript source records resolved to 158 logical refs; fixed five-master order; base ACTI keyword properties and all REFR VMADs decoded.", "result": "Source placements use WETrigger, WETriggerOnLoad, or DLC2WETrigger bases and distribute across Tamriel, Solstheim, or four WarehousePrefabs references. Four base ACTIs define event keywords; instance properties select load and road behavior. Flags 0x400 map to Persistent without Initially Disabled under EV-0275. This does not show loaded state, physical cave gating, player access, or a profile winner."},
        {**common, "id": "EV-0390", "kind": "script", "source": "Bounded classic PEX 3.2 extraction from Skyrim - Misc.bsa", "coverage": "WETriggerScript, WEScript, WEParentScript, and QF_WE13_0009F32F; bytecode/disassembly hashes preserved. Archive SHA-256 is in the capture manifest.", "result": "WETriggerScript sends Story Manager events; the other three linked file bodies show no direct StartQuest or SetStage writer, and the WE13 startup fragment is a no-op while another fragment cleans up encounter actors. This is a four-file linked-script screen, not a complete archive or loose-script negative."},
    ])
    EVIDENCE.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    claims = CLAIMS.read_text(encoding="utf-8")
    if any(claim in claims for claim in ("CL-L223", "CL-L224", "CL-L225")):
        raise ValueError("one or more Q68 claims already exist")
    claims += "\n\n| CL-L223 | In the fixed official-five-master source scope, the mapped ordinary and Solstheim Story Manager event paths both select WE13 QUST 0009F32F, whose top-level condition is GetLevel >= LevelGateTrollCave (12); no direct bypass is identified in the bounded exact-reference and linked-PEX screens. | supported for mapped source paths | [EV-0387], [EV-0388], [EV-0390], [EV-0321], [EV-0214] | No global start-path negative follows; active profile winner, other archives/loose scripts/native callers, actual quest startup, and alias fill remain unverified. |\n"
    claims += "\n| CL-L224 | In the four bounded linked PEX files, WETriggerScript dispatches Story Manager events and no direct StartQuest or SetStage writer is identified; QF_WE13 startup is a no-op and its other fragment performs encounter cleanup. | supported for the tested PEX files | [EV-0390] | This does not cover all archive or loose PEX files, native callers, or runtime-indirect paths. |\n"
    claims += "\n| CL-L225 | The fixed-five-master placement extraction resolved 167 direct REFR WETriggerScript source records to 158 logical references using three trigger base families and decoded their event properties; the records are persistent under the EV-0275 bit mapping. | supported for the source placement extraction | [EV-0389], [EV-0275] | Source placement and persistence flags do not prove loaded state, physical cave accessibility, player reachability, or a profile winner. |\n"
    CLAIMS.write_text(claims.rstrip() + "\n", encoding="utf-8")

    mechanisms = MECHANISMS.read_text(encoding="utf-8")
    if "M-0092" in mechanisms:
        raise ValueError("M-0092 already exists")
    mechanisms += "\n\n## M-0092 — WE13 Story Manager encounter scheduling and quest gate\n\n"
    mechanisms += "The ordinary WEStart/WERoadStart route reaches SMEN 0001379A -> SMBN WEQuestNode 000896A8 -> SMQN WEQuests 0004A601 -> WE13 QUST 0009F32F. A second Solstheim route reaches SMEN 0001379A -> SMBN DLC2WENode 0401E7D9 -> SMBN DLC2WERegionNorthNode 0401E7DF -> SMQN DLC2WERegionNorthQuestNode 0401E7E1 -> the same WE13 QUST. The regional branch checks WEEnabled, DLC2 event keywords, and DLC2RegionNorthLocation; it changes scheduling context, not the selected QUST's serialized GetLevel >= LevelGateTrollCave (12) condition [EV-0387], [EV-0321]. The four tested linked PEX files show trigger-event dispatch and no direct quest start/stage writer; the fixed official-master scan and trigger-placement extraction bound that source map [EV-0388], [EV-0389], [EV-0390]. This supports a level-12 condition on the mapped selector paths, not a global claim that WE13 cannot be started or aliased by another route. Physical cave access and clean level-one state remain unobserved [EV-0260]. No edge to armor XP is supported: no shared call, ActorValue, HitData field, callback owner, or serialized state is identified [CL-L223].\n"
    MECHANISMS.write_text(mechanisms, encoding="utf-8")

    graph = GRAPH.read_text(encoding="utf-8")
    if "## Q-0068 — WE13" in graph:
        raise ValueError("Q-0068 graph section already exists")
    graph += "\n\n## Q-0068 — WE13 troll-cave event gate\n\n"
    graph += "Both mapped Story Manager event branches, including the Solstheim regional path, select WE13 QUST 0009F32F, whose top-level GetLevel condition is >= LevelGateTrollCave (12) [EV-0387], [EV-0321]. The fixed five-master exact-reference screen and the four tested linked PEX files identify no independent direct start/stage writer within their scope [EV-0388], [EV-0390]. The 167 direct REFR WETriggerScript source records resolve to 158 logical refs; their event keywords and persistence flags describe dispatch sources, not loaded state or cave access [EV-0389], [EV-0275]. Keep global bypass and physical access unresolved; Q-0070 retains the exact level-one test, while Q-0069 is the next ready static question [EV-0260]. No OBJ-1/OBJ-2 edge is justified because no shared native call, ActorValue, HitData field, callback owner, or serialized state connects WE13 scheduling to armor XP [CL-L223].\n"
    GRAPH.write_text(graph, encoding="utf-8")

    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    items = frontier["items"]
    current = next(item for item in items if item.get("id") == "Q-0068")
    if current.get("status") != "in_progress":
        raise ValueError("Q-0068 is not the active in-progress frontier item")
    if any(item.get("id") == "Q-0070" for item in items):
        raise ValueError("Q-0070 already exists")
    current["question"] = "Within the fixed official source scope, do all mapped WE13 event selectors converge on its level-12 QUST condition, and what remains unresolved about direct starts and physical cave access?"
    current["next_action"] = "Close Q68 as a bounded source map with EV-0387–EV-0390; preserve direct-start and cave-access unknowns in Q70, then continue with Q69."
    current["cross_source_assessment"] = "Both mapped Story Manager routes select WE13 QUST 0009F32F with GetLevel >= 12; bounded exact-reference and four-file PEX screens found no separate direct start/stage writer. Trigger placements identify event senders, not loaded state or physical cave access. Keep the clean level-one discriminator as Q70; do not infer an OBJ-2 edge."
    current["linked_claims"] = list(dict.fromkeys([*current.get("linked_claims", []), "CL-L223", "CL-L224", "CL-L225"]))
    current["evidence"] = list(dict.fromkeys([*current.get("evidence", []), "EV-0387", "EV-0388", "EV-0389", "EV-0390"]))
    current["successors"] = list(dict.fromkeys([*current.get("successors", []), "Q-0069", "Q-0070"]))
    for hypothesis in current["hypotheses"]:
        if hypothesis["id"] == "Q68-H1":
            hypothesis.update(status="supported", evidence=["EV-0387", "EV-0321"], model="Both mapped Story Manager paths select WE13 QUST 0009F32F, whose top-level condition requires GetLevel >= 12; direct unscanned start routes and actual alias fill remain unresolved.")
        elif hypothesis["id"] == "Q68-H2":
            hypothesis.update(status="proposed", evidence=["EV-0388", "EV-0390"], model="A different direct-start or physical-access path may expose related content below level 12; bounded source screens do not cover all archives, loose files, native callers, active winners, or cave traversal.")
        elif hypothesis["id"] == "Q68-H3":
            hypothesis.update(status="supported", evidence=["EV-0387", "EV-0389"], model="The QUST condition and trigger placements describe encounter scheduling/eligibility; neither proves that a physical cave entrance is blocked.")
    current["attempts"].append({
        "action_key": "q68-bounded-source-screen-registration",
        "outcome": "EV-0387–EV-0390 register the native selector map, fixed-source reference scan, trigger placements, and bounded linked PEXs. The mapped selectors converge on WE13's level-12 condition; source triggers do not establish physical access.",
        "evidence": ["EV-0387", "EV-0388", "EV-0389", "EV-0390"],
        "new_discriminant": "A clean level-one ordinary-trigger test must record player level, WE13 running/stage state and aliases, encounter actors, and physical cave traversal separately; include no-trigger and ordinary-trigger controls on the exact verified target.",
        "recorded_utc": stamp,
    })
    q69 = next(item for item in items if item.get("id") == "Q-0069")
    q69["next_action"] = "Resolve INFO 00095585 conditions and its parent DIAL/owning QUST with direct file records and native five-master fields; then compare its SetStage(20) callback to the mapped GOG Quest.SetStage startup guard and identify what remains for a clean level-one test."
    q69["cross_source_assessment"] = "The TIF body proves only a DA05.SetStage(20) request. INFO availability, owning-quest state, fresh-state startup, player reachability, and profile winner remain unobserved. The Grotto route is independent of WE13 and has no supported causal link to OBJ-2."
    items.append({
        "id": "Q-0070",
        "objective": "OBJ-1",
        "kind": "experiment",
        "status": "blocked_environment",
        "question": "On a verified Steam AE level-one state, do ordinary WE trigger exposure, WE13 quest/alias state, encounter spawn, and physical troll-cave access separate into independently observable outcomes?",
        "hypotheses": [
            {"id": "Q70-H1", "model": "Below level 12, ordinary trigger exposure leaves WE13 stopped or unfilled, while physical cave access may still be possible.", "predicted_discriminant": "A read-only capture after a no-trigger control and ordinary trigger exposure records level 1, WE13 running/stage state, alias targets, and nearby encounter actors; a separate natural traversal records cave access.", "status": "proposed", "evidence": ["EV-0387", "EV-0389", "EV-0260"]},
            {"id": "Q70-H2", "model": "At least one natural level-one route starts or fills WE13 or exposes the same encounter content without changing level.", "predicted_discriminant": "The clean run shows a naturally caused running/stage/alias/actor transition at level 1 with no forced stage, injected script, or plugin change.", "status": "proposed", "evidence": ["EV-0260", "EV-0387"]},
            {"id": "Q70-H3", "model": "Physical cave access is independent of WE13 encounter scheduling and can be demonstrated while the quest remains stopped.", "predicted_discriminant": "The level-one player enters the relevant physical cave by ordinary traversal, records its exact location/door route, and observes WE13 remains stopped with no relevant aliases or spawned encounter.", "status": "proposed", "evidence": ["EV-0260", "EV-0389"]}
        ],
        "methods": [
            "Verify Steam SkyrimSE.exe ProductVersion 1.6.1170.0 and the complete exact target order; if MO2-managed, use its selected profile's full plugins.txt.",
            "Use a clean disposable numeric level-one save and a read-only observer capable of capturing player level, WE13 running/stage state, relevant aliases, trigger events, and actor presence.",
            "Run a no-trigger control, then ordinary trigger exposure without console forcing, injected scripts, or plugin changes; record numeric level and exact quest/alias/actor changes.",
            "Separately identify the relevant physical cave location from source records and attempt natural traversal while preserving the same state capture."
        ],
        "blocked_by": [],
        "evidence": ["EV-0109", "EV-0260", "EV-0321", "EV-0387", "EV-0389"],
        "priority": 1.0,
        "information_gain": 0.99,
        "next_action": "EV-0260 records no verified complete target order, clean level-one save, or deployed read-only Observer. Keep this discriminator blocked while pursuing available source research; map a concrete cave entrance and ensure read-only state capture can see WE13 running/stage/aliases plus player level.",
        "linked_claims": [],
        "successors": [],
        "attempts": [],
        "cross_source_assessment": "No live result exists. This is a vanilla-candidate protocol only; it is not validation until performed without diagnostic intervention on the exact verified target and complete order."
    })
    frontier["session_checkpoint"] = {
        "timestamp_utc": stamp.replace("+00:00", "Z"),
        "task": "Q-0068 source map registered; Q-0069 is next ready source research; Q-0070 preserves the separate level-one live discriminator.",
        "next_action": q69["next_action"],
    }
    frontier["last_session_checkpoint"] = {
        "recorded_utc": stamp,
        "next_action": q69["next_action"],
        "active_process": "TX-20261018-0004 is ready to close; Q-0069 is next, with Q-0070 environment-blocked on exact level-one access evidence.",
    }
    frontier["next_action"] = q69["next_action"]
    FRONTIER.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "registered": ["EV-0387", "EV-0388", "EV-0389", "EV-0390"],
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "capture_count": len(captured),
        "input_count": len(inputs),
        "new_frontier_item": "Q-0070",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
