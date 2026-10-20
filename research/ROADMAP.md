
EV-0341 maps the remaining helper-created PlayerCamera states. EV-0342 identifies ThirdPersonState+0xA0 as a refcounted return from a type-erased slot+0x150 call on the PlayerCharacter slot+0x378 result, with virtual slot+0x8 release paths. This refines the +0xA0 producer but does not identify its concrete class or connect it to a ProcessTrapHit teardown site. The NiNode/NiAVObject family remains an analogy; differing concrete vtables or finalizers would falsify the shared-family model. No Actor::UseSkill AV11/AV12 edge or cross-objective link to the VQ00/VQ01 route is established. Keep Q-0064 active, then reselect the P0 quest-runtime discriminator. Claims CL-L176–CL-L179 -> M-0064 [EV-0341], [EV-0342].
EV-0344 resolves the lookup receiver to the constructed PlayerCharacter global and the wrapper to AnimatedCameraStartHandler entry 1. Its flag-zero result still selects a TLS or nested field; the selected object's vtable and returned finalizer are open. Q-0064 remains active; follow both context producers to their concrete slot+0x150 target, then reselect the P0 armor and quest-runtime lanes. Claims CL-L181/182 -> M-0065.EV-0345 bounds the AnimatedCameraStart/DeltaStart callback branch: the wrappers share FUN_1408e6500 and an IHandlerFunctor<Actor,BSFixedStringCI>-named base, but the lookup receiver and returned member remain untyped. Continue with the five missing ProcessTrapHit cleanup-site contexts; do not convert this camera branch's unresolved relation into a negative armor-XP claim. Claim CL-L183 -> M-0065.EV-0346 completes the local contexts for all eight FUN_14072fd60 indirect sites. Five are refcount-final releases of +0x9D0/+0x9A8/+0x9A0/+0x8F8/+0x730; concrete tables and descendants remain open. The global DAT_143188918 class is resolved by EV-0344, while the resource values are not. Next, identify exact source-backed vtables/finalizers, starting with the +0x8F8 skeleton and +0x730 scene-object paths. Claim CL-L184 -> M-0066.EV-0347 ties PlayerCharacter+0x8F8 to `Actors\\Character\\1stPerson\\Skel` and the generic mesh-resource path, but does not resolve the NIF root class or slot +0x8 descendants. The +0x730 displacement scan reconfirms the cell-transition writer without adding a concrete type. Next, inspect the +0x9D0 type-selected metadata/resource producer and compare its exact return/finalizer path; then continue the independent +0x9A0/+0x9A8 model path. Claim CL-L185 -> M-0067.EV-0348 maps the +0x9D0 fallback to descriptor key-2/key-1 lookup values but does not resolve their concrete classes or finalizers. Continue through the independent +0x9A0/+0x9A8 model-resource producer and compare exact vtables; preserve unresolved data branches. Claim CL-L186 -> M-0068.EV-0349 maps the +0x9A0/+0x9A8 model path through a two-slot adapter and sorted-name array lookup. Its lookup contract differs from +0x8F8 slot +0x150 use but does not resolve class identity. Next, inspect candidate setter FUN_1407445d0 and its exact callers for a concrete producer-backed vtable; otherwise continue with the +0x730 source. Claim CL-L187 -> M-0069.EV-0350 maps the +0x9A0/+0x9A8 setter and its model-resource caller, but leaves the incoming object's vtable and finalizer unknown. Continue on the independent +0x730 cell-scene child producer, then screen exact finalizer descendants for AV11/AV12. Claim CL-L188 -> M-0070.EV-0351 maps the +0x730 cell helper to an opaque cell+0x130+8 pointer; no class or non-null writer is recovered. Next resolve the PlayerCamera global slot-0 cleanup path, then return to the unresolved scene child. Claim CL-L189 -> M-0071.

EV-0352 identifies the PlayerCamera slot-0 deleting destructor and five unresolved child dispatches. Next screen the +0x128 producer path; the broad +0x28 scan does not identify a concrete object writer. Claim CL-L190 -> M-0072.

