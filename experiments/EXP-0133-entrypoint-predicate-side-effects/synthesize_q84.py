#!/usr/bin/env python3
"""Correct Q82's current ledgers and synthesize the completed Q84 static trace."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path.relative_to(ROOT)} expected one target, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")

def replace_line(path: Path, prefix: str, new: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    hits = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(hits) != 1:
        raise SystemExit(f"{path.relative_to(ROOT)} expected one line prefix, found {len(hits)}")
    if lines[hits[0]] == new:
        return
    lines[hits[0]] = new
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> None:
    claims = ROOT / "research/CLAIMS.md"
    old466 = "| CL-L466 | In direct read-only parsing of the five official masters, 13 PERK entry DATA rows use selector 37 and 10 use selector 39; the matching rows use only EPFT function IDs 1 and 2, with raw EPFD payloads retained. | supported for the exact official five-master file screen | [EV-0675] | Duplicate records are not winner-resolved; Creation Club and user plugins, active load order, runtime invocation, and other selectors are outside this capture. The initial PRKE interpretation was corrected; only DATA/EPFT results are counted. |"
    new466 = "| CL-L466 | Retracted/superseded: the selector counts and raw payloads in the official five-master screen remain valid, but EPFT values 1/2 were incorrectly interpreted as handler IDs. EV-0683 shows the wrapper takes the handler ID from DATA[1]; EPFT selects the function-data class. See corrected CL-L471. | retracted by EV-0683 | [EV-0675], [EV-0683] | The direct capture remains valid and file-level rows are retained; it does not resolve active-profile winners, Creation Club/user plugins, or runtime invocation. |"
    old467 = "| CL-L467 | In GOG AE 1.6.1179.0, the captured entrypoint function-ID 1/2 handlers write or add numeric result values; each handler also invokes a typed function-data virtual predicate at vtable +8. | supported for the bounded captured handler bodies | [EV-0672], [EV-0676] | No direct equipment mutation, event queue, input, or yield appears in these bodies, but the typed predicate's side effects and runtime subclasses are unresolved. CommonLib labels are mutable and serve as names only. |"
    new467 = "| CL-L467 | In GOG AE 1.6.1179.0, generic handler-table IDs 1 and 2 resolve to SetValue/AddValue numeric-result bodies and each calls a function-data virtual at vtable +8; this generic fact does not map EPFT 1/2 to those handlers in the official selector rows. | supported for the bounded generic handler bodies; official-row attribution superseded by EV-0683 | [EV-0672], [EV-0683] | CommonLib labels are mutable and serve as names only. Official selector rows instead use DATA[1] IDs 1/3/14 [EV-0683], [EV-0684]. |"
    claims_text = claims.read_text(encoding="utf-8")
    if "| CL-L471 |" not in claims_text:
        if old466 in claims_text:
            claims_text = claims_text.replace(old466, new466, 1)
        if old467 in claims_text:
            claims_text = claims_text.replace(old467, new467, 1)
        claims.write_text(
        claims_text.rstrip()
        + "\n\n"
        + "| CL-L471 | For the 23 file-level official five-master PERK rows using selectors 37/39, DATA[1] handler IDs are 1 (one row), 3 (19 rows), and 14 (three file rows), while EPFT separately selects function-data classes 1/2. | supported for the exact official file screen and captured GOG wrapper mapping | [EV-0675], [EV-0683] | Duplicate/override rows remain file-level, not winning records; this does not establish Steam runtime dispatch. |\n"
        + "| CL-L472 | In GOG AE 1.6.1179.0, handlers 3 and 14 gate on OneValue/TwoValue class codes and update only the numeric entrypoint result directly; handler 14's two-value payload reads numeric ActorValue index 138 with coefficient about 0.01 for the three official selector-39 file rows. | supported for the bounded GOG bodies and exact official record bytes | [EV-0684] | ActorValue label 138 as BlockPowerModifier is a mutable CommonLib label; handler 14 calls an ActorValue getter whose miss path may update derived-value caches [EV-0685]. This is not a live or Steam result. |\n"
        + "| CL-L473 | The captured GOG handler-14 ActorValue getter can populate per-Actor and ActiveEffect derived-value caches on cache misses; the captured stores do not directly write permanent/temporary/damage ActorValue inputs, equipment, HitData, skill progress, or event state. | supported for the bounded direct cache path | [EV-0685] | The ActorValueInfo +0x68 callback target for runtime index 138 is unresolved because the pointer table is uninitialized in the static image; no transitive or Steam negative is claimed. |\n",
        encoding="utf-8",
        )

    mechanisms = ROOT / "research/MECHANISMS.md"
    mechanism_text = mechanisms.read_text(encoding="utf-8")
    mstart = mechanism_text.index("## M-0200 —")
    old_mechanism_prefix = "The official five-master file screen found 13 selector-37"
    pstart = mechanism_text.find(old_mechanism_prefix, mstart)
    pend = mechanism_text.index("\n\n## M-0201", mstart)
    replacement = (
        "The official five-master screen found 13 selector-37 and 10 selector-39 file rows, but EV-0683 corrects "
        "the field attribution: DATA[1] carries handler IDs 1 (one row), 3 (19 rows), and 14 (three file rows); "
        "EPFT separately selects function-data classes 1/2 [EV-0675], [EV-0683]. Generic handlers 1/2 remain "
        "mapped in EV-0672, but they are not the complete official-row handler set. The captured GOG IDs 3/14 "
        "gate on type-1/type-2 data objects and write numeric entrypoint results; ID14 additionally reads numeric "
        "AV index 138 and a coefficient from the TwoValue payload [EV-0684]. Its ActorValue getter can populate "
        "derived-value caches on a miss; direct stores observed in that bounded path target caches, not the "
        "underlying permanent/temporary/damage inputs, equipment, HitData, UseSkill/AVSK, or an event queue "
        "[EV-0685]. A dynamic ActorValueInfo callback remains unresolved, so this is not a global negative. No "
        "equipment-interposition window is identified in the captured GOG source path. The blocked branch routes "
        "AV9 and remains a separate control [EV-0222], [EV-0261]. No measured protection/AVSK result or qualifying "
        "OBJ-2 outcome is established; keep EV-0260 open. No OBJ-1 edge is added. Claims CL-L465, CL-L467, "
        "CL-L471–CL-L473."
    )
    if pstart >= 0 and pstart < pend:
        mechanism_text = mechanism_text[:pstart] + replacement + mechanism_text[pend:]
    old_header = "## M-0200 — Synchronous HitData mitigation-to-armor-skill phase order (EV-0670–EV-0676)"
    new_header = "## M-0200 — Synchronous HitData mitigation-to-armor-skill phase order (EV-0670–EV-0685)"
    if old_header in mechanism_text:
        mechanism_text = mechanism_text.replace(old_header, new_header, 1)
    mechanisms.write_text(mechanism_text, encoding="utf-8")

    contradictions = ROOT / "research/CONTRADICTIONS.md"
    replace_line(
        contradictions,
        "- **Model B:** mitigation, selector callbacks, worn-armor scan, and UseSkill routing execute synchronously in the same resolver pass;",
        "- **Model B:** mitigation, selector callbacks, worn-armor scan, and UseSkill routing execute synchronously in the same resolver pass; official selector DATA[1] IDs 1/3/14 update a numeric result, with ID14 reading an ActorValue and potentially maintaining derived-value caches.",
    )
    replace_line(
        contradictions,
        "- **Assessment:** Model B is supported and Model A is not identified within the exact GOG 1.6.1179.0 and official five-master scope.",
        "- **Assessment:** EV-0683 retracts the EPFT-as-handler interpretation: official rows use DATA[1] IDs 1/3/14, while EPFT selects the function-data class. Captured handler 3/14 bodies write numeric results; handler 14's ActorValue getter may write derived-value caches on a miss in the traced direct path [EV-0683]–[EV-0685]. No equipment or HitData writer, authoritative ActorValue setter, UseSkill/AVSK sink, or event submission is identified in the bounded code. The exact ActorValueInfo callback target for AV138 remains unresolved. Model A is not identified; Model B is supported as synchronous result computation, with the cache side effect and callback limit retained. Model C is supported only as branch routing; positive protection, landed-hit eligibility, raw AV9/AV11/AV12, and raw AVSK are unmeasured. No OBJ-2 exploit or global negative follows.",
    )

    graph = ROOT / "research/KNOWLEDGE_GRAPH.md"
    graph_text = graph.read_text(encoding="utf-8")
    gstart = graph_text.index("### Q-0082 — mitigation and the unblocked armor-skill selector")
    gend = graph_text.index("### Q-0083", gstart)
    graph_section = """### Q-0082/Q-0084 — mitigation, selector handlers, and the unblocked armor-skill scan (EV-0670–EV-0685)

