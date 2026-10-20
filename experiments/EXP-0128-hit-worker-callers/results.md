# Results

## Initial state

EV-0397's raw capture contains 95 direct call sites from 95 unique functions into GOG worker `FUN_14065b800`; it has one separately selected caller body plus 32 incoming caller bodies. EV-0423 repeats the query with the current hash-identified script and confirms the exact same caller set, 33 decompiled bodies, a 64-entry storage cap, and 62 remaining bodies. No tag-0xB constructor occurs in the inspected subset. The dispatcher case 0xB and separate Actor-state/process route both reach `FUN_1406bb690`, which calls `FUN_1406bcaa0` [EV-0397], [EV-0291], [EV-0423].

The first collector attempt used the obsolete interpretation of 64 as the complete caller count and stopped on its expected-coverage guard before writing output. That parser expectation was corrected; the failure is a tooling correction, not evidence about caller behavior. Eight of the 62 initially uninspected callers are now reviewed, leaving 54; one caller from the initial eight-function batch remains. Ordinary enemy-hit coverage, Steam behavior, effective protection, and raw AVSK remain unobserved [EV-0260].

## First remaining caller: `FUN_140656d90`

The identity-checked direct-call census finds one outgoing edge, at RVA `0x656DCC`, from `FUN_140656d90` to `FUN_14065b800`. Its stack payload's first word is `2` (RVA `0x656DC4`); it copies three fields from `param_3` and stores `param_2`, whose actor/event meaning is not identified. This caller does not construct tag `0xB` [EV-0424]. The first default query captured the same body but its metadata marked `ok=false` because this function has no analyzed incoming direct call edges; the explicit `--list-call-edges` retry completed all checks and is the positive evidence capture. This result narrows one caller only.

## Second remaining caller: `FUN_140656de0`

The function sets its payload word to `0x1E` and has one direct worker call at RVA `0x656E9D`. Captured caller `FUN_140668f50` invokes this builder with constant `0x116C` and its `param_1` under additional unresolved predicates; that pointer is also compared with the PlayerCharacter global `DAT_143138a98` in the caller body [EV-0425]. This does not identify the event type or establish ordinary-hit coverage. The caller does not construct tag `0xB`.

## Third remaining caller: `FUN_140656ef0`

This function sets payload word 0 to `0x1F` and directly calls `FUN_14065b800` at RVA `0x656F1D`. Captured caller `FUN_14035de10` invokes it after `FUN_14033e470` succeeds, checks the returned object and a byte at `+0x1A`, then requires `FUN_1406d4110()` to return true; an alternative path calls `FUN_140286ac0` [EV-0426]. The payload and event meanings are unresolved. This caller does not construct tag `0xB`.

## Fourth remaining caller: `FUN_140657290`

This function sets payload word 0 to `3` and calls `FUN_14065b800` at RVA `0x6572AD`. Captured caller `FUN_1402b3910` initializes a status word to 2, passes it to a virtual callback at slot `0x168`, then emits this event if bit 9 is set [EV-0427]. The event meaning and callback receiver type are unresolved; no tag `0xB` constructor appears in this caller.

## Fifth remaining caller: `FUN_140657460`

The function checks `param_2` for null, sets payload word 0 to `6`, increments the referenced object's counter at `+8`, and calls `FUN_14065b800` at RVA `0x657487`. Its captured caller `FUN_1402e45f0` selects this path only when a pointer/byte/predicate condition (`bVar4`) is true; otherwise it calls `FUN_1414a33c0` [EV-0428]. Event and payload meaning are unknown, and no tag `0xB` constructor appears.

## Sixth remaining caller: `FUN_1406575c0` and candidate consumer `FUN_1406b9df0`

`FUN_1406575c0` stores tag `0x10` in payload word 0 and directly calls `FUN_14065b800` at RVA `0x65767B`. Its sole captured caller is `FUN_1406b9df0`. After checking actor/state fields and calling `FUN_1406bb060`, `FUN_1406b9df0` calls `FUN_1406d4110`; when nonzero it invokes `FUN_1406575c0(DAT_14319a7c0,param_1,param_2)` and returns. The alternate branch reads numeric/flagged fields from `param_2` and, under further conditions, calls `FUN_1406be430` with `param_2` [EV-0429].

This is a candidate hit/damage consumer, but the type of `param_2`, the semantics of the predicate and helpers, and any relation to the established HitData/AV11/AV12 resolver are unresolved. H4 predicts the follow-up call-edge/decompiler traces will expose HitData and resolver correspondence; H5 predicts they will show a separate or secondary event path. No armor-XP causal edge is added yet.

## Shared handler caller census

The follow-up census finds 89 outgoing direct call edges, 28 indirect call sites, and eight incoming caller functions for `FUN_1406b9df0`. Captured `FUN_1406bcaa0` builds `local_e8` through `FUN_1407dd220` or `FUN_1407dd5b0`, then conditionally calls `FUN_1406b9df0(param_2,local_e8)` after its player skill-routing block; those builders are already mapped as HitData constructors [EV-0430], [EV-0302], [EV-0222]. Captured `FUN_140659160` case `0x10` also calls `FUN_1406b9df0` with an actor and event-data pointer when actor+0x68 is nonzero [EV-0430]. This supports a shared HitData handler call route and falsifies the proposal that the handler is unrelated to the known resolver for these mapped callers.

H4 and H5 now distinguish field-preserving tag-`0x10` re-entry from a notification-only second pass. `FUN_1407dce10` copies the source dwords at offsets `0x50`, `0x54`, `0x5c`, and `0x80`; `FUN_1406b9df0` reads those same offsets from its second argument [EV-0430], [EV-0431]. The tag-`0x10` builder clones its second argument and the dispatcher passes the clone back to the same handler. Selected pointer fields are managed separately, so exact object identity is not preserved. H4 is supported for these handler-consumed fields; whether the second pass repeats core damage side effects remains unresolved.

The helper query also captures `FUN_1406576a0`, which builds tag 8 and clones `param_3`, and `FUN_140658e50`, which builds tag `0x5c` and clones `param_2`; both dispatch to `FUN_14065b800` [EV-0431]. These account for two more of the originally uninspected callers and contain no tag-0xB constructor. Event meanings remain unresolved. No evidence shows tag 0x10 skipping armor XP: the known resolver call has already passed through its visible player skill-routing block, and ProcessTrapHit remains bounded by its own wrapper/resolver analysis.

## Shared gate predicate and mask

The identity-checked GOG query of `FUN_1406d4110` finds one direct callee and 131 direct call sites from 106 unique caller functions in its retained capture [EV-0432]. When the integer field at `DAT_1431785f0+0x6c` equals 1, the predicate obtains a per-thread 32-bit mask from TLS+0x688, allocating a bit if the slot is empty, then tests whether `DAT_14319c2e0` contains any bit outside that thread mask. This is a static control/data-flow description; the mask's writers and the state field's runtime meaning are not identified. The wide caller spread is consistent with a generic coordination gate, but does not establish its purpose or decide whether tag-0x10 side effects repeat. H4 remains supported for copied handler fields; H5 remains open. Next, trace references to `DAT_14319c2e0` and inspect candidate writers before interpreting the gate.

The address census finds 29 global-mask references across the predicate and seven neighboring functions: `FUN_1406d41c0`, `FUN_1406d4290`, `FUN_1406d48a0`, `FUN_1406d4c00`, `FUN_1406d4cd0`, `FUN_1406d5290`, `FUN_1406d5440`, and `FUN_1406d56e0` [EV-0433]. The query of `FUN_1406d41c0` confirms atomic setting/clearing of the current thread bit. Several callers capture whether their bit was previously set, bracket a function/callback path with the bit set, and restore that prior state on return [EV-0434]. Together with `FUN_1406d4110`'s other-thread test, this supports a static per-thread active-region mask interpretation.

This changes the tag-0x10 model. When another thread bit is present, `FUN_1406b9df0` dispatches a tag-0x10 payload with copied handler fields and returns. Worker `FUN_14065b800` uses a reentrant global lock, waits if another thread owns it, invokes an event callback, and calls dispatcher `FUN_140659160` if that callback does not consume the event [EV-0423], [EV-0429]–[EV-0431]. The static path is consistent with a serialized continuation when another thread is active, not a demonstrated notification-only pass. Whether the callback consumes this event, the mask clears before re-entry, or normal damage/skill side effects ultimately run remains unknown. This result does not establish an armor-XP bypass or a Steam behavior.

## Ninth additional worker caller: `FUN_140657790`

This caller writes tag `0x42`, copies `param_2`, and sends the event through `FUN_14065b800`; its sole captured caller is `FUN_1406563b0` [EV-0435]. When two preconditions in that caller hold, `FUN_1406d4110` selects the tag-0x42 worker path; otherwise it calls `FUN_140656710`. The dispatcher case 0x42 performs a virtual `+0x78` call on the payload object [EV-0397]. This shows the global gate serves another event route and is not hit-specific. The object type and event meaning remain unknown; there are now 53 uninspected worker caller bodies. Next trace the wrapper's upstream caller, then continue with the exact remaining worker set.

The wrapper census finds no direct incoming callers to `FUN_1406563b0`. The raw capture records two DATA references to its entry without source-function identity [EV-0436]. Its body uses an unresolved virtual `+0x10` method and the helper-returned object's `+0x70` field before the mask check; failed preconditions call `FUN_1405aed00`, while the clear-gate branch calls `FUN_140656710`. The wrapper may be indirectly registered, but the reference types do not identify a table or owner. Event semantics remain unknown, so continue with the exact worker list.

## Tenth additional worker caller: `FUN_1406577d0`

This builder writes tag 9, retains its referenced objects, and sends the payload through `FUN_14065b800`; the fresh query captures four callers [EV-0437]. Several choose tag 9 under `FUN_1406d4110`, otherwise making a direct call through virtual slot `+0x210`. One caller, `FUN_140a2b5c0`, contains the error string “Cannot damage a None object” for a null resolved object; this does not identify the virtual method or establish ordinary-hit semantics. `FUN_1407e7f00` has both a tag-9 branch and another branch that constructs HitData and calls `FUN_1406b9df0`; their conditions and effects need a more focused trace. The dispatcher case 9 routes the event to virtual slot `+0x210` or `FUN_140668f50` [EV-0397]. No tag-0xB constructor appears in this caller. There are now 52 uninspected worker callers; next inspect `FUN_1407e7f00` and its caller context.

## Branch discrimination in `FUN_1407e7f00`

The bounded branch/caller query confirms that a single invocation takes one of two call routes [EV-0438]. When `plVar13` is nonnull and byte `lVar4+0x48` is clear, the function constructs a local HitData object and calls `FUN_1406b9df0`. In the alternate branch, destination byte `+0x13` bit 0 gates a damage calculation and a call to tag-9 builder `FUN_1406577d0`. This establishes a conditional HitData-versus-tag-9 fork, but not the meanings of those flags, ordinary incoming-hit coverage, protection, or AV11/AV12 effects. The tag-9 route is not evidence that the same invocation also calls the HitData handler. Continue with the next exact worker caller, `FUN_140657830`; 52 of the original 62 remain unreviewed. The clean Steam hit with measured protection and raw AV9/AV11/AV12/AVSK remains the runtime discriminator under EV-0260.

## Eleventh additional worker caller: `FUN_140657830`

When `param_2` is nonnull, this builder writes event tag `0x3B`, increments the referenced object's counter at `+0x28`, stores the object and byte argument, and calls `FUN_14065b800` [EV-0439]. Its two captured callers, `FUN_14067a830` and `FUN_14073bbc0`, choose this event on the true branch of `FUN_1406d4110`; each takes another event route when the predicate is false. Tag `0x3B` is not tag `0x0B`, so this inspected caller does not support Q79-H1. It strengthens the conclusion that the active-thread gate serves multiple event types, without identifying an ordinary-hit route. Eleven of 62 original callers have been reviewed; 51 remain. Next query `FUN_140657980`.

## Twelfth additional worker caller: `FUN_140657980`

The builder stores tag `0x51` in a local payload and sends it directly to `FUN_14065b800`; the remaining captured payload storage is not assigned [EV-0440]. The GOG project has no direct incoming call edge to this function. It has one DATA reference, but the raw capture provides no source-function identity, so registration and event family remain unknown. Tag `0x51` is not `0x0B`; this body adds another non-B sample without supporting or falsifying the complete 62-caller hypothesis. Twelve of 62 original callers are reviewed; 50 remain. Next query `FUN_1406579f0`.

## Thirteenth additional worker caller: `FUN_1406579f0`

When both object arguments are nonnull, this builder writes tag `0x53`, obtains two payload values through virtual `+8` calls, increments the first object's reference count at `+0x28`, and calls the worker [EV-0441]. It has two captured callers, `FUN_1404825e0` and `FUN_140477b00`; both reach it under additional object/state predicates after cleanup/array work. Those predicates do not identify an ordinary hit, and the event's payload type remains unknown. Tag `0x53` is not `0x0B`; the sample does not support Q79-H1. Thirteen of 62 original callers are reviewed; 49 remain. Next query `FUN_140657a70`.

## Fourteenth additional worker caller: `FUN_140657a70`

The builder writes worker tag `0x0B`, retains `param_2`, stores `param_3` and `param_4`, and calls `FUN_14065b800`. Its sole captured caller is `FUN_1406bb690`. That caller requires `param_1[0x1f] != 0`; if `FUN_1406d4110` is true, it sends the tag-0xB payload with the same actor/event arguments and returns. When the gate is clear, it continues through conditional calls to `FUN_1406bcaa0`. Worker dispatcher case 0xB returns to `FUN_1406bb690`; `FUN_1407ba3e0` is a separate state/process route into that function [EV-0442], [EV-0397], [EV-0291].

This supports a static gated continuation within the resolver family and rejects the hypothesis that none of the reviewed direct worker callers constructs tag 0xB. It does not identify the caller's event as an ordinary physical hit, establish effective protection or an AV11/AV12 award attempt, determine final skill XP, or transfer the GOG route to Steam. Fourteen of 62 initially uninspected callers are reviewed; 48 remain. Next trace `FUN_1407ba3e0`'s source and process/actor arguments, then continue the exact caller census.

## Actor/process route: `FUN_1407ba3e0`

The callback has two direct callees and no analyzed incoming direct-call edges. It invokes a virtual method at `param_2` vtable offset `+0x4c8` with argument 0; if the result is false, it gets the global object through `FUN_14014ed90` and calls `FUN_1406bb690(param_2, process+0x5d0 == *param_3, 1)`. It then conditionally updates `param_2+0xc8` when the high nibble is `0x2`. Two DATA references point to the function, but neither has source-function identity [EV-0443].

This confirms a separate static Actor/process callback route into the same handler family as the tag-0xB path. The virtual method meaning, `param_3` type, table/registration owner, and relationship to an ordinary physical hit remain unknown. Treat it as a candidate callback source, not as proof of hit coverage or an armor-XP effect. Next inspect the two DATA-reference contexts, then resume the 48-caller census.

### Address correction for the callback table

The first address-context attempt used RVA `0x36669c`, which maps to code in `FUN_140366650` and has no xrefs to the selected address [EV-0444]. The intended data row from EV-0443 is at virtual address `0x14366669c`, whose GOG image-relative RVA is `0x366669c`. The corrected address is in program memory but has no function or xrefs; its address query does not expose backing bytes or owner [EV-0445]. Neither capture provides callback-registration or hit-semantic evidence.

The second data context at RVA `0x18bae08` has two analyzed DATA references, at `0x1407c3440` and `0x1407c344e`, both within `FUN_1407c3400` [EV-0446]. This identifies a candidate code source for the table-like data but not whether it initializes, dispatches or merely stores the callback entry. Next inspect `FUN_1407c3400` and its callers before drawing a callback or hit inference.

`FUN_1407c3400` has no incoming direct-call xrefs and four DATA-reference contexts. It conditionally initializes a static allocator/state object, allocates `0x10` bytes, zeros the object's `+8` field, and stores the labeled `HitFrameHandler::vftable` at offset 0 [EV-0447]. The table data places `FUN_1407ba3e0` at vtable slot 1, eight bytes after its base. This supports the class/slot relation but does not establish who invokes the factory, when the callback runs, or whether it sees ordinary incoming hits. Verify vtable RTTI before inferring more from the name.

The RTTI query for vtable RVA `0x18bae08` resolves its type descriptor to `.?AVHitFrameHandler@@`, with subobject offset 0 and type descriptor RVA `0x206EA70` [EV-0448]. A direct zero-based slot-1 query then resolves address `0x1418bae10` to `FUN_1407ba3e0` at RVA `0x7BA3E0` and rechecks the same RTTI identity [EV-0449]. The static class/slot mapping is confirmed; runtime invocation and ordinary-hit provenance remain unknown. Inspect sibling methods only if they discriminate callback purpose.

The four-entry pointer read initially left an apparent table boundary: entry 2 at `0x1418bae18` is a non-function pointer and entry 3 is `FUN_1407c1000` [EV-0450]. RTTI at the entry-3 base resolves to `.?AVAnticipateAttackHandler@@`, with a complete-object locator at entry 2, signature 1, and subobject offset 0 [EV-0451]. Thus entry 3 starts a separate complete vftable, not a HitFrameHandler sibling segment. `FUN_1407c2320` conditionally initializes allocator state, allocates 0x10 bytes, clears +8, and stores `AnticipateAttackHandler::vftable`; there are zero analyzed direct incoming calls and four DATA references [EV-0452]. This resolves the table-layout ambiguity but does not identify runtime construction, method semantics, ordinary-hit coverage, protection, or XP effects. Resume the 48 remaining exact worker callers.

The next exact worker caller, `FUN_140657ab0`, constructs tag 0x0D when its object pointer is nonnull, increments that object's +0x28 counter, and queues the event [EV-0453]. Its sole caller, `FUN_1405cd570`, checks an Actor-like virtual method at +0x4c8, calls `FUN_1405dab70`, and branches on the shared `FUN_1406d4110` gate. The gate-set branch queues tag 0x0D; the gate-clear branch may instead call `FUN_140712d10` before a virtual +0x278 call. This resembles a state/update callback route, but neither ordinary-hit coverage nor a HitData edge is shown. Fifteen of 62 initially uninspected callers are reviewed; 47 remain. Next inspect dispatcher case 0x0D and the gate-clear handler.

Dispatcher case 0x0D calls `FUN_140712d10(object[0x1f], object)` when both values are nonnull, which matches the gate-clear target from `FUN_1405cd570` [EV-0454], [EV-0453]. It does not directly call `FUN_1406b9df0` or the tag-0xB handler `FUN_1406bb690`; deeper callees are unresolved. Trace `FUN_140712d10` next, then resume the 47 remaining exact callers if this route lacks a HitData or armor-award edge.

`FUN_140712d10` has 18 outgoing direct-call edges, one indirect site, and only the two mapped direct callers `FUN_1405cd570` and `FUN_140659160` [EV-0455]. Its body gates on process/Actor flags, updates Actor fields, and calls helper `FUN_1406c21c0` among its direct callees. The complete direct-edge scan contains no edge to `FUN_1406b9df0`, `FUN_1406bb690`, or `FUN_1406bcaa0`. This is a direct no-edge result; the indirect site and `FUN_1406c21c0` descendants are unresolved. Query `FUN_1406c21c0` before closing this state/update route.

`FUN_1406c21c0` has 38 outgoing direct edges, three indirect sites, and 31 direct callers [EV-0456]. Its body sets Actor/process state, can construct `TESActionData` and `BGSActionData`, and calls process/action helpers. The complete direct list contains no edge to `FUN_1406b9df0`, `FUN_1406bb690`, or `FUN_1406bcaa0`. This bounds the direct tag-0xD route through the state handler without establishing a HitData or armor-XP connection; indirect sites and downstream behavior remain unknown.

## Sixteenth additional worker caller: `FUN_140657b50`

`FUN_140657b50` builds tag `0x0E`, retains its nonnull object at +0x28, and queues the event. Its sole captured caller `FUN_1407bc3a0` runs a virtual method at `param_2[7]+0x88`; results 1 and 2 select tag 0x0E, while result 0 instead calls `FUN_1406c9030` and emits tags 8 and 4. This caller does not use the shared `FUN_1406d4110` gate [EV-0457]. Worker dispatcher case 0x0E calls `FUN_1407136e0(object[0x1f], object)` [EV-0454]. The exact route is supported, but process-status meaning and any HitData, effective-protection, AV11/AV12, or armor-XP relationship remain unknown. H14 is supported for routing; H15 (hit/skill route) remains proposed and H16 is now supported for the bounded process/Actor-state body without direct calls to mapped HitData/tag-0xB handlers [EV-0458]. Query `FUN_1406653a0` at RVA `0x6653a0` to test the remaining direct state-helper branch; then resume the exact caller census at `FUN_140657b90`. Sixteen of 62 initial callers are reviewed; 46 remain.

## Tag-0x0E dispatcher target: `FUN_1407136e0`