EV-0353 resolves the PlayerCamera+0x128 bhkRigidBody destructor path to FUN_140e92c60; its body+0x28 child array still dispatches unknown slot+8 targets. Next recover the child-array producers and tables. Claim CL-L191 -> M-0073.

EV-0354 bounds the first PlayerCamera rigid-body cleanup pass to an empty body+0x28/+0x38 child vector. Next resolve FUN_140ebf0b0 and any post-constructor vector writers. Claim CL-L192 -> M-0074.

EV-0355 resolves the later body child writer as physics constraint setup on a flagged ProcessTrapHit scene traversal. Next trace FUN_140b3a830 descendants and the remaining indirect sites against the AV11/AV12 skill sink; keep Steam runtime tests separate. Claim CL-L193 -> M-0075.

EV-0356 excludes FUN_140b3ac30 for the factory-created hkpConstraintInstance because its exact slot+0x30 returns zero. Continue with remaining ProcessTrapHit indirect sites against Actor::UseSkill slot +0xF7. Cross-domain review of EV-0326 and EV-0356 adds no quest-to-armor causal edge; a direct shared call/state dependency or same-build trace would falsify this [CL-L194].

EV-0357 resolves the factory-created hkpConstraintInstance slot-0 cleanup body, but its callback array and member finalizers remain open. Next identify writers to +0x40/+0x48 and producer classes at +0x18/+0x28/+0x30, then screen their targets against AV11/AV12. Keep Steam hit/protection/raw-AVSK measurements separate.

EV-0358 maps the hkpConstraintInstance callback-array consumer and its direct callers, but identifies no exact producer. Next trace FUN_140b439e0's incoming callers/receiver lineage, then resolve producer-backed writes to +0x18/+0x28/+0x30 or callback registration. Broad offset scans remain candidate-only.

EV-0359 splits FUN_140b439e0 callers by class/record route. Next trace whether the ProcessTrapHit-created hkpConstraintInstance enters the hkpSimulationIslandAndEntity ConMstPtr collection or a post-collision type-1 command record; then follow producer-backed callback/member descendants against AV11/AV12.

EV-0360 ties the exact ProcessTrapHit hkpConstraintInstance to its entity constraint record and add-callback notification. Next resolve exact +0x40/+0x48 callback writers and callback entry classes; follow attach slot +0x8 and detach slot +0x10 targets plus member finalizers to AV11/AV12. Preserve the open Steam effective-protection/raw-AVSK experiment.

EV-0361 narrows the exact hkp add-callback dispatch callers to island/entity and post-collision routes; the retained listener-name string has no analyzed references. Continue with exact-instance member/callback producer lineage and preserve the Steam positive-damage, effective-protection, raw-AVSK discriminator.

EV-0362 corrects the island type label and maps EntityPtrs (+0x60/+0x68) to per-entity constraint records (+0x100/+0x108). EV-0363 shows the broad displacement scan output stopped before 0x140b, so writer status remains unresolved. Next trace the exact selected owner from FUN_140b678a0/FUN_140b43a20 into that list.

EV-0497 resolves the bounded tag-0x4A helper body as a byte-gated selector-list transition: it toggles matching per-index bits and routes through one of two manager update functions. H40 is supported for this static structure; H39 remains open across five virtual sites and deeper descendants. This adds no edge to the quest-gate mechanism, mapped HitData/ActorValue routes, effective protection, or armor-skill awards. Resume Q-0079 at exact worker caller 27/62 (`FUN_140658130`, GOG RVA 0x658130); keep the GOG static result separate from the outstanding clean Steam protection/raw-AVSK test.

EV-0498 resolves exact caller 27/62 as a tag-0x60 worker builder; the build-matched dispatcher calls `FUN_140e88fd0(payload,1)` for a nonnull payload. The source-less DATA xref does not identify the producer, and the target is uninspected. H41 is supported for the bounded builder/dispatcher mapping; H42 remains open for combat/skill descendants. Trace `FUN_140e88fd0` (GOG RVA 0xe88fd0), then resume caller 28/62. No causal edge to OBJ-1, effective protection, or armor XP is added.

