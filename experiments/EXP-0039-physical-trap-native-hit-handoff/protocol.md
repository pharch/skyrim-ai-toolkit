# EXP-0039 protocol

## Source identity

- Installed Steam AE executable ProductVersion 1.6.1170.0 is separately verified in EV-0109. No full active order or selected MO2 profile is configured.
- The native caller investigation uses only the existing GOG Skyrim AE 1.6.1179.0 Ghidra project and matching executable hash `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. Do not transfer GOG RVAs to Steam.
- The captured `Skyrim.esm` and `Skyrim - Misc.bsa` hashes and sizes are recorded in EV-0292. No profile winner is inferred from the base installation.

## Competing-model discriminants

1. **Completed in EV-0293:** Resolve the Papyrus native registration for `ObjectReference.ProcessTrapHit` against the exact GOG binary and follow build-attested registration, vtable and direct-callee edges. The player route reaches common HitData construction and then a separate actor-hit handler.
2. **Completed bounded callback/health screen (EV-0295), Actor/PlayerCharacter slot screen (EV-0296), and ActorMagicCaster method screen (EV-0297):** A full direct-call census found no outgoing edge from `FUN_1406b9df0` to `FUN_1406bcaa0`; its visible `UseSkill` site uses AV15. The runtime-initialized ActorValue callback table maps AV11/AV12 to `FUN_1406b65c0`, which dispatches Actor slot `0xCA`; the selected PlayerCharacter target updates fields/container state without a visible skill award. The Health AV24 callback and selected `HandleHealthDamage` descendants also show no AV11/AV12 award. The remaining typed receiver slots `0x99`, `0x5C`, and `0x70` map to state predicates, an ActorMagicCaster object-provider, and a state lookup; the PlayerCharacter `0x70` override adds a slot-`0x71` flag predicate. The first ActorMagicCaster methods update fields/list state and compute a scalar; their selected bodies show no armor award or resolver return. Other indirect receiver objects and nested subtype calls remain unresolved; trace them only when their concrete types offer a route to armor credit or `FUN_1406bcaa0`.
3. On the installed Steam target, a later live experiment must verify a valid trap impact, positive HitData/damage, armor mitigation with qualifying armor worn, selected `UseSkill` AV/points, raw AVSK deltas and protection. Use miss, block, zero-damage and unequipped-armor controls to reject false positives.
4. Keep exact profile/order, disposable-save, and read-only Observer requirements explicit. Static script flow does not prove a live hit, protection, skill award or exploit. No GOG RVA transfers to Steam.

## Bounded record and script route

1. Read official-master ACTI records with the direct TES4 parser and preserve their source file hashes; do not claim winner resolution.
2. Extract only exact PEX names from the tested `Skyrim - Misc.bsa` route. Record archive hash, PEX offsets, sizes and hashes; inspect with the bounded classic PEX 3.2 disassembler.
3. Compare the Papyrus call with local `ObjectReference.psc` only as a native declaration; the PSC does not disclose the native implementation.

## Current exclusions

The current lane is offline WSL/Linux source analysis. No game was launched, no save or plugin was modified, no profile-specific order was read, and no live observer data was collected.