The identity-checked GOG query finds 15 direct outgoing calls, five indirect call sites, and four incoming direct caller functions: `FUN_140666b80`, `FUN_1406857c0`, `FUN_1406ebea0`, and worker dispatcher `FUN_140659160` [EV-0458]. Its body checks Actor/process fields, marks TLS offset `0x768`, calls virtual methods, updates nested state/flags, releases references, and finishes with direct call `FUN_1406653a0`. The complete direct-call list has no edge to mapped HitData/tag-0xB functions `FUN_1406b9df0`, `FUN_1406bb690`, or `FUN_1406bcaa0` [EV-0458]. This supports the bounded process/Actor-state model for the direct body, while five indirect sites, virtual targets, `FUN_1406653a0`, and deeper behavior remain open. No ordinary-hit, effective-protection, AV11/AV12 award, or armor-XP effect follows. Next inspect `FUN_1406653a0` for a direct or descendant HitData/ActorValue path; the exact worker census then resumes at `FUN_140657b90` with 46 of 62 initial callers remaining.

## Final direct helper: `FUN_1406653a0`

This function has no direct calls and one incoming caller, `FUN_1407136e0` [EV-0459]. It reads the receiver's field at `+0xCC`; unless the high bits match `0x20` or `0x80`, it returns. For either selected group it tail-jumps through the receiver vtable at `+0x530`, passing whether the group is `0x20`. Ghidra's decompiler labels the indirect jump as a call, but the disassembly confirms a `JMP qword ptr [RAX + 0x530]`. The primary Actor base-table target is now resolved to `FUN_140665140`, but the actual dynamic receiver table and possible override remain unknown [EV-0462]. H15 remains open; no hit, protection, ActorValue, or armor-XP conclusion is established.

The first RTTI lookup attempt searched initialized memory for `AVActor` and found 35 matches but zero analyzed string references [EV-0460]. Address-context query at candidate RVA 0x203CDB8 found zero exact-address xrefs and did not expose backing bytes or an enclosing type name [EV-0461]. That candidate is not verified as the Actor type descriptor or tag-0x0E receiver type. A separate exact primary Actor vtable query maps base slot +0x530, but the second table that references its target remains unidentified [EV-0462].

## Primary Actor implementation of slot +0x530

The build-matched primary `VTABLE::Actor` table at RVA 0x189EC20 has RTTI `.?AVActor@@` and subobject offset zero; slot 0xA6 (+0x530) resolves to `FUN_140665140` at RVA 0x665140 [EV-0400], [EV-0462]. The target body reads and edits Actor field +0xCC state bits, builds TESActionData/BGSActionData values on selected transitions, and calls action/process helpers. The complete scan has 17 direct call edges, no indirect call sites and no analyzed incoming direct callers; it has no direct edge to mapped HitData handlers FUN_1406b9df0, FUN_1406bb690, or FUN_1406bcaa0 [EV-0463]. Another untyped table also references the target, so the runtime receiver class and any override remain unresolved. This supports the Actor action/state model for the base implementation but does not falsify H15's possible dynamic override or descendant route. No ordinary-hit, effective-protection, AV11/AV12, or armor-XP result follows.

The exact worker-caller review now covers 17 of 62 initially uninspected functions, with 45 remaining. The count correction excludes the Actor vtable/body probes EV-0462/EV-0463; `FUN_140657b90` is the seventeenth reviewed worker caller, not the eighteenth.

## Tag-0x55 Actor update continuation

`FUN_140657b90` writes worker tag 0x55, retains its object payload and calls `FUN_14065b800`. Its sole captured producer `FUN_1406e5da0` selects this route when shared gate `FUN_1406d4110` is nonzero after outer state/update checks [EV-0464]. Dispatcher case 0x55 checks `object[0x1F]` and calls back into `FUN_1406e5da0(object[0x1F], object)`, the same update routine that queued the event [EV-0465]. This is a static gated continuation candidate and a separate immediate dispatcher target from tag 0x0B's `FUN_1406bb690` path.

The complete scan of `FUN_1406e5da0` has 31 direct call edges, 17 indirect sites, and 14 direct incoming callers. Its direct body uses Actor/process fields and helpers, and conditionally calls tag-0x55 builder `FUN_140657b90`; the full direct edge list has no edge to mapped HitData handlers `FUN_1406b9df0`, `FUN_1406bb690`, or `FUN_1406bcaa0` [EV-0466]. The routine is shared by 14 callers, so its general body is not tag-0x55-specific. The indirect sites, their descendants, and the gate state on worker re-entry remain open. This supports the interpretation that `FUN_1406d4110` is a shared scheduling/state gate rather than hit-specific evidence; the tag and gate do not establish ordinary-hit coverage, effective protection, AV11/AV12, or armor XP.

## Tag-0x0F Actor/process physics route

`FUN_140657bc0` constructs worker tag 0x0F. Its sole captured caller, `FUN_140713250`, reaches the builder in a code-1 Actor/process update branch after checking shared gate `FUN_1406d4110`; the branch decrements and then clears its process timer [EV-0467]. The branch is a gated state/update route, but the status byte's meaning and worker scheduling are not established. Dispatcher case 0x0F calls `FUN_140713a20(object[0x1F], object)`. That target obtains a byte from `FUN_1406a73f0(object+0x38)` and calls `FUN_140725340(object, byte)` [EV-0468].

`FUN_140725340` has 27 direct edges, seven indirect sites and two callers. Its captured body reads Actor/process and collision/position state, uses a Havok contact collector, adjusts position/vector fields, optionally constructs TESActionData/BGSActionData, and updates Actor state. The complete direct list has no edge to mapped HitData handlers `FUN_1406b9df0`, `FUN_1406bb690`, or `FUN_1406bcaa0` [EV-0469]. Its physics helper `FUN_140b3eb50` writes the TLS profiling label `TtworldLinCast`, constructs an `hkpWorldLinearCaster`, and calls `FUN_140bec450`; the helper has three direct edges, two indirect sites and nine callers [EV-0470]. This bounded trace supports a collision/position path. It does not equate a Havok collision query with an incoming combat hit, and its indirect/downstream behavior remains open. No causal armor-protection, AV11/AV12, or armor-XP edge is supported.

## Tag-0x14 entity-update handoff

`FUN_140657c80` constructs worker tag 0x14 and has one analyzed incoming caller, `FUN_1403f5dc0` [EV-0471]. The caller walks an entity-like array at offsets +0x60/+0x68 and queues the event when `DAT_14319a7c0` is nonzero and its captured state predicates `(local_128 != 0) || (bVar5 && !bVar4)` hold. The global and predicate meanings remain unknown. This route does not use the already mapped shared thread gate `FUN_1406d4110`.

Dispatcher case 0x14 calls `FUN_1414a3950(DAT_142034080, payload, 0)` [EV-0465], [EV-0472]. The target has three direct call edges, zero indirect sites and 17 incoming callers. It acquires/releases thread-associated state using `FUN_1401947e0` and TLS, then passes the payload to `FUN_14021cd70` with base `param_1+0x1c8`; the alternate flag selects `param_1+0x1e0`. Its complete direct scan has no mapped HitData or ActorValue/skill handler. The downstream handoff function is the next discriminant, with competing models: a path into HitData/ActorValue processing, or a state/container route without that connection. Until it is traced, no transitive no-hit conclusion follows.

`FUN_14021cd70` has one direct callee, `FUN_140cc8350`, no indirect sites and eight direct callers, including `FUN_1414a3950` [EV-0473]. The body requests a BSTArray append, stores the payload in its backing array when insertion succeeds, and increments the payload's +8 reference count. This supports deferred/reference-counted storage for the immediate tag-0x14 route. An address-context query for manager global `DAT_142034080` finds 254 xrefs across 168 deduplicated functions, including dispatcher `FUN_140659160` and nearby methods, but does not resolve the member offsets or identify array consumers [EV-0474]. The broad global screen leaves the competing combat/skill versus state-only models unresolved. Inspect nearby method `FUN_1414a81f0` because it has five labeled references to the global, without presuming it drains the tag-0x14 arrays, then continue with exact worker caller `FUN_140657d80`.

The nearby method screen finds 56 direct edges, 17 indirect sites and one incoming caller for `FUN_1414a81f0`; its body reads manager field +0x228, not tag-0x14 array members +0x1c8/+0x1e0, and has no mapped direct HitData/ActorValue edge [EV-0475]. It calls `FUN_14021cd70` with `param_3` twice, but this query does not identify that pointer as the tag-0x14 array. H19/H20 therefore remain unresolved.

## Tags 0x24/0x25/0x27: shared value and physics-filter route

`FUN_140657d80` constructs tag 0x24, stores its payload and third argument, retains the payload, and directly calls worker `FUN_14065b800` at `0x140657da7` [EV-0476]. This explicit body edge and its presence in the EV-0423 remaining-caller inventory make it the twentieth reviewed caller. The same fresh query reports zero incoming callers and `XREF_CALL_EDGE=NOT_FOUND_IN_ANALYZED_PROJECT`, which conflicts with the direct body edge and inventory. Preserve the discrepancy as an index/build-analysis limitation; it is not evidence that the builder lacks a worker call [EV-0476], [CL-L290].

Dispatcher cases 0x24 and 0x25 both call `FUN_14065c6e0` [EV-0465]. The tag-0x24 case passes `(uVar26 ^ param_1[4]) & 0x7f ^ uVar26`, with `uVar26` taken from payload field +0x4c when the referenced object is nonnull and not the `-0x20` sentinel; case 0x25 passes `param_1[4]` directly. `FUN_14065c6e0` has two direct calls and no indirect sites: it gets a record through `FUN_140e83cb0`, stores the supplied 32-bit value at returned object offset +0x2c when available, and calls `FUN_140e83d30` [EV-0477].

The helper chain reaches `FUN_140e8bd30`, which sets TLS +0x768 to 0x30, obtains an object through virtual slot +0x140, reads its +0x430 field, and branches on payload byte +0x48 to either `FUN_140b3bda0` or `FUN_140b3c4e0` [EV-0477]. Those branch bodies identify themselves through TLS labels as entity and phantom filter updates. `FUN_140b3bda0` (23 direct edges, three indirect sites) and `FUN_140b3c4e0` (13 direct edges, two indirect sites) perform broadphase overlap/filter work; neither complete direct list contains the mapped HitData/tag-0xB handlers [EV-0478]. This supports H22 for the captured event-value and physics-filter route and narrows H21, but indirect virtual targets and descendants remain unresolved. Cross-system synthesis: tag 0x0F's physics path uses a world linear cast for collision/position work [EV-0469], [EV-0470], whereas tags 0x24/0x25 route into broadphase overlap/filter maintenance; both use Havok-facing code, but neither captured path establishes a combat hit, armor resolution, or skill award. The exact worker-caller sample remains 20/62, with 42 remaining. Resume the census at `FUN_140657e40`; keep H21, the xref discrepancy, and tag-0x14 consumers open.

`FUN_140657e40` is the next inventoried caller and constructs tag 0x27, stores two 32-bit arguments, retains the payload, and explicitly calls the worker at `0x140657e6c` [EV-0479]. Its incoming scan again reports zero callers despite EV-0423's membership, repeating the exact discrepancy from adjacent builder `FUN_140657d80`; count from the outgoing edge and leave the cause open [EV-0476], [EV-0479], [CL-L293]. Existing dispatcher case 0x27 also calls `FUN_14065c6e0`. It starts with payload field +0x4c when the object is valid, conditionally replaces the low seven bits from `param_1[4]`, and conditionally replaces the high field from `param_1[6]` before entering the same value-storage/overlap-filter route [EV-0477]. The value semantics remain unknown.

Across tags 0x24/0x25/0x27, different dispatcher expressions converge on one bounded event-value write and entity/phantom broadphase overlap/filter mechanism. This does not establish ordinary-hit coverage, effective protection, AV11/AV12 award, or armor XP; indirect virtual targets and descendants remain open. The exact worker-caller sample covers 21 of the 62 initially uninspected functions, leaving 41. Reviewed tags now include 0x27; EV-0462/EV-0463 remain vtable work and are excluded from this count.

## Tag-0x28 positive-float route

`FUN_140657e80` builds tag 0x28, retains its nonnull payload, stores a scalar argument carried in XMM2, and directly calls `FUN_14065b800` at `0x140657ea8` [EV-0480]. Its incoming-call scan again reports zero callers despite EV-0423 inventory membership; this is the third consecutive inspected census entry with that discrepancy [EV-0476], [EV-0479], [EV-0480]. The cause is unknown, so the explicit outgoing worker call determines inclusion.

Dispatcher case 0x28 calls `FUN_140e8f270(payload, scalar)`. That helper continues only for a positive float and has one direct callee, `FUN_140e905e0` [EV-0477], [EV-0480]. The recursive helper walks nested pointers from offsets +0x118/+0x122, selects a path by comparing a virtual lookup result with `DAT_14328f300`, then retrieves a scalar, multiplies it by the input, and invokes a virtual +0x18 setter or `FUN_140b31ba0`. A separate caller, `FUN_1407bcdf0`, reaches the same positive-scalar helper after `FUN_140e8fc90` succeeds and chooses its scalar from captured globals or object field +0x15c [EV-0481]. Its complete 26-edge direct scan contains no mapped HitData handler; five indirect sites remain. H24 is supported for this bounded recursive object/property update, while H23's possible ActorValue/combat effect remains proposed.

There is a captured decompiler/register mismatch: pseudocode for `FUN_140e8f270` renders `FUN_140e905e0(0, local_res10)`, but its disassembly leaves RCX untouched from entry to the call, and dispatcher case 0x28 passes nonnull `plVar14` in RCX [EV-0480], [EV-0481], [CL-L296]. Treat the nonnull first argument as a static ABI/register inference and preserve the contradictory decompiler output. `FUN_140e905e0` has three indirect sites, and its nested object/setter types remain unknown. No ActorValue, effective-protection, AV11/AV12, ordinary-hit, or armor-XP result is established. The exact sample covers 22 of 62 initially uninspected worker callers, with 40 remaining; the next uninspected caller in the verified inventory is `FUN_140657f70` (RVA 0x657f70). EV-0462/EV-0463 remain excluded vtable work.

## Tag-0x3C recursive callback route

`FUN_140657f70` constructs tag 0x3C, atomically retains its payload, stores three byte arguments, and directly calls `FUN_14065b800` at `0x140657fa3` [EV-0482]. Its incoming scan again reports zero callers despite its EV-0423 inventory entry, now the fourth consecutive inspected remaining-caller body with an explicit worker edge and that xref discrepancy. A single DATA reference has no source identity; cause and prevalence remain unknown.

Dispatcher case 0x3C passes the object and three bytes to `FUN_140e89260` [EV-0468]. Its captured route rejects null payloads and conditionally checks an object/state bit through `FUN_140e0f510`; it builds a local record with field +0x0C=0x0D and, when global pointer `0x14202d678` is nonnull, sends the record into `FUN_140e898f0` [EV-0483]. The decompiler renders this call with two arguments, but instruction flow loads the callback pointer into R8; retain that discrepancy [CL-L302].

`FUN_140e898f0` has one self-recursive direct edge and three indirect sites. It obtains node values through vtable +0x90, dispatches a callback, and recursively visits children at +0x118/count +0x122 through a vtable +0x18 lookup [EV-0484]. The four-entry pointer region resolves index 1 to `FUN_140e89ee0`; the callback's body calls unresolved vtable +0x98 and, when it returns a nonnull object, increments or decrements that object's +0x40 count according to record byte +0x10 [EV-0485]–[EV-0487]. Two node virtual targets and the callback's receiver type remain unknown. This supports a bounded recursive callback/lifetime route, not a combat or ActorValue interpretation; no direct HitData or ActorValue call appears in the captured route.

Cross-system synthesis: tag 0x24/0x25/0x27 routes to Havok broadphase overlap/filter maintenance, tag 0x28 to positive-only recursive scalar/property work, and tag 0x3C to callback-driven object-reference changes. All flow through the same worker dispatcher, but they remain distinct mechanisms with no shared direct HitData or ActorValue edge [EV-0477], [EV-0478], [EV-0480], [EV-0481], [EV-0482]–[EV-0487]. Tags 0x28 and 0x3C share observed child-array offsets +0x118/+0x122 and parent slot +0x18; treat this as a structural analogy until producer-backed RTTI/vtable evidence identifies the node types [CL-L303]. The caller sample is 23/62, with 39 remaining. Continue at exact next caller `FUN_140657fc0` (RVA 0x657fc0).

## Tag-0x4C gated helper route

`FUN_140657fc0` constructs tag 0x4C for a nonnull object, increments its +0x28 reference count, stores one byte argument, and calls `FUN_14065b800`; three direct callers are captured [EV-0488]. All three test `FUN_1406d4110`: when true they queue tag 0x4C, and when false they call `FUN_1406940d0` directly with that same object and byte. Existing dispatcher case 0x4C calls the same target with the payload and byte [EV-0397]. This is a static gated/deferred route with a direct fallback, not a claim that the target's complete effects are identical under worker scheduling. The 0x4C builder has three analyzed incoming calls, making the four prior consecutive zero-xref results a bounded cluster rather than a universal property [EV-0482], [EV-0488].

The next discriminant is the exact body and caller/callee graph for `FUN_1406940d0` (RVA 0x6940d0). The caller sample is 24/62, with 38 remaining. Keep HitData/ActorValue/skill descendants, ordinary-hit coverage, effective protection, and the Steam matched-hit/AVSK result open.

`FUN_1406940d0` has 12 direct call edges, six indirect call sites, and four direct callers: the three tag-0x4C producers' gate-clear branches plus dispatcher `FUN_140659160` [EV-0489]. Its body obtains process/global context, conditionally updates a value at context offset +0x15c, then in a captured branch calls `FUN_14065c6e0` with a composed value and calls `FUN_140e8f210` with an object/value pair. The first target is the same event-value helper reached by tags 0x24/0x25/0x27 and previously traced to Havok broadphase overlap/filter maintenance [EV-0477], [EV-0478]. No mapped HitData or ActorValue/armor-skill handler appears in the complete direct-call list. H30 is supported for the bounded process/context-value plus event-value/broadphase route; H29's possible indirect combat/skill descendants remain proposed because six indirect sites and `FUN_140e8f210` are unresolved.

Cross-system synthesis: tag 0x4C reuses the same process/event-value machinery as a previously separated tag family, while also entering an adjacent object/value helper whose relation to the tag-0x28 scalar/property system is not established. This is a new causal edge within OBJ-2, not evidence for armor XP. Next trace `FUN_140e8f210` at RVA 0xe8f210; then resume the exact worker census at `FUN_140658000`.

`FUN_140e8f210` is a thin forwarding wrapper: it copies two 32-bit operands into an 8-byte pair and calls `FUN_140e90750`, with one direct edge and no indirect sites [EV-0490]. Its 11 direct callers include `FUN_1406940d0`, tag-0x0D target `FUN_140712d10`, and dispatcher `FUN_140659160`, plus eight other functions; one DATA xref lacks a source identity. Captured callers provide different pairs, including `(0, selected_value)` from tag 0x4C and `(0x21, value)` from `FUN_14069b4f0`. H31 is supported only as a shared forwarding wrapper; the pair's operation semantics remain unknown.

`FUN_140e90750` is a recursive node update. It checks an associated linked list for `DAT_14328f300`, obtains a record with `FUN_1402f39c0`, reads the record's +0x4c value, conditionally replaces its low 7 bits from input word 0 and high 16 bits from word 1, obtains a storage pointer through `FUN_140e83cb0`, writes +0x2c, and calls `FUN_140e83d30`. It then gets child nodes through parent vtable +0x18 and walks pointers +0x118/count +0x122 recursively. The update chain reaches `FUN_140e8bd30`, previously linked to event-value/Havok broadphase work. Direct callers are `FUN_140e8f210`, itself, and `FUN_140e8fc90`; there are two unresolved indirect sites and four DATA references without source-function identity [EV-0491].

This supports a recurring object-tree traversal/update substrate with tag 0x28: both routes share the `DAT_14328f300` selector, `FUN_1402f39c0` lookup, child offsets, and parent slot. Their per-node operations differ: packed bit replacement and a +0x2c write here versus positive-float multiplication and a setter in `FUN_140e905e0` [EV-0480], [EV-0481], [EV-0491]. H32 is supported for the structural substrate; same runtime class, identical operation semantics, and gameplay effect are not established. The bounded scan has no mapped direct HitData or ActorValue/armor-skill edge. No protection or armor-XP result follows.

Continue the exact worker census after `FUN_140658000`; caller 25 of 62 has been reviewed, leaving 37. Retain unresolved H21/H23/H26/H29 descendants, tag-0x14 array consumers, xref discrepancies, the tag-0x28/tag-0x3C dynamic-type question, and the exact Steam protection/raw-AVSK discriminator.

`FUN_140658000` is caller 25 of the original 62. It writes payload tag 0x4D, copies two retained +0x28 objects, two retained +8 pointers, two three-word value blocks, two 32-bit values and one byte, then calls the worker at 0x1406580d8. The body has one direct edge and no indirect call sites; its incoming-call scan reports producer `FUN_1407bcdf0` and one DATA reference without source-function identity [EV-0492].

The producer checks process/object and nonnull data conditions, then uses `FUN_1406d4110`: a nonzero gate queues tag 0x4D, while a clear gate calls `FUN_140e8fc90` directly with the corresponding argument family. The EV-0490 dispatcher capture shows case 0x4D also routes the payload to `FUN_140e8fc90`; on a true return, both captured branches call `FUN_140e8f270` and follow-up state/Actor methods [EV-0490], [EV-0492]. This supports H33, a static gated deferred/immediate route to a common helper. EV-0493 resolves that helper's bounded body: a matched child node routes to packed update `FUN_140e90750`, while an unmatched `param_9` branch builds and attaches a Havok ball-and-socket or fixed constraint. The complete direct scan has no mapped HitData or ActorValue target; nine indirect sites remain open. H34 is supported for those bounded object/constraint branches and H35 remains proposed for indirect combat/skill descendants [EV-0493]. The helper is also a direct caller of `FUN_140e90750`, linking the tag-0x4D route to the packed-value update substrate [EV-0491], [EV-0492], [EV-0493].

