# Rolling Research Roadmap

This is a *map of Skyrim AE research programs*, not a fixed completion
checklist. Rebuild it after major discoveries and at regular synthesis
checkpoints. Do not reuse non-AE evidence without an AE-specific verification.

## A. Objective 1 — Level-gated world / quest triggers (P0, main focus)

1. Compile a version- and DLC-aware inventory of level-gated quests and encounters using AE records, UESP revisions, and imported historical reports with explicit provenance.
2. Classify gates: dialogue condition, story-manager event condition, native/event callback, leveled spawn list, alias fill, trigger box, Papyrus check, delayed timer, encounter-zone state, save-state cache.
3. Find the authoritative enforcement path per representative gate. Identify whether there is a player-level read, an intermediate snapshot, or an alternate entry point.
4. Derive a *vanilla-accessible* manipulation/ordering/composition that bypasses a gate without `setstage`/mod edits as final solution.
5. Test against uninstrumented clean saves; generalize across multiple gates only after evidence.

## B. Objective 2 — Wear any armor with zero XP from hits (P0)

1. Establish a controlled repeatable attack protocol and measure armor skill XP directly before/after.
2. Separate damage reduction, contact registration, armor classification, and skill-use routing.
3. Trace event and native XP grant path in Ghidra / SKSE / game records as supported by available binaries.
4. Seek independent switch, state, temporary effect, actor flag, race/perk mechanism, or timing trick that blocks XP without disabling armor protection.
5. Validate both armor types and distinct hit sources.

Near-term OBJ-2 discriminator: resolve the remaining bounded caller uncertainty for the normal HitData/AV9/AV11/AV12 resolver while keeping the blocked-hit candidate distinct from the already mapped ProcessTrapHit route. EXP-0122 establishes a tag-0xB event callback and a separate Actor-state caller into the known resolver, but neither route proves ordinary enemy-hit coverage (EV-0291, EV-0397). The decisive check remains a verified Steam hit with a qualifying block, positive measured armor protection, AV9/AV11/AV12 instrumentation, and raw AVSK deltas after EV-0260 prerequisites are available.

## C. Enchanting with tiny XP budget (P1)

Trace native crafting XP computation; measure discontinuities and edge cases; integrate known numeric/ULP research; verify cumulative thresholds across 15→16 and 20→21.

## D. Permanent alchemy (P1)

Trace duration, ActiveEffect lifetime and serialization; compare poison vs potion application and numeric shifting; differentiate true indefinite instance from sustained/reapplied effects.

Current bounded result: EV-0279 shows GOG base ActiveEffect save/load routines persist elapsed/duration/magnitude/flags, references, and usUniqueID; base Update/Finish are stubs. This does not establish functional persistence or the installed Steam behavior. A same-build ActiveEffect observer and designated test save remain necessary; keep this P1 work behind the active OBJ-1/OBJ-2 P0 loop.

## Shared workstreams

- Source verification (UESP and Discord, explicit attribution and conflicting observations).
- Record-layer truth (xEdit, full active load order, binary data).
- Native code pathways (Ghidra offsets/version provenance).
- Runtime instrumentation (DevBench, SKSE probes, possible SkyLink MCP bridge).
- Session durability, causal graph, hypotheses, experiment lifecycle, and synthesis.

## Synthesis checkpoint — 2026-10-18

EV-0330 resolves one PlayerCamera HUD callback away from native skill progress. EV-0331, EV-0332, and EV-0333 map conditional/resource producers but leave data-selected classes unresolved. Armor-hit and enchanting routes share Actor::UseSkill through distinct producers [EV-0217]–[EV-0223], [EV-0280], [EV-0281]. No shared call/data edge links current Q-0064 teardown branches to that sink, while unresolved dynamic targets prevent a global negative. The mapped Dawnguard Fort route has no observed ActorValue dependency [EV-0326]. Continue one bounded +0x730 callback trace, then reselect the highest-information P0 line; retain exact Steam damage/protection/raw-AVSK and level-one transition tests as open runtime discriminants.

EV-0334 maps the +0x730 cell transition to a NiNode candidate child attach/detach operation, with child+0x30 as the parent link; the concrete runtime vtable and child finalizer remain unresolved. Together with the conditional +0x8F8 NiNode candidate [EV-0331] and +0x9A0/+0x9A8 model adapter [EV-0333], this creates a falsifiable cross-field class-family question Q-0065. Refcount slot similarity alone does not establish a shared type. Continue Q-0064's exact finalizer discriminator, then reselect among the P0 frontier.

EV-0335 maps PlayerCamera+0x28 as the active state pointer and resolves the index-9 ThirdPersonState slot+0x10 callback to FUN_1408e9990. This is a camera-state transition path, distinct from the NiNode candidate at +0x730 and model/skeleton resource paths at +0x8F8/+0x9A0/+0x9A8. Two direct helpers, the nested +0xA0 finalizer, other state callbacks, and the teardown-selected state remain unresolved. Continue Q-0064; do not infer a global no-skill result.

