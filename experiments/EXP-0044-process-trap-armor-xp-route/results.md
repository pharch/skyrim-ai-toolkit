# Results

## Bounded GOG static result — EV-0302

- **Shared mitigation:** The physical-trap `FUN_1407dd110` and normal builders `FUN_1407dd220`/`FUN_1407dd5b0` reach `FUN_1407ddf50`. The helper snapshots HitData `totalDamage` (`+0x50`) into `physicalDamage` (`+0x54`), reads AV39 through ActorValueOwner, calls Actor vtable slot `0xE7` (`GetArmorBaseFactorSum`), then applies the resulting factor to `totalDamage` before blocked-hit bookkeeping. This is source order, not a measured positive PlayerCharacter protection value.
- **Known award branch:** The normal `FUN_1406bcaa0` resolver contains the player AV11/AV12 award branch before it calls the shared receiver handler. The `ProcessTrapHit` wrapper calls `FUN_1407dd110` then `FUN_1406b9df0` directly, without a direct call to `FUN_1406bcaa0`.
- **Unresolved scope:** `FUN_1407ddf50` has 10 unresolved indirect callsites; `FUN_1406b9df0` has 28. EV-0295 maps the visible handler `UseSkill` call to AV15 Sneak and traces selected AV11/AV12 callbacks without an award, but does not resolve all descendants.

## Hypothesis status

The shared armor-related mitigation path and bypass of the known resolver award branch are supported for the GOG static call path. The full no-AV11/AV12 claim remains open because indirect dispatch is incomplete. No positive live trap damage, effective worn-armor protection, unchanged raw AVSK, Steam mapping, or level-one vanilla reproduction is established.

## Next discriminator

Q-0042 resolves the 28 remaining receiver indirections for any hidden AV11/AV12 award path. After that bounded native trace, a separate exact-Steam clean-save comparison must measure positive unblocked trap damage with functional armor against a control while preserving raw Light/Heavy Armor AVSK.
