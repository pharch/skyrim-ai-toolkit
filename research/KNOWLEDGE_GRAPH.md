# Mechanisms and Causal Graph

The source snapshot proposes these legacy links. Edges are imported as hypotheses or reported dependencies; shared terminology alone does not establish causality. Source revision is unavailable, and evidence IDs point to hashed historical reports.

```text
M-0001 -> G-0001 -> Q-0001 / speech-family breadth
M-0002 -> G-0003 -> reachable independent ActorValue writers
M-0003 -> G-0002 -> C-LEG-0001 / C-LEG-0004
M-0004 -> G-0002 -> mixed payload and delivery tests
M-0005 -> G-0004 -> functional cleanup test
M-0006 -> G-0001 / G-0007 / no-caster hazard boundary
M-0007 -> G-0006 -> craft publication/interposition question
M-0008 -> G-0005 -> player-created useful hazard question
M-0001 -> speech result-family matrix and Intimidate quest-state candidate [EV-0068, EV-0069]
M-0002 -> corrected Recover cleanup operand and observed +0x94 slot delta [EV-0057]
M-0003/M-0004 -> poison-reference inventory, recipe/XP model, null-key AV148 writer, and CC script-writer limits [EV-0056, EV-0059–EV-0064, EV-0082, EV-0083]
M-0005 -> frozen-deadload user report; direct spell membership, favorites slot, and MGR21 perk save/revert are separate branches [EV-0075–EV-0078]
M-0006 -> scroll/spell skill-use route and historical MGEF multiplier scans [EV-0072, EV-0073, EV-0086]
M-0007 -> fixed COBJ outputs, furniture skill gate, condition functions, and Staff Enchanter handle lead [EV-0065–EV-0067, EV-0084, EV-0085]
M-0012 -> finite potion native cleanup and transformation boundary [EV-0058, EV-0079]
M-0013 -> self-poison inventory ownership and transfer limits [EV-0062, EV-0063]
M-0014 -> Enchanting cap reads base ActorValue, not effective value [EV-0087]
M-0015 -> cast-power membership serialization and synchronous power-bundle replacement [EV-0088, EV-0100]
M-0012 -> duration/classification records, expiry flag, zero-duration cleanup, and deferred Dispel limits [EV-0094–EV-0099]
M-0013 -> HitData ownership, fixed poison-gas payload, and fixed reflection spells [EV-0101–EV-0103]
M-0003/M-0004 -> empty-keyword scan and null-key AV148 record boundary [EV-0093]
M-0008 -> player-created hazard cause copied to owner; no cause-less player route in the static scope [EV-0106]
Q-0001/Q-0013 -> corrected quest gate counts and thresholds [EV-0108]
Q-0006 -> stale consume-classification writer closure and separate long-duration Waterbreathing candidate [EV-0107]
EC-0001 status conflict -> “confirmed” source labels versus unresolved recipe/delivery evidence [EV-0053, EV-0056, EV-0090, EV-0091]
Speech status conflict -> root “confirmed” label versus unlogged detailed observation [EV-0068, EV-0092]

Blocked-hit receiver branch -> Block AV9, skips armor AV11/12
      |
      +-- negative Damage Resist (AV39) -> hypothesized non-positive Block points
               |
               +-- WICast / Marked-for-Death candidate (actor, target, location unknown)
```

## Cross-domain synthesis

The strongest grounded bridge to P0 is the separation between the hit receiver's armor-skill branch and its Block-skill amount. The source reports that blocking can suppress AV11/12 while leaving AV9 positive; a route to zero total skill XP must prove a non-positive AV9 amount and retain useful protection. The Marked-for-Death / WICast records are a candidate AV39 writer path, but the actor selection, counter baseline, and location access are not established. This is an inference from two static report families, not a verified shared runtime route.

### Derived OBJ-2 follow-up

`Q-0015` is a narrower successor to `Q-0004`, grounded in [EV-0020], [EV-0021], and the broader receiver/skill-sink audit [EV-0036]. It combines two separately reported branches into one discriminating question: can an ordinarily reachable AV39 writer make the blocked-hit Block amount non-positive while armor still reduces damage, so the shared skill-use guard rejects AV9 and the blocked route also omits AV11/12? The scripted-writer audit [EV-0037] rules out two tempting resistance-script routes but does not cover the separate WICast record candidate. The rival predicts clamping/reconstruction, an unreachable writer, a positive award, or failed protection control. This remains a proposed mechanism inference; the route and runtime predicates are unverified.

Other armor branches are already bounded by legacy reports: projectile-owner death does not alter the incoming armor predicate ([EV-0049]); pure spell projectiles avoid the physical sink by changing damage paths ([EV-0050]); and the audited official EP22 perk family contains no generic zero/negative XP multiplier ([EV-0051]). These are negative/adjacent results, not evidence that Q-0015 works.

A second shared primitive is the positive-amount skill-use guard. It appears in Speech, armor-block, and hazard analyses, but each caller computes a different amount and has separate state preconditions. The guard alone is not an exploit.

## Evidence links