EV-0494 resolves `FUN_140e95190` as a selector-gated BSTArray append under TLS marker 0x33. It searches `param_2` for selectors `DAT_14328f6e0` or `DAT_14328f710`; on a match it appends the object into `param_1+0x28` via `FUN_140cc8350` and increments its +8 refcount. It has 11 incoming direct callers, including `FUN_140e8fc90`. In that route, the constructed constraint is offered as the candidate item, but selection and ownership are not established. This supports H36 for the append behavior.

Next query `FUN_140e860d0` (GOG RVA 0xe860d0), the other direct target in the constraint branch. Competing models: (A) it registers/attaches the constraint into Havok or an object physics owner, predicted by constraint dataflow and Havok/world calls; (B) it reaches HitData/ActorValue/protection/armor skill, predicted by a mapped handler edge with tag-0x4D dataflow. Resolve the bounded call graph, then resume exact worker caller `FUN_1406580f0`; the census is 25/62 with 37 remaining. Nine virtual sites in `FUN_140e8fc90` remain an open transitive lane.

## Constraint attachment convergence: `FUN_140e860d0`

EV-0495 finds eight direct edges, two indirect virtual sites, five incoming direct caller functions, and one source-less DATA reference. The tag-0x4D callsite in `FUN_140e8fc90` passes `plVar9[2]` from the constructed constraint object returned through `FUN_140ef2e70`. `FUN_140e860d0` obtains owner/context state through vtable slots +0x138/+0x140. With owner field +0xc5d8 clear, it validates the constraint and endpoint fields then calls `FUN_140b3a710`; otherwise it can queue the object in the owner's indexed area and increment count +0xc5e4. The immediate route is the same exact helper mapped in the ProcessTrapHit hkpConstraintInstance attachment path [EV-0360], [EV-0364].

This supports static convergence on a shared constraint attachment/queue primitive, not identical runtime types, owner states or effects across the two callers. No mapped direct HitData or ActorValue/armor-skill call appears in `FUN_140e860d0`; its two virtual sites and deeper attachment descendants remain unresolved. The result does not establish ordinary-hit coverage, protection, or armor XP. H37 is supported for the bounded shared-helper route; H35 remains proposed for unresolved combat/skill descendants. Resume at exact worker caller `FUN_1406580f0` (25/62 reviewed, 37 remain).

## Caller 26: tag-0x4A object/value route

EV-0496 resolves exact caller `FUN_1406580f0` (RVA 0x6580f0): it writes tag 0x4A, retains the object in its +0x28 counter, stores a byte, and calls the worker. The complete body has one direct edge, no indirect sites, two incoming caller functions (`FUN_1407bc650` and `FUN_1407bc6f0`), and one source-less DATA reference. Both captured producers use `FUN_1406d4110`: on a set result they enqueue tag 0x4A with byte 1 or 0, respectively; on a clear result they call `FUN_140664b20`, then `FUN_1402ef0c0`/`FUN_140ea0760` and conditionally update the float at the returned object's +0x20 field when the new value is greater. The dispatcher case 0x4A in the build-matched EV-0455 raw capture repeats that helper/value sequence using the payload object and byte.

This supports H38 for static producer/dispatcher convergence on an object/value update under the shared gate. The captured route has no mapped direct HitData or ActorValue/armor-skill handler, but the gameplay meaning of the field and descendants of `FUN_140ea0760` remain unknown, so H39 stays proposed. No ordinary-hit, protection, or armor-XP conclusion follows. The exact census is now 26/62; 36 remain. Next trace `FUN_140ea0760` at GOG RVA 0xea0760 and compare its bounded path to HitData/ActorValue/skill handlers before returning to the next inventoried caller.

## Helper follow-up — selector-list state transition

EV-0497 traces `FUN_140ea0760` (RVA 0xea0760): nine direct edges, five indirect virtual sites, four incoming functions and one source-less DATA reference. The helper requires receiver byte +0x321 and a changed byte at +0x320, then obtains a refcounted object through `FUN_140ea6200`. After a type-field check, it walks the list from receiver virtual +0x80 and selects entries whose record +0x20 matches `DAT_14328f338`. It sets or clears a per-index bit through `FUN_140b250b0`/`FUN_140b25080`; the clear branch also resets three associated per-entry fields. It then selects `FUN_140b39940` or `FUN_140b3ae10` through a manager returned by virtual +0x140, based on record fields. This supports H40 for a byte-gated selector-list/manager transition and narrows H39, but five virtual sites, concrete types, selector meaning and deeper descendants remain unknown. No mapped direct HitData/ActorValue/armor-skill target, transitive negative, protection result, or armor-XP result is established [EV-0497].

The cross-system review adds no causal edge to OBJ-1 quest gates or to M-0017's mapped hit/protection/skill branches: the current tag-0x4A path resolves to object/list state operations, with all combat-relevant dynamic targets unresolved. Continue at exact caller 27/62, `FUN_140658130` (RVA 0x658130), and use its tag/payload and producer conditions to select a source-backed continuation.

## Caller 27 — tag-0x60 worker builder

EV-0498 resolves `FUN_140658130` (RVA 0x658130): one direct edge to `FUN_14065b800`, no indirect call sites, no direct incoming code-call edges, and one source-less DATA reference. It writes tag 0x60, increments a nonnull payload's +8 reference count, stores the pointer and calls the worker. The nearby DATA words interleave adjacent code addresses and data pointers, but no owning table function or producer is recovered. The build-matched EV-0455 dispatcher case 0x60 calls `FUN_140e88fd0(payload,1)` when nonnull. H41 is supported for this bounded mapping; H42 remains proposed because the handler and source context are unresolved. No hit/XP or runtime consequence is established. Caller count is now 27/62, leaving 35; next trace `FUN_140e88fd0` and compare object/process-state behavior with mapped HitData/ActorValue/skill routes.

## Tag-0x60 helper follow-up — recursive hierarchy callback

EV-0499 maps `FUN_140e88fd0`: two direct edges, no indirect sites, three callsites from two incoming functions, and one source-less DATA reference. For a null third argument it first searches for a selected child whose vtable identity and +0x18 flag bit match; otherwise this guard is skipped. If `PTR_FUN_14202d630` is nonnull, it invokes `FUN_140e898f0` with a `{0,input byte,4}` record and the callback pointer. That helper queries each node through vtable +0x90, invokes the callback for nonnull results, and recursively walks child pointers +0x118/count +0x122 via vtable +0x18 when the record byte is nonzero. Tag 0x60 reaches the handler with byte 1. The worker call's third-register value is not established; the callback, dynamic types, and downstream effects remain unknown. H43 is supported for this bounded traversal/callback structure; H42 remains proposed. No mapped direct HitData/ActorValue/armor-skill target or runtime result follows [EV-0499], [EV-0498], [EV-0455].

Next inspect address context at GOG RVA 0x65b582, the exact dispatcher callsite, to establish the third-argument register state. Then trace `PTR_FUN_14202d630` references/writers; return to exact worker caller 28/62 after those discriminants.

EV-0500 resolves the dispatcher callsite: at RVA 0x65b578 it sets R8B=1, at 0x65b57b copies that into EDX, at 0x65b57f loads RCX with the payload, and at 0x65b582 calls `FUN_140e88fd0`. The exact call therefore passes arg2=1 and arg3=1. For tag 0x60 the optional `param_3==0` selector/type/flag check is bypassed, while `param_2==1` enables recursive child traversal. H41/H43 are supported for this branch; H42 remains open through `PTR_FUN_14202d630` and runtime types. Next trace the global callback pointer's references/writers; no HitData/ActorValue/armor-XP result is established.

## Caller 27 — tag-0x60 worker builder

EV-0498 resolves `FUN_140658130` (RVA 0x658130): one direct edge to `FUN_14065b800`, no indirect call sites, no direct incoming code-call edges, and one source-less DATA reference. It writes tag 0x60, increments a nonnull payload's +8 reference count, stores the pointer and calls the worker. The nearby DATA words interleave adjacent code addresses and data pointers, but no owning table function or producer is recovered. The build-matched EV-0455 dispatcher case 0x60 calls `FUN_140e88fd0(payload,1)` when nonnull. H41 is supported for this bounded mapping; H42 remains proposed because the handler and source context are unresolved. No hit/XP or runtime consequence is established. Caller count is now 27/62, leaving 35; next trace `FUN_140e88fd0` and compare object/process-state behavior with mapped HitData/ActorValue/skill routes.

## Callback pointer xref: `PTR_FUN_14202d630`

EV-0501 queries the global callback pointer at GOG RVA 0x202d630. The identity-checked address-context capture reports one xref, a READ from `FUN_140e88fd0` at VA 0x140e88ffa. The pointer cell has no function boundary and the bounded context reports zero instructions, so this capture does not reveal the function-pointer value or its initialization/writer path. This result confirms the expected callback read site but leaves the callback identity and dynamic effects unresolved; H42 remains proposed. The raw capture is `.local/ghidra/gog-query-20261019T130113Z.stdout.raw` (SHA-256 `3669f14221dca24a6ca2a9346927bf1606d551dea2dc4f9562c8b4cf52ad0976`); metadata is `.local/ghidra/gog-query-20261019T130113Z.meta.json` (SHA-256 `a03c99aa8c698d9ab52890923233dc2b6965f21571f2178dcf53aa2c85030a33`).

Next use the bounded single-entry pointer query `python3 scripts/python_env.py run tools/ghidra_probe.py --pointer-table-rva 0x202d630 --pointer-count 1 --timeout 600`, then inspect the resolved target if present. Resume worker caller 28/62, `FUN_140658240` at GOG RVA 0x658240. The census remains 27/62 reviewed and 35 remaining; no mapped HitData/ActorValue/armor-skill continuation or protection/armor-XP result is established.

## Callback target resolution: `FUN_140e89be0`

EV-0502 reads the single pointer cell at GOG RVA 0x202d630. The value is 0x140e89be0 and resolves in the exact GOG 1.6.1179.0 program to `FUN_140e89be0`; the sole captured reference is the READ by `FUN_140e88fd0` at 0x140e88ffa. Both the one-entry pointer scan and xref scan completed. This identifies the static callback target but does not establish its body, dynamic node flow, or combat/skill effects; H42 remains proposed. Raw capture `.local/ghidra/gog-query-20261019T130709Z.stdout.raw` SHA-256 `e6630982544afdcef284474ea9b63d4a3251c240a92de24c44fe1d659db04db3`; metadata `.local/ghidra/gog-query-20261019T130709Z.meta.json` SHA-256 `2cf861b776acc0d6e30ba591e0149238649403a82b05731eb4e7b7641730e7ea`.

Next query `FUN_140e89be0` at GOG RVA 0xe89be0 with complete direct/incoming edge coverage and bounded direct callees; compare its body and payload flow against mapped HitData/ActorValue/protection/armor-skill routes and object/process/state work. Then resume caller 28/62, `FUN_140658240`.

## Callback body: `FUN_140e89be0`

EV-0503 maps the callback body at GOG RVA 0xe89be0. It reads `param_1+0x10`, clears that object's +0x40 pointer, atomically decrements the pointed object's +0x8 count, and calls vtable +0x8 when the prior count is 1. It then re-reads +0x40 and may tail-jump through vtable +0x128 when the pointed object's +0x10 differs from the earlier object. The function has no outgoing direct call edges, one indirect CALL at 0x140e89c12, one indirect tail JMP at 0x140e89c2f, and no direct incoming call edge. This supports a bounded reference-release/cleanup operation; the dynamic type and virtual targets remain unresolved, so H42 stays proposed and the direct no-edge is not transitive. Raw capture `.local/ghidra/gog-query-20261019T131015Z.stdout.raw` SHA-256 `df63826275c552ed4133374d4488b86cc1c4c335c2b0626aee8f43d5ee03523b`; metadata `.local/ghidra/gog-query-20261019T131015Z.meta.json` SHA-256 `2f021f471300152a3d7fe755e805379512f8216358485e6bfa80fd163616056f`.

Next test whether the adjacent pointer cells at GOG RVA 0x202d628, 0x202d630 and 0x202d638 form a callback family: run a bounded pointer-count-3 query at 0x202d628 and preserve all values and xrefs. If sibling targets are structurally related, inspect their bodies; otherwise resume worker caller 28/62, `FUN_140658240`.

## Adjacent callback cell screen

EV-0504 reads the three consecutive pointer cells at GOG RVAs 0x202d628/630/638. Their values are 0x140e89bb0, 0x140e89be0 and 0x140e89c50, each with one captured READ from `FUN_140e88e90`, `FUN_140e88fd0` and `FUN_140e88d70`, respectively. Only the center target resolves as an analyzed function, `FUN_140e89be0`; the outer target addresses have no function boundary in the current project. This supports a testable callback-cluster hypothesis but not shared semantics. Raw capture `.local/ghidra/gog-query-20261019T131409Z.stdout.raw` SHA-256 `59d04e98a71b27fee4567e3c8b0a7c343c28ef6b8269706e8c5751f7b19fcff9`; metadata `.local/ghidra/gog-query-20261019T131409Z.meta.json` SHA-256 `69962802ccfea3a0f4f1056bec2c7c4a0cd3e29a326123de7d7dda907dc19604`.

Next query address context at GOG RVA 0xe89bb0, then 0xe89c50 sequentially. Preserve exact xrefs and bounded context without inferring bodies from linear windows. If a target boundary is recovered, compare its direct routes; otherwise return to exact worker caller 28/62, `FUN_140658240`.

## First sibling callback target

EV-0505 inspects address 0x140e89bb0 (GOG RVA 0xe89bb0), which has no analyzed function boundary. The two captured references are a PARAM from `FUN_140e88e90` and the DATA pointer cell at 0x14202d628. The instruction context at the target reads word `[RCX+0x18]`, tests dword `[RDX+0x10]`, conditionally updates `[RCX+0x18]`, and returns at 0x140e89bd6. This is compatible with a shared state-callback interface but remains only a bounded linear observation; do not assign a complete function body or gameplay meaning. Raw capture `.local/ghidra/gog-query-20261019T131638Z.stdout.raw` SHA-256 `c1aea7c91d6d3b602977029aa36c11018651f1dee0fd9cf38938d68f528361cf`; metadata `.local/ghidra/gog-query-20261019T131638Z.meta.json` SHA-256 `65899dad0103da6ae443cd3afcf25062acb2753e3a3ec194fda4201c14180f3e`.

Next query address context at GOG RVA 0xe89c50; compare its function-boundary status, exact xrefs and bounded fields with this target. Then return to worker caller 28/62 if the family hypothesis remains unresolved.


## Second sibling callback target

EV-0506 inspects address 0x140e89c50 (GOG RVA 0xe89c50). It has no analyzed function boundary and two xrefs: a PARAM reference from `FUN_140e88d70` at 0x140e88da2 and the DATA pointer cell at 0x14202d638. Its bounded target context compares dword `[RDX+0x18]` with zero, loads dword `[RDX+0x10]`, sets R9B from the comparison, zeroes R8D, and jumps indirectly through `[RAX+0x170]`. This shares descriptor offsets with EV-0505's first outer target, but the bounded operation differs and neither target has a recovered function body. Treat H44 as an unresolved structural lead; the target-context comparison is complete. Raw capture `.local/ghidra/gog-query-20261019T132225Z.stdout.raw` SHA-256 `fa999217760404931e07b40651e3b9cc239386e93f236281cad185eea4aace3c`; metadata `.local/ghidra/gog-query-20261019T132225Z.meta.json` SHA-256 `f61faeab584aff648dea79884419228389b72bc86b4a727f34ac66ba1621883c`.

No causal edge to HitData, ActorValues, protection, armor skill, or quest state is added. Return to worker caller 28/62, `FUN_140658240`.


## Caller 28/62: `FUN_140658240`

EV-0507 confirms this exact remaining-set member has one direct worker call at 0x14065827d, zero indirect calls, two incoming callers (`FUN_14066dfa0` and `FUN_140738730`), and one source-less DATA reference. With nonnull object and payload pointers it builds tag 0x17, stores the two pointers and two byte inputs, atomically increments object +0x28, and submits the record. Both incoming callers invoke it only when `FUN_1406d4110` is nonzero; their gate-clear paths call `FUN_1406a19b0` after virtual slot +0x378 selection. The complete dispatcher capture EV-0465 includes case 0x17, which invokes recipient vtable slot +0x5a0 with the payload pointer and two byte values.

This is not another tag-0xB constructor. A separate action/state continuation is plausible from the builder and shared gate, but the recipient type and slot target are unresolved, so a HitData/ActorValue path through the virtual method is not excluded. No hit, protection, armor-skill or XP result follows. Next resolve primary `VTABLE::Actor` RVA 0x189ec20 slot +0x5a0, then inspect the exact target if it maps. Raw capture `.local/ghidra/gog-query-20261019T132736Z.stdout.raw` SHA-256 `1e8f276591af30e4cdd511436f4067eaf7651dc282dc74cdac354d9a7ff60eca`; metadata `.local/ghidra/gog-query-20261019T132736Z.meta.json` SHA-256 `88f1edfd56d4499066df617dd7c643e2eb1c96db7b04b1668c385aec33684c87`.


## Caller 28 slot resolution: Actor +0x5a0

EV-0508 maps primary `VTABLE::Actor` at RVA 0x189ec20, RTTI `.?AVActor@@`, subobject offset zero. Slot index 0xb4 (byte offset +0x5a0) points to `FUN_14066dfa0` at RVA 0x66dfa0. Its bounded body calls `FUN_1406d4110`; when set, it submits tag 0x17 through `FUN_140658240`, and when clear it calls `FUN_1406a19b0` plus receiver virtual +0x378. This is the same function that appears as an incoming producer for the tag-0x17 builder, creating a base Actor requeue route. A second vtable data reference at 0x1418a6ea8 also points to this function, but that table's owner is unresolved. The slot query is not a complete direct-edge census; inspect the exact target with bounded direct targets and incoming callers next. No HitData/ActorValue/protection/armor-skill/XP result follows. Raw capture `.local/ghidra/gog-query-20261019T133355Z.stdout.raw` SHA-256 `e90ae84f13030bc62120ac046e081e566c0f3c8ce6973821f62166d22637fb2a`; metadata `.local/ghidra/gog-query-20261019T133355Z.meta.json` SHA-256 `e9fd526f979305748510c9255a979e5aa4155986d5916f9fb49ec5b4d8e03943`.


## Caller 28 base Actor edge census

EV-0509 finds exactly three direct callees for `FUN_14066dfa0`: shared gate `FUN_1406d4110`, tag-0x17 builder `FUN_140658240`, and helper `FUN_1406a19b0`. There is one unresolved vtable +0x378 call and no analyzed incoming direct caller. The set-gate branch resubmits tag 0x17. The clear branch's bounded helper decompilation reads actor field +0x19d, uses an object/node returned via `FUN_140e1a040` and virtual +0x18, traverses child offsets +0x118/+0x122, invokes `FUN_14063da50`/virtual +0x1d0, and later calls `FUN_1406551c0` or changes a child +0xf4 bit. This narrows the base path toward object/node action-state work, but no complete edge scan for the helper or mapping for virtual +0x378 is captured; do not claim a transitive negative. Next query `FUN_1406a19b0` with full direct/incoming coverage. Raw `.local/ghidra/gog-query-20261019T133623Z.stdout.raw` SHA-256 `e0956decd00030f4673650f9ccbf9955a7fdb6b7968646e6836e5d10d269404f`; metadata `.local/ghidra/gog-query-20261019T133623Z.meta.json` SHA-256 `43e8f92b3ba170182d3dd24ac9b7dbe8d41f5d673bc4648028449bbfae3c1b13`.


## Caller 28 fallback helper census

EV-0510 completes `FUN_1406a19b0` direct and incoming coverage: 7 unique direct target functions across 11 callsites, 4 unresolved indirect calls, and 3 incoming callsites from `FUN_14066dfa0` plus `FUN_140738730` twice. The body branches on actor byte +0x19d, uses `FUN_140e1a040` and virtual +0x18 to obtain object/node records, iterates child arrays at +0x118/+0x122, and calls `FUN_14063da50`, virtual +0x1d0, type/name mapping helpers and `FUN_1406551c0`. The bounded `FUN_1406551c0` body obtains two node objects and calls virtual +0x1a8 for selected child entries. The complete direct list contains no mapped HitData/ActorValue/skill handler, but four virtual sites remain; do not infer a transitive or runtime negative. `FUN_14066dfa0` passes its unresolved primary Actor slot +0x378 return into this helper. Resolve that base slot at table RVA 0x189ec20, zero-based index 0x6f (= byte offset +0x378), before closing this tag-0x17 route. Raw `.local/ghidra/gog-query-20261019T134124Z.stdout.raw` SHA-256 `111c781025b6315d966b78f1482abbb1a0ce56f89c89a2ea1c00bfc162c797fb`; metadata `.local/ghidra/gog-query-20261019T134124Z.meta.json` SHA-256 `f913c7311b899c9e4952fac29ff72a03d931f94508cc35e18f1708ac0444ff6e`.