EV-0336 maps ThirdPersonState+0xA0 to a dynamic child-resource lookup via PlayerCharacter slot+0x378 and the returned object's slot+0x150. NiNode implements the same slot as recursive child traversal, creating a conditional common-family hypothesis with +0x730 and +0x8F8; the actual receiver and member finalizer are still unknown. Q-0065 now includes this fourth candidate. Q-0064 remains active on the exact receiver/finalizer and AV11/AV12 path.

## Q-0064 update — 2026-10-18

EV-0364 corrects attachment: constraint +0x10 receives endpoint +0x130, endpoint +0x100/+0x108 stores records, and constraint +0x60 points back. Typed island initialization, EntityPtrs serialization, insertion and merge support hkpSimulationIsland ownership. Continue with callback +0x40/+0x48 producers and concrete callback/member descendants; keep Steam positive-damage/effective-protection/raw-AVSK testing open. OBJ-2 evidence only; no edge to OBJ-1.

EV-0365 rejects one +0x40/+0x48 callback-writer candidate as a separate constraint-data payload. The ProcessTrapHit constructor path still dispatches wrapper slots +0x128/+0x188; resolve those exact class tables before concluding about callback population.

EV-0366 resolves the ProcessTrapHit fixed/malleable setup slots through pointer/backlink/refcount behavior and confirms two hkpConstraintInstance constructor families start callback arrays empty. Whole-program +0x40/+0x48 scans are broad; FUN_140b91bb0's apparent +0x48 field is part of one 16-byte copy from +0x40. Inspect the exact hkpConstraintInstance vtable 0x141973d58 and overlapping writer callers next; later callbacks/finalizers and AV11/AV12 remain open. Claim CL-L206 -> M-0085.

EV-0367 confirms that hkpConstraintInstance slot-0 finalization dispatches every non-null +0x40/+0x48 callback entry through entry slot +0x18, compacts nulls and frees the array. No concrete entry class or AV11/AV12 descendant is identified. Cross-screen exact writer candidates and world-attach provenance next. Claim CL-L207 -> M-0086.

EV-0368 confirms the ProcessTrapHit creation-time reference balance: hkp instance count 1 -> wrapper retain 2 -> temporary release 1 without callback dispatch. Later releases and exact writers remain open. Claim CL-L208 -> M-0087.

EV-0369 classifies six hkp-region same-offset candidates as curve or constraint-data layouts. The direct writer candidate lists intersect in 1,271 functions; callback production remains open. Claim CL-L209 -> M-0088.

EV-0370 maps chain-instance removal and final-delete callbacks through the inherited array; callback producers and ProcessTrapHit ownership remain open. Claim CL-L210 -> M-0089.

EV-0371 does not establish a ProcessTrapHit owner edge for the chain factory. Resume Q-0064 at the exact hkpConstraintInstance callback writer and keep the chain relation unresolved [CL-L211].

EV-0372 confirms FUN_140b48150 writes transform vector data on the separate constraint-data receiver, not the callback array. Continue Q-0064 with receiver-backed candidates [CL-L212].

EV-0373 finds that the B49260 candidate belongs to a typed record/list path, with no callback-array or ProcessTrapHit edge. Return Q-0064 to the exact teardown indirect callsites [CL-L213].

EV-0374 confirms no causal bridge between the examined DA04 and physical-trap paths; keep the DA04 level-one and trap protection/raw-AVSK tests separate. Q-0064 proceeds at the exact +0x8F8 resource finalizer [CL-L214].

EV-0375 bounds one ProcessTrapHit constraint detach branch to callback notification and endpoint record removal; callback targets remain unresolved. Continue Q-0064 at a concrete PlayerCharacter teardown field [CL-L215].

EV-0376 leaves the candidate idempotent listener helper unowned: no analyzed direct caller or ProcessTrapHit manager link is identified. Continue with the constructor-attested +0xB8 vtable slot census [CL-L216].

EV-0377 leaves the ProcessTrapHit listener method unlinked: displayed +0xB8 callsites have untyped/different receivers, and the scan output is capped. Resume after exact resource/runtime class evidence becomes available [CL-L217].

EV-0397 maps two captured GOG callers into the normal HitData receiver resolver: a tag-0xB event callback and a separate Actor-state/current-process callback. EV-0423 corrects the worker census to 95 unique direct callers, 33 decompiled bodies, and 62 uninspected bodies; the reported 64 is a storage cap. None of the inspected bodies constructs tag 0xB. The repeated pointer table and its single-xref non-function data entry do not identify the second callback's owner, so ordinary physical-hit coverage remains unresolved. Keep this candidate separate from ProcessTrapHit's direct bypass of the known AV11/AV12 wrapper. The practical Steam protection/raw-AVSK discriminator remains blocked by EV-0260. No shared OBJ-1 edge is supported.

