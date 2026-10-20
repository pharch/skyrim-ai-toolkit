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
Q-0001 -> M-0016 -> DA14QuestStartNode [SMQN:0003FA1A] -> sole child DA14Start [QUST:0003FA17] [EV-0212–EV-0214]
QF_DA14Start Fragment_2 -> SetStage(5) on DA14, then Stop(self) [EV-0215]
M-0012 -> duration/classification records, expiry flag, zero-duration cleanup, and deferred Dispel limits [EV-0094–EV-0099]
M-0013 -> HitData ownership, fixed poison-gas payload, and fixed reflection spells [EV-0101–EV-0103]
M-0003/M-0004 -> empty-keyword scan and null-key AV148 record boundary [EV-0093]
M-0008 -> player-created hazard cause copied to owner; no cause-less player route in the static scope [EV-0106]
Q-0001/Q-0013 -> corrected quest gate counts and thresholds [EV-0108]
Q-0006 -> stale consume-classification writer closure and separate long-duration Waterbreathing candidate [EV-0107]
EC-0001 status conflict -> “confirmed” source labels versus unresolved recipe/delivery evidence [EV-0053, EV-0056, EV-0090, EV-0091]
Speech status conflict -> root “confirmed” label versus unlogged detailed observation [EV-0068, EV-0092]

HitData builder -> GetActorValue(AV39) + GetArmorBaseFactorSum -> totalDamage mitigation
        | physicalDamage is copied before this reduction; blocked flag is set afterward [EV-0261]
        v
Blocked-hit receiver branch -> Block AV9, skips armor AV11/12
      |
      +-- negative Damage Resist (AV39) -> hypothesized non-positive Block points
               +-- Marked-for-Death MGEF (negative armor candidate; player target not established)
       WICast CAST event -> Player-conditioned R1 caster alias
               +-- R2 nominal target alias; API documentation says akSpellTarget returns None
               +-- no supported edge from WICast to PlayerRef AV39
```

## Cross-domain synthesis

The strongest grounded bridge to P0 is the separation between the hit receiver's armor-skill branch and its Block-skill amount. The GOG source-order trace shows AV39 and the armor-base-factor sum reduce HitData total damage before blocked-hit bookkeeping; the receiver then routes blocked hits to AV9 and skips AV11/12 ([EV-0261], [EV-0222]). This confirms an upstream damage calculation followed by a separate skill branch, not a player-reachable XP-suppression result. Marked for Death remains a negative AV39 candidate, but WICast's Player-conditioned R1 alias and the event API's target-None caveat favor a player-cast response over a player-targeted writer ([EV-0241], [EV-0244]). No natural event, player AV39 state, or blocked-hit result is established.

### Derived OBJ-2 follow-up

`Q-0015` is a narrower successor to `Q-0004`, grounded in [EV-0020], [EV-0021], and the broader receiver/skill-sink audit [EV-0036]. It combines two separately reported branches into one discriminating question: can an ordinarily reachable AV39 writer make the blocked-hit Block amount non-positive while armor still reduces damage, so the shared skill-use guard rejects AV9 and the blocked route also omits AV11/12? The scripted-writer audit [EV-0037] rules out two tempting resistance-script routes but does not cover the separate WICast record candidate. The rival predicts clamping/reconstruction, an unreachable writer, a positive award, or failed protection control. This remains a proposed mechanism inference; the route and runtime predicates are unverified.

Other armor branches are already bounded by legacy reports: projectile-owner death does not alter the incoming armor predicate ([EV-0049]); pure spell projectiles avoid the physical sink by changing damage paths ([EV-0050]); and the audited official EP22 perk family contains no generic zero/negative XP multiplier ([EV-0051]). These are negative/adjacent results, not evidence that Q-0015 works.

A second shared primitive is the positive-amount skill-use guard. It appears in Speech, armor-block, and hazard analyses, but each caller computes a different amount and has separate state preconditions. The guard alone is not an exploit.

## Evidence links

- Quest gate scan: `EV-0019`.
- Block receiver: `EV-0020`.
- Negative resistance: `EV-0021`.
- WICast/Marked for Death: `EV-0022`, `EV-0035`, `EV-0241`, `EV-0244`.
- Shared skill-use guard: `EV-0029`.
- Incoming armor routing and invulnerability gate: `EV-0036`, `EV-0039`, `EV-0261`.
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

### DA14 Story Manager gate and intro handoff (OBJ-1)

The Steam AE official-master record scan links `DA14QuestStartNode` to its sole child `DA14Start` and identifies a `GetLevel` condition at comparison value 14 on PlayerRef using the xEdit condition table and PlayerRef reference notes; EV-0108 is the independent corrected CTDA operator decode that classifies the matching threshold as `>=14` ([EV-0108], [EV-0212]–[EV-0214]). No function-80 condition was found in the screened DA14/DA14Start QUST conditions or 65 linked INFO records across the official five-master corpus ([EV-0212], [EV-0213]). The `QF_DA14Start` PEX contains a fragment that sets stage 5 on its `DA14` Quest property and then stops itself ([EV-0215]); the VMAD fragment-to-stage mapping and active profile winner were not recovered. This static path supports CL-L065 and M-0016, but it does not establish that the main quest fully starts, exclude other entry paths, or demonstrate level-one access.

This record/Papyrus handoff has no supported causal edge to the incoming armor-skill route in M-0009. They share no evidenced native function, record gate, ActorValue or serialized state; this is an explicit no-edge rationale rather than a claim that the systems cannot share a lower-level engine primitive.

### DA14 stage-406 trigger access path (OBJ-1)

`REFR 00000EC8` (`defaultSetStageTRIG`) -> `DA14.SetStage(406)` is inside `CELL 0003D62B` (`DA14Interior`). The bounded cell scan finds an XTEL link to exterior `REFR 0003DC45` in `Morvunskar01`; that portal reference is persistent and initially disabled. The checked Skyrim.esm and Update.esm DA14 stage tables stop at stage 200, while alias 36's XMarker is enabled by `QF_DA14 Fragment_53` at an unresolved trigger stage ([EV-0216], [EV-0250]). The five-master raw FormID screen found no new direct record-level pre-gate MoveTo/Enable/start candidate; Update.esm's DA14 portal branch is cleanup after stage 200, and Dragonborn's DA14 alias caller remains unresolved ([EV-0264], [EV-0275]). This favors a downstream route for the records examined, not an exhaustive proof against dynamic/native paths or a runtime result for an undefined stage. It adds no causal edge to the OBJ-2 hit/armor path: no shared record, ActorValue, or native writer is supported between this DA14 chain and M-0017/M-0018/M-0020.

Claim mapping: CL-L107 records the bounded direct-reference result [EV-0264, EV-0275].


### OBJ-2 hit-data and armor-skill path (M-0017)

`HitData` population helper RVA 0x7DD220 -> hit-resolution function RVA 0x6BCAA0 -> player-receiver branch -> `kBlocked` bit 0 selects either AV9 Block points or unblocked worn-armor AV11/12 selection -> virtual Actor::UseSkill slot 0xF7 -> PlayerCharacter positive-points guard -> skill-progress callee ([EV-0217]–[EV-0223]). The positive `[RSP+0xA0]` comparison is on the attacker-side call and branches into, rather than away from, the receiver branch; this corrects the earlier attribution in EV-0036 ([EV-0222], C-OBJ2-ARMOR-GATE).

The supported source claims for this chain are CL-L066, CL-L067 and CL-L068; they preserve the GOG-only static scope and the unresolved protection/runtime result.

The worn-armor scan uses positive base armor rating to select an armor skill. That does not establish the actor's effective mitigation on the same hit. EV-0261 adds the source-order edge from the GOG AV39/armor-base-factor calculation into HitData total damage before the blocked flag and receiver skill route. No edge is yet supported from a non-positive armor points argument to a vanilla-reachable state that preserves measured effective armor protection; that remains Q-0004/Q-0015/Q-0018. No causal edge connects the MFD candidate or ActorValueInfo metadata to the concrete AV39 getter because the getter implementation and natural PlayerRef route are unresolved. There is no supported causal edge from DA14 Story Manager state M-0016 to this hit/skill route; no shared record, ActorValue or native state has been identified.

Physical-trap inputs add a GOG-only edge into the shared HitData/armor-related calculation path and then directly into `FUN_1406b9df0`. The known `FUN_1406bcaa0` AV11/AV12 receiver resolver calls that same handler only after its skill branch. The shared handler consumes HitData `totalDamage` and can conditionally route a negative Health (`0x18`) delta through `FUN_1406b49d0` to Actor::HandleHealthDamage [EV-0217], [EV-0218], [EV-0222], [EV-0293], [EV-0294]. This is a candidate damage path past the known inline armor resolver, not a measured protection/AVSK result or a global negative for unqueried descendants.

EV-0296 maps the Actor receiver's slot `0x99` state predicate, slot `0x5C` ActorMagicCaster object-provider, and slot `0x70` state lookup in `FUN_1406b9df0`; the PlayerCharacter `0x70` override adds a slot-`0x71` flag predicate and then delegates. The selected targets have no captured AV11/AV12 `UseSkill` call or direct edge back to `FUN_1406bcaa0`. This extends the bounded M-0033-to-M-0017 continuation with an ActorMagicCaster setup branch, not an XP-transfer edge. The remaining non-Actor receiver indirections stay unclassified; no edge to OBJ-1 quest gates, ActiveEffect save serialization, or effective protection is supported. Claim mapping: CL-L130 -> mapped Actor/PlayerCharacter receiver slots [EV-0291], [EV-0295], [EV-0296].

EV-0297 follows the selected ActorMagicCaster update methods. They change caster fields/list state, read owner/flag values, and compute a scalar; no AV11/AV12 `UseSkill` or direct edge to `FUN_1406bcaa0` appears in the mapped call depth. A nested pointer supplied from HitData `+0x38` remains dynamically typed, and its virtual targets are unresolved. This sharpens the M-0033 path classification but adds no XP-transfer edge and no causal relation to ActiveEffect save/load or OBJ-1 gate state. Claim mapping: CL-L131 -> bounded ActorMagicCaster method screen [EV-0296], [EV-0297].


### OBJ-2 AV39 candidate-to-hit hypothesis (M-0018)

The corrected GOG native trace adds a conditional candidate chain: MFD's Detrimental flag and ActorValueInfo bit 9 determine whether `OnAdd` flips ActiveEffect magnitude; `ModifyOnStart` supplies its generic MagicTarget actor to `ModifyActorValue`, and the Recover flag selects a temporary modifier mode ([EV-0257], [EV-0258]). AV39's bit-9 value and natural PlayerRef target remain unknown. This supports a possible MFD-to-actor-AV39 mechanism only under those conditions; it adds no edge to the HitData AV9 formula, retained protection, or AVSK progress.

EV-0259 screens the GOG `ActorValueInfo` Load/ClearData/InitItemImpl bodies and installed official-five-master AVIF subrecords. No direct write to `+0x60` or AVIF `DATA` field is identified, but the base loader still uses indirect dispatch and global/runtime writers remain unsearched. This narrows the initialization source without adding a causal edge from AVIF metadata or the ValueModifier path to HitData, effective protection, or armor XP; Q-0015 retains this explicit no-edge rationale.

The installed official-master scan connects Marked-for-Death spell forms to an AV39 MGEF and identifies separate Doom Lord, test-spell, and Haknir weapon candidates ([EV-0224]–[EV-0227], [EV-0242], [EV-0243]). MGEF `0010319D` is a Value Modifier for AV39; its Update.esm override adds the Detrimental flag, while the three tiers store magnitude 25/50/75 and 60-second duration ([EV-0257]). This identifies a plausible harmful AV39 candidate but does not establish the resulting raw ActorValue delta. The MFD spell tiers decode as Voice, Fire and Forget, Aimed delivery rather than Self delivery; this narrows but does not decide whether an ordinary enemy can apply the effect to PlayerRef ([EV-0225], [EV-0255]). The exact shout record links its three word tiers; the four other official references are INFO conditions checking `GetEquippedShout`, and the direct NPC_ scan found no shout/tier reference ([EV-0256]). These are bounded record results and do not exclude list, script, native, or event selection. WICast's event-filled CastingActor/R1 and SpellTarget/R2 aliases plus separate forced Player alias are preserved in EV-0241. The Papyrus Index's CK-Wiki-derived `OnStoryCastMagic` reference defines caster and target parameters but notes that `akSpellTarget` always returns None ([EV-0244]); this supports an inference that R1 is the player's cast source and R2 is not evidence of PlayerRef. No causal edge is established from WICast or the MFD records to player AV39 application, or from AV39 to measured Block XP suppression. Q-0015 remains open for a natural player-target route and the required hit/protection/XP measurements.

M-0020 adds a generic, build-attested GOG ActorValue clamp lead: `GetClampedActorValue` reads ActorValueInfo flags and has a zero-floor path ([EV-0249]). EV-0258 corrects the effect-slot attribution and shows ActorValueInfo bit 9 also controls MFD magnitude sign normalization and the mode-2 modifier clamp direction; the flag's AV39 value and relationship to the hit-damage input remain unresolved. A bounded direct-caller audit found one dynamic-index caller with no local AV39-excluding bound, plus three unresolved DATA references to its function entry; the project reports no exact-address users for those locations ([EV-0252]–[EV-0254]). The exact AV39 metadata, record consumers and damage-resist caller are not resolved, so no edge is added from that generic clamp to the AV39 value used by HitData or the AV9 amount. A direct Steam AVIF capture without a DATA range does not resolve that engine behavior. The discriminant remains an exact-build caller/data trace or natural raw AV39 plus HitData capture, followed by the protection and AVSK controls in EXP-0013.

### OBJ-1 Haknir gate, alias and book lead (M-0019)

Dragonborn.esm SMQN 02024003 (`GetLevel >= 36`) -> child LEVL QUST 02038FB0 -> child stage-10 `Fragment_0` -> main QUST 02024002 stage 10. The main Haknir alias is Initially Disabled and resolves through the Gyldenhul Barrow location chain to ACHR 02037FEA ([EV-0231]–[EV-0234], [EV-0271]). A second identified stage-10 writer is DLC2Init QUST 02016E02 stage 100 -> `Fragment_4`; it checks Player `GetLevel` against a QF property bound to GLOB 02024004 (static value 36.0) before calling main-Q `SetStage(10)`. The raw official-master screen found only these DLC2Init and SMQN records as non-NAVM references to that global ([EV-0233], [EV-0271]).

Main-Q stage 10 registers the Shoal update path; that path may reach stage 20. DLC2WE13's book-carrying encounter is conditioned on main-Q stage 20, and eleven book placements outside the Barrow do not prove access ([EV-0233]–[EV-0236]). The recovered book `OnRead` calls `SetStage(1)` only after `GetStageDone(mainQ,20)` succeeds. The misc Haknir quest reads main-Q stage 20 to change its own objective/map state but contains no main-Q `Start` or `SetStage` call in the complete bounded PEX ([EV-0270], [EV-0271]). Main-Q stage 90 -> `Fragment_23` -> `Alias_Haknir.StartBattlePhase(0)` -> phase-0 move/enable/combat -> `OnDying` -> main-Q stage 100 ([EV-0245], [EV-0270]). This favors gated progression for the traced book, initializer, LEVL helper and misc-quest paths, without ruling out uninspected runtime/native/profile writers or proving alias fill. No level-one transition or death was observed; EV-0260 records missing live test prerequisites. No causal edge is supported between M-0019 and OBJ-2 hit/skill paths M-0017/M-0018; the evidence identifies no shared record, ActorValue or native function.

### OBJ-2 award-side EP22 record route (CL-L092)

The five-master MGEF/PERK screen links the 1,633-record primary-AV inventory and 523-record PERK inventory to the EP22 award-side route ([EV-0262]). Two Skyrim PERKs apply positive 1.20 multipliers under `EPMagic_IsAdvanceSkill` conditions for Block/Heavy Armor or Light Armor; the Dragonborn 0.05 entry is scoped to Enchanting at staff FURN 02017736. This adds a bounded award-side node to M-0017/Q-0004 but no edge from these records to AV39 mitigation, HitData total damage, or effective protection. Q-0004 still needs matched raw AVSK and protection observations; EV-0260 records the live environment gap.

### OBJ-2 PlayerCharacter armor-factor dispatch (CL-L093)

The GOG HitData builder's Actor slot `0xE7` call resolves on a PlayerCharacter vtable to a getter returning the float at `this+0x274`; the base Actor slot is a zero-returning stub ([EV-0263]). The builder applies the factor to `totalDamage` before the blocked flag, after which the receiver path routes to AV9 and omits AV11/12 ([EV-0261], [EV-0222]). This adds a dynamic-dispatch node to M-0017 and supports the source-order half of Q-0014. It does not establish a positive factor, actual protection for equipped armor, XP deltas, or Steam equivalence; EXP-0017 retains the required live discriminator. No causal edge links this hit path to OBJ-1 quest gates.

DA14Start stage 30/50 -> first/second Sam drinking SCEN Start; scenes -> DA14Start stages 40/60; stage 70 -> DA14 stage 5 -> DA14Start Stop [EV-0264]
Dragonborn DLC2DialogueRavenRock QUST -> DA14 alias 3 property `DA14Gleda`; caller behavior unresolved [EV-0264]

DA07StartNode [GetLevel >= 20] -> DA07intro QUST [EV-0019, EV-0265]
DA07intro stage 0 -> Pamphlet ALCO alias -> WICourier; alias equip/receipt -> SetStage(5) [EV-0265]
  Base pamphlet BOOK and inspected INFO handoffs do not independently fill alias/start quest [EV-0265]
DA07intro stage 0 -> Enable/MoveTo Silus; MoveTo Madena scene markers [EV-0267]
  Initial placements: Silus ACHR 000240CE initially disabled in Silus house; Madena ACHR 0001A6C3 in White Hall [EV-0267]
REFR 000B1403 DawnstarExterior04 -> wait for Silus + Madena -> DA07intro.SetStage(7)
  -> DA07intro stage 7 -> DA07IntroScene (aliases 0/2) -> if scene completes, SetStage(10) [EV-0266]
  Ordinary actor-pair bootstrap is disfavored from screened initial placements; alternate writers/runtime remain open [EV-0260, EV-0267]
DA07StartNode [GetLevel >= 20] -> DA07MuseumScenesNode -> DA07MuseumScenes QUST [EV-0019, EV-0268]
  Separate player Museum trigger refs in Silus house -> DA07MuseumScenes.SetStage(10/20/40/50) [EV-0268]
  DA07MuseumIntroScene [Begin on Quest Start] -> tapestry scene -> DA07intro.SetStage(200) + DA07.SetStage(5) [EV-0268]
  REFR 000240CA XLOC [level 255 Requires Key, KEYM 000960F0] -> keyed house boundary -> museum trigger access prerequisite [EV-0269]
  Museum trigger box centers are 277–671 coordinate units from the door reference; spatial lead only, no NIF collision or clip evidence [EV-0269]
  Candidate only: house inaccessible until level 20 by UESP; clip route, alias fill, HasLoaded3D, and useful quest progression unobserved [EV-0260, EV-0268, EV-0269]

No causal edge is supported between these DA07 quest records/scripts and the OBJ-2 HitData/armor skill mechanisms M-0017/M-0018; the investigated paths share no identified record, ActorValue, native routine, or serialization primitive [EV-0265–EV-0268].

Claim mapping: CL-L095 -> M-0022 pamphlet alias lifecycle [EV-0265]; CL-L096 -> M-0023 actor-pair trigger [EV-0266]; CL-L097 -> M-0024 actor readiness [EV-0267]; CL-L098 -> M-0025 Museum-trigger scene and locked-entry candidate [EV-0268, EV-0269]. Q-0020 carries the Museum-trigger entry and scene discriminants.

### GOG Papyrus SetStage startup path (Q-0013)

In GOG AE 1.6.1179.0, the inferred `Quest.SetStage` wrapper -> `TESQuest::EnsureQuestStarted(startNow=false)` -> deferred stage work when startup is pending; an event-scoped Event ID with the tested flag bit clear is rejected before this path [EV-0272]. A separate immediate EnsureQuestStarted branch calls the quest-start helper and `BGSStoryTeller::BeginStartUpQuest`. No named alias-fill call or alias state is established. For the Haknir chain, the native ability to schedule startup does not remove either caller's `GetLevel >= 36` predicate: DLC2Init checks the global before SetStage, and the LEVL helper is selected behind the Story Manager threshold [EV-0271, EV-0272]. This refines interpretation of M-0019 and adds no causal edge to OBJ-2 armor/skill mechanisms M-0017/M-0018. The native trace is GOG-only; no Steam RVA mapping is implied.

Claim mapping: CL-L105 -> M-0026 GOG SetStage start scheduling and event guard [EV-0272].

### MFD word forms and Drain Vitality spell payload (OBJ-2 candidate screen)

Dawnguard SHOU `02018244/020181B8/020181B7` (Drain Vitality labels) reuse the three MFD word forms -> linked custom SPELs `02018243/020181B5/020181B4` -> Health/Magicka/Stamina, Script-archetype and stagger MGEFs [EV-0273].
The three Value Modifier effects target AV24/25/26; the captured custom spell payloads omit MFD MGEF `0010319D` (AV39) [EV-0273, EV-0257].
This narrows the reported shout path but does not identify its acquisition, target, Script-archetype behavior, profile winner, or natural WICast alias fill. It adds no supported edge to the AV39 -> HitData mitigation -> armor-skill/Block XP chain [EV-0222, EV-0257, EV-0273].

Claim mapping: CL-L106 -> M-0027 Drain Vitality/MFD word-payload distinction [EV-0273]. WICast target and natural Player AV39 remain unresolved under C-OBJ2-WICAST-PLAYER-TARGET and EV-0260.

### Research tool capability boundary (Q-0007)

Current WSL Python 3.12 strict dispatch and research-state integrity checks pass [EV-0274]. The direct TES4 parser has source-file scope [EV-0205, EV-0273]; native xEdit is a separately validated five-official-master Windows UI route with a later WSL interop failure [EV-0207, EV-0247]; Ghidra is the existing matching GOG project, not the installed Steam runtime [EV-0210, EV-0272]. Exact-profile winners and live SKSE/Observer state remain gated [EV-0260].

This is research infrastructure, not an engine causal node. No edge from tool readiness to a level-one quest transition, AV39 state, armor mitigation, or skill XP is supported. The current all-suite status remains unresolved because EV-0211 and later EV-0260 differ; EV-0274 records only strict Python and research-state passes and runs no tests.

Claim mapping: CL-TOOL-006 -> bounded offline interface and prerequisite inventory [EV-0274].

### Dawnguard VQ01 book alias and Crypt02 stage-trigger candidate

VQ00 level-10 helper -> starts VQ00 and sets VQ01 misc objective stage 5 -> misc-objective fragment requests VQ01 stage 10 -> VQ01 stage-10 fragment enables `VQ01EnableMarker` (`02002F66`) -> forced Book reference `0200D072` is in Crypt02 and parented to that marker [EV-0276].

VQ01 main-quest `Book` alias -> `DLC1VQ01BookScript`: read requests VQ01 stage 17; player pickup requests stage 17 only if VQ01 stage 15 is done [EV-0276]. This corrects the historical EV-0019 owner label. The bounded stage-trigger screen also places VQ01 stage-15 (prerequisite 10), stage-17 (no optional prerequisite property), and stage-18 (prerequisite 17) references in Crypt01/02. The generic script PEX and the physical/activation route to the stage-17 reference remain unresolved [EV-0276].

Separate physical-gate chain: persistent marker REFR `02017772` (base `XMarker` STAT `0000003B`) -> XESP child REFR `02009742` (`NorPortcullisLarge01`, ACTI `0003E726`) -> generic `default2StateActivator` animation and keyword-linked collision toggles [EV-0277]. The PEX contains no VQ01 stage call. EV-0282 decodes XESP Flags as zero (ordinary parent inheritance, no Pop In); the child's ACTI header `0x40000000` maps to Navmesh - Ground, while both child and STAT parent lack Initially Disabled. This narrows the serialized state model but does not establish loaded state, a parent writer, collision, passage through rubble, or the stage-17 trigger route. The child/parent marker chain remains distinct from VQ01's Book alias marker `02002F66`. This does not add an edge to OBJ-2.

Source interpretation branch: Dimhollow's UESP place-summary `level=Min: 6` -> `Template:Place Summary/Skyrim` “Level” row -> `Skyrim:Encounter Zone Level` redirect -> `Skyrim:Dungeons#Levels`, which describes encounter-zone minimum/maximum levels as separate from entry [EV-0278]. Installed Crypt01/Crypt02 CELL records both link XEZN to ECZN `02004EE7` (`DLC1DimhollowCryptZone`). This source/record chain is separate from VQ01 stage gates and the physical rubble path; it adds no OBJ-2 edge.

Claim mapping: CL-L108 -> `M-0028` book alias ownership/configuration [EV-0276]; CL-L109 -> `M-0028` stage-trigger placement candidate [EV-0276]; CL-L110 -> `M-0029` portcullis parent, flag decode, and generic activation [EV-0277], [EV-0282]; CL-L111 -> `C-OBJ1-DIMHOLLOW-MIN-LEVEL` field interpretation [EV-0278]. Q-0021 tracks Crypt02 stage-17 reachability and trigger semantics. No causal edge is supported from this OBJ-1 source/quest/placement chain to OBJ-2 armor mitigation, AV39, or armor/Block XP.
### ActiveEffect save/load serialization screen (Q-0006)

The fresh GOG 1.6.1179.0 Address Library mapping resolves ActiveEffect vtable ID 205813 to RVA 0x187C738. Base SaveGame/LoadGame write and restore elapsed time, duration, magnitude, flags, references, and the 16-bit usUniqueID; FinishLoadGame rebuilds associated ReferenceEffect attachments. Base Update/Finish are stubs, CanFinish is a separate gate, and the inspected Compare body does not read usUniqueID (EV-0279). This supports a serialized logical-state model but does not establish functional after-load persistence, wait/travel timer progression, the full expiry dispatcher, derived overrides, or Steam behavior. Q-0006 remains blocked only on a functional save/Observer discriminator under EV-0260.

