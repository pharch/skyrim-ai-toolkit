# EV-0639 — Caller 57 tag-0x5F perk-rank addition and callbacks

## Competing models and discriminants

- H1, rank-list update: the event reports a perk rank insertion/update. It predicts the AddPerkVisitor, rank-count bound, PlayerCharacter rank-list mutation, and old/new-rank callback routing.
- H2, level-one perk-gate bypass: this route can place a perk on a level-one PlayerCharacter despite a level requirement. It predicts an ordinary caller path into the add routine without a level predicate and a verified level-gated perk whose rank becomes available at level one. A rank-count bound alone is insufficient.
- H3, combat/armor-skill route: the event or a rank callback reaches HitData, effective protection, AV11/AV12, or UseSkill. It predicts a producer-backed data/control edge to a mapped sink; unresolved per-rank virtual calls do not establish one.

## Direct GOG evidence

All captures use the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Their metadata verifies read-only execution, disabled auto-analysis, and executable identity. These RVAs do not transfer to Steam AE 1.6.1170.0.

- FUN_140658d00 writes tag 0x5F, derives a dword with FUN_1402ef8f0, stores another object pointer and two byte values, then queues through FUN_14065b800. Worker case 0x5F resolves a handle and calls FUN_1403906c0 with the object and both payload bytes [EV-0637], [EV-0639].
- The sole analyzed event producer is FUN_140750d80, called from FUN_14074b150 and FUN_14074b220. It rejects a null perk. If requested rank is zero, it reads the current matching rank through FUN_14068f020/FUN_1407177b0 and increments it. It returns when the request exceeds the byte at perk+0x52, scans PlayerCharacter+0x4b8 with a Ghidra-labeled BGSPerk::AddPerkVisitor, stores a perk-rank pair, and emits tag 0x5F with old rank 0 and the requested new rank [EV-0639].
- FUN_14068f020 calls FUN_1407177b0 through a nonnull nested pointer at +0xF8. FUN_1407177b0 uses the BGSPerk::FindPerkInRanksVisitor label, dispatches through PlayerCharacter slot +0x7D0, and returns a matched rank byte or zero. This is a current-rank lookup, not a Player-level read [EV-0639].
- FUN_1403906c0 scans a collection at +0x60/count +0x70. It calls each entry's virtual slot +0x58 when stored-rank+1 matches the old byte, or slot +0x50 when it matches the new byte; then it invokes FUN_1403918a0 and FUN_140391660. Two indirect sites remain, so callback effects are unresolved [EV-0639].
- FUN_14074b220 requires a nonnull object, updates a reference-counted collection at +0x4E8/+0x4F8, and may call FUN_140750d80 with rank 1 after checking a separate list at +0x4D0/+0x4E0. FUN_14074b150's decompilation omits displayed call arguments, but its captured instructions preserve incoming RCX/RDX/R8 across the call to FUN_140750d80. Neither wrapper has an analyzed incoming direct caller [EV-0639].
- A six-entry function-pointer region at RVA 0x18AD540 contains FUN_14074b150 and FUN_14074b220, but its bounded scan reports zero references to the table base. The RTTI check returns signature 0x83485740, not a validated MSVC vtable. The owner and runtime invokers remain unknown [EV-0639].

## Result and limits

H1 is supported for the captured static rank-list route and tag-0x5F event. The visible requested-rank limit is the perk's rank-count byte; this bounded path does not read Player level or establish perk eligibility. H2 remains proposed because wrapper invokers, perk records, and a natural level-one call are not established. H3 has no mapped direct sink, but the per-rank virtual callbacks remain unresolved. This is not a validated vanilla exploit, level-one access result, armor-XP bypass, Steam result, or bounty resolution. No causal edge is added to OBJ-1 quest gates, HitData, protection, AV11/AV12, or UseSkill.

## Next action

Continue the exact worker-caller census at caller 58/62, FUN_140658dd0; preserve the unknown owner of the rank-list wrappers as a later level-one access discriminator.