## Synthesis checkpoint — 2026-10-18 (Q-0078)

EV-0422 maps the five-master MS06/MS06Start dialogue, trigger, and scene route. The helper's early scenes advance the helper and rumor quests; the explicit Falk-note request to main MS06 stage 10 conditionally fails the GOG initial SetStage guard. The trigger-script extraction miss and natural scene scheduling remain unknown, and Steam level-one state is still unobserved. No shared native call, ActorValue, HitData field, ActiveEffect, or serialized dependency links this OBJ-1 route to M-0009 or M-0096; preserve a no-edge rationale rather than inferring a cross-domain mechanism.

Next Q-0079 resumes OBJ-2 at the 62 exact worker callers not decompiled in EV-0397 [EV-0423]. The first discriminator is whether any remaining body constructs the tag-0xB payload that reaches the mapped AV9/AV11/AV12 resolver; even a match is only an event route until ordinary-hit coverage, protection, and raw AVSK are separately observed. Keep the exact Steam matched-hit protocol in EV-0260 open.

## Synthesis checkpoint — 2026-10-19 (Q-0079)

The worker caller sample now spans four mechanistically distinct routes: tags 0x24/0x25/0x27 reach Havok broadphase overlap/filter maintenance; tag 0x28 performs positive-only recursive scalar/property updates; tag 0x3C traverses child objects, invokes a callback, and changes a returned object's reference count. The tag-0x28 and tag-0x3C routes share child-array offsets +0x118/+0x122 and parent virtual slot +0x18, but their callback/value slots and builder arguments differ; this supports only a structural analogy, not a common runtime class [EV-0477], [EV-0478], [EV-0480], [EV-0481], [EV-0482]–[EV-0487], [CL-L303]. These heterogeneous event payloads use the same worker dispatcher without a mapped shared HitData, ActorValue, effective-protection, or armor-XP edge. The GOG-only tag-0x3C chain also preserves an ABI/decompiler discrepancy: disassembly passes a callback in R8 where pseudocode omits it [CL-L302].

Four consecutive inventoried caller bodies directly invoke the worker while their incoming-call scans report zero xrefs. Inventory membership and direct body disassembly independently establish these as callers; the query/index discrepancy's cause and prevalence remain unresolved [EV-0476], [EV-0479], [EV-0480], [EV-0482]. Keep the mismatch as a tooling/evidence issue rather than using zero xrefs to exclude a caller. Continue the exact census at `FUN_140657fc0`; the decisive OBJ-2 discriminator remains an ordinary verified hit observed with effective protection and raw AVSK on exact Steam AE, which is currently unavailable under EV-0260.

EV-0488 adds a neighboring tag-0x4C builder whose three captured callers use `FUN_1406d4110` to choose between worker enqueue and a direct call to common helper `FUN_1406940d0`; dispatcher case 0x4C targets that helper too [EV-0397], [EV-0488]. This bounds the preceding four zero-xref results to a repeated local observation and shows the shared gate wraps heterogeneous event handlers. The call graph does not yet establish the helper's behavior or any HitData/ActorValue edge. Continue at `FUN_1406940d0` (RVA 0x6940d0), then return to the exact worker census at `FUN_140658000`; the caller sample is 24/62, with 38 remaining.

EV-0489 traces `FUN_1406940d0` to conditional process/context +0x15c value updates, a composed-value call into the previously mapped `FUN_14065c6e0` broadphase route, and a second object/value call into `FUN_140e8f210`. Its direct scan has no mapped HitData or ActorValue handler; six indirect sites and the second helper remain open [EV-0477], [EV-0478], [EV-0489]. This creates a static cross-link from tag 0x4C to the tag-0x24/0x25/0x27 event-value/physics family, while leaving tag 0x28 similarity unresolved. Next inspect `FUN_140e8f210` at RVA 0xe8f210, then resume the exact worker census at `FUN_140658000`; no ordinary-hit, protection, AVSK, or armor-XP result is established.

EV-0490 shows `FUN_140e8f210` packs two 32-bit values and forwards them to `FUN_140e90750`; its 11 direct callers include both tag-0x4C helper `FUN_1406940d0` and tag-0x0D target `FUN_140712d10`, plus the dispatcher and other Actor/process functions [EV-0454], [EV-0489], [EV-0490]. EV-0491 resolves the target as a recursive packed-value update that shares the object-tree selector, record lookup, child offsets, and parent slot observed in tag 0x28, while using different per-node semantics (bit replacement and +0x2c write versus positive-float multiplication and setter) [EV-0480], [EV-0481], [EV-0491]. This supports a recurring traversal/update substrate, not a common dynamic class or identical gameplay effect. Its update chain also reaches the previously mapped event-value/Havok broadphase helper; two indirect sites and source-less DATA refs remain unresolved. The exact worker census now resumes at `FUN_140658000` (24/62 reviewed, 38 remaining); no armor-XP or effective-protection result is established.