## Caller 28 Actor +0x378 forwarding thunk

EV-0511 resolves primary `VTABLE::Actor` RVA 0x189ec20, RTTI `.?AVActor@@`, subobject offset zero. Slot index 0x6f (byte offset +0x378, entry VA 0x14189ef98) maps to `FUN_1402f3770` at RVA 0x2f3770. The exact instructions are `MOV RAX,[RCX]` then `JMP qword ptr [RAX+0x380]`; decompilation confirms an indirect tail dispatch. The query reports 14 DATA references to the thunk, including the primary Actor entry, but does not resolve the downstream +0x380 target or runtime receiver type. This explains why the base table does not identify the input producer passed by `FUN_14066dfa0` to `FUN_1406a19b0`; it does not identify a hit or skill route. Raw `.local/ghidra/gog-query-20261019T134349Z.stdout.raw` SHA-256 `c5f84849d3ba6a2d99e8629f627d3540e185904ddcbf419fa4a1b4070ad25250`; metadata `.local/ghidra/gog-query-20261019T134349Z.meta.json` SHA-256 `e6418444ad12a4bdbc24ad4b7e6e7bcb4b312ae977e18256732b23c6f624ae35`.

Next query primary Actor slot index 0x70 (byte offset +0x380) using `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x189ec20 --vtable-slot 0x70 --timeout 600`. Compare the concrete slot target with HitData/ActorValue/armor-skill and object/node/action-state predictions. Preserve dynamic type/subclass uncertainty and GOG versus Steam separation.

## Tag-0x17 Actor +0x380 selector and cross-domain synthesis

EV-0512 maps primary `VTABLE::Actor` slot index 0x70 (byte offset +0x380; entry VA 0x14189efa0) to `FUN_1402e55a0` at RVA 0x2e55a0. The exact body returns TLS +0x5f0 when receiver RCX equals TLS +0x5f8; otherwise it returns the nested receiver +0x68/+0x68 pointer when present, or null. Prior complete call-edge evidence EV-0296 maps Actor slot +0x70 to the same no-call helper. EV-0511 shows the preceding +0x378 thunk forwards through runtime slot +0x380; `FUN_14066dfa0` passes the helper output to `FUN_1406a19b0`, whose bounded body uses it in object/node lookup and child-state work [EV-0509], [EV-0510].

Cross-domain synthesis: the same Actor slot +0x70 helper is used inside the GOG HitData receiver `FUN_1406b9df0` [EV-0295], [EV-0296]. This is exact code reuse between a hit-processing route and the tag-0x17 base fallback, but the hit handler uses the result as a context gate while the tag-0x17 helper uses it for object/node operations. The evidence does not establish pointer identity, shared runtime type, a causal continuation from tag 0x17 into HitData, or any AV11/AV12/armor-XP/protection effect. Q79-H46/H47 retain same-context versus independent-context models. Raw `.local/ghidra/gog-query-20261019T134938Z.stdout.raw` SHA-256 `deecc0bee4f48fbf6c19af116429647e3111ec29eb53a5d11807d3eebeda78fc`; metadata `.local/ghidra/gog-query-20261019T134938Z.meta.json` SHA-256 `04e9c5ad9f948a1fbaee88eec8c666d51ec669ce61e53390877cca33ea664980`.

Next resume the exact inventory at caller 30/62, `FUN_140658310` (RVA 0x658310). Capture its worker tag, producer branch, incoming callers, and dispatcher target, then compare direct and bounded descendants with mapped HitData/ActorValue/skill routes.

## Caller 29/62 — tag-0x19 process-gated worker event

EV-0513 finds exact inventoried builder `FUN_1406582d0` (RVA 0x6582d0) with one direct worker edge, no indirect sites, and one direct caller `FUN_140687370`. The builder writes tag 0x19, retains its payload pointer, increments payload +0x28 when nonnull, and submits it to `FUN_14065b800`. Its producer checks `FUN_1402e9000(param_1,1)`, obtains a record/type value, checks `FUN_1403e0d20`, makes an unresolved virtual +0x2b8 call, calls `FUN_1402e8f30`, then submits tag 0x19 with `param_1`. Existing dispatcher evidence EV-0455 maps case 0x19 to `FUN_140687430(payload,0)`. The handler is uninspected, and the producer's virtual target is unresolved; do not infer hit or skill meaning from the tag. Raw `.local/ghidra/gog-query-20261019T135847Z.stdout.raw` SHA-256 `819dd3e171c197b946b02ffaa032c8f108aff3e721ef234855ef9e27afb97a1b`; metadata `.local/ghidra/gog-query-20261019T135847Z.meta.json` SHA-256 `fcac2f0feaf27a7121a172d406c4a50d9a8663d0c8f0a384aae310293e4fb811`. Caller census is now 29/62, with 33 remaining.

Competing models for the next query: (A) `FUN_140687430` re-enters HitData/ActorValue/armor-skill processing; (B) it continues a process/state update independent of incoming hits. Predicted discriminant: complete its direct/indirect call census and bounded targets, then compare against mapped `FUN_1406b9df0`, `FUN_1406bb690`, `FUN_1406bcaa0`, and `Actor::UseSkill` paths. Preserve unresolved virtuals and GOG/Steam separation.


## Tag-0x19 handler direct census — EV-0514

`FUN_140687430` has 49 direct-call sites to 38 unique targets, nine unresolved virtual calls, two direct caller functions, and one source-less DATA reference in the identity-checked GOG 1.6.1179.0 project. The handler selects context through `FUN_1402e55a0`, obtains a process-associated object with `FUN_140716b10`, reads the fixed string pointer `DismemberedLimb1_Head1`, creates/updates hierarchy nodes, traverses child fields +0x118/+0x122, calls hierarchy/state helpers, updates child +0xf4, and conditionally calls `FUN_1406e5da0`. Its `param_2==0` branch has additional positional/vector work. The second direct caller `FUN_1406883b0` walks body-part records including a `Torso` string and invokes `FUN_140687430(param_1,1)`.

The complete direct target list has no mapped `FUN_1406b9df0`, `FUN_1406bb690`, `FUN_1406bcaa0`, or ActorValue/armor-skill award target. This supports process/object hierarchy updates for the bounded direct route. It does not rule out HitData/skill processing through nine virtual sites or descendants, and it is not a runtime negative. The producer virtual +0x2b8 remains unresolved. Exact capture: `.local/ghidra/gog-query-20261019T140144Z.stdout.raw` SHA-256 `d647cc087a9b932f6db75c6004b65717d557b7ebb26af76b85ca2a69e8599be0`; metadata `.local/ghidra/gog-query-20261019T140144Z.meta.json` SHA-256 `b9845fc8273fa44ab952b0be12defbe3203a0df71087fe141ea1dd9e3a49c1a1`.

Next: query `FUN_140687370` at RVA 0x687370 with complete direct/incoming edges and up to eight bounded targets; resolve the producer conditions and virtual +0x2b8 receiver/target where the static project permits, then resume caller 30/62.

## Tag-0x19 producer indexed callback — EV-0515

`FUN_140687370` has six direct call/jump edge sites to five unique functions, one indirect virtual call through receiver slot +0x2b8 at VA 0x1406873dd, one direct caller `FUN_1407baca0`, and one source-less DATA reference. The path loads an indexed pointer from `param_1[0x3f]+0x270+index*8`, calls the virtual method with that pointer and scalar flags, updates a state record via `FUN_1402e8f30` (including receiver slot +0x50 with 0x20000), then tail-jumps to `FUN_1406582d0` to submit tag 0x19. The exact target and field semantics remain open. `FUN_1402e9000` is decompiled separately as void even though this producer tests AL after the call; preserve that discrepancy.

Next resolve base Actor slot index 0x57 (byte +0x2b8) in the verified GOG table and inspect the target, then resume worker caller 30/62. Raw capture `.local/ghidra/gog-query-20261019T140833Z.stdout.raw` SHA-256 `659211ec06475a0b2b47696bc98fe7f41b289d306a1e843f25adc10995ada0c1`; metadata `.local/ghidra/gog-query-20261019T140833Z.meta.json` SHA-256 `9a5805db999621833ab571934263557d2c93e37f9a6f5d7881a866b6e6462756`. No direct evidence of hit/skill/protection/XP results follows.

## Actor +0x2b8 base target: item/equipment workflow — EV-0516

Primary Actor table RVA 0x189ec20, RTTI `.?AVActor@@`, zero subobject offset, slot index 0x57 (byte +0x2b8) maps to `FUN_1406a2cd0` at RVA 0x6a2cd0. Four captured calls to this target come from `FUN_1406a1bf0`, whose bounded item-use branches contain equip and quest-item messages. The target reads an actor list through virtual +0x3f0, checks BGSBipedObjectForm records and item/list state, and calls `FUN_14022b7a0`. This supports base-method reuse in an item/equipment workflow. The query was not a complete call-edge census, and the producer's indexed pointer/type and runtime override are unknown.

Next: complete direct/incoming coverage for FUN_1406a2cd0 and compare its callees to mapped HitData, effective-protection and AV11/AV12 functions. Raw capture `.local/ghidra/gog-query-20261019T141242Z.stdout.raw` SHA-256 `093850f503b3d1d72de41cf9502e997b1cec1ab73ea32cafd47a3dc5e389f916`; metadata `.local/ghidra/gog-query-20261019T141242Z.meta.json` SHA-256 `178acc01102a4a12290ab0a7beb06a0bd4e8e6e8370abd0fb86d20d1906bd274`. No protection/XP effect is yet established.

## Complete FUN_1406a2cd0 edge census — EV-0517

The base Actor +0x2b8 target has 22 direct call sites to 19 unique functions, four unresolved virtual calls, and four incoming callsites all from `FUN_1406a1bf0`. The full body obtains a list through +0x3f0, iterates slot/list records, checks BGSBipedObjectForm via RTTI, and calls item/container operations including `FUN_1406cc240` and `FUN_14022b7a0`. No mapped direct HitData or ActorValue/armor-skill award function is in the complete target list. Four virtuals and deeper descendants remain open; this is not a transitive or runtime negative.

Next trace `FUN_14022b7a0` with direct/incoming edges and bounded callees; then choose producer-backed virtual targets. Capture `.local/ghidra/gog-query-20261019T141556Z.stdout.raw` SHA-256 `773b229f61f39d70c9087bb7e37315f11140b3d0b6e07172d3977703f6bbd244`; metadata `.local/ghidra/gog-query-20261019T141556Z.meta.json` SHA-256 `d391b742bfac9b5e22dc1e022eaf16f137901197463746e99a8b0b22ec36ebc9`.

## FUN_14022b7a0 item/list helper — EV-0518

The helper has 115 direct call sites to 51 unique targets, three unresolved virtual calls (+0x380 twice and +0x50 once), and two incoming functions (`FUN_1402e1b20`, `FUN_1406a2cd0`). Its direct body mutates nested record/list state and calls `FUN_1406b98f0`, shared selector `FUN_1402e55a0` followed by `FUN_140661f60`, and a shared-gate branch selecting direct `FUN_1402e90d0` or `FUN_1406581b0`. No mapped direct HitData/ActorValue/armor-skill award function appears in the complete direct list. The selector's exact code identity is also present in the HitData receiver and tag-0x17 path, but returned-object identity is unknown.

Next trace `FUN_1406b98f0` with complete edges and bounded callees against the mapped HitData/protection/AV11/AV12 sinks; then inspect other descendants as evidence warrants. Raw capture `.local/ghidra/gog-query-20261019T141816Z.stdout.raw` SHA-256 `96f9a05567042ea42ab1b38d559e302e11e17e598582effc1ffd5f10ecb7c5ac`; metadata `.local/ghidra/gog-query-20261019T141816Z.meta.json` SHA-256 `bfe4c5b794b95984f34dc1048fb4f541c68e660327119f82dc36832e615332c3`.

## FUN_1406b98f0 nested selector — EV-0519

`FUN_1406b98f0` has one direct callee (`FUN_14070fd50`), zero indirect sites, and 69 direct incoming callsites across 51 functions. It reads param_1+0xf8 and returns the first qword of the callee's selected nonnull entry. The selector examines a nested +8 pointer, chooses +0x220 or +0x260 according to its second argument, and requires pointed-record marker byte +0x1a == 0x29. In the captured item helper caller `FUN_14022b7a0`, the decompiler shows selector argument 0 and uses the result in a TESActionData-related path. The target signature lists only one parameter while the direct callee uses the second argument, so preserve the register/prototype uncertainty. No direct HitData/ActorValue/armor-skill target appears.

Next trace context consumer `FUN_140661f60`, then follow remaining branch evidence. Raw capture `.local/ghidra/gog-query-20261019T142111Z.stdout.raw` SHA-256 `89fc61fddb417d9d08ebb36d11f0b9314ffe9811100eb599689e86ddbb89fcfb`; metadata `.local/ghidra/gog-query-20261019T142111Z.meta.json` SHA-256 `224df180bffa1c415de52617ae776a7558d1df1a8679b342cc9ac7b75d924258`.

## Shared context consumer FUN_140661f60 — EV-0520

The function has six direct callsites to five unique functions, two unresolved virtual +0x18 calls and 11 incoming callers. Its direct body obtains a context node through `FUN_140e1a040` using global +0x230 data, otherwise searches child offsets +0x118/+0x122 and skips names beginning `BIP`. It conditionally selects a child through `FUN_1414ae8a0`, then passes the chosen pointer to `FUN_1407158f0`, which assigns nested component +0x178 with reference-count changes. `FUN_1414ae8a0` filters by dynamic identity against `DAT_14332c3a0`. The same context consumer is called by item/list helper `FUN_14022b7a0` and process target `FUN_1406e5da0`; this is shared bounded state work, not evidence of common HitData/armor XP semantics.

Next resolve `FUN_1414ae8a0` and the `DAT_14332c3a0` identity. Raw capture `.local/ghidra/gog-query-20261019T142433Z.stdout.raw` SHA-256 `95d99f184d554f48f12750010e932aefb08b3ecc68ed7da1151278bee3fbb9ee`; metadata `.local/ghidra/gog-query-20261019T142433Z.meta.json` SHA-256 `6e8e8a76d0b76d100292ca2fb9271219fe563138cc3200d23b72b83364d8aa8b`.

## Recursive hierarchy identity selector — EV-0521

`FUN_1414ae8a0` has one direct callee (`FUN_1414ae980`), four unresolved virtual sites, and two callsites from sole captured caller `FUN_140661f60`. It walks child pointers from +0x118/count +0x122, resolves candidate objects through virtual +0x18/+0x38, obtains a nested object at +0x128, and compares that object's virtual +0x10 return to the address `DAT_14332c3a0`. A match returns the candidate; otherwise it uses the recursive fallback. The fallback's bounded decompilation shows the same identity check but was not separately queried for a complete edge census.

This narrows the +0x178 selection mechanism to recursive hierarchy matching, but `DAT_14332c3a0`'s contents/type and all selected-object readers remain unknown. No armor/protection/HitData/ActorValue/armor-skill edge or runtime negative is established. Next query GOG address RVA 0x332c3a0 for exact data identity and references, then inspect producer-backed +0x178 readers. Raw capture `.local/ghidra/gog-query-20261019T142912Z.stdout.raw` SHA-256 `b66f513d64e449dfa43448e8b21f927377ac30af676f5cbd487e8fb9e7c84bc7`; metadata `.local/ghidra/gog-query-20261019T142912Z.meta.json` SHA-256 `e891b727ba6b7d2e70b80dbbcfee7ef558b6589631b70799d735413e0152c3a0`.

## Identity global reference census — EV-0522

GOG address context for RVA 0x332c3a0 confirms mapped memory with no function boundary and 47 references. One candidate WRITE xref is at RVA 0x0d2f660; an overlapping DATA xref at +3 has no function assignment. The query did not expose the stored bytes/value or the dynamic identity type. Next inspect the write-site address context at RVA 0x0d2f660 before attempting to name the token. Raw capture `.local/ghidra/gog-query-20261019T143304Z.stdout.raw` SHA-256 `1e2750a811bd986a411157676e61ac2ad5ab9328dbe71ad1cf61db4618d83a74`; metadata `.local/ghidra/gog-query-20261019T143304Z.meta.json` SHA-256 `22b885a624cf8572713b3e8b7994f08545bd3b0bf0e7b9d21f286a0901d3edda`.

## Candidate identity-global write context — EV-0523

The address at GOG RVA 0x0d2f660 has no function boundary and 410 incoming xrefs. Its visible instructions store RDX through `[RCX]`, return RCX, and store R8 through `[RCX+8]`; they do not name DAT_14332c3a0. EV-0522's WRITE/DATA classification is therefore retained as an unresolved reference discrepancy, not a demonstrated global write. Next search the exact +0x178 displacement for selected-component readers/writers. Raw capture `.local/ghidra/gog-query-20261019T143523Z.stdout.raw` SHA-256 `d3a393ba016646f876810fdfd71143041d4c1e40aa07655486293318e43bf7a3`; metadata `.local/ghidra/gog-query-20261019T143523Z.meta.json` SHA-256 `4b09cf61c45ca590036b98798e7089d289fee113fe914f5683cddf99db4338bd`.

## Whole-program +0x178 displacement scan — EV-0524

The exact GOG scan covered 5,654,579 instructions and found 987 +0x178 accesses across 722 functions (529 stack accesses), with 199 writer-candidate functions and eight computed-writer candidates. It confirms FUN_1407158f0 reads/writes qword +0x178. Nearby FUN_140715840 reads the same displacement; FUN_140715940 compares the qword with zero and reads it later. The scan does not infer receiver types or connect those reads to the pointer selected by FUN_1414ae8a0. This broad match set reinforces collision risk; it does not identify an armor or combat field. Next query FUN_140715940 with full direct/incoming edges and bounded callees. Raw capture `.local/ghidra/gog-query-20261019T143757Z.stdout.raw` SHA-256 `b937cb27dec6ece29fe3c5d0a898cf110d41ac53a0dfaebf7e07c2b758781000`; metadata `.local/ghidra/gog-query-20261019T143757Z.meta.json` SHA-256 `daf60922bbcad6fc537806c85567602d5efa5642927355aa289b95b346c4380f`.

## Actor-update +0x178 consumer candidate — EV-0525

`FUN_140715940` has 13 direct call targets and no indirect call sites; its two incoming callers are `FUN_140773750` and `FUN_140734890`. Under a component/flag condition it reads `(*(param_1+8))+0x178`; on a non-global path it passes the nested selected object's +0x70 pointer to `FUN_1414fdb10`, combines the float result with other inputs, then calls `FUN_1406eeb00` and `FUN_1406e68a0`. Another branch calls the shared context selector `FUN_1402e55a0` and `FUN_140661f60`. The captured caller `FUN_140734890` passes `param_1[0x1f]`, `param_1`, 0. These support a bounded actor-update state path, but not armor/protection/HitData semantics or exact pointer identity with the +0x178 setter. Next trace `FUN_1414fdb10`. Raw capture `.local/ghidra/gog-query-20261019T144133Z.stdout.raw` SHA-256 `20e0e85e9f030b03643c9b2371cd6538c3b47875aca3b233b41679e5705ade65`; metadata `.local/ghidra/gog-query-20261019T144133Z.meta.json` SHA-256 `d48b6c85e15f5822469424b3401b620399ebded504793789ec`.

## Position-dependent nested-context float aggregation — EV-0526

`FUN_1414fdb10` has one direct callee (`FUN_14150aea0`), no indirect sites, and one incoming caller (`FUN_140715940`). It loops a pointer/count array and sums each callee's float result. The callee reads record fields at +0x48, +0xa0/+0xa4/+0xa8, and +0x11c/+0x124/+0x128/+0x134; its body computes a square-root distance factor, caps it, and returns a weighted float. `FUN_140715940` supplies the nested +0x178 object +0x70 pointer as the array parameter. This gives a bounded actor-update context calculation; it does not name the record type or the eventual effect. Next trace `FUN_1406eeb00`, which receives the aggregate result. Raw capture `.local/ghidra/gog-query-20261019T144515Z.stdout.raw` SHA-256 `b95c93ad62d3d6570543c1fb285ab8c9604b2f62091f3b61d0ed5319946c2e28`; metadata `.local/ghidra/gog-query-20261019T144515Z.meta.json` SHA-256 `57022d9a5a8ce72c89775f0593b15bae1601468c4cdb724c888c036ea5ae0a53`.

## Aggregate field sink — EV-0527

`FUN_1406eeb00` has no outgoing call or indirect sites and one incoming caller, `FUN_140715940`. Its complete body checks `param_1+0x10`, then stores the incoming float at `(*(param_1+0x10))+0x3a8`. The field meaning is unknown; this is a bounded object-state write, not a mapped ActorValue/HitData call. `FUN_140715940` next invokes paired update `FUN_1406e68a0`, which is the next discriminator. Raw capture `.local/ghidra/gog-query-20261019T144738Z.stdout.raw` SHA-256 `3ddf93cc64129b9bc34d293ad4bec3dd375468c34f527c53bf8e22710ad576de`; metadata `.local/ghidra/gog-query-20261019T144738Z.meta.json` SHA-256 `4618fa608739143736056414a27217ffe698b4abf895e581e32b569b00e51d60`.

## Paired actor-update field sinks — EV-0528

