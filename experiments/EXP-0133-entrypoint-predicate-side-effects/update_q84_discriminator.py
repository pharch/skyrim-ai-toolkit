#!/usr/bin/env python3
"""Correct the Q84 model to distinguish DATA[1] handler ID from EPFT class ID."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTIER = ROOT / "research/FRONTIER.json"
RECOVERY = ROOT / "research/RECOVERY.json"
CHECKPOINT_UTC = "2026-10-20T02:19:50+00:00"
NEXT_ACTION = (
    "Query the GOG handler-table slots actually selected by DATA[1] values 1, 3, and 14 for selector 37/39. "
    "Resolve full handler bodies, data-type gates, direct/indirect calls, and numeric versus gameplay-state writes; "
    "map each ID back to EPFT class and official row. Correct the earlier Q82 interpretation and retain "
    "Steam/profile/runtime limits."
)


def main() -> None:
    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    recovery = json.loads(RECOVERY.read_text(encoding="utf-8"))
    if recovery.get("status") != "running" or recovery.get("transaction_id") != "TX-20261020-0003":
        raise SystemExit("refusing Q84 model correction outside the active transaction")
    if recovery.get("frontier_id") != "Q-0084":
        raise SystemExit("active transaction does not own Q-0084")
    item = next((row for row in frontier.get("items", []) if row.get("id") == "Q-0084"), None)
    if item is None or item.get("status") != "in_progress":
        raise SystemExit("Q-0084 is not active and in progress")

    item["question"] = (
        "For official HitData selector 37/39 PERK entries in GOG AE 1.6.1179.0, do the actual DATA[1] handler IDs "
        "1, 3, or 14 and their EPFT-selected function-data classes produce any equipment, HitData, ActorValue, "
        "or queued-state change between mitigation and the worn-armor AV11/AV12 scan?"
    )
    models = {row["id"]: row for row in item["hypotheses"]}
    h1 = models["Q84-H1"]
    h1["model"] = (
        "For the captured GOG path and official selector-37/39 rows, DATA[1] IDs 1/3/14 select bounded numeric "
        "entrypoint handlers and EPFT selects data classes whose vtable +8 methods only report their type; none "
        "mutates equipment, HitData, ActorValues, or queued event state before the armor scan."
    )
    h1["predicted_discriminant"] = (
        "The BGSEntryPointPerkEntry wrapper and EPFT-selected OneValue/TwoValue data classes are identified; "
        "handlers 1/3/14 and their direct descendants only compute numeric results or read inputs, with no "
        "relevant state writer, setter, queue, or yield before FUN_1406bcaa0's AV11/AV12 scan."
    )
    h2 = models["Q84-H2"]
    h2["model"] = (
        "At least one actual handler ID DATA[1]=1/3/14 or one EPFT-selected data-class predicate used by a matching "
        "official selector row can mutate equipment, HitData, ActorValues, or queued state before the receiver's "
        "worn-armor scan."
    )
    h2["predicted_discriminant"] = (
        "A producer-backed handler or concrete function-data target reaches a relevant field write, equipment/" 
        "ActorValue setter, or synchronous/deferred state submission before FUN_1406bcaa0 performs the AV11/AV12 selection."
    )
    for model in (h1, h2):
        model["status"] = "proposed"
        model["evidence"] = list(dict.fromkeys([*model.get("evidence", []), "EV-0671", "EV-0672", "EV-0675", "EV-0681", "EV-0682", "EV-0683"]))

    item["methods"] = [
        "Use DATA[0] as selector, DATA[1] as the wrapper-returned handler ID, DATA[2] as the separate byte field, and EPFT/EPFD as function-data class/payload; do not conflate these fields with PRKE.",
        "Verify the wrapper receiver and data pointer through GOG RTTI/vtable and parser storage before using handler or class-specific virtuals.",
        "Query handler IDs 1, 3, and 14 from the exact GOG dispatch table; inspect full bodies, type gates, incoming rows, direct/indirect calls, and writes against the AV39-to-AV11/AV12 phase order.",
        "Map every handler ID to the official selector row and EPFT class; retain file-level duplicates and do not claim profile winners.",
        "Treat all GOG/Steam comparisons as cross-build static evidence only; retain EV-0260's complete-order Steam matched-hit/protection/raw-AVSK requirement.",
    ]
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0681", "EV-0682", "EV-0683"]))
    item["next_action"] = NEXT_ACTION
    item["cross_source_assessment"] = (
        "Correction EV-0683 resolves the wrapper field: BGSEntryPointPerkEntry GetFunction reads DATA[1], while "
        "GetFunctionData returns the pointer at entry+0x18; the separately serialized EPFT selects the function-data "
        "class [EV-0681]–[EV-0683]. The 23 official selector-37/39 file rows use DATA[1] values 1/3/14, with EPFT "
        "class values 1/2 [EV-0675], so Q82's earlier EPFT-as-handler interpretation and the provisional ID-2/type-1 "
        "mismatch are superseded. The data-class +8 methods observed so far return constant type codes, but the "
        "actual handlers 3/14 remain unresolved. No inference about live protection, armor XP, Steam equivalence, "
        "profile winners, or an OBJ-1 causal edge follows. EV-0260 remains open."
    )
    frontier["session_next_action"] = NEXT_ACTION
    frontier["next_action"] = NEXT_ACTION
    if isinstance(frontier.get("target"), dict):
        frontier["target"]["next_action"] = NEXT_ACTION
    frontier["session_checkpoint"] = {
        "timestamp_utc": CHECKPOINT_UTC,
        "task": "Q-0084/TX-20261020-0003: query the correct DATA[1] entrypoint handlers after separating them from EPFT function-data class IDs.",
        "next_action": NEXT_ACTION,
    }
    frontier["last_session_checkpoint"] = {
        "recorded_utc": CHECKPOINT_UTC,
        "next_action": NEXT_ACTION,
        "active_process": "TX-20261020-0003",
    }
    FRONTIER.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("updated Q-0084 discriminator and supersession note for Q82 field interpretation")


if __name__ == "__main__":
    main()