EV-0492 maps worker caller `FUN_140658000` as tag 0x4D. Its producer `FUN_1407bcdf0` uses `FUN_1406d4110` to select queueing or an immediate call to `FUN_140e8fc90`, and dispatcher case 0x4D invokes the same helper [EV-0490], [EV-0492]. EV-0493 resolves that helper as a paired-object mechanism: on a matching node it calls `FUN_140e90750` for a packed recursive update; on an unmatched `param_9` branch it constructs a Havok ball-and-socket/fixed constraint. EV-0494 shows `FUN_140e95190` appends a candidate constraint to a TLS-marked selector-gated refcounted array, while separate target `FUN_140e860d0` remains unresolved. There are 26 direct edges and nine indirect sites in `FUN_140e8fc90`, with no mapped direct HitData or ActorValue target. This adds a cross-system event/object-tree/physics-constraint path without establishing combat or armor behavior. Trace `FUN_140e860d0`, then resume at exact caller `FUN_1406580f0`; 25/62 worker callers are reviewed, 37 remain. No Steam effective-protection/raw-AVSK or armor-XP result is established.

EV-0495 closes that static attachment-target question: tag 0x4D passes its constructed constraint pointer through `FUN_140e860d0`, whose immediate branch reaches `FUN_140b3a710` and whose alternate branch queues the object on its owner. The exact helper and immediate attachment route are already mapped from the separate ProcessTrapHit-created hkpConstraintInstance [EV-0360], [EV-0364]. This is a supported causal convergence on a native constraint primitive, not a claim that tag 0x4D is a combat hit or shares the same runtime types/owner. Two virtual sites in `FUN_140e860d0` and nine in `FUN_140e8fc90` remain. Resume the exact worker census at `FUN_1406580f0` (25/62 reviewed, 37 remaining), testing whether the next payload reaches mapped HitData/ActorValue handlers or another state/physics route.

EV-0496 advances the caller census to 26/62 and maps caller `FUN_1406580f0` as tag 0x4A. Its two producers use `FUN_1406d4110` to select a queued byte/object payload or a direct helper/value update; dispatcher case 0x4A repeats the same helper sequence [EV-0496], [EV-0455]. The direct branch conditionally raises an object float field and contains no mapped HitData or ActorValue/armor-skill edge, but the value's meaning and `FUN_140ea0760` descendants remain open. This is another static event-to-state path through a shared thread gate, not a hit or XP result. Trace `FUN_140ea0760` at RVA 0xea0760, then resume the exact caller inventory; 36 callers remain.

## Synthesis checkpoint — 2026-10-19 (Q-0079 Actor context selector)

EV-0511/EV-0512 resolve the tag-0x17 base Actor +0x378 route through slot +0x380 to the TLS/nested-field selector `FUN_1402e55a0`. EV-0295/EV-0296 show the same helper in the GOG HitData receiver `FUN_1406b9df0`, while EV-0510 shows the tag-0x17 caller passes the selected pointer to object/node helper `FUN_1406a19b0`. This is exact code reuse across the two routes; no shared returned object, HitData continuation, AV11/AV12 award, protection effect, armor-XP bypass, or OBJ-1 gate edge is established. Keep Q79-H46/H47 as competing same-context versus independent-context models. Continue the exact worker inventory at caller 30/62, `FUN_140658310` (RVA 0x658310), then compare its producer/dispatcher route to mapped HitData and skill sinks. Preserve the clean Steam matched-hit/raw-AVSK discriminator and separate level-one quest transition tests under EV-0260.

EV-0513 maps exact caller 29/62 to tag 0x19 from process/type-gated producer `FUN_140687370`; dispatcher case 0x19 calls `FUN_140687430(payload,0)`. Its virtual +0x2b8 call and handler remain unresolved. Keep dispatcher handler `FUN_140687430` unresolved until the remaining exact caller review selects it; caller 30/62 is `FUN_140658310`. Do not infer hit meaning from the event tag.


## Q-0079 update — tag-0x19 direct hierarchy route (EV-0514)

EV-0514 maps `FUN_140687430` to 49 direct-call sites over 38 unique targets and nine unresolved virtual calls. Its captured body and second caller `FUN_1406883b0` use process-associated object/child hierarchy state and body-part string references, including `DismemberedLimb1_Head1` and `Torso`; the complete direct target list contains no mapped HitData/ActorValue/armor-skill award target. This supports the bounded direct state-update model only; virtual calls and descendants leave Q79-H48 open, and producer virtual +0x2b8 remains unresolved. Exact next action: trace `FUN_140687370`, then resume worker caller 30/62. No protection/XP result or OBJ-1 edge is established [EV-0513], [EV-0514], [CL-L330], [M-0114].

## Q-0079 update — tag-0x19 indexed producer callback (EV-0515)

