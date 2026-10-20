#!/usr/bin/env python3
"""Update Q81's tested hypotheses and queue the next independent OBJ-2 screen."""
from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
FRONTIER = ROOT / "research/FRONTIER.json"


def main() -> None:
    data = json.loads(FRONTIER.read_text(encoding="utf-8"))
    items = data["items"]
    q81 = next((item for item in items if item.get("id") == "Q-0081"), None)
    if q81 is None or q81.get("status") != "in_progress":
        raise SystemExit("expected active Q-0081")
    if any(item.get("id") == "Q-0082" for item in items):
        raise SystemExit("Q-0082 already exists; refusing duplicate")

    q81["question"] = "Does the Dragonborn cultist main-quest CLOC route have a player-level gate, and is the DLC2WE09 world-encounter level condition a hard threshold or a location alternative?"
    by_id = {hyp["id"]: hyp for hyp in q81["hypotheses"]}
    by_id["Q81-H1"]["model"] = "The inspected CLOC route and its native child QUST have no player-level CTDA, while the distinct DLC2WE09 world QUST contains a level/location OR group; a hidden startup or script gate may still exist outside these records."
    by_id["Q81-H1"]["predicted_discriminant"] = "Complete profile and runtime evidence show whether the CLOC QUST actually starts for a level-one player on its ordinary main-quest trigger and whether the world QUST Conditions are invoked at start."
    by_id["Q81-H1"]["evidence"] = ["EV-0654", "EV-0656", "EV-0660", "EV-0666", "EV-0668"]
    by_id["Q81-H2"]["predicted_discriminant"] = "A compiled active PEX, profile winner, verified Steam code path, or clean natural-start observation identifies a level predicate on the main CLOC route before its actual target transition."
    by_id["Q81-H2"]["evidence"] = ["EV-0653", "EV-0654", "EV-0655", "EV-0656", "EV-0660", "EV-0663", "EV-0669"]
    by_id["Q81-H3"]["status"] = "falsified"
    by_id["Q81-H3"]["predicted_discriminant"] = "Falsified: the official five-master records identify different child QUSTs under distinct CLOC and SCPT event branches (DLC2CultistAmbush 0403546D versus DLC2WE09 040331C0); shared script/global references and stage-10 handoff do not make them the same QUST or Story Manager child."
    by_id["Q81-H3"]["evidence"] = ["EV-0654", "EV-0656", "EV-0657", "EV-0658", "EV-0660", "EV-0661", "EV-0664"]
    q81["hypotheses"].append({
        "id": "Q81-H4",
        "model": "In GOG AE 1.6.1179.0 condition-list evaluation, the DLC2WE09 QUST's consecutive OR-flagged GetLevel >=25 and GetInCurrentLoc Solstheim rows form a trailing OR group, ANDed with the earlier chance/stage conditions; level 25 is not a hard requirement for every evaluation of that group.",
        "predicted_discriminant": "An exact Steam build mapping or ordinary level-one run with all earlier conditions satisfied distinguishes a genuine location alternative from a build/profile/start-timing difference; quest start and encounter selection must be observed separately.",
        "status": "supported",
        "evidence": ["EV-0657", "EV-0665", "EV-0666", "EV-0667", "EV-0668", "EV-0669"]
    })
    q81["methods"] = [
        "Compare exact official-five-master QUST, SMEN, SMQN, and SMBN identities, conditions, child links, stages, scripts, and state handoffs; never promote source-file presence to a profile winner.",
        "Decode CTDA operator and low-bit flags from raw bytes, then use build-attested condition-list code to test actual grouping; keep the GOG 1.6.1179 engine separate from Steam 1.6.1170 records and runtime.",
        "Treat the main CLOC QUST and world SCPT QUST as distinct routes even where source scripts share a stage handoff; distinguish quest start, alias fill, journal state, and actor spawn.",
        "Retain a clean level-one no-trigger/trigger control under EV-0260 with the exact active order, disposable save, and read-only observation. Console/Papyrus/plugin forcing is diagnostic only."
    ]
    q81["evidence"] = list(dict.fromkeys([*q81["evidence"], "EV-0666", "EV-0667", "EV-0668", "EV-0669"]))
    q81["next_action"] = "Resume only when EV-0260's exact Steam profile/full order, disposable level-one save, and read-only observation lane are available. Test the ordinary CLOC main-quest trigger and the world-encounter Solstheim OR route separately; record the exact transition, level, prerequisites, negative control, and repetition."
    q81["linked_claims"] = list(dict.fromkeys([*q81.get("linked_claims", []), "CL-L462", "CL-L463", "CL-L464"]))
    q81["cross_source_assessment"] = "Official-five-master SSEView records establish distinct CLOC and SCPT QUST children and the DLC2WE09 Conditions row order [EV-0654]–[EV-0664]. Raw CTDA bytes and revision-pinned TES5Edit decoding encode GetLevel >=25 plus OR on the following Solstheim location row [EV-0665]–[EV-0666]. The identity-checked GOG 1.6.1179 evaluator groups consecutive OR-flagged rows and ANDs that group with prior unflagged conditions [EV-0667]–[EV-0669]; this is a GOG static mechanism inference, not a Steam RVA transfer or quest-start/runtime result. EV-0663's loose PSC source shows a shared stage-10 handoff but is not compiled active PEX. The exact profile, active order, and natural level-one CLOC/world transitions remain unverified under EV-0260. No causal edge to armor XP or protection is supported."
    q81["successors"] = ["Q-0082"]

    items.append({
        "id": "Q-0082",
        "objective": "OBJ-2",
        "kind": "mechanism",
        "status": "ready",
        "question": "Is there a player-accessible interposition window between HitData protection calculation and the unblocked worn-armor AV11/AV12 UseSkill award, allowing armor to reduce a landed hit while no eligible armor is worn at skill selection?",
        "hypotheses": [
            {
                "id": "Q82-H1",
                "model": "A synchronous callback or player-accessible equipment transition can occur after protection is calculated but before the receiver scans worn armor, so the same hit could be mitigated by armor and then miss the Heavy/Light award selector.",
                "predicted_discriminant": "The GOG 1.6.1179 caller/order trace contains a synchronous callback or yield between mitigation and the worn-ARMO scan; a clean Steam event trace then shows positive armor-caused protection with no raw AV11/AV12 increment across repeated unblocked hits.",
                "status": "proposed",
                "evidence": ["EV-0222", "EV-0261", "EV-0285", "EV-0260"]
            },
            {
                "id": "Q82-H2",
                "model": "The damage and armor-skill branches execute synchronously from one HitData processing pass with no player-accessible state change between them; the receiver sees the same equipment state relevant to the hit.",
                "predicted_discriminant": "Disassembly shows only synchronous native calls between armor-factor mitigation and the receiver scan/UseSkill call, with script/event dispatch queued for later; ordinary equip/unequip actions cannot interleave before the award.",
                "status": "proposed",
                "evidence": ["EV-0222", "EV-0223", "EV-0261", "EV-0285"]
            },
            {
                "id": "Q82-H3",
                "model": "The apparent zero-armor-XP route is ordinary blocked-hit routing: armor mitigation occurs, but the blocked branch awards AV9 Block and skips AV11/AV12, so it is not a qualifying unblocked-hit XP bypass.",
                "predicted_discriminant": "The captured branch condition and a controlled hit trace show the attack is marked blocked, AV9 changes, and AV11/AV12 remain unchanged; an unblocked positive-damage hit with eligible armor still selects AV11/AV12.",
                "status": "supported",
                "evidence": ["EV-0222", "EV-0261", "EV-0260"]
            }
        ],
        "methods": [
            "Read EV-0222/EV-0223/EV-0261/EV-0285 raw captures and reconstruct exact source order from HitData population through AV39/armor-factor mitigation, receiver branch, worn-ARMO scan, Actor::UseSkill, and PlayerCharacter positive-points gate.",
            "Enumerate direct calls, virtual sites, callback/event queue submissions, and all paths between the protection write and AV11/AV12 selection; do not treat a queued Papyrus event as synchronous without evidence.",
            "Keep blocked hits as a control only: record AV9 Block separately and do not count a blocked/nonqualifying hit as a positive armor-XP bypass.",
            "If a plausible interposition exists, specify an ordinary player-accessible sequence and test it on verified Steam AE with a full active order, disposable level-one save, matched attack, positive Health/protection delta, and repeated numeric AVSK for Heavy/Light/Block under EV-0260."
        ],
        "blocked_by": [],
        "evidence": ["EV-0220", "EV-0221", "EV-0222", "EV-0223", "EV-0261", "EV-0285", "EV-0286", "EV-0287", "EV-0260"],
        "priority": 0.98,
        "information_gain": 0.92,
        "next_action": "Inspect EXP-0012 and EXP-0033 through EXP-0035 raw/captured GOG results, then query exact call order and indirect/event sites in FUN_1407ddf50 and FUN_1406b9df0. Locate any synchronous equipment mutation opportunity between the armor-factor application and the receiver's worn-ARMO AV11/AV12 selection; preserve GOG build identity and a bounded no-window result if none exists.",
        "linked_claims": ["CL-L067", "CL-L068", "CL-L069", "CL-L115", "CL-L116"],
        "cross_source_assessment": "The existing GOG source trace places AV39/armor-factor mitigation before blocked-flag handling and receiver skill routing [EV-0261]; the receiver scans positive base-DNAM worn armor and sends positive points to AV11/AV12, while the blocked branch routes to AV9 [EV-0222]–[EV-0223]. A cached snapshot, synchronous interposition callback, and ordinary block are competing models. No live Steam protection or numeric AVSK result is available [EV-0260], and no OBJ-1 causal edge is proposed.",
        "attempts": [],
        "successors": []
    })
    FRONTIER.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"updated": "Q-0081", "added_ready": "Q-0082", "q81_h3": by_id["Q81-H3"]["status"], "q81_h4": q81["hypotheses"][-1]["status"]}, indent=2))


if __name__ == "__main__":
    main()