This path has no identified shared native routine, ActorValue, HitData field, or serialization caller with OBJ-2's incoming-hit routing and armor/Block XP path M-0017 (EV-0217–EV-0223, EV-0261–EV-0263). It also does not identify a common serializer with the screened OBJ-1 quest-stage paths. The word “effect” or the fact that both systems persist state is not a causal edge. No OBJ-2 or OBJ-1 edge is added. Claim mapping: CL-L112 -> M-0030 ActiveEffect base timer-field serialization (EV-0279).

### Enchanting credit and shared skill-use sink (Q-0005)

The GOG EnchantMenuCraftCallback success path -> one visible `Actor::UseSkill` slot `0xF7` dispatch -> PlayerCharacter positive-points guard and skill-progress helper; its skill ID is read from the workbench `usesSkill` byte and its points come from a shared global float [EV-0280]. Base Skyrim.esm `CraftingEnchantingWorkbench` FURN `000BAD0D` stores WBDT `03 17`, mapping `usesSkill` to AV23/Enchanting [EV-0281].

The same PlayerCharacter `UseSkill`/progress sink receives incoming-hit armor and Block awards in the separate GOG trace [EV-0217]–[EV-0223]. This is a supported cross-domain edge from M-0031 to M-0017 at the award sink, while the craft station's points source and HitData's damage-derived points source remain distinct. It does not connect Enchanting credit to armor mitigation, AV39, or OBJ-1 quest initiation; no XP-suppression transfer is established. Raw Enchanting progress and the numeric points value remain unknown because no verified AVSK observer or disposable test save is available (EV-0260).

Claim mapping: CL-L113 -> M-0031 craft credit path [EV-0280, EV-0281]; CL-SYN-002 -> shared skill-use sink with caller-specific producers [EV-0217]–[EV-0223], [EV-0280]. The exact Steam runtime path and one-versus-two craft deltas remain open under C-OBJ3-ENCHANT-CREDIT and EXP-0029.

### Zero effective armor rating and hit XP (Q-0023)

Worn positive-base-DNAM ARMO -> unblocked receiver's AV11/12 eligibility selection -> PlayerCharacter positive-points guard -> skill progress [EV-0217]–[EV-0222]. The GOG source checks base item rating, not the current displayed/effective rating, before selecting the armor skill route. The private export's level-one negative-rating and displayed-zero reports are untrusted leads; the reported continued XP is consistent with that source path but does not independently confirm it for Steam [EV-0283].

This updates the armor branch of M-0009 and adds contradiction C-OBJ2-BASE-DNAM-VERSUS-EFFECTIVE-RATING. It adds no edge from AV39, Dragonhide/transformation state, or the OBJ-1 quest paths to zero armor XP. A true zero-base-DNAM item with separate measurable protection remains a distinct candidate; no live control or raw AVSK result exists.

Claim mapping: CL-L114 -> M-0009 worn base-DNAM eligibility versus effective rating [EV-0283], [EV-0222]. Q-0023 closed as a bounded lead screen; the active P0 objectives remain open.

### Dawnguard archive tool boundary (Q-0024)

The tested Papyrus CLI fixes extraction to the uncompressed PEX stream in `Skyrim - Misc.bsa`; the optional literal scan adds `cc*.bsa`, not Dawnguard. The internal helper's path argument, raw signature scan, and synthetic test fixture do not constitute a validated Dawnguard BSA route [EV-0284]. This blocks only that extraction lane. No archive bytes were inspected, and no conclusion about the target PEX or quest mechanism follows.

This tool capability has no causal edge to VQ01 trigger behavior, level-one access, armor mitigation, AV39, or skill XP. Claim mapping: CL-TOOL-007 -> bounded archive-interface capability [EV-0284]. Continue with the independent P0 armor points-producer question Q-0025.

### OBJ-2 receiver armor points dataflow and whole-HitData clear (Q-0025)

Default `FUN_1407dd220` / alternate `FUN_1407dd5b0` hit population -> `FUN_1407ddf50` snapshots pre-resistance `totalDamage +0x50` into `physicalDamage +0x54` -> AV39 and armor-base-factor mitigation changes `totalDamage` -> player receiver AV11/AV12 `UseSkill` points read from `physicalDamage +0x54` -> PlayerCharacter positive-points guard -> skill progression [EV-0217], [EV-0220]–[EV-0223], [EV-0261], [EV-0285]. The standard source path separates the armor points input from the final mitigated damage field.

Attacker `currentProcess->middleHigh->doNoDamage` is consumed one-shot -> if attacker `IsInCombat` is false or `AIProcess::ignoringCombat` is set, `FUN_1407dda40` zeroes the 8-byte pair at `HitData+0x50` -> both `totalDamage` and `physicalDamage` become zero before receiver routing -> non-positive AV11/AV12 points are rejected by the PlayerCharacter sink [EV-0220], [EV-0221], [EV-0285], [EV-0286]. This is an attacker-side whole-hit cancellation path; it does not establish that armor caused the damage reduction or that useful protection is retained. The only observed direct setter call that can pass true is `FUN_14048a5b0`, which reads bit 1 from parameter slot 7 through process-level-gated `FUN_14048a390`; the callback table consumer and slot schema are unresolved [EV-0287]. This is not a direct edge from ordinary HitData construction. Claim mapping: CL-L117 -> bounded setter source and caller [EV-0287].

This strengthens M-0017's caller-specific points producer and adds the attacker process/combat-state cancellation edge. It does not establish a causal link from AV39 mitigation to normal AV11/AV12 points, from this state to effective armor protection, or from OBJ-1 quest state to OBJ-2. Claim mappings: CL-L115 -> M-0017 pre-resistance points [EV-0285]; CL-L116 -> attacker-side no-damage clear [EV-0286]; contradiction C-OBJ2-ARMOR-POINTS-VERSUS-MITIGATED-DAMAGE.

### Ebony Warrior CLOC gate and quest-stage handoff (Q-0028)

Skyrim.esm `SMEN 0001320E` (`CLOC`) -> Dragonborn.esm `SMQN 0202C49F` (`DLC2EbonyWarriorNode`) with PlayerRef `GetLevel >= 80`, five city `Location 2` event-data alternatives, and a `DLC2SolstheimLocation` `Location 1` condition -> sole child `QUST 0202C49E` (`DLC2EbonyWarriorQuest`) [EV-0288]. The CLOC QUST's Start Game Enabled bit is clear. Its stage-10 QF fragment enables the unique `EbonyWarrior` alias, moves its reference to `CityCenter`, and adds the pickpocket modifier perk. Later stage-100 `OnLocationChange` logic moves the actor to the Last Vigil alias and starts combat when the player enters that location; `OnDeath` requests stage 200 [EV-0288]. The location event-slot direction remains unproven, so the graph records the serialized fields and callback ordering without assigning old/new meanings.

All 4,421 Dragonborn.esm INFO CTDAs were screened with no function-index-80 predicate, while linked DIAL/quest-stage records use quest-stage conditions [EV-0288]. This supports M-0032, C-OBJ1-EW-STORYMANAGER-LEVEL80-VERSUS-PROMPT, CL-L118 (CLOC node and GetLevel condition), CL-L119 (quest stage/alias handoff), and CL-L120 (bounded INFO negative screen). The separate GOG native trace finds the functions inferred as `Quest.Start` and `Quest.SetStage` reject a nondefault Event ID before deferred `EnsureQuestStarted` work; the installed Steam QUST's ENAM=CLOC is a separate record observation, so their interaction is an inference [EV-0272], [EV-0289]. Five-master QUST/DIAL/INFO scans found no external QUST reference; its six QNAM DIAL references and three INFO quest-stage references are confined to Dragonborn.esm [EV-0289]. Q-0030 then scanned raw subrecord bytes across every record signature in the five official masters. The only ACHR for NPC base `020285C3` is `02030CC9` `DLC2EbonyWarriorRef`, marked Initially Disabled and lacking XESP; the QUST's `EbonyWarrior` alias uses that same base as a Unique Actor fill, and stage 10 enables/moves it [EV-0290]. Its other raw references belong to the quest's dialogue, packages, perk, location, story node, and view/link records. This supports the serialized gated alias path and falsifies an independent direct-record placement/start path within the five source files. Parent CELL context, PEX bodies, dynamic lookups, profile overrides, and runtime state remain open. The Steam CLOC record and GOG event-scope trace remain separate observations, not proof of Steam behavior. This OBJ-1 selection/relocation chain has no supported edge to M-0017 armor mitigation or AV11/AV12 hit XP.

Claim mapping: CL-L121 -> GOG event-scoped Quest.Start/SetStage wrapper behavior (EV-0272, EV-0289); CL-L122 -> bounded official QUST/DIAL/INFO reference screen (EV-0289); CL-L123 -> the sole initially disabled ACHR and gated alias fill (EV-0288, EV-0290); CL-L124 -> all-signature five-master raw byte screen (EV-0290).

### Physical trap Papyrus handoff and the HitData caller gap (Q-0031)

`TrapFallingRockLg01` ACTI -> `PhysicsTrap` tiered damage assignment -> `PhysicsTrapHit.OnTrapHitStart` impact checks -> native `ObjectReference.ProcessTrapHit` [EV-0292]. In the matching GOG project, the exact native registration -> `FUN_140a30e80` -> receiver vtable slot `0x58` -> PlayerCharacter `FUN_140679da0` -> `FUN_1407dd110` -> common HitData builder `FUN_1407ddf50` -> separate receiver handler `FUN_1406b9df0` [EV-0261], [EV-0293]. This establishes a causal edge from trap inputs to M-0017's HitData construction/armor-calculation subpath.

The trap receiver handler does not directly call the previous AV11/AV12 candidate `FUN_1406bcaa0`; that function's only observed direct caller remains `FUN_1406bb690` [EV-0291]. `FUN_1406b9df0` includes a conditional AV15 Sneak call through Actor::UseSkill slot `0xF7`, a distinct award from Heavy/Light Armor AV11/AV12. Thus the trap path and M-0017/M-0031 share the generic skill-award sink, while their skill IDs and points producers differ. This creates no demonstrated transfer to armor XP, no finding that a valid hit bypasses AV11/AV12, and no live mitigation result. M-0030 ActiveEffect serialization and M-0032 quest alias/start records still have no shared native call, ActorValue, HitData field or serializer with this path.

EV-0294 adds the call convergence: the exact trap route enters `FUN_1406b9df0` from `FUN_140679da0`; the known AV11/AV12 resolver `FUN_1406bcaa0` calls that same handler after its skill branch. The handler reads HitData `totalDamage` and conditionally reaches `Actor::HandleHealthDamage` through `FUN_1406b49d0` for a negative Health delta. This is a static post-resolver damage candidate; remaining descendants, actual protection and AVSK remain open.

EV-0295 extends the route through ActorValue callbacks. `FUN_1406b49d0` -> `FUN_1406b4c70` indexes the runtime-initialized table at `0x14319b880`; startup code assigns AV11 and AV12 to `FUN_1406b65c0`, which dispatches Actor slot `0xCA`. The Actor base target is a `RET`; PlayerCharacter target `FUN_140729110` resets two fields and updates a container through `FUN_1406d2850`. Health AV24 maps to `FUN_1406b6050`, followed by the selected `HandleHealthDamage` path. No AV11/12 `UseSkill` or direct edge back to `FUN_1406bcaa0` appears in these mapped callbacks. This narrows the candidate route without establishing live damage/protection or resolving every indirect call in `FUN_1406b9df0`.

Claim mapping: CL-L125 -> bounded direct-caller context (EV-0291); CL-L126 -> physical trap record/PEX input (EV-0292); CL-L127 -> exact GOG native/PlayerCharacter route to shared HitData construction (EV-0293); CL-L128 -> shared post-resolver handler and conditional HealthDamage route (EV-0294); CL-L129 -> bounded AV11/12 callback table and PlayerCharacter slot-0xCA target (EV-0295). M-0033 links trap inputs to M-0017 builder/armor calculations and the common receiver handler. The visible AV15 branch shares the generic `UseSkill` sink with other skill-credit producers but does not establish AV11/AV12 transfer [EV-0261], [EV-0292]–[EV-0295]. No new edge to OBJ-1 or a separate armor-credit mechanism is supported. No Steam or vanilla-reproduction edge is added.

### M-0034 — Dawnguard level-10 messenger helper and alternate starts (Q-0037)

`DLC1VQ00Node` SMQN `0200D911` -> `GetLevel >=` GLOB `0200D912` (`DLC1VQMinLevel` = 10) -> QUST `0200D90B` (`DLC1VQ00ChangeLocation`) -> Messenger alias to `DLC1Durak` NPC_ `0201541D` [EV-0298]. This is the serialized level-gated Durak messenger path. Captured QUST VQ00 `0200D90E` and VQ01 `0200352A` conditions are stage/cell checks, with no `GetLevel`; targeted VQ00/VQ01 INFO conditions identify dialogue actors. Local UESP revision 3603039 separately reports guard-rumor, Agmaer/Dayspring Canyon, and Fort Dawnguard routes, including `Awakening` progress without the starter quest appearing in the journal. These are alternate-path leads, not a level-one runtime result. The native xEdit query failed before record loading; no profile winner, script absence, or exact level-one transition is claimed. The Dawnguard path has no causal edge to M-0017, AV39, ActiveEffect serialization, or armor/Block XP because no shared native, ActorValue, HitData, or saved-state primitive was observed. Claim mapping: CL-L132 -> scoped gate and alternatives [EV-0298].


### Dawnguard Story Manager census extension (Q-0038)

Q-0038 enumerated all 36 Dawnguard.esm SMQN and its one SMEN record. Only `DLC1VQ00Node` contains a function-80 `GetLevel` CTDA; the AM/PM vampire-attack nodes use function-74 `GetGlobalValue`, and SMEN `0001320E` has no CTDA [EV-0299]. This strengthens the bounded source census but does not cover other record signatures, scripts, profile winners, or runtime. No causal edge to OBJ-2 is supported. Claim mapping: CL-L133 -> complete Dawnguard.esm SMEN/SMQN census [EV-0298], [EV-0299].

### Five-master Story Manager census (Q-0039)

EV-0300 expands the serialized source-file inventory from Dawnguard alone to all five official masters. Fifteen distinct SMQN nodes carry function-index-80 `GetLevel` predicates; twelve extend beyond DA14, Durak, and Ebony Warrior. Their children and parent branches are mapped, with several nodes selecting helper QUSTs rather than the named main quest. This falsifies the known-three-exhaustive model only within the five-master SMEN/SMQN file scope. No causal edge is added to the armor/HitData/XP graph: no shared native call, ActorValue, ActiveEffect or serialized state primitive was observed. DA04's helper-vs-main-start distinction is queued as Q-0040. Claim mapping: CL-L134/CL-L135 -> EV-0300; mechanism M-0035.

### DA04 helper-versus-book entry (Q-0040)

`SMQN 0010481D DA04SeptimusFindPlayerNode` -> `GetLevel >= 15` -> helper `QUST 0010481C DA04SeptimusSendForPlayerQuest`; the helper fragment adds the Septimus letter to the courier. Main `QUST 0002D512 DA04` instead has the Start Game Enabled flag and binds alias 19 `RuminationsBook` to REFR `00032787`/BOOK `00032785`. The alias's `DA04RuminationsScript.OnRead` calls `SetStage(1)`; VMAD maps that stage to Fragment_18, which sets stage 5 [EV-0300], [EV-0301]. This supports a source-level ordinary early-entry route below the helper threshold and falsifies the all-entry-gated model for this chain. It does not prove active-profile winners, physical accessibility, or a level-one runtime transition.

Cross-domain synthesis: the DA04 path and M-0017/M-0033 armor hit-credit paths show no shared native call, HitData, armor/Block ActorValue, ActiveEffect or serialization primitive [EV-0301], [EV-0217]–[EV-0223], [EV-0292]–[EV-0297]. The relation remains unsupported; discovery of a shared state writer or call edge would falsify this no-edge assessment. No causal edge is added. Claim mapping: CL-L136 -> EV-0300/EV-0301; mechanism M-0036.

### Shared trap mitigation and resolver bypass (Q-0041)

`ProcessTrapHit` PlayerCharacter slot 0x58 -> `FUN_140679da0` -> `FUN_1407dd110` -> shared `FUN_1407ddf50` -> `FUN_1406b9df0`. Normal builders `FUN_1407dd220`/`FUN_1407dd5b0` also call `FUN_1407ddf50`; the helper snapshots `totalDamage` into `physicalDamage`, reads AV39 and Actor slot 0xE7 (`GetArmorBaseFactorSum`), then reduces `totalDamage` before blocked-hit bookkeeping [EV-0302]. The known normal resolver `FUN_1406bcaa0` places its player AV11/AV12 award branch before the same receiver handler, while the captured trap wrapper calls the trap builder and handler without a direct edge through that resolver [EV-0302]. This supports the shared static calculation and resolver-bypass submodel in M-0037 and M-0017.

Q-0042 partitions the 28 receiver-handler sites [EV-0303]: thirteen vtable slot-1 dispatches appear behind reference-count cleanup checks; seven mapped Actor/ActorMagicCaster sites are state/caster paths; one `Actor::UseSkill` call passes AV15 Sneak; three ActorValueOwner calls read Health or restore Stamina; and four source-reference `TESObjectREFR` calls are `AsExplosion`, `AsProjectile`, and `GetActorCause` access with bounded handle validation. No mapped site awards AV11/AV12 or directly returns to `FUN_1406bcaa0`. The release targets and possible derived source-reference overrides remain residuals, so this is not a whole-program or runtime no-award conclusion. Ten indirect sites remain in shared `FUN_1407ddf50`; Q-0043 ranks/traces those candidates for additional damage or armor-factor effects.

Cross-domain assessment: the DA04 level-gate/book path M-0036 shares no identified native call, HitData, AV39, armor/Block skill, ActiveEffect or serialization primitive with this route, so no OBJ-1 edge is added. PlayerCharacter AV39/factor values, positive effective armor protection, raw AVSK change, Steam mapping and vanilla level-one reproduction remain unobserved. Claim mapping: CL-L137 -> EV-0302; CL-L138 -> EV-0303; mechanism M-0037/M-0038.

### Shared HitData helper weapon input (Q-0043)

In GOG AE 1.6.1179.0, `FUN_1407ddf50` obtains a conditional target-actor ActorValue index from `HitData.weapon +0x194` and applies that value to `totalDamage`; this is a supported additional record-selected damage input on weapon-bearing routes [EV-0304]. The weapon attack-damage/AV66/AV9 values feed `percentBlocked`; AV163 feeds `criticalDamageMult`; and the MagicTarget invulnerability check can clear selected damage fields. Three remaining indirect sites are refcount-cleanup calls. The captured ProcessTrapHit builder supplies a null weapon pointer, so the two weapon-specific branches are skipped while the shared AV39/Actor slot-`0xE7` calculation remains [EV-0302], [EV-0304].

This adds no demonstrated armor-rating factor beyond the previously mapped AV39/slot-`0xE7` path and does not establish positive effective protection, raw AVSK, or Steam behavior. The DA04/Dawnguard/Ebony Warrior/DA08 quest gate records share no identified native call, ActorValue, HitData field, ActiveEffect or serialization primitive with this helper; no OBJ-1 causal edge is proposed. A same-build call/data edge linking this helper's weapon state or damage values to a quest-start Story Manager predicate would falsify the current no-edge assessment. Claim mapping: CL-L139 -> M-0039 [EV-0304].

### DA08 rumor helper and main-quest startup (Q-0044)

SMQN `000DC9E1` (`DA08KickerNode`) -> `GetLevel >= 20` -> helper QUST `000DC9E0` (`DA08RumorPointer`); main QUST `0004A37B` (`DA08`) separately serializes Start Game Enabled [EV-0300], [EV-0301], [EV-0305]. The helper fragment writes `PlayerGotRumor` on main DA08 and stops the helper, while the bounded main-QF fragment conditionally advances helper stage after main objective setup. Main-owned DA08 dialogue topics are present in the captured DIAL set. This supports a helper-only level-20 Story Manager path for main-Q startup, not an observed level-one dialogue or access route. INFO parent/condition coverage and live state remain unresolved. Claim mapping: CL-L140 -> M-0040.

Cross-domain assessment: DA08's quest flag, dialogue ownership, and helper rumor property have no identified shared call, ActorValue, HitData state, armor-skill writer, ActiveEffect, or serialization primitive with the OBJ-2 hit mitigation/XP paths [EV-0305], [EV-0217]–[EV-0223], [EV-0302]–[EV-0304]. No causal edge is added. A same-build state/call dependency or discriminating experiment linking quest startup to the armor/XP route would falsify this no-edge assessment.

### DA09 level-12 startup, Beacon placement, and stage callbacks (Q-0045)

SMQN `0009E1AD DA09IncreaseLevelNodeSHARES` -> `GetLevel >= 12` -> main QUST `0004E4E1 DA09` [EV-0300], [EV-0306]. The Update.esm override serializes `ENAM=LEVL` with Start Game Enabled clear under the EV-0301 schema mapping. The quest-owned Gem alias receives `DA09GemScript`; its player-container callback requests stage 100. The statue alias callback requests stage 200 if the player carries the Gem [EV-0306]. These are stage requests; the Steam behavior of `SetStage` on a stopped LEVL quest remains unobserved.

The separate CLOC helper QUST `00081C59 DA09ChangeLocation` -> SMQN `00081C5A` with a main-DA09 stage-0 condition and `DA09ChangeLocChance` global -> helper's BossContainer alias placement of the main quest's Gem alias [EV-0306]. This is downstream placement, not an identified pre-start route. The beam shooter requires main stage 300; Shade death requests stage 400; Update fix-up relocates the Gem alias under stage/location conditions. A full hash-verified Skyrim.esm group join covers 15,037 DIAL and 31,465 INFO records, mapping 20 DA09-owned DIALs and 25 INFO children with no function-80/GetLevel condition [EV-0306]. The five-master raw FormID screen reports no direct Beacon REFR/LVLI candidate and no interpreted external VMAD Start caller; dynamic/native callers, non-official plugins, other archives, profile winners, item availability, and runtime remain unknown.

Cross-domain assessment: no shared native call, HitData field, ActorValue, armor skill, ActiveEffect, or serialization primitive connects the DA09 quest/alias chain to M-0017/M-0033/M-0037 armor protection and XP mechanisms [EV-0306], [EV-0217]–[EV-0223], [EV-0292]–[EV-0297], [EV-0302]–[EV-0304]. No causal edge is added. Claim mapping: CL-L141 -> M-0041. A same-build data/call dependency would change this no-edge assessment.

### DA13 level-10 Refugee helper chain (Q-0046)

Serialized start path: `WEJS14 QUST 000BED92 (GetLevel >= 10)` -> `AfflictedRefugee` alias 39 INFO/TIF `000BECE9` -> WEJS14 stage 100 -> `Da13Intro` stage 1 -> intro scene -> helper stage 100 -> main DA13 `Start()` [EV-0307]. This bypasses the ordinary DA13 SMQN `000C4CC5` threshold of 12 in the prepared source, but does not establish level-one access or a live transition. The Empty Vessel stage-21 activator remains behind an Initially Disabled reference enabled only by the main quest's Kesh alias in the screened official records. Main-owned INFO `000A1A65` stage-21 availability while DA13 is stopped remains unresolved. No OBJ-1 to OBJ-2 causal edge is supported. Claim mapping: CL-L142 -> M-0042.

## Q-0047 — DA06 level-9 node versus Largashbur start paths

`SMQN 000A0E73` / `GLOB 000A0E71=9` selects main DA06 `QUST 0003B681`, whose Start Game Enabled bit is clear. Stage 0 enables the marker parented to the fixed giant; the hostile trigger only changes faction hostility. Atub INFO `0008E660` has an alias-ref condition and its TIF requests stage 50; death callbacks can request stage 255, but stopped-owner behavior remains unresolved. Thus no successful pre-level-9 start or progression is established, and the GOG event-scope trace is not Steam proof [EV-0272], [EV-0308]. Claim mapping: CL-L143 -> M-0043.

Cross-domain assessment: no shared call, HitData field, ActorValue, armor skill writer, ActiveEffect, or serialization dependency links DA06's quest/alias/faction path to OBJ-2 [EV-0308], [EV-0217]–[EV-0223], [EV-0302]–[EV-0304]. No causal edge is added.

## Q-0048 — Clothing-class armor rating versus hit XP selector

The five prepared official masters contain 36 unique positive-DNAM Clothing ARMO records with 56 resolved Clothing-class ARMA links [EV-0309]. GOG AE 1.6.1179.0's player receiver skips subtype 2 before selecting Heavy/Light AV11/AV12 [EV-0222]. The PlayerCharacter slot 0xE7 returns a cached factor at `this+0x274`, which the hit builder consumes [EV-0261], [EV-0309]. Its item-rating writers and Clothing contribution are not identified. This is a source-side candidate only; no effective protection, zero armor AVSK, or Steam result is established. Claim CL-L144 maps to M-0044.

Cross-domain assessment: Q-0048's ARMO type, cached armor factor, and hit receiver selector share an OBJ-2 path, but no identified same-build mechanism connects that path to OBJ-1 level-gated quest startup. Record no causal edge; a mapped same-build state or call dependency would falsify this assessment.

## Q-0049 — DA02 level-30 node, event helper, and book SetStage callback

Main DA02 QUST `0004D8D6` is selected by a level-30 Story Manager child; Start Game Enabled is clear. WEDA02's source conditions require main DA02 running at stage <1. The four fixed books are disabled below the level-30 global, while the `OnRead` callback still requests stage 1 for a quest below that stage. The callback's stopped-quest effect remains unknown. Generic book lists have minimum level 24, and the only source reference found for `QABooksContainer` is in QASmoke [EV-0310]. Claim CL-L145 maps to M-0045.

Cross-domain assessment: DA02's Story Manager predicates, WEDA02 event aliases, and book callbacks share no identified call, ActorValue, HitData field, armor-skill award, ActiveEffect, or serialization primitive with OBJ-2. No causal edge is added. A matched same-build call/data dependency or a source/runtime state field consumed by both routes would change this assessment.