EV-0515 maps producer `FUN_140687370` to an indexed record-pointer argument passed through receiver vtable +0x2b8, followed by `FUN_1402e8f30` state writes and tag-0x19 submission. The caller's `FUN_1402e9000` AL branch conflicts with that helper's separate `void` decompilation; keep the mismatch unresolved. Next resolve primary Actor slot index 0x57, then return to worker caller 30/62. Q79-H51/H52 compare a part/hierarchy action with a generic Actor hook. No HitData/armor-skill/protection/XP result or OBJ-1 edge is added [EV-0515], [CL-L331], [M-0115].

## Q-0079 synthesis — Actor +0x2b8 item/equipment edge (EV-0516)

The tag-0x19 producer's indexed receiver call through Actor +0x2b8 maps in the GOG base Actor table to FUN_1406a2cd0. Its bounded other caller is an item-use/equipment method with equip/quest-item messages; target body includes BGSBipedObjectForm and item/list operations. This supports item/equipment reuse for the base method, while indexed payload identity, dynamic overrides, full descendants and protection/armor-skill effects remain open. Next complete FUN_1406a2cd0 direct/incoming coverage and compare to HitData/AV11/AV12 routes, then resume caller 30/62 [EV-0515], [EV-0516], [CL-L332], [M-0116].

## Q-0079 update — complete Actor +0x2b8 direct graph (EV-0517)

FUN_1406a2cd0 has 22 direct sites to 19 targets, four unresolved virtuals, and four incoming calls all from the item/equipment method FUN_1406a1bf0. Its complete direct route includes BGSBipedObjectForm/list work with no mapped direct HitData/ActorValue/armor-skill target. This narrows only the base direct method; the four virtuals and descendants remain open. Trace FUN_14022b7a0 next, then producer-backed virtuals; preserve caller 30/62 as the next exact inventory item [EV-0517], [CL-L333], [M-0117].

## Q-0079 synthesis — shared context and actor getter in item/list path (EV-0518)

FUN_14022b7a0 has 115 direct-call sites, three virtual sites and no mapped direct HitData/ActorValue award target. Its branches call `FUN_1406b98f0`, select context with `FUN_1402e55a0` before `FUN_140661f60`, and use the shared gate before `FUN_1406581b0` [EV-0518]. The same selector is used by the HitData receiver and tag-0x17 fallback, establishing code reuse but no returned-pointer identity [EV-0295], [EV-0296], [EV-0512]. Next trace FUN_1406b98f0, then continue the exact caller census; armor protection/XP stays unproven [CL-L334], [M-0118].

## Q-0079 update — nested-record getter and context consumer (EV-0519)

FUN_1406b98f0 resolves to a compact nested-record selector through FUN_14070fd50, with 51 callers and no direct HitData/ActorValue/armor-skill call. The item/list caller uses the output in a TESActionData-related branch. Its prototype omits a second selector value consumed by the callee; keep that register discrepancy open. Next trace FUN_140661f60, which consumes the common context selector in the same item route, then return to caller 30/62 [EV-0518], [EV-0519], [CL-L335], [M-0119].

## Cross-system synthesis — item/list and tag-0x55 hierarchy state (EV-0520)

FUN_140661f60 is called from item/list helper FUN_14022b7a0 and process-update target FUN_1406e5da0. It chooses a context hierarchy node and updates nested component +0x178 through reference-counted setter FUN_1407158f0; selector FUN_1414ae8a0 and two node virtuals remain unresolved. This supports a shared object-state primitive, not a shared hit/armor-XP effect. Next map FUN_1414ae8a0 and its DAT_14332c3a0 type identity, then resume caller 30/62 [EV-0520], [CL-L336], [M-0120].

## Q-0079 update — recursive hierarchy identity selector (EV-0521)

`FUN_1414ae8a0` searches hierarchy children and returns a candidate when its nested object's virtual +0x10 identity equals `DAT_14332c3a0`, with a recursive fallback; two callsites from `FUN_140661f60` feed the selected pointer to the existing +0x178 setter [EV-0521], [EV-0520]. The identity type, fallback descendants, and producer-backed +0x178 readers remain unresolved. Keep hierarchy-state and combat/protection models competing. Next query the exact GOG data address at RVA 0x332c3a0, then inspect +0x178 readers. No armor-XP bypass or Steam protection/raw-AVSK result is established.

## Q-0079 update — actor-update consumer of +0x178 (EV-0525)

FUN_140715940 has 13 direct targets, no indirect sites, and callers FUN_140773750/FUN_140734890. It reads nested +0x178 into a float calculation through FUN_1414fdb10 before calling FUN_1406eeb00/FUN_1406e68a0; another branch calls FUN_140661f60 through the shared selector [EV-0525]. This supports a bounded actor-update consumer, but not armor protection, HitData, ActorValue, or pointer identity with FUN_1407158f0. Next inspect FUN_1414fdb10 and keep H57/H58 competing [CL-L341], [M-0122].