The GOG path snapshots physicalDamage, applies AV39/armor-factor mitigation to totalDamage, then returns through synchronous builder callbacks into FUN_1406bcaa0. The resolver performs the player-receiver unblocked worn-ARMO scan and AV11/AV12 award branch in that same function; its later FUN_1406b9df0 call is a separate health/trap continuation [EV-0670], [EV-0673]. The selector 0x25/0x27 visitor runs synchronously [EV-0671]. Correction EV-0683 establishes that BGSEntryPointPerkEntry returns the handler ID from DATA[1], while EPFT chooses the function-data class; the 23 file-level official rows use IDs 1/3/14 and EPFT classes 1/2 [EV-0675], [EV-0683]. IDs 3/14 perform numeric-result calculations, and ID14 reads AV index 138 through ActorValueOwner [EV-0684].

Causal path retained: HitData mitigation -> synchronous selector visitor -> numeric result -> receiver worn-ARMO scan -> AV11/AV12 UseSkill, bounded to the GOG 1.6.1179.0 source and raw official five-master rows [EV-0670]–[EV-0685]. The ID14 getter may populate per-Actor and ActiveEffect derived-value caches on a miss. The captured direct cache stores do not write the source permanent/temporary/damage AV values, equipment, HitData, UseSkill/AVSK, or event state; the ActorValueInfo+0x68 callback for runtime AV138 remains unresolved [EV-0685].