## Q-0050 — BOD2 Armor Type, cached armor factor, and hit mitigation

`ARMO BOD2` serialized Armor Type at byte offset 4 -> GOG runtime `ARMO+0x1BC` via parser `FUN_140278170` -> inventory visitor `FUN_14072a500` excludes value 2 before adding item rating -> cache writer `FUN_140728b70` stores aggregate at PlayerCharacter `+0x274` -> PlayerCharacter slot `0xE7` returns the cache to the hit builder -> GOG hit damage calculation consumes the result [EV-0309], [EV-0311], [EV-0261]. This explains why the official positive-DNAM Clothing records found in EV-0309 do not contribute to this cached factor, even though the normal unblocked armor XP selector also skips subtype 2 [EV-0222].

The newly established edges remain within the OBJ-2 armor/data path. No shared call, ActorValue, state field, or serialization dependency connects them to OBJ-1 Story Manager or quest-start mechanisms. The GOG build is 1.6.1179.0; the installed Steam target is 1.6.1170.0 and has no matched live protection/AVSK capture. A same-build quest dependency would falsify the no-edge assessment; a Steam hit experiment is still required for the bounty.

Claim mapping: CL-L146 -> M-0046; Q-0050.

## Q-0052 — Physical-trap armor mitigation and hit-earned XP

`Skyrim.esm ARMO DNAM` -> GOG `FUN_140278170` runtime `ARMO+0x200` -> BOD2 type-0/1 visitor `FUN_14072a500` -> rating calculation `FUN_140223b20` plus Actor entry-point visitor selector `0x55` -> cached PlayerCharacter `+0x274` -> slot `0xE7` -> shared trap/ordinary hit mitigation helper `FUN_1407ddf50` [EV-0312], [EV-0311], [EV-0261], [EV-0302]. The trap wrapper bypasses the normal resolver `FUN_1406bcaa0` containing the known player AV11/AV12 branch [EV-0302]. The bounded receiver-handler census identifies no mapped AV11/AV12 award, but residual cleanup and derived-reference dispatch are unresolved [EV-0303], [EV-0304].

This supports a static OBJ-2 candidate only. It does not establish the named/effective role of selector `0x55`, an exhaustive no-award call graph, damage reduction, Steam code equivalence, raw AVSK, or vanilla level-one reproduction. No objective edge to OBJ-1 is justified. Q-0052 -> M-0047; claim CL-L147. Continue with an independent OBJ-1 engine question (Q-0053) while retaining the exact Steam hit/AVSK test and deeper receiver boundary as open P0 work.

## Q-0054 — Physical-trap handler cleanup and handle provenance

The fresh GOG `FUN_1406b9df0` census and generic helper traces in EV-0315 refine the 28-site receiver map: one temporary handle derives from receiver `param_1`, a second from HitData `+0x18`, and the HitData `+0x20` sourceRef is resolved separately. `FUN_140179540` and `FUN_1402ef8f0` are shared generic handle helpers, so the concrete cleanup target classes remain unknown. No mapped receiver site supplies AV11/AV12 to skill progress; the mapped cleanup, derived-reference, and runtime boundaries do not establish zero armor XP. This updates the OBJ-2 evidence under CL-L138/CL-L147 and M-0047 only.

Cross-domain assessment: no shared call, ActorValue, quest state, HitData field, ActiveEffect, or serialization dependency connects this trap receiver path to OBJ-1. No causal edge is added. Exact Steam 1.6.1170.0 repeated positive-damage hit, effective-protection, and raw AVSK capture remains the gameplay discriminator [EV-0260], [EV-0315].

## Q-0053 — Conditional Quest.SetStage startup path

Papyrus `Quest.Start` registration -> `FUN_140a48c50`; `Quest.SetCurrentStageID` registration -> `FUN_140a48aa0`; separate `Quest.SetStage` callback candidate -> `FUN_14034de90` [EV-0313]. On accepted states, SetStage can call the GOG-mapped `TESQuest::EnsureQuestStarted` in start-now mode, reach `BGSStoryTeller::BeginStartUpQuest`, process initialization/reference-promotion work, then look up and dispatch the requested stage. No explicit player-level check appears in the inspected callback path [EV-0272], [EV-0313].

The callback remains guarded by event-ID, ready-bit, and internal state. EV-0314 resolves the GOG/source bridge: DA02, DA09, and DA06 are serialized `ENAM=LEVL` cases, and the GOG QUST parser stores that field at `+0xE0`, where SetStage tests it. The exact ready-bit values and Steam field/runtime behavior remain unresolved [EV-0289], [EV-0306], [EV-0308], [EV-0310], [EV-0314]. Running state, alias completion, journal/dialogue, functional access, and a vanilla level-one transition are not established. Q-0053 -> M-0048; claim CL-L148.

Cross-domain assessment: this changes the OBJ-1 quest-start model only. No shared call, ActorValue, HitData field, ActiveEffect, armor-skill award, or serialization dependency links it to OBJ-2. Do not add a causal edge between objectives; pursue Q-0055 for the LEVL/runtime guard mapping and keep the exact Steam observer test open.

## Q-0055 — QUST ENAM to GOG SetStage guard field

TESQuest constructor default `+0xE0 = 0xFFFFFFFF` -> constructor-installed vtable slot 6 -> QUST parser `FUN_1403c7a50` `ENAM` reader writes four bytes to `+0xE0` -> direct source DA02/DA09/DA06 `ENAM=LEVL` cases -> registered SetStage entry predicate accepts only when ready bit `+0xDC.0` is set or event field `+0xE0 == -1` [EV-0314], [EV-0313], [EV-0310], [EV-0306], [EV-0308]. This supports initial-guard rejection for nondefault LEVL plus clear ready bit, and initial-guard acceptance when the bit is set. It does not establish actual target ready state, later startup, running state, aliases, functional access, Steam behavior, or level-one progression.

Q-0055 -> M-0049; claim CL-L149. Cross-domain assessment: the evidence changes the OBJ-1 serialized-field/guard map only. No shared native call, ActorValue, HitData field, ActiveEffect, armor-skill award, or causal serialization dependency with the OBJ-2 trap-hit path was identified, so no OBJ-2 edge is added.

## Q-0056 — Serialized QUST startup flag to the SetStage guard bit

`QUST DNAM.General.Flags` U16 bit 0 (`Start Game Enabled`) -> GOG TESQuest QUST parser `FUN_1403c7a50` -> `TESQuest+0xDC.0` at load -> registered GOG `Quest.SetStage` initial OR guard [EV-0316], [EV-0313]. Exact source DA04 flags set bit 0 (`0x0111`); DA02, DA06, and DA09 flags clear it (`0x0100`) [EV-0316], [EV-0301], [EV-0306], [EV-0308], [EV-0310]. The inspected constructor/helper add `0x0100` without setting bit 0. EV-0318 traces the GOG file-load chain: per-file record dispatch reaches TESQuest slot 6 with its record buffer, registers the parsed form by FormType, and then `FUN_1401bdf20` sweeps FormType arrays after the per-file loop. The sweep includes QUST `0x4D` and calls vtable `+0x98`, which is TESQuest slot 19 / `FUN_1403c8420`; that method can clear bit 0 [EV-0316], [EV-0318]. Thus post-parse load-finalization dispatch is supported for GOG, and the model that slot 19 runs only on later quest transitions is falsified. The first natural callback order remains a load-order inference; this does not establish target callback reachability, the field value at a natural callback, Steam behavior, stopped-quest startup, aliases, functional access, or a level-one transition. Claim CL-L150/CL-L151 -> M-0050, connected to M-0049's SetStage guard.

Cross-domain assessment: this adds a causal link within OBJ-1 between a serialized quest flag, its loaded native field, the post-file-load slot-19 dispatch, and the initial SetStage predicate. The edge to the first natural callback remains an ordering inference. No shared call, ActorValue, HitData field, ActiveEffect, armor-skill award, or serialization dependency connects that path to OBJ-2's incoming armor/XP route. No cross-objective edge is justified. Q-0057/EV-0318 resolves the GOG load-finalization dispatch component; Steam callback timing remains open.

## Q-0058 — ProcessTrapHit cleanup route and receiver teardown

On the captured GOG `FUN_140679da0` ProcessTrapHit route, HitData initialization clears `+0x18/+0x1C`; the builder stores the PlayerCharacter-derived handle at `+0x1C`, and neither helper writes `+0x18` [EV-0319]. Therefore the first handle-derived refcount cleanup at `FUN_1406b9df0` `0x1406BA047` is skipped on this route. The independent receiver handle at the second site `0x1406BA070` uses owner `+0x20`; PlayerCharacter's secondary-vtable slot `+0x8` reaches the common dispose thunk, then slot 0 and the PlayerCharacter teardown body. The teardown retains eight unresolved indirect sites [EV-0319], refining the generic handle provenance in EV-0315.

Cross-domain assessment: this updates the OBJ-2 builder/handle/cleanup path only. It does not resolve zero armor XP, effective protection, or Steam 1.6.1170.0 behavior, and no shared quest state, ActorValue, call dependency, ActiveEffect, or serialization primitive links it to OBJ-1. No cross-objective causal edge is added. Retain the Steam positive-damage / effective-protection / raw-AVSK test [EV-0260] and the unresolved teardown descendants.

Claim mapping: CL-L152 -> M-0047; Q-0058 [EV-0319].

## Q-0059 — First natural SetStage callback order

The GOG `FUN_1401b9510` load path completes its `FUN_1401bb4f0` per-file record loop before calling `FUN_1401bdf20` [EV-0318]. A second path, `FUN_1401be290`, also calls `FUN_1401bb4f0` for record processing and then `FUN_1401bdf20`; its sole analyzed direct code caller is `FUN_1403753b0`, which conditionally calls that loader after a file-path helper and then calls `FUN_1401bb490` [EV-0320]. Neither direct trace identifies a natural `Quest.SetStage` dispatch. The SetStage callback binding is table-based and still lacks indexed code xrefs [EV-0313]; the second wrapper also has only an unclassified data reference and no analyzed direct caller [EV-0320]. Thus the first natural callback order remains unresolved; absence of a direct call is inconclusive.

Cross-domain assessment: this refines the OBJ-1 load/finalization timing model only. No shared call, ActorValue, HitData field, ActiveEffect, armor-skill award, or serialization dependency links it to OBJ-2. No cross-objective causal edge is added. The exact Steam callback and quest-state observer plus level-one progression remain open [EV-0260]. Claim mapping: CL-L153 -> M-0050; Q-0059 [EV-0320].

## Q-0060 — Full official GetLevel census and DA03Start guard path

Five verified official source files contain 327 function-index-80 conditions across eight record signatures; the fixed official-source-layer view retains 320 [EV-0321]. The QUST winners occupy Story Manager and alias Match Conditions; one PACK and linked DIAL/INFO records add a concrete DA03Start guard-greeting path. Its package and INFO child both require player level at least 10 and DA03Start stage below 5. The QF method `Fragment_27` calls `DA03.SetStage(5)`, but no INFO-fragment link from the gated response is captured. Keep this as a guarded conversation path, not a universal DA03 start gate or level-one bypass.

This changes the OBJ-1 record-level progression map only. No shared native call, ActorValue, quest state, HitData field, ActiveEffect, armor-skill award, or serialization dependency connects the DA03Start conditions to OBJ-2. No cross-objective causal edge is added. Enumerate DA03Start's other DIAL/INFO topics, especially Lod's direct dialogue, before selecting an exact level-one transition test. Claim CL-L154 -> M-0051; Q-0060 [EV-0321].

## Q-0061 — Lod DA03Start handoff and reward callback

Lod alias 6 -> level-10 DIAL/INFO response -> DA03Start stage 10 -> QF Fragment_27 -> DA03 stage 5 [EV-0322], [EV-0323]. The independent unlevelled goodbye callback -> helper stage 20 -> gold reward/helper stage 200 -> helper stop; no DA03 main-quest call appears in that captured callback. This supports a level-gated direct handoff and helper-only unlevelled reward route in the fixed official source view. Runtime accessibility, full profile order, and level-one progression remain unknown. No edge to OBJ-2 is supported. Claim CL-L155 -> M-0052.

## Q-0062 — ProcessTrapHit versus inline armor skill routing

Physical trap records/scripts -> Papyrus ObjectReference.ProcessTrapHit -> PlayerCharacter FUN_140679da0 -> shared HitData population/resistance (including AV39 and armor-base-factor work) -> FUN_1406b9df0 [EV-0261], [EV-0293], [EV-0324]. The separate known FUN_1406bcaa0 path performs AV11/AV12 armor or AV9 Block skill routing through Actor slot 0xF7 before calling FUN_1406b9df0 [EV-0217]–[EV-0223], [EV-0324]. The trap path therefore bypasses that direct wrapper and has one visible downstream AV15 Sneak skill call. This is a static functional-armor/zero-armor-XP candidate, not a measured no-award outcome: 28 indirect call sites, positive final damage, effective protection, exact Steam behavior, and raw AVSK remain unresolved [EV-0260], [EV-0295], [EV-0315].

The new edge is confined to OBJ-2's trap-to-hit-builder-to-receiver path. No shared call, state, ActorValue, quest record, ActiveEffect, or serialization dependency connects it to OBJ-1; no cross-objective causal edge is added. Claim CL-L156 -> M-0053; Q-0062.

EV-0325 narrows the mapped receiver calls: the ActorValueOwner sites read base Health and restore Stamina damage; the PlayerCharacter cleanup body has no direct slot-0x7B8 call in its 108-edge census, but retains eight indirect sites. No edge to OBJ-1 is supported.

## Q-0063 — Dawnguard Fort dialogue to main-quest stage request

`DLC1VQ00` Start Game Enabled -> Durak INFO/TIF stages 20 and 50 -> `DLC1VQ01MiscObjective` stage 10 -> Isran 120/150 -> Tolan 180 -> helper QF `Fragment_16` -> `DLC1VQ01.SetStage(10)` -> main VQ01 Dimhollow objective/map marker [EV-0326]. This route is distinct from the level-10 SMQN Durak messenger helper and the separately level-gated approach INFOs [EV-0298], [EV-0299]. The serialized route supports an alternate-entry candidate; quest startup from stopped state, level-one dialogue availability, aliases, access, Steam behavior, and vanilla execution remain unknown. GOG `Quest.SetStage` startup tracing is separate-build evidence [EV-0313].

Cross-domain assessment: these quest records and callbacks expose no shared call, ActorValue, HitData field, armor-skill award, ActiveEffect, or serialization dependency with the OBJ-2 armor/XP route. No causal edge to OBJ-2 is added. A same-build state or call dependency would change this assessment. Claim CL-L157 -> M-0054; Q-0063.

EV-0327 adds two bounded OBJ-2 cleanup observations. PlayerCharacter primary slot `0x98` -> `FUN_1407373e0` reads/clears `+0x730`, may call nested slot `+0x1C0`, and releases through slot `+0x8`; the complete direct/computed scan found no non-null PlayerCharacter writer, leaving producer/type unknown. The teardown global slot-0 dispatch resolves through `PlayerCamera::vftable` to `FUN_1408e8b50` -> `FUN_1408e4070`, whose five indirect resource calls remain unresolved. These observations narrow Q-0064 but do not establish a no-award or positive-award result. Claims CL-L158 -> M-0055 and CL-L159 -> M-0056; Q-0064 remains active. No OBJ-1 edge is supported [EV-0327].

EV-0328 screens PlayerCharacter final-release candidate fields `+0x9D0`, `+0x9A8`, `+0x9A0`, and `+0x8F8` with complete direct/computed writer scans. The `+0x8F8` producer loads through path `Actors\Character\1stPerson\Skel` and teardown helper `FUN_140737210` clears/releases it; the object's runtime type and destructor target remain unresolved. Other same-offset hits and the shared `FUN_140744xxx` cluster need receiver provenance. This narrows, but does not decide, Q-0064. Claim CL-L160 -> M-0057. No edge to OBJ-1 is supported [EV-0328].

EV-0329 maps PlayerCharacter teardown fields +0x9A0/+0x9A8 to refcount-final virtual slot +0x8 calls and traces a shared setter plus a resource-derived non-null value producer. The related FUN_140744180 helper path uses exact primary PlayerCharacter vtable accessors for +0x8F8/+0x8F0. EV-0344 resolves the setter's DAT_143188918 receiver as a PlayerCharacter construction path; the stored resource object's class/finalizer remains unresolved, so no edge to Actor::UseSkill or AV11/AV12 skill progress is added or excluded. Claim CL-L161 -> M-0058; Q-0064 remains active. No edge to OBJ-1 is supported [EV-0329], [EV-0344].

EV-0330 maps the AutoVanity state callback to queued HUD message type 0x17, the registered HUDMenu slot+0x20 handler, and Scaleform ShowElements. The exact native branch has no Actor skill-progress sink and does not take its optional native callback. This is one bounded PlayerCamera callback branch; it adds no edge to AV11/AV12 skill progress and does not resolve Q64-H1/H2. Claim CL-L162 -> M-0059; no edge to OBJ-1 is supported [EV-0330].

EV-0331 maps the GOG NiNode parser and a conditional NiNode finalizer chain for PlayerCharacter +0x8F8's resource path. The exact NIF root and subtree remain unobserved; child +0x8 finalizers and a NiAVObject slot+0x128 callback remain dynamic. No edge to AV11/AV12 skill progress or OBJ-1 is added. Claim CL-L163 -> M-0060 [EV-0331].

EV-0332 narrows a candidate PlayerCharacter +0x9D0 store to a TES-owned cell/resource query and metadata fallback. The exact stored-object vtable and finalizer remain unknown; no edge to AV11/AV12 skill progress or OBJ-1 is added. Claim CL-L164 -> M-0061 [EV-0332].

EV-0333 advances the candidate +0x9A0/+0x9A8 producer through a data-selected model resource and FUN_140d19980's unresolved +0xB8/+0xE8 adapter. The loaded root class and final slot+0x8 callback remain unknown. Armor-hit and enchanting producers share the Actor::UseSkill sink through separately mapped routes [EV-0217]–[EV-0223], [EV-0280], [EV-0281]; no shared call/data edge from this cleanup producer is established, so no causal edge is added and transitive reachability remains unresolved. The mapped Dawnguard Fort route has no observed ActorValue dependency [EV-0326]. Claim CL-L165 -> M-0062 [EV-0333].

EV-0334 connects PlayerCharacter +0x730 cell transitions to a candidate NiAVObject/NiNode parent-child lifecycle: add stores the parent at child+0x30; removal detaches the child from the parent and releases refs. The exact parent vtable and child finalizer remain data-dependent, so this branch does not exclude a destructor descendant reaching skill progress. EV-0331's +0x8F8 NiNode remains conditional, and EV-0333's +0x9A0/+0x9A8 model resource has no mapped vtable; common class/finalizer identity is a new testable hypothesis, not an established edge. No causal edge to Actor::UseSkill AV11/AV12 or OBJ-1 is added [EV-0334], [EV-0331], [EV-0333]. Claim CL-L166 -> M-0063.

EV-0335 identifies PlayerCamera+0x28 as an active-state interface and maps the index-9 ThirdPersonState slot+0x10 callback to camera-field reset and conditional helper/refcount work. This is structurally distinct from the +0x730 scene-child candidate [EV-0334] and the +0x8F8/+0x9A0 resource-release candidates [EV-0328], [EV-0329], [EV-0331], [EV-0333]. EV-0330 separately maps an AutoVanity callback to a HUD branch. Do not infer a shared cleanup class or a global no-skill result: the teardown-selected state, other state tables, helper descendants, and nested finalizer are unresolved. No causal edge to Actor::UseSkill AV11/AV12 or OBJ-1 is added [EV-0335]. Claim CL-L167 -> M-0064.

EV-0336 expands the PlayerCamera cleanup model: ThirdPersonState+0xA0 receives a value from PlayerCharacter vtable+0x378 followed by a dynamic slot+0x150 lookup. NiNode's slot+0x150 recursively searches child nodes, making a shared NiAVObject path with the +0x730 scene child [EV-0334] and conditional +0x8F8 skeleton [EV-0331] testable. The receiver vtable is not mapped, so no edge to NiNode is drawn; +0x9A0/+0x9A8 remain separate data-selected model resources [EV-0333]. No causal edge to Actor::UseSkill AV11/AV12 or OBJ-1 is added. Claim CL-L168 -> M-0065.

EV-0337 maps the PlayerCharacter +0x378 flag-zero getter to a TLS/nested-field context accessor. This improves source provenance for the ThirdPersonState+0xA0 named-object candidate [EV-0336], but the selected object class, slot +0x150 target, and member finalizer remain untyped; the NiNode comparison stays conditional. `FUN_1402e55a0` has no outgoing calls, which adds no edge to Actor::UseSkill AV11/AV12 and does not exclude downstream dispatch. The +0x68/+0x5F0 scans are broad or fail to expose the TLS-indexed writer. No causal edge to OBJ-1 is added. Claim CL-L169 -> M-0065.

EV-0338 maps FirstPersonState and BleedoutCameraState slot+0x10 targets under the PlayerCamera transition interface [EV-0335]. FirstPerson performs a field clear and array update; Bleedout releases a +0x120 member through a dynamic finalizer and runs playback/event helpers. These are distinct per-state cleanup branches; the selected state, Bleedout finalizer, and further descendants remain open. No causal edge to Actor::UseSkill AV11/AV12 or OBJ-1 is added. Claims CL-L170 and CL-L171 -> M-0064.

EV-0339 maps FreeCameraState and IronSightsState slot+0x10 callbacks under the PlayerCamera transition interface [EV-0335]. FreeCamera's `FUN_140cd7210` descendant only stores two fields; IronSights' callback is a no-op. These branches add no direct edge to Actor::UseSkill AV11/AV12, while the shared array helper, other state callbacks, and state selection remain unresolved. No edge to OBJ-1 is added. Claims CL-L172 and CL-L173 -> M-0064.

EV-0340 maps FurnitureCameraState slot+0x10 to a handle-derived float/update path with a nested dynamic finalizer. PlayerCameraTransitionState shares the no-op FUN_140244650 target with IronSightsState [EV-0339]. No direct AV11/AV12 edge is added; Furniture's finalizer, remaining state callbacks, and teardown selection remain unresolved. No edge to OBJ-1 is supported. Claims CL-L174 and CL-L175 -> M-0064.

EV-0341 resolves PlayerCamera state indices 2, 7, 10, and 12 and maps their slot+0x10 callbacks. Horse and Dragon share a helper that releases a +0xA0 member through an unresolved virtual slot+0x8 finalizer. No direct AV11/AV12 sink or causal edge to Actor::UseSkill or OBJ-1 is supported; ProcessTrapHit state reachability remains unknown. Claims CL-L176 and CL-L177 -> M-0064.

EV-0342 establishes a structural path: PlayerCharacter slot+0x378 result -> virtual slot+0x150 result -> ThirdPersonState+0xA0 -> refcounted virtual slot+0x8 cleanup. These are GOG AE 1.6.1179.0 source links. The returned type/finalizer and any connection to ProcessTrapHit remain unsupported; no causal edge to Actor::UseSkill or OBJ-1 is added. Claims CL-L178 and CL-L179 -> M-0064.

Cross-domain synthesis (2026-10-18): the OBJ-1 Fort dialogue route to a VQ01 stage request [EV-0326] and the OBJ-2 trap/camera cleanup chain [EV-0325], [EV-0342] have no shared native call, ActorValue, HitData, or quest-readiness edge in captured evidence. Their possible interaction is unsupported. For Q-0065, the +0xA0 slot+0x150 return remains only analogous to NiNode child lookup; matching concrete vtables and slot+0x8 finalizers would support a common family, while a distinct vtable/finalizer would falsify it. No OBJ-1/OBJ-2 causal edge is added.

EV-0343 shows that the slot+0x150 argument is copied with a refcounted pointer header; this is compatible with a named-child lookup and NiNode's recursive same-slot behavior [EV-0336]. The actual receiver vtable and result class remain unmatched, so Q65-H1 is not promoted and no causal edge to Actor::UseSkill or OBJ-1 is added. A different concrete slot+0x150 table would falsify the NiNode-family hypothesis. Claim CL-L180 -> M-0065.

EV-0344 resolves the FUN_1408e6500 slot +0x378 receiver as the PlayerCharacter global and its wrapper as entry 1 of AnimatedCameraStartHandler::vftable. The flag-zero result selects TLS +0x5F0 when its +0x5F8 owner matches the PlayerCharacter, or a nested +0x68/+0x68 path. This narrows the source but leaves the slot +0x150 receiver/result class, finalizer, and ProcessTrapHit reachability unknown; neither Q64 hypothesis is resolved and Q65's NiNode comparison stays conditional. No edge to Actor::UseSkill or OBJ-1 is added. Claims CL-L181/182 -> M-0065.

EV-0345 maps paired AnimatedCamera callback wrappers into FUN_1408e6500 with flags 0/1 and identifies their base interface as IHandlerFunctor<Actor,BSFixedStringCI>. The fixed-string type shape is compatible with named lookup but does not establish a NiNode receiver or connect this path to ProcessTrapHit or Actor::UseSkill AV11/AV12. Q64-H1/H2 and Q65-H1/H2 remain unresolved. Claim CL-L183 -> M-0065; no causal edge is added.

EV-0346 supplies the local contexts missing from EV-0325: the five late FUN_14072fd60 calls release fields +0x9D0, +0x9A8, +0x9A0, +0x8F8, and +0x730 through dynamic slot +0x8 when each refcount reaches its final release. Combined with the first three callsite contexts in EV-0325/0327, all eight sites are field/interface-mapped, but none of the five new object finalizer tables is concrete. EV-0344 resolves the shared global receiver class without resolving stored resource types. No edge to AV11/AV12 or OBJ-1 is added; Q64-H1/H2 remain proposed. Claim CL-L184 -> M-0066 [EV-0346].

