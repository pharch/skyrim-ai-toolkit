# EXP-0044 — ProcessTrapHit armor mitigation and armor XP

**Status:** Bounded static route result recorded in EV-0302. GOG AE 1.6.1179.0 is the analysis build; Steam AE 1.6.1170.0 remains the separate runtime target. The next investigation continues through unresolved receiver indirections and then the clean level-one Steam discriminator.

**Question:** Can a vanilla physical trap preserve effective worn-armor protection while omitting Light/Heavy Armor skill credit on a level-one player?

**Prior evidence:** EV-0292–EV-0295 establish the configured trap-to-`ProcessTrapHit` handoff, the GOG native binding and common HitData construction, a distinct post-resolver handler, and bounded callback/receiver branches without a mapped AV11/AV12 award. Their unresolved indirect calls and lack of live damage/protection/AVSK measurements remain material.

**Current result:** EV-0302 shows that the trap and normal hit builders both call `FUN_1407ddf50`, which snapshots `physicalDamage` before applying AV39/`GetArmorBaseFactorSum` mitigation to `totalDamage`. The trap route calls the shared handler directly, bypassing the known normal resolver's AV11/AV12 award branch. Ten indirect sites in the shared mitigation helper and 28 in the receiver handler remain unresolved; positive player protection and raw AVSK deltas are unknown.

See [competing models](hypothesis.md), [predicted discriminants](expected-discriminants.md), and [protocol](protocol.md).