EV-0499 narrows `FUN_140e88fd0` to an optional selector/type/flag check and a recursive child-hierarchy callback through `FUN_140e898f0`. The callback target, node types, and third-register value at the worker-dispatch call are unresolved; H43 is supported for the bounded traversal, while H42 remains open. Inspect the callsite at RVA 0x65b582 and references/writers to `PTR_FUN_14202d630`, then resume caller 28/62. No HitData, ActorValue, effective-protection, armor-skill, or OBJ-1 edge is established.

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

## Q-0079 update — caller 32 is a tag-0x1c Actor/process continuation (EV-0549–EV-0550)

Caller 32/62 FUN_140658390 retains an object pointer and writes tag 0x1c. Dispatcher case 0x1c returns the object to FUN_140729140 with argument zero. That branch skips the helper's three indirect virtual sites, checks the shared thread-state gate, and reaches direct Actor/process update calls when clear. This helper has eight additional direct callers; event/runtime semantics remain unknown. The recurring gate across hit, actor-update, registry, and physics families is stronger evidence for shared scheduling than for combat semantics [EV-0432], [EV-0464]–[EV-0470], [EV-0544]–[EV-0550]. No armor-XP, effective-protection, or OBJ-1 edge is added. Continue caller 33/62 FUN_1406583d0.

## Q-0079 update — caller 33 is a gated tag-0x1d object-state route (EV-0551–EV-0552)

Caller 33/62 writes tag 0x1d from FUN_1401d4620; dispatcher case 0x1d returns the object and two byte arguments to that helper. Its direct path includes Open/Close property operations and, under separate flag/type/helper gates, calls the previously mapped tag-0x1a/0x1b registry handlers [EV-0545], [EV-0546], [EV-0548], [EV-0551], [EV-0552]. Three virtual targets and runtime object identity remain unresolved. The shared worker gate spans distinct hit, actor-update, registry and object-state paths without a demonstrated armor/quest causal edge. Continue caller 34/62 FUN_140658480.

## Q-0079 update — caller 34 is a generation-handle Actor continuation (EV-0553–EV-0558)

Caller 34/62 is tag 0x21. Its key is allocated/reused in a generation-checked global table, resolved back to the source Actor, and dispatched through primary Actor slot +0x6c8 to the same base function that queued it [EV-0545], [EV-0553]–[EV-0557]. The clear-gate branch and a separate Actor caller reach the same nested Actor/process object and scalar wrapper, but the dynamic +0x190/slot+0x8 target and scalar meaning remain unknown [EV-0556], [EV-0558]. This is a concrete cross-system deferred Actor continuation; it adds no armor-XP or level-gate edge. Continue caller 35/62 FUN_140658500.

## Q-0079 update — caller 35 is a gated water-effect pair (EV-0559–EV-0561)

Caller 35/62 builds tag 0x2c from a scalar and three coordinates after spatial thresholds. Its producer queues tags 0x2c/0x2d under the shared gate or calls their handlers directly. Case 0x2c selects CWaterSmall/Medium/Large and a waterSplash NIF effect; case 0x2d updates distance-gated coordinate buffers [EV-0545], [EV-0559]–[EV-0561]. This distinguishes the worker gate from combat semantics once again. A virtual effect target and buffer consumers remain open; no armor or quest edge is added. Continue caller 36/62 FUN_140658550.

## Q-0079 update — caller 43 tag-0x3d indexed state route (EV-0586)

Caller 43 builds tag `0x3d`; four producer functions provide different indices/flags and the fallback case calls `FUN_1406c6ee0` [EV-0574], [EV-0586]. The helper uses two unresolved virtual slots to select indexed state and calls update/cleanup helpers. One producer references `iMagicEquipped`, but no direct mapped HitData/protection/AV/UseSkill path is established. Nineteen of the original 62 callers remain; resume at `FUN_1406588e0` [CL-L398], [M-0141].