EV-0347 ties PlayerCharacter+0x8F8 to the named first-person skeleton resource and generic mesh loader; this strengthens the source-path side of EV-0331's conditional NiNode candidate but does not establish a concrete NIF root or destructor table. The exact +0x8 finalizer descendants remain untyped, so no edge to Actor::UseSkill AV11/AV12 is added or excluded. The separate +0x730 cell-scene branch remains mapped only to a cell-transition child candidate [EV-0334], while +0x9D0 and +0x9A0/+0x9A8 retain data-selected producer gaps [EV-0332], [EV-0333]. Claim CL-L185 -> M-0067; Q64-H1/H2 and Q65-H1/H2 remain unresolved.

EV-0348 bounds the +0x9D0 metadata fallback to key-2/key-1 descriptor-table lookups that return data-selected 64-bit values. Neither helper body provides a concrete finalizer or Actor::UseSkill edge, so Q64-H1/H2 remain unresolved and no no-skill edge is added. The independent +0x9A0/+0x9A8 model-resource path remains the next static discriminator [EV-0333]. Claim CL-L186 -> M-0068.

EV-0349 maps the candidate +0x9A0/+0x9A8 model path through FUN_140d19980's dynamic +0xB8/+0xE8 adapter and FUN_140d27eb0's sorted-name array. The +0x8F8 path instead calls its root's slot +0x150 [EV-0347]; these use-site differences do not establish different concrete classes or a shared NiNode family. The finalizer/AV11/AV12 relationship remains unresolved. Claim CL-L187 -> M-0069; no causal sink edge is added.

EV-0350 maps the candidate +0x9A0/+0x9A8 setter's mode-selected fields and dynamic refcount-final slot +0x8. One caller passes the model-resource output traced in EV-0349/EV-0333, but the object class and descendants remain data-selected. No edge to Actor::UseSkill AV11/AV12 is resolved or excluded. The next independent branch is the +0x730 cell-scene child source. Claim CL-L188 -> M-0070.

EV-0351 confirms the +0x730 cell-transition helper reads a data-selected pointer at receiver+0x130+8. Existing evidence does not identify an attributable non-null writer or the selected object's vtable, so the scene child finalizer remains unresolved and no AV11/AV12 edge is added. The next bounded branch is the typed PlayerCamera global finalizer. Claim CL-L189 -> M-0071.

EV-0352 links the PlayerCamera global used in the ProcessTrapHit cleanup census to a factory-installed table and deleting-destructor path. The owner is identified, but its five child dispatches remain data-dependent, so no AV11/AV12 edge is added. Claim CL-L190 -> M-0072; Q64-H1/H2 remain unresolved.

EV-0353 resolves PlayerCamera+0x128 to a constructed bhkRigidBody and its slot+8 deleting-destructor chain. The body destructor exposes a child-array slot+8 frontier, so this result narrows one owned-object class without resolving Q64-H1/H2 or adding an AV11/AV12 edge. Claim CL-L191 -> M-0073.

EV-0354 narrows the PlayerCamera rigid-body branch: the +0x28 child pointer and +0x38 count initialize to zero, so the first slot+0x150 cleanup loop has no entries. This is an initial-state result only; later producers remain open and no AV11/AV12 edge is added. Claim CL-L192 -> M-0074.

EV-0355 adds a source-backed edge from FUN_1406b9df0 through FUN_1407c9980 and FUN_140e962d0 into recursive rigid-body constraint handling. The resolved descendants manipulate physics constraints and resources; no edge to AV11/AV12 skill credit is established. Claim CL-L193 -> M-0075.

EV-0356 narrows the ProcessTrapHit constraint-helper branch: the factory-created hkpConstraintInstance's slot +0x30 returns zero, so its conditional list-removal path is skipped [EV-0355]. Cross-domain synthesis: EV-0326's five-master Dawnguard Fort stage-request route and EV-0356's GOG ProcessTrapHit physics branch have different provenance and no supported shared call/state dependency. Status: no causal edge established; falsifier: a direct shared native call, state-bearing field, or discriminating same-build event trace. Claim CL-L195 -> M-0076; CL-L194 records the bounded no-edge result.

EV-0357 extends the bounded ProcessTrapHit physics path from FUN_140b3a830's refcount release to the factory-created hkpConstraintInstance slot-0 deleting destructor. Its mapped direct body performs callback/member cleanup and TLS allocator release; callback slot +0x18 and embedded member finalizers remain dynamic. No edge to AV11/AV12 is established, and no new edge to the EV-0326 quest route is supported [CL-L194], [CL-L196].

EV-0358 maps the hkpConstraintInstance callback consumer and bounds its direct callers, while exact callback population remains unresolved. The +0x40/+0x48 scan candidates include other receiver layouts and add no causal edge to Actor::UseSkill AV11/AV12 or to the EV-0326 Dawnguard quest route [CL-L194], [CL-L197].

EV-0359 distinguishes the chain-instance cleanup override from the base hkpConstraintInstance factory class and identifies potential island/entity and command-queue carriers. It adds no causal edge to Actor::UseSkill AV11/AV12 or to the Dawnguard quest candidate until exact object membership is proven [CL-L194], [CL-L198].

EV-0360 establishes the exact ProcessTrapHit-created hkpConstraintInstance -> FUN_140e860d0 -> FUN_140b3a710/FUN_140b43a20/FUN_140b678a0 -> entity constraint-record edge. It also links attachment to the existing add-callback consumer, but no callback producer/target or AV11/AV12 edge is established [CL-L199].

EV-0361 adds direct caller and callback-slot context for the hkp add/remove dispatch path. It does not establish a producer-backed listener or any causal edge to Actor::UseSkill AV11/AV12 [CL-L200].

EV-0362 corrects the EV-0359 adjacent-byte class label to `hkpSimulationIsland` and maps its entity/constraint serializer. This correction adds no edge from the exact ProcessTrapHit instance to EntityPtrs/ConMstPtr or to Actor::UseSkill AV11/AV12; membership remains unresolved [CL-L198], [CL-L201].

EV-0363 withdraws the EV-0362 +0x60/+0x68 writer negative because the access lists were capped at 2,048 lines before the physics functions. No causal edge to ProcessTrapHit owner membership or AV11/AV12 is added [CL-L202].


EV-0364 corrects EV-0360: constraint +0x10 copies endpoint +0x130; endpoint +0x100/+0x108 stores records, with instance +0x60 pointing back. Typed island initialization, EntityPtrs serialization, insertion and merge support this owner relation [CL-L203], [CL-L204], [M-0083]. Live membership and AV11/AV12 are unresolved. No causal edge to OBJ-1 is supported.


EV-0365 rejects one +0x40/+0x48 alias as a callback producer: FUN_140b91bb0 writes those offsets on constraint-data payload stored at instance +0x18. The ProcessTrapHit constructor path initializes the exact callback fields empty, then invokes wrapper slots +0x128/+0x188. No skill-progress or OBJ-1 causal edge is established; resolve those exact wrapper targets next [CL-L205], [M-0084].


EV-0366 narrows the ProcessTrapHit hkpConstraintInstance setup route: fixed/malleable wrappers share pointer-setter and observer methods, store an instance +0x58 backlink, and update reference counts without directly writing callback fields +0x40/+0x48. Both mapped constructors start the callback pointer/count empty. The displacement scans are broad and receiver ambiguous; the decompiled +0x48 store in FUN_140b91bb0 comes from a 16-byte vector copy beginning at +0x40. No edge to Actor::UseSkill AV11/AV12 is established; inspect exact vtable methods next [CL-L206], [M-0085].


EV-0367 adds a concrete callback edge: hkpConstraintInstance slot-0 finalization -> FUN_140b487e0 -> FUN_140b674a0 -> each non-null callback entry slot +0x18 with the instance pointer; null entries are compacted and callback storage is later freed. Entry class, producer and Actor::UseSkill AV11/AV12 descendants are not identified, so no edge to armor skill progress is added [CL-L207], [M-0086].

EV-0368 adds a bounded lifetime edge: constructor count 1 -> wrapper retain to 2 -> factory temporary release to 1, with no slot-0 deletion callback on that handoff. Later terminal release and callback producers remain unresolved. No edge to AV11/AV12 or the OBJ-1 Story Manager gate is supported [CL-L208], [M-0087].

EV-0369 classifies six hkp-region +0x40/+0x48 candidates as curve or constraint-data receiver paths, not the exact hkpConstraintInstance callback array. No edge to the callback entry slot +0x18 consumer or AV11/AV12 sink is added. The complete candidate intersection has 1,271 functions and remains open [CL-L209], [M-0088].

EV-0370 maps two hkpConstraintChainInstance phases over its inherited callback array: removal slot +0x20 -> FUN_140b439e0 -> FUN_140b67350 -> entry slot +0x10; slot-0 finalization -> FUN_140b5d520 -> base FUN_140b487e0 -> FUN_140b674a0 -> entry slot +0x18. No callback producer, skill sink, or ProcessTrapHit owner edge is established [CL-L210], [M-0089].

EV-0371 adds bounded GOG call and pointer-window evidence for the hkpConstraintChainInstance factory. Because neither an exact owner nor a ProcessTrapHit call edge is identified, it adds no causal edge between the chain helper and the ProcessTrapHit cleanup path; keep the relationship unresolved [CL-L211], [C-OBJ2-Q64-CHAIN-OWNER].

EV-0372 classifies FUN_140b48150's +0x40 access as a 16-byte vector write on separate 0xe0-byte constraint-data storage, which hkpConstraintInstance retains at +0x18. The candidate adds no edge to callback registration or AV11/AV12 [CL-L212].

EV-0373 classifies FUN_140b49260's +0x40 access as a vector in a tagged 0x50-byte record passed to a typed-list manager. It adds no causal edge from this record path to hkpConstraintInstance callback storage, ProcessTrapHit teardown or AV11/AV12 [CL-L213].

### P0 cross-domain synthesis — DA04 and physical-trap armor XP (EV-0374)

DA04 book-read stage transition [EV-0301] and ProcessTrapHit HitData mitigation/skill routing [EV-0261, EV-0324] remain a **bounded no-edge** in the mapped evidence. No shared call, ActorValue, HitData field, constraint callback owner, or serialized state is identified [CL-L214]. Generic event/callback vocabulary is analogy only. This assessment is falsified by an exact common call/data dependency or a controlled clean runtime result showing DA04 stage state changes trap mitigation or raw AVSK. The physical-trap route remains the strongest static OBJ-2 candidate, while DA04 remains an independent OBJ-1 low-level-start candidate. EV-0370–EV-0373 do not identify a callback producer/target; Q-0064 continues at the PlayerCharacter +0x8F8 resource finalizer.

### ProcessTrapHit constraint removal branch (EV-0375)

The factory-created hkpConstraintInstance reaches the mode-1 removal path through FUN_140b3a830/FUN_140b43ab0. FUN_140b67350 dispatches any non-null callback through its entry slot +0x10; FUN_140b67d60 removes the instance from its endpoint record. The callback class, writer and concrete target remain unresolved [CL-L215]. The mapped direct cleanup adds no Actor::UseSkill AV11/AV12 edge; no global negative or causal edge to OBJ-1 is supported.

### Q64 listener add helper no-edge rationale (EV-0376)

No causal edge is added from FUN_140b56a80 to the ProcessTrapHit manager or the AV11/AV12 skill-progress sink: the bounded direct-call census has no incoming caller, and its two raw DATA references identify no executable consumer. This is a bounded absence of an identified edge, not proof that dynamic invocation is impossible [CL-L216].

### Q64 slot +0xB8 callsite no-edge rationale (EV-0377)

No edge is added from FUN_140b66f40 to the ProcessTrapHit manager. The displayed candidate calls do not identify hkpWorld slot 23 or the manager argument; the +0xB8 scan's 2,048-row output cap leaves other callsites unknown [CL-L217].

### Q-0065 class-family comparison boundary (EV-0378)

The exact ProcessTrapHit physics tables are distinct from the NiNode parser candidate, but no source edge identifies those tables as the producer of the PlayerCharacter or ThirdPersonState cleanup values. Keep the class-family edges among those values unresolved: common slot +0x8 release behavior does not prove shared type. No direct Actor::UseSkill AV11/AV12 edge is added for the bounded descendants; unresolved resource/finalizer targets prevent a route-wide negative. No causal edge to OBJ-1 is supported [CL-L218].

### Q-0066 VQ01 conditional startup (EV-0379–EV-0382)

Source route: Fort Dawnguard VQ00 dialogue helper -> VQ01.SetStage(10) [EV-0326]. GOG static route: SetStage callback -> EnsureQuestStarted(start-now) -> state/ref/alias preflight -> BeginStartUpQuest only when accepted -> requested stage processing [EV-0313, EV-0380, EV-0382]. VQ01's no-ENAM record and constructor defaults pass the observed initial guard [EV-0379, EV-0381]. Keep the preflight-to-successful-start and startup-to-functional-access edges unresolved; no level-one Steam runtime capture exists. No causal edge to OBJ-2 is supported [CL-L219, CL-L220].

## Q-0067 — DA05 Ill Met by Moonlight

Fixed official-five-master QUST/Story Manager exports and a source-hash-verified Skyrim.esm group join find no GetLevel condition in DA05 QUST 0002A49A, location node 0005D331, the 38 DA05-owned DIALs/51 linked INFOs, or the 30 INFOs with a direct DA05 reference [EV-0384, EV-0385, EV-0214]. UESP revision 3628445 names Mathies/Sinding but supplies no ReqLevel field [EV-0383]. Keep this as a bounded no-level-gate result; the fixed source scope is not a profile winner and no clean level-one dialogue/progression result exists [EV-0260]. The separate grotto INFO 00095585 TIF sets its TopicInfo-owning helper QUST 000955CF to stage 20; helper Fragment_2 kills alias Hunter00_JKier and requests main DA05 stage 60, while the TIF separately sets DA05.PlayerTalkedToHunter [EV-0391, EV-0393, CL-L226]. Availability and fresh-state startup remain unresolved. No shared native call, ActorValue, HitData field, callback owner, or serialization edge to the OBJ-2 armor XP path is supported [CL-L221].


## Q-0068 — WE13 troll-cave event gate

Mechanism M-0092 maps both Story Manager event branches. Each selects WE13 QUST 0009F32F, whose top-level GetLevel condition is >= LevelGateTrollCave (12) [EV-0387], [EV-0321]. The fixed five-master exact-reference screen and the four tested linked PEX files identify no independent direct start/stage writer within their scope [EV-0388], [EV-0390], [CL-L224]. The 167 direct REFR WETriggerScript source records resolve to 158 logical refs; their event keywords and persistence flags describe dispatch sources, not loaded state or cave access [EV-0389], [EV-0275], [CL-L225]. Keep global bypass and physical access unresolved; Q-0070 retains the exact level-one test, while Q-0069 is the next ready static question [EV-0260]. No OBJ-1/OBJ-2 edge is justified because no shared native call, ActorValue, HitData field, callback owner, or serialized state connects WE13 scheduling to armor XP [CL-L223].


## Q-0069 — corrected Grotto helper dialogue route

INFO 00095585 belongs to helper QUST 000955CF through DIAL 00095582 and requires alias 57 on Subject [EV-0391]. The TIF calls its owning helper quest SetStage(20), not main DA05.SetStage(20); helper Fragment_2 kills the Hunter alias and requests main DA05.SetStage(60), while the separate DA05 property marks PlayerTalkedToHunter [EV-0393]. The mapped ordinary route is main DA05 stage 50 -> helper stage 10; fixed-source census and placed trigger checks support that route but do not establish exclusivity [EV-0392], [EV-0394], [CL-L222], [CL-L226], [CL-L227], [M-0093]. Retain a clean level-one pre-stage-50 dialogue test as Q-0071; reopen Q-0070 for static physical cave/door mapping before its exact runtime discriminator [EV-0260]. No OBJ-1/OBJ-2 edge is supported.


## Q-0070 — WE13 event anchor versus physical cave

The fixed-five-master WE13 QUST export shows an event-filled `TRIGGER` reference alias and `myHoldLocation` location alias, WETravel linked-reference child markers, and `EncTroll` creation at `TravelMarker1`; it names no fixed cave location, interior cell, or entrance door [EV-0395], [CL-L228], [M-0094]. Local UESP revision 3526243 describes trolls across wilderness, caves, and Dwarven ruins, and uses “cave trolls” generically [EV-0396], [CL-L229]. This narrows the meaning of `LevelGateTrollCave`: it is the level-12 predicate on the mapped encounter selection path, not evidence of a fixed door gate [EV-0321], [EV-0387]. The clean level-one event test remains open under EV-0260 and is retained as Q-0072. No physical traversal, quest startup, alias fill, spawn, profile winner, or OBJ-1/OBJ-2 causal edge is established.


## Q-0073 — Hit resolver caller scope

GOG AE 1.6.1179.0 caller map: `FUN_140659160` case 0xB -> `FUN_1406bb690(Actor, byte, byte)`; callback worker `FUN_14065b800` reaches the dispatcher when its callback does not consume the event. A separate `FUN_1407ba3e0` route requires Actor slot 0x99 to return false and a current-process target pointer match; it has no analyzed incoming direct caller. The repeated pointer table places it at entry 1, but its adjacent non-function data target has no decoded type/owner [EV-0397]. The worker query lists 95 direct callers; a fresh capture confirms the exact set and decompiles 33 bodies. The reported 64 caller functions is the implementation's storage cap, leaving 62 exact bodies uninspected. No tag-0xB constructor occurs in the decompiled subset [EV-0423]. `FUN_1406bb690` calls `FUN_1406bcaa0` twice. This supports two bounded event/state routes into M-0017, not a complete ordinary-hit call map [CL-L230], [M-0095].

Cross-domain assessment: M-0017/EV-0261 places mitigation before blocked-hit routing and EV-0222 maps blocked hits to AV9 rather than AV11/AV12. Q-0073 does not establish ordinary enemy-hit coverage, Steam equivalence, effective protection, AVSK deltas, or a vanilla exploit. No causal edge to OBJ-1 is justified. Preserve the exact live comparison in Q-0004/EXP-0017 under EV-0260; the event producer and table owner remain unresolved.


## Q-0074 — Clothing magic/element resistance candidate

Record path: Skyrim.esm Clothing ARMO 000FC061 -> ENCH 000FC05B -> constant/self MGEF 000B7A35, a Peak Value Modifier to AV44 [EV-0398, CL-L231]. Health MGEF records include Fire/Shock/Frost ResistValues AV41/42/43 [EV-0399, CL-L232]. In GOG AE 1.6.1179.0, RTTI resolves the Actor `MagicTarget` vtable at subobject offset 0xA0; slot 0x0A maps to `FUN_1406c45a0`, which reads target resistance ActorValues and incoming-effect ResistValue before a residual-factor helper [EV-0400, EV-0401, EV-0402, CL-L233, M-0096]. This is a distinct source/code protection candidate outside the type-2 Heavy/Light selector [EV-0222, EV-0261]; the physical cached armor-factor route remains unresolved [EV-0311].

Cross-domain assessment: Q-0074's ActorValue and magic-target path does not share a captured quest-start call, quest state, HitData route, or serialization field with Q-0071/Q-0072. No causal edge to OBJ-1 is justified. Level-one acquisition, live Steam damage reduction, qualifying hit, and numeric AVSK remain unresolved under EV-0260.


## Q-0075 — Clothing resistance item acquisition screen

Official-master records place Arch-Mage boots ARMO `0007C92E` through fixed REFR `00077D05` in owned CELL `000CAB92`, with a Shock Resist AV42 magnitude-40 effect and zero physical `DNAM` rating [EV-0403], [EV-0404], [CL-L234]. A separate Riverwood Trader leveled-list chain can produce Resist Magic ring `0010DFC8` at level 1 but has a 25% parent chance-none and is not a guaranteed stock result [EV-0405], [CL-L235]. UESP's revision-captured room lock/quest sequence is secondary grounding only; suggested level 6 is not a proven minimum and physical level-one entry remains unobserved [EV-0406], [EV-0260].

The fixed source falsifies the no-fixed-record-source model, but does not establish deterministic level-one acquisition. This is an item-source dependency on the College route, not a causal engine edge between OBJ-1 quest initiation and the M-0096 magic resistance path or the physical armor XP selector. Keep live access, protection and AVSK separate.

## Q-0076 — College/Under Saarthal direct level-condition screen

The exact MG01/MG02 Skyrim.esm QUST records and the complete exact-five-master GetLevel census have no matching direct `GetLevel` CTDA [EV-0321], [EV-0407]. The 96/69 QNAM-linked DIAL topics and 159/103 INFO children have no function-index-80 condition [EV-0409], [CL-L236]. The complete Story Manager level-node map selects no MG01/MG02 child [EV-0300]. The quarter entry endpoints require CollegeArchMageKey; Tolfdir's MG02-stage-200 topic carries the TIF fragment that adds the key and robe to the player [EV-0410]–[EV-0413], [CL-L237]. The captured MG01/MG02 and dialogue PEX bodies call no `GetLevel`; QF_MG01 starts MG02 and QF_MG02 locks its ArchMageDoor properties [EV-0413], [CL-L238]. This supports the source-level stage/key mechanism M-0097, not a level-one bypass. The exact quest-variable operand, some fragment/door property bindings, profile winner, room entry and theft legality remain unresolved [EV-0260].

Cross-domain assessment: no shared native call, ActorValue, HitData field, or serialized state links this College route to M-0009's incoming armor XP selector or M-0096's resistance calculation. No OBJ-1/OBJ-2 causal edge is supported.


## Q-0077 — Savior's Hide, resistance, and the armor-XP selector

Source chain: DA05 QUST `0002A49A` stage 100 / `Fragment_20` -> `AddItem(SaviorsHide, 1)` -> Skyrim.esm ARMO `0002AC61` (Light type, DNAM 2600) -> ENCH `001097B7` -> Resist Magic AV44 magnitude 15 and Resist Poison AV40 magnitude 50 [EV-0415], [EV-0416]. This is a serialized reward/effect edge, not proof of a natural level-one grant or measured damage reduction.

Claim links: CL-L239 and CL-L240 extend the source-item and enchantment-record nodes in M-0096. These source/effect links do not add a causal edge to M-0009 or OBJ-1.

Separate build-specific paths: GOG PlayerCharacter `UseSkill` slot `0xF7` ignores non-positive points [EV-0417]; the bounded `physicalDamage`/HitData builder searches and caller maps do not identify a magical producer into that selector [EV-0418]–[EV-0420]. GOG `MagicTarget::CheckResistance` reads resistance ActorValues at a virtual method, but the fresh census found no direct code xref/callsite [EV-0421]. These endpoints remain unconnected. A live qualifying hit with controlled protection and raw AVSK data is still required [EV-0260].

Cross-domain assessment: the DA05 reward is related to the source item, while the item's resistance effect and the armor XP selector have no demonstrated shared call, ActorValue, HitData field, or serialized transition. No OBJ-1/OBJ-2 causal edge is added. A captured magic-only hit that never invokes AV11/AV12 would falsify the suppression interpretation, not prove it.


## Q-0078 — MS06 level-10 Story Manager and helper note route

Source route: SMQN `000D91D2 MS06IncreaseLevelNodeSHARES` selects main MS06 QUST `00026C4D` at the level-10 global threshold. The separate start-enabled helper MS06Start reaches a stage-5 appeal scene that advances its own helper quest to stage 10; helper stage 10 stages MS06Rumor to 20. This helper scene chain does not directly stage main MS06 [EV-0300], [EV-0422], [CL-L242], [M-0098]. The Falk-note `MS06StageSetter` is a distinct direct `MS06.SetStage(10)` request. Given the captured main QUST flags and ENAM, the existing GOG 1.6.1179.0 initial guard rejects that request; exact Steam behavior and alias fill remain unknown [EV-0313], [EV-0314], [EV-0316], [EV-0260].

The five-master source screen found no function-index-80 condition in 85 linked INFO rows or the captured SCEN CTDAs; none of the 22 attached TIF PEXs directly starts a quest or requests main MS06 stage 10. The five placed trigger records include a main stage-60 write with a stage-50 prerequisite; `PotemaBossFightScene` binds main MS06 and contains a stage-125 writer, but scheduling while MS06 is stopped is unresolved [EV-0422], [CL-L241], [CL-L243]. The missing trigger PEX is a coverage limit, not inert behavior.

**Causal assessment:** No edge from M-0098/OBJ-1 to M-0009 or M-0096/OBJ-2 is supported. The records/scripts identify no shared call path, ActorValue, HitData field, ActiveEffect, or serialized dependency [EV-0422]. This no-edge assessment would be falsified by an identified shared writer or a controlled runtime trace showing a causal data/state dependency. The exact level-one Steam transition remains open under EV-0260; no vanilla bypass is claimed.

EV-0438 refines the Q-0079 branch model: within `FUN_1407e7f00`, the constructed-HitData call to `FUN_1406b9df0` occurs only when `plVar13` is nonnull and `lVar4+0x48` is clear; the alternate branch checks destination byte `+0x13` bit 0 and may call tag-9 builder `FUN_1406577d0`. These call routes are exclusive within one invocation. This adds a static control-flow relation between that function and both callees, not a gameplay or armor-XP causal edge; field semantics, runtime path and ordinary-hit coverage remain unknown [EV-0438], [CL-L258]. The next exact worker caller is `FUN_140657830`.

EV-0439 extends the shared-gate comparison: `FUN_140657830` builds tag `0x3B` for `FUN_14065b800`, and two captured callers select it under `FUN_1406d4110`. This makes three inspected tags (`0x42`, 9 and `0x3B`) that use the same predicate on nonidentical static event routes. Tag `0x3B` is not tag `0x0B`; neither this route nor the common gate identifies ordinary-hit coverage, protection or AVSK effects. No new causal edge to the armor-XP or level-one models is supported. Fifty-one originally uninspected worker callers remain; next inspect `FUN_140657980` [EV-0435], [EV-0437], [EV-0439], [CL-L255], [CL-L257], [CL-L259].

EV-0440 adds a bounded negative sample: `FUN_140657980` writes tag `0x51` and calls the worker but has no incoming direct-call edge in the analyzed project; its single DATA reference has no source identity. This does not establish that the builder is unused or identify its producer. No tag-0xB event or armor-XP causal edge is added. Fifty originally uninspected callers remain; next inspect `FUN_1406579f0` [EV-0440], [CL-L260].

