#!/usr/bin/env python3
"""Add a source-ready OBJ-1 follow-up after the frontier was all blocked."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
frontier_path = ROOT / "research" / "FRONTIER.json"
recovery = json.loads((ROOT / "research" / "RECOVERY.json").read_text(encoding="utf-8"))
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))

if recovery.get("status") != "idle" or recovery.get("last_transaction_id") != "TX-20261020-0001":
    raise SystemExit("frontier reselection requires the completed Q82 checkpoint")
if any(row.get("id") == "Q-0083" for row in frontier.get("items", [])):
    raise SystemExit("Q-0083 already exists")

q83 = {
    "id": "Q-0083",
    "objective": "OBJ-1",
    "kind": "mechanism",
    "status": "open",
    "question": "Is the Dragonborn main-quest CLOC cultist attack genuinely level-gated at initiation, or does any level dependence apply only to the separate world encounter or spawned actor variant?",
    "hypotheses": [
        {
            "id": "Q83-H1",
            "model": "An explicit Player-level predicate above 1 gates the CLOC cultist-attack initiation before the DLC2CultistAmbush QUST starts.",
            "predicted_discriminant": "The exact official CLOC parent/child conditions, linked INFO/alias conditions, attached script logic, or a build-identified native callback reads Player level before the real QUST start; distinguish this from actor scaling and journal state.",
            "status": "proposed",
            "evidence": ["EV-0653", "EV-0654", "EV-0656", "EV-0658", "EV-0260"],
        },
        {
            "id": "Q83-H2",
            "model": "The CLOC route is initiated by main-quest/event state without a player-level threshold in the official five-master path; the explicit GetLevel row belongs to separate DLC2WE09 world-encounter conditions.",
            "predicted_discriminant": "A complete source-bounded walk finds no Player-level predicate before CLOC QUST startup, while record conditions and fragments depend on event/main-quest state; the separate world route remains a distinct child/QUST.",
            "status": "proposed",
            "evidence": ["EV-0654", "EV-0656", "EV-0657", "EV-0658", "EV-0664", "EV-0665"],
        },
        {
            "id": "Q83-H3",
            "model": "Player level affects only the cultist actor or combat variant selected after event initiation, rather than whether the CLOC quest/encounter starts.",
            "predicted_discriminant": "Actor/NPC/leveled-list/template records or a source-backed selector show level-dependent variant selection downstream of CLOC startup, with no matching pre-start Player-level gate.",
            "status": "proposed",
            "evidence": ["EV-0653", "EV-0654", "EV-0656", "EV-0260"],
        },
    ],
    "methods": [
        "Reconcile Q81 source claims and contradictions before extending the search; distinguish event selection, QUST startup, actor spawn/variant, and journal state.",
        "Ground the level-threshold and cultist-variant premises against revision-cited local UESP pages, retaining the local corpus provenance limit.",
        "Trace the exact official-five-master CLOC parent/child, QUST, linked INFO, aliases, script properties, actor/NPC templates, and levelled records; preserve raw rows and do not claim active-profile winners.",
        "Use only the supported archive/source-discovery route for missing Dragonborn PEX; if the configured archive lacks the file, retain that precise scope limit and continue the record/native screen.",
        "Keep exact Steam natural initiation and level-one preservation under EV-0260; console, script injection, and forced stage are diagnostic only.",
    ],
    "blocked_by": [],
    "evidence": ["EV-0653", "EV-0654", "EV-0656", "EV-0657", "EV-0658", "EV-0663", "EV-0664", "EV-0260"],
    "priority": 0.995,
    "information_gain": 0.95,
    "next_action": "Read the linked Q81 records and C-OBJ1 contradictions; retrieve revision-cited local UESP pages for the cultist ambush and The Way of the Voice. Then extend the official five-master CLOC chain into its linked actor/NPC/leveled records and attempt only the supported Dragonborn source/archive route for attached PEX. Decide whether any level predicate gates actual QUST initiation versus only encounter/actor variant; retain EV-0260 for a natural level-one transition.",
    "linked_claims": ["CL-L461", "CL-L462", "CL-L463", "CL-L464"],
    "cross_source_assessment": "Q81 established separate CLOC DLC2CultistAmbush and SCPT DLC2WE09 children/QUSTs, a CLOC QUST with no direct GetLevel row, and a separate world-condition pair with an OR flag [EV-0654], [EV-0656]–[EV-0669]. These facts do not resolve attached script/native predicates or actor-level variant selection. The objective remains whether a genuinely level-gated transition can be initiated at character level 1; a route accessible at any level is not an exploit.",
    "successors": [],
    "attempts": [],
}
frontier["items"].append(q83)
q81 = next(row for row in frontier["items"] if row.get("id") == "Q-0081")
q81["successors"] = list(dict.fromkeys([*q81.get("successors", []), "Q-0083"]))
q81["next_action"] = "The runtime CLOC/world encounter transition remains blocked on EV-0260. Q-0083 now continues the independent static question: determine whether the main-quest CLOC start has any true Player-level gate versus only actor-variant scaling; keep exact natural level-one proof separate."
q80 = next(row for row in frontier["items"] if row.get("id") == "Q-0080")
q80["next_action"] = "The bounded clothing/resistance source model and no-edge are recorded in C-OBJ2-Q80 and M-0198. Resume only after EV-0260 supplies the exact disposable profile/order, level-one inventory roll, matched magic/physical hit controls, and numeric protection/raw-AVSK samples. Q-0083 continues independent OBJ-1 static work meanwhile."
q82 = next(row for row in frontier["items"] if row.get("id") == "Q-0082")
q82["next_action"] = "Closed as a bounded GOG/official-five-master static phase-order result [EV-0670]–[EV-0676], M-0200. The exact Steam positive-protection/raw-AVSK test remains EV-0260; Q-0083 is the active independent OBJ-1 source discriminator."
frontier["session_next_action"] = q83["next_action"]
frontier["next_action"] = q83["next_action"]
frontier.setdefault("target", {})["next_action"] = "Begin Q-0083 with the generated transaction ID; inspect the linked Q81 and Q80 source/claim/contradiction records, capture revision-cited UESP premises, and trace the official CLOC chain into actor/leveled records and any supported Dragonborn PEX source. Keep natural Steam level-one initiation under EV-0260."
frontier_path.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("added Q-0083 as the highest-priority open static OBJ-1 line; preserved Q80/Q81 runtime blockers")