## Cross-system synthesis — distance-weighted context update (EV-0526)

The tag-0x19/item/process hierarchy thread now reaches an actor-update consumer: FUN_140661f60 assigns a nested +0x178 pointer; FUN_140715940 later reads +0x178 and routes its +0x70 array into FUN_1414fdb10/FUN_14150aea0, which computes capped distance-attenuated floats [EV-0520], [EV-0521], [EV-0525], [EV-0526]. This links hierarchy selection, nested component storage, spatial data and actor update. It does not identify the array type or final state effect and adds no HitData, AV11/AV12, armor protection, armor XP, or OBJ-1 edge. Next inspect FUN_1406eeb00, which receives the aggregate result; keep the clean Steam matched-hit/AVSK check open under EV-0260.

## Cross-domain synthesis — paired context-state stores (EV-0528)

The hierarchy/item/process thread reaches `FUN_140715940`, which sums distance-weighted context entries and writes two adjacent fields through paired no-call setters: aggregate float at nested +0x3a8, followed by `DAT_14319c47c` at +0x3b0 [EV-0520], [EV-0525]–[EV-0528]. This tightens the bounded actor-update state model. No direct route to the mapped HitData/AV11/AV12 armor-skill branch or M-0096 resistance path appears, and no OBJ-1 quest/Story Manager dependency is supported. Cross-system relations remain analogies without a shared call or field reader. Next scan exact +0x3a8 operands for producer-backed readers; keep H57 downstream uncertainty and the clean Steam matched-hit/AVSK result open under EV-0260.

## Q-0079 +0x3a8 reader census — EV-0529

The complete GOG displacement scan found 54 +0x3a8 operands across 38 functions. `FUN_1406eeae0` reads a dword at +0x3a8 immediately adjacent to `FUN_1406eeb00`, the aggregate setter, but the scan does not establish a shared receiver; other same-offset accesses confirm collision risk [EV-0529]. Query the candidate reader's callers/callees, then continue with +0x3b0 readers if needed. No armor, HitData, AV11/AV12, OBJ-1, or M-0096 causal edge is added.

## Cross-domain synthesis — +0x3a8 context value and detection/light consumers (EV-0530)

The actor-update route writes nested +0x3a8 after aggregating distance-weighted context entries [EV-0525]–[EV-0528]. The getter for the same offset is called by four functions; one logs the returned value as “light” in a GetDetected message, and another uses it in a threshold branch [EV-0530]. The setter path also receives a caller +0xf8 slot expression, matching the outer slot used by getter callers [EV-0525], [EV-0530]. This supports a light/detection context-state interpretation, but runtime type and same-instance identity remain unproven. No causal edge to the mapped AV11/AV12 HitData route, armor protection, M-0096 resistance, or OBJ-1 quest gates is supported. Next inspect `FUN_140734890` and keep H59/H60 plus H57/H58 scoped.

## Cross-domain synthesis — shared actor +0xf8 update context (EV-0531)

`FUN_140734890` forwards the same +0xf8 pointer to `FUN_1406e5da0` and `FUN_140715940`; the latter calculates and stores the paired +0x3a8/+0x3b0 state [EV-0531], [EV-0525], [EV-0528]. Getter callers also pass +0xf8 to `FUN_1406eeae0`, whose value participates in detection/light logic [EV-0530]. This supports a structural bridge across actor/process update and perception state, but the function has no direct incoming callers and 33 unresolved virtual sites; primary Actor vtable registration is not established. No HitData, armor-protection, AV11/AV12, OBJ-1, or M-0096 causal edge is supported. Next query primary Actor slot +0x718.

## Q-0079 type discriminator — primary Actor slot mismatch (EV-0532)

Primary `VTABLE::Actor` slot +0x718 maps to `FUN_1406b9000`, not `FUN_140734890` [EV-0532]. This falsifies the base-slot prediction but does not resolve the update function owner; the +0xf8 dataflow remains structural. Next inspect code/data references to `FUN_140734890` for an alternate table, and keep no-hit/armor claims bounded.

## Q-0079 update — unresolved data references to FUN_140734890 (EV-0533)

The function has two source-less DATA references at RVAs 0x3660620 and 0x18ad2d8; neither identifies a vtable or registration owner [EV-0533]. Primary Actor slot +0x718 maps elsewhere [EV-0532]. Inspect the nearer data location before assigning a type, and preserve the +0xf8 relationship as structural only.

## Q-0079 update — source address remains untyped (EV-0534)

RVA 0x18ad2d8 is mapped but has no function, no references pointing to the address, and no instruction at the exact location [EV-0534]. The query did not read the qword previously referenced to FUN_140734890 [EV-0533]. Next inspect one pointer-sized entry only; keep owner/type, registration, HitData, armor and Steam-runtime relations unresolved.

## Q-0079 update — one data slot points to FUN_140734890 (EV-0535)