The GOG AE 1.6.1179.0 read-only edge census for `FUN_1406e68a0` found zero outgoing calls/indirect sites and one incoming callsite from `FUN_140715940`. Its bounded body conditionally stores the 32-bit argument to `(*(param_1+0x10))+0x3b0`. The captured caller first sends its distance-weighted float through `FUN_1406eeb00` to the same nested-base expression +0x3a8, then passes `DAT_14319c47c` to `FUN_1406e68a0` and clears flag +0x328. Both setters make no further calls. This establishes a paired actor-update state write in this path, not field semantics, reader identity, or an armor/HitData/ActorValue effect. No OBJ-1 edge is established; the relation to M-0096 remains analogy only.

Raw `.local/ghidra/gog-query-20261019T145047Z.stdout.raw` SHA-256 `245b48af61c264731281dfef03837df1e538b6ccb95f3d54bc93141c74696253`; metadata `.local/ghidra/gog-query-20261019T145047Z.meta.json` SHA-256 `bbeaa096eeaa087ce5511b2cc327b6264395ae8037d41e0b51af6014798ad47f`. Next inspect producer-backed readers of +0x3a8/+0x3b0 and keep collision candidates separate.

## Whole-program +0x3a8 reader census — EV-0529

The completed GOG scan visited 5,654,579 instructions and found 54 operand accesses across 38 functions, 15 writer-candidate functions, two computed-writer candidates, and 49 stack accesses. `FUN_1406eeae0` reads dword [RAX+0x3a8] at RVA 0x6EEAE9, adjacent to `FUN_1406eeb00` at RVA 0x6EEB00, which writes float [RAX+0x3a8]. Separate same-offset readers and writers remain, including `FUN_1406ebea0`; displacement alone does not identify the receiver.

Raw `.local/ghidra/gog-query-20261019T145542Z.stdout.raw` SHA-256 `cf19c1ec550b38091a2e6341f9baea3223ce46ae34425807afef593072d96d75`; metadata `.local/ghidra/gog-query-20261019T145542Z.meta.json` SHA-256 `425cbca9d1817f7fa52d27dac4412262869cb0ff08cb86a0e3cdb24e09f9041c`. Next query `FUN_1406eeae0` with complete caller/callee edges; compare same-field and offset-collision models before assigning identity.

## +0x3a8 getter callers and detection/light use — EV-0530

The getter `FUN_1406eeae0` returns the dword at `(*(param_1+0x10))+0x3a8` or zero and has four captured callers. `FUN_1406807c0` and `FUN_140692aa0` pass outer +0xf8 values; `FUN_14032ada0` logs the result in the format “GetDetected >> %i and light %i”. The actor-update caller `FUN_140734890` passes `param_1[0x1f]` to `FUN_140715940`, the setter route, matching the +0xf8 qword expression structurally [EV-0525]. This supports a shared +0xf8 nested-state route and a light/detection use, but does not prove identical runtime class/instance or connect the field to armor/HitData. `FUN_1406936f0` decompiles a call with no visible argument despite its direct xref; preserve the register/prototype uncertainty.

Raw `.local/ghidra/gog-query-20261019T150035Z.stdout.raw` SHA-256 `6cc81677630d44a937a68e2f46008745ee74fa6081aec37bbe4eb8790b83dd19`; metadata `.local/ghidra/gog-query-20261019T150035Z.meta.json` SHA-256 `0675f8e0c7f34b1f8570a79da33e1dc88ff22099e22a757024f432bf9aa5b5a6`. Next resolve `FUN_140734890` caller/source details.

## +0xf8 actor-update orchestration and shared state route — EV-0531

`FUN_140734890` has 143 direct call edges, 33 unresolved indirect sites, and no analyzed direct incoming caller. It passes `param_1[0x1f]` (+0xf8) to both `FUN_1406e5da0` and `FUN_140715940`; the latter performs the nested +0x3a8/+0x3b0 writes [EV-0531], [EV-0525], [EV-0528]. The same outer +0xf8 slot expression is supplied by callers of `FUN_1406eeae0`, a +0x3a8 getter used in detection/light paths [EV-0530]. This strengthens a structural shared-state path, not an exact class/instance identity. No direct call to the mapped HitData resolvers appears in the edge list. Primary Actor vtable registration and 33 indirect calls remain unresolved.

Raw `.local/ghidra/gog-query-20261019T150516Z.stdout.raw` SHA-256 `d6620f8345ea70ba475e98c139a6cb1db1cc5dd34c8aed0bfe9f8a7de43635f1`; metadata `.local/ghidra/gog-query-20261019T150516Z.meta.json` SHA-256 `b4deb13647d61385c333ee142a7d76d1d72ada72dcc8e67adc4a44a0d48b2e1c`. Next query primary Actor vtable slot index 0xE3 (+0x718).

## Primary Actor +0x718 slot discriminator — EV-0532

The primary GOG `VTABLE::Actor` table at RVA 0x189EC20, slot index 0xE3 (+0x718), resolves under `.?AVActor@@` RTTI/subobject offset 0 to `FUN_1406b9000` (RVA 0x6B9000), not `FUN_140734890`. The target checks a nested pointer at +0x160 and byte +0x43 before returning a boolean-like value. A second untyped table at RVA 0x18A7020 also references FUN_1406b9000. The expected primary base-slot link is falsified; no data reference or alternate vtable owner for FUN_140734890 is established. Preserve the shared +0xf8 argument as structural only.

Raw `.local/ghidra/gog-query-20261019T150821Z.stdout.raw` SHA-256 `f23638ba582ac58d2b91bd44880555eecbaa38e40546fac36935c389b369500b`; metadata `.local/ghidra/gog-query-20261019T150821Z.meta.json` SHA-256 `5726e96900bab63f63087efae8718c364157bef125a7f7112f53eb3e2156c400`. Next inspect all code/data references to FUN_140734890.

## FUN_140734890 source-reference census — EV-0533

The address-context query reports two DATA references to FUN_140734890, from VA 0x143660620/RVA 0x3660620 and VA 0x1418ad2d8/RVA 0x18ad2d8. Both sources lack a recovered function identity. The query does not establish a vtable, callback/registration table, or class owner. Combined with the primary Actor +0x718 mismatch [EV-0532], keep the +0xf8 route structural only and do not infer the function is unreachable.

Raw `.local/ghidra/gog-query-20261019T151045Z.stdout.raw` SHA-256 `dde14413758c8c0046a88879e900ac8f2c20c91c24e1c3eb040db19981a02def`; metadata `.local/ghidra/gog-query-20261019T151045Z.meta.json` SHA-256 `3530fe7adb1f7069675c43ae51c2b7bdbc944890cfaa6bddbe2760cc4cc091b8`. Next inspect source RVA 0x18ad2d8.

## FUN_140734890 source-address context — EV-0534

Address-context query at the source location previously reported as a DATA ref to `FUN_140734890` confirms RVA 0x18ad2d8 is mapped, has no function identity, zero references pointing to that location, and no instruction at the exact address [EV-0534], [EV-0533]. This does not expose the qword value or an enclosing table. Do not infer a vtable/registration owner; inspect at most one pointer-sized entry before deciding whether neighbors or RTTI are warranted. Primary Actor slot +0x718 still maps to `FUN_1406b9000` [EV-0532].

Raw `.local/ghidra/gog-query-20261019T151420Z.stdout.raw` SHA-256 `3a6edbdc1c56c25648a3ee277d504d38bf4f6b890e866f0aba239ce80b845224`; metadata `.local/ghidra/gog-query-20261019T151420Z.meta.json` SHA-256 `7cee95fbe88bf00484c9553f51a03bed388fb5584c5e70872278b1314b771304`.

## FUN_140734890 data pointer at RVA 0x18ad2d8 — EV-0535

A one-entry query reads qword `0x140734890` at RVA `0x18ad2d8`, resolving to `FUN_140734890` at RVA `0x734890`; the complete entry-reference scan reports zero xrefs pointing to the entry [EV-0535], [EV-0533]. This supports a static pointer from that location to the function. One value does not establish an enclosing vtable/callback table, owner, runtime class, or execution. The second source RVA `0x3660620` remains to inspect.

Raw `.local/ghidra/gog-query-20261019T151653Z.stdout.raw` SHA-256 `6ea336782559e9e98a6f19aa768bdaa2ad386ba4ca9991437517b066edef94da`; metadata `.local/ghidra/gog-query-20261019T151653Z.meta.json` SHA-256 `3f42b4ec9f59df89ab4ae5056ec8fdf2052bd638e08af724fef5e2ffa4a46fdb`.

## Second FUN_140734890 data-reference source — EV-0536

A one-qword read at RVA `0x3660620` returns `0x735D6800734890`; Ghidra’s 64-bit target is not a function, and the complete entry-xref scan finds zero references pointing to this entry [EV-0536]. The low 32 bits `0x00734890` equal FUN_140734890’s RVA; high 32 bits `0x00735D68` are an unresolved address candidate. Competing interpretations are two packed 32-bit RVAs versus an unrelated 64-bit field whose low word coincides with the function RVA. Next check the high-half candidate as an exact GOG address, without assuming an encoding.

Raw `.local/ghidra/gog-query-20261019T151857Z.stdout.raw` SHA-256 `b9ce7f260dd8cf79627a2c64a6b2d8a2c2f0fe92ed7b550d2c7fae701645bf66`; metadata `.local/ghidra/gog-query-20261019T151857Z.meta.json` SHA-256 `e71f2b7c7c9bf2779cda542e84cec8a1edffe9cfc34b664546ba1db84167c02d`.

## High-word candidate address context — EV-0537

The high-word candidate RVA `0x735D68` is mapped but has no function, incoming references, or instruction at the exact address; the preceding decoded instruction at VA `0x140735D67` is `RET` [EV-0537]. This is compatible with an exclusive-end boundary, but the RET owner is not yet identified and no relation to `FUN_140734890` is established. Check the function containing that RET before interpreting the second qword as a start/end pair.

Raw `.local/ghidra/gog-query-20261019T152121Z.stdout.raw` SHA-256 `218e2dee0aa87b109c5cd14faf16041a30bdc4fda8004da49f10d820b0ce5edc`; metadata `.local/ghidra/gog-query-20261019T152121Z.meta.json` SHA-256 `5f7487fdfc58d91ce0aea31c634ee98507eaa6618c0bc4a11a521bb8a770dac4`.

## RET owner for the EV-0536 high word — EV-0538

Address query at RVA `0x735D67` returns `FUN_140734890` as the containing function and decodes `RET` at VA `0x140735D67` [EV-0538]. The qword at RVA `0x3660620` has low32 `0x734890` (that entry RVA) and high32 `0x735D68` (the byte after the RET) [EV-0536], [EV-0533]. This matches a start/exclusive-end range pair for this function, but data format/owner and runtime registration are still unproven. Read one adjacent qword at RVA `0x3660628` to test whether the same layout repeats.

Raw `.local/ghidra/gog-query-20261019T152425Z.stdout.raw` SHA-256 `5a4c57af4114563e507b6cb157bf0d6c7da908b53185243ae32b6534f23ae41a`; metadata `.local/ghidra/gog-query-20261019T152425Z.meta.json` SHA-256 `c79fa74cb4540182a82bbd27ce002da79eabd8831e1408aac160a53cf159e493`.

## Adjacent qword after the candidate function-range pair — EV-0539

The qword at RVA `0x3660628` is `0x735D7001D74768`; low32 is `0x01D74768`, high32 `0x00735D70`, and the latter matches a decoded `PUSH` instruction address in EV-0538’s post-RET context [EV-0539], [EV-0538]. It could be a third 32-bit field followed by the next row’s begin RVA in a 12-byte function-range table, but the address is not confirmed as a function entry. Query RVA `0x735D70` before assigning the row layout; do not infer runtime registration.

Raw `.local/ghidra/gog-query-20261019T152657Z.stdout.raw` SHA-256 `6da2dba4f13dc51b4afb9871d127382649cce96914de72617410ed2a78559262`; metadata `.local/ghidra/gog-query-20261019T152657Z.meta.json` SHA-256 `a16087c6345baa7de3bd877cb1855a628a55ff6204a87ad0fe7f741d5cbb8763`.

## Candidate next begin RVA — EV-0540

Address query at RVA `0x735D70` resolves to `FUN_140735d70`; one DATA ref comes from RVA `0x366062c`, 12 bytes after the candidate first row at `0x3660620`, with two additional source-less DATA refs at RVAs `0x1d749a8` and `0x1d749dc` [EV-0540]. This strengthens, but does not prove, a 12-byte function-range-row pattern. Read the first two dwords at `0x366062c` and compare them with FUN_140735d70’s start and observed end; no PE `.pdata`, unwind, registration, or gameplay semantics are inferred.

Raw `.local/ghidra/gog-query-20261019T152923Z.stdout.raw` SHA-256 `5a633aacd113e5f31ab868e2b4dbbf70c88aac8e5ba03fb3dfcaafb83638f74d`; metadata `.local/ghidra/gog-query-20261019T152923Z.meta.json` SHA-256 `56abad975b837f66b133ffc13b35f72800f370639de91cfb118ddbc2f4ee06d5`.

## Second candidate range end — EV-0541

The qword at RVA `0x366062c` is `0x735DA200735D70`; low32 `0x735D70` matches FUN_140735d70’s entry, while high32 `0x735DA2` is a candidate end [EV-0541], [EV-0540]. This repeats the candidate begin/end shape from the preceding row. Check the instruction at `0x735DA1` and its containing function before promoting a range interpretation; table section, format, and runtime owner stay unknown.

Raw `.local/ghidra/gog-query-20261019T153117Z.stdout.raw` SHA-256 `124dc6129901f677d773c0c9fe2a2123b9fbc96f1700c9230ede3fd21832ba76`; metadata `.local/ghidra/gog-query-20261019T153117Z.meta.json` SHA-256 `ad706b012e1c9e392e484394977518b924ad1ea51a4e80ea674526620bddb36e`.

## Candidate end-minus-one check — EV-0542

RVA `0x735DA1` remains associated with `FUN_140735d70` but has no instruction boundary itself; the nearest preceding decoded instruction is `MOV RCX,RBX` at RVA `0x735D9F`, not `RET` [EV-0542]. Thus the predicted end-minus-one RET for candidate end `0x735DA2` is not observed. Check exact function membership at `0x735DA2` once; do not promote a repeated code-range-row interpretation unless the candidate is outside the function body.

Raw `.local/ghidra/gog-query-20261019T153320Z.stdout.raw` SHA-256 `ee90ee8a0a5813d1c92c0fcc696157db3878a63f405b16de2dd3ca02399b0794`; metadata `.local/ghidra/gog-query-20261019T153320Z.meta.json` SHA-256 `c6f62727f663f1e2a6f57af3de50fb3eb8230ff9467afb798371a378fba7c0ac`.

## Candidate end membership check — EV-0543

RVA `0x735DA2`, the high32 of the second qword candidate, is an instruction inside `FUN_140735d70`: `MOVAPS xmmword ptr [RSP+0x40],XMM6`. Ghidra reports five DATA refs to that address [EV-0543]. This falsifies the proposed second row’s exclusive-end interpretation; adjacent qwords do not establish a repeated function-range table. The first row’s address coincidence remains unexplained, and no runtime owner or HitData/armor edge was found. Close this side subline and return to caller 30/62 (`FUN_140658310`).

Raw `.local/ghidra/gog-query-20261019T153529Z.stdout.raw` SHA-256 `6384051e9fcd7ec7b08e964ed607c8d1bfb9e463141ccbe6b6ac7011b8c742f0`; metadata `.local/ghidra/gog-query-20261019T153529Z.meta.json` SHA-256 `411228b4c78acdf18f338d6b8888202ceca18550334deaeb920effaa07640749`.

## Caller 30/62 — tag-0x1A gated worker event

EV-0544 maps exact worker caller `FUN_140658310` (RVA `0x658310`) with one outgoing worker edge, zero indirect sites, and one direct caller `FUN_140640910`. It writes tag `0x1A`, increments nonnull payload +0x28, and submits it. The producer checks a global byte, a nested object byte equal to `0x1d`, `FUN_1402fa8c0()==0`, `param_2[2]`, and `FUN_1406d4110`; alternate branches call other helpers/builders. No tag-0xB or direct HitData/AV/armor-skill call appears in this caller. Dispatcher case `0x1A` remains to inspect; do not infer event semantics.

Raw `.local/ghidra/gog-query-20261019T153917Z.stdout.raw` SHA-256 `4e319866d5b9db10c1f0f43535ad421168278459f945c21e88c91b55541af78b`; metadata `.local/ghidra/gog-query-20261019T153917Z.meta.json` SHA-256 `35df43876ebadd274ed4d23490f53a99ea18701cc3862b7bfbd9616295f96d76`.

Next: inspect `FUN_140659160` case `0x1A` and its exact direct target(s), then resume caller 31/62 `FUN_140658350`.

## Tag-0x1A dispatcher case — EV-0545

The complete direct-edge census of worker dispatcher `FUN_140659160` reports 198 outgoing direct edges, 81 indirect sites, and a complete direct scan. Case `0x1A` loads the payload and calls `FUN_1404c2480(DAT_1420f9d38,payload)`; adjacent case `0x1B` calls `FUN_1404c2650` with the same global/payload shape [EV-0545]. Case execution and event semantics are unknown. Inspect `FUN_1404c2480` before deciding whether this state path has any direct HitData/ActorValue sink; then continue caller 31/62 `FUN_140658350`.

Raw `.local/ghidra/gog-query-20261019T154137Z.stdout.raw` SHA-256 `21e9b0535970e075b44ecfdbde508e3dd4221c80368c9b7e3643b6051049a034`; metadata `.local/ghidra/gog-query-20261019T154137Z.meta.json` SHA-256 `161a5abe1805744f2160c3d35df84afbabe7ccc6cdfd63f18d6d967d5ea45f33`.

## Tag-0x1A handler — guarded registry/list update (EV-0546)

`FUN_1404c2480` has eight direct calls, zero indirect sites, and four direct callers (`FUN_1402daa60`, `FUN_140640910`, `FUN_1401d4620`, and `FUN_140659160`). Its body saves/restores TLS +0x768 with marker 0x4F, locks `DAT_1431463f0`, reads payload integer +0x14, gates on a nested type byte and `FUN_14027d830`, hashes the integer, searches stored hash/list/array entries, and removes or appends the ID [EV-0546]. No direct HitData/ActorValue/protection/armor-skill path appears. `FUN_1404c2200` calls deeper helper `FUN_1404ca0f0`, which remains unexpanded; do not call this a global negative. Continue exact worker caller 31/62 `FUN_140658350`.

Raw `.local/ghidra/gog-query-20261019T154344Z.stdout.raw` SHA-256 `4bc938f41b11102e17a4f239622971abfafcae571754bfe83c617d7111da2c54`; metadata `.local/ghidra/gog-query-20261019T154344Z.meta.json` SHA-256 `846ebfc771da2116fd01d982379ac8232603a5f9ce94f7ef940bbada4f16a143`.

## Caller 31/62 — paired tag-0x1B worker builder

EV-0547 maps `FUN_140658350` (RVA `0x658350`) with one worker edge, zero indirect sites, and one direct caller `FUN_140640910`. It writes tag `0x1B`, retains/increments the payload, and submits it. The same producer selects queued tag 0x1A or 0x1B from `param_2[2]` and `FUN_1406d4110`; when the queue gate is clear it calls `FUN_1404c2480` or `FUN_1404c2650` directly [EV-0547], [EV-0544], [EV-0545]. This is consistent with deferred versus immediate paired registry operations, but event semantics are unknown. No tag-0xB or direct HitData/AV/armor-skill path appears. Inspect `FUN_1404c2650` next, then return to caller 32/62 `FUN_140658390`.

Raw `.local/ghidra/gog-query-20261019T154616Z.stdout.raw` SHA-256 `0bb5e6a8a5c1f651fcf5ce97d3ce4fc1c7f48cf7d1c5cc5ed9372b230fd3d33b`; metadata `.local/ghidra/gog-query-20261019T154616Z.meta.json` SHA-256 `ca03e57e4beb17251303117327add01faaa7cecfde00e2ad2250aa76c51cefa9`.

## Tag-0x1B handler — paired registry transfer (EV-0548)

`FUN_1404c2650` has 8 direct calls, zero indirect sites, and 6 callers including `FUN_140640910` and dispatcher `FUN_140659160`. Under nested byte/bit gates it removes payload ID +0x14 from manager integer array +0x100 with `FUN_1403241a0`, adds payload pointer to array +0xe8 with `FUN_1404ca0f0`, and may call `FUN_1404c2290` to remove the payload pointer from secondary +0x40 storage and follow reference-counted child entries through `FUN_1404c7d60` [EV-0548]. This conditionally complements tag-0x1A’s bounded registry updates, but event/class semantics remain unresolved; one virtual release call remains in the nested helper. No direct HitData/AV/protection/armor-skill path appears. Continue caller 32/62 `FUN_140658390`.

Raw `.local/ghidra/gog-query-20261019T154806Z.stdout.raw` SHA-256 `6d10b7d86356e64ee3cdf23c70f07fa2b1c72c569a053b8554423c8f5d45d619`; metadata `.local/ghidra/gog-query-20261019T154806Z.meta.json` SHA-256 `9ec42da1a7955c72d1ce146c018b52d3a80bab2bcae0336a740b8f85684cabb7`.

## Caller 32/62 — tag-0x1c Actor/process continuation