EV-0441 maps another distinct non-B worker payload: `FUN_1406579f0` writes tag `0x53` and receives two captured callers under unresolved object/state predicates. Neither caller establishes ordinary-hit coverage or an armor/AV causal edge. The inspected caller sample is now 13/62 with no tag-0xB body found; 49 remain. Continue at `FUN_140657a70` [EV-0441], [CL-L261].

EV-0442 revises that sample result: `FUN_140657a70` constructs tag 0x0B for `FUN_14065b800`; its sole captured caller `FUN_1406bb690` takes the tag-0xB worker path when `FUN_1406d4110` is true and returns. When the gate is clear, the function continues through conditional `FUN_1406bcaa0` calls. Worker dispatcher case 0xB re-enters `FUN_1406bb690`, while the separate Actor-state/process route `FUN_1407ba3e0` also reaches it [EV-0442], [EV-0397], [EV-0291], [CL-L262]. This supports a static gated continuation into the resolver family and rejects the full-set claim that none of the 62 callers constructs tag 0xB. The exact event source, ordinary physical-hit coverage, protection, AV11/AV12 attempt and final skill XP remain unknown; no armor-XP causal edge is added. Fourteen callers are reviewed and 48 remain. Next trace `FUN_1407ba3e0`'s source/process arguments, then continue the census.

EV-0443 refines the second route: `FUN_1407ba3e0` calls a virtual method at `param_2` vtable offset `+0x4c8`; if false, it obtains a global process object and calls `FUN_1406bb690(param_2, process+0x5d0 == *param_3, 1)`. It then conditionally changes bits in `param_2+0xc8`. There are no analyzed incoming direct-call edges and two DATA references without source-function identity [EV-0443], [CL-L263]. This is a separate Actor/process callback path into the handler; neither its registration nor its relation to ordinary incoming attacks is identified. No causal edge to effective armor protection, AV11/AV12 award attempts or armor XP is supported. Inspect the two DATA-reference contexts before continuing the worker census.

EV-0445 confirms the first correctly addressed cell at RVA 0x366669c has no function boundary or xrefs and the address-context adapter does not expose its backing bytes. EV-0446 shows the second table-like data address at RVA 0x18bae08 has two DATA references from instructions 0x1407c3440 and 0x1407c344e in `FUN_1407c3400`. This maps a candidate source function, not a callback registration or event meaning. No new hit, protection, or AV/XP causal edge is supported; inspect `FUN_1407c3400` before assigning semantics.

EV-0447 identifies the candidate data consumer: `FUN_1407c3400` allocates a 0x10-byte object, zeros its `+8` field and stores the labeled `HitFrameHandler::vftable` at offset 0. The table places `FUN_1407ba3e0` at slot 1 [EV-0447], [EV-0443], [CL-L264]. This supports a named HitFrameHandler class/slot relation; registration, ordinary-hit initiation and final resolver/armor/AV effects remain open. Verify RTTI next. No live armor-XP or OBJ-1 causal edge is added.

EV-0448 supplies independent MSVC RTTI for vtable address `0x18bae08`: its type name is `.?AVHitFrameHandler@@`, subobject offset 0, and type descriptor RVA `0x206EA70`. This confirms the class identity behind `FUN_1407c3400`'s vtable store and strengthens the interpretation of `FUN_1407ba3e0` as a HitFrameHandler slot-1 method. It does not establish runtime caller, ordinary-hit coverage, or an armor-XP edge. Read the slot directly next [EV-0448], [CL-L264].

EV-0449 directly reads zero-based slot 1 at vtable RVA `0x18bae08`: slot address `0x1418bae10` resolves to `FUN_1407ba3e0` at RVA `0x7BA3E0`, and RTTI remains `.?AVHitFrameHandler@@`. This closes the static class/slot mapping. Runtime invocation, ordinary-hit provenance, and protection/AV/armor-XP effects remain unknown; inspect sibling methods only if they discriminate callback purpose [EV-0449], [CL-L264].

EV-0451 resolves the adjacent table boundary: `0x141b39578` is a complete-object locator for `.?AVAnticipateAttackHandler@@` at vftable RVA `0x18bae20`, so the following `FUN_1407c1000` entry belongs to a distinct class table, not HitFrameHandler. EV-0452 shows `FUN_1407c2320` allocating a 0x10-byte object, clearing +8, and storing that vftable at offset 0, with no analyzed incoming direct callers. This resolves the table-layout ambiguity but adds no causal edge to ordinary incoming hits, protection, AV11/AV12, or armor XP [EV-0450]–[EV-0452], [CL-L266].

EV-0453 identifies the next worker payload: `FUN_140657ab0` constructs tag 0x0D around an Actor-like pointer and increments its +0x28 counter. Its sole caller `FUN_1405cd570` checks virtual slot +0x4c8, performs `FUN_1405dab70`, and branches on the shared thread gate; only the gate-set branch queues tag 0x0D, while the gate-clear branch may call `FUN_140712d10` [EV-0453], [CL-L267]. This is a state/update callback candidate, not ordinary-hit evidence. No causal edge to HitData, effective armor protection, AV11/AV12, armor XP, or OBJ-1 is supported pending dispatcher and direct-path mapping.

EV-0454 maps dispatcher case 0x0D to `FUN_140712d10(object[0x1f], object)`, the same function called directly by `FUN_1405cd570` when the shared gate is clear [EV-0453], [EV-0454], [CL-L268]. At the dispatcher layer this differs from tag 0x0B's re-entry into `FUN_1406bb690`; deeper calls are not yet known. No edge to HitData, armor mitigation, AV11/AV12, or XP should be asserted until `FUN_140712d10` and its relevant callees are traced.

EV-0455 gives `FUN_140712d10` 18 outgoing direct calls, one indirect call site, and two direct incoming callers. Its body gates on Actor/process state and updates fields through actor/process helpers; the complete direct-call list has no direct edge to `FUN_1406b9df0`, `FUN_1406bb690`, or `FUN_1406bcaa0`. It does call `FUN_1406c21c0`, and that state-handler descendant remains unresolved. Record only a direct no-edge to the known HitData/tag-0xB functions, not a transitive proof that tag 0x0D cannot affect hits or XP [EV-0455], [CL-L269].

EV-0456 follows `FUN_1406c21c0`: 38 direct-call edges, three indirect sites and 31 direct callers. Its captured body constructs `TESActionData`/`BGSActionData` objects and invokes actor/process action helpers; the complete direct call list has no edge to `FUN_1406b9df0`, `FUN_1406bb690` or `FUN_1406bcaa0`. This broad action/state function is not tag-0xD-specific because of its 31 callers. The bounded direct route from tag 0x0D through it adds no direct HitData/XP edge, while indirect behavior and descendants remain open [EV-0455], [EV-0456], [CL-L270]. Resume the exact worker-caller census with `FUN_140657b50`.


EV-0457 establishes the exact tag-0x0E producer/caller route: `FUN_1407bc3a0` queues it for virtual process-query results 1 or 2, and dispatcher case 0x0E routes the object to `FUN_1407136e0` [EV-0457], [EV-0454], [CL-L271]. The status meaning is unresolved. No causal edge is added from this route to HitData, effective protection, AV11/AV12, or armor XP; query `FUN_1407136e0` to discriminate the proposed hit/skill and process/action models. The tag-0x0E caller also differs from the tag-0x0D caller's observed `FUN_1406d4110` gate, so the two should not be merged into one mechanism without further evidence.

EV-0458 shows the complete direct body for `FUN_1407136e0`: Actor/process flag checks, TLS marker handling, virtual calls, nested state/flag updates, reference release, and a final direct call to `FUN_1406653a0`. Its 15-edge scan has no direct call to mapped HitData/tag-0xB functions `FUN_1406b9df0`, `FUN_1406bb690`, or `FUN_1406bcaa0`; five indirect sites and four incoming caller functions are enumerated [EV-0458], [CL-L272]. This supports a bounded direct Actor/process-state model, not a global no-hit/no-XP conclusion. No causal edge to effective protection or armor XP is added. Trace `FUN_1406653a0` next because it is a direct terminal helper on this route.

EV-0459 narrows that terminal helper: `FUN_1406653a0` reads flag field +0xCC, returns unless the high bits are 0x20 or 0x80, and then performs an indirect tail jump through receiver vtable slot +0x530; its only analyzed incoming direct caller is `FUN_1407136e0` [EV-0459], [CL-L273]. The receiver's exact vftable/RTTI and slot implementation remain unknown. This is a flag-conditioned virtual dispatch, not a mapped HitData or skill call. Resolve the receiver type and slot implementation before assigning any hit/XP meaning; preserve a no-edge rationale for ordinary-hit, protection and armor XP pending that evidence.

EV-0460's initialized-memory `AVActor` substring search found 35 matches and zero analyzed string references; it does not expose enclosing type names or identify a vftable [EV-0460], [CL-L274]. EV-0461 queried the first candidate type-descriptor address at RVA 0x203CDB8 and found no function boundary or exact-address xrefs; the address adapter did not expose its backing bytes or type name [EV-0461], [CL-L275]. These are bounded tooling/data-context negatives, not evidence that Actor RTTI is absent. No causal edge to HitData, ActorValue, protection, or armor XP is supported. Check local PE/RTTI readers for a better exact-type path, then resume the worker census if this candidate remains unidentifiable.

EV-0462 resolves primary `VTABLE::Actor` slot 0xA6 (+0x530) at GOG RVA 0x189EC20 to `FUN_140665140`; the table RTTI is `.?AVActor@@` with subobject offset zero [EV-0462], [EV-0400]. EV-0463 shows the target transitions the +0xCC state field and invokes action/process helpers, with 17 direct call edges and no direct edge to mapped HitData handlers [EV-0463], [CL-L276], [CL-L277]. This supports the base Actor process/action interpretation for the slot. A second untyped table also references the function, so the tag-0x0E receiver's dynamic class and possible override remain open. No causal edge to HitData, effective protection, AV11/AV12, or armor XP is added. Continue the exact worker-caller census at `FUN_140657b90`; 45 initial callers remain.

EV-0464 and EV-0465 show a second use of the shared thread gate: `FUN_1406e5da0` queues worker tag 0x55 through `FUN_140657b90` when `FUN_1406d4110` is nonzero, and case 0x55 calls back into `FUN_1406e5da0` with the stored object/process pair. EV-0466 bounds that routine's direct path at 31 edges and finds no direct call to the mapped HitData handlers, while 17 indirect sites and re-entry gate state remain unresolved. Together with the tag-0x10 HitData continuation and other event tags sharing the gate [EV-0432]–[EV-0439], this supports the gate as a shared threading/state mechanism rather than hit-specific evidence. It does not prove that the tag-0x55 runtime continuation completes or that tag 0x10 cannot reach ordinary-hit effects. No causal edge to protection, AV11/AV12 or armor XP is added; the worker census continues at `FUN_140657bc0` [EV-0464]–[EV-0466], [CL-L278]–[CL-L280].

EV-0467–EV-0470 extend that cross-system model: a separate tag-0x0F producer also checks the shared gate, but its dispatcher enters an Actor/process position and collision route (`FUN_140713a20` → `FUN_140725340`) that invokes the Havok world linear-cast helper `FUN_140b3eb50`. The `TtworldLinCast` profiling label and `hkpWorldLinearCaster` construction support a physics-query interpretation for this bounded path. Its direct scan has no mapped HitData edge, while indirect sites and downstream behavior remain open. Tags 0x55 and 0x0F therefore show distinct Actor/process event continuations reusing the same gate; this does not make the gate hit-specific, and a collision query is not evidence of an incoming combat hit. No causal edge to effective armor protection, AV11/AV12, armor XP, or OBJ-1 is supported. The exact worker sample is 18/62, with 44 remaining [EV-0467]–[EV-0470], [CL-L281]–[CL-L284].

EV-0471/EV-0472 add a third event pattern: tag 0x14 is selected by an entity-update caller under `DAT_14319a7c0` and local state predicates, rather than the `FUN_1406d4110` gate used by tags 0x55 and 0x0F. Dispatcher case 0x14 enters `FUN_1414a3950`, which performs TLS/thread-associated state handling and forwards the payload to `FUN_14021cd70`; its complete direct scan has no mapped HitData/ActorValue edge [EV-0465], [EV-0471], [EV-0472], [CL-L285], [CL-L286]. This expands the model from one shared gate to heterogeneous event producers and consumers converging on `FUN_14065b800`. The target helper remains unresolved, so competing combat/skill and state-only descendants remain open. No causal edge to OBJ-2 armor protection/XP or OBJ-1 quest initiation is added. The exact worker sample is 19/62, with 43 remaining; next resolve `FUN_14021cd70`, then continue at `FUN_140657d80`.

EV-0473 shows the immediate handoff is a reference-counted BSTArray append: `FUN_14021cd70` invokes allocator/growth helper `FUN_140cc8350`, stores the payload on successful insertion, then increments its +8 reference count [EV-0473], [CL-L287]. This strengthens the deferred-storage reading for tag 0x14 without resolving what later drains the manager's array members at `DAT_142034080+0x1c8/+0x1e0`. The next causal discriminator is to identify producer-backed readers of those exact array members; do not infer HitData absence from the append helper.

EV-0474 shows the manager base `DAT_142034080` is referenced by 168 functions across 254 xrefs, including dispatcher `FUN_140659160`; this wide base-pointer use does not identify the +0x1c8/+0x1e0 array readers [EV-0474], [CL-L288]. The tag-0x14 direct route remains a refcounted array append, but its consumer is open. The next screen is nearby method `FUN_1414a81f0` because it has five manager-global references; this is a candidate inspection, not a mapped consumer edge.

EV-0475 screens that candidate: `FUN_1414a81f0` has 56 direct edges and 17 indirect sites, references `DAT_142034080` through field +0x228 rather than the target +0x1c8/+0x1e0 members, and has no mapped direct HitData/ActorValue edge [EV-0475], [CL-L289]. Its two `FUN_14021cd70(param_3)` calls do not identify `param_3` as the tag-0x14 array. Thus the array consumer is still unknown, and no causal edge to armor protection/XP or OBJ-1 is added.

EV-0476 adds a fourth distinct producer shape to the reviewed event sample: `FUN_140657d80` explicitly stores tag 0x24 and calls the common worker, but its incoming-xref query reports no caller despite that direct edge and its inclusion in EV-0423 [EV-0476], [CL-L290]. The inventory/body conflict is retained as an analysis discrepancy. Across the newer routes, the same worker therefore carries shared-gate Actor/process continuations (0x55 and 0x0F), a thread-associated array handoff (0x14), and a separately parameterized event/action route (0x24/0x25) [EV-0464]–[EV-0476]. This supports a common dispatch/scheduling primitive over heterogeneous payloads; it does not support a single hit-specific meaning for the worker. Cases 0x24 and 0x25 converge on `FUN_14065c6e0` but use different input expressions [EV-0465]. EV-0477–EV-0478 trace this target to a record write at +0x2c and TLS-marked entity/phantom Havok broadphase overlap/filter work, with no mapped direct HitData handlers in either branch body. This is a bounded positive state/physics route, not a transitive or runtime no-hit result: indirect virtual targets and descendants remain open [CL-L291], [CL-L292]. Comparison with tag 0x0F shows two distinct Havok-facing mechanisms—world linear-cast collision/position work and broadphase overlap/filter updates—without an established damage or ActorValue edge [EV-0469], [EV-0470], [EV-0477], [EV-0478]. No causal edge to effective armor protection, AV11/AV12 award, armor XP, or level-gated quest initiation is established. The exact worker sample is 20/62, with 42 remaining; next resume the exact caller `FUN_140657e40`.

## Q-0079 — corrected worker census and partial caller review

EV-0423 verifies that GOG worker `FUN_14065b800` has 95 unique direct callers, not 64; 64 is the query's caller-storage cap. The exact EV-0397 set partitions into 33 previously decompiled bodies and 62 initially uninspected bodies. Ten additional callers are now mapped: `FUN_140656d90`, `FUN_140656de0`, `FUN_140656ef0`, `FUN_140657290`, `FUN_140657460`, `FUN_1406575c0`, `FUN_1406576a0`, `FUN_140658e50`, `FUN_140657790`, and `FUN_1406577d0`, with tags 2, 0x1E, 0x1F, 3, 6, 0x10, 8, 0x5c, 0x42, and 9 [EV-0424]–[EV-0429], [EV-0431], [EV-0435], [EV-0437], [CL-L244]–[CL-L249], [CL-L251], [CL-L254], [CL-L255], [CL-L257]. EV-0430 maps eight incoming callers of `FUN_1406b9df0`, including known resolver `FUN_1406bcaa0` calling it with a HitData object after its player skill-routing block and dispatcher `FUN_140659160` case 0x10 calling it with actor/event data. EV-0431 shows that tag-0x10 builder `FUN_1407dce10` copies the same fields at offsets 0x50, 0x54, 0x5c, and 0x80 that the handler consumes, then case 0x10 passes the clone back to the handler; tags 8 and 0x5c use the helper too. EV-0432 maps the shared predicate `FUN_1406d4110`: with the global state field at `DAT_1431785f0+0x6c` equal to 1, it allocates/reads a per-thread mask and checks whether `DAT_14319c2e0` has any other thread bits set. EV-0433 finds 29 mask references across that predicate and seven nearby helpers, with several READ_WRITE candidates. EV-0434 confirms `FUN_1406d41c0` atomically sets/clears the current thread bit, and several callers save and restore prior membership around function/callback work. EV-0435 shows the same gate on another event producer: `FUN_1406563b0` sends tag 0x42 through the worker when the gate is true and follows `FUN_140656710` otherwise; dispatcher case 0x42 makes a virtual `+0x78` call on the payload object. EV-0436 shows that wrapper has no direct callers and two data references with no source-function identity. EV-0437 maps tag 9 through four callers; several use the same gate, while `FUN_1407e7f00` also contains a separate constructed-HitData call to `FUN_1406b9df0` on another branch. The tag-9 method/class and its relation to ordinary hits are unresolved. These second event routes confirm the gate is shared rather than hit-specific. The tag-0x10 path remains a serialized continuation candidate, not an armor-XP bypass. No new edge to M-0009, M-0096, or OBJ-1 is supported. There are 52 of the initially uninspected worker callers still to review; next inspect `FUN_1407e7f00`'s branch/caller context and continue the census, preserving the Steam matched-hit/protection/raw-AVSK discriminator under EV-0260.

## Q-0079 synthesis — tags 0x28 and 0x3C (EV-0480–EV-0487)

The same worker/dispatcher carries heterogeneous mechanisms: tag 0x24/0x25/0x27 reaches Havok broadphase overlap/filter maintenance [EV-0477], [EV-0478]; tag 0x28 reaches positive-only recursive scalar/property updates [EV-0480], [EV-0481]; tag 0x3C reaches a gated recursive callback route whose resolved callback adjusts a returned object's reference count [EV-0482]–[EV-0487]. Their common dispatcher does not support a single hit-specific meaning, and none of these bounded routes maps directly to HitData or an ActorValue award. Unknown virtual descendants prevent a global negative.

Tag-0x28 and tag-0x3C helpers both traverse child pointers at +0x118/count +0x122 and use parent vtable slot +0x18. This supports a structural analogy, not a proven shared runtime type or a causal edge. The falsifying discriminator is a producer-backed RTTI/vtable comparison: distinct dynamic type identities or incompatible slot/member behavior would reject the common-node-type model [EV-0481], [EV-0483], [EV-0484], [CL-L303]. The separate decompiler/register discrepancy in the tag-0x28 and tag-0x3C calls remains preserved [CL-L296], [CL-L302].

The worker sample is now 23/62, with 39 remaining. No edge is added to OBJ-1 or to M-0009/M-0096, and no effective-protection, AV11/AV12, raw AVSK, or armor-XP result is established. Continue with exact remaining caller `FUN_140657fc0`.

## Q-0079 synthesis — tag 0x4C gated helper route (EV-0488)

`FUN_140657fc0` constructs tag 0x4C with a retained object and byte. Its three captured callers share a discriminating gate pattern: a true `FUN_1406d4110` result queues the event; a false result calls `FUN_1406940d0` directly with the same captured arguments [EV-0488]. Dispatcher case 0x4C calls that same helper [EV-0397]. This is a deferred common-helper route with direct fallback, but static equivalence does not establish identical runtime effects or scheduling. The helper's behavior is the next high-information discriminator.

Cross-system synthesis now distinguishes Havok broadphase maintenance (0x24/0x25/0x27), recursive scalar/property work (0x28), recursive callback/reference-count work (0x3C), and a gated/deferred helper call (0x4C). The worker dispatcher and thread gate are shared scheduling primitives across heterogeneous events, not evidence of one hit-specific mechanism [EV-0432], [EV-0477]–[EV-0488]. Tag 0x4C has three incoming caller xrefs, so the four preceding zero-xref results are a bounded repeated pattern rather than a universal omission [EV-0476], [EV-0479], [EV-0480], [EV-0482], [EV-0488]. No direct HitData/ActorValue, protection, or armor-XP edge follows from the tag route. The sample is 24/62 with 38 remaining; next inspect `FUN_1406940d0` at RVA `0x6940d0` and preserve the Steam runtime discriminator under EV-0260.

## Q-0079 synthesis — tag 0x4C process/context and physics edge (EV-0489)

The tag-0x4C helper `FUN_1406940d0` updates a process/context value at +0x15c and, in the captured branch, calls `FUN_14065c6e0` with a composed value, then `FUN_140e8f210` with an object/value pair [EV-0489]. The first helper is already mapped to event-value storage and Havok broadphase overlap/filter maintenance [EV-0477], [EV-0478]. This creates a supported static causal edge from the tag-0x4C route into that previously separated physics/state family, with `FUN_140e8f210` as a new unresolved branch. Six indirect sites and that direct object/value helper remain open; the complete body has no mapped direct HitData or ActorValue handler. This is a causal link within OBJ-2, not a bridge to armor XP or OBJ-1.

The next discriminant is `FUN_140e8f210` at GOG RVA 0xe8f210: compare its signature, direct/indirect callees, and dataflow with the tag-0x28 recursive scalar/property route. If the object/value shape and producer-backed targets match, that supports a shared state propagation mechanism; distinct layouts/call chains would preserve separate models. Keep the exact Steam protection/raw-AVSK test under EV-0260 open. The caller sample remains 24/62, with 38 remaining; after this branch, resume at `FUN_140658000`.

## Q-0079 synthesis — shared object/value wrapper and cross-event convergence (EV-0490)

`FUN_140e8f210` is a one-edge wrapper that packs two 32-bit operands and forwards them to `FUN_140e90750`; 11 direct caller functions include both tag-0x4C helper `FUN_1406940d0` and tag-0x0D target `FUN_140712d10`, as well as dispatcher `FUN_140659160` [EV-0490], [EV-0397], [EV-0489], [EV-0454]. This is a new convergence point across Actor/process and event-dispatch paths. The captured callers provide different operand pairs, so the common wrapper does not establish a common operation meaning.

The relationship to tag 0x28 remains a live competing model: `FUN_140e8f210` packages two words for `FUN_140e90750`, while tag 0x28 enters recursive helper `FUN_140e905e0` with a positive scalar. Compare the target's argument decoding, receiver/member layout, recursion, and setter targets before linking them [EV-0480], [EV-0481], [EV-0490]. No mapped direct HitData/ActorValue, effective-protection, or armor-XP edge has emerged; next query `FUN_140e90750` at RVA 0xe90750, then continue the exact worker census at `FUN_140658000`.

## Q-0079 synthesis — recurring object-tree update substrate (EV-0491)

`FUN_140e90750` walks the same observed object-tree shape as tag-0x28 `FUN_140e905e0`: both use the `DAT_14328f300` selector, `FUN_1402f39c0` record lookup, child pointers +0x118/count +0x122, and parent vtable slot +0x18 [EV-0481], [EV-0491]. Their node updates are distinct: `FUN_140e90750` conditionally replaces low 7/high 16 bits and writes the packed result at +0x2c, while `FUN_140e905e0` multiplies a positive scalar and invokes a setter. The evidence supports a recurring recursive traversal/update substrate; it does not identify a shared dynamic class or equivalent behavior.

The packed update's `FUN_140e83d30` edge reaches `FUN_140e8bd30`, connecting this wrapper's path to the previously mapped event-value/Havok broadphase chain [EV-0477], [EV-0478], [EV-0491]. Two indirect call sites and four DATA refs without source identities remain unresolved. No direct HitData, ActorValue, effective-protection, or armor-XP edge is established. H32 is now supported only at the structural substrate level; continue the exact worker census at `FUN_140658000` (24/62 reviewed, 38 remaining).

## Q-0079 synthesis — tag 0x4D paired-object and constraint route (EV-0492–EV-0493)

Worker caller `FUN_140658000` writes tag 0x4D. Its producer `FUN_1407bcdf0` uses the shared `FUN_1406d4110` thread-state predicate to queue the payload or directly call `FUN_140e8fc90`; dispatcher case 0x4D also routes the queued payload to that helper [EV-0490], [EV-0492]. This is static deferred/immediate convergence, not evidence that timing or effects are equivalent.

`FUN_140e8fc90` resolves paired objects against record/child data. A matching node with `param_9==0` calls `FUN_140e90750` with a packed value, linking tag 0x4D to the recursive object-tree update substrate; an unmatched `param_9!=0` branch constructs a Havok ball-and-socket or fixed constraint and calls `FUN_140e95190`/`FUN_140e860d0` [EV-0491], [EV-0493]. This adds a direct bridge between event dispatch, recursive object properties, and physics constraints. The complete body has 26 direct edges and nine unresolved indirect sites but no mapped direct HitData or ActorValue/armor-skill edge. EV-0494 resolves `FUN_140e95190` as selector-gated array append, while `FUN_140e860d0` remains the unresolved attachment branch. Combat effects, effective protection and armor XP remain unestablished; do not infer a global negative. Next query `FUN_140e860d0`, then continue with exact worker caller `FUN_1406580f0` (25/62 reviewed, 37 remaining).