The qword at RVA 0x18ad2d8 is VA 0x140734890 and resolves to FUN_140734890; no references point to the entry [EV-0535]. Record the static pointer only. Isolated field versus table/registration-entry ownership remains unresolved. Next inspect the second source at RVA 0x3660620; preserve the primary Actor slot mismatch and no HitData/armor edge.

## Q-0079 update — second data source has a split-value ambiguity (EV-0536)

RVA 0x3660620 contains qword 0x735D6800734890. Its low 32 bits match FUN_140734890’s RVA; high 32 bits are 0x735D68 and remain unresolved [EV-0536]. Packed 32-bit RVAs versus an unrelated/encoded qword remain competing models. Query the high-half candidate under the exact GOG target before assigning meaning.

## Q-0079 update — high-word candidate follows a RET (EV-0537)

RVA 0x735D68 has no function/instruction identity, and the preceding decoded instruction at VA 0x140735D67 is RET [EV-0537]. A function-end interpretation is plausible but not connected to FUN_140734890; next identify which function owns the RET.

## Q-0079 update — second source matches FUN_140734890 code bounds (EV-0538)

RVA 0x3660620’s low32 equals FUN_140734890 entry RVA 0x734890; high32 0x735D68 follows a RET at 0x735D67 inside that function [EV-0538], [EV-0536]. A start/exclusive-end pair is plausible, while the record format/owner remains unknown. Test one adjacent qword at RVA 0x3660628, then return to the unfinished worker-caller census unless it repeats.

## Q-0079 update — adjacent qword suggests a 12-byte code-range row (EV-0539)

RVA 0x3660628 reads 0x735D7001D74768; high32 0x735D70 matches a decoded PUSH address after FUN_140734890’s RET [EV-0539], [EV-0538]. A 12-byte code-range/unwind row is plausible but unverified. Query the exact high-half address to see whether it begins another function; then close this no-combat-edge subline and return to the remaining worker-caller census.

## Q-0079 update — next candidate begin is a function at +12 bytes (EV-0540)

RVA 0x735D70 maps to FUN_140735d70 and has a source-less DATA ref from RVA 0x366062c, +12 from candidate row 0x3660620 [EV-0540]. This supports a possible 12-byte record pattern. Read the next candidate row’s begin/end pair before classifying the region; two other source-less refs remain unknown.

## Q-0079 update — second candidate begin/end qword (EV-0541)

RVA 0x366062c contains 0x735DA200735D70; low32 matches FUN_140735d70 entry and high32 0x735DA2 is a possible end [EV-0541]. Check the instruction at 0x735DA1 before identifying a repeated function-range pattern; keep section type and runtime registration unresolved.

## Q-0079 update — second candidate end-minus-one is not RET (EV-0542)

RVA 0x735DA1 still maps to FUN_140735d70 but is not an instruction boundary; preceding instruction is MOV at 0x735D9F [EV-0542]. The predicted terminal RET is absent. Query exact candidate end RVA 0x735DA2 once, then return to worker-caller research unless a clear boundary emerges.

## Q-0079 side-line closure — no repeated range record or combat edge (EV-0543)

RVA 0x735DA2 is an instruction inside FUN_140735d70, so the second qword is not an exclusive function end [EV-0543]. The first qword’s start/end-like values remain unexplained; no source owner, registration, or HitData/armor edge is established. Resume the unfinished worker-caller census at caller 30/62, FUN_140658310.

## Cross-domain synthesis — actor update, data references, and HitData worker census (EV-0530–EV-0543)

The +0xf8 relation between `FUN_140734890`, paired +0x3a8/+0x3b0 updates, and detection/light getter callers remains structural only [EV-0530], [EV-0531]. Primary Actor slot +0x718 maps to a different function [EV-0532]. The source at RVA 0x18ad2d8 contains a direct pointer to `FUN_140734890`, but no enclosing table or RTTI owner has been identified [EV-0533]–[EV-0535]. The second source’s split qword produced a tempting code-boundary coincidence, but its adjacent candidate end lies inside another function, so no simple range table is supported [EV-0536]–[EV-0543]. This side path adds no hit dispatch, effective armor protection, AV11/AV12, armor XP, or OBJ-1 gate edge. Keep the exact Steam matched-hit test separate; resume the primary worker-caller census at caller 30/62, `FUN_140658310`.

## Q-0079 update — caller 30 tag-0x1A dispatcher target (EV-0545)

Dispatcher case 0x1A calls FUN_1404c2480(global,payload); adjacent case 0x1B calls FUN_1404c2650 [EV-0545]. Query the exact tag-0x1A target for a direct HitData/ActorValue route, then resume caller 31/62 FUN_140658350. Do not infer event semantics from tags.

## Q-0079 update — tag-0x1A target is guarded registry/list work (EV-0546)