Explicit no-edges: no causal edge from Q82/Q84 to OBJ-1 or Q81's Story Manager/condition path; no edge from cache maintenance or numeric selector results to a measured protection/AVSK result; and no edge from the AV9 route to a qualifying OBJ-2 outcome until EV-0260's landed-hit, positive-protection, and numeric XP measurements exist. Claim mapping: CL-L465, CL-L467, CL-L471–CL-L473 -> M-0200.

"""
    graph_text = graph_text[:gstart] + graph_section + graph_text[gend:]
    if "### Q-0084 — handler field correction" in graph_text:
        raise SystemExit("Q84 graph synthesis already exists")
    graph_text += """### Q-0084 — handler field correction and ActorValue cache side effect (EV-0681–EV-0685)

EPFT is not the handler ID. BGSEntryPointPerkEntry returns DATA[1] as the function ID and separately returns its function-data pointer; EPFT selects OneValue/TwoValue [EV-0681]–[EV-0683]. Official selector rows therefore select handlers 1/3/14. Handler 3 multiplies the numeric result using OneValue data. Handler 14 uses TwoValue data to read AV index 138 and coefficient about 0.01, then scales the numeric result [EV-0684].

Handler 14's ActorValue read is not memory-pure: a cache miss can fill Actor+0x150 and ActiveEffect-manager+0x30 derived-value caches [EV-0685]. The bounded captured stores are cache stores, not direct source AV, equipment, HitData, XP, or event writes. The default-value callback behind ActorValueInfo+0x68 is unresolved for runtime AV138 because the static image does not initialize the global pointer table. Keep this as an explicit uncertainty; no gameplay or Steam result follows. No OBJ-1 causal edge is added.
"""
    graph.write_text(graph_text, encoding="utf-8")

    (ROOT / "experiments/EXP-0133-entrypoint-predicate-side-effects/README.md").write_text("""# EntryPoint handler and function-data side effects