## Q-0079 update — caller 44 tag-0x3f immediate/deferred convergence (EV-0587)

Caller 44's producer chooses an immediate `FUN_1405d4bf0` call or submits the same four values through tag `0x3f`; the worker wrapper reaches the same helper in the same argument order [EV-0574], [EV-0587]. The helper's object virtuals remain unresolved and it has no direct mapped HitData/protection/AV11/AV12/UseSkill sink. Eighteen original callers remain; resume at `FUN_140658950` [CL-L399], [M-0142].

## Q-0079 update — caller 45 tag-0x40 handler bounded (EV-0588)

The tag-0x40 worker target `FUN_14040e300` has three direct callees and no indirect sites. It updates object/scalar state and invokes a helper with a `TESImageSpace` form-cast branch; no direct mapped HitData/effective-protection/AV11/AV12/UseSkill target appears [EV-0588]. Payload identity, form provenance and transitive behavior remain unknown; inspect producer `FUN_140357c70` through `FUN_14033e470` next [CL-L400], [M-0143].

## Q-0079 update — caller 45 typed-value producer path (EV-0589)

Caller 45's sole producer decodes descriptor-selected values through shared `FUN_14033e470` and forwards an object/boolean to the tag-0x40 worker only on success [EV-0589]. The wrapper body does not directly read Actor/HitData fields; input provenance and decoded type remain unresolved. Continue to caller 46/62 without treating the generic decoder as evidence of a hit or armor route [CL-L401], [M-0144].

## Q-0079 update — caller 45 registration reference (EV-0590)

The tag-0x40 producer has no analyzed direct callers and one unresolved data reference at RVA `0x362ffb4`; the containing table does not yet identify the decoder descriptor or payload type [EV-0590]. Inspect that data address once, then continue caller 46/62 if it remains opaque [CL-L402], [M-0145].

## Q-0079 update — caller 45 xref is likely unwind metadata (EV-0591)

The only data reference to caller 45's producer matches the documented x64 `RUNTIME_FUNCTION` start/end/unwind-info triplet in two GOG examples, so it is likely `.pdata` exception metadata rather than an application descriptor [EV-0591]. The decoder's selected type and input remain unresolved. Resume the original caller inventory at `FUN_1406589f0` (caller 46/62); do not treat the xref as a gameplay-registration lead [CL-L403], [M-0145].

## Cross-domain synthesis — Q-0079 caller 54 (EV-0636)

The tag-0x54 Actor update uses primary Actor slot +0x380/FUN_1402e55a0, the exact selector also present in the HitData receiver and tag-0x17 route [EV-0295], [EV-0296], [EV-0512], [EV-0636]. The tag-0x32 immediate/deferred state callback also reaches the recursive object-tree helper already mapped for tag 0x3C [EV-0483]–[EV-0486]. These are verified shared-code edges; the selected runtime pointer and downstream HitData/armor effect remain unknown. Q79-H47 is supported as the conservative code-reuse model, while H46's shared-object claim remains proposed. Caller 54 has no mapped direct HitData/protection/AV11/AV12/UseSkill sink, but 21 virtual sites and recursive descendants remain open [EV-0636]. No causal edge is added. OBJ-2 still requires the clean Steam matched-hit/protection/raw-AVSK test [EV-0260]; OBJ-1 remains separate. Continue caller 55/62 FUN_140658c90.

## Cross-domain synthesis — Q-0079 caller 55 (EV-0637)

Caller 54's tag-0x54 branch is spatial/context Actor state work with nested-state and object-tree helper reuse [EV-0636]; caller 55 is a distinct numeric value/limit notification into tag-0x57 registry lookup [EV-0637]. These worker routes share dispatcher infrastructure but have different producer payloads and consumers. Caller-55 literals 0x18–0x1A and 0xFC–0xFE do not establish named ActorValues, quest conditions, or resource events. No causal edge to HitData/protection/AV11/AV12/UseSkill or the level-one quest objective is added. The clean Steam matched-hit/protection/raw-AVSK test remains outstanding [EV-0260]. Continue caller 56/62 FUN_140658cc0.