FUN_1404c2480 hashes/searches payload ID +0x14 and removes/appends stored entries under a TLS marker and lock; 8 direct calls, no indirect sites, 4 callers. No direct HitData/AV/armor-skill path appears; deeper FUN_1404ca0f0 remains open. Continue caller 31/62 FUN_140658350.

## Cross-domain synthesis — thread-gated registry pair, no combat edge (EV-0544–EV-0548)

Caller 30/31 share one producer and thread-state gate: tags 0x1A/0x1B queue paired handlers or call them immediately. The handlers conditionally move payload pointers and IDs among hash/list arrays; tag 0x1B also follows reference-counted child entries [EV-0544]–[EV-0548]. The manager/type and event semantics remain unknown, with one nested virtual release open. This is a registry-state mechanism, not a mapped HitData, effective protection, AV11/AV12, armor-XP, or OBJ-1 route. Resume worker caller 32/62 FUN_140658390.

## Cross-domain synthesis — collection cleanup and defensive clothing comparator (EV-0581, EV-0398–EV-0402, EV-0222, EV-0604/0605)

Actor.RemoveSpell tag 0x5d and tag 0x44 each manipulate refcounted pointer collections, but their helpers and observed call paths differ; CL-L418 records only an analogy. No ActiveEffect identity or combat/armor effect follows. Separately, the official Clothing ARMO 000FC061 carries AV44 Resist Magic while having zero physical DNAM, and the GOG CheckResistance body reads AV44/AV40 plus the incoming effect ResistValue. This is a potentially measurable magic-defense comparator outside the mapped positive-DNAM Heavy/Light AV11/AV12 selector, but level-one acquisition, the ordinary magic-hit caller, Steam damage reduction and numeric AVSK are unverified. Q-0080 tests that narrow candidate and separates magic from physical hits. No shared causal edge to the MS06 level-10 Story Manager path (Q-0078) is supported.

Next: resume the running caller-47 investigation at object factories `FUN_1404a27f0`/`FUN_1404a28a0`, then caller 48/62. After that checkpoint, reselect between the remaining OBJ-2 callers, Q-0080 and an independent OBJ-1 gate candidate; retain the exact unforced Steam transition and numeric protection/AVSK tests.

## Cross-domain synthesis — 2026-10-20 — pending level state and armor XP

Q83/Q85 kept the Dragonborn CLOC initiation chain separate from the world-cultist QUST: the Solstheim location row is a conditional alternative to the level-25 predicate only after earlier chance/stage predicates, and neither natural level-one startup nor Steam evaluation timing is observed [EV-0654]–[EV-0687]. Q82/Q84 bounded the GOG HitData phase order and entrypoint-handler effects: mitigation precedes the worn-armor scan, while selector handlers update numeric results or derived-value caches without a captured direct equipment, source-ActorValue, HitData, or skill-progress write [EV-0670]–[EV-0685].

Q86 adds a direct cross-domain path: the unblocked player-receiver worn-armor route sends skill 11/12 points through UseSkill slot 0xF7 to the skill-progress routine, which also adds cumulative character-level XP [EV-0221], [EV-0670], [EV-0674], [EV-0689], [EV-0690]. Separately, the captured GetLevel getter reads ActorBaseData.level [EV-0689]. The native writer and pending-versus-accepted timing remain unresolved, so do not infer that XP changes the gate-visible field before acceptance. This is a causal XP-routing edge, not evidence of a level-one exploit, armor protection, or zero-armor-XP behavior.

Next static discriminator: map the exact GOG ActorBaseData.level read offset and trace only producer-backed writes with Player/base-form provenance; compare candidate callers to the skill-threshold/event and LevelUpMenu paths. Keep Steam live observations under EV-0260 and continue P0 selection.

## Cross-domain synthesis — Q-0087 level writer and armor XP bridge (EV-0691–EV-0694)

The stored Player level field is now mapped to a threshold-gated StatsMenu update writer in GOG 1.6.1179.0. `FUN_1409611e0` handles `StatsMenu::ProcessMessage(kUpdate)`; when the Player progress pair is due, it calls the writer that stores GetLevel+1. The StatsMenu factory is registered by name; the earlier constructor attribution for `FUN_140960d40` is corrected by EV-0693, without changing the RTTI/slot mapping.

Cross-domain synthesis adds the important link: positive HitData-derived worn-armor skill points pass through UseSkill to PlayerCharacter+0x9b8, where the skill-progress helper increments the progress float. The StatsMenu threshold handler loads the same pointer and compares the same progress pair before writing the field [EV-0689]–[EV-0694]. Thus armor XP can feed the level gate through a delayed menu-update stage in this bounded GOG source path. Steam timing, user-action ordering, effective protection, zero armor XP, and a natural level-one quest start remain unobserved; keep those under EV-0260.

Next: resolve registrations for FUN_140356a10/FUN_140355210 and the StatsMenu message/input boundary, then reselect toward the remaining OBJ-2 functional-armor/zero-XP mechanisms. Do not treat GOG behavior as Steam validation.
