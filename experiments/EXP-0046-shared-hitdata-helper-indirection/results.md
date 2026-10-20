# Results

## Starting evidence

EV-0302 records that GOG `FUN_1407ddf50` snapshots HitData `totalDamage` (`+0x50`) to `physicalDamage` (`+0x54`), obtains AV39 via ActorValueOwner, calls Actor slot `0xE7` (`GetArmorBaseFactorSum`), and reduces `totalDamage` before blocked-hit bookkeeping. The same capture enumerates ten unresolved indirect callsites.

The EV-0302 raw disassembly shows three reference-count release calls, three explicit ActorValueOwner getter calls with indices `0x42`, `0x09`, and `0xA3`, one dynamic ActorValueOwner getter whose index comes from an associated object's `+0x194` field, an Actor slot-`0xE7` call, an associated-object `+0xC0` slot-`0x4` call, and an Actor `+0xA0` slot-`0x4` call. These are GOG RVAs from the 1.6.1179.0 analysis build.

## Fresh query results — EV-0304

The complete ten-site classification and raw source identities are in EV-0304 and its private capture manifest. All addresses below are GOG 1.6.1179.0 only.

- `0x1407de113` loads an ActorValue index from weapon `+0x194`, reads that value from the HitData target actor, and conditionally reduces `totalDamage` when the weapon pointer and index are valid. This establishes an additional record-selected damage input in weapon-bearing helper use; the actual installed weapon indices and values were not screened, and this input is not identified with AV39.
- `0x1407de2fc` dispatches weapon `GetAttackDamage`; the returned base-form field, together with AV66 ShieldPerks and AV9 Block, enters `FUN_140418290` and is stored in `percentBlocked` (`+0x5c`).
- `0x1407de472` reads AV163 ReflectDamage and contributes to HitData `criticalDamageMult` (`+0x7c`) under the bounded local condition.
- `0x1407de518` dispatches MagicTarget slot 4 (`IsInvulnerable`). Its matching-GOG base target is a false-returning stub. A true return conditionally clears `totalDamage`, `targetedLimbDamage`, `resistedPhysicalDamage`, `resistedTypedDamage`, and `stagger`, but not the prior `physicalDamage` snapshot. Actor/PlayerCharacter secondary-vtable dispatch remains inferred from pinned headers rather than independently enumerated.
- `0x1407de049` remains the already mapped Actor slot `0xE7` (`GetArmorBaseFactorSum`) input; `0x1407de331` and `0x1407de34a` are the AV66/AV9 reads above. The three remaining sites at `0x1407de43e`, `0x1407de554`, and `0x1407de579` are reference-count cleanup dispatches.

The common HitData initializer zeros the `weapon` field. The captured `ProcessTrapHit` builder does not write it before or after calling the shared helper; therefore the two optional weapon branches (`0x1407de113` and `0x1407de2fc`) are skipped on that captured trap construction route. The trap route still uses AV39/slot `0xE7` and reaches the later invulnerability gate.

H1 is supported and H2 is falsified for the general weapon-bearing helper route. No additional armor-rating factor beyond AV39/slot `0xE7` is established, and the optional weapon input is not present on the captured ProcessTrapHit route. No runtime protection, armor AVSK, Steam equivalence, profile winner, or level-one reproduction is established.
