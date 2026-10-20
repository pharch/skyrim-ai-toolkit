from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    if marker not in text:
        p.write_text(text.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L418",
    "| CL-L418 | In GOG AE 1.6.1179.0, Actor.RemoveSpell tag 0x5d and tag-0x44 caller 47 each reach distinct refcounted object-collection cleanup paths; the current evidence shows only a structural analogy, with no shared direct helper, RTTI identity, or call chain. | supported as a bounded analogy only | [EV-0581], [EV-0604], [EV-0605] | No shared class or causal relation to ActiveEffect lifetime, HitData, armor protection, AV11/AV12, or quest gating is established. A shared concrete removal helper or RTTI/call-chain link would change this assessment. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0158 — Worker collection cleanup is a structural analogy (EV-0581, EV-0604/0605)",
    "## M-0158 — Worker collection cleanup is a structural analogy (EV-0581, EV-0604/0605)\n\nThe Actor.RemoveSpell tag-0x5d route removes an object from a pointer-backed collection [EV-0581]. The unrelated tag-0x44 path uses `FUN_1401fdb80` and `FUN_140d1ed80` to update manager-owned pointer arrays with reference counting [EV-0604], [EV-0605]. These are distinct GOG call paths with no shared direct helper, RTTI identity, or proven class; the resemblance is an analogy, not an ActiveEffect or gameplay edge. To upgrade it, find a common concrete removal helper or compatible receiver type and trace its producer. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L418.",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "Cross-system analogy CL-L418 — collection cleanup",
    "Cross-system analogy [CL-L418]: EV-0581 (Actor.RemoveSpell/tag 0x5d) and EV-0604/EV-0605 (tag 0x44) each show reference-counted pointer-collection cleanup. They use distinct direct helpers and lack a shared RTTI/call-chain link. This is analogy only, not evidence of shared ActiveEffect or armor semantics. Falsifier/upgrade condition: demonstrate a common concrete removal target or compatible receiver RTTI reached from both producer paths. No edge to OBJ-1 is supported.",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
if any(row.get("id") == "Q-0080" for row in frontier["items"]):
    raise SystemExit("Q-0080 already exists")
q80 = {
    "id": "Q-0080",
    "objective": "OBJ-2",
    "kind": "mechanism",
    "status": "open",
    "question": "Can the official Resist Magic clothing candidate ARMO 000FC061 provide a level-one player with measurable protection from incoming magic attacks while the Heavy/Light skill route remains at zero, and is this a distinct damage path rather than a positive-DNAM HitData bypass?",
    "hypotheses": [
        {
            "id": "Q80-H1",
            "model": "The level-one-accessible clothing enchantment modifies AV44 and reduces resistable magic damage through MagicTarget::CheckResistance, while its zero physical DNAM rating leaves it outside the mapped positive-DNAM Heavy/Light selector.",
            "predicted_discriminant": "The exact vanilla item and acquisition path are confirmed; a controlled incoming magic hit causes positive but lower Health damage with the item, while repeated numeric Heavy/Light AVSK samples stay unchanged and no AV11/AV12 hit-award call is observed.",
            "status": "proposed",
            "evidence": ["EV-0398", "EV-0402", "EV-0222", "EV-0260"]
        },
        {
            "id": "Q80-H2",
            "model": "The clothing resistance path protects against magic effects only and does not demonstrate armor-like protection against the qualifying physical hit required for the bounty prize.",
            "predicted_discriminant": "Paired controls show reduced damage from an AV41-44-resistable magic effect but no reduction from a comparable physical hit; the magic path remains separate from the mapped HitData/AV11/AV12 branch.",
            "status": "proposed",
            "evidence": ["EV-0398", "EV-0399", "EV-0402", "EV-0222"]
        }
    ],
    "methods": [
        "Verify the exact five-master ARMO/ENCH/MGEF chain and identify a natural level-one acquisition route for ARMO 000FC061; source records alone do not establish player access.",
        "Trace the ordinary incoming magic-effect route into MagicTarget::CheckResistance and determine whether it enters any HitData or Heavy/Light skill-use path; keep GOG and Steam identities separate.",
        "When the verified Steam test lane and disposable save/Observer prerequisites are available, compare naked and equipped controls under the same resistable magic attack, recording nonzero Health damage, numeric Heavy/Light/Block AVSK before and after repeated hits, level, item slot and all other effects.",
        "Run a separate physical-hit control. If only magic damage is reduced, classify this as a defensive-apparel comparator or partial result, not proof of a general physical-armor XP bypass."
    ],
    "blocked_by": [],
    "evidence": ["EV-0398", "EV-0399", "EV-0400", "EV-0401", "EV-0402", "EV-0222", "EV-0223", "EV-0260"],
    "priority": 0.88,
    "information_gain": 0.91,
    "next_action": "Resolve the item’s level-one acquisition route from local UESP/source records, then trace the GOG incoming magic-effect caller of MagicTarget::CheckResistance and compare it with the mapped HitData AV11/AV12 route. Record exact Steam health/AVSK testing as a later external experiment under EV-0260.",
    "linked_claims": ["CL-L067", "CL-L231", "CL-L232", "CL-L233"],
    "cross_source_assessment": "This is a candidate parallel defense path, not a causal link to M-0017: EV-0398 identifies a Clothing ARMO with zero physical DNAM and AV44 Resist Magic; EV-0402 maps CheckResistance reading AV44/AV40 and the incoming effect ResistValue; EV-0222 maps a separate positive-base-DNAM Heavy/Light AV11/AV12 selector. The incoming magic caller, level-one acquisition, effective protection, and Steam numeric AVSK are still unknown. It does not connect to OBJ-1 Story Manager gates.",
    "attempts": [],
    "successors": []
}
frontier["items"].append(q80)
frontier["target"]["next_action"] = "Continue active Q-0079/TX-20261018-0013 at caller 47 object factories FUN_1404a27f0/FUN_1404a28a0, then caller 48/62; Q-0080 is a ready clothing-resistance discriminator awaiting reselection after the active transaction checkpoint."
frontier["last_session_checkpoint"] = {
    "recorded_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "next_action": frontier["session_next_action"],
    "active_process": "TX-20261018-0013"
}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

roadmap_text = (
    "## Cross-domain synthesis — collection cleanup and defensive clothing comparator (EV-0581, EV-0398–EV-0402, EV-0222, EV-0604/0605)\n\n"
    "Actor.RemoveSpell tag 0x5d and tag 0x44 each manipulate refcounted pointer collections, but their helpers and observed call paths differ; CL-L418 records only an analogy. No ActiveEffect identity or combat/armor effect follows. Separately, the official Clothing ARMO 000FC061 carries AV44 Resist Magic while having zero physical DNAM, and the GOG CheckResistance body reads AV44/AV40 plus the incoming effect ResistValue. This is a potentially measurable magic-defense comparator outside the mapped positive-DNAM Heavy/Light AV11/AV12 selector, but level-one acquisition, the ordinary magic-hit caller, Steam damage reduction and numeric AVSK are unverified. Q-0080 tests that narrow candidate and separates magic from physical hits. No shared causal edge to the MS06 level-10 Story Manager path (Q-0078) is supported.\n\n"
    "Next: resume the running caller-47 investigation at object factories `FUN_1404a27f0`/`FUN_1404a28a0`, then caller 48/62. After that checkpoint, reselect between the remaining OBJ-2 callers, Q-0080 and an independent OBJ-1 gate candidate; retain the exact unforced Steam transition and numeric protection/AVSK tests.\n"
)
append_once("ROADMAP.md", "## Cross-domain synthesis — collection cleanup and defensive clothing comparator", roadmap_text)

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
old = "**OBJ-2:** Q-0079 has 47/62 exact worker callers reviewed; 15 remain. EV-0603–EV-0605 map caller 47/tag 0x44 through a gated object producer into manager-array membership cleanup; unresolved virtual effects and the clean Steam protection/raw-AVSK test remain open."
new = old + " Q-0080 is queued to test the AV44 clothing-resistance comparator against the distinct positive-DNAM AV11/AV12 selector [EV-0398]–[EV-0402], [EV-0222]; level-one access and clean Steam damage/AVSK remain unverified. Cross-domain collection cleanup remains an analogy only [CL-L418]."
if old not in state:
    raise SystemExit("STATE P0 summary anchor not found")
state = state.replace(old, new, 1)
state_path.write_text(state, encoding="utf-8")
print("synthesis recorded as CL-L418/M-0158; analogy preserved; Q-0080 added as ready OBJ-2 discriminator")
