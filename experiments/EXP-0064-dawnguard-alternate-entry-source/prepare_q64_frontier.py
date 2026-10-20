#!/usr/bin/env python3
"""Carry the Dawnguard result forward and prepare the OBJ-2 cleanup question."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "research/FRONTIER.json"


def main() -> None:
    frontier = json.loads(PATH.read_text(encoding="utf-8"))
    items = frontier["items"]
    q63 = next(item for item in items if item["id"] == "Q-0063")
    if q63.get("status") != "in_progress":
        raise SystemExit("Q-0063 is not the active investigation")
    if any(item["id"] == "Q-0064" for item in items):
        raise SystemExit("Q-0064 already exists; refusing duplicate frontier item")

    for hypothesis in q63["hypotheses"]:
        if hypothesis["id"] == "Q63-H1":
            hypothesis["status"] = "supported"
            hypothesis["evidence"] = list(dict.fromkeys([*hypothesis.get("evidence", []), "EV-0326"]))
        elif hypothesis["id"] == "Q63-H2":
            hypothesis["status"] = "falsified"
            hypothesis["model"] += " (falsified within the mapped Fort dialogue source path; runtime startup remains unknown)."
            hypothesis["evidence"] = list(dict.fromkeys([*hypothesis.get("evidence", []), "EV-0326"]))
    q63["evidence"] = list(dict.fromkeys([*q63.get("evidence", []), "EV-0326"]))
    q63["linked_claims"] = list(dict.fromkeys([*q63.get("linked_claims", []), "CL-L157"]))
    q63["successors"] = list(dict.fromkeys([*q63.get("successors", []), "Q-0064"]))
    q63["next_action"] = (
        "After closing this bounded source result, open Q-0064 and resolve the eight indirect sites "
        "in the GOG PlayerCharacter teardown body; keep Steam positive-damage, protection, and raw-AVSK observation open."
    )

    items.append({
        "id": "Q-0064",
        "objective": "OBJ-2",
        "kind": "mechanism",
        "status": "open",
        "question": "Can any of the eight unresolved indirect calls in the ProcessTrapHit PlayerCharacter teardown chain reach AV11/AV12 skill progress, or do all captured cleanup targets resolve away from armor-skill credit?",
        "hypotheses": [
            {
                "id": "Q64-H1",
                "model": "The eight indirect sites and their relevant descendants do not dispatch armor skill progress for AV11/AV12 on the captured ProcessTrapHit cleanup route.",
                "predicted_discriminant": "Build-attested callsite contexts and concrete target resolution show the relevant cleanup path reaches neither Actor::UseSkill slot 0xF7 with AV11/AV12 nor the mapped skill-progress sink; unknown targets remain unresolved rather than counted as negative.",
                "status": "proposed",
                "evidence": ["EV-0325", "EV-0319", "EV-0324"]
            },
            {
                "id": "Q64-H2",
                "model": "At least one indirect teardown callback or relevant descendant can route an armor ActorValue into skill progress, weakening the trap armor-XP bypass candidate.",
                "predicted_discriminant": "A resolved virtual/function target from the captured cleanup route reaches Actor::UseSkill or the mapped skill-progress sink with an AV11/AV12 input; a generic indirect site without target/type/argument evidence is inconclusive.",
                "status": "proposed",
                "evidence": ["EV-0325", "EV-0319", "EV-0324"]
            }
        ],
        "methods": [
            "Read EV-0319, EV-0324 and EV-0325 notes, manifests and the raw eight-site teardown census before querying; preserve the distinction between direct absence and unresolved virtual targets.",
            "Use the existing identity-checked GOG 1.6.1179.0 project through the strict dispatcher in -noanalysis -readOnly mode; collect bounded instruction context, references, class/vtable evidence and call edges for each site.",
            "Resolve only observed target tables and bounded descendants that can reach Actor::UseSkill slot 0xF7 or the mapped skill-progress routine; trace the ActorValue argument and retain unresolved sites explicitly.",
            "Do not transfer GOG addresses to Steam 1.6.1170.0. Keep positive final damage, effective protection, and repeated raw AVSK deltas as a separate exact-target runtime discriminator under EV-0260."
        ],
        "blocked_by": [],
        "evidence": ["EV-0325", "EV-0319", "EV-0324", "EV-0261", "EV-0260"],
        "priority": 1.0,
        "information_gain": 0.96,
        "next_action": "Inspect the EV-0325 raw census and EV-0319 handle-to-PlayerCharacter teardown trace; list the exact eight indirect callsite offsets, argument/receiver context, and observed function-pointer or vtable bases before selecting a bounded target query.",
        "linked_claims": [],
        "successors": [],
        "attempts": [],
        "cross_source_assessment": "This is an OBJ-2 armor-skill-routing investigation. No shared quest-start field or call edge with OBJ-1 is currently identified; do not add a cross-objective edge without same-build dependency evidence."
    })
    PATH.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Q-0063 evidence links updated; Q-0064 prepared as the next P0 OBJ-2 investigation")


if __name__ == "__main__":
    main()