## Cross-domain synthesis — Q-0079 caller 56 (EV-0638)

Caller 54 maps spatial/context Actor updates and shared nested-object helpers; caller 55 maps a numeric value/limit registry notification; caller 56 maps PlayerCharacter collection cleanup with an RTTI-verified perk-rank visitor [EV-0636]–[EV-0638]. Their common worker dispatcher does not establish a shared causal mechanic. The caller-56 route removes a rank-list entry under captured conditions; it does not demonstrate a perk grant, level eligibility check, HitData event, effective protection change, AV11/AV12 award, or armor XP effect. One runtime PlayerCharacter virtual override remains unresolved. Keep this as a separate state-cleanup mechanism with no OBJ-1/OBJ-2 edge. The clean Steam protection/raw-AVSK test remains outstanding [EV-0260]. Continue caller 57/62 FUN_140658d00.

## Cross-domain synthesis — Q-0079 callers 56–57 (EV-0639)

Callers 56 and 57 expose opposite operations over the same PlayerCharacter rank-list field +0x4b8: caller 56's RTTI-verified FindPerkInRanksVisitor locates/removes a matching entry, while caller 57's AddPerkVisitor path inserts or updates a perk-rank pair [EV-0638], [EV-0639]. Caller 57 defaults rank zero to current rank+1 and enforces only the captured perk rank-count byte +0x52. The two callers support a shared list-lifecycle model; they do not identify a level-one caller or prove perk level requirements are bypassed. Old/new rank callbacks remain unresolved. No edge is added to OBJ-1 quest gates or OBJ-2 HitData/protection/armor XP. Continue caller 58/62 FUN_140658dd0 and preserve wrapper-table ownership for a later level-one discriminator.

## Cross-domain synthesis — Q-0079 caller 58 (EV-0640)

Caller 58's tag 0x5A updates a handle-keyed coordinate record from Player/object positions; one producer is an Actor slot-0x9C threshold method and another comes from a Havok contact-pair collection [EV-0640]. Caller 54 also uses spatial predicates but reaches a different Actor/context state route; no shared receiver, manager, quest gate, HitData field, or armor-skill writer has been identified [EV-0636], [EV-0640]. The worker queue is shared infrastructure, not a common gameplay cause. The 13 manager virtual callbacks remain unresolved. No OBJ-1/OBJ-2 edge is added. Continue caller 59/62 FUN_140658e10, preferring explicit level or combat discriminants.

## Cross-domain synthesis — Q-0079 caller 59 (EV-0641)

The latest callers occupy distinct systems: caller 56 removes matching perk-rank entries, caller 57 adds/updates rank pairs under a perk rank-count bound, caller 58 maintains handle-keyed coordinates with Actor/physics producers, and caller 59 dispatches a disarm-related Actor action [EV-0638]–[EV-0641]. The shared worker is transport infrastructure; no common receiver, progression gate, HitData field, protection calculation, or armor-skill writer links these routes. Caller 59's explicit PlayerCharacter message makes the disarm outcome the supported model, while 16 Actor virtual sites and runtime descendants remain open. No OBJ-1/OBJ-2 causal edge is added. Continue caller 60/62 FUN_140658e50; retain the clean Steam protection/raw-AVSK discriminator [EV-0260].

## Cross-domain synthesis — Q-0079 caller 60 (EV-0642)

Caller 59 is a deferred disarm-related Actor action; caller 60 is a distinct tag-0x5C event produced inside mapped HitData handler `FUN_1406b9df0` and serialized through `FUN_1407dce10` [EV-0641], [EV-0642]. The tag-0x5C dispatcher returns to `FUN_1406be430`, which is also called on the producer's alternate branch and is shared with an Actor/process callback [EV-0599], [EV-0600]. This is verified cross-system helper reuse with distinct runtime arguments. Its bounded effect is vector/physics-like plus an unnamed numeric ActorValue-0x24 query; no direct effective-protection/AV11/AV12/UseSkill edge is established. The two worker events are not one mechanism. Continue caller 61/62 FUN_140658f70 and retain clean Steam evidence requirements [EV-0260].

