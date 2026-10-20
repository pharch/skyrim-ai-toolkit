# EXP-0012 results

## Source declarations and address mapping

- CommonLib declares `Actor::UseSkill` at virtual slot `0xF7`, `Actor::HandleHealthDamage` at `0x104`, `HitData::totalDamage` at `+0x50` and `HitData::physicalDamage` at `+0x54` (EV-0217). It maps Heavy Armor to AV11 and Light Armor to AV12 (EV-0218).
- Fresh GOG Address Library data maps `VTABLE::PlayerCharacter` ID 208040 to RVA `0x18ACD70` for the attested 1.6.1179 executable (EV-0219). The base Actor slot 0xF7 is a one-instruction RET default (EV-0220).
- PlayerCharacter's concrete slot 0xF7 target is `FUN_140739050`; it passes only when points are strictly positive, then calls `FUN_14077d090`, whose observed body updates skill progress for AV IDs 6–23. The generic Ghidra wrapper lacks a direct incoming xref for this virtual target; identity, slot, outgoing call, disassembly and decompilation checks pass (EV-0221).

## Hit-resolution control flow

- `FUN_1406bcaa0` at RVA `0x6BCAA0` consumes a local hit-data structure populated by helper `FUN_1407dd220` and reaches two actor skill-use branches (EV-0222, EV-0223).
- The attacker-side call at `0x1406bcd72` occurs before the receiver identity check. The strictly-positive comparison at `0x1406bcce6` has a JBE target at `0x1406bcd78`, where the receiver is compared with the global player. This means that non-positive `[RSP+0xA0]` skips the attacker-side call but proceeds into the player-receiver branch when its identity matches. The older EV-0036 paragraph that lists this comparison as a receiver prerequisite misattributes that branch.
- For an unblocked player receiver, the function scans worn entries for non-null ARMO forms, excludes subtype `+0x1BC == 2`, requires positive base armor rating at `+0x200`, counts the Heavy/Light categories, selects AV11 or AV12, and dispatches at `0x1406bcf00`. The points value is loaded from `[RSP+0xA4]`. The receiver branch contains no direct test of `[RSP+0xA0]` before this call.
- For a blocked player receiver, the function routes to AV9 and uses the difference of the physical/total damage fields; this branch skips AV11/AV12. The positive-points PlayerCharacter guard can reject the selected skill call, but no runtime points or XP result was measured.
- The armor selection scan tests base item DNAM; it does not by itself show measured effective armor mitigation. The helper query is bounded and does not establish all damage normalization.
- EV-0261 extends the builder trace: it snapshots `totalDamage` into `physicalDamage`, reads AV39 through virtual `GetActorValue`, combines that value with `GetArmorBaseFactorSum`, and applies the factor to `totalDamage` before setting the blocked flag. The following captured helpers do not rewrite those two damage fields; receiver routing follows population. The call site does not directly use `GetClampedActorValue`, but the concrete `GetActorValue` implementation is unresolved.

## Assessment and limits

H1 is supported for source order: the GOG hit builder computes AV39/armor-base-factor mitigation into HitData before the blocked/unblocked receiver award branch. H2, interpreted as a separate/deferred award event, is falsified for this GOG path. This does not show that any player-reachable vanilla candidate keeps effective protection while yielding zero Heavy/Light XP; effective mitigation, Block XP, raw armor XP and level preservation were not measured. The unresolved virtual `GetActorValue` implementation also leaves negative AV39 survival unknown. No Steam 1.6.1170 call-path claim is made.

The `[RSP+0xA0]` versus `[RSP+0xA4]` correction is recorded in C-OBJ2-ARMOR-GATE. Next, highest information gain is Q-0015: trace vanilla-reachable negative AV39 writers against the now-mapped Block points formula; keep Q-0004 and Q-0018 open for a protection/control measurement.