`FUN_140e95190` is not an unconditional constraint registration. It sets TLS +0x768 to 0x33, checks the candidate object for selector entries `DAT_14328f6e0` or `DAT_14328f710`, appends matching objects to the record's BSTArray at +0x28, and increments the object reference count [EV-0494]. In `FUN_140e8fc90`, the newly constructed constraint is offered to this selector-gated array, while `FUN_140e860d0` is called separately. This separates candidate-list membership from the still-unresolved physics/world attachment effect. Eleven callers show the append helper is shared. Next query `FUN_140e860d0`, then return to `FUN_1406580f0`; caller count remains 25/62.

EV-0495 resolves the other tag-0x4D branch target as a shared polymorphic constraint attachment/queue helper. `FUN_140e8fc90` passes `plVar9[2]`, a pointer from its constructed constraint object, to `FUN_140e860d0`. The helper dispatches through owner/context virtual slots +0x138/+0x140; its immediate path validates endpoint fields and calls `FUN_140b3a710`, while its alternate path stores the pointer in an owner-side queue. This is the same exact helper already traced from the ProcessTrapHit-created hkpConstraintInstance route [EV-0360], [EV-0364], [EV-0495]. Add a causal edge between these two call routes and the shared native helper, but do not infer identical runtime object types, combat semantics, HitData, or armor-XP effects. Two helper virtual sites, nine parent helper virtual sites, and deeper callbacks remain unresolved. Resume the exact caller `FUN_1406580f0`; census is 25/62.

EV-0496 adds worker tag 0x4A as another use of the shared thread-state gate: two producers queue an object/byte payload when `FUN_1406d4110` is set, and their clear branches converge on the same helper/value update sequence reached by dispatcher case 0x4A [EV-0496], [EV-0455]. The captured route conditionally raises a float field and has no mapped direct HitData or ActorValue/armor-skill edge. This adds an event-to-object/value state edge within OBJ-2, not a hit/XP edge; `FUN_140ea0760` descendants remain the next discriminator. Tag 0x4A reinforces that the worker/gate is shared by heterogeneous payloads, as already seen for process, physics, and constraint routes [EV-0432], [EV-0477]–[EV-0496].

EV-0497 refines the tag-0x4A helper route: after a byte-change/receiver-flag guard and a type check, `FUN_140ea0760` scans a selector-matched list, sets or clears each selected entry's bit, and dispatches through one of two manager update functions. Add the causal path `tag-0x4A producer/dispatcher -> FUN_140ea0760 -> selector-list bit/manager state transition`. No edge is added to HitData, ActorValue, armor skill, effective protection, or OBJ-1 quest state: the captured direct callees do not map those targets, while five virtual sites and deeper descendants remain unresolved [EV-0497], [EV-0496], [EV-0260].

EV-0498 maps caller `FUN_140658130` to tag 0x60 and the worker dispatcher route to `FUN_140e88fd0(payload,1)` for a nonnull payload. Add this static event-dispatch edge only. Its source-less DATA xref does not identify the producer, and the handler has not been traced; no causal edge to HitData/ActorValue, armor protection, armor skill, or the Q-0078 quest gate is supported [EV-0498], [EV-0455], [EV-0260].

EV-0499 refines this node: `FUN_140e88fd0` optionally checks selector/type/flag state, then invokes a global callback over a recursively traversed child hierarchy through `FUN_140e898f0`. This adds `tag 0x60 -> FUN_140e88fd0 -> hierarchy callback traversal` as a static mechanism path. The callback target, dynamic types, and worker call's third-register value remain unresolved, so there is no supported causal edge to HitData, ActorValue, effective protection, armor skill, or OBJ-1 quest state [EV-0499], [EV-0498], [EV-0260].

EV-0500 resolves the worker ABI: tag-0x60 case sets both arg2 and arg3 to 1, bypassing `FUN_140e88fd0`'s optional selector/type/flag guard and enabling recursion through `FUN_140e898f0`. This strengthens the event-to-hierarchy traversal edge only; callback target and dynamic effects remain open, so no armor-skill or quest-gate causal edge is added [EV-0500], [EV-0499], [EV-0260].

EV-0501 finds the sole captured xref to `PTR_FUN_14202d630`: a READ from `FUN_140e88fd0`; the bounded query does not expose pointer content or a writer. This corroborates the callback read site without adding a target or causal edge to HitData, ActorValue, armor skill, or OBJ-1 quest state [EV-0501], [EV-0499], [EV-0500].

EV-0498 maps caller `FUN_140658130` to tag 0x60 and the worker dispatcher route to `FUN_140e88fd0(payload,1)` for a nonnull payload. Add this static event-dispatch edge only. Its source-less DATA xref does not identify the producer, and the handler has not been traced; no causal edge to HitData/ActorValue, armor protection, armor skill, or the Q-0078 quest gate is supported [EV-0498], [EV-0455], [EV-0260].

EV-0502 maps `PTR_FUN_14202d630` to `FUN_140e89be0`; its sole captured reader is `FUN_140e88fd0`. This adds the static callback-target edge to the tag-0x60 hierarchy route, while the callback body and any HitData/ActorValue, armor-skill, protection, or quest-state effect remain unproven [EV-0502], [EV-0501], [EV-0500].

EV-0503 refines the callback node: `FUN_140e89be0` clears an object +0x40 pointer, atomically releases the pointed object +0x8 reference count, and has unresolved vtable +0x8 and +0x128 dispatches. This supports an object-lifetime path at the bounded body only; it adds no edge to HitData/ActorValue, armor skill, protection, or quest state [EV-0503], [EV-0502].

EV-0504 maps the three adjacent callback cells at 0x14202d628/630/638 to readers `FUN_140e88e90`, `FUN_140e88fd0`, and `FUN_140e88d70`, respectively. Only the middle target resolves to an analyzed function (`FUN_140e89be0`), whose bounded body is a reference-release callback. The outer cell targets remain unmapped, so no shared runtime type or causal edge to combat/skill is added [EV-0504], [EV-0503].

EV-0505 adds bounded context at the first adjacent pointer target 0x140e89bb0: it is referenced as a PARAM by `FUN_140e88e90` and begins with +0x18/+0x10 field accesses, but has no analyzed function boundary. This is a structural lead only; no runtime type or gameplay edge is added [EV-0505], [EV-0504].

EV-0506 compares the second outer callback target at 0x140e89c50 with EV-0505: both unbounded target contexts access the RDX descriptor at +0x10/+0x18, while the second path dispatches through virtual slot +0x170. This supports a shared-layout lead only; distinct bounded operations and absent function boundaries leave type/family semantics unresolved. No causal edge to HitData, ActorValues, protection, armor skill, or OBJ-1 quest state is added [EV-0506], [EV-0505], [EV-0504].

EV-0507 advances Q-0079 to exact worker caller 28/62: FUN_140658240 builds tag 0x17 with object/payload pointers and two bytes, increments object +0x28, and submits it through FUN_14065b800. Both incoming callers use the shared FUN_1406d4110 gate; case 0x17 invokes recipient virtual slot +0x5a0 [EV-0507], [EV-0465], [EV-0432]. This strengthens the gate as a reused coordination primitive, but receiver type/slot implementation are open and no causal edge to HitData, protection, AV11/AV12, armor skill, armor XP, or OBJ-1 is added.

EV-0508 resolves primary Actor slot index 0xb4 (+0x5a0), used by tag-0x17 dispatcher case, to FUN_14066dfa0. This is also a producer caller: when FUN_1406d4110 is nonzero it submits another tag-0x17 through FUN_140658240; on the clear-gate branch it calls FUN_1406a19b0 and virtual +0x378 [EV-0508], [EV-0507], [EV-0465]. The requeue supports an Actor/action state route, while helper/virtual descendants and runtime type remain unresolved; no causal edge to HitData, ActorValues, protection, AV11/AV12, armor skill, armor XP, or OBJ-1 is added.

EV-0509 completes FUN_14066dfa0’s direct scan: three direct edges to the shared gate, tag-0x17 builder and FUN_1406a19b0, plus one virtual +0x378 call. The set-gate route requeues tag 0x17; the bounded clear-gate helper body uses object/node offsets and mutates child state or calls FUN_1406551c0. This supports an Actor/action-state route for the base implementation only. No edge to mapped HitData/ActorValue/armor-skill handling is present in the complete direct list; helper descendants and the virtual call remain open [EV-0509], [EV-0508].

EV-0510 completes FUN_1406a19b0 direct/incoming coverage: seven unique direct targets, four unresolved virtual sites, and three incoming callsites from FUN_14066dfa0/FUN_140738730. Its direct path and bounded FUN_1406551c0 target operate on object/child-node state, with no mapped HitData/ActorValue/armor-skill function in the complete direct list. The base Actor caller passes a virtual +0x378 result into this helper; that producer remains unresolved, so no transitive or runtime negative is added [EV-0510], [EV-0509], [EV-0508].

EV-0511 resolves primary `VTABLE::Actor` slot +0x378 to `FUN_1402f3770`, whose exact thunk tail-jumps through the runtime receiver vtable +0x380. This creates a structural dispatch edge from the base slot to an unresolved dynamic slot; the concrete target and runtime class remain open. No edge to HitData, ActorValues, protection, armor skill/XP, or OBJ-1 is supported [EV-0511], [EV-0510].

EV-0512 maps primary Actor +0x380 to `FUN_1402e55a0`, the same helper reached by Actor slot +0x70 in HitData receiver `FUN_1406b9df0` [EV-0295], [EV-0296]. The tag-0x17 base path reaches the helper through the +0x378 forwarding thunk and passes its pointer to `FUN_1406a19b0` for object/node operations [EV-0511], [EV-0509], [EV-0510]. This is an exact shared-code edge, not proof that both paths use the same returned runtime object or that tag 0x17 continues into hit/skill processing. The HitData consumer retains unresolved indirect sites; the tag-0x17 helper's bounded path is object/node state. Keep the shared-context question in Q79-H46/H47. No causal edge to AV11/AV12, protection, armor XP, or OBJ-1 quest gating is added [CL-L328], [M-0113].

EV-0513 maps caller 29/62 `FUN_1406582d0` to tag 0x19 from process/type-gated producer `FUN_140687370`; dispatcher case 0x19 calls `FUN_140687430(payload,0)` [EV-0455], [EV-0513]. The producer also calls unresolved virtual +0x2b8. Until the target is inspected, this adds a worker-event route only; no edge to mapped HitData, ActorValue, protection, armor skill/XP, or OBJ-1 is established [CL-L329].


EV-0514 completes the direct/incoming census for tag-0x19 handler FUN_140687430: the worker dispatcher reaches it with payload and flag 0; its 49 direct-call sites cover 38 unique targets, while nine virtual calls remain unresolved. The bounded body uses process-associated object and child-hierarchy state, the DismemberedLimb1_Head1 string pointer, and a conditional edge to FUN_1406e5da0; caller FUN_1406883b0 invokes it with flag 1 from a body-part record traversal containing a Torso label [EV-0514], [EV-0513], [EV-0455], [EV-0464]–[EV-0466]. Add these event/handler/hierarchy edges only. There is no mapped direct edge from the complete handler list to HitData, ActorValue, effective protection, or armor-skill award functions; do not infer a transitive negative because nine virtual calls and descendants remain. The producer virtual +0x2b8 is also untraced. No causal edge to M-0009/M-0096 or OBJ-1 is supported [CL-L330], [M-0114], [EV-0260].

EV-0515 extends the tag-0x19 producer route: `FUN_140687370` has one captured caller, `FUN_1407baca0`, and after its observed guards loads an indexed record pointer from param_1[0x3f]+0x270, invokes receiver vtable +0x2b8 with that pointer/flags, writes an actor state record through `FUN_1402e8f30`, then tail-jumps to tag-0x19 builder `FUN_1406582d0` [EV-0515], [EV-0513]. Record these ordered structural edges; they connect the callback to tag submission but do not identify its semantics or establish a HitData/ActorValue/armor-skill effect. The separately decompiled `FUN_1402e9000` body is typed void while the producer branches on its AL result; preserve the discrepancy [CL-L331], [M-0115]. Next resolve primary Actor slot +0x2b8 on the same GOG build. No Steam mapping, armor-XP edge, or OBJ-1 gate edge is supported [EV-0260].

Cross-domain synthesis for EV-0515/EV-0516: the tag-0x19 producer calls primary Actor slot +0x2b8 with an indexed record. The exact base target is FUN_1406a2cd0; its other captured callers are four callsites in FUN_1406a1bf0, an item/equipment path with equip/quest-item messages and BGSBipedObjectForm checks [EV-0515], [EV-0516]. The later tag-0x19 handler separately performs process/object hierarchy updates with `DismemberedLimb1_Head1` and `Torso` strings [EV-0514]. This creates a supported base-method item/equipment edge adjacent to the hierarchy handler, but does not identify the indexed pointer or prove that the two phases manipulate armor. Add a new OBJ-2 descendant investigation to trace FUN_1406a2cd0's direct calls toward effective protection and AV11/AV12. Do not add an edge to armor XP, M-0009/M-0096, or OBJ-1 until dataflow supports it [CL-L332], [M-0116], [EV-0260].

EV-0517 completes the direct call graph of base Actor +0x2b8 target FUN_1406a2cd0: 22 sites to 19 direct targets, four unresolved virtual calls, and four incoming callsites from the item/equipment method FUN_1406a1bf0. Its direct body includes BGSBipedObjectForm/slot-mask traversal and item/container work; no mapped direct HitData, ActorValue or armor-skill award target appears [EV-0517], [CL-L333], [M-0117]. Add a bounded item/list edge only. The four virtual destinations, descendants, producer indexed-record type, effective protection and armor XP remain open. Trace direct helper FUN_14022b7a0 next; do not infer a transitive no-hit result or add an armor-XP causal edge.

EV-0518 adds a third captured consumer of `FUN_1402e55a0`: item/list helper FUN_14022b7a0 calls it on param_4 and passes the selected result to FUN_140661f60, in addition to the tag-0x17 fallback and HitData receiver routes [EV-0518], [EV-0512], [EV-0295], [EV-0296]. Add code-reuse edges only; no same-pointer or shared downstream HitData claim. FUN_14022b7a0 also directly calls FUN_1406b98f0 and, under shared gate FUN_1406d4110, selects direct FUN_1402e90d0 or helper FUN_1406581b0. Those exact edges create a new OBJ-2 question: does the Actor getter or state helper reach effective protection or AV11/AV12? The complete direct list has no mapped HitData/ActorValue award target, but three indirect sites and descendants remain open [CL-L334], [M-0118]. No armor-XP or OBJ-1 causal edge is established.

EV-0519 maps `FUN_1406b98f0` to a one-call nested-record selector (`FUN_14070fd50`) with 69 incoming callsites across 51 functions and no direct HitData/ActorValue/armor-skill call. It reads the component at +0xf8, returns the first qword of a candidate whose marker byte is 0x29, and in the item helper path its result participates in a TESActionData-related branch [EV-0518], [EV-0519]. Add only the component -> selector -> returned entry edge; the marker type and downstream gameplay effect remain unknown. A signature mismatch leaves the selector argument register uncertain. The context consumer `FUN_140661f60` remains a separate direct edge after `FUN_1402e55a0`; trace it next [CL-L335], [M-0119].

EV-0520 synthesizes the item/list and tag-0x55 process-update routes: both call `FUN_140661f60`, which selects a hierarchy node (named context or child walk), skips `BIP`-prefixed entries, and calls `FUN_1407158f0` to update nested field +0x178 with refcount changes [EV-0520], [EV-0518], [EV-0464]–[EV-0466]. This adds a shared bounded hierarchy-state edge across two producer routes. It does not establish the same context object, selected type, HitData causality, effective armor protection, AV11/AV12 or armor XP. `FUN_1414ae8a0`, its dynamic identity `DAT_14332c3a0`, two node virtuals and +0x178 consumers remain unresolved [CL-L336], [M-0120].

EV-0521 resolves the bounded selector mechanics: `FUN_140661f60` calls recursive hierarchy search `FUN_1414ae8a0` at two sites; the search walks child records, checks a nested object at +0x128 using virtual +0x10, compares that returned identity to `DAT_14332c3a0`, and falls back to `FUN_1414ae980` when no candidate matches [EV-0521], [EV-0520]. Add structural edges from the context consumer to the selector, from the selector to the identity global/fallback, and from the chosen pointer to the existing `FUN_1407158f0` +0x178 assignment. Do not add a causal edge to HitData, ActorValues, effective protection or armor XP: the global's type/value and downstream readers remain unknown, and four selector virtual calls remain unresolved [CL-L337], [M-0121].

EV-0522 adds an address/reference observation for the selector token: GOG RVA 0x332c3a0 has 47 captured references, including a candidate WRITE xref at RVA 0x0d2f660 and overlapping DATA xref at +3, but the address-context query exposes no value or type [EV-0522]. Record the reference census and writer candidate only; add no object-type or gameplay edge until the write-site context is inspected [CL-L338].

EV-0523 prevents a false initialization edge: the candidate WRITE xref address is an unbounded generic two-field store through RCX, and its visible instructions do not name DAT_14332c3a0 [EV-0523], [EV-0522]. Keep the reference classification as a contradiction; do not add a global-writer or object-identity edge until caller/dataflow evidence ties the store destination to the global [CL-L339].

EV-0524 gives the bounded global context for +0x178: 987 hits span 722 functions, including 529 stack accesses. The exact setter FUN_1407158f0 is accompanied by nearby read candidates FUN_140715840 and FUN_140715940, but the scan does not identify their receiver type or connect their pointers to FUN_1414ae8a0 output [EV-0524], [EV-0521], [EV-0520]. Add candidate links only; the causal graph remains selector -> setter +0x178, with no edge from the field to HitData, protection or armor skill until receiver identity/dataflow is proved [CL-L340].

EV-0525 adds the first concrete selected-component consumer candidate: actor-update target FUN_140715940 conditionally reads nested +0x178, passes a nested +0x70 pointer to FUN_1414fdb10 for float computation, and then updates through FUN_1406eeb00/FUN_1406e68a0. It also calls FUN_140661f60 after FUN_1402e55a0 in another branch; two captured callers are FUN_140773750 and FUN_140734890 [EV-0525]. Add these bounded structural edges but leave reader/writer pointer identity unlinked. No HitData/ActorValue/protection/armor-XP edge is justified until FUN_1414fdb10 and update helpers are traced [CL-L341], [M-0122].

EV-0526 refines the selected-component branch: FUN_140715940 passes nested +0x178 object +0x70 to FUN_1414fdb10; that helper sums FUN_14150aea0 over a pointer/count array, where entries contribute a capped distance-attenuated float using coordinate and scalar fields [EV-0526], [EV-0525]. Add these bounded numeric/dataflow edges. The calculation supports a context/object-state route but the array type and final FUN_1406eeb00/FUN_1406e68a0 effects remain unresolved; do not link it to armor, HitData, ActorValues, or armor XP without further evidence [CL-L342], [M-0123].

EV-0527 resolves one immediate terminal operation of the numeric route: FUN_1406eeb00 has no callees and stores the FUN_140715940 float argument at (*(param_1+0x10))+0x3a8 [EV-0527], [EV-0525]. Add the value -> field +0x3a8 store edge only. The field semantics and readers remain unknown; do not connect it to ActorValues, armor protection, HitData or skill XP. FUN_1406e68a0 is the paired update still to trace [CL-L343], [M-0124].

EV-0528 adds the paired structure `FUN_140715940 -> FUN_1406eeb00 -> nested +0x3a8` and `FUN_140715940 -> FUN_1406e68a0 -> nested +0x3b0`, with the second setter receiving `DAT_14319c47c` immediately after the distance-weighted aggregate write [EV-0528], [EV-0527], [EV-0525]. This is a supported call/dataflow edge within the actor-update route. No edge is added from either field to mapped HitData, effective protection, ActorValue/AV11/AV12 or armor-skill awards; no edge is added to OBJ-1 quest/Story Manager state or M-0096 magic resistance. Those remain analogies pending a reader or shared call. Exact field meaning and reader identity are unresolved.

EV-0529 adds a candidate association, not a causal edge: `FUN_1406eeae0` reads dword +0x3a8 at RVA 0x6EEAE9, near writer `FUN_1406eeb00`, but the whole-program scan does not establish shared receiver identity or a call route [EV-0529]. Record H59 (same nested field) against H60 (offset collision); query callers/callees before adding an edge. No mapped edge to HitData, protection, ActorValue/AV11/AV12, armor XP, OBJ-1, or M-0096 is added.

EV-0530 adds getter-to-consumer routes: `FUN_1406eeae0` reads nested +0x3a8; caller `FUN_14032ada0` logs the result as “light” in a GetDetected message, while `FUN_1406807c0` uses the value in a threshold branch. The getter callers pass outer +0xf8 pointers. EV-0525 records the actor-update caller `FUN_140734890` passing its +0xf8 field expression into the writer route `FUN_140715940 -> FUN_1406eeb00` [EV-0530], [EV-0525], [EV-0527]. This supports a shared structural slot path, but not same runtime type/instance. No causal edge to M-0017 HitData/AV11/AV12 armor skill, effective protection, M-0096 resistance, or OBJ-1 quest state is supported. Preserve the decompiler argument discrepancy in FUN_1406936f0.

EV-0531 maps a shared outer slot in `FUN_140734890`: its +0xf8 field is passed to both `FUN_1406e5da0` (Actor/process update) and `FUN_140715940` (distance-weighted paired-state updater) [EV-0531]. The getter callers of `FUN_1406eeae0` also pass an outer +0xf8 value, and one logs the +0x3a8 result as light [EV-0530]. This supports structural convergence on the +0xf8 state slot across actor/process and detection/light routes. Do not equate runtime class/instance until the Actor vtable/virtual owner is mapped. No edge to M-0017 HitData/armor skill, effective protection, M-0096 resistance, or OBJ-1 quest/Story Manager state is added.

EV-0532 rules out one proposed type edge: primary `VTABLE::Actor` slot +0x718 maps to `FUN_1406b9000`, not `FUN_140734890`; RTTI is primary `.?AVActor@@`, subobject offset zero [EV-0532], [EV-0400]. No edge is added from `FUN_140734890` to primary Actor slot +0x718. Its relation to the +0xf8 getter/setter route remains structural only, pending data references or another table identity. No armor/HitData/AV/OBJ-1 edge is added.

EV-0533 records two source-less DATA references to `FUN_140734890` at RVAs 0x3660620 and 0x18ad2d8 [EV-0533]. They do not identify an owner, vtable, registration path, or edge from primary Actor slot +0x718, which maps elsewhere [EV-0532]. Add no registration/type edge yet; inspect the nearby source address. The +0xf8 relation remains structural only and adds no HitData/armor/OBJ-1 edge.

EV-0534 adds only address-context provenance for the source at RVA 0x18ad2d8: mapped address, no function, no inbound refs to that address, and no instruction at the exact address [EV-0534]. Since the qword and enclosing type are not inspected, add no type, registration, or runtime-owner edge to FUN_140734890; add no HitData/armor/OBJ-1 causal edge.

EV-0535 confirms a static data-pointer relation `RVA 0x18ad2d8 -> FUN_140734890` (VA 0x140734890), with zero captured xrefs pointing to the entry [EV-0535]. Add this address-to-function pointer relation only; do not infer table membership, registration, runtime owner or call execution. No edge to HitData/armor/OBJ-1 is justified.

EV-0536 records qword 0x735D6800734890 at RVA 0x3660620; low32 0x00734890 equals the FUN_140734890 RVA from EV-0533, while high32 0x00735D68 remains unvalidated [EV-0536]. Record only the raw data relation and unresolved split; no encoding, type, registration, runtime owner, or causal edge to HitData/armor/OBJ-1 follows.

EV-0537 places a decoded RET immediately before high-word candidate RVA 0x735D68, but the candidate itself has no function or instruction identity [EV-0537]. Add no function-boundary edge until the RET owner is identified; the EV-0536 qword split remains an unresolved data interpretation. No gameplay/HitData/armor edge is supported.

EV-0538 ties qword at RVA 0x3660620 to FUN_140734890’s code bounds: low32 equals entry RVA 0x734890; high32 equals RVA 0x735D68, immediately after a RET inside the function at 0x735D67 [EV-0538], [EV-0536], [EV-0533]. Record this code-range correspondence only; do not add a table-owner/runtime-registration edge until adjacent pattern and source use are established. No HitData/armor/OBJ-1 edge follows.

EV-0539 records adjacent qword 0x735D7001D74768 at RVA 0x3660628; high32 0x735D70 matches a decoded PUSH address after FUN_140734890’s RET, while low32 0x01D74768 remains untyped [EV-0539], [EV-0538]. This may fit a 12-byte function-range record followed by the next begin RVA, but add no table-owner/runtime registration edge until the address and record layout are verified. No combat/armor/OBJ-1 edge follows.

EV-0540 maps candidate next begin RVA 0x735D70 to FUN_140735d70 and records a DATA ref from RVA 0x366062c, 12 bytes after the candidate row at RVA 0x3660620 [EV-0540]. Add only this source-address/function relation; do not infer PE unwind section, record owner, runtime registration, or any HitData/armor/OBJ-1 edge.

EV-0541 adds a second qword candidate at RVA 0x366062c: low32 0x735D70 is FUN_140735d70 entry RVA; high32 0x735DA2 is a candidate end [EV-0541], [EV-0540]. This repeated data pattern is not yet a proven code-range array or runtime registration; no gameplay/HitData/armor edge follows.

EV-0542 places RVA 0x735DA1 inside the Ghidra-associated FUN_140735d70 context but not at an instruction boundary; preceding decoded instruction is MOV at 0x735D9F [EV-0542]. Do not add the second-row end or range-table edge until 0x735DA2 membership is checked. No runtime/HitData/armor edge is supported.

EV-0543 puts RVA 0x735DA2 inside FUN_140735d70 at a MOVAPS instruction and reports five source-less DATA refs to that address [EV-0543]. This blocks the proposed repeated range-row edge from the adjacent qword sequence. The data interpretation has no recovered owner and adds no combat/HitData/armor/OBJ-1 causal edge; return to the remaining worker-caller line.

