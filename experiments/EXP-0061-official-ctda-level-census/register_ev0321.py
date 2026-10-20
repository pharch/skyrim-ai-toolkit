from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TX = ROOT / ".local/alignment/transactions/TX-20261017-0007"
NOTE = TX / "EV-0321-note.md"
MANIFEST = TX / "EV-0321-capture-manifest.json"
REGISTER = ROOT / "research/EVIDENCE.json"
CAPTURES = (
    ".local/alignment/transactions/TX-20261017-0007/EV-0321-getlevel-census.json",
    ".local/alignment/transactions/TX-20261017-0007/EV-0321-getlevel-summary.json",
    ".local/alignment/transactions/TX-20261017-0007/EV-0321-progression-record-join.json",
    ".local/alignment/transactions/TX-20261017-0007/EV-0321-progression-condition-classification.json",
    ".local/alignment/transactions/TX-20261017-0007/EV-0321-official-winner-resolution.json",
    ".local/alignment/transactions/TX-20261017-0007/EV-0321-winning-qust-pack-summary.json",
    ".local/alignment/transactions/TX-20261017-0007/EV-0321-global-operands.json",
    ".local/alignment/transactions/TX-20261017-0007/EV-0321-da03-dialogue-join.json",
    ".local/alignment/transactions/TX-20261017-0007/uesp-daedras-best-friend.json",
    ".local/alignment/transactions/TX-20261017-0007/EV-0321-da03-qf-disassembly.raw.txt",
    ".local/alignment/transactions/TX-20261017-0007/EV-0321-da03-tif-extract.raw.txt",
    ".local/alignment/xedit-bridge/20261017T184545.306992Z/stdout.raw",
    ".local/alignment/xedit-bridge/20261017T190659.316267Z/stdout.raw",
    ".local/readiness/papyrus/QF_DA03Start_000D7939.pex",
)
EXPERIMENT_FILES = (
    "experiments/EXP-0061-official-ctda-level-census/README.md",
    "experiments/EXP-0061-official-ctda-level-census/hypothesis.md",
    "experiments/EXP-0061-official-ctda-level-census/predicted-outcomes.md",
    "experiments/EXP-0061-official-ctda-level-census/expected-discriminants.md",
    "experiments/EXP-0061-official-ctda-level-census/protocol.md",
    "experiments/EXP-0061-official-ctda-level-census/results.md",
    "experiments/EXP-0061-official-ctda-level-census/implications.md",
    "experiments/EXP-0061-official-ctda-level-census/scan_ctda.py",
    "experiments/EXP-0061-official-ctda-level-census/summarize_ctda.py",
    "experiments/EXP-0061-official-ctda-level-census/join_progression_records.py",
    "experiments/EXP-0061-official-ctda-level-census/classify_progression_join.py",
    "experiments/EXP-0061-official-ctda-level-census/resolve_official_winners.py",
    "experiments/EXP-0061-official-ctda-level-census/summarize_official_winners.py",
    "experiments/EXP-0061-official-ctda-level-census/resolve_global_operands.py",
    "experiments/EXP-0061-official-ctda-level-census/trace_da03_dialogue.py",
    "experiments/EXP-0061-official-ctda-level-census/register_ev0321.py",
)
TOOL_INPUTS = (
    "scripts/python_env.py",
    "scripts/research_state.py",
    "tools/plugin_reader.py",
    "tools/papyrus_pex.py",
    "tools/ae_target.py",
    "scripts/local_config.py",
    *EXPERIMENT_FILES,
)
NOTE_TEXT = """# EV-0321 — Full official GetLevel census and DA03Start guard-dialogue trace

- **Captured:** {captured}
- **Transaction:** TX-20261017-0007 / Q-0060
- **Lane:** read-only five-official-master source scan, targeted record join, bounded PEX disassembly, and local secondary-source grounding
- **Runtime identity:** Steam AE 1.6.1170.0 ProductVersion and executable SHA-256 match EV-0109. The fixed official-master order used here is a source-layer comparison, not the target's full active order or a profile winner.
- **Capture integrity:** EV-0321 records per-master hashes for the complete CTDA scan and rechecks them before the DIAL/INFO join. Raw scan outputs, query captures, UESP revision capture, QF PEX output, disassembly and the bounded TIF lookup are hashed in the manifest.

## Competing models and discriminant

- **H1:** function-index-80/GetLevel conditions occur only in the already-screened SMQN/DIAL/INFO families; no additional official signature adds a quest, encounter or access gate.
- **H2:** at least one other official signature adds a level condition tied to progression.
- **Discriminant:** complete five-master CTDA traversal with per-file hashes and parse counts, followed by source-owner joins for novel signatures and official-source-layer comparison.

## Direct observations

1. The parser completed 1,178,548 records and 117,272 32-byte CTDAs across Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm and Dragonborn.esm; 327 conditions use function index 80. Eight signatures contain hits: INFO 43, SMQN 15, ENCH 40, MGEF 50, PACK 1, PERK 36, QUST 57 and SPEL 85. The official-source-layer resolver retains 320 hits in its fixed order. It is not a profile winner query.
2. The candidate PACK `000E0D53 DA03StartGuardStartQuestGreet` contains `GetLevel >= 10` and `GetStage(DA03Start 000D7939) < 5`. The referenced DA03Start QUST has the serialized Start Game Enabled bit. The package PDTO points to DIAL `000E0D44 DA03StartGuardGreetBranchTopic`.
3. A hash-verified GRUP type-7 parent join maps DIAL `000E0D44` to one INFO child, `000E0D46`. That INFO also requires `GetLevel >= 10` and `GetStage(DA03Start) < 5`; it has four more CTDAs with raw function index 566 and parameters 7–10. Their function name is unresolved. The complete INFO subrecord list has no VMAD or direct quest-fragment subrecord.
4. `QF_DA03Start_000D7939` was extracted from `Skyrim - Misc.bsa` (archive SHA-256 `ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d`) and bounded-disassembled. `Fragment_27` calls `DA03.SetStage(5)`; `Fragment_29` adds 25 gold and sets the helper to stage 200; the other captured methods perform objective/stop operations. No call from INFO `000E0D46` to these methods is established. The exact `TIF__000E0D46` lookup found no supported stream in this bounded base-Misc-BSA extractor.
5. The local UESP capture is `Skyrim:A Daedra's Best Friend`, revision 3582964 (2026-06-28), URL `https://en.uesp.net/w/index.php?title=Skyrim:A_Daedra's_Best_Friend&oldid=3582964`, raw-capture SHA-256 `861cdbe0fc2239e77a0ff1410095eb88fac0275c47a61ed476bc9e8d2cb25a15`. It lists ReqLevel 10 and describes the Falkreath guard encounter pointing the player to Lod; it is secondary context, not proof of runtime dialogue behavior.

## Assessment and limits

H1 is falsified within the complete five-official-master CTDA source corpus and H2 is supported. PACK and QUST add conditions outside SMQN/DIAL/INFO, while the joined DA03Start package/INFO pair ties a level-10 condition to one guard-greeting path. This does not show that every start of DA03 or DA03Start is level-gated, nor that the guarded response itself calls `SetStage`. The INFO response uses a localized string ID in the record; the wording here comes from the bounded UESP capture.

No full active order, MO2 winner, live state transition, level-one access, or vanilla reproduction was observed. The TIF lookup covers only the tested base-Misc-BSA stream extractor; its no-hit is not an all-archive or loose-file negative. The next static discriminant is the full DA03Start-owned DIAL/INFO corpus, especially Lod's player-start topics and any matching VMAD/TIF fragment binding. No OBJ-2 armor/XP causal edge is supported.
"""


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0321" for row in register.get("items", [])):
        raise ValueError("EV-0321 already exists in research/EVIDENCE.json")
    for relative in CAPTURES:
        if not (ROOT / relative).is_file():
            raise FileNotFoundError(ROOT / relative)
    for relative in TOOL_INPUTS:
        if not (ROOT / relative).is_file():
            raise FileNotFoundError(ROOT / relative)

    captured = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    TX.mkdir(parents=True, exist_ok=True)
    NOTE.write_text(NOTE_TEXT.format(captured=captured), encoding="utf-8")
    artifact_paths = {ROOT / relative for relative in (*CAPTURES, *TOOL_INPUTS)} | {NOTE}
    artifact_rows = [
        {"artifact": path.relative_to(ROOT).as_posix(), "size_bytes": path.stat().st_size, "sha256": digest(path)}
        for path in sorted(artifact_paths)
    ]
    census = json.loads((TX / "EV-0321-getlevel-census.json").read_text(encoding="utf-8"))
    dialogue = json.loads((TX / "EV-0321-da03-dialogue-join.json").read_text(encoding="utf-8"))
    manifest = {
        "evidence_id": "EV-0321",
        "transaction_id": "TX-20261017-0007",
        "frontier_id": "Q-0060",
        "captured_utc": captured,
        "target_identity": {
            "edition": "AE",
            "distribution": "Steam",
            "product_version": "1.6.1170.0",
            "executable_sha256": "c434208894f07f604b852f29b8edc3a58c4de63de783373733e72b2b73f33be9",
            "identity_evidence": "EV-0109",
        },
        "official_sources": census.get("source_files", []),
        "query_scope": "Complete read-only five-official-master source census; fixed official-source-layer comparison; targeted Skyrim.esm PACK/QUST and GRUP type-7 DIAL/INFO source join; bounded base-Misc-BSA PEX extraction/disassembly.",
        "profile_and_runtime_limit": "No complete target active order, MO2 winner, live Observer session, quest-state transition, level-one access, or vanilla reproduction was observed.",
        "dialogue_source_layer": {
            "source_order_scope": dialogue["source_order_scope"],
            "record_counts_by_file_walk": dialogue["source_record_counts_by_file_walk"],
            "topic_form_id": dialogue["PDTO_topic_form_id"],
            "info_child_count": dialogue["INFO_winning_child_count"],
            "info_parent_join": dialogue["INFO_parent_join"],
        },
        "uesp_page": {
            "title": "Skyrim:A Daedra's Best Friend",
            "revision_id": 3582964,
            "timestamp": "2026-06-28T23:23:18Z",
            "url": "https://en.uesp.net/w/index.php?title=Skyrim:A_Daedra's_Best_Friend&oldid=3582964",
            "raw_capture": ".local/alignment/transactions/TX-20261017-0007/uesp-daedras-best-friend.json",
            "raw_capture_sha256": "861cdbe0fc2239e77a0ff1410095eb88fac0275c47a61ed476bc9e8d2cb25a15",
        },
        "pex_archive": {
            "filename": "Skyrim - Misc.bsa",
            "sha256": "ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d",
            "extracted_script": "QF_DA03Start_000D7939.psc",
            "extracted_pex_sha256": "cc9642c5dba648b018cae5af4d661c1cd13d7f38289bf32a944fa4e2af3520df",
            "tif_lookup_scope": "No supported TIF__000E0D46 stream in the tested bounded base-Misc-BSA extractor; not an all-archive/loose-file negative.",
        },
        "related_evidence": ["EV-0109", "EV-0214", "EV-0039", "EV-0300", "EV-0306", "EV-0260"],
        "tool_inputs_sha256": {relative: digest(ROOT / relative) for relative in TOOL_INPUTS},
        "artifacts": artifact_rows,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    local_hashes = {row["artifact"]: row["sha256"] for row in artifact_rows}
    local_hashes[MANIFEST.relative_to(ROOT).as_posix()] = digest(MANIFEST)
    evidence: dict[str, Any] = {
        "id": "EV-0321",
        "kind": "record",
        "source": "Complete five-official-master GetLevel CTDA census, targeted DA03Start guard package/dialogue source join, bounded QF PEX disassembly, and local UESP revision capture.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0007/EV-0321-note.md",
        "sha256": digest(NOTE),
        "captured_utc": captured,
        "edition": "AE",
        "runtime": "Steam SkyrimSE.exe ProductVersion 1.6.1170.0 and SHA-256 are separately identified in EV-0109; all five official master hashes are in the EV-0321 capture manifest.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "scripts/python_env.py strict dispatcher",
            "tools/plugin_reader.py and EXP-0061 source-bound census/GRUP join scripts",
            "tools/papyrus_pex.py on the bounded base Misc BSA stream",
            "Local UESP database page capture at revision 3582964",
        ],
        "coverage": "Complete five-official-master CTDA scan and fixed official-source-layer comparison; targeted DA03Start PACK/QUST and DIAL/INFO source join; bounded base-Misc-BSA QF PEX extraction and TIF lookup. No full active order or runtime transition.",
        "result": "The complete census finds GetLevel outside the known SMQN/DIAL/INFO signatures, falsifying Q60-H1 and supporting Q60-H2 within the source corpus. PACK 000E0D53 and linked INFO 000E0D46 both require GetLevel >=10 and DA03Start stage <5. The INFO has four additional unresolved function-566 conditions and no VMAD/direct fragment field. QF disassembly contains no captured call from that INFO to DA03.SetStage; whether Lod's separate direct topics permit a level-one start remains open.",
        "related_evidence": ["EV-0109", "EV-0214", "EV-0039", "EV-0300", "EV-0306", "EV-0260"],
        "local_hashes": local_hashes,
    }
    register["items"].append(evidence)
    REGISTER.write_text(json.dumps(register, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0321", "artifact_count": len(artifact_rows), "sha256": digest(NOTE), "manifest": MANIFEST.relative_to(ROOT).as_posix()}, indent=2))


if __name__ == "__main__":
    main()