This experiment corrects the Q82 field interpretation and bounds the handler
path for official HitData selectors 37/39. BGSEntryPointPerkEntry returns
DATA[1] as the handler ID; EPFT selects the separate function-data class
[EV-0683]. The official file rows therefore use handler IDs 1, 3, and 14,
not operation IDs inferred from EPFT.

GOG handler 3 uses OneValue data and updates a numeric result. Handler 14 uses
TwoValue data, reads ActorValue index 138 and a coefficient, and updates the
numeric result [EV-0684]. On a getter cache miss, handler 14's ActorValue call
can populate per-Actor and ActiveEffect derived-value caches [EV-0685]. No
direct equipment, HitData, source ActorValue, armor skill-progress, or event
writer was identified in the bounded capture. The ActorValueInfo callback
target for AV138 is unresolved.

The scope is the existing read-only GOG project plus the official five-master
selector/EPFT/EPFD screen. This cannot establish Steam equivalence, profile
winners, a live hit, effective armor protection, raw AVSK, or a vanilla
exploit. EV-0260 remains open.
""", encoding="utf-8")

    (ROOT / "experiments/EXP-0133-entrypoint-predicate-side-effects/hypothesis.md").write_text("""# Competing models

## Q84-H1 — numeric handler with cache-only ActorValue maintenance

For the exact GOG path and official selector 37/39 rows, DATA[1] chooses the
handler and EPFT selects the function-data class. Handler IDs 1/3/14 compute
numeric entrypoint results; handler 14's ActorValue getter may maintain
derived-value caches on a miss but does not alter equipment, HitData, source
ActorValue inputs, skill progress, or queued gameplay state in the captured
path.

**Prediction:** exact wrapper, class, record, handler, and cache stores map to
the numeric result and derived-value caches. No authoritative gameplay writer,
UseSkill/AVSK sink, equipment mutation, HitData mutation, or event submission
appears in the captured path.

## Q84-H2 — relevant gameplay-state change

At least one matching handler, function-data implementation, or dynamic
ActorValueInfo callback changes equipment, HitData, source ActorValue state,
skill progress, or queued gameplay state before the later worn-armor scan.

**Prediction:** a producer-backed target reaches a relevant field store,
setter, progress sink, or event submission in the phase before
FUN_1406bcaa0 scans worn ARMO.

The captured direct bodies support H1 within the resolved scope [EV-0684],
[EV-0685]. The AV138 ActorValueInfo+0x68 callback remains unresolved, so H2 is
not globally excluded. No runtime or Steam behavior is inferred.
""", encoding="utf-8")

    (ROOT / "experiments/EXP-0133-entrypoint-predicate-side-effects/expected-discriminants.md").write_text("""# Expected discriminants

| Model | Evidence that would support it | Evidence that would weaken it |
|---|---|---|
| H1: numeric result plus cache maintenance | Wrapper DATA[1]/EPFT split is producer-backed; handlers 1/3/14 only update the numeric result; the ActorValue getter's stores are bounded to derived caches; no gameplay setter, award, equipment, HitData, or queue write appears. | A matching handler or its concrete getter callback writes equipment, HitData, source ActorValue, skill progress, or queued state before the armor scan. |
| H2: relevant gameplay-state change | A producer-backed official row and reachable handler/function-data path reaches a relevant gameplay-state writer in the correct hit phase. | Complete target/call mapping restricts direct writes to numeric results and derived-value caches; unresolved dynamic callbacks are separately bounded. |

