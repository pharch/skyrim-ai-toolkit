#!/usr/bin/env python3
"""Register the bounded receiver-site and PlayerCharacter cleanup follow-up."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TX = ROOT / ".local/alignment/transactions/TX-20261017-0009"
GHIDRA = ROOT / ".local/ghidra"
CAPTURES = {
    "20261017T221945Z": ("0x6BA492", "address_context_query", "488ed4bd74f43d47bf4494b67b4e69fb32b1fe35cfe2b3b175e3075bf752f2f7"),
    "20261017T222051Z": ("0x6BA952", "address_context_query", "8be52bd1df739b8ca01b9af8a6e92d80ba99af2d9f264aceef14c672e470dad4"),
    "20261017T222312Z": ("0x72FD60", "direct_call_edge_census", "586d2f227bd0659b3f745b27823f29f6e914ed86d1bd684f42c3d2be749fe76a"),
}
BINARY_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    metadata: list[dict] = []
    local_hashes: dict[str, str] = {}
    for stamp, (address, mode, expected_stdout_sha) in CAPTURES.items():
        stdout = GHIDRA / f"gog-query-{stamp}.stdout.raw"
        meta_path = GHIDRA / f"gog-query-{stamp}.meta.json"
        if not stdout.is_file() or not meta_path.is_file():
            raise SystemExit(f"missing raw Ghidra capture for {stamp}")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        checks = meta.get("checks", {})
        if (
            meta.get("analysis_binary_sha256") != BINARY_SHA
            or meta.get("exit_code") != 0
            or (meta.get("requested_address_rva") or meta.get("requested_rva")) != address
            or meta.get("query_mode") != mode
            or meta.get("stdout_sha256") != expected_stdout_sha
            or meta.get("read_only") is not True
            or meta.get("auto_analysis_disabled") is not True
            or checks.get("program_identity_matches_gog_binary") is not True
            or checks.get("script_no_error") is not True
        ):
            raise SystemExit(f"query identity or expected component failed: {stamp}")
        if mode == "address_context_query":
            if checks.get("address_context_complete") is not True:
                raise SystemExit(f"address context incomplete: {stamp}")
        elif checks.get("direct_call_edge_scan") is not True or checks.get("decompilation") is not True:
            raise SystemExit(f"function census incomplete: {stamp}")
        local_hashes[stdout.relative_to(ROOT).as_posix()] = sha(stdout)
        local_hashes[meta_path.relative_to(ROOT).as_posix()] = sha(meta_path)
        metadata.append(meta)

    note = TX / "EV-0325-note.md"
    write(note, """# EV-0325 — Trap receiver ActorValue operations and PlayerCharacter cleanup body

## Build identity and method

