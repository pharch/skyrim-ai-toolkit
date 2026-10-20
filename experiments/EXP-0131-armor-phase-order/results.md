# Results

## Hit builder and receiver order — EV-0670

The identity-checked GOG capture places the physical-damage snapshot before AV39/armor-factor mitigation of `totalDamage`. The builder wrappers return into the resolver path whose unblocked player-receiver branch scans worn ARMO and routes eligible armor to AV11/AV12 in `FUN_1406bcaa0`; the later call to `FUN_1406b9df0` follows that award path. This corrects the earlier frontier endpoint: `FUN_1406b9df0` is not the direct pre-award AV11/AV12 selector [EV-0670], [EV-0222], [EV-0261].

## Synchronous selector visitor — EV-0671

`FUN_1407ddf50` invokes `FUN_140386070` for selector values 0x25 and 0x27. The visitor walks the selected Actor entrypoint list synchronously through PlayerCharacter slot 0x100. Each entry callback reads its function ID and data, then dispatches to the function table. Selector metadata and function IDs are different fields. No event queue or player-input yield appears in the bounded visitor body. Its typed callback predicates and all runtime subclasses are not globally excluded.

## Function handlers and official record screen — EV-0672, EV-0675, EV-0676

The official five-master screen parsed 523 PERK records and 785 entrypoint DATA rows. It found 13 selector-37 rows and 10 selector-39 rows. Selector 37 rows use EPFT function ID 1; selector 39 rows use IDs 1 or 2. Raw EPFD payloads are preserved. Duplicate records remain file-level rows; this is not active-order or winner resolution [EV-0675].

In the captured GOG handler table, function ID 1 reaches `FUN_140386340` and ID 2 reaches `FUN_1403863b0`. Their bounded bodies perform a SetValue write or AddValue float update to the entrypoint result, respectively. Each has a typed function-data virtual predicate at vtable +8. No direct equipment mutation, event enqueue, player action, or yield is visible in those bounded handler bodies [EV-0672]. CommonLib's mutable generated documentation labels selector 37/39 as `kModTargetDamageResistance`/`kModPercentBlocked` and operation IDs 1/2 as `kSetValue`/`kAddValue`; these are labels only, not the source of binary behavior [EV-0676].

The first parser attempt incorrectly treated the `PRKE` entry header as selector/function data. The corrected screen uses `DATA[0]` for the selector and `EPFT` for the operation; only that corrected capture is used in the counts and interpretation [EV-0675].

## Comparator and remaining gaps — EV-0673, EV-0674

`FUN_1406b9df0` is retained as a distinct HandleHealthDamage/ProcessTrapHit comparator, with 28 unresolved indirect sites; its post-resolver call does not make it the ordinary player-receiver AV11/AV12 award selector [EV-0673]. PlayerCharacter vtable slot 0xF7 points to `FUN_140739050`, consistent with the earlier UseSkill mapping. The attacker-side call is separate from the player-receiver armor award after the worn-ARMO scan [EV-0674], [EV-0221], [EV-0222].

## Bounded conclusion

The exact GOG 1.6.1179.0 path and official five-master PERK rows provide no identified player-accessible equipment interposition between armor mitigation and the AV11/AV12 selector. H1 is rejected for this captured source scope; H2 is supported as the bounded synchronous path. This does not exclude side effects in the unresolved function-data virtual predicate, third-party/Creation Club records, Steam-specific differences, or runtime-only behavior. H3 remains an ordinary blocked-hit control route at the branch level, not proof of bounty-qualifying effective protection.

There is still no measured positive armor protection, raw Heavy/Light AVSK result, verified hit sample, or vanilla reproduction. EV-0260 remains the exact Steam experiment dependency: verified target and complete order, disposable level-one save, read-only event/protection/AVSK measurement, controls, and repetition. Q82 closes only this bounded static question.