EV-0549 maps exact worker caller FUN_140658390 (RVA 0x658390): it stores tag 0x1c, retains the nonnull payload pointer at +0x28, and calls FUN_14065b800. Its one captured direct producer is FUN_140729140. Existing dispatcher capture EV-0545 shows case 0x1c calls FUN_140729140(payload,0).

EV-0550 finds 15 direct calls, three indirect sites, and nine direct callers of FUN_140729140. In the dispatcher-supplied zero-argument branch, the helper skips the three vtable calls at +0x3f0/+0x3f8, checks FUN_1406d4110, and when clear calls Actor/process update helpers including FUN_1406e5da0. This is a shared update helper with eight other direct callers, not a tag-specific combat interpretation. No direct mapped HitData/ActorValue/protection/armor-skill target appears in the bounded body; FUN_1406e5da0 descendants, runtime gate scheduling, and Steam behavior remain open.

Caller 32 does not construct tag 0x0b and does not resolve H3. Q79-H1 remains supported from earlier exact tag-0x0b evidence, Q79-H2 remains falsified as a full-set claim, and whether the tag-0x0b route is an ordinary incoming hit remains unresolved. The inventory now has 32/62 callers reviewed; 30 remain. Next inspect caller 33/62 FUN_1406583d0.

Raw .local/ghidra/gog-query-20261019T155132Z.stdout.raw SHA-256 7c9e373e4c1aaf1b49d659d1b85a4db20d611238bc216e30c006d806cd5d36a0; metadata .local/ghidra/gog-query-20261019T155132Z.meta.json SHA-256 a2d768f30b3e52c6e35cd7bee60b19f860e2013437dd4ef46e052531a1920229.
Raw .local/ghidra/gog-query-20261019T155306Z.stdout.raw SHA-256 8d364caee6aa916813b03d4d94245fb7375a9657eeb53472146621529b321046; metadata .local/ghidra/gog-query-20261019T155306Z.meta.json SHA-256 828bf3ad50ac96558f5141b6984d28e0c69d8d9596a550150211b798c7613ff4.

## Caller 33/62 — tag-0x1d object-state path

EV-0551 maps exact worker caller FUN_1406583d0: it retains the payload, writes tag 0x1d, stores two byte arguments, and calls FUN_14065b800. Its only captured caller is FUN_1401d4620. EV-0545 shows the dispatcher returns that object and both bytes to FUN_1401d4620.

EV-0552 gives 14 direct calls, 3 indirect sites, and 8 callers. FUN_1401d4620 accepts nested type bytes 0x18/0x1c/0x1d, queues tag 0x1d under the shared thread gate, and on direct paths performs property work with strings Open or Close. Under separate global/type/helper gates it calls FUN_1404c2480 or FUN_1404c2650, the handlers mapped for tags 0x1a/0x1b [EV-0546], [EV-0548]. No direct mapped HitData/AV/protection/armor-skill target appears in bounded bodies; virtual targets and receiver identity remain unresolved.

Caller 33 does not construct tag 0x0b. Q79-H1 remains supported, H2 remains falsified as a full-set claim, and H3/ordinary-hit coverage remain unresolved. The inventory now covers 33/62 callers, with 29 remaining. Next inspect caller 34/62 FUN_140658480.

Raw .local/ghidra/gog-query-20261019T155825Z.stdout.raw SHA-256 f1f549a89a128588a180deb8a89461c91b7593cc7af2be52371323f8b7749218; metadata SHA-256 d9b0b55381191d44886f004330562c2f01d55e46adca1490aa0116fde93b5e10.
Raw .local/ghidra/gog-query-20261019T155947Z.stdout.raw SHA-256 ff0dcc9833f8eae0b57185b06b1395a54c8fba0e5ee624d99596b8b46713bbd2; metadata SHA-256 b92113c213fdcb16111c583584356b0f6e25afb1e4bfee81a2d81c07b99b4ba0.

## Caller 34/62 — tag-0x21 generation-handle Actor continuation

EV-0553 maps FUN_140658480: one outgoing worker edge, zero indirect sites, one producer FUN_14067e960. The builder stores tag 0x21, a 32-bit key, and a scalar. Existing dispatcher case 0x21 resolves the key and calls virtual slot +0x6c8 with the scalar [EV-0545].

EV-0554/EV-0555 trace the key through global generation-managed tables: FUN_140178cf0 allocates/reuses an index-generation handle and retains source object +0x20; FUN_14018a7e0 validates generation fields and recovers object base by subtracting +0x20. EV-0557 maps primary Actor table slot 0xD9/+0x6c8 to FUN_14067e960, the same function that queues the event. The bounded static model is therefore a deferred re-entry into the same primary Actor base method. Runtime dynamic overrides and gate state remain unknown.

EV-0556 maps the clear-gate branch and a separate Actor caller into the same nested Actor/process object and FUN_140ea05c0 wrapper, which dispatches via nested +0x190/vtable slot +0x8. EV-0558 shows that second caller's scalar originates in a broad typed-input decoder, but its meaning is unknown. No direct mapped HitData/ActorValue/protection/armor-skill target appears; the nested target and downstream behavior remain unresolved.

Q79-H61 (same Actor method re-entry through a generation handle) is supported. Q79-H62 (the nested process setter reaches an ActorValue/armor-skill sink) remains proposed. Caller 34 adds no tag-0x0b producer. The inventory now covers 34/62, with 28 remaining. Next inspect caller 35/62 FUN_140658500.

Raw .local/ghidra/gog-query-20261019T160249Z.stdout.raw SHA-256 6c75b43f7f5719f6b4fbe8af899dbd1d0fba9af58f4566193ea7c221f2b2a935.
Raw .local/ghidra/gog-query-20261019T160417Z.stdout.raw SHA-256 89eb0d51e77a284405622803e9d0164bbd19a886e16d35178f391398b5fa5b59; ref-store raw .local/ghidra/gog-query-20261019T161043Z.stdout.raw SHA-256 35e4c4834f8e1f14a43613ee9db3e8acfa3408fc6d741cf40a60a10f988dc900.
Raw .local/ghidra/gog-query-20261019T160533Z.stdout.raw SHA-256 36e2334a9999ecd5e9a49b9a399f637ab788a2795684b601f261656a09fb101d.
Raw wrapper/accessor captures are hash-attested in the evidence ledger EV-0556; Actor slot and scalar captures are EV-0557/EV-0558.

## Caller 35/62 — tag-0x2c spatial water effect

EV-0559 maps FUN_140658500 with one outgoing worker edge, zero indirect sites, and one producer FUN_14051d020. It stores tag 0x2c, a scalar, and three coordinates. The producer calls FUN_14051cdd0/FUN_140525820 directly when the shared gate is clear, or queues tags 0x2c/0x2d when set.

EV-0560 maps FUN_14051cdd0 with 18 direct calls, one indirect site, and four callers. The bounded body selects CWaterSmall/Medium/Large and uses Effects_waterSplash.NIF. It reaches paired handler FUN_140525820 or queues tag 0x2d. EV-0561 maps that paired handler with two direct array-helper calls and no indirect sites; under a global/radius gate it updates two coordinate buffers. Their consumers are unknown; ripple interpretation is contextual inference.

The caller35/handler route is bounded spatial water/effect processing. It contains no direct mapped HitData/ActorValue/protection/armor-skill edge; one virtual effect target and coordinate-buffer consumers remain unresolved. Q79-H63 is supported for the captured static water-effect route. Q79-H1/H2/H3 statuses do not change. The inventory now covers 35/62 callers, with 27 remaining. Next inspect caller 36/62 FUN_140658550.

Raw .local/ghidra/gog-query-20261019T161847Z.stdout.raw SHA-256 4184d7e322b8e30d830b239f4db8a854ca5155820c27d6ff0990dbedafe3b1c9.
Raw .local/ghidra/gog-query-20261019T162014Z.stdout.raw SHA-256 a3940359a33fd1094a6962d834b81fda1084718b9acccb3aeea3a0a9b9eec1ee.
Raw .local/ghidra/gog-query-20261019T162118Z.stdout.raw SHA-256 3872b0f354734619d8bde3fb58a2aeb4bbef1f5c47704d0f83f4cbdff0c920cc.

## Caller 36/62 — tag-0x2d with a separate masked-code producer

EV-0562 maps FUN_140658550: one outgoing edge to FUN_14065b800, zero indirect sites, and three direct producers. FUN_14051cdd0 and FUN_14051d020 are the caller35 water/effect producers; FUN_1407ed990 is a third source. The builder stores tag 0x2d, a scalar, and three float coordinates. Dispatcher case 0x2d returns to FUN_140525820 [EV-0545], whose distance-gated coordinate-buffer writes are bounded in EV-0561.

EV-0563 shows FUN_1407ed990 copying `(param_5+0x2c)&0x7f` into a pooled record and, when `param_1+0x1d4` bit 12 is clear, branching on value 0x0b. The clear thread gate calls FUN_140525820 directly; the set gate calls FUN_140658550. The source object and code meaning are not identified. EV-0564 confirms the shared eligibility predicate also reads the masked code but does not type it as HitData. FUN_1407e25b0 is reached from one analyzed direct caller, FUN_1407cb9d0 [EV-0565]. Its complete 17-edge direct-call census has three indirect sites but no direct call to FUN_1406b9df0, FUN_1406bb690, or FUN_1406bcaa0 [EV-0566].

This supports a second producer family for the same bounded spatial/coordinate event. It does not show that code 0x0b is a HitData flag, an ordinary incoming hit, or a water category. Competing Q79-H64/H65 remain proposed until the input object's type and producer are resolved. H63 remains supported only for the caller35 water/effect source; H1/H2/H3 and H62 do not change. No HitData/ActorValue/effective-protection/armor-skill edge or OBJ-1 edge is added. The inventory now covers 36/62 callers, with 26 remaining. Next inspect caller 37/62 FUN_1406585a0.

Raw .local/ghidra/gog-query-20261019T162340Z.stdout.raw SHA-256 c921059e7db16dbff5aa3d2609d9c0439074952d7c4337b3d34af3e3fa.
Raw .local/ghidra/gog-query-20261019T162445Z.stdout.raw SHA-256 3e3e3b48e90039c1f482e5f2e498ea1afc210498516b50f4ddd3672346ec2d0c.
Raw .local/ghidra/gog-query-20261019T162628Z.stdout.raw SHA-256 4789a20278fe2f44dee3e8a3c0ccb30f46631b2fcfd3f3b5c167dff891ba93ac.
Raw .local/ghidra/gog-query-20261019T162827Z.stdout.raw SHA-256 2140983ec9476bfe12528882ab8bc1a7b88bde4f481a5a375eb9a3917c649b86.
Raw .local/ghidra/gog-query-20261019T162938Z.stdout.raw SHA-256 e7652da40717f502286ff8a00eba3533768d2314189141da7fd9124640d7854d.

## Caller 37/62 — tag-0x2e Actor/process continuation

EV-0567 maps FUN_1406585a0: one outgoing edge to FUN_14065b800, zero indirect sites, and one producer FUN_14068b3a0. It retains the object pointer and stores two bytes with tag 0x2e. Dispatcher case 0x2e calls FUN_14068b3a0 with those fields [EV-0545], supporting deferred same-method re-entry.

EV-0570 gives FUN_14068b3a0 nine direct calls, one indirect +0x4c8 site, and five callsites from four callers including dispatcher FUN_140659160. When the shared gate is clear, it reads process+0x10+0x328 through FUN_1406f1c00, compares that value with Actor+0x260, and may write Actor+0x260 plus a constant through FUN_1406f1be0. EV-0568/0569 show these paired helpers have no direct calls/sites and one observed caller each; they read/write the same unnamed process dword. A player-only branch may resolve TESImageSpaceModifier and reach image-space/sound helpers. The +0x4c8 base Actor slot is the previously mapped masked state predicate FUN_140677100 [EV-0291], but runtime overrides remain unknown.

The captured direct callers include FUN_1406a1830, whose body selects FSTLandHardHeavy/Light and calls the update after a positive computed value, and FUN_140669f70, which contains an NPCHumanDrowning string branch plus a separate path invoking FUN_140668f50 before FUN_14068b3a0 [EV-0570]. EV-0571 shows FUN_140668f50 conditionally sends ActorValue code 0x18 through FUN_1406b49d0; prior GOG mapping identifies Health and shows this helper is also called by the HitData/armor-related handlers [EV-0294], [CL-L128]. Thus some parent contexts are adjacent to Health updates, but this does not turn tag 0x2e into HitData or an armor-skill event. The tag-0x2e routine has no direct mapped HitData/AV11/AV12/protection/armor-skill target. Its +0x4c8 dynamic override, FUN_1408044e0 descendants, untyped process field, and clean Steam behavior remain open. Caller37 adds no tag-0x0b builder; H1/H2/H3 and H64/H65 do not change. The inventory covers 37/62 callers, with 25 remaining. Next inspect caller 38/62 FUN_140658660 after the focused FUN_1408044e0 check.

Raw .local/ghidra/gog-query-20261019T163514Z.stdout.raw SHA-256 042b9277d9375b3a117f6351d73bd85f940dcafe6bc7e53aa5888f28015048f5.
Raw .local/ghidra/gog-query-20261019T163636Z.stdout.raw SHA-256 c7302b2d9e1b8575beee015bd60239d086aa4f6f860ae86f7bd261508a5cd1ea.
Raw .local/ghidra/gog-query-20261019T163729Z.stdout.raw SHA-256 0c1891fe750194e2cf8803433230db097502c662850e77939e93fb7b64f8d2ce.
Raw .local/ghidra/gog-query-20261019T163845Z.stdout.raw SHA-256 a89325db82c8905d365240dc1cb21e2c11ae2af9883561fb8c07ee041b164477.
Raw .local/ghidra/gog-query-20261019T164008Z.stdout.raw SHA-256 6f02698b18392bb15531756ecfda147a2e0ecdc0e1f04b265d2844dcf807e8c9.

### Shared code-0x1d helper argument comparison (EV-0572)

`FUN_1408044e0` has 22 direct calls, three indirect sites, and 12 distinct direct callers. Its tag-0x2e call from `FUN_14068b3a0` uses mode 3/code 0x1d with null source-data and final-pointer arguments and flag 0. The HitData handler `FUN_1406b9df0` calls the same code with a nonnull source-data pointer, flag 1 and a nonnull final pointer at a separate site; it also calls code 0x23 [EV-0572]. Thus the shared helper is a real cross-system edge, while the captured payload forms differ. This narrows but does not eliminate the possibility that one upstream parent of tag 0x2e is hit-adjacent. The helper's dynamic sites and descendants remain open; no direct armor-skill consequence is shown.

### Caller 38/62: tag-0x34 producer and dispatcher (EV-0573/0574)

`FUN_140658660` has one direct edge to `FUN_14065b800`, no indirect sites, and one direct caller `FUN_1406c1d40`. It retains its Actor argument and queues tag `0x34`. The producer uses the shared `FUN_1406d4110` gate: when clear, it directly updates a process-selected vector from Actor coordinates; when set, it submits the same Actor in tag `0x34` [EV-0573]. Worker fallback `FUN_140659160` case `0x34` obtains the Actor-associated process object through `FUN_140664b20`, invokes virtual slots `+0x18` and `+0x38` with Actor coordinates and a constant vector, then clears process-state fields [EV-0574], with the selected nested-object shape independently mapped in EV-0556. The callback targets and broader source ancestry remain unresolved. The exact case has no direct HitData, AV11/AV12, UseSkill, effective-protection or quest-gate edge; unrelated dispatcher cases are not attributed to this path.

### Caller 39/62: tag-0x35 producer and process object update (EV-0575/0576)

`FUN_1406586a0` retains an Actor-associated pointer and optional object, writes tag `0x35`, and queues both. Producers `FUN_1407bc060` and `FUN_1407bc1f0` use the shared thread gate; clear branches call `FUN_140ea04c0(FUN_140664b20(Actor),payload)`, while set branches queue the same pointer tuple [EV-0575]. The second producer builds Actor/process position/state and conditionally supplies an optional pointer. Dispatcher case `0x35` calls the same helper with the two payload values and releases references [EV-0576]. `FUN_140ea04c0` compares the receiver's current object through virtual slot `+0x78`, may dispatch nested old/new object slots `+0x150`/`+0x148`, then tail-calls receiver slot `+0x70`; it has three indirect sites and no direct calls. Concrete types and dynamic targets remain unknown. No direct HitData/AV11/AV12/UseSkill/protection/quest-gate edge is established in this case/helper; unrelated callers and neighboring event cases are not attributed to tag 0x35.

### Caller 40/62: tag-0x2a StartCombat and player-target discriminator (EV-0577/0578/0579)

Competing models before the field trace: (1) `FUN_140766520(player)` returns Actor.Level and the global comparison is a level threshold; (2) it returns another player-associated state value and the comparison is not a level gate. The discriminant was the exact getter dataflow plus the field's producer/consumer use.

The GOG Actor native registrar binds `Actor.StartCombat` to `FUN_1409ec930`. Its queueing branch requires two process-backed Actors and state predicates, then builds tag `0x2a` with two converted handles [EV-0577]. Worker fallback case `0x2a` resolves those handles and enters `FUN_1406e4ba0`/`FUN_14071e250`; the latter has a player-target threshold comparison [EV-0578]. `FUN_140766520` returns Actor+`0x9d8` component `+0x18`, which is used as a bound over a pointer-backed `0xa8`-byte record array and supplied as the array helper's capacity/bound field [EV-0579]. This falsifies the direct Actor.Level model for the getter but does not identify the global or comparison purpose. No quest-start, Story Manager, encounter creation, HitData, AV11/AV12, effective-protection or UseSkill edge is established in the bounded route. This does not validate an OBJ-1 bypass or a Steam-runtime result.

### Caller 41/62: tag-0x5d builder and one producer (EV-0580)

`FUN_140658810` builds tag `0x5d` with a copied 32-bit value and an 8-byte payload, then calls the generic worker. Its only captured producer is `FUN_1409e90c0`, which obtains the 32-bit value through `FUN_140178cf0(param_3)` or a default global and forwards `param_4` [EV-0580]. The API and argument meanings remain unknown. Competing models for the next probe: a generic Actor-associated/state update predicts a bounded helper without a mapped HitData/AV11/AV12/UseSkill sink; a combat/skill continuation predicts a producer-backed path to one of those mapped sinks. Query the exact tag-0x5d dispatcher target `FUN_1406c36e0` before classifying this caller. No P0-A or P0-B edge is established.

### Caller 41/62: tag-0x5d case and collection-state helper (EV-0581)

Worker fallback case `0x5d` resolves the event's 32-bit handle and calls `FUN_1406c36e0(resolved_object, eight_byte_payload)` [EV-0581]. The helper searches the first object's pointer-backed collection for the second object, removes it, updates associated linked-list/fixed-slot/current-object members, invokes state helpers, and releases/compacts the collection. Five functions call the helper directly; two virtual calls remain unresolved. This supports Q79-H75 for the bounded route. Q79-H76 remains proposed because the helper has dynamic calls and shared callers, although no direct mapped HitData/AV11/AV12/UseSkill edge appears in this case/helper. Next identify the exact native registration and producer context of `FUN_1409e90c0`; preserve source/type uncertainty and do not infer a P0-A or armor-XP result.

### Caller 41/62: native registration resolves tag 0x5d (EV-0582)

The GOG Actor native registrar binds `FUN_1409e90c0` to Papyrus `Actor.RemoveSpell`; its wrapper converts one object through `FUN_140178cf0` or a default global, then queues the converted value and second argument under tag `0x5d` [EV-0582], [EV-0580]. The matched case resolves the handle and invokes `FUN_1406c36e0`, whose bounded body removes object membership and updates related slots [EV-0581]. This identifies the bounded operation as the Actor.RemoveSpell native route. It does not establish how unresolved dynamic callbacks alter spell effects, armor protection, AV11/AV12, HitData, or quest state; it also does not establish Steam runtime equivalence.

### Caller 42/62: tag-0x5e Actor.DispelSpell lead (EV-0583)

`FUN_140658850` builds tag `0x5e`; its sole producer `FUN_1409e9120` is registered as Papyrus `Actor.DispelSpell` with `NativeFunction1<class_Actor,bool,class_SpellItem*>` [EV-0583]. The fallback case resolves the Actor handle and calls `FUN_1405c4800(Actor+0xa0, SpellItem, default, 0)`. Competing models for the next probe: Q79-H77 predicts the helper mutates an Actor-associated ActiveEffect/spell runtime collection; Q79-H78 predicts a generic spell/state helper without an ActiveEffect lifetime or damage/XP consequence. Query the exact helper's incoming/outgoing edges and producer-backed structure before classification. This is a cross-system spell-state lead, not evidence of functional armor with zero XP.

### Caller 42/62: FUN_1405c4800 effect-record discriminator (EV-0584)

`FUN_1405c4800` iterates a record list through unresolved receiver vslot `+0x38`, matches candidate+`0x40` against the SpellItem argument, checks candidate+`0x34` when a non-default selector is supplied, and applies additional optional identity filters [EV-0584]. For the tag-0x5e arguments, a matched candidate calls `FUN_1405aed00(candidate,1)` unless receiver bit `+0x10` selects deferred queue helper `FUN_1405c74e0`. The immediate routine sets candidate flag bit `0x40000` at `+0x7c` and conditionally calls `FUN_1405b0730`; another direct caller walks a pointer-backed `0xa8`-stride list and passes its selected records to the same helper [EV-0584]. This supports Q79-H77 as a spell-linked effect-record lifecycle model and falsifies Q79-H78's strict no-lifecycle alternative. The records are not RTTI-confirmed as ActiveEffect, dynamic list provider/queue targets remain open, and no HitData/protection/AV11/AV12/UseSkill/armor-XP link is established. Next query FUN_1405aed00, then resolve the vslot +0x38 provider if needed.

