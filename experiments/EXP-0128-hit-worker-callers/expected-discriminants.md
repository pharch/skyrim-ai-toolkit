# Expected discriminants

| Observation | H1 | H2 | H3 |
|---|---|---|---|
| Exact 62 remaining worker callers | A caller constructs/selects tag 0xB and reaches the dispatcher with an Actor/event payload | All inspected callers use other tags or do not select the tag-0xB route | Tag 0xB is constructed, but its source/conditions point to a non-hit or secondary event |
| Route to resolver | Payload reaches `FUN_140659160` case 0xB -> `FUN_1406bb690` -> `FUN_1406bcaa0` | No new path beyond EV-0397's bounded routes | Same static path as H1, but ordinary player-hit semantics remain absent |
| Practical armor result | Still needs a clean Steam hit with measured protection and AV11/AV12/AVSK | Still unresolved | Still unresolved |

No outcome from these GOG static queries can substitute for the matched Steam hit protocol in EV-0260.

| Caller 34 tag 0x21 | H61 predicts generation-handle resolution returns the source Actor and virtual +0x6c8 re-enters the same Actor method; H62 predicts a nested +0x190/slot+0x8 descendant reaches ActorValue/HitData/UseSkill. | H61 is supported for the primary Actor table; H62 still requires producer-backed nested type and sink evidence. |

| Caller 35 tags 0x2c/0x2d | H63 predicts spatial water/effect handlers; a competing model predicts a combat/armor sink through direct or indirect descendants. | Water-size/splash setup and coordinate-buffer updates support the bounded effect model; one virtual site and array consumers remain unresolved. |

EV-0562–EV-0566 discriminant: resolve the runtime type and producer of the object field `(param_5+0x2c)&0x7f` copied by FUN_1407ed990. A writer or caller that identifies a HitData/collision source supports Q79-H64 for a hit-adjacent spatial effect; a non-hit source supports Q79-H65. Neither outcome establishes armor skill XP. The upstream wrapper's three indirect targets, FUN_1407ed990's four indirect targets, the coordinate-buffer consumers, and clean Steam matched-hit/AVSK telemetry remain separate open checks.

EV-0567–EV-0571 discriminant: follow FUN_1408044e0, the remaining direct helper selected by a tag-0x2e byte, and resolve the process field at *( *(process+0x10)+0x328 ) only from producer-backed type evidence. A mapped HitData/AV11/AV12/UseSkill descendant supports Q79-H67; a bounded Actor/process or visual target supports H66 for this route. Preserve the hard-landing/drowning contexts, dynamic +0x4c8 override, and the clean Steam positive-hit/protection/raw-AVSK requirement.

EV-0572 discriminant: tag 0x2e and HitData both call FUN_1408044e0 with code 0x1d, but their source-data/final-pointer arguments and flag differ. Resolve the three dynamic sites only if producer-backed evidence can show the tag-0x2e null-data path reaches a HitData/AV11/AV12/UseSkill sink; otherwise retain H66 for the bounded state/effect route and H67 only as an upstream-source possibility.

EV-0573/0574 caller 38 discriminant: trace case-0x34 virtual slots +0x18/+0x38 against the exact process-selected object class and compare the producer's clear-gate route. H69 predicts vector/state continuation; H70 requires a source-backed HitData/AV11/AV12/UseSkill edge. Do not infer from unrelated cases in FUN_140659160.

EV-0575/0576 caller 39 discriminant: resolve the type and target for FUN_140ea04c0 receiver slots +0x78/+0x70 and nested slots +0x148/+0x150 from the object returned by FUN_140664b20. H71 predicts a process object update/replacement; H72 requires a source-backed HitData/AV11/AV12/UseSkill edge. Keep case 0x37 and other shared-helper callers separate.

EV-0577/0578/0579 caller 40 discriminants: the direct Actor.Level model predicts that `FUN_140766520` returns a known player-level field; the competing component-state model predicts a producer-backed array bound or other non-level value. The captured field is the Actor+`0x9d8` component's `+0x18`, consumed as a bound over `0xa8`-byte records. To identify the threshold semantics, resolve writers/readers of that exact component field and identify `DAT_141ffda78` from an identity-checked GOG query. Do not infer a DA quest start from `Actor.StartCombat`.

EV-0580 caller 41 discriminants: follow worker case `0x5d` to `FUN_1406c36e0` and trace the payload plus the sole producer `FUN_1409e90c0`. A state/property path supports Q79-H75; a producer-backed edge into mapped HitData, AV11/AV12, or UseSkill supports Q79-H76. Keep the native registration name and the 32-bit converter's semantics unknown until their exact registry/source evidence is captured.

EV-0583 caller 42 helper discriminant: query `FUN_1405c4800` from the tag-0x5e path. Q79-H77 requires source-backed ActiveEffect record/array or lifetime operations on the Actor+`0xa0` receiver; Q79-H78 predicts a generic spell/state update without those edges. Preserve all direct callers, virtual targets and argument fields; do not infer protection or XP from the native name `DispelSpell` alone.

EV-0584 bounded result: SpellItem matching plus candidate flag/deactivation handling supports an effect-record lifecycle operation; the candidate class is not RTTI-confirmed. Resolve `FUN_1405aed00` direct/incoming descendants and the concrete list provider for receiver slot `+0x38`. A producer-backed target into damage/protection/AV11/AV12/UseSkill is required before adding a P0-B edge.

EV-0585 bounds caller 42's transition to candidate bit-18 marking plus a shared status/timing handler; class and terminal effect remain unknown. Resume the primary census at `FUN_140658890` (caller 43/62), test its payload and producer against tag 0x0B and mapped HitData/AV11/AV12/UseSkill routes, and preserve no-edge results where direct evidence is absent.

EV-0586 resolves caller 43 as tag 0x3d and its fallback target as an indexed state/update helper with unresolved virtuals; no direct mapped hit/armor-skill sink appears. Resume the original census at caller 44/62 FUN_1406588e0 to test Q79-H1/H2/H3 and preserve the clean Steam matched-hit/protection/raw-AVSK discriminator.

EV-0587 establishes that tag 0x3f's queued wrapper and the producer's immediate branch converge on FUN_1405d4bf0 with the same four fields. Its direct body uses unresolved object virtuals and nested cleanup/state helpers, with no mapped HitData/protection/AV11/AV12/UseSkill sink. Resume caller 45/62 FUN_140658950 and keep Q79-H1/H2 open.
