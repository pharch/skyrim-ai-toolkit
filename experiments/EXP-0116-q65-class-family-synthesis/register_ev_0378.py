#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
TX = ROOT / ".local/alignment/transactions/TX-20261018-0001"
SOURCES = [
    "EV-0331", "EV-0334", "EV-0336", "EV-0337", "EV-0342",
    "EV-0344", "EV-0346", "EV-0347", "EV-0348", "EV-0349",
    "EV-0350", "EV-0351", "EV-0352", "EV-0353", "EV-0354",
    "EV-0355", "EV-0356",
]
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data.rstrip() + "\n", encoding="utf-8")

def append_once(path: Path, marker: str, data: str) -> None:
    old = path.read_text(encoding="utf-8")
    if marker in old:
        raise SystemExit("duplicate append: " + marker)
    write(path, old.rstrip() + "\n\n" + data.strip())

def main() -> None:
    ep = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(ep.read_text(encoding="utf-8"))
    by_id = {item.get("id"): item for item in evidence["items"]}
    missing = [source for source in SOURCES if source not in by_id]
    if missing:
        raise SystemExit("missing linked evidence: " + ", ".join(missing))
    if "EV-0378" in by_id:
        raise SystemExit("EV-0378 already exists")

    result = """# Results — Q-0065 producer-backed class-family synthesis

## Question and competing models

Q-0065 asked whether PlayerCharacter +0x730, +0x8F8, +0x9D0, +0x9A0/+0x9A8, and ThirdPersonState +0xA0 share a concrete NiAVObject/NiNode finalizer family, or hold distinct data-selected scene/resource classes that happen to release through slot +0x8.

- H1 predicts exact producer-backed matching vtables and slot +0x8 targets for the cleanup values.
- H2 predicts exact differing tables or class provenance for those same values.
- A match requires the actual producer/result class for each field. A generic slot +0x8 call does not distinguish either model.

## Source-linked comparison

The identity-checked GOG AE 1.6.1179.0 evidence is bounded to the existing analysis executable SHA-256 {binary}; its RVAs do not transfer to Steam AE 1.6.1170.0.

- The NiNode parser candidate installs NiNode::vftable at RVA 0x19AC3F0. The +0x8F8 field loads the data-selected resource Actors\\Character\\1stPerson\\Skel, but no supported NIF inspection identifies that asset's root or descendants [EV-0331, EV-0347].
- PlayerCharacter +0x730 follows a refcounted scene-child attach/detach pattern compatible with NiAVObject. NiNode slot +0x1A8/+0x1C0 methods are structural comparators; the actual parent and child tables and child finalizer remain unresolved [EV-0334, EV-0351].
- ThirdPersonState +0xA0 receives the result of slot +0x150 on an object returned by PlayerCharacter slot +0x378. The context receiver vtable, result class, and result finalizer remain unresolved [EV-0336, EV-0337, EV-0342, EV-0344, EV-0346].
- PlayerCharacter +0x9D0 returns opaque descriptor-selected values; +0x9A0/+0x9A8 receives a generic model-resource result through a two-slot adapter and sorted-name lookup. Neither path identifies the selected object's vtable or +0x8 finalizer [EV-0348, EV-0349, EV-0350].
- As a class-family comparator, the ProcessTrapHit child factory installs hkpConstraintInstance::vftable at RVA 0x1973D58. Its wrapper children select bhkFixedConstraint or bhkMalleableConstraint tables at RVAs 0x19EB9C0 and 0x19F50A8; their +0x158 destructor targets differ. These are exact physics classes on the captured factory path, not identified producer tables for the PlayerCharacter cleanup fields [EV-0355, EV-0356].
- Thus the observed physics tables show why slot +0x8 alone is not a class identity test. They do not prove that any unresolved cleanup field holds one of those classes or a class distinct from the other cleanup fields.

## Decision and limits

Neither Q65-H1 nor Q65-H2 wins. The source comparison separates known NiNode and physics table identities, but does not recover concrete producer-backed vtables for the target cleanup fields. No mapped descendant adds a direct Actor::UseSkill AV11/AV12 edge; unresolved field and child finalizers prevent a route-wide negative. No causal edge to OBJ-1 is supported.

This static line is blocked pending either a tested read-only NIF root inspector for the exact first-person skeleton asset and equivalent source-selected model roots, or verified same-build runtime class telemetry for the exact objects. Continue independent OBJ-1 and P0 static work while that discriminator is unavailable.
""".format(binary=BINARY)
    write(EXP / "results.md", result)
    write(EXP / "README.md", """# EXP-0116 — Q-0065 class-family synthesis

Compare exact producer evidence for scene/resource cleanup fields with the mapped GOG physics constraint classes. Preserve unresolved dynamic class boundaries and do not infer identity from slot +0x8.
""")
    write(EXP / "hypothesis.md", """# Competing models

- H1: the targeted cleanup values share a concrete NiAVObject/NiNode family; exact producer/result tables and finalizers match.
- H2: the target values are distinct data-selected resources that share only the generic refcount release slot.
- A match or mismatch requires the concrete class of each target field. Generic slot +0x8 behavior is inconclusive.
""")
    write(EXP / "protocol.md", """# Protocol

Review the linked build-attested GOG producer, parser, setter, and finalizer traces. Compare exact class tables only where the source establishes the producer and receiver. Keep the Steam runtime separate. Record a no-edge rationale when class identity or skill-progress reachability is not established.
""")
    write(EXP / "expected-discriminants.md", """# Expected discriminants

- H1: each targeted field has a source-backed producer/result vtable in the same NiAVObject/NiNode family and matching finalizer chain.
- H2: exact producer evidence shows different class tables/finalizers for target fields.
- Neither: resource/data-selected class remains unknown. A separate known physics table is a class comparator, not a verdict about the target fields.
""")
    write(EXP / "implications.md", """# Implications

The captured physics constraint classes are distinct exact table identities, but they do not type the target cleanup fields. Preserve Q65-H1/H2 as proposed and continue OBJ-1/OBJ-2 through other tractable lines. The exact next discriminator is a supported NIF/model-root inspector or verified same-build runtime vtable observation.
""")

    note = TX / "EV-0378-note.md"
    write(note, """# EV-0378 — Q-0065 class-family comparison boundary

## Scope and provenance

This is a synthesis of existing read-only GOG AE 1.6.1179.0 traces, all tied to analysis executable SHA-256 {binary}. It adds no new binary, game, or runtime observation. The installed Steam AE 1.6.1170.0 build and GOG analysis build remain distinct.

## Rival models and discriminant

Q65-H1 requires exact producer-backed matching vtables/finalizers across the targeted cleanup fields. Q65-H2 requires exact producer-backed mismatches. A shared refcount slot +0x8 is compatible with both and is not a discriminant.

## Result

The NiNode candidate table at RVA 0x19AC3F0 is source-backed as a NIF parser registration, but the exact +0x8F8 asset root is not parsed [EV-0331, EV-0347]. The +0x730 path is structurally compatible with a NiAVObject scene child, while its actual parent/child class tables remain unknown [EV-0334, EV-0351]. The ThirdPersonState +0xA0 result and the +0x9D0/+0x9A0/+0x9A8 values remain context- or resource-selected [EV-0336, EV-0337, EV-0342, EV-0344, EV-0346, EV-0348, EV-0349, EV-0350].

The ProcessTrapHit factory installs an exact hkpConstraintInstance table at RVA 0x1973D58 and creates bhkFixedConstraint/bhkMalleableConstraint wrappers with separate tables at 0x19EB9C0/0x19F50A8 and different +0x158 destructor targets [EV-0355, EV-0356]. This establishes distinct physics class identities in that branch, but does not identify any of the target cleanup-field producers. The compared exact classes demonstrate why a generic +0x8 release ABI cannot prove shared class identity.

Neither Q65 model is selected. No direct Actor::UseSkill AV11/AV12 sink is mapped in the bounded callbacks, but unresolved resource and child finalizers prevent a global negative. No OBJ-1 causal edge is supported.

## Next discriminator

A tested read-only NIF/model-root inspection for the exact loaded resources or exact same-build runtime class telemetry is required to identify the target values. Keep Steam runtime observations separate from GOG static evidence.
""".format(binary=BINARY))

    docs = [EXP / name for name in (
        "README.md", "hypothesis.md", "protocol.md",
        "expected-discriminants.md", "results.md", "implications.md",
    )]
    local_hashes = {
        path.relative_to(ROOT).as_posix(): sha(path)
        for path in docs + [Path(__file__).resolve(), note]
    }
    manifest = {
        "evidence_id": "EV-0378",
        "synthesis_only": True,
        "source_evidence_ids": SOURCES,
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY,
        "registered_local_hashes": local_hashes,
    }
    mp = TX / "EV-0378-source-manifest.json"
    write(mp, json.dumps(manifest, indent=2, ensure_ascii=False))
    local_hashes[mp.relative_to(ROOT).as_posix()] = sha(mp)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0378",
        "kind": "native",
        "source": "Source-linked synthesis of build-attested GOG Ghidra producer, parser, and cleanup traces; no new runtime capture.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261018-0001/EV-0378-note.md",
        "sha256": sha(note),
        "runtime": "Existing GOG AE 1.6.1179.0 static traces; distinct from Steam AE 1.6.1170.0; synthesis adds no runtime observation.",
        "lane": "mechanism_inference",
        "tools": ["research evidence, claims, mechanisms, experiment and frontier review"],
        "coverage": "Bounded comparison of NiNode, PlayerCharacter cleanup-field producer paths, and ProcessTrapHit physics constraint vtables.",
        "result": "Known physics constraints have exact distinct tables, but the target cleanup fields remain data-selected; neither shared NiNode-family nor distinct-target-family model is resolved. Common slot +0x8 release behavior is not class identity.",
        "related_evidence": SOURCES,
        "local_hashes": local_hashes,
    })
    write(ep, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims = ROOT / "research/CLAIMS.md"
    append_once(claims, "| CL-L218 |", "| CL-L218 | In the compared GOG AE 1.6.1179.0 source paths, the ProcessTrapHit factory installs hkpConstraintInstance and separate bhkFixedConstraint/bhkMalleableConstraint tables, while concrete producer vtables for PlayerCharacter +0x730/+0x8F8/+0x9D0/+0x9A0/+0x9A8 and ThirdPersonState +0xA0 remain unresolved. The shared slot +0x8 release ABI does not decide whether those target fields share a class family. | supported for the compared static scopes | [EV-0378], [EV-0331], [EV-0334], [EV-0336], [EV-0347], [EV-0349], [EV-0350], [EV-0355], [EV-0356] | A supported exact NIF/model-root parse or same-build runtime vtable for the target values could establish a match or mismatch; no Steam behavior or global AV11/AV12 negative follows. |")
    mechanisms = ROOT / "research/MECHANISMS.md"
    append_once(mechanisms, "## M-0077 — Q-0065 class-family comparison boundary", """## M-0077 — Q-0065 class-family comparison boundary

The captured ProcessTrapHit factory installs hkpConstraintInstance and wraps it with either bhkFixedConstraint or bhkMalleableConstraint; the wrapper tables are distinct and their +0x158 destructor targets differ [EV-0355], while the exact hkpConstraintInstance table and slot+0x30 behavior are mapped [EV-0356]. These physics identities do not type PlayerCharacter +0x730, +0x8F8, +0x9D0, +0x9A0/+0x9A8, or ThirdPersonState +0xA0. The latter paths remain structural or data-selected [EV-0331], [EV-0334], [EV-0336], [EV-0347], [EV-0348], [EV-0349], [EV-0350]. Therefore Q65-H1/H2 remain proposed; common slot+0x8 dispatch is not a class edge. No direct Actor::UseSkill AV11/AV12 descendant is established in the mapped bounded branch, and unresolved finalizers prevent a route-wide negative. Claim CL-L218 -> M-0077; Q-0065.""")
    graph = ROOT / "research/KNOWLEDGE_GRAPH.md"
    append_once(graph, "### Q-0065 class-family comparison boundary (EV-0378)", """### Q-0065 class-family comparison boundary (EV-0378)

The exact ProcessTrapHit physics tables are distinct from the NiNode parser candidate, but no source edge identifies those tables as the producer of the PlayerCharacter or ThirdPersonState cleanup values. Keep the class-family edges among those values unresolved: common slot +0x8 release behavior does not prove shared type. No direct Actor::UseSkill AV11/AV12 edge is added for the bounded descendants; unresolved resource/finalizer targets prevent a route-wide negative. No causal edge to OBJ-1 is supported [CL-L218].""")

    readme = ROOT / "experiments/README.md"
    append_once(readme, "EXP-0116 / EV-0378", "EXP-0116 / EV-0378 compares exact mapped physics tables with the still data-selected cleanup fields. Q65-H1/H2 remain proposed; common slot +0x8 is not a class discriminator.")
    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q65 = next(item for item in frontier["items"] if item.get("id") == "Q-0065")
    if q65.get("status") != "in_progress":
        raise SystemExit("Q-0065 is not in progress")
    for collection, value in ((q65.setdefault("evidence", []), "EV-0378"), (q65.setdefault("linked_claims", []), "CL-L218")):
        if value not in collection:
            collection.append(value)
    for hypothesis in q65["hypotheses"]:
        if "EV-0378" not in hypothesis.setdefault("evidence", []):
            hypothesis["evidence"].append("EV-0378")
    q65.setdefault("successors", []).append("Q-0066")
    q63 = next(item for item in frontier["items"] if item.get("id") == "Q-0063")
    if "Q-0066" not in q63.setdefault("successors", []):
        q63["successors"].append("Q-0066")
    if any(item.get("id") == "Q-0066" for item in frontier["items"]):
        raise SystemExit("Q-0066 already exists")
    frontier["items"].append({
        "id": "Q-0066",
        "objective": "OBJ-1",
        "kind": "mechanism",
        "status": "open",
        "question": "When the Fort Dawnguard dialogue callback requests DLC1VQ01.SetStage(10), do the Quest.SetStage entry and EnsureQuestStarted guards permit startup of the stopped, start-disabled VQ01 quest, or can this path only stage an already-running quest?",
        "hypotheses": [
            {
                "id": "Q66-H1",
                "model": "The registered Quest.SetStage callback conditionally calls EnsureQuestStarted in start-now mode before applying stage 10; VQ01's source event and entry fields allow the mapped Fort path to initiate the quest below level 10.",
                "predicted_discriminant": "Exact VQ01 QUST flags/ENAM and native callback predicates satisfy the stopped-state startup branch with no level comparison; a clean level-one Fort dialogue test then shows a real running-state transition, stage 10, filled aliases, and useful Dimhollow access.",
                "status": "proposed",
                "evidence": ["EV-0313", "EV-0326"],
            },
            {
                "id": "Q66-H2",
                "model": "A SetStage event/ready-bit or EnsureQuestStarted eligibility guard rejects VQ01 while stopped/start-disabled, so the Fort callback does not initiate the actual quest even though it requests stage 10.",
                "predicted_discriminant": "The exact VQ01 record inputs fail a native startup guard or a clean level-one run leaves the quest stopped and aliases unfilled after the natural dialogue chain.",
                "status": "proposed",
                "evidence": ["EV-0313", "EV-0326"],
            },
        ],
        "methods": [
            "Read EV-0313/EV-0314 and EXP-0055/EXP-0056 before new probes; preserve the distinction between Quest.SetStage and Quest.SetCurrentStageID.",
            "Resolve the exact DLC1VQ01 QUST identity and source fields, including Start Game Enabled, ENAM, and stage/alias conditions, in the fixed official-master scope.",
            "Trace the registered GOG SetStage callback's entry predicate, EnsureQuestStarted return guards, BeginStartUpQuest call, and stage-writer preconditions; do not transfer GOG RVAs to Steam.",
            "State a separate exact Steam AE 1.6.1170.0 clean level-one runtime test with no setstage/startquest, script injection, or modified records.",
        ],
        "blocked_by": [],
        "evidence": ["EV-0313", "EV-0314", "EV-0326", "EV-0260"],
        "priority": 0.99,
        "information_gain": 0.97,
        "next_action": "Reconcile VQ01's exact official-source QUST fields with EV-0313's SetStage startup guard, then query the helper's remaining eligibility predicates and compare them with VQ01. Record the clean level-one runtime discriminator separately; keep any GOG result static and build-scoped.",
        "linked_claims": ["CL-L105", "CL-L157"],
        "successors": [],
        "attempts": [],
        "cross_source_assessment": "OBJ-1 Dawnguard stage request and OBJ-2 armor/HitData research have no supported shared call or state edge in inspected evidence.",
    })
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))
    print("registered EV-0378 / CL-L218 / M-0077 and opened Q-0066")
if __name__ == "__main__":
    main()