## Cross-domain synthesis — Q-0079 caller 61 (EV-0643)

Caller 60 is a HitData-derived event that rejoins a vector/physics-like helper; caller 61 is an independent eye-headpart texture replacement after geometry validation [EV-0642], [EV-0643]. Both use the worker queue, but no shared receiver, progression state, damage record, armor protection, or skill writer links them. This separates transport reuse from a causal gameplay relation. No OBJ-1/OBJ-2 edge is added. Inspect final caller 62/62 FUN_140658fb0 and reconcile the exact inventory.

## Cross-domain synthesis — Q-0079 caller 62 (EV-0644)

The last worker caller adds a second HitData-adjacent code reuse observation: caller 60/tag 0x5C was directly produced inside the mapped HitData handler and rejoined a vector/physics helper [EV-0642], while caller 62/tag 0x62 comes from `FUN_1406c72d0` and reaches `FUN_1406bc400`, another helper called by mapped HitData code [EV-0644]. The payloads and target helpers differ, so the worker's shared transport and reused Actor helpers do not establish one causal event or an armor XP/protection mechanism. Caller 61 remains a separate eye-texture update [EV-0643]. No OBJ-1/OBJ-2 causal edge is added. Reconcile the 95-caller exact partition, then select Q-0080; preserve the live Steam matched-hit test as open [EV-0260].

## Cross-domain synthesis — Q-0081 separate cultist branches and location alternative (EV-0654–EV-0669)

Official five-master records separate CLOC `DLC2CultistAmbush` from SCPT `DLC2WE09`, though their loose PSC stage-10 fragments share a `DLC2MQ01` handoff [EV-0654]–[EV-0664]. The world QUST's raw `GetLevel >=25` and Solstheim rows both set the OR bit; pinned TES5Edit source decodes those operators, and the GOG 1.6.1179 evaluator groups consecutive OR-flagged rows [EV-0665]–[EV-0668]. This supports a GOG static inference of `earlier chance/stage conditions AND (level >=25 OR Solstheim location)`, while the caller census does not locate the condition-list evaluation point [EV-0669]. The precise EV-0260 natural Steam start test remains outstanding: exact profile/full order, disposable level-one save, read-only quest transition observation, ordinary triggers, controls and repetition. No vanilla level-one exploit is claimed.

Cross-domain review found no shared record, ActorValue, ActiveEffect, serialization field, or native call edge linking Q81's quest conditions to OBJ-2's HitData protection and AV11/AV12 award sequence. Generic condition-list infrastructure is not a causal bridge. Keep the Q81 static source inference and the OBJ-2 armor mechanism as distinct frontier items; continue with Q-0082's mitigation-to-skill phase-order trace while the Steam runtime dependency remains blocked.

## Synthesis checkpoint — Q-0082 mitigation and award order (EV-0670–EV-0676)

The GOG 1.6.1179.0 source trace places AV39/armor-factor mitigation before the unblocked player-receiver worn-ARMO AV11/AV12 selector in `FUN_1406bcaa0`; `FUN_1406b9df0` is a later, distinct health/trap path [EV-0670], [EV-0673]. Matching selector rows across the five official masters use EPFT IDs 1/2, whose captured GOG handlers write/add numeric results [EV-0672], [EV-0675]. This narrows a synchronous equipment-interposition hypothesis, but one typed function-data virtual predicate remains unresolved and the Steam matched-hit/protection/raw-AVSK experiment is still required [EV-0260].

Cross-domain review adds no link between this HitData route and the Q81 quest-condition/Story Manager chain. Selector visitor reuse is generic engine infrastructure, not a shared progression cause. Keep Q-0082's bounded result at M-0200, retain the exact EV-0260 runtime discriminator, and continue with the next ready P0 frontier question.

