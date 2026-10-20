#!/usr/bin/env python3
"""Record Q86's bounded findings and seed its exact level-field writer follow-up."""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TX = "TX-20261020-0005"
EVIDENCE_IDS = {"EV-0688", "EV-0689", "EV-0690"}

CLAIM_475 = "| CL-L475 | In GOG AE 1.6.1179.0, Actor::GetLevel forwards the actor base-data pointer to TESActorBaseData::GetLevel, which reads the 16-bit actorData.level field and applies PCLevelMult scaling/clamps only on the flagged path. | supported for this build-specific direct getter path | [EV-0689] | This does not establish when Player level changes, whether a pending level-up retains the old field value, Steam behavior, or a live level-one quest gate. |\n"
CLAIM_476 = "| CL-L476 | In GOG AE 1.6.1179.0, the unblocked Player receiver worn-armor branch calls PlayerCharacter vtable slot 0xF7 with the selected skill index 11/12 and calculated points; its positive-points target reaches the same skill-progress routine that adds separate cumulative character-level XP. | supported for the captured static GOG call path | [EV-0221], [EV-0670], [EV-0674], [EV-0689], [EV-0690] | This is not a live ordinary-hit result, positive-protection measurement, Steam mapping, armor-XP bypass, or proof that the GetLevel field changes at any particular time. |\n"

MECHANISM_203 = """\n## M-0203 — Stored ActorBaseData level getter is separate from skill-XP accumulation (EV-0688–EV-0689)\n\nIn GOG AE 1.6.1179.0, Actor::GetLevel loads the actor's base-form pointer and forwards the TESActorBaseData subobject to a helper that reads its 16-bit actorData.level field. Only the flagged PCLevelMult path scales from Player level and applies bounds [EV-0689]. The resolved PlayerCharacter skill-progress routine instead tracks per-skill progress and a separate cumulative character-level XP value, then dispatches a skill-level event. The resolved event listener updates a misc statistic; the bounded LevelUpMenu apply helper refreshes thresholds/attributes and reads GetLevel for display/profile processing without a direct store to the level field [EV-0689].\n\nThis separates the getter input from the XP accumulator in the captured source paths; it does not identify all Player level-field writers or choose whether the field changes at threshold versus acceptance. EV-0688 is secondary UESP grounding only. GOG RVAs do not transfer to Steam. Claim CL-L475.\n"""
MECHANISM_204 = """\n## M-0204 — Hit-earned armor skill points enter the shared Player skill-progress path (EV-0690)\n\nIn the captured GOG AE 1.6.1179.0 HitData receiver path, the unblocked Player branch selects armor skill 11 or 12 and calls vtable byte offset +0x7b8 (slot 0xF7) with the calculated points. The exact PlayerCharacter slot target is FUN_140739050 [EV-0674]; its positive-points branch reaches FUN_14077d090 [EV-0221], the skill-progress/threshold routine mapped in EV-0689. That routine adds a separate cumulative character-level XP value [EV-0689]. This establishes a GOG static causal connection from the bounded armor skill award path into general skill and character-XP progression [EV-0690].\n\nThe captured source path does not prove an ordinary incoming live hit, effective protection, a qualifying zero-XP result, Steam equivalence, or when the Player GetLevel field changes. The connection is to XP routing, not to the armor mitigation result itself. No bounty outcome follows. Claim CL-L476.\n"""
GRAPH_086 = """\n### EV-0688–EV-0690 — Pending level, stored getter, and armor-skill XP convergence\n\nThe revision-pinned local UESP page supplies only secondary grounding for pending versus accepted level-ups [EV-0688]. GOG AE 1.6.1179.0 code shows Actor::GetLevel reading the stored 16-bit ActorBaseData level field (with a flagged PCLevelMult branch), while the resolved skill-progress routine tracks skill progress and separate cumulative character-level XP [EV-0689]. Claim CL-L475 maps this bounded getter.\n\nA later exact GOG query resolves the Player receiver branch in FUN_1406bcaa0: its unblocked worn-armor selector reaches vtable byte offset +0x7b8, slot 0xF7, with armor skill 11/12 and calculated points. The slot target checks positive points and enters the same skill-progress helper [EV-0221], [EV-0670], [EV-0674], [EV-0689], [EV-0690]. This is a supported causal edge from the bounded HitData armor-skill route into cumulative character-level XP progression (M-0200 -> M-0204 -> the skill-progress arm of M-0203). It may be relevant when a level-one player accumulates hit-earned skill progress, but no pending-level timing, GetLevel field write, live ordinary hit, or Steam result is established.\n\nKeep separate: no causal edge is established from the stored GetLevel field to effective armor protection or to suppression of AV11/AV12. The GOG code link does not validate a vanilla level-one bypass or OBJ-2 exploit. Preserve EV-0260 for the Steam before-threshold/pending/accepted and matched-hit/protection/raw-AVSK observations. Claims CL-L475–CL-L476; mechanisms M-0203–M-0204.\n"""
ROADMAP_086 = """\n## Cross-domain synthesis — 2026-10-20 — pending level state and armor XP\n\nQ83/Q85 kept the Dragonborn CLOC initiation chain separate from the world-cultist QUST: the Solstheim location row is a conditional alternative to the level-25 predicate only after earlier chance/stage predicates, and neither natural level-one startup nor Steam evaluation timing is observed [EV-0654]–[EV-0687]. Q82/Q84 bounded the GOG HitData phase order and entrypoint-handler effects: mitigation precedes the worn-armor scan, while selector handlers update numeric results or derived-value caches without a captured direct equipment, source-ActorValue, HitData, or skill-progress write [EV-0670]–[EV-0685].\n\nQ86 adds a direct cross-domain path: the unblocked player-receiver worn-armor route sends skill 11/12 points through UseSkill slot 0xF7 to the skill-progress routine, which also adds cumulative character-level XP [EV-0221], [EV-0670], [EV-0674], [EV-0689], [EV-0690]. Separately, the captured GetLevel getter reads ActorBaseData.level [EV-0689]. The native writer and pending-versus-accepted timing remain unresolved, so do not infer that XP changes the gate-visible field before acceptance. This is a causal XP-routing edge, not evidence of a level-one exploit, armor protection, or zero-armor-XP behavior.\n\nNext static discriminator: map the exact GOG ActorBaseData.level read offset and trace only producer-backed writes with Player/base-form provenance; compare candidate callers to the skill-threshold/event and LevelUpMenu paths. Keep Steam live observations under EV-0260 and continue P0 selection.\n"""