EV-0684/EV-0685 support H1 for the captured GOG bodies and direct stores, with
the AV138 ActorValueInfo+0x68 callback still unresolved. This does not prove
positive protection, zero XP, a profile winner, Steam behavior, or a vanilla
reproduction; EV-0260 remains required.
""", encoding="utf-8")

    (ROOT / "experiments/EXP-0133-entrypoint-predicate-side-effects/protocol.md").write_text("""# Protocol

1. Read EXP-0131 results, then validate every GOG capture against the existing
   GOG AE 1.6.1179.0 executable hash, read-only mode, and disabled auto-analysis.
2. Keep wrapper fields distinct: DATA[0] is the selector, DATA[1] is the
   handler ID returned by BGSEntryPointPerkEntry, DATA[2] is a separate byte,
   and EPFT/EPFD specify function-data class and payload [EV-0683].
3. Reconcile all official selector-37/39 file rows with handler IDs 1/3/14 and
   EPFT classes 1/2; preserve duplicate rows and do not claim profile winners.
4. Inspect concrete handler bodies and type gates, then trace any ActorValue
   getter side effects to bounded cache helpers. Separate cache writes from
   source ActorValue, equipment, HitData, skill-progress, and event writes.
5. Preserve raw Ghidra stdout/metadata under ignored .local; never modify the
   GOG project, game files, plugins, saves, or co-saves.
6. Keep the unresolved AV138 ActorValueInfo+0x68 callback target explicit.
   Do not transfer GOG RVAs or static behavior to Steam AE.
7. Keep EV-0260's exact Steam test requirements: verified target and complete
   order, clean level-one save, ordinary matched hits, positive effective
   protection, raw AVSK and HitData observations, controls, and repetitions.
   Console forcing, injected scripts, and altered plugins are diagnostic only.
""", encoding="utf-8")

    (ROOT / "experiments/EXP-0133-entrypoint-predicate-side-effects/results.md").write_text("""# Results

## Field correction — EV-0683

The earlier Q82/Q84 interpretation treated EPFT values as handler IDs. The
build-identified BGSEntryPointPerkEntry wrapper shows slot +8 returns
DATA[1] as the handler ID and slot +0x10 returns a separate function-data
pointer. The GOG loader selects the function-data class from EPFT [EV-0681]–
[EV-0683]. The 23 official five-master rows for selectors 37/39 use IDs 1
(one row), 3 (19 rows), and 14 (three file rows); EPFT values 1/2 are class
IDs [EV-0675], [EV-0683]. The raw EV-0675 capture remains valid; its old
EPFT-as-handler interpretation is superseded.

## Actual handler bodies — EV-0684

Handler 3 at GOG RVA 0x386420 gates on function-data type 1 and multiplies the
numeric entrypoint result by the OneValue float at object +8. Handler 14 at
RVA 0x386870 gates on type 2, reads the TwoValue float at +8 as an ActorValue
index and the float at +0xC as a coefficient, then scales the numeric result
using ActorValue*coefficient plus a constant. The three file-level ID-14 rows
are selector-39 AlchemySkillBoosts and PerkSkillBoosts entries (the latter
also appears in Update.esm). Their payload bytes are
00 00 0A 43 0A D7 23 3C, encoding numeric index 138 and approximately 0.01.
CommonLib's mutable ActorValues.h labels 138 BlockPowerModifier; this is a
label reference only, without a pinned commit.

Handler 1 is the one DeflectArrows selector-39 row and is covered by EV-0672.
The captured direct handler writes are numeric result writes. The bodies do
not directly write equipment, HitData, source ActorValues, skill progress, or
event state.

## ActorValue getter side effects — EV-0685