EV-0545 adds static worker-dispatch edge `case 0x1A -> FUN_1404c2480(global,payload)` and adjacent `case 0x1B -> FUN_1404c2650(global,payload)` [EV-0545], [EV-0544]. Add only these direct dispatcher edges; no event-name, HitData, ActorValue, protection, armor-skill, or OBJ-1 causal edge is established.

EV-0546 refines the static edge `tag 0x1A -> FUN_1404c2480 -> guarded hash/list/array updates keyed by payload +0x14`; the handler has 8 direct calls, no indirect sites, and 4 callers [EV-0546], [EV-0545]. Add only that bounded state-update chain. Deeper FUN_1404ca0f0 remains open; no HitData/armor/OBJ-1 causal edge is supported.

EV-0548 refines paired worker routes: tag 0x1B reaches `FUN_1404c2650`, which conditionally removes ID +0x14 from integer array +0x100 and appends the payload pointer to +0xe8, with gated secondary child-record updates [EV-0548]. Together with EV-0544–EV-0547 this supports a static thread-gated paired registry update. Do not infer manager/type semantics, ordinary-hit meaning, or any HitData/armor/OBJ-1 edge; nested virtual release remains open.

EV-0549 and EV-0545 add the static handoff FUN_140729140 -> tag-0x1c builder FUN_140658390 -> FUN_14065b800 -> dispatcher case 0x1c -> FUN_140729140(payload,0). EV-0550 bounds the zero-argument branch: it skips three indirect virtual call sites, tests the shared thread-state gate, and on the clear path calls Actor/process update helpers including FUN_1406e5da0. Record this event/worker/update chain only. The helper has eight other direct callers and downstream update descendants remain open; no causal edge to HitData, effective armor protection, ActorValue/armor XP, or OBJ-1 is established.

EV-0551/EV-0545 add the static tag-0x1d handoff FUN_1401d4620 -> FUN_1406583d0 -> worker -> dispatcher case 0x1d -> FUN_1401d4620(object,byte1,byte2). EV-0552 links the direct branch's gated calls to the existing tag-0x1a/0x1b handlers FUN_1404c2480/FUN_1404c2650 [EV-0546], [EV-0548]. Record the bounded object-state/property and registry edges only; three indirect sites and dynamic object identity remain unknown. No causal edge to HitData, effective protection, ActorValue/armor XP, or OBJ-1 is supported.

EV-0553–EV-0557 add a bounded tag-0x21 cycle: Actor base slot +0x6c8 -> FUN_14067e960 -> generation-handle allocator -> tag-0x21 worker -> generation-checked resolver -> recovered Actor base -> virtual slot +0x6c8 -> FUN_14067e960. The gate-clear branch of the same method reaches an Actor/process nested object and FUN_140ea05c0, whose dynamic receiver +0x190/slot+0x8 target is unresolved [EV-0556]. This is a static deferred Actor continuation only; do not add a HitData, ActorValue, effective-protection, armor-XP, or OBJ-1 edge.

EV-0559–EV-0561 add the paired static water-effect route: FUN_14051d020 -> tag-0x2c/0x2d builders -> worker dispatcher cases -> FUN_14051cdd0 water-size/splash-effect setup and FUN_140525820 distance-gated coordinate-buffer writes. The producer calls the same handlers directly when the thread gate is clear. Record the spatial/effect edges; keep the +0xd8 virtual target and buffer consumers unresolved. No edge to HitData, ActorValue, protection, armor XP, or OBJ-1 is supported.

EV-0562–EV-0566 widen the tag-0x2d source set: FUN_1407ed990 copies a masked input code into its event record and, for code 0x0b on a gated branch, converges on FUN_140525820 directly or through worker tag 0x2d. FUN_1407cb9d0 is the only analyzed direct caller of FUN_1407e25b0; its direct-edge census does not reach mapped HitData/tag-0x0b/ProcessTrapHit routines. Add these producer and worker edges, but keep source-type semantics, indirect sites, coordinate-buffer consumers and runtime owner unresolved. No causal edge to protection, ActorValue, armor XP or OBJ-1 is supported.

EV-0567–EV-0571 add tag-0x2e Actor/process edges: FUN_14068b3a0 -> worker tag-0x2e -> dispatcher case 0x2e -> FUN_14068b3a0; the clear-gate branch reads/writes `*( *(process+0x10)+0x328 )` against Actor+0x260 and can invoke player image-space/sound helpers. In two parent contexts the routine is adjacent to FUN_140668f50's Health ActorValue update, a helper also used by mapped HitData handlers. Keep the Health-to-process adjacency separate from the tag-0x2e body: no direct AV11/AV12/UseSkill, armor-protection, or XP edge is added. FUN_1408044e0, dynamic +0x4c8, process-field identity, and clean Steam behavior remain unresolved.

EV-0572 refines shared FUN_1408044e0 edges: tag-0x2e FUN_14068b3a0 and HitData FUN_1406b9df0 both call the helper with code 0x1d, but the former supplies null source-data/final-pointer arguments and flag 0 while the latter supplies event data/final pointer and flag 1. Retain the shared function edge and distinct argument edges; do not collapse them into a HitData or armor-skill causal edge. Three dynamic sites remain unresolved.

EV-0573/0574 adds the tag-0x34 Actor/process route: producer FUN_1406c1d40 queues Actor coordinates under the shared gate; fallback case 0x34 uses FUN_140664b20 and virtual slots +0x18/+0x38 to update the process-selected object and clear state. The case-local targets remain unresolved. No causal edge to M-0017 armor mitigation, M-0031 skill awards, or OBJ-1 quest gates is supported.

EV-0575/0576 adds tag-0x35 object-update route: two producers choose queued or direct FUN_140ea04c0 execution on the FUN_140664b20 Actor-associated object; the helper compares the current optional object and conditionally invokes dynamic old/new-object methods before a final virtual continuation. Concrete types and targets remain unresolved. No causal edge to M-0017 armor mitigation, M-0031 skill awards, or OBJ-1 quest gates is supported.

EV-0577–EV-0579 adds tag-0x2a StartCombat route: Papyrus native `Actor.StartCombat` enters a process-backed Actor worker continuation; its player-target comparison reads Actor+`0x9d8` component `+0x18`, a bound used over `0xa8`-byte records. This falsifies a direct Actor.Level interpretation but leaves the global threshold's purpose unknown. The path does not establish quest/encounter initiation or armor-skill causality; no graph edge to OBJ-1, M-0017, or M-0031 is added.

EV-0580/0581 adds the tag-0x5d route: one producer builds a 32-bit converted-value/8-byte-payload event; the worker resolves the value and calls `FUN_1406c36e0`, which removes an object from a pointer-backed collection and updates related slots. Dynamic calls and concrete types remain unresolved. No causal edge to OBJ-1, armor mitigation, or armor-skill progression is supported.

EV-0582 identifies caller 41's native binding as Papyrus `Actor.RemoveSpell`: its wrapper converts an object handle and submits tag `0x5d`, whose matched handler removes object membership through FUN_1406c36e0 [EV-0580], [EV-0581]. This connects native dispatch, handle serialization, and Actor spell-state mutation. No causal edge to OBJ-1, HitData mitigation, or armor skill progression is supported.

EV-0584 refines Actor.DispelSpell: tag-0x5e's Actor+0xa0 helper matches a SpellItem-linked record, then sets candidate lifecycle/status state or defers the operation. Its list provider, record RTTI and terminal effect remain unresolved. No causal edge to armor protection, HitData, AV11/AV12, UseSkill, or OBJ-1 is supported.

EV-0585 refines Actor.DispelSpell's matched-record route: it sets candidate+0x7c bit 18 and calls a shared timing/status handler. The handler and candidate class are not semantically resolved, so no edge to effective armor, HitData, AV11/AV12, UseSkill or OBJ-1 is added.

EV-0586 adds a second bounded Actor-state family to the worker census: tag 0x3d routes an indexed object and flags to FUN_1406c6ee0, which selects state through unresolved virtual slots and invokes update/cleanup helpers. One producer references `iMagicEquipped`, but this does not establish armor or skill effects. No HitData/protection/AV/UseSkill/OBJ-1 causal edge is added [EV-0574], [EV-0586].

EV-0587 shows that tag 0x3f's producer immediate branch and deferred worker case converge on FUN_1405d4bf0 with the same four payload values. The helper uses unresolved object slots and nested state traversal; it has no direct mapped HitData/protection/AV11/AV12/UseSkill sink, and no OBJ-1/OBJ-2 edge is added [EV-0574], [EV-0587]. Callers 42–44 share the generic worker but retain distinct payload semantics.

EV-0588 bounds tag 0x40's FUN_14040e300 handler as a scalar/state update with a TESImageSpace-related direct helper branch and no direct mapped HitData/protection/AV11/AV12/UseSkill edge. Payload type, form provenance and transitive behavior remain unknown; no OBJ-1/OBJ-2 causal edge is added [EV-0574], [EV-0588].

EV-0589 shows that tag 0x40's producer forwards outputs of a shared typed-value decoder into the worker builder; the producer body itself does not directly read Actor/HitData state. Input provenance and decoded type remain unknown, and no OBJ-1/OBJ-2 causal edge is added [EV-0587], [EV-0588], [EV-0589].

EV-0590 records one data xref to tag-0x40 producer FUN_140357c70 at RVA 0x362ffb4, with no analyzed direct callers and no resolved containing-table semantics. The decode descriptor and runtime source remain unknown; no OBJ-1/OBJ-2 causal edge is added [EV-0589], [EV-0590].

EV-0591 compares GOG xref DWORDs for FUN_140357c70 and FUN_14040e300 with Microsoft's x64 RUNTIME_FUNCTION layout and finds matching start/end/unwind triples. The apparent table reference is likely exception metadata rather than gameplay registration; caller 45's selected decoder type and input remain unknown [EV-0588], [EV-0590], [EV-0591]. No OBJ-1/OBJ-2 causal edge is added.

EV-0592 maps tag 0x43 as a retained object+dword worker payload with seven producer functions. For sampled producer FUN_1407bacf0, gate-set queueing and gate-clear direct execution both target FUN_14069e070(object,1), matching worker case 0x43 [EV-0574]. Six producer bodies and helper semantics remain unresolved; no OBJ-1/OBJ-2 causal edge is added.

EV-0593 shows that all seven tag-0x43 producers preserve object+selector across queue/direct branches and converge on FUN_14069e070. The helper updates a three-bit object state and calls component/reference helpers, with three unresolved virtuals and no direct mapped HitData/protection/AV11/AV12/UseSkill edge. No causal edge to OBJ-1 or armor M-0009 is added [EV-0592], [EV-0593].

EV-0594 shows that FUN_140717d10 conditionally resets nested state and may route through FUN_1406671b0 to worker builder FUN_140657870. The bounded bodies expose no mapped HitData/protection/AV11/AV12/UseSkill target, but the secondary event tag remains unknown [EV-0593], [EV-0594]. No OBJ-1/OBJ-2 causal edge is added.

EV-0595 links the secondary builder from EV-0594 to dispatcher case 10: handle resolution, conditional vector state, a second handle, then an unresolved virtual callback at recipient vtable byte offset +0x870. Its type/target remain unknown, so no OBJ-1/OBJ-2 causal edge is added.

EV-0596 shows FUN_140665950 passes the same object to the tag-0x0A builder after invoking byte offset +0x4c8, which EV-0291 maps to primary Actor slot 0x99. This supports Actor-vtable compatibility for that producer route; dispatcher byte offset +0x870 remains unresolved. No OBJ-1/OBJ-2 causal edge is added.

EV-0597 resolves primary GOG VTABLE::Actor to RVA 0x189EC20 for the exact GOG 1.6.1179.0 binary/Address Library pair. This supports the pending slot 0x10e target query only and creates no gameplay causal edge.

EV-0598 resolves primary Actor slot 0x10e (+0x870) to FUN_140699500 in GOG AE 1.6.1179.0. Its broad Actor/process cleanup body still needs a complete direct-call screen; no OBJ-1/OBJ-2 causal edge is yet supported.

EV-0599 records a process-conditioned direct edge from tag-0x0A target FUN_140699500 to FUN_1406be430, the same helper called in the candidate hit/damage path EV-0429. Arguments differ and the helper lacks a confirmed AV11/AV12 sink in prior bounded evidence EV-0294, so this is a shared-code convergence only; no OBJ-1/OBJ-2 causal edge is added.

EV-0600 connects the tag-0x0A Actor state callback and candidate HitData handler to shared FUN_1406be430 while preserving their distinct arguments. The helper queries numeric ActorValue 0x24 and reaches a vector/physics-like sink, with no direct AV11/AV12/UseSkill edge. No OBJ-1/OBJ-2 causal relationship is established.

EV-0601 maps the Actor +0x50 call after FUN_1406be430 to FUN_1401dfdc0, which conditionally forwards to FUN_140606580 through a global manager pointer. The recipient/helper behavior is unresolved; no OBJ-1/OBJ-2 causal edge is added.

EV-0602 extends the tag-0x0A Actor route from its vector helper through Actor slot +0x50 into a gated manager-owned map keyed by Actor+0x14, where a selector is ORed into stored state. This bounds caller 46's direct path without linking it to HitData/protection/AV11/AV12/UseSkill or OBJ-1/OBJ-2.

EV-0603 shows caller 47's tag-0x44 deferred event re-enters FUN_1401fa010, while its gate-clear path may call FUN_1401fdb80 on an acquired object's +0x170 member. No HitData/armor-skill or OBJ-1/OBJ-2 edge is established; the recipient/helper remain unresolved.

EV-0604 shows FUN_1401fdb80 scanning/removing a pointer-array entry or deriving a key from unresolved object vtable +0x148 for FUN_140d1ed80. Its second caller arises in a float/time branch, weakening but not eliminating a combat interpretation. No OBJ-1/OBJ-2 causal edge is added.

EV-0604 shows FUN_1401fdb80 scanning/removing a pointer-array entry or deriving a key from unresolved object vtable +0x148 for FUN_140d1ed80. Its second caller arises in a float/time branch, weakening but not eliminating a combat interpretation. No OBJ-1/OBJ-2 causal edge is added.

EV-0605 traces FUN_140d1ed80 to manager-array removal for object-key -1 and unresolved manager vtable +0x1c8 for other keys. Four callers share the helper; its generic data structure does not establish gameplay effect. No OBJ-1/OBJ-2 causal edge is added.

Cross-system analogy [CL-L418]: EV-0581 (Actor.RemoveSpell/tag 0x5d) and EV-0604/EV-0605 (tag 0x44) each show reference-counted pointer-collection cleanup. They use distinct direct helpers and lack a shared RTTI/call-chain link. This is analogy only, not evidence of shared ActiveEffect or armor semantics. Falsifier/upgrade condition: demonstrate a common concrete removal target or compatible receiver RTTI reached from both producer paths. No edge to OBJ-1 is supported.

EV-0606 shows tag-0x44's FUN_1404a27f0 factory retrieving/removing global-array entries by +0x28 key; the same factory is used by two BGSDecalNode-labeled cleanup callers. This is a registry association, not exact returned RTTI or proof of game effect. It weakens a combat interpretation but does not close unresolved dispatch.

EV-0607 shows the alternate tag-0x44 factory uses a second keyed global array but shares FUN_1401fe280 with the first factory [EV-0606]. The producer decompilation omits arguments at the second call, so register parity is still unverified. This supports a shared collection primitive within caller 47, not a combat/armor or quest edge.

EV-0608 resolves identical output/key arguments to both tag-0x44 factory branches and maps another caller's child-key callback into the same producer. Together with BGSDecalNode cleanup use of the same registry [EV-0606], this supports a generic object-list lifecycle route for caller 47. Unresolved virtuals remain; no HitData/armor-skill edge is established.

EV-0609 maps caller 48's containing function FUN_140658a60 as tag 0x45 with a byte payload. Its sole caller and dispatcher case route immediate/deferred work to FUN_1401fa100 through the shared thread-state gate. The deferred argument and helper effects remain open; no OBJ-1/OBJ-2 edge is established.

EV-0610 bounds FUN_1401fa100 as a flag-dependent manager child-list cleanup/update path with dynamic +0x1c0 callbacks and no direct mapped armor-skill target. The deferred producer byte remains unresolved. No OBJ-1/OBJ-2 causal edge is added.

EV-0611 confirms immediate and deferred caller-48 tag-0x45 paths both use selector byte 1 before reaching FUN_1401fa100. This closes the payload-parity ambiguity while leaving dynamic object callbacks open. No OBJ-1/OBJ-2 edge is established.

EV-0612 maps caller 49's tag-0x48 object/pointer-pair payload to a dispatcher list-iteration route through unresolved object vtable +0x10 and FUN_14054e390. The builder's sole data xref remains unclassified; no OBJ-1/OBJ-2 edge is established.

EV-0613 identifies `FUN_14054e390` as a generic list-entry virtual callback primitive shared by four callers, including dispatcher case 0x48. This is structural evidence only; no armor-skill or quest-gate causal edge is established.

EV-0614's three neighboring DWORDs at caller 49's sole data xref match the x64 `RUNTIME_FUNCTION` begin/end/unwind-info layout previously tested in EV-0591. The reference is likely unwind metadata rather than gameplay registration; its exact PE section is unverified. No OBJ-1/OBJ-2 causal edge is added.

EV-0615 maps caller 50's tag-0x49 retained-object event to a producer with list callbacks and immediate/deferred paths. This is a structural route with unresolved type/virtual semantics; no HitData, armor-skill or quest-gate causal edge is established.

EV-0616 bounds the caller-50 producer to an object/list-conditioned immediate-or-queued update with 7 unresolved virtual calls and no direct mapped hit/armor-skill sink. Its source-less xref at RVA `0x18bb248` lies among code-pointer qwords, suggesting candidate vtable base `0x18bb240`; RTTI identity is pending. No causal edge is added.

EV-0617 joins caller 50's slot-1 function pointer to RTTI-identified primary vtable `AddRagdollHandler`. This is a static type identity edge only; trigger and gameplay-effect edges remain unsupported.

EV-0618 links AddRagdollHandler slot-1's immediate `+0x1a8` virtual operation to its queued tag-0x12 dispatcher route by matching receiver/object/flags/selector; the final argument still needs disassembly. This is a control-flow convergence edge only, with target/effect unresolved.

EV-0619 refines EV-0618: immediate and tag-0x12 paths use the same slot and pointer roles but have different visible argument setup. Exact call parity is falsified; inherited worker context and target semantics remain unknown.

EV-0620 shows the worker wrapper explicitly forwards only the event pointer to `FUN_140659160`; it supplies no proven extra event arguments for case 0x12. This supports rejecting a payload-parity claim while leaving virtual target behavior unresolved.

EV-0621 establishes that AddRagdollHandler tag-0x49 producer/dispatcher and actor/process routine `FUN_140699500` directly reuse `FUN_14054e340`, an any-match list-predicate helper. This is a shared native primitive, not evidence that the caller families share hit, armor-skill or quest-gate behavior; no causal edge is added.

EV-0621 establishes that AddRagdollHandler tag-0x49 producer/dispatcher and actor/process routine `FUN_140699500` directly reuse `FUN_14054e340`, an any-match list-predicate helper. This is a shared native primitive, not evidence that the caller families share hit, armor-skill or quest-gate behavior; no causal edge is added.

EV-0622 identifies caller 50's first list pass as per-entry virtual `+0x28` side-effect callback plus a seen-entry flag; the same helper is used by `FUN_140713d90`. The helper relationship is structural and does not identify HitData/armor behavior.

EV-0623 shows caller 50 selects its `+0x1a8` receiver via an optional-object lookup or global fallback keyed by bit 0 at subobject `+0x40`. Receiver type and slot target remain unresolved; no HitData/armor edge is added.

EV-0624 maps `FUN_140179080` as a bitmap-gated, thread-local-cached numeric-key lookup over holder entries. Caller 50's optional branch requests key 1 and obtains the entry's `+0x10` object through `FUN_1401699e0` [EV-0623–EV-0624]. Concrete type and `+0x1a8` target remain unresolved; no HitData/armor edge is added.

EV-0625 shows `DAT_1420f9d28` is zero in the static image, with 47 direct reads, an `RDI` assignment from `FUN_1402c65b0`, and a zeroing write from `FUN_1402c6720`. This identifies runtime-populated storage but not the receiver type or virtual `+0x1a8` target; trace assignment provenance before adding a class or gameplay edge.

EV-0626 connects the global fallback setter to `FUN_1402c6810`: it uses a three-dword global input, stores the result inside the holder placed in `DAT_1420f9d28`, and its sole analyzed direct caller has a nonzero-argument gate. This narrows construction provenance, but type and `+0x1a8` target remain unresolved [EV-0623], [EV-0625–EV-0626].

EV-0627 ties caller 50's global fallback to the GOG symbol-labeled `bhkWorldM` class through the zero-argument factory branch and constructor vftable assignment. Its virtual slot `+0x1a8` remains unresolved; the class edge narrows dispatch context but adds no HitData/armor-skill edge [EV-0623], [EV-0626–EV-0627].

EV-0628 recovers the bhkWorldM vtable pointer written by `FUN_140ebdf30`: GOG VA `0x1419e9078`, RVA `0x19e9078`. Validate RTTI and inspect slot `0x35` (+`0x1a8`) before adding method or gameplay edges [EV-0626–EV-0628].

EV-0629 validates GOG vtable RVA `0x19e9078` as primary `.?AVbhkWorldM@@` RTTI at subobject offset zero. Caller 50's fallback class is supported; its slot `0x35` (+`0x1a8`) and gameplay effect remain open [EV-0627–EV-0629].

EV-0630 resolves bhkWorldM slot `+0x1a8` to `FUN_140e884d0`, whose sixth argument controls whether a `FUN_140e0f510` state/bit eligibility check runs. Immediate AddRagdollHandler supplies zero; deferred case setup leaves inherited values unknown [EV-0619], [EV-0620]. Record this as a candidate route-control edge only; no direct HitData/armor skill edge is shown.

### EV-0631 corrects AddRagdollHandler tag-0x12 argument setup

The earlier parity mismatch came from assigning the `0x65939c` call (case `0x4`) to case `0x12`. The actual case-0x12 call at `0x659c92` constructs the same six argument positions as the immediate AddRagdollHandler call, including argument six equal to zero [EV-0631], [CL-L444], [M-0184]. This corrects a native control-flow/argument edge and falsifies the proposed eligibility-bypass mechanism. It adds no causal edge from AddRagdollHandler to HitData, protection or armor skill; callback/runtime outcomes remain open.

### EV-0632 maps caller 51 tag-0x4b to PlayerCharacter state updates

Caller 51 builds tag 0x4b with a byte; dispatcher case 0x4b passes that byte and verified PlayerCharacter global `DAT_143188918` to `FUN_140738380` [EV-0632], [EV-0344]. The bounded route updates paired object `+0xf4` flags and PlayerCharacter `+0xbe3` behind primary slot `+0x4c8` state checks at `+0xc8`, then uses nested keyed-object callbacks. The recursive helper has no direct HitData/protection/AV11/AV12/UseSkill edge; ten producer virtual sites remain unresolved. This is a bounded state edge, with no causal OBJ-2 edge [CL-L445], [M-0185].

Cross-caller synthesis: caller 50 fallback construction and caller 51 callback setup both reference the same adjacent tuple `DAT_1432740d8..+8`, but pass it to different helpers [EV-0626], [EV-0632]. Treat this as a shared-configuration lead only; exact schema/common mechanism is unproved. Next trace `FUN_140cb4ae0`.

### EV-0633 disambiguates the shared DAT_1432740d8 tuple consumers

Caller 50's fallback factory consumes the tuple as object-configuration input and replaces the third field with zero on its false branch. Caller 51's helper copies all three supplied dwords into queued event metadata. The direct helpers and transformations differ; reuse of one global input does not establish a shared registration/update mechanism [EV-0626], [EV-0632], [EV-0633], [CL-L446], [M-0186]. The address query reports 1,349 references to the first dword but exposes no initialized values. **No causal edge is added** from this tuple to HitData, protection, armor XP or quest gates because the captured paths contain no data/control edge to those mechanisms and the tuple semantics remain unknown. Continue caller 52/62 `FUN_140658be0`.

### EV-0634 maps caller 52 tag-0x56 to retained-object collection callbacks

Caller 52 queues tag 0x56 with a retained object. The sole analyzed producer wrapper tests the shared queue gate, then either enqueues the object or invokes slot +0x138 directly. Deferred case 0x56 performs keyed manager collection work before invoking the same object slot. Its only analyzed producer source is an array walk/refcount cleanup path under `FUN_140643ec0` [EV-0634]. This supports a bounded lifecycle/object-list mechanism. **No causal edge is added** to HitData, effective armor protection, AV11/AV12, UseSkill or armor XP because the target slot is unresolved and the captured direct route contains no mapped sink [CL-L447], [M-0187]. Continue caller 53/62 `FUN_140658c10`.

### EV-0635 maps caller 53 tag-0x50 from Actor slot 0x89 to process state

Primary `VTABLE::Actor` slot 0x89 (`+0x448`) emits tag 0x50 with a retained object pointer [EV-0400], [EV-0635]. The dispatcher passes that object through a thunk to `FUN_1402ec610`; its entry guard skips PlayerCharacter receivers, and its bounded direct body performs Actor/process and object-state work [EV-0344], [EV-0635]. **No causal edge is added** to HitData, protection, AV11/AV12, UseSkill or armor XP because no direct mapped sink is present and 17 dynamic virtual sites remain unresolved [CL-L448], [M-0188]. Continue caller 54/62 `FUN_140658c50`.

### EV-0636 maps caller 54 tag-0x54 spatial/context state