def append_once(relative: str, marker: str, content: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


def main() -> None:
    recovery = json.loads((ROOT / "research/RECOVERY.json").read_text(encoding="utf-8"))
    if (recovery.get("status"), recovery.get("transaction_id"), recovery.get("frontier_id")) != ("running", TX, "Q-0086"):
        raise SystemExit("Q86 is not active")
    evidence = json.loads((ROOT / "research/EVIDENCE.json").read_text(encoding="utf-8"))
    known = {row.get("id") for row in evidence.get("items", [])}
    if not EVIDENCE_IDS.issubset(known):
        raise SystemExit("Q86 synthesis evidence is not completely registered")

    append_once("research/CLAIMS.md", "CL-L475", CLAIM_475)
    append_once("research/CLAIMS.md", "CL-L476", CLAIM_476)
    append_once("research/MECHANISMS.md", "M-0203 —", MECHANISM_203)
    append_once("research/MECHANISMS.md", "M-0204 —", MECHANISM_204)
    append_once("research/KNOWLEDGE_GRAPH.md", "EV-0688–EV-0690 —", GRAPH_086)
    append_once("ROADMAP.md", "Cross-domain synthesis — 2026-10-20 — pending level state and armor XP", ROADMAP_086)

    result_path = ROOT / "experiments/EXP-0135-player-level-up-commit/results.md"
    result_text = result_path.read_text(encoding="utf-8")
    old = "This narrows the models without selecting one. The `GetLevel` getter does not derive the returned level from cumulative skill XP in the resolved helper, weakening that H2 submodel. An automatic threshold/notification writer to the Player base-data field remains possible, and the acceptance-time writer was not identified. The capped broad displacement scan found 3,136 writer-candidate functions and analyzed only its first 16, so it is not a negative writer census. Steam before-threshold, pending, and accepted states remain unobserved under EV-0260; there is no vanilla level-one bypass or OBJ-2 edge."
    replacement = "This narrows the timing models without selecting one. The `GetLevel` getter does not derive its return from cumulative skill XP in the resolved path. An automatic threshold/notification writer to the Player base-data field remains possible, and the acceptance-time writer was not identified. The capped broad displacement scan found 3,136 writer-candidate functions and analyzed only its first 16, so it is not a negative writer census. Steam before-threshold, pending, and accepted states remain unobserved under EV-0260; no vanilla level-one bypass or OBJ-2 outcome is established. EV-0690 subsequently identifies a GOG-only causal route from the HitData worn-armor AV11/AV12 call into that shared skill-progress/character-XP routine, as documented below."
    if old in result_text:
        result_text = result_text.replace(old, replacement, 1)
    if "## Cross-domain update — EV-0690" not in result_text:
        result_text += """\n\n## Cross-domain update — EV-0690\n\nA fresh identity-checked GOG query of `FUN_1406bcaa0` shows the unblocked Player receiver branch calling vtable byte offset `+0x7b8` (slot `0xF7`) with armor skill index 11/12 and the calculated point value. EV-0674 maps that exact PlayerCharacter slot to `FUN_140739050`; EV-0221 shows its positive-points branch entering `FUN_14077d090`; EV-0689 maps that routine to per-skill progress and separate cumulative character-level XP. This establishes a static causal edge from the bounded armor-skill award path into character-XP accumulation. It does not establish live ordinary-hit coverage, protection, a zero-XP exploit, Steam behavior, or when the gate-visible Player level field changes.\n\n### Exact next investigation — Q-0087\n\nMap the GOG `TESActorBaseData.actorData.level` read offset from `FUN_1401d7b20`, then identify producer-backed stores to that exact field with Player/base-form provenance. Compare the writers' direct incoming call paths to `FUN_14077d090` threshold/event handling and the LevelUpMenu apply path. An acceptance-only writer supports the deferred-field model; a threshold/notification writer supports automatic advancement. A capped displacement scan is not a negative census. Preserve the Steam before-threshold/pending/accepted discriminator under EV-0260.\n"""
    result_path.write_text(result_text, encoding="utf-8")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    by_id = {item.get("id"): item for item in frontier.get("items", [])}
    q86 = by_id.get("Q-0086")
    if q86 is None or q86.get("status") != "in_progress":
        raise SystemExit("Q86 frontier item is not active")
    q86["evidence"] = list(dict.fromkeys([*q86.get("evidence", []), *sorted(EVIDENCE_IDS)]))
    q86["linked_claims"] = list(dict.fromkeys([*q86.get("linked_claims", []), "CL-L475", "CL-L476"]))
    q86["next_action"] = "Record EV-0690's exact GOG-only connection from the Player receiver worn-armor AV11/AV12 call through UseSkill slot 0xF7 into cumulative character-level XP; update the cross-domain graph while keeping level-field timing unresolved; then close Q86 as a bounded static result and begin Q87 to trace exact Player actorData.level writers."
    if "Q-0087" not in by_id:
        q87 = copy.deepcopy(q86)
        q87.update({
            "id": "Q-0087",
            "objective": "OBJ-1",
            "kind": "mechanism",
            "status": "open",
            "question": "Which producer-backed GOG call path writes the Player TESActorBaseData.actorData.level field, and is that writer reached at skill-XP threshold/notification or only after level-up acceptance?",
            "hypotheses": [
                {
                    "id": "Q87-H1",
                    "model": "The Player actorData.level writer is reached only from the accepted LevelUpMenu/apply-level path; skill threshold and notification update progress/XP without committing the gate-visible field.",
                    "predicted_discriminant": "An exact store to the verified level-field offset has Player/base-form provenance and an incoming call chain terminating only at the accepted attribute callback/menu route.",
                    "status": "proposed",
                    "evidence": ["EV-0260", "EV-0689"],
                },
                {
                    "id": "Q87-H2",
                    "model": "A threshold/event-notification path writes the Player actorData.level field before the level-up is accepted.",
                    "predicted_discriminant": "An exact store to the verified field offset has a producer-backed call chain from skill-threshold progress or its event listener, independent of the accept callback.",
                    "status": "proposed",
                    "evidence": ["EV-0260", "EV-0689", "EV-0690"],
                },
            ],
            "methods": [
                "Re-read the identity-checked GOG getter body and CommonLib layout to pin the exact ActorBaseData.level offset.",
                "Trace bounded code/data references and store candidates only when the base-form/Player receiver provenance is established; do not treat broad displacement hits as a negative census.",
                "Compare producer-backed writer callers to the skill-XP threshold/event route and LevelUpMenu accept/apply route using the same GOG build.",
                "Preserve the Steam before-threshold, pending-before-acceptance, and accepted-state observation under EV-0260; GOG RVAs are not transferred.",
            ],
            "blocked_by": [],
            "evidence": ["EV-0260", "EV-0689", "EV-0690"],
            "priority": 0.99,
            "information_gain": 0.99,
            "next_action": "Read EV-0689/EV-0690 captures and the pinned CommonLib level-up declarations; map the exact actorData.level read offset in GOG FUN_1401d7b20, then trace producer-backed stores with Player/base-form provenance. Compare only verified candidate callers to skill-threshold/event and LevelUpMenu apply paths. Do not use the capped displacement scan as a negative census. Keep the natural Steam pending-versus-accepted observation under EV-0260.",
            "linked_claims": ["CL-L475", "CL-L476"],
            "successors": [],
            "attempts": [],
        })
        by_id["Q-0087"] = q87
        frontier["items"].append(q87)
    frontier_path.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"claims": ["CL-L475", "CL-L476"], "mechanisms": ["M-0203", "M-0204"], "seeded_frontier": "Q-0087"}, indent=2))


if __name__ == "__main__":
    main()