The queried program is the existing GOG Skyrim AE 1.6.1179.0 Ghidra project. The analysis executable SHA-256 is `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. Each query used the project in `-noanalysis -readOnly` mode; the capture manifest records stdout and metadata hashes. No Steam RVA is inferred. Installed Steam AE 1.6.1170.0 remains a distinct target under EV-0109.

## Direct observations

- At GOG RVA `0x6BA492` in `FUN_1406b9df0`, the receiver is Actor's `+0xB8` ActorValueOwner subobject, virtual byte offset `+0x18` (slot 3), and the argument is `0x18` (Health). The pinned CommonLibSSE-NG declarations in EV-0261 map this slot to `GetBaseActorValue`; the call is a Health read, not a skill-credit sink.
- At GOG RVA `0x6BA952`, the same subobject dispatches byte offset `+0x30` (slot 6) with modifier `2`, ActorValue `0x1A` (Stamina), and a computed value. EV-0261's pinned declarations map this to `RestoreActorValue`; this is Stamina damage/resource mutation, not AV11/AV12 skill progress.
- The fresh census of `FUN_14072fd60`, the PlayerCharacter cleanup body reached by the receiver-side release chain traced in EV-0319, completed with 108 direct edges and 8 indirect call sites. Its captured body contains no direct Actor slot `0xF7` / byte offset `0x7B8` call and no direct edge to the mapped skill-progress routine. The eight indirect calls and descendants of its direct calls remain unresolved; this does not establish a global no-award result.
- The receiver's separate direct `UseSkill` site at `0x6BA19C` remains the AV15 Sneak path already mapped by EV-0295/EV-0324. These fresh callsite contexts do not change the bounded wrapper-bypass comparison in EV-0324.

## Assessment and limits

The fresh evidence confirms the prior EXP-0045 classification of the Health and Stamina calls and narrows the PlayerCharacter cleanup body: no direct skill-progress dispatch is present in its 108-edge census, while 8 indirect sites remain. No AV11/AV12 award is identified by these specific queries, but no complete transitive audit, positive final damage, effective protection, Steam behavior, raw AVSK delta, active-profile winner, or vanilla reproduction is established. The physical-trap route remains a candidate only.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    manifest = TX / "EV-0325-capture-manifest.json"
    write(manifest, json.dumps({
        "evidence_id": "EV-0325",
        "captured_utc": "2026-10-17T22:23:52+00:00",
        "analysis_binary": {"product_version": "1.6.1179.0", "sha256": BINARY_SHA, "distribution": "GOG"},
        "query_metadata": [{
            "requested_address_or_rva": item.get("requested_address_rva") or item.get("requested_rva"),
            "query_mode": item.get("query_mode"),
            "stdout_sha256": item.get("stdout_sha256"),
            "metadata_artifact": item.get("metadata_artifact"),
            "checks": item.get("checks"),
            "read_only": item.get("read_only"),
            "auto_analysis_disabled": item.get("auto_analysis_disabled"),
            "ok": item.get("ok"),
        } for item in metadata],
        "local_hashes": local_hashes,
    }, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = sha(manifest)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0325" for row in evidence["items"]):
        raise SystemExit("EV-0325 already exists; refusing duplicate registration")
    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0325",
        "kind": "native",
        "source": "Fresh read-only GOG instruction-context queries for two ActorValueOwner receiver sites and a complete call-edge census of the PlayerCharacter cleanup body.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0009/EV-0325-note.md",
        "sha256": sha(note),
        "runtime": "GOG Skyrim AE 1.6.1179.0 static project, executable SHA-256 " + BINARY_SHA + ". Steam AE 1.6.1170.0 is separate; no GOG RVA is transferred.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py existing GOG project through strict dispatcher with -noanalysis -readOnly", "EV-0261 pinned CommonLibSSE-NG ActorValueOwner and ActorValues declarations"],
        "coverage": "Exact receiver call arguments at GOG RVAs 0x6BA492 and 0x6BA952, plus FUN_14072fd60 direct/indirect call census and decompilation. No complete transitive callgraph or live test.",
        "result": "The ActorValueOwner sites read base Health and restore Stamina damage. The PlayerCharacter cleanup body has 108 direct edges and 8 indirect sites, with no direct slot-0xF7 skill-progress dispatch identified. This narrows the cleanup branch but does not prove zero armor XP.",
        "related_evidence": ["EV-0324", "EV-0295", "EV-0315", "EV-0319", "EV-0261", "EV-0260"],
        "local_hashes": local_hashes,
    })
    evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "Q-0063" for row in frontier["items"]):
        raise SystemExit("Q-0063 already exists; refusing duplicate frontier item")
    frontier["items"].append({
        "id": "Q-0063",
        "objective": "OBJ-1",
        "kind": "mechanism",
        "status": "open",
        "question": "Does any ordinary Dawnguard rumor, Isran, or Fort Dawnguard callback start DLC1VQ01/Awakening below level 10, or does the level-10 Durak Story Manager helper remain the only known natural entry route?",
        "hypotheses": [
            {
                "id": "Q63-H1",
                "model": "At least one ordinary dialogue or arrival callback can start or advance the actual Dawnguard questline at level 1 without the Durak level-10 helper.",
                "predicted_discriminant": "Hash-identified Dawnguard DIAL/INFO VMAD and attached PEX bodies contain a reachable direct Start/SetStage or equivalent VQ01 transition with no GetLevel>=10 prerequisite, distinct from starting a rumor/helper quest.",
                "status": "proposed",
                "evidence": ["EV-0298", "EV-0299", "EV-0260"]
            },
            {
                "id": "Q63-H2",
                "model": "The known level-10 Durak Story Manager condition gates only the messenger helper; ordinary rumor or Fort routes do not yet establish a level-one VQ01/Awakening transition in the captured source scope.",
                "predicted_discriminant": "Source joins show alternate responses only set up helper/rumor state or require the gated handoff, with no direct actual-quest start path; runtime accessibility remains unobserved.",
                "status": "proposed",
                "evidence": ["EV-0298", "EV-0299", "EV-0260"]
            }
        ],
        "methods": [
            "Read EV-0298/EV-0299 and EXP-0040/EXP-0041 before querying; keep the level-gated Durak helper distinct from DLC1VQ00/DLC1VQ01/Awakening.",
            "Join Dawnguard.esm DIAL/INFO/QUST/VMAD record fields and aliases for Durak, Isran, Agmaer, and any guard-rumor topics using source hashes and exact FormIDs.",
            "Use the tested archive-source-discovery route to extract relevant Dawnguard.bsa TIF and QF PEX files; map callbacks to Start/SetStage and helper-state transitions.",
            "Use local UESP pages only as attributed leads; keep the full Steam profile order, level-one test, exact quest-running state, and vanilla reproduction as separate runtime requirements under EV-0260."
        ],
        "blocked_by": [],
        "evidence": ["EV-0298", "EV-0299", "EV-0260"],
        "priority": 1.0,
        "information_gain": 0.98,
        "next_action": "Join Dawnguard.esm DIAL/INFO VMAD and QUST alias fields for the Durak, Isran, Agmaer, and guard-rumor routes, then extract their exact TIF/QF PEX bodies from Dawnguard.bsa and trace whether any callback directly starts or stages DLC1VQ01/Awakening below level 10. Preserve archive hashes and helper-versus-main-quest distinctions; do not claim a live level-one bypass.",
        "linked_claims": [],
        "successors": [],
        "attempts": [],
        "cross_source_assessment": "This is an OBJ-1 Dawnguard quest-entry investigation. No shared ActorValue, HitData, armor-skill, ActiveEffect, or serialization dependency links it to OBJ-2; no cross-objective causal edge is proposed."
    })
    frontier_path.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    exp_results = ROOT / "experiments/EXP-0063-trap-direct-receiver-candidate/results.md"
    text = exp_results.read_text(encoding="utf-8")
    marker = "## Follow-up receiver and cleanup trace — EV-0325"
    if marker not in text:
        text = text.rstrip() + "\n\n" + marker + "\n\nFresh exact-context captures confirm the ActorValueOwner calls at 0x6BA492 (base Health read) and 0x6BA952 (Stamina damage restoration), matching the earlier EXP-0045 classification. The PlayerCharacter cleanup body FUN_14072fd60 has 108 direct edges and 8 indirect sites; the census contains no direct slot-0x7B8 skill dispatch. The unresolved indirect calls and transitive descendants remain open. These findings narrow the static path but do not establish zero XP, positive final damage, effective protection, Steam behavior, or vanilla reproduction [EV-0325].\n"
        exp_results.write_text(text, encoding="utf-8")

    exp_implications = ROOT / "experiments/EXP-0063-trap-direct-receiver-candidate/implications.md"
    text = exp_implications.read_text(encoding="utf-8")
    marker = "EV-0325 also narrows the cleanup branch"
    if marker not in text:
        text = text.rstrip() + "\n\nEV-0325 also narrows the cleanup branch: the mapped ActorValueOwner calls are Health/Stamina operations, and the PlayerCharacter cleanup body has no direct slot-0x7B8 dispatch among 108 direct edges. Eight indirect sites remain. The candidate still needs the exact Steam hit/protection/raw-AVSK observation.\n"
        exp_implications.write_text(text, encoding="utf-8")

    graph = ROOT / "research/KNOWLEDGE_GRAPH.md"
    text = graph.read_text(encoding="utf-8")
    marker = "EV-0325 narrows the mapped receiver calls"
    if marker not in text:
        text = text.rstrip() + "\n\nEV-0325 narrows the mapped receiver calls: the ActorValueOwner sites read base Health and restore Stamina damage; the PlayerCharacter cleanup body has no direct slot-0x7B8 call in its 108-edge census, but retains eight indirect sites. No edge to OBJ-1 is supported.\n"
        graph.write_text(text, encoding="utf-8")

    contradiction = ROOT / "research/CONTRADICTIONS.md"
    text = contradiction.read_text(encoding="utf-8")
    target = "- **Evidence:** [EV-0324], [EV-0293]"
    if "[EV-0325]" not in text[text.find("## C-OBJ2-TRAP-DIRECT-ROUTE"):]:
        pos = text.find("## C-OBJ2-TRAP-DIRECT-ROUTE")
        end = text.find("\n## ", pos + 3)
        if end < 0:
            end = len(text)
        section = text[pos:end].replace(target, "- **Evidence:** [EV-0325], [EV-0324], [EV-0293]", 1)
        text = text[:pos] + section + text[end:]
        contradiction.write_text(text, encoding="utf-8")

    exp64 = ROOT / "experiments/EXP-0064-dawnguard-alternate-entry-source"
    write(exp64 / "README.md", """# EXP-0064 — Dawnguard alternate entry source path

**Question:** Can an ordinary Dawnguard rumor, Isran, or Fort Dawnguard route start DLC1VQ01/Awakening below level 10, apart from the Durak Story Manager helper?

**Frontier:** Q-0063 / OBJ-1. This is a source investigation. No level-one bypass is established until a natural runtime transition is observed under the exact verified Steam build and profile.
""")
    write(exp64 / "hypothesis.md", """# Competing models

- **H1 — alternate main-quest callback:** an ordinary dialogue/arrival callback directly starts or stages DLC1VQ01/Awakening at level 1 without the Durak level-10 helper.
- **H2 — helper or rumor only:** the apparent alternate route starts a rumor/helper or supplies a later transition, while the known level-10 Durak node remains the only source-established questline entry in the inspected scope.

EV-0298/EV-0299 establish a level-10 Durak Story Manager helper and no GetLevel condition in the captured VQ00/VQ01 QUST fields. They do not resolve Dawnguard BSA callback bodies or level-one behavior. The discriminant is exact DIAL/INFO/VMAD-to-PEX call flow into the main quest versus helper-only state.
""")
    write(exp64 / "protocol.md", """# Protocol

1. Read EV-0298/EV-0299, the source queries in EXP-0040/EXP-0041, EV-0260 readiness, and relevant local UESP lead with revision provenance.
2. Use the strict record route for hash-identified Dawnguard.esm DIAL/INFO/QUST/VMAD fields; record exact FormIDs, aliases, CTDA conditions, and attachments.
3. Use the tested archive-source-discovery route to extract only linked Dawnguard.bsa PEX streams. Verify archive and per-script hashes and parse TIF/QF functions.
4. Trace direct Start/SetStage routes and helper-versus-main quest changes; preserve unresolved methods and indirect paths.
5. Treat direct parsing and PEX as static source evidence, not a merged profile winner or live dialogue result. Keep the exact Steam level-one test, no-trigger control, numeric level, and quest-running/stage observer as runtime requirements.
""")
    write(exp64 / "results.md", """# Results

Investigation not yet run. Initial evidence EV-0298/EV-0299 shows the sole `GetLevel >= DLC1VQMinLevel (10)` condition in Dawnguard.esm Story Manager records is on the Durak messenger helper node; the captured VQ00/VQ01 QUST records do not contain a GetLevel condition. Alternate dialogue and archive PEX routes remain unresolved.
""")
    write(exp64 / "implications.md", """# Implications

A Durak helper gate does not by itself prove the Awakening questline is level-gated, and a secondary-source alternate route does not prove level-one access. Keep each route attached to exact records and PEX callbacks. No OBJ-2 causal edge is supported.
""")

    print(json.dumps({
        "registered": "EV-0325",
        "note_sha256": sha(note),
        "capture_manifest_sha256": sha(manifest),
        "captures": len(metadata),
        "frontier_successor": "Q-0063",
        "experiment": "EXP-0064-dawnguard-alternate-entry-source"
    }, indent=2))


if __name__ == "__main__":
    main()