### Caller 42/62 follow-up: FUN_1405aed00 shared handler (EV-0585)

The tag-0x5e `Actor.DispelSpell` path calls `FUN_1405aed00(candidate,1)` after `FUN_1405c4800` finds a matching candidate with bit 18 clear [EV-0584]. `FUN_1405aed00` sets candidate+`0x7c` bit 18 and takes the branch to `FUN_1405b0730(candidate,0)` [EV-0585]. The latter is a multi-branch timing/status handler that reads record and linked-object fields, changes status bits, and may call further virtual/direct helpers; this capture does not identify the record RTTI or prove a terminal removal effect. H77 remains supported as a spell-linked record-state/lifecycle model, while exact ActiveEffect identity remains open. No HitData/protection/AV11/AV12/UseSkill/armor-XP edge is added. Continue at worker caller 43/62 `FUN_140658890` [EV-0585].

### Caller 43/62: FUN_140658890 tag-0x3d indexed state route (EV-0586)

`FUN_140658890` stores tag `0x3d`, retains its object argument, copies the index and two byte flags, and submits the payload to `FUN_14065b800` [EV-0586]. Five xrefs across four producer functions supply different combinations. The fallback case `0x3d` calls `FUN_1406c6ee0(object,index,flag1,flag2)` and releases the retained reference [EV-0574]. `FUN_1406c6ee0` has six direct callees plus unresolved receiver slots `+0x380` and `+0x2e0`; it gates and selects indexed object state before invoking cleanup/update helpers [EV-0586]. One producer references `iMagicEquipped` and conditionally calls receiver slot `+0x688`, but its dynamic type and gameplay meaning are not established. H79 supports the bounded state route; H80's direct mapped hit/protection/ActorValue/UseSkill sink prediction is falsified for this exact helper. This is not a tag-0x0b producer, and Q79-H1/H2 remain open with 19 callers left. No OBJ-2 causal edge is added. Next inspect caller 44/62 `FUN_1406588e0`.

### Caller 44/62: FUN_1406588e0 tag-0x3f queue/direct convergence (EV-0587)

Caller `FUN_1406588e0` builds tag `0x3f` with four values derived from its sole producer `FUN_1405d3900`; the producer calls `FUN_1405d4bf0` directly when the shared gate is clear and queues the matching fields when set [EV-0587]. Worker fallback case 0x3f calls `FUN_1405d3680`, which forwards those four values to the same `FUN_1405d4bf0` helper in the same order [EV-0574], [EV-0587]. The shared helper has three direct callees plus four indirect sites, including unresolved slots `+0x378` and `+0x380`; its bounded body performs form/global checks and nested object traversal/update work. No direct mapped HitData/effective-armor/AV11/AV12/UseSkill sink appears. H81 is supported and H82 is falsified for the captured direct/deferred alternatives; nested type and virtual behavior remain open. Eighteen original callers remain; continue at caller 45/62 `FUN_140658950`.

### Caller 45/62 target: tag-0x40 scalar/state update (EV-0588)

The worker's tag-0x40 case reaches `FUN_14040e300(object, payload, flag)` [EV-0574]. Its GOG 1.6.1179.0 call-edge census finds three direct callees and no indirect sites. The handler clears/reinitializes state, stores or clears the payload according to the flag, calls `FUN_14040e420`, reads a shared scalar using `FUN_140635730`, updates two scalar fields and a bitfield, and has a direct helper path that casts form ID `0x167` to `TESImageSpace` [EV-0588]. No direct mapped HitData/effective-protection/AV11/AV12/UseSkill sink appears. Payload RTTI, form provenance, descendant behavior and runtime role remain unknown. Q79-H1/H2/H3 are unchanged; caller 46/62 remains next.

### Caller 45/62 producer decode path (EV-0589)

The tag-0x40 producer `FUN_140357c70` initializes output locals, invokes shared typed-value decoder `FUN_14033e470`, returns false if decoding fails, and otherwise passes the returned object plus a nonzero test of the second output into `FUN_140658950` [EV-0587], [EV-0589]. The decoder walks descriptor-selected values from a byte stream and has RTTI-checked conversions to `SpellItem`, `MagicItem`, and `EffectSetting`; it has 613 call xrefs across 64 caller functions and four unresolved indirect sites [EV-0589]. The exact type selector, stream source and output object's RTTI remain unknown. The wrapper body contains no direct Actor/HitData field read, but this does not rule out gameplay data in its input. No mapped direct HitData/protection/AV11/AV12/UseSkill edge is added; caller 46/62 is next.

### Caller 45/62 data-registration census (EV-0590)

`FUN_140357c70` has two direct outgoing calls (typed decoder `FUN_14033e470` and builder `FUN_140658950`), no indirect sites, no analyzed direct callers, and one data xref at RVA `0x362ffb4` [EV-0590]. Its containing table and descriptor semantics are not resolved by the captured context. Inspect that data location once; if it remains opaque, continue caller 46/62. No gameplay or OBJ-1/OBJ-2 meaning is assigned.

### Caller 45/62 xref metadata comparison (EV-0591)

The apparent producer data-table reference is reclassified as likely Windows x64 exception metadata. Its adjacent values are `0x357c70`, `0x357ce7`, and `0x1c70fcc`; the same three-field pattern appears for known handler `FUN_14040e300` as `0x40e300`, `0x40e3a5`, and `0x1c91ba8` [EV-0588], [EV-0591]. Microsoft documents `RUNTIME_FUNCTION` as image-relative function start, function end, and unwind-info DWORDs stored in sorted `.pdata`. The address-only Ghidra query had no function or code xrefs there. This strongly supports unwind metadata, not a gameplay registration; the exact PE section was not separately enumerated. The producer's decoder descriptor remains unknown. H85 is supported and H86 falsified for this xref only; continue caller 46/62.

### Caller 46/62: FUN_1406589f0 tag-0x43 sampled convergence (EV-0592)

Caller `FUN_1406589f0` creates tag `0x43` with an object plus dword and increments the object refcount at `+0x28`; seven direct producer functions reach it [EV-0592]. The sampled `FUN_1407bacf0` calls `FUN_1406d4110`; gate true submits `(object,1)` through the worker builder, while gate false calls `FUN_14069e070(object,1)` directly. Existing worker evidence maps case `0x43` to `FUN_14069e070(object,payload_dword)` [EV-0574]. This supports direct/deferred helper convergence for that producer, not all seven. Inspect the shared helper and the remaining producer families; no direct armor/HitData edge is established by the builder.

### Caller 46/62: tag-0x43 complete producer and helper trace (EV-0593)

All seven producer bodies preserve object plus selector 0–6 across the gate-set worker path (`FUN_1406589f0`) and gate-clear direct path (`FUN_14069e070`); `FUN_1407baef0` also performs a separate earlier action [EV-0593]. The shared handler compares the selector to the three-bit value at object `+0xc8`, updates bitfield mask `0x1c0000`, and runs component/reference/state helpers. Its direct census has 12 call instructions, eight unique targets and three unresolved indirect sites. Direct helpers `FUN_1406bc0c0`/`FUN_1406bc100` are not the mapped HitData/AV11/AV12/UseSkill targets; `FUN_140717d10` and virtual consumers remain open [EV-0593]. H91 is supported/H92 falsified for all seven captured producer branches; H89 is falsified/H90 supported for the direct helper body only. No runtime object identity or full transitive negative is claimed.

### Caller 46/62 descendant check: FUN_140717d10 (EV-0594)

The descendant `FUN_140717d10` has one direct callee and no indirect sites. It checks a byte against nested `+0x332`, clears `+0x2f8` and `+0x332`, and conditionally calls `FUN_1406671b0`; that helper may update parent `+0x108` and submit builder `FUN_140657870` [EV-0594]. No mapped HitData/effective-protection/AV11/AV12/UseSkill target appears in these inspected bodies. Identify the secondary builder's tag once, then continue caller 47/62; object types and runtime effects remain unknown.

### Caller 46 secondary event: tag 0x0A builder FUN_140657870 (EV-0595)

The builder `FUN_140657870` writes tag `0x0A` with a handle-like value and scalar/vector/byte payload, then submits it to the generic worker. Existing dispatcher case 10 resolves the handle, may apply a vector update, changes object state, resolves a second handle, and calls an unresolved recipient vtable slot `+0x870` [EV-0595]. No direct mapped HitData/protection/AV11/AV12/UseSkill call appears in the bounded bodies. The receiver RTTI and virtual target remain open; continue caller 47/62 after resolving the strongest available type/slot discriminator.

### Tag-0x0A caller-type discriminator (EV-0596)

The builder has three direct callers. `FUN_140665950` invokes virtual byte offset `+0x4c8` on `param_1` and then passes that same object to the builder; EV-0291 maps that byte offset to primary `VTABLE::Actor` slot `0x99` [EV-0596], [EV-0291]. This supports Actor-vtable compatibility for that exact route, but not exact RTTI for all callers. Resolve the Actor vtable slot `0x10e` corresponding to dispatcher byte offset `+0x870`; then continue caller 47/62.

### Matching GOG Actor vtable base for tag-0x0A slot resolution (EV-0597)

The matching GOG 1.6.1179.0 Address Library maps `VTABLE::Actor` array entry 0 (AE ID 207511) to RVA `0x189EC20` [EV-0597]. The deprecated legacy map lacks runtime provenance and is not used. Next read slot index `0x10e` (byte offset `+0x870`) from this exact GOG vtable and screen the target/callees; do not transfer this RVA to Steam.

### Tag-0x0A Actor callback target (EV-0598)

Primary GOG `VTABLE::Actor` slot `0x10e` (`+0x870`) maps to `FUN_140699500` / RVA `0x699500` under RTTI `.?AVActor@@` [EV-0598]. Its body has Actor/process state and cleanup work, but the slot query did not request a complete call-edge census. Next enumerate its direct callees and screen mapped HitData/protection/AV11/AV12/UseSkill sinks before continuing caller 47/62.

### FUN_140699500 direct-call screen and shared-helper discriminator (EV-0599)

The complete direct-call census finds 195 edges and 45 unresolved indirect sites. No exact direct call reaches mapped `FUN_1406bb690`, `FUN_1406bcaa0`, `FUN_1407ddf50`, or `FUN_1406bbb80`. A process-conditioned branch calls `FUN_1406be430` with Actor/process-derived values and pointer `Actor+0x54`, then calls unresolved Actor vtable byte offset `+0x50` [EV-0599]. The same helper occurs in the earlier candidate hit/damage route [EV-0429], but no shared HitData or XP behavior is established. Query all direct callers and descendants of `FUN_1406be430` to test the competing models; preserve the 45 unresolved virtual sites as open.

### Shared vector helper separates tag-0x0A state from candidate HitData arguments (EV-0600)

`FUN_1406be430` has five direct callees and one indirect ActorValueOwner-like getter. It transforms vector inputs, reads numeric ActorValue `0x24`, and passes a computed vector to a nested physics-like sink `FUN_1403fd6b0` [EV-0600]. The tag-0x0A Actor callback passes process-derived scalar/vector data, Actor `+0x54`, and null final context; `FUN_1406b9df0` supplies fields copied from a HitData-shaped record. No direct AV11/AV12/UseSkill sink occurs in the helper. This narrows away direct HitData argument equivalence while leaving high-level effects unknown. Resolve Actor slot `+0x50` called immediately after the helper, then continue caller 47/62.

### Actor slot +0x50 manager dispatch following tag-0x0A vector helper (EV-0601)

The follow-up Actor slot `0xA` / byte offset `+0x50` maps to `FUN_1401dfdc0`; if global `DAT_14317bfc0` exists it delegates Actor and selector arguments to `FUN_140606580` [EV-0601]. Resolve that bounded manager/helper before closing caller 46; no P0 sink is established yet.

### Caller 46/62 bounded closure: tag-0x0A vector and keyed-state path (EV-0602)

The secondary tag-0x0A path reaches primary Actor slot `+0x870` (`FUN_140699500`), which has a process-conditioned vector helper branch (`FUN_1406be430`) and then Actor slot `+0x50` (`FUN_1401dfdc0`). The manager continuation checks TLS/global/Actor flags and updates a manager-owned keyed record with `Actor+0x14` and a selector bit [EV-0595]–[EV-0602]. The shared vector helper reads numeric ActorValue `0x24` and reaches a vector/physics-like sink, but the tag-0x0A caller's inputs differ from the HitData-shaped caller, and no direct AV11/AV12/UseSkill or mapped protection sink appears. This closes caller 46 only as a bounded static Actor/process vector/state route; one Actor slot `+0x160`, generic update descendants, the 45 other vtable sites on FUN_140699500, runtime effects, and GOG/Steam equivalence remain unresolved. Continue caller 47/62 `FUN_140658a30`. No OBJ-1/OBJ-2 causal edge is added.

### Caller 47/62: tag-0x44 gated producer and self-reentry (EV-0603)

`FUN_140658a30` writes tag `0x44`, a dword and a byte. Its sole producer `FUN_1401fa010` queues this payload under `FUN_1406d4110`; dispatcher case `0x44` re-enters the same producer. On the clear-gate path, the producer may acquire an object and call `FUN_1401fdb80` on its `+0x170` member [EV-0603]. No tag `0x0B` or direct mapped HitData/AV11/AV12/UseSkill edge appears. Identify the object helper, then continue caller 48/62.

### Caller 47/62: collection cleanup helper narrows tag-0x44 route (EV-0604)

`FUN_1401fdb80` searches a pointer array at `param_1+0x128` for `param_2`. A match is removed by `FUN_1401fe380`; otherwise object vtable `+0x148` supplies a key to `FUN_140d1ed80`. Its second caller reaches it from a float/time comparison, passing a component and parent [EV-0604]. This favors generic membership cleanup/keyed lookup over combat work but leaves virtual and lookup descendants open. Identify the acquired object and trace `FUN_140d1ed80`; then continue caller 48/62.

### Caller 47/62: manager-array fallback bounds tag-0x44 state route (EV-0605)

`FUN_140d1ed80` has four callers and one direct array-removal helper. For object key `-1`, it searches a manager-owned refcounted array by pointer identity, clears fields `+0x30/+0x38`, and removes the slot through `FUN_140d20780`; other keys use unresolved manager vtable `+0x1c8` [EV-0605]. This supports a generic registry/state path but leaves the virtual branch and downstream effects open. Next inspect tag-0x44 object factories and their producer callers, then continue caller 48/62.

### Caller 47/62: keyed factory shares a registry with BGSDecalNode cleanup (EV-0606)

`FUN_1404a27f0` looks up a global-array object by field +0x28, returns a retained reference, and removes the entry. Its other two callers are Ghidra-labeled BGSDecalNode cleanup bodies that perform the same keyed lookup on child entries [EV-0606]. This supports a scene/decal registry association for the tag-0x44 route, but exact result type and alternate factory remain open. Next inspect `FUN_1404a28a0`, then continue caller 48/62.

### Caller 47/62: parallel registry factory and shared array erase helper (EV-0607)

The alternate factory `FUN_1404a28a0` scans a second global array by field +0x28 and removes a matching entry through the same `FUN_1401fe280` helper as the first factory [EV-0606], [EV-0607]. Its sole caller is the tag-0x44 producer. Ghidra's producer decomp omits arguments at the call despite the callee prototype; inspect producer instructions before interpreting key parity. No mapped hit/armor-skill edge occurs in the factory. Next query producer callsite registers, then continue caller 48/62.

### Caller 47/62: tag-0x44 object callback and factory arguments resolved (EV-0608)

Producer disassembly shows both factory branches receive the same output pointer and key, correcting the omitted-argument decompilation. `FUN_1401fa3d0` filters child entries by unresolved virtual `+0x10` identity and owner pointer, then calls the producer with child `+0x28`/+0x54 values; `FUN_1401fbd10` drains a dword list into the same producer. The global keyed arrays are also used by BGSDecalNode-labeled cleanup callers [EV-0606]–[EV-0608]. Caller 47 is bounded as generic object-list lifecycle work with unresolved virtual cleanup, no direct tag-0x0B/HitData/armor-skill edge, and no global negative. Continue caller 48/62.

### Caller 48/62: tag-0x45 byte builder and gated producer (EV-0609)

The original listed RVA `0x658a80` falls inside `FUN_140658a60`, which writes tag `0x45` plus a byte. Its sole caller `FUN_140774b80` uses `FUN_1406d4110` to choose an immediate call to `FUN_1401fa100(manager,1)` or a queued call through the builder; case `0x45` routes back to `FUN_1401fa100` with the payload byte [EV-0609]. The deferred byte argument is omitted by decompilation and remains unresolved. No direct HitData/armor-skill target occurs in these captured bodies. Query FUN_1401fa100 and resolve the producer register path next.

### Caller 48/62: tag-0x45 target is flag-dependent manager-list cleanup (EV-0610)

`FUN_1401fa100` clears manager child lists in flag-0 mode; in nonzero mode it removes/compacts entries, calls `FUN_1401fdab0`, conditionally reaches `FUN_1414a33c0`, and invokes unresolved child vtable `+0x1c0` [EV-0610]. The immediate tag-0x45 caller passes 1, while the dispatcher forwards the byte payload. No direct HitData/AV11/AV12/UseSkill route occurs in the captured body. Query producer register arguments before closing caller 48.

### Caller 48/62 closure: tag-0x45 selector parity and manager cleanup (EV-0611)

Producer instructions set `RDX=1` before the thread-state gate. The direct branch calls `FUN_1401fa100(manager,1)`; the queued branch calls tag-0x45 builder `FUN_140658a60(manager)` with the byte still in `RDX`, and dispatcher case 0x45 forwards it back [EV-0608], [EV-0609], [EV-0611]. Immediate and deferred paths therefore converge on the same flag-1 manager-list cleanup. No direct mapped HitData/armor-skill edge occurs; two finalizer sites remain unresolved, so this is a bounded local result only. Continue caller 49/62.

### Caller 49/62: tag-0x48 refcounted object-pair and list case (EV-0612)

The requested RVA `0x658af0` lies inside builder `FUN_140658ac0`, which queues tag `0x48` with a retained object pointer and second pointer-sized value. No incoming direct caller is analyzed; one data xref at RVA `0x3657848` remains unclassified. Case 0x48 obtains a list through object+`0x38` vslot `+0x10`, iterates entries and calls `FUN_14054e390` [EV-0612], [EV-0608]. Trace that helper and classify the xref before closure; no direct HitData/armor-skill sink appears in the bounded builder/case.

### Tag-0x48 list helper FUN_14054e390 (EV-0613)

The helper invokes each non-null entry object's virtual slot `+0x20` with a context pointer, sets context byte `+8`, and returns 1. It has four callers, including `FUN_140659160`'s tag-0x48 list loop. The exact callback contract is unresolved; no direct mapped armor-skill sink appears. Inspect caller 49's data xref RVA `0x3657848` next [EV-0613].

### Caller 49/62 data-xref classification and bounded closure (EV-0614)

The sole source-less DATA xref at RVA `0x3657848` points to `FUN_140658ac0`. Its neighboring DWORDs `0x658ac0`, `0x658afe`, and `0x1d4f8f0` match the x64 `RUNTIME_FUNCTION` begin/end/unwind-info layout, as documented and independently matched against a known GOG handler in EV-0591. The address-only query found no function or instructions there. This strongly supports compiler unwind metadata rather than application registration; the exact PE section remains unverified [EV-0614]. Caller 49 is closed as a bounded generic tag-0x48 list-callback route [EV-0612–EV-0614]. No OBJ-1/OBJ-2 causal edge or global negative is added. Continue caller 50/62 `FUN_140658b10`.

### Caller 50/62: tag-0x49 retained-object list/update route (EV-0615)

`FUN_140658b10` queues tag `0x49` with a retained object. Its sole producer `FUN_1407bbb90` has process/object-conditioned branches and two list callback helpers, then chooses an unresolved immediate vtable `+0x1a8` call or a deferred tag-0x49 event plus `FUN_140657c30`. Case 0x49 independently obtains an object list and visits entries with `FUN_14054e340` [EV-0615]. Object type and callbacks remain unresolved; compare the producer's direct/incoming call graph and callback targets before interpreting the route.

### Caller 50/62 producer graph and candidate vtable discriminator (EV-0616)

`FUN_1407bbb90` has 11 direct edges, 7 unresolved indirect sites, and no analyzed direct code caller. Its direct calls do not include mapped HitData/protection/AV11/AV12/UseSkill targets. An xref at RVA `0x18bb248` sits among consecutive qwords that decode as code addresses, with the producer at the second qword; treat RVA `0x18bb240` as a candidate vtable base only. Query its MSVC RTTI identity before assigning a class or reading virtual slots. The immediate `+0x1a8` call, list callbacks and `FUN_140657c30` continuation remain unresolved [EV-0616].

### Caller 50/62 producer RTTI identity (EV-0617)