In GOG AE 1.6.1179.0, producer FUN_14066b6e0 uses process and horizontal grid predicates before building tag 0x54; case 0x54 calls FUN_1402eb6f0, whose complete direct census has 63 edges and 21 unresolved virtual sites [EV-0636]. This route also has a tag-0x32 immediate/deferred branch converging on Actor slot +0x328/FUN_140666770, which uses FUN_1402e55a0 and recursive helper FUN_140e88c50 [EV-0636], [EV-0400]. The selector is also used by the HitData receiver and tag-0x17 route [EV-0295], [EV-0296], [EV-0512]; the recursive helper is independently mapped on tag 0x3C [EV-0483]–[EV-0486]. These are verified shared-code edges, not a causal edge: no same runtime pointer, HitData effect, protection change, AV11/AV12 award, or armor XP effect is shown. H47 is supported as conservative code-reuse model; H46 remains proposed pending runtime identity evidence. Continue caller 55/62 FUN_140658c90.

### EV-0637 maps caller 55 tag-0x57 numeric registry route

Caller 55's sole producer gates literal categories 0x18–0x1A against supplied values and limit globals, sets per-category bits, and submits codes 0xFC–0xFE as tag 0x57 [EV-0637]. Dispatcher case 0x57 reaches FUN_140971910, a six-direct-call, zero-indirect numeric lookup/initialization helper [EV-0637]. Category/code names and downstream meanings are unverified. The bounded direct route has no mapped HitData/protection/AV11/AV12/UseSkill sink. No causal edge is added; continue caller 56/62 FUN_140658cc0.

### EV-0638 maps caller 56 tag-0x58 PlayerCharacter perk-rank cleanup

Caller 56 tag 0x58 reaches PlayerCharacter collection removal; the conditional +0x4b8 path uses RTTI-verified BGSPerk::FindPerkInRanksVisitor and a direct pointer-match method to locate/remove a matching rank entry [EV-0344], [EV-0637], [EV-0638]. The runtime PlayerCharacter virtual override at +0x650 remains unresolved. **No causal edge is added** to perk eligibility/granting, HitData, protection, AV11/AV12, UseSkill, armor XP, or quest gates. Continue caller 57/62 FUN_140658d00.

### EV-0639 maps caller 57 tag-0x5F perk-rank addition

The AddPerkVisitor route and caller 56's FindPerkInRanksVisitor cleanup both use PlayerCharacter rank-list field +0x4b8 [EV-0638], [EV-0639]. Caller 57 adds or updates a rank entry under a perk rank-count bound and dispatches old/new rank bytes to unresolved callbacks; caller 56 conditionally removes a matched entry. This is a shared list lifecycle, not proof of a level-one perk grant or shared quest/combat cause. No causal edge is added to OBJ-1, HitData, effective protection, AV11/AV12, UseSkill, or armor XP. Claim mapping: CL-L451/CL-L452 -> M-0191/M-0192.

### EV-0640 maps caller 58 tag-0x5A coordinate state

Caller 58's tag 0x5A reaches a handle-keyed spatial manager. Its two producers include primary Actor slot 0x9C threshold logic and a keyed collection cleanup path called from Havok contact-pair processing [EV-0640]. The manager reads Player/object coordinates and keeps 13 indirect callbacks unresolved. This shares only a broad spatial/physics domain with caller 54's Actor context work; no common object, manager, quest predicate, HitData field, protection calculation, or armor-skill writer is established [EV-0636], [EV-0640]. No OBJ-1/OBJ-2 causal edge is added. Claim mapping: CL-L453 -> M-0193.

### EV-0641 maps caller 59 tag-0x5B disarm-related Actor action

Caller 59's producer queues two object handles under an object bit-13 gate, then runs a separate immediate state/update helper. Deferred case 0x5B resolves both handles, applies a primary Actor slot +0x658 operation, and emits “You have been disarmed.” for the PlayerCharacter branch [EV-0400], [EV-0641]. The actor method retains 16 unresolved virtual sites. This connects to the shared Actor table identity and worker transport only; no causal edge to OBJ-1 level gates, HitData protection, AV11/AV12, or armor XP is established. Claim mapping: CL-L454 -> M-0194; no OBJ-1/OBJ-2 graph edge.

### EV-0642 connects caller 60 tag-0x5C to mapped HitData context

Caller 60 tag 0x5C is produced by mapped HitData handler `FUN_1406b9df0`; it clones handler fields with `FUN_1407dce10`, then dispatches to `FUN_1406be2c0`, which calls the same `FUN_1406be430` helper used in the producer's alternate direct branch [EV-0295], [EV-0296], [EV-0431], [EV-0642]. EV-0600 maps that helper to a vector/physics-like operation and numeric ActorValue query 0x24, with no direct AV11/AV12/UseSkill sink [EV-0600]. This is a supported HitData-to-shared-helper relationship; it does not connect to effective armor protection or XP. No OBJ-1/OBJ-2 edge is added. Claim mapping: CL-L455 -> M-0195.

### EV-0643 maps caller 61 tag-0x61 eye texture update

Caller 61's producer validates a target 3D, eye-tagged headparts, and eye geometry, then sends a geometry/TextureSet pair through tag 0x61 [EV-0643]. The dispatcher conditionally replaces a nested texture pointer and invokes geometry/resource callbacks. This follows caller 60's HitData-derived shared helper as an independent rendering system; the worker is shared transport, not a gameplay cause. No OBJ-1/OBJ-2 causal edge is established. Claim mapping: CL-L456 -> M-0196.

### EV-0644 maps caller 62 tag-0x62 shared Actor handler

Caller 62's tag-0x62 producer `FUN_1406c72d0` routes through the worker dispatcher to `FUN_1406bc400`; the exact target is also called by mapped HitData handler `FUN_1406b9df0` [EV-0644], [EV-0295], [EV-0296]. This is a supported code-reuse edge, not proof of equal runtime events or arguments. The target's Actor/process action helper and bounded direct call body add no mapped level gate, protection, AV11/AV12 or UseSkill relationship [EV-0644]. Preserve a no-edge rationale from this route to OBJ-1/OBJ-2; the clean Steam matched-hit observation remains decisive [EV-0260]. Claim mapping: CL-L457 -> M-0197.

### EV-0645–EV-0652 connect a level-8 clothing-list candidate to a separate GOG effect-resistance path

Official records place ARMO `000FC061` in the Resist Magic necklace LVLI at levels 8–11 and nest that list under `LootCitizenPocketsCommon`; Madesi is a level-8 NPC record referencing the common pocket list [EV-0646]–[EV-0648]. This is a candidate route to an item from a level-one player only if runtime list resolution supplies a qualifying request level; no actor-level/player-level edge is established. Keep the competing request-level models in C-OBJ2-Q80-NPC-INVENTORY-REQUEST-LEVEL.

The clothing enchantment modifies AV44, and the GOG Actor `MagicTarget::CheckResistance` consumer is now tied to an exact slot +0x50 call from `FUN_1406c68d0` on the `Actor+0xA0` subobject; the function applies the return factor to target-effect values [EV-0398], [EV-0400]–[EV-0402], [EV-0650]–[EV-0651]. This strengthens the static effect-resistance route and its separation from the positive-DNAM HitData AV11/AV12 armor-skill selector [EV-0222]. It does not establish a live attack, Health delta, physical armor rating/protection, or zero armor AVSK.

Cross-domain synthesis: `FUN_1407ee620` calls both the resistance evaluator and `FUN_1406be430`, a vector/physics-like helper also called from mapped HitData code [EV-0600], [EV-0652]. The captured argument structures differ and the shared helper has no direct AV11/AV12/UseSkill sink in the bounded review. Preserve the function-reuse edge, but add no causal edge from magic resistance to physical-hit armor XP or from this record-list candidate to OBJ-1 quest/encounter gates. Claim mapping: CL-L458–CL-L460 -> M-0198; no OBJ-1/OBJ-2 prize edge.

### EV-0654 opens a shared Dragonborn cultist event-path discriminator

The official-five-master native QUST export shows `DLC2CultistAmbush` (`Dragonborn.esm:0403546D`) has event `CLOC`, stage indexes 1/10/255, and six CTDA function rows with no `GetLevel`. The same record attaches `DLC2WE09ActorScript` and `DLC2WECultistAmbushPlayerScript`, references `DLC2MQ01` (`04017F8E`), and stores `DLC2WE09Chance` (`04033C24`) [EV-0654]. This conflicts with treating the UESP labels as proof of two independent routes and motivates C-OBJ1-Q81-CULTIST-AMBUSH-ROUTE-IDENTITY. It does not map the Story Manager source, script predicates, or quest-start transition. **No causal edge is added** from this QUST to level-one initiation or from the secondary-source threshold to the main-quest path until the event/node/script chain is resolved. Claim CL-L461; keep OBJ-1 runtime proof under EV-0260.

### EV-0655–EV-0669 resolve separate cultist branches and a location alternative

The five-master records show distinct routes: CLOC `DLC2CultistAmbushNode` selects QUST `DLC2CultistAmbush`, while SCPT `DLC2WEPriorityQuests`/`DLC2WENode` selects QUST `DLC2WE09` [EV-0656], [EV-0658], [EV-0664]. Their loose stage-10 PSC fragments share a `DLC2MQ01.Start`/wait, objective-alias fill, `DLC2MQ01.SetStage(5)`, and chance-global write, but this shared source handoff does not make the QUSTs or event branches identical [EV-0663].

`DLC2WE09`'s condition rows encode GetLevel >=25 and GetInCurrentLoc Solstheim with OR set on both rows [EV-0657], [EV-0665], [EV-0666]. The build-identified GOG 1.6.1179.0 evaluator groups consecutive OR rows and combines that group with preceding AND conditions; applying it yields the bounded expression earlier chance/stage predicates AND (GetLevel >=25 OR Solstheim location) [EV-0667]–[EV-0669]. This is a GOG static inference applied to official five-master data, not a Steam RVA transfer or proof of evaluation timing, natural level-one world encounter, or QUST startup. EV-0260 remains the separate Steam test requirement.

Cross-domain synthesis: the quest route and OBJ-2 armor route share no verified record, ActorValue, ActiveEffect, serialization field, or native call edge. The QUST condition evaluator is generic engine infrastructure, but no evidence connects it to the HitData protection/AV11/AV12 sequence. Preserve an explicit no-edge from CL-L462–CL-L464/M-0199 to M-0017/M-0198; do not promote shared engine provenance into a causal mechanic.

### Q-0082/Q-0084 — mitigation, selector handlers, and the unblocked armor-skill scan (EV-0670–EV-0685)

The GOG path snapshots physicalDamage, applies AV39/armor-factor mitigation to totalDamage, then returns through synchronous builder callbacks into FUN_1406bcaa0. The resolver performs the player-receiver unblocked worn-ARMO scan and AV11/AV12 award branch in that same function; its later FUN_1406b9df0 call is a separate health/trap continuation [EV-0670], [EV-0673]. The selector 0x25/0x27 visitor runs synchronously [EV-0671]. Historical correction: CL-L466 is retracted/superseded by EV-0683; EPFT was incorrectly treated as the handler ID, and the original row payload evidence remains valid. The retracted claim is retained here so the transaction history remains linked. Correction EV-0683 establishes that BGSEntryPointPerkEntry returns the handler ID from DATA[1], while EPFT chooses the function-data class; the 23 file-level official rows use IDs 1/3/14 and EPFT classes 1/2 [EV-0675], [EV-0683]. IDs 3/14 perform numeric-result calculations, and ID14 reads AV index 138 through ActorValueOwner [EV-0684].

Causal path retained: HitData mitigation -> synchronous selector visitor -> numeric result -> receiver worn-ARMO scan -> AV11/AV12 UseSkill, bounded to the GOG 1.6.1179.0 source and raw official five-master rows [EV-0670]–[EV-0685]. The ID14 getter may populate per-Actor and ActiveEffect derived-value caches on a miss. The captured direct cache stores do not write the source permanent/temporary/damage AV values, equipment, HitData, UseSkill/AVSK, or event state; the ActorValueInfo+0x68 callback for runtime AV138 remains unresolved [EV-0685].

Explicit no-edges: no causal edge from Q82/Q84 to OBJ-1 or Q81's Story Manager/condition path; no edge from cache maintenance or numeric selector results to a measured protection/AVSK result; and no edge from the AV9 route to a qualifying OBJ-2 outcome until EV-0260's landed-hit, positive-protection, and numeric XP measurements exist. Claim mapping: CL-L465, CL-L467, CL-L471, CL-L472, CL-L473 -> M-0200.

### Q-0085 — location alternative, event selectors, and ferry access screen (EV-0389–EV-0390, EV-0657–EV-0669, EV-0686–EV-0687)

The world-event causal chain is a Solstheim placed DLC2WETrigger/WETriggerScript event submission -> SMEN 0001379A Script Event parent -> SCPT priority and DLC2WENode keyword selectors -> QUST DLC2WE09 condition list [EV-0389], [EV-0390], [EV-0661], [EV-0662], [EV-0664]. The source condition model is event-chance AND MQ105 >= 160 AND DLC2MQ06 < 550 AND (GetLevel >=25 OR current location is Solstheim); the <550 row is a stage ceiling, not a completion prerequisite [EV-0657], [EV-0665]–[EV-0669]. The GOG evaluator supports the OR grouping only as a cross-build static inference. The official selectors and trigger path have no additional explicit player-level predicate in the bounded screen [EV-0686].

The source-ordered six INFO rows below DLC2DRRGjalundPassageWindhelmTopic contain no function index 80; this association is based on DIAL TIFC and file offsets, not native xEdit export [EV-0686]. Revision-pinned UESP describes a before-cultist 250-gold ferry route and a distinct post-cultist dialogue check, without claiming a level-one start [EV-0687]. This supports a conditional sub-25 location candidate, not a natural level-one Steam quest-start result. MQ105 >=160 reachability, chance state, evaluator timing, active-profile winners, and alias fill remain under EV-0260.

Cross-domain synthesis: the quest/event route shares no identified causal call or state with M-0200/M-0017's combat protection and skill-award path. No OBJ-2 edge is added. Claim mapping: CL-L462–CL-L464 and CL-L474 -> M-0202.

### Q-0083 — CLOC initiation, world encounter, and serialized cultist actor chain (EV-0654–EV-0680)

Record/source graph: Skyrim CLOC parent -> `DLC2CultistAmbushNode` -> QUST `DLC2CultistAmbush`; separate Skyrim SCPT parent -> `DLC2WEPriorityQuests`/`DLC2WENode` -> QUST `DLC2WE09` [EV-0654], [EV-0656]–[EV-0664]. The `DLC2WE09` serialized level/location rows form a GOG-evaluator-backed OR group after earlier chance/stage conditions [EV-0657], [EV-0665]–[EV-0669]. The screened CLOC records and loose PSC fragments contain no explicit pre-start `GetLevel`; this remains a bounded static result rather than natural runtime proof.

Serialized actor-record graph: CLOC alias NPC_ records -> intermediate `DLC2LvlCultist*` NPC_ records -> `DLC2LCharCultist*` LVLN roots -> level-1 child LVLNs -> NPC_ leaf records [EV-0677]. Root LVLNs encode `LVLF=0x03` and thresholds through 46; level-1 child leaves encode actor level 12. These are source-record relationships, not evidence that the CLOC alias-fill path selects those bases. GOG's TESNPC template-copy override uses a base-template pointer, per-field mask and ACBS `UsesTemplate` branch [EV-0678]; its generic code is not connected to these exact Steam alias records. Schema references label fields only [EV-0680].

Explicit no-edges: no causal edge from the serialized actor chain to QUST initiation or a verified level-one encounter; no edge from the CLOC/world/template mechanism to M-0200/M-0017 or OBJ-2 armor protection/XP; no edge from generic GOG TESNPC template-copy code to Steam runtime selection. Keep H3/H4 in C-OBJ1-Q83 and preserve the level-one alias-fill observation under EV-0260. Claim mapping: CL-L468, CL-L469, CL-L470 -> M-0201.
### Q-0084 — handler field correction and ActorValue cache side effect (EV-0681–EV-0685)

EPFT is not the handler ID. BGSEntryPointPerkEntry returns DATA[1] as the function ID and separately returns its function-data pointer; EPFT selects OneValue/TwoValue [EV-0681]–[EV-0683]. Official selector rows therefore select handlers 1/3/14. Handler 3 multiplies the numeric result using OneValue data. Handler 14 uses TwoValue data to read AV index 138 and coefficient about 0.01, then scales the numeric result [EV-0684].

Handler 14's ActorValue read is not memory-pure: a cache miss can fill Actor+0x150 and ActiveEffect-manager+0x30 derived-value caches [EV-0685]. The bounded captured stores are cache stores, not direct source AV, equipment, HitData, XP, or event writes. The default-value callback behind ActorValueInfo+0x68 is unresolved for runtime AV138 because the static image does not initialize the global pointer table. Keep this as an explicit uncertainty; no gameplay or Steam result follows. No OBJ-1 causal edge is added.

### EV-0688–EV-0690 — Pending level, stored getter, and armor-skill XP convergence

The revision-pinned local UESP page supplies only secondary grounding for pending versus accepted level-ups [EV-0688]. GOG AE 1.6.1179.0 code shows Actor::GetLevel reading the stored 16-bit ActorBaseData level field (with a flagged PCLevelMult branch), while the resolved skill-progress routine tracks skill progress and separate cumulative character-level XP [EV-0689]. Claim CL-L475 maps this bounded getter.

A later exact GOG query resolves the Player receiver branch in FUN_1406bcaa0: its unblocked worn-armor selector reaches vtable byte offset +0x7b8, slot 0xF7, with armor skill 11/12 and calculated points. The slot target checks positive points and enters the same skill-progress helper [EV-0221], [EV-0670], [EV-0674], [EV-0689], [EV-0690]. This is a supported causal edge from the bounded HitData armor-skill route into cumulative character-level XP progression (M-0200 -> M-0204 -> the skill-progress arm of M-0203). It may be relevant when a level-one player accumulates hit-earned skill progress, but no pending-level timing, GetLevel field write, live ordinary hit, or Steam result is established.

Keep separate: no causal edge is established from the stored GetLevel field to effective armor protection or to suppression of AV11/AV12. The GOG code link does not validate a vanilla level-one bypass or OBJ-2 exploit. Preserve EV-0260 for the Steam before-threshold/pending/accepted and matched-hit/protection/raw-AVSK observations. Claims CL-L475–CL-L476; mechanisms M-0203–M-0204.

### Q-0087 — StatsMenu level writer and armor-skill XP bridge (EV-0691–EV-0694)

The exact GOG setter FUN_1401d7ba0 writes the 16-bit `TESActorBaseData+0x10` field read by GetLevel. Its threshold writer FUN_14077d650 reads Player GetLevel+1 after the shared progress pair is due, emits `UILevelUp`, and calls that setter [EV-0691]. RTTI and the vtable slot table identify FUN_1409611e0 as StatsMenu::ProcessMessage slot 4; the pinned CommonLib declaration maps type 0 to `kUpdate` [EV-0692]. A later lifecycle trace corrects EV-0692's constructor attribution: FUN_1409607f0 is the constructor, FUN_140960d40 is a cleanup/destructor body, and FUN_1400bc3f0 registers `StatsMenu` with factory FUN_14096e280 [EV-0693]. The correction does not change the RTTI or slot-4 identity.

Cross-domain causal chain: the unblocked Player HitData route selects armor skill AV11/AV12 and sends positive points through PlayerCharacter slot 0xF7 to FUN_140739050 [EV-0670], [EV-0674], [EV-0690]. That target passes PlayerCharacter+0x9b8 into FUN_14077d090, which mutates the accumulated progress float. StatsMenu's update path loads the same Player+0x9b8 pointer; its threshold predicate compares the same inner float pair, and its due path writes the stored Player level [EV-0689], [EV-0691], [EV-0692], [EV-0694]. This establishes a bounded GOG static edge from hit-earned armor skill points to level progress and then to the GetLevel field when the threshold is due and a StatsMenu `kUpdate` runs.

The user-action timing remains unresolved: the static map does not establish whether opening StatsMenu or its update is itself acceptance, nor whether a distinct callback runs earlier. Two other setter paths and the registrations for FUN_140356a10/FUN_140355210 remain partially unclassified. Keep the Steam pending-before-acceptance observation and exact profile order under EV-0260. No causal edge from this chain to positive physical protection or a zero-armor-XP bypass is established. Claims CL-L477, CL-L478, CL-L479; mechanisms M-0203, M-0204, M-0205, M-0206.

### Q-0088 — equal displacement does not establish StatsMenu field identity (EV-0695)

The GOG analyzed-memory-operand scan for `+0x325` has five matches: the StatsMenu `ProcessMessage` read, a set-true wrapper, a byte-zero write in an unresolved large routine, a comparison, and a separate no-function store at RVA `0x9628B9` [EV-0695]. The set-true wrapper's only analyzed caller is `FUN_1406C8D10`, whose bounded body performs soul-gem inventory selection and Player-facing soul-capture feedback. Its target object's dynamic class is not identified. The independent store at `0x9628B0` has no analyzed incoming xrefs and is absent from the first 64 entries read from the RTTI-identified StatsMenu vtable. This is not a complete-vtable negative or proof of unrelated ownership.

Cross-domain assessment: displacement is an address-level search key, not a typed field identity. No supported causal edge connects the soul-capture write, the unbounded code store, and StatsMenu's `+0x325` state check. EV-0695 therefore does not add or retract the Q87 armor-skill-to-level-progress causal bridge [EV-0694]; it narrows only the candidate state-writer interpretation. The extra Player level-writer tables also remain unresolved. Keep Q88's timing models open and EV-0260's natural Steam pending/interface-open/accepted observation as the decisive runtime test. Claim CL-L480; no new mechanism or OBJ-1/OBJ-2 prize edge is added.


### Q-0089 — selector-0x55 adjusts cached item armor rating (EV-0696–EV-0698)

The GOG 1.6.1179.0 PlayerCharacter cached armor-factor visitor passes a candidate non-clothing item rating through Actor slot 0x100 / selector 0x55 before cache accumulation [EV-0311], [EV-0696]. The exact official five-master screen contains three SetValue-zero rows and 28 positive multipliers; Dragonhide and Earth Stone MGEFs each name a corresponding zero-setting perk in `Perk to Apply` [EV-0697]. This supports a bounded code-to-record candidate route for setting a per-item cache contribution to zero. It does not establish active-effect lifetime, final effective protection, profile winners, or Steam behavior.

No causal edge is added from selector-0x55 cache adjustment to the unblocked HitData armor-skill award. Existing GOG evidence places armor AV11/AV12 routing in a separate resolver that scans positive raw ARMO DNAM ratings [EV-0670], [EV-0690]; Q-0090 tests whether its points input is a pre-mitigation HitData field. UESP's Dragonhide description is retained only as a secondary lead [EV-0698]. Claims CL-L481, CL-L482, and CL-L483; mechanism M-0207. The exact cross-system falsifier is a source path showing selector 0x55 changes the armor-award points/eligibility input, followed by EV-0260 runtime protection and raw-AVSK measurement.


### Q-0090 — armor mitigation and armor XP read different HitData fields (EV-0699)

The bounded GOG builder/mitigation path copies the current HitData `+0x50` value to `+0x54` before later target-side AV39/armor-factor reductions to `+0x50`. The Player resolver's unblocked armor branch screens for positive raw ARMO DNAM, then passes `+0x54` to the armor skill UseSkill slot [EV-0670], [EV-0690], [EV-0699]. This supports a causal edge from builder snapshot to the armor award points argument and a separate edge from raw equipment DNAM to award eligibility.

Selector `0x55` is directly observed only in the cached per-item armor-factor path [EV-0696]; it is not explicitly dispatched in the captured HitData builder/mitigation bodies [EV-0699]. Therefore this static scope does not support selector-0x55 zeroing as a direct way to suppress the armor points input. This is not a global negative: selectors `0x1A`, `0x1C`, `0x00`, `0x23`, `0x24`, `0x12`, `0x01`, `0x11`, and `0x02` occur before the `+0x54` copy and are the subject of Q91. No live protection/AVSK result or Steam transfer is established. Claims CL-L484 and CL-L485; mechanism M-0208. The falsifier is a direct pre-snapshot/data path showing selector `0x55` or an MGEF-linked zero row changes `+0x54`, followed by a matched Steam hit with positive armor protection and raw AVSK.


## Q-0091 synthesis — one conditional player-side zero before the armor points snapshot (EV-0700–EV-0702)

The five-master selector screen found one Player-applicable zero row in the pre-snapshot incoming-damage path: DeftMovement. If its conditions hold, selector `0x24` multiplies HitData `+0x50` by zero before the builder copies that value to `+0x54`; the PlayerCharacter UseSkill wrapper rejects non-positive points [EV-0221], [EV-0699], [EV-0701]. This supports a conditional static edge from DeftMovement entry-point data to the armor points input and then to the positive-points guard.

The route is intermittent and is described as damage avoidance. It does not show a qualifying hit where worn armor supplied positive protection, repeated zero Heavy/Light AVSK, or level-one acquisition. The raw five-master reference scan attaches the other zero rows to non-player actor/content candidates [EV-0700]. No causal edge from this finding to OBJ-1, positive armor protection, or a completed OBJ-2 solution is added. A distinct next question is whether the downstream `Mod Skill Use` route can zero skill credit after a positive hit-points input while remaining separate from the protection calculation. Claims CL-L486–CL-L487 -> M-0209.


## Q-0092 synthesis — a separate award-side modifier exists, but no official zero row was found (EV-0703–EV-0704)

The captured PlayerCharacter route separates the incoming-hit points gate from skill-credit calculation: positive points enter the skill helper; AVIF `useMult`/`offsetMult` and EntryPoint 22 (`kModSkillUse`) are applied before the per-skill progress field is updated [EV-0221], [EV-0700], [EV-0703]. The five-master Heavy/Light coefficients are nonzero, and the complete official EP22 screen has only positive amounts [EV-0262], [EV-0704].

This makes award credit structurally separable from the earlier HitData/protection computation, but the screened official source records provide no zero/negative modifier. No causal edge from the award visitor to positive protection or an observed zero AVSK is added. Q91's DeftMovement route acts earlier by zeroing incoming damage on a conditional proc; Q92's downstream route is distinct, and neither is a qualifying OBJ-2 result. No OBJ-1 edge is added. Claims CL-L488–CL-L489 -> M-0210.