## Q-0085 — location alternative and ferry-source screen (EV-0686–EV-0687)

The SCPT world-event selectors and Solstheim trigger chain contain no separate explicit player-level predicate in the bounded official source screen. QUST DLC2WE09 remains chance AND MQ105 >= 160 AND DLC2MQ06 < 550 AND (level >= 25 OR current location is Solstheim), with the operator grouping supported by the exact GOG evaluator evidence [EV-0657], [EV-0665]–[EV-0669]. The six source-ordered INFO rows below Gjalund's initial Windhelm passage topic have no GetLevel function index, and revision-cited UESP describes a before-cultist 250-gold ferry route [EV-0686], [EV-0687]. This is a conditional static route, not a natural level-one result; stage reachability, chance value, Steam timing, profile order and aliases remain under EV-0260. No OBJ-2 edge is added. Next investigate whether GetLevel remains unchanged while skill experience is waiting for the player to accept a level-up.

## Q-0087 — threshold writer, StatsMenu update, and armor XP bridge (EV-0691–EV-0694)

The exact GOG level-field writer is `FUN_1401d7ba0`. A threshold-gated caller reads Player GetLevel+1 and stores it through this helper; RTTI, vtable slot 4, and CommonLib map the UI caller to StatsMenu `ProcessMessage(kUpdate)` [EV-0691], [EV-0692]. EV-0693 corrects the constructor/destructor role assignment and identifies the registered `StatsMenu` factory; it does not resolve which player action opens or accepts the interface.

The cross-domain trace ties hit-earned armor skill progress to the same Player progress object checked by that update handler. Positive AV11/AV12 points pass PlayerCharacter+0x9b8 into the skill helper; the StatsMenu handler loads the same pointer, tests the threshold pair, and can write the stored level [EV-0689]–[EV-0694]. This is a static GOG causal bridge from OBJ-2 XP into OBJ-1 gate-visible level progression. It is not a Steam result, a natural level-one quest start, a protection result, or a zero-XP armor exploit. Continue with Q-0088's writer-registration/UI-input discriminator and retain all live checks in EV-0260.

## Q-0088 — state-byte displacement and StatsMenu update timing (EV-0695)

The complete GOG `+0x325` operand scan found five accesses, but the set-true wrapper's sole analyzed caller is an inventory/soul-capture path. The separate unbounded byte-one store at RVA `0x9628B9` has no analyzed function owner/xrefs and does not appear in the first 64 entries read from the RTTI-identified StatsMenu vtable [EV-0695]. These are bounded observations; object type, full vtable extent, and indirect dispatch remain open. Equal offsets are not one cross-object field, and no producer for StatsMenu's exact `+0x325` byte was resolved.

The prior Q87 GOG causal bridge is unchanged: positive HitData-derived armor skill points update the same progress object tested by the due-threshold StatsMenu writer [EV-0694]. No link connects the soul-capture path to that armor/level edge. Q88 closes only its static candidate discrimination; periodic-versus-input timing and extra writer-table consumers remain unresolved. Keep the clean Steam pending/open-without-attribute/accepted sequence under EV-0260, then follow the frontier selector to the next independent P0 question.


## OBJ-2 frontier synthesis — 2026-10-20

Q-0052/EXP-0053 and EV-0311/EV-0312 establish a GOG static path from positive type-0/1 DNAM through the PlayerCharacter +0x274 cache into the shared hit builder, while the physical-trap route bypasses the normal resolver's known AV11/AV12 award branch [EV-0261], [EV-0302], [EV-0311], [EV-0312]. The remaining local callback at selector 0x55 may change the contribution before caching; neither its concrete slot target nor the numeric/record semantics are established. Q-0089 tests that uncertainty against primary selector metadata and scoped official PERK rows. This is a bounded GOG mechanism question, not proof of effective Steam protection, zero Heavy/Light AVSK, or a vanilla reproduction; preserve EV-0260 for that runtime test. No call/state/ActorValue edge connects this path to OBJ-1.