The candidate table base RVA `0x18bb240` validates with an MSVC Complete Object Locator and type descriptor `.?AVAddRagdollHandler@@`, subobject offset zero. EV-0616's qword at `0x18bb248` is the function pointer to `FUN_1407bbb90`, making it zero-based slot 1 in the primary vtable [EV-0617]. This identifies class membership, not the producer's method name, argument type, trigger or armor/HitData/skill effect. Next trace the queued continuation `FUN_140657c30`.

### Caller 50/62 immediate and deferred slot +0x1a8 comparison (EV-0618)

The AddRagdollHandler slot-1 method invokes vtable `+0x1a8` directly when the gate is clear. When set, it queues tag `0x49` and builds a tag-`0x12` object-pair/dword event with `FUN_140657c30`; dispatcher case 0x12 invokes the same receiver slot with matching visible object, constants and selector fields. The decompiled last argument is ambiguous, so inspect its machine instructions before claiming exact parity. The virtual target remains unknown [EV-0618].

### Caller 50/62 disassembly corrects immediate/deferred argument parity (EV-0619)

The immediate AddRagdollHandler call sets `R8D=1`, `R9B=1`, selector in stack dword `[RSP+0x20]`, and zero in stack byte `[RSP+0x28]`. Case 0x12 instead loads `R8D` from the event selector byte at payload+0x18 and does not set matching R9/stack arguments in its block. Both use the same receiver/object pointer roles and vtable slot `+0x1a8`, but exact argument parity is falsified. `FUN_14065b800` is the sole direct caller of the dispatcher; inspect its callsite to bound inherited context before interpreting the mismatch [EV-0619].

### Worker wrapper context for tag-0x12 virtual call (EV-0620)

`FUN_14065b800`'s only direct call to dispatcher `FUN_140659160` moves the event pointer into `RCX` and sets no `RDX/R8/R9` or stack arguments at the callsite. Thus the tag-0x12 case's extra virtual-call values are not proven event payload fields, and they cannot restore parity with the producer's explicit immediate setup [EV-0620]. The target signature and terminal behavior remain unknown. Next query shared callback `FUN_14054e340`.

### Caller 50/62 tag-0x49 any-match list callback (EV-0621)

`FUN_14054e340` visits non-null list entries through virtual slot `+0x10` while the context byte is false; a true predicate sets the byte and stops later checks. This is a generic any-match helper with six callers, including tag-0x49 producer/dispatcher and prior actor/process routine `FUN_140699500` [EV-0621]. Shared helper reuse is an engine-level connection only; element type and predicate meaning remain unknown. Trace sibling `FUN_14054e3c0` next.

### Caller 50/62 first list pass and sibling callback (EV-0622)

`FUN_14054e3c0` invokes element virtual slot `+0x28` for each non-null entry, sets a seen-entry byte, and returns 1. Its two callers are the AddRagdollHandler producer and `FUN_140713d90`. Caller 50 runs this pass before its distinct +0x10 any-match pass [EV-0621–EV-0622]. Element type and callback effect remain unresolved. Next trace the returned object `FUN_1402b8b60` used as receiver for unresolved `+0x1a8`.

### Caller 50/62 virtual receiver resolver (EV-0623)

Caller 50 passes `param+0x60` to `FUN_1402b8b60`. A bit at that subobject's `+0x40` selects an owned-object lookup through `FUN_1401699e0(subobject+0x48)`; otherwise the resolver returns global `DAT_1420f9d28`. That object receives the unresolved `+0x1a8` call and is retained in tag 0x12 for deferred dispatch [EV-0623]. Trace the owned-object lookup and global type before slot interpretation.

### Caller 50/62 optional-object holder lookup (EV-0624)

`FUN_140179080(holder,key)` uses a bitmap gate, a thread-local holder/key cache, and a linked-list scan comparing each entry's virtual `+0x8` result with the requested key. A match returns the entry; `FUN_1401699e0` requests key 1 and extracts its `+0x10` object with reference-count handling [EV-0623–EV-0624]. This is shared keyed-holder infrastructure; it does not identify caller 50's concrete receiver or virtual `+0x1a8` target. Inspect the global fallback `DAT_1420f9d28` next.

### Caller 50/62 global fallback storage (EV-0625)

At static image load, `DAT_1420f9d28` and the next three qwords are zero. The exact fallback cell has 47 direct reads and two writes in analyzed code: `FUN_1402c65b0` stores `RDI`; `FUN_1402c6720` stores zero [EV-0625]. The fallback is runtime-populated, but its assigned object class and caller-50 slot `+0x1a8` target remain unresolved. Trace both writer functions and their incoming callers to recover RDI provenance and the set/clear lifecycle.

### Caller 50/62 global fallback setter provenance (EV-0626)

`FUN_1402c65b0` obtains an 8-byte holder, constructs a local three-dword input from `DAT_1432740d8`, `+4` and `+8`, passes it to `FUN_1402c6810`, stores the holder in global `DAT_1420f9d28`, then places the helper result in `*holder` and retains it when nonnull. Its sole analyzed direct caller `FUN_140221790` calls the setter when its second argument is nonzero [EV-0626]. Trace `FUN_1402c6810` and the zeroing path to identify the fallback object; the global resolver returns the holder's first qword [EV-0623].

### Caller 50/62 fallback receiver class (EV-0627)

The fallback setter passes `0` into `FUN_1402c6810`, selecting its `FUN_140ebdf30` branch. The helper calls common `FUN_140e84cf0` initialization and installs the GOG symbol-labeled `bhkWorldM::vftable`; the other branch installs `bhkWorld::vftable` [EV-0626–EV-0627]. Since `FUN_1402b8b60` returns the first qword in the holder, the caller-50 fallback receiver is bhkWorldM when no optional key-1 object is present [EV-0623], [EV-0627]. Find its vtable address and query zero-based slot `0x35` (+`0x1a8`) before interpreting the method.

### Caller 50/62 bhkWorldM vtable address (EV-0628)

Constructor `FUN_140ebdf30` stores `0x1419e9078` into the object vptr, giving GOG RVA `0x19e9078` [EV-0628]. Use the RTTI query on this table and read zero-based slot `0x35` for caller 50's `+0x1a8` method; do not transfer the RVA to Steam AE.

### Caller 50/62 fallback receiver RTTI (EV-0629)

The table at GOG RVA `0x19e9078` is primary MSVC RTTI type `.?AVbhkWorldM@@`, signature 1, subobject offset zero [EV-0629]. The constructor-symbol inference is now independently confirmed. Read vtable slot `0x35` (+`0x1a8`) next.

### Caller 50/62 bhkWorldM slot +0x1a8 target (EV-0630)

The primary bhkWorldM vtable's slot `0x35` (+`0x1a8`) resolves to `FUN_140e884d0`. The method returns false for a null object. If its sixth argument is zero, it calls `FUN_140e0f510(object)` and requires bit 1 of byte at `result+0x18`; otherwise it bypasses that eligibility check. A passing path sets receiver byte `+0xc5f8` and packages optional callbacks through `FUN_140e898f0` [EV-0630]. AddRagdollHandler immediate call passes zero, while the deferred event's inherited sixth argument remains unknown [EV-0619], [EV-0620]. Test the dispatcher call context to distinguish bypass from ordinary rejection; no direct HitData/armor-skill edge appears in this target.

### Caller 50/62 correction: case-0x12 argument parity (EV-0631)

The earlier disassembly at RVA `0x65939c` was a valid virtual call, but the full dispatcher and a new address-only query identify it as case `0x4`, not case `0x12`. The actual tag-0x12 virtual call is at `0x659c92` [EV-0631].

The immediate producer passes `(receiver, object, 1, 1, uVar13, 0)`. The tag-0x12 builder stores the same receiver/object roles and `uVar13` at payload `+0x18`. Case 0x12 sets `R8D=1`, `R9B=1`, copies payload `+0x18` to stack argument five, and writes zero to stack argument six. Thus all six argument positions match. `FUN_14065b800` still forwards only the event pointer; the dispatcher consumes the event payload and forms the virtual call itself [EV-0615], [EV-0616], [EV-0618], [EV-0620], [EV-0631].

This falsifies the proposed nonzero-`param6` bypass of the `FUN_140e884d0` object-state gate for this static GOG path [EV-0630], [EV-0631]. The exact runtime receiver, optional callback execution, hit/protection effects and armor-skill XP remain unobserved; no OBJ-2 causal edge is added. Caller 50 is bounded for the worker-caller census. Continue with caller 51/62 `FUN_140658b50`.

### Caller 51/62: tag-0x4b PlayerCharacter state route (EV-0632)

`FUN_140658b50` builds tag `0x4b` with a byte from its sole producer `FUN_140738380`. In the queued branch the shared thread gate sends that byte; dispatcher case `0x4b` invokes `FUN_140738380(DAT_143188918, byte)`. The global is a verified PlayerCharacter object [EV-0344].

The producer's clear-gate path selects two objects through PlayerCharacter slot `+0x378` with selectors 1 and 0. For a nonzero byte it checks primary PlayerCharacter slot `+0x4c8` (`FUN_140677100`): RTTI identifies the vtable as `.?AVPlayerCharacter@@`, and the method tests masked field `+0xc8`. It compares and changes bit 0 at the selected objects' `+0xf4`, changes PlayerCharacter byte `+0xbe3`, builds paired state records, iterates four objects at PlayerCharacter `+0x1a8`, and calls resource/hierarchy helpers including `FUN_140661f60` [EV-0632].

The exact producer body has 12 direct call edges and 10 dynamic virtual sites; 13 direct caller functions are recorded. Recursive helper `FUN_1402df6d0` has three direct callees, two virtual sites and a recursive edge. It traverses nested keyed objects, checks a record bit and updates object state through `FUN_140e2bd10`. Neither bounded direct body has a mapped HitData/protection/AV11/AV12/UseSkill sink [EV-0632].

Cross-caller synthesis: caller 50 and caller 51 both pass `DAT_1432740d8..+8` to distinct helpers, respectively `FUN_1402c6810` and `FUN_140cb4ae0` [EV-0626], [EV-0632]. The tuple schema and shared-helper relationship are open; this adds no HitData or armor edge. Caller 51 is bounded for the worker census, with dynamic callbacks unresolved. Next query `FUN_140cb4ae0`, then continue caller 52/62 `FUN_140658be0`.

### Cross-caller synthesis: shared tuple consumers (EV-0633)

Caller 51 reaches `FUN_140cb4ae0` through `FUN_140cb41c0`; that helper copies all three dwords at its supplied tuple pointer into event-record fields and queues the record through `FUN_140cbc770`. Caller 50 independently copies `DAT_1432740d8`, `+4`, and `+8` into a factory input for `FUN_1402c6810`; its false/fallback branch sends the first two dwords through `FUN_140e854e0` and sets the third to zero [EV-0626], [EV-0632], [EV-0633].

The direct consumers and field transformations differ, falsifying the proposed shared direct registration/update primitive. The tuple's values and semantic names remain unknown; the address query finds 1,349 xrefs to the first dword but provides no initialized scalar values. This shared-storage observation adds no HitData, armor protection, AV11/AV12, UseSkill, armor-XP, or quest-gate edge. Resume caller 52/62 `FUN_140658be0`.

### Caller 52/62: tag-0x56 retained-object collection route (EV-0634)

`FUN_140658be0` stores tag `0x56` and a retained object. Its only analyzed direct producer, `FUN_140778a20`, tests `FUN_1406d4110`: the queued branch calls the builder, while the clear-gate branch invokes receiver slot `+0x138` immediately. Dispatcher case 0x56 calls `FUN_140777f40(DAT_1420f7db0, object)` and then the same slot on the same receiver [EV-0634]. Thus the deferred route has one additional manager action but matches the immediate virtual call's receiver/slot and has no explicit arguments.

The producer wrapper is called twice by `FUN_140774b80`, which walks pointer collection `+0xe8`, invokes the wrapper for each member, decrements references and clears the collection. Its only analyzed caller is `FUN_140643ec0`, a broad cleanup sequence. The manager helper branches on object virtual slots `+0x160`/`+0x180` and searches or updates keyed collections at `+0x108`, `+0x128`, or `+0xe8`. Treat the outer cleanup interpretation as inference; the exact RTTI and `+0x138` target remain unknown [EV-0634].

No mapped HitData/protection/AV11/AV12/UseSkill target occurs in the captured tag-specific direct path. The unresolved virtual target keeps this bounded; no global negative, armor-XP bypass, or Steam behavior follows. Continue caller 53/62 `FUN_140658c10`.

### Caller 53/62: Actor slot-0x89 tag-0x50 process-state route (EV-0635)

`FUN_140658c10` queues tag `0x50` and retains the object. Its producer `FUN_140664cf0` is primary `VTABLE::Actor` slot 0x89 (`+0x448`); it filters one global and flag bit 11, then queues the object [EV-0400], [EV-0635]. Case 0x50 dispatches through thunk `FUN_140664d20` to `FUN_1402ec610` [EV-0635].

The handler's entry guard skips its body when receiver flag bit 11 is set or the receiver is verified PlayerCharacter [EV-0344], [EV-0635]. Its remaining direct code handles Actor/process and object-state updates, with 51 direct call edges and 17 unresolved virtual sites. No mapped HitData, protection, AV11/AV12 or UseSkill direct target appears in the bounded body. Caller 53 is closed as a bounded Actor-state path; dynamic descendants and Steam behavior remain open. No causal OBJ-2 edge is added. Continue caller 54/62 `FUN_140658c50`.

### Caller 54/62: tag-0x54 spatial/context update (EV-0636)

The producer selects tag 0x54 under process/grid predicates and dispatches to FUN_1402eb6f0, whose full direct census has 63 edges and 21 unresolved virtual sites. Its gated tag-0x32 route and immediate branch converge on Actor slot +0x328/FUN_140666770; this callback reuses the TLS/nested selector FUN_1402e55a0 and recursive object-tree helper FUN_140e88c50 [EV-0636]. Those helpers also appear in the HitData receiver and tag-0x3C route [EV-0295], [EV-0296], [EV-0483]–[EV-0486], [EV-0512]. Treat this as exact code reuse only. No same-pointer or armor/HitData causal edge is established. Caller 54 is closed as a bounded route; caller 55/62 is FUN_140658c90.

### Caller 55/62: gated numeric tag-0x57 registry notification (EV-0637)

Caller 55 FUN_140658c90 writes tag 0x57 with a supplied 32-bit code. Its sole producer FUN_14075a430 checks a category/value/limit predicate; caller FUN_14074b720 supplies categories 0x18–0x1A, threshold globals, codes 0xFC–0xFE, and separate state bits at +0xbe4 [EV-0637]. This does not prove a threshold crossing or identify the literal categories.

The dispatcher passes the code to FUN_140971910, whose complete direct census has six edges and no indirect sites; its bounded body performs numeric-list lookup and gated registry initialization [EV-0637]. No direct mapped combat/armor sink or causal OBJ-2 edge is established. Caller 55 is bounded; continue caller 56/62 FUN_140658cc0.

### Caller 56/62: PlayerCharacter tag-0x58 perk-rank cleanup (EV-0638)

Caller 56 FUN_140658cc0 writes tag 0x58 with an object and mode byte. Its two nonnull-gated producers pass modes 0 and 1; dispatcher case 0x58 supplies the PlayerCharacter singleton to FUN_14074b350 [EV-0344], [EV-0637], [EV-0638]. The handler edits two object collections and conditionally calls FUN_140750f70.

The cleanup helper's stack visitor has verified RTTI BGSPerk::FindPerkInRanksVisitor, and its method matches a candidate by pointer before removing the associated rank entry [EV-0638]. PlayerCharacter slot +0x650 remains dynamic; the base Actor entry is empty but does not establish the runtime override. The bounded route shows no direct HitData/protection/AV11/AV12/UseSkill sink, no perk grant or level-gate change, and no causal OBJ-1/OBJ-2 edge. Continue caller 57/62 FUN_140658d00.

### Caller 57/62: tag-0x5F perk-rank addition (EV-0639)

Caller 57 writes tag 0x5F with an object-derived dword, another object pointer, and two bytes. Its sole analyzed producer FUN_140750d80 scans PlayerCharacter+0x4b8 with a Ghidra-labeled AddPerkVisitor, defaults rank 0 to current rank+1, bounds the request by perk+0x52, stores the rank pair, and emits the worker event [EV-0639]. Dispatcher case 0x5F resolves a handle and calls FUN_1403906c0 with both rank bytes [EV-0637], [EV-0639].

FUN_1403906c0 invokes per-rank slots +0x58/+0x50 and has two unresolved indirect sites. Wrapper FUN_14074b150/FUN_14074b220 have no analyzed incoming direct callers; the six-entry pointer region at RVA 0x18AD540 has no identified table-base references and invalid RTTI. The bounded path shows a perk rank-count bound, not a Player-level gate. It does not establish level-one access or a vanilla bypass, and no mapped HitData/protection/AV11/AV12/UseSkill sink appears. Continue caller 58/62 FUN_140658dd0.

### Caller 58/62: tag-0x5A spatial-state route (EV-0640)

Caller 58 writes tag 0x5A with a dword and boolean. Dispatcher case 0x5A resolves the object handle and calls FUN_1405259c0 on a manager; its true branch uses PlayerCharacter and object coordinates to create/update a keyed record, while false/null cases clean up state. The target has five direct calls and 13 unresolved virtual sites [EV-0637], [EV-0640].

Producer FUN_140686320 is verified as primary Actor slot 0x9C and emits the tag under object/process/float-threshold predicates. Its only analyzed direct caller FUN_140731e80 compares a float with geometry-derived state. Producer FUN_14051df20 removes keyed entries; one caller processes hkpAllCdBodyPairTempCollector collision pairs [EV-0640]. The bounded route shows no Player-level check or mapped direct HitData/protection/AV11/AV12/UseSkill sink. No OBJ-1/OBJ-2 causal edge is added. Continue caller 59/62 FUN_140658e10.

### Caller 59/62: tag-0x5B disarm-related Actor action (EV-0641)

Caller 59 writes tag 0x5B with two dwords. Its producer queues them when a resolved object's +0xCC bit 13 is set, then invokes `FUN_1405aed00(param_1,0)`. Dispatcher case 0x5B resolves both payloads and calls `FUN_14067aea0`; its successful PlayerCharacter branch emits “You have been disarmed.” and calls primary Actor slot +0x658/FUN_14067a400 [EV-0400], [EV-0641]. That Actor method has 25 direct calls and 16 unresolved virtual sites. The producer's immediate helper instead updates bit `0x40000` and may call `FUN_1405b0730(param_1,0)`; direct convergence is not shown. The bounded captures show no explicit level check or direct mapped HitData/protection/AV11/AV12/UseSkill sink. No OBJ-1/OBJ-2 causal edge is added. Continue caller 60/62 FUN_140658e50.

### Caller 60/62: tag-0x5C HitData-derived serialized helper route (EV-0642)

Caller 60's sole producer is mapped HitData handler `FUN_1406b9df0`. It builds tag 0x5C after cloning its handler argument with `FUN_1407dce10`; dispatcher case 0x5C resolves the cloned context's object identifier and calls `FUN_1406be2c0`. The target conditionally calls `FUN_1406be430`, the exact helper called directly on the producer's alternate predicate branch [EV-0295], [EV-0296], [EV-0431], [EV-0642]. This supports a HitData-derived direct/deferred shared-helper relationship, not identical runtime arguments or ordinary enemy-hit coverage. `FUN_1406be430` queries numeric ActorValue 0x24 and reaches a vector/physics-like sink, with no direct AV11/AV12/UseSkill target [EV-0600]. Effective protection, armor XP and dynamic descendants remain unmeasured; no OBJ-1/OBJ-2 causal edge is added. Continue caller 61/62 FUN_140658f70.

### Caller 61/62: tag-0x61 eye-texture update (EV-0643)

Caller 61 writes tag 0x61, retains its object argument, and stores a supplied second payload. Its sole producer reports failures for missing TextureSet, 3D, eye-tagged headparts, or geometry; success queues the resolved eye geometry with the supplied TextureSet. Dispatcher case 0x61 checks two object-type identity pointers, conditionally replaces a nested +0x78 texture pointer, then calls a nested virtual callback and three geometry/resource helpers [EV-0643]. The bounded path shows no explicit level/quest predicate or direct HitData/protection/AV11/AV12/UseSkill edge. No OBJ-1/OBJ-2 causal edge is added. Continue final caller 62/62 FUN_140658fb0.

### Caller 62/62: tag-0x62 shared Actor handler (EV-0644)

Caller 62 `FUN_140658fb0` writes tag 0x62; its sole analyzed producer is `FUN_1406c72d0`, and dispatcher case 0x62 calls `FUN_1406bc400`. That target's three direct callers include the mapped HitData handler `FUN_1406b9df0`; it conditionally calls `FUN_140672640`, whose captured body checks Actor/PlayerCharacter state and related Actor entries. These facts establish shared code identity, not matching event origin or arguments [EV-0644], [EV-0295], [EV-0296]. The bounded bodies show no explicit level/quest gate or mapped effective-protection/AV11/AV12/UseSkill sink; 13 and five indirect sites and runtime behavior remain open. No OBJ-1/OBJ-2 causal edge is added. The 95-function census contains an exact partition of 33 previously decompiled plus 62 remaining bodies; caller 62 is the final body. Verify the preserved partition, close Q-0079, then begin Q-0080; Steam matched-hit/protection/raw-AVSK evidence remains required [EV-0397], [EV-0423], [EV-0260].
