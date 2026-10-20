# Results

EV-0324 confirms the bounded route comparison: ProcessTrapHit uses shared HitData construction/resistance then calls FUN_1406b9df0 directly. The known FUN_1406bcaa0 wrapper contains the visible AV11/AV12 armor or AV9 Block branch before reaching the same handler. One visible UseSkill call in the handler carries AV15 Sneak. The handler retains 28 unresolved indirect sites.

No zero armor XP, positive final damage, effective protection, Steam equivalence, profile winner, or vanilla reproduction is established. The next static discriminator is targeted mapping of unresolved descendants with potential AV11/AV12 or UseSkill routes.

## Follow-up receiver and cleanup trace — EV-0325

Fresh exact-context captures confirm the ActorValueOwner calls at 0x6BA492 (base Health read) and 0x6BA952 (Stamina damage restoration), matching the earlier EXP-0045 classification. The PlayerCharacter cleanup body FUN_14072fd60 has 108 direct edges and 8 indirect sites; the census contains no direct slot-0x7B8 skill dispatch. The unresolved indirect calls and transitive descendants remain open. These findings narrow the static path but do not establish zero XP, positive final damage, effective protection, Steam behavior, or vanilla reproduction [EV-0325].