- Quest gate scan: `EV-0019`.
- Block receiver: `EV-0020`.
- Negative resistance: `EV-0021`.
- WICast/Marked for Death: `EV-0022`, `EV-0035`.
- Shared skill-use guard: `EV-0029`.
- Incoming armor routing and invulnerability gate: `EV-0036`, `EV-0039`.
- Scripted negative-resistance writer audit and direct caller inventory: `EV-0037`, `EV-0038`.
- Projectile-owner, nonphysical spell, and EP22 perk boundaries: `EV-0049`–`EV-0051`.
- Poison surface, cleanup, reachability, and script writer reports: `EV-0056`–`EV-0064`, `EV-0078`–`EV-0079`, `EV-0082`–`EV-0083`.
- Enchanting, Speech, skill-use, and observer follow-ups: `EV-0065`–`EV-0077`, `EV-0080`–`EV-0081`, `EV-0084`–`EV-0086`.
- Historical runtime-only notes with missing raw logs: `EV-0070` and `EV-0071` (load baseline and school-selection report; neither is a current-target observation).
- ActiveEffect `kEnchanting` source-type boundary: `EV-0074` (static audit; no finite alchemy/spell route found in its examined scope).
- Enchanting base-skill cap, cast-power list cleanup, disenchant list/instance selection, and source-status discrepancies: `EV-0087`–`EV-0092`.
- Alchemy duration/classification edge cases, poison-gas/reflection controls, Shalidor scrolls, direct spell serialization, and the deadload user brief: `EV-0093`–`EV-0105`.
- Quest-gate, hazard-cause, and poison-consumption follow-ups: `EV-0106`–`EV-0108`.

The new evidence IDs connect to these topic groups: Speech selection/family and its stale confirmation label (`EV-0068`–`EV-0069`, `EV-0092`); Float32 cleanup correction (`EV-0057`); alchemy classification, Peak, recipe, script inventories, and old confirmation labels (`EV-0056`, `EV-0059`–`EV-0061`, `EV-0082`–`EV-0083`, `EV-0090`–`EV-0095`); self-poison delivery, transfer, and fixed payload controls (`EV-0062`–`EV-0063`, `EV-0101`–`EV-0103`); robe reachability (`EV-0064`); enchanting furniture, fixed outputs, conditions, callback ordering, and the base-skill cap (`EV-0065`–`EV-0067`, `EV-0084`–`EV-0085`, `EV-0087`); skill-use paths/multiplier scans (`EV-0072`–`EV-0073`, `EV-0086`); deadload/effect cleanup/transform and cast-power membership (`EV-0075`–`EV-0079`, `EV-0088`, `EV-0100`, `EV-0105`); disenchant row/instance handling (`EV-0089`); Shalidor scroll boundary (`EV-0104`); and observer limitations (`EV-0080`–`EV-0081`). Each is linked to a historical evidence record and a claim row in `research/CLAIMS.md`.

## Imported-source boundaries

The poison surface's 148 recipes are candidates from a historical scan, not verified recipes or delivery routes. The 89.2167511 Conjuration value is a cost-model prediction. The AV148 robe and its level gate are static source claims. Potion cleanup reports do not establish an all-load-order absence of writers. The deadload frozen-time statement is an unlogged historical user report; MGR21 and direct spell membership remain independent save/revert hypotheses. Enchanting furniture reports do not identify an accessible route. All new links point to historical reports and must retain those epistemic limits.

## Local mission cross-source and cross-domain synthesis

### DA14 level threshold (D13)

`EV-0108` is a hashed legacy static gate scan reporting `DA14 >=14`; local UESP page revision 3593351 (`EV-0129`) sets `ReqLevel=14` on *A Night To Remember* and names Sam Guevenne. The independent report and wiki page are consistent on a level-14 threshold lead. This is a cross-source check, not proof of a current runtime gate or bypass. The actual Steam AE file queries show the same 288-subrecord DA14 record in Skyrim.esm and Update.esm (`EV-0111`, `EV-0112`), but the active Python record reader preserves raw CTDA bytes and does not decode their semantics. The active profile/order is still incomplete (`EV-0110`), so no current winner or initiation transition is established.


### Ebony Warrior level threshold (D03)

`EV-0108` is a hashed legacy gate inventory reporting the Ebony Warrior threshold as `>=80`. Local UESP revision 3580051 (`EV-0134`) identifies the level-80 encounter. A private Apocrypha context capture (`EV-0133`) reports the same threshold but preserves uncertainty about whether it is a hard prerequisite or a prompt; the message body and identifiers remain in ignored storage. These sources agree on a reported threshold, but none establish the current AE winner or the exact transition. This scoped source agreement is recorded as `CL-L064`.

### Enchanting boundary and unsupported bridge (E12)

`EV-0124` is a local wiki statement about one base XP per crafted enchantment and named nonfactors. The legacy Staff Enchanter, furniture callback, and base-skill-cap findings (`EV-0065`, `EV-0066`, `EV-0084`, `EV-0087`) arise from different static/native investigations and lack matched current-build raw XP observations. No shared native function, record predicate, save field, or callback boundary is supported by these sources. They remain separate models under `CL-SYN-001` and Q-0005; the predicted discriminant is a paired 1.6.1170 test measuring raw Enchanting XP before/after matched crafts, comparing one versus two effects and varying item value or soul level while holding XP modifiers fixed. That prediction is not an observed result.
