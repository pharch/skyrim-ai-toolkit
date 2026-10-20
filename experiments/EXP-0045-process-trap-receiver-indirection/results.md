# Results

## Starting evidence

EV-0295 identifies AV15 Sneak in the visible receiver `UseSkill` branch and maps selected AV11/AV12 callbacks without an award. EV-0302 reports 28 unresolved indirect sites in `FUN_1406b9df0` and 10 in the shared mitigation helper. These are prior bounded findings; no EXP-0045 callsite has yet been resolved.

## New result

EV-0303 records a fresh GOG `TESObjectREFR` vtable mapping and queries for slots `0x8E`, `0x8F`, and `0x51`, plus a fresh query of the ActorCause handle-validation helper.

- HitData `sourceRef` is at `+0x20`; the trap payload carries its reference handle into that field through the captured ProcessTrapHit builder path [EV-0261], [EV-0293], [EV-0302].
- Slot `0x8E` is `AsExplosion`; its matching GOG base target is a two-instruction zero return. Slot `0x8F` is `AsProjectile`; its base target is also a two-instruction zero return. These are type tests on the source reference, not AV11/AV12 awards.
- Slot `0x51` is `GetActorCause`. Its mapped target returns source-reference cause data through one helper. The selected downstream `FUN_14043ab60` body validates a handle/form-table entry and has no calls or indirect sites.
- Across all 28 sites, the typed groups are 13 refcount-release-style calls, seven previously mapped Actor state/caster calls, one AV15 Sneak `UseSkill`, three ActorValueOwner Health/Stamina operations, and these four source-reference calls. No mapped site shows an AV11/AV12 award or direct return to the normal resolver.

This is a bounded GOG static classification. The thirteen cleanup targets, every possible derived source-reference override, Steam behavior, effective worn-armor protection, raw AVSK change, and a level-one vanilla reproduction remain open.

## EV-0315 follow-up

A fresh identity-checked census of `FUN_1406b9df0` repeats the 28-site result. The first temporary handle comes from receiver `param_1` through generic `FUN_1402ef8f0`/`FUN_140179540` conversion and resolution; a second comes from HitData `+0x18`. The HitData `+0x20` sourceRef is resolved independently. `FUN_140179540` is a shared handle-table resolver and `FUN_1402ef8f0` is a shared handle converter, so neither identifies the concrete cleanup classes [EV-0315].

No new AV11/AV12 skill-progress sink was found in the mapped receiver groups. The result does not prove zero armor XP: concrete cleanup targets, all derived sourceRef overrides, Steam dispatch, positive effective protection, and raw AVSK remain unresolved. The exact live discriminator remains repeated positive-damage trap hits with functional worn armor and before/after raw Light/Heavy AVSK on a verified Steam 1.6.1170.0 setup [EV-0260], [EV-0315].
