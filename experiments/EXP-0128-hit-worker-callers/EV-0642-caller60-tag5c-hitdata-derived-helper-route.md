# EV-0642 — Caller 60/tag-0x5C HitData-derived serialized helper route

## Competing models and discriminants

- H1, HitData-derived serialized branch: `FUN_1406b9df0` selects caller 60/tag 0x5C from a mapped HitData handler, clones its second argument with `FUN_1407dce10`, and the dispatcher returns the cloned context to `FUN_1406be2c0`, which calls shared helper `FUN_1406be430`. It predicts the producer edge, copied handler fields, tag-0x5C case, and common helper identity.
- H2, unrelated Actor/process update: the tag may use worker infrastructure but is produced elsewhere or changes only unrelated actor state. It predicts no producer edge from the mapped HitData handler or copy of its event context.
- H3, armor protection or armor-XP operation: the serialized helper directly changes effective protection or routes to AV11/AV12/UseSkill while retaining protection. It predicts a mapped sink/field in the bounded helper chain, or a clean Steam matched-hit observation; helper reuse alone is insufficient.

## Direct GOG evidence

Captures use the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Metadata confirms read-only execution, disabled auto-analysis, and matching executable identity. This project is separate from Steam AE 1.6.1170.0; no GOG RVA is transferred to Steam.

- Caller 60 `FUN_140658e50` writes tag 0x5C, allocates an event/context object, calls `FUN_1407dce10(local_res10,param_2)` to clone the producer's second argument, derives a byte flag through a virtual `+0x478` call, and queues through `FUN_14065b800`. Its sole analyzed direct producer is `FUN_1406b9df0`, the mapped HitData handler [EV-0295], [EV-0296], [EV-0642].
- In `FUN_1406b9df0`, after Actor/process and HitData-field predicates, a branch where `FUN_140667430(param_1)` is nonzero calls caller 60/tag 0x5C. The alternate zero branch directly calls `FUN_1406be430`; the queued route later reaches that same exact function through `FUN_1406be2c0`. The common callee identity is established, but receiver and argument identity/equivalence are not [EV-0642].
- Dispatcher case 0x5C reads the cloned context's object identifier at `+0x18`, resolves it, and calls `FUN_1406be2c0(resolved_object,context,flag)`. The target has three direct call edges and three unresolved indirect sites. Under its captured object/context predicates it copies vector fields and calls `FUN_1406be430` [EV-0642].
- Existing EV-0431 maps `FUN_1407dce10` as copying handler fields at offsets 0x50, 0x54, 0x5C, and 0x80 consumed by `FUN_1406b9df0`; caller 60 invokes this helper on the same handler argument [EV-0431], [EV-0642]. This supports a HitData-derived serialized context, not proof that every field has the same runtime object identity.
- Existing EV-0600 maps `FUN_1406be430` as vector transformation with a numeric ActorValue query at receiver `+0xB8` using value `0x24`, then a vector/physics-like sink `FUN_1403fd6b0`; the helper has no direct AV11/AV12/UseSkill sink [EV-0600]. The caller-60 route adds no direct protection or armor-skill sink in the captured dispatcher/target bodies [EV-0642].

## Result and limits

H1 is supported: caller 60 is a HitData-derived worker branch and its dispatcher target rejoins the same helper used on the alternate direct branch of `FUN_1406b9df0`. H2 is contradicted for producer origin, though worker transport and shared helpers still serve other systems. H3 is not supported by the bounded direct call chain; effective protection, armor XP, runtime AV award, the exact meaning of ActorValue 0x24, and descendants of three unresolved virtual sites remain open. The tag is 0x5C, not the tag-0xB constructor sought by the wider caller census. This does not establish ordinary enemy-hit coverage, a level-one bypass, an armor-XP result, Steam behavior, or bounty resolution. Record the supported HitData/helper edge; add no OBJ-1/OBJ-2 causal edge.

## Next action

Continue caller 61/62, `FUN_140658f70`; preserve caller 62/62 and the independent clean Steam matched-hit/effective-protection/raw-AVSK test.
