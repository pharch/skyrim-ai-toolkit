#!/usr/bin/env python3
"""Add the DA07 pre-gate key hypothesis after Q92, without closing evidence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTIER = ROOT / "research/FRONTIER.json"


def main() -> int:
    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    if any(row.get("id") == "Q-0093" for row in frontier.get("items", [])):
        raise SystemExit("Q-0093 already exists")
    q93 = {
        "id": "Q-0093",
        "objective": "OBJ-1",
        "kind": "mechanism",
        "status": "open",
        "question": "Can a level-one player obtain Silus's Museum Key (KEYM 000960F0) before DA07's level-20 start and use it to enter the house, or is the reported Silus inventory conditioned on quest state?",
        "hypotheses": [
            {
                "id": "Q-0093-H1",
                "model": "Silus's base inventory, an initially available list, or a pre-gate script supplies the Museum key before DA07 starts; normal pickpocketing can therefore open the keyed house boundary at level one if Silus is accessible.",
                "predicted_discriminant": "Installed NPC/list/script data provide KEYM 000960F0 independently of the level-20 Story Manager path, and a later clean level-one test finds Silus present with the key pickpocketable and the door opening.",
                "status": "proposed",
                "evidence": ["EV-0267", "EV-0268", "EV-0269"]
            },
            {
                "id": "Q-0093-H2",
                "model": "The key is granted or carried only after quest-conditioned actor/alias setup; the UESP inventory listing does not establish pre-gate availability.",
                "predicted_discriminant": "The only identified grant/holder path depends on a DA07 stage or alias transition downstream of the level-20 route, and a clean level-one state lacks the key.",
                "status": "proposed",
                "evidence": ["EV-0267", "EV-0268", "EV-0269"]
            },
            {
                "id": "Q-0093-H3",
                "model": "The secondary source names Silus as the key holder, but installed static records cannot resolve the time-dependent inventory or actor availability needed for a pre-gate route.",
                "predicted_discriminant": "Static holder data remain indirect or incomplete; only an unforced level-one observation can decide Silus presence, pickpocket availability, key possession, and door access.",
                "status": "proposed",
                "evidence": ["EV-0260", "EV-0267", "EV-0269"]
            }
        ],
        "methods": [
            "Preserve the local UESP Keys, Pieces of the Past, Silus, and house page titles, revisions, timestamps, URLs, and only the relevant key-holder/level-gate passages; treat them as leads, not engine proof.",
            "With the exact installed AE target identified, screen Skyrim.esm NPC_ 000240CC, ACHR 000240CE, KEYM 000960F0, REFR 000240CA, all five official masters' direct key references, leveled inventory chains, VMAD, enable parents, and DA07 stage/alias writers.",
            "Inspect attached PEX only through the tested Skyrim - Misc.bsa extractor; do not infer Dawnguard archive absence, key absence, pre-gate accessibility, or a runtime result from an unsupported source route.",
            "Keep the static key-source result separate from actual level-one actor presence, pickpocket success, door opening, trigger entry, scene completion, and useful DA07 progression; retain EV-0260 for the clean candidate/control."
        ],
        "blocked_by": [],
        "evidence": ["EV-0109", "EV-0260", "EV-0267", "EV-0268", "EV-0269"],
        "priority": 1.0,
        "information_gain": 0.99,
        "next_action": "Reconcile the secondary UESP report that Silus carries KEYM 000960F0 with exact installed NPC/list/script records and Silus's level-gated enable path; determine whether any source can place the key with a reachable player before DA07 starts.",
        "linked_claims": ["CL-L098"],
        "successors": [],
        "attempts": [],
        "cross_source_assessment": "The local UESP key table reports Silus as holder without timing, while the prior exact official-master reference screen found no direct NPC inventory occurrence. The same house door requires that key and its internal Museum triggers can request quest stages before the level-20 Story Manager child, but the placed Silus actor is initially disabled and no runtime key/entry state is known. This is an OBJ-1 source conflict and candidate path only; no edge to the OBJ-2 skill-credit mechanisms is supported."
    }
    frontier["items"].append(q93)
    FRONTIER.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    index = ROOT / "experiments/README.md"
    content = index.read_text(encoding="utf-8")
    content += "\nEXP-0140 investigates whether Silus carries the DA07 Museum key before the level-20 start and whether a natural level-one key path can open the keyed house boundary; UESP's holder summary is not treated as proof of timing or gameplay.\n"
    index.write_text(content, encoding="utf-8")
    print(json.dumps({"added": "Q-0093", "status": "open", "experiment": "EXP-0140-da07-museum-key-pre-gate"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