Handler 14 calls ActorValueOwner slot +8 on its actor context. The captured
Actor getter checks an ActiveEffect derived-value cache, computes a value on
miss, sums modifier floats, and stores into the ActiveEffect cache. Its base
value virtual also reads and writes an Actor-side per-value cache. The traced
cache helpers store computed values and associated cache state; direct writes
are to derived caches, lock bookkeeping, or output arguments, not the source
permanent/temporary/damage ActorValue fields. No equipment, HitData,
UseSkill/AVSK, or event sink was identified in the bounded path.

The base-value path includes an indirect ActorValueInfo+0x68 default-value
callback. The static GOG image does not initialize the global ActorValueInfo
table pointer, so its runtime function target for index 138 is unresolved.
This is a concrete limit, not evidence of absence. The getter is therefore not
described as memory-pure, and the static result is not a transitive negative.

## Bounded assessment

The corrected GOG mapping supports synchronous numeric result computation for
the captured official rows and identifies cache-only writes on the traced
handler-14 getter path. It does not identify an equipment interposition
window or a direct source-AV/HitData/skill-progress writer before the
worn-armor scan. The dynamic ActorValueInfo callback, Steam differences,
active-profile winners, and runtime behavior remain open.

No positive armor protection, verified landed hit, raw AVSK change, zero-XP
result, level-one vanilla reproduction, or bounty resolution is established.
EV-0260 remains the exact Steam test requirement.
""", encoding="utf-8")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q84 = next(item for item in frontier["items"] if item["id"] == "Q-0084")
    if q84.get("status") != "in_progress":
        raise SystemExit("Q-0084 is no longer in progress")
    q84["question"] = (
        "Do the official HitData selector-37/39 rows with DATA[1] handlers 1/3/14 write authoritative gameplay "
        "state before the worn-armor scan, after separating numeric-result writes and handler-14 derived-value "
        "cache maintenance from source ActorValue, equipment, HitData, skill-progress, and queued-state changes?"
    )
    h1, h2 = q84["hypotheses"]
    h1.update({
        "model": (
            "For the captured GOG path and official selector rows, DATA[1] handlers 1/3/14 compute numeric results; "
            "handler 14 can populate derived-value caches on an ActorValue getter miss, but no authoritative "
            "equipment, HitData, source ActorValue, skill-progress, or queued-gameplay write occurs in the resolved path."
        ),
        "predicted_discriminant": (
            "The wrapper and data classes are producer-backed; handler bodies and the traced cache-miss path show "
            "numeric-result and derived-cache writes only, with no relevant gameplay setter or sink. Any unresolved "
            "dynamic ActorValueInfo callback is retained as a boundary."
        ),
        "status": "supported",
        "evidence": list(dict.fromkeys([*h1.get("evidence", []), "EV-0683", "EV-0684", "EV-0685"])),
    })
    h2.update({
        "model": (
            "A matching handler or its dynamic ActorValueInfo callback changes equipment, HitData, source ActorValue, "
            "skill progress, or queued gameplay state before the later worn-armor scan."
        ),
        "predicted_discriminant": (
            "A producer-backed target reaches a relevant gameplay writer, setter, award, or event submission before "
            "FUN_1406bcaa0 scans worn ARMO."
        ),
        "status": "proposed",
        "evidence": list(dict.fromkeys([*h2.get("evidence", []), "EV-0683", "EV-0684", "EV-0685"])),
    })
    q84["methods"] = [
        "Use DATA[0] as selector, DATA[1] as handler ID, DATA[2] as a separate byte, and EPFT/EPFD as function-data class/payload.",
        "Map all official selector-37/39 file rows to handler IDs 1/3/14 and preserve duplicate rows without winner claims.",
        "Trace handler bodies, data-type gates, numeric writes, and ActorValue getter cache helpers; distinguish cache maintenance from source AV and gameplay-state writes.",
        "Keep the ActorValueInfo+0x68 callback target unresolved unless an exact runtime or data-initialization source resolves it.",
        "Treat GOG/Steam comparison as cross-build static evidence and keep EV-0260's matched-hit/protection/raw-AVSK test open.",
    ]
    q84["evidence"] = list(dict.fromkeys([*q84.get("evidence", []), "EV-0684", "EV-0685"]))
    q84["linked_claims"] = ["CL-L465", "CL-L467", "CL-L471", "CL-L472", "CL-L473"]
    q84["next_action"] = (
        "After closing this bounded static line, begin Q-0085 on whether the Dragonborn world-cultist QUST's "
        "Solstheim location alternative permits level-one initiation after accounting for upstream stage and event "
        "selector conditions. Keep natural Steam verification under EV-0260."
    )
    q84["cross_source_assessment"] = (
        "EV-0683 corrects the wrapper field: BGSEntryPointPerkEntry returns DATA[1] as handler ID, while EPFT selects "
        "the function-data class. The 23 official file rows use IDs 1/3/14 and EPFT classes 1/2 [EV-0675], [EV-0683]. "
        "Captured handler 3/14 bodies calculate numeric results; handler 14 reads AV index 138 and a coefficient. "
        "Its getter can populate Actor and ActiveEffect derived-value caches on a miss; direct writes traced in that "
        "path do not alter source AV inputs, equipment, HitData, skill-progress, or queued state [EV-0684], [EV-0685]. "
        "A dynamic ActorValueInfo+0x68 callback remains unresolved because the GOG static image has no initialized "
        "global table pointer. No live protection, raw AVSK, Steam equivalence, active-profile winner, or OBJ-1 edge "
        "is established; EV-0260 remains open."
    )
    q84["attempts"].append({
        "action_key": "q84-handler-field-correction-and-actorvalue-cache-trace",
        "outcome": (
            "Corrected the handler/data-class field confusion, mapped actual GOG handler IDs 3/14 and official rows, "
            "and traced handler 14's ActorValue getter through ActiveEffect and Actor derived caches. The resolved "
            "direct stores are numeric outputs or derived caches; a runtime ActorValueInfo+0x68 callback remains "
            "unresolved."
        ),
        "evidence": ["EV-0683", "EV-0684", "EV-0685", "EV-0675", "EV-0670", "EV-0673"],
        "new_discriminant": (
            "The ActorValueInfo+0x68 callback target for AV138 cannot be resolved from the uninitialized static "
            "global table; retain it as a bounded uncertainty and proceed to the independent level-one location gate."
        ),
        "recorded_utc": "2026-10-20T02:50:00+00:00",
    })
    q82 = next(item for item in frontier["items"] if item["id"] == "Q-0082")
    q82["cross_source_assessment"] = (
        "Correction EV-0683 supersedes the Q82 interpretation that EPFT IDs 1/2 were official handler IDs. Official "
        "rows use DATA[1]=1/3/14, with EPFT class IDs 1/2 [EV-0675], [EV-0683]. Captured GOG IDs 3/14 compute numeric "
        "selector results; handler 14 can populate derived AV caches on a miss [EV-0684], [EV-0685]. No equipment "
        "interposition or direct source-AV/HitData/skill-progress writer is identified in the bounded path. This "
        "does not establish protection, XP suppression, Steam behavior, profile winners, or a vanilla exploit."
    )
    q82["evidence"] = list(dict.fromkeys([*q82.get("evidence", []), "EV-0683", "EV-0684", "EV-0685"]))

    q85 = {
        "id": "Q-0085",
        "objective": "OBJ-1",
        "kind": "mechanism",
        "status": "open",
        "question": (
            "Does the Solstheim location alternative in Dragonborn's DLC2WE09 world-cultist route permit level-one "
            "initiation once its preceding stage and event-selector conditions are satisfied, or does an upstream "
            "condition still block access below level 25?"
        ),
        "hypotheses": [
            {
                "id": "Q85-H1",
                "model": (
                    "The level and Solstheim conditions form an OR group, and an ordinary level-one arrival on "
                    "Solstheim can satisfy the location branch once earlier chance/stage conditions pass."
                ),
                "predicted_discriminant": (
                    "Raw CTDA and parent/node conditions show no additional pre-start level threshold, while exact "
                    "stage preconditions and the official travel route can be satisfied at level 1."
                ),
                "status": "proposed",
                "evidence": ["EV-0656", "EV-0657", "EV-0658", "EV-0664", "EV-0665", "EV-0666", "EV-0667", "EV-0668", "EV-0669"],
            },
            {
                "id": "Q85-H2",
                "model": (
                    "A preceding event selector, quest-state predicate, stage requirement, or access transition "
                    "prevents a level-one character from reaching the location alternative before level 25."
                ),
                "predicted_discriminant": (
                    "The exact parent/node/SCPT chain contains a necessary pre-start condition that cannot be "
                    "satisfied by the ordinary level-one route or the event QUST is not initiated by that branch."
                ),
                "status": "proposed",
                "evidence": ["EV-0654", "EV-0656", "EV-0657", "EV-0658", "EV-0664", "EV-0260"],
            },
        ],
        "methods": [
            "Read Q83's linked evidence, claims, contradiction, and EXP-0132 results before choosing new inputs.",
            "Reparse official parent/node/QUST records and condition bytes for DLC2WE09, preserving raw form IDs and file identity.",
            "Resolve preceding MQ105 and DLC2MQ06 stage comparisons, event chance, location form, and start timing from official records and available loose source.",
            "Verify the level-one Solstheim travel/access premise against a revision-pinned local source or authoritative record source; label it as a premise, not a reproduction.",
            "Keep natural Steam QUST start, alias, actor, and level observations under EV-0260; GOG evaluator use remains cross-build static inference.",
        ],
        "blocked_by": [],
        "evidence": ["EV-0654", "EV-0656", "EV-0657", "EV-0658", "EV-0664", "EV-0665", "EV-0666", "EV-0667", "EV-0668", "EV-0669", "EV-0260"],
        "priority": 0.99,
        "information_gain": 0.96,
        "next_action": (
            "Read the Q83 source artifacts and EXP-0132 result, then inspect exact DLC2WE09 stage comparisons, "
            "location FormID, parent/node selector conditions, and the ordinary level-one route to Solstheim. "
            "Separate the static OR expression from natural Steam event start; preserve EV-0260 as the runtime test."
        ),
        "linked_claims": ["CL-L462", "CL-L463", "CL-L464"],
        "successors": [],
        "attempts": [],
    }
    if any(item.get("id") == "Q-0085" for item in frontier["items"]):
        raise SystemExit("Q-0085 already exists")
    frontier["items"].append(q85)
    frontier["session_next_action"] = q84["next_action"]
    frontier["next_action"] = q84["next_action"]
    if isinstance(frontier.get("target"), dict):
        frontier["target"]["next_action"] = q84["next_action"]
    frontier["session_checkpoint"] = {
        "timestamp_utc": "2026-10-20T02:50:00+00:00",
        "task": "Q-0084/TX-20261020-0003: reconcile actual DATA[1] handler IDs, ActorValue cache side effects, and the unresolved runtime callback.",
        "next_action": q84["next_action"],
    }
    frontier["last_session_checkpoint"] = {
        "recorded_utc": "2026-10-20T02:50:00+00:00",
        "next_action": q84["next_action"],
        "active_process": "TX-20261020-0003",
    }
    frontier_path.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
    e684 = next(item for item in evidence_doc["items"] if item["id"] == "EV-0684")
    e684["tools"][0] = "python3 scripts/python_env.py run tools/ghidra_probe.py --pointer-table-rva 0x1FF7D88 --pointer-count 1 --timeout 600"
    e684["tools"][2] = "python3 scripts/python_env.py run tools/ghidra_probe.py --pointer-table-rva 0x1FF7E90 --pointer-count 1 --timeout 600"
    evidence_path.write_text(json.dumps(evidence_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("synthesized Q84 corrections, evidence links, and Q85 frontier item")

if __name__ == "__main__":
    main()
