# Legacy mechanism ledger

Stable M IDs are retained from snapshot `LEGACY-20261014-A`. Entries below summarize source claims; they are not current-build confirmation. See `research/EVIDENCE.json` for per-file hashes and the external source-revision limit.

<a id="m-0001"></a>
## M-0001 — Cached dialogue result / late skill-use calculation

Legacy model: a success result may be selected while effective Speech is high, followed by a later non-positive skill-use amount. The family matrix adds an Intimidate-only quest-state suppression candidate; the claimed no-XP outcome is an unlogged historical observation ([EV-0068], [EV-0069]). Dialogue-family breadth remains open.

Legacy mechanism record: [M-0001](MECHANISMS.md#m-0001) (`EV-0004`). Related glitch record: `glitches/G-0001-speech-xp-exploit.md`.

<a id="m-0002"></a>
## M-0002 — Float32 ActorValue accumulation and cleanup

Legacy numeric model: independent temporary writers can round when aggregated and leave a cleanup delta; raw bits, source identity, operation order, and reachable writers are required. The root numeric examples are retained as unverified illustrations ([EV-0040]); the detailed source model is [EV-0005]. A later report corrects the cleanup operand: Recover subtracts the negated effective magnitude, while `+0x94` receives an observed modifier-slot delta afterward ([EV-0057]).

Legacy mechanism record: [M-0002](MECHANISMS.md#m-0002) (`EV-0005`). Related glitch record: `glitches/G-0003-shifting-float-residue.md`.

<a id="m-0003"></a>
## M-0003 — Alchemy classification, cost ordering, and Peak key

Legacy static model separates poison/potion classification, costliest effect, Peak comparison key, and resistance behavior. Ingredient order alone does not prove commit order. Follow-up reports add the 89.2167511 Conjuration-poison XP prediction, the null-key AV148 CC writer, and a scoped VMAD writer inventory ([EV-0059]–[EV-0061], [EV-0064], [EV-0082], [EV-0083], [EV-0093]–[EV-0095]); these are static findings with recipe, reachability, and plugin-scope limits. A separate report models item class from the first raw matched effect before scaling; the Jarrin edge case is only predicted under extreme scaling ([EV-0094]).

Legacy mechanism record: [M-0003](MECHANISMS.md#m-0003) (`EV-0006`). Related glitch record: `glitches/G-0002-mixed-poison-classification.md`.

<a id="m-0004"></a>
## M-0004 — Poison Resistance-sensitive effect scaling

Legacy reports tie scaling to item classification and effect data. One inventory reports 50 PoisonResist MGEFs, 319 reverse-reference rows, and 148 possible mixed-effect recipes; an older probe supports hostile-first classification only ([EV-0056]). No exact recipe, resistance amplification, delivery, or XP result is imported, and no general rule that every beneficial effect scales is imported.

Legacy mechanism record: [M-0004](MECHANISMS.md#m-0004) (`EV-0007`). Related glitch record: `glitches/G-0002-mixed-poison-classification.md`.

<a id="m-0005"></a>
## M-0005 — Deadload queue/load boundary

Legacy static model: the load worker can revert VM state and drain queued callbacks. A historical user report says game time freezes during deadload, which weakens expiry-inside-deadload models but is not executable-verified ([EV-0078]). Direct spell membership, favorites hand-slot assignment, and MGR21 perk cleanup are distinct paths ([EV-0075]–[EV-0077]); a retained icon or membership is insufficient functional evidence.

Legacy mechanism record: [M-0005](MECHANISMS.md#m-0005) (`EV-0008`). Related glitch record: `glitches/G-0004-deadload-cleanup-retention.md`.

<a id="m-0006"></a>
## M-0006 — Positive skill-use amount guard

Legacy native analysis reports a shared non-positive amount guard. Caller-specific formulas and effective outcome remain separate questions ([EV-0009], [EV-0038]). Historical skill-use scans also distinguish scroll from ordinary spell paths and report no valid-skill exact-zero MGEF in the scanned corpus ([EV-0072], [EV-0073], [EV-0086]); these do not establish a current-order XP suppressor.

Legacy mechanism record: [M-0006](MECHANISMS.md#m-0006) (`EV-0009`). Related glitch record: `glitches/G-0001-speech-xp-exploit.md`.

<a id="m-0007"></a>
## M-0007 — Synchronous craft transaction boundary

Legacy static analysis reports synchronous alchemy/enchanting calls and no known player-controlled interposition. The ordinary enchanting callback produces output before a fixed skill-use call; condition functions inspect/register data without creating an inventory transaction ([EV-0067], [EV-0084]). Signed `usesSkill` values outside 6–23 skip the skill call, but no accessible type-3 furniture was found; fixed COBJ outputs and the Staff Enchanter furniture lead do not establish an XP bypass ([EV-0065], [EV-0066], [EV-0085]). A transaction boundary is not itself a bypass.

Legacy mechanism record: [M-0007](MECHANISMS.md#m-0007) (`EV-0010`). Related glitch record: `glitches/G-0006-enchanting-preview-mismatch.md`.

<a id="m-0008"></a>
## M-0008 — No-caster hazard path

Legacy native model reports a stack `NonActorMagicCaster` route. A later static audit reports player-created hazards receive the player `ActorCause` before ticking and finds no official cause-less writer in its scope; environmental non-actor hazards remain controls, not player routes ([EV-0031], [EV-0106]).

Legacy mechanism record: [M-0008](MECHANISMS.md#m-0008) (`EV-0011`). Related glitch record: `glitches/G-0005-blizzard-no-xp-candidate.md`.

## M-0009 — Incoming armor skill-use routing

Legacy static analysis reports that incoming player damage reaches Heavy/Light Armor `UseSkill` after positive damage and a positive-DNAM worn-armor scan, while blocked hits redirect to Block AV9 ([EV-0036]). The fresh GOG AE 1.6.1179 trace confirms the inline AV11/12 versus AV9 routes and positive-DNAM armor selection, but corrects the positive-damage attribution: the `[RSP+0xA0]` test at 0x1406bcce6 gates the attacker-side call at 0x1406bcd72; its JBE target enters the player-receiver branch at 0x1406bcd78. The receiver's AV11/12 call at 0x1406bcf00 passes `[RSP+0xA4]` to the PlayerCharacter `UseSkill` override, which independently rejects non-positive points ([EV-0217]–[EV-0223]). The blocked branch calls AV9 with a damage-field difference and skips AV11/12. This is build-attested static GOG evidence, not a Steam RVA transfer or live hit result; armor protection, exact runtime arguments, and XP deltas remain unmeasured. Projectile owner-death checks and pure spell paths remain adjacent limits, not useful physical-hit suppression results ([EV-0049], [EV-0050], related `EV-0020`, `EV-0023`).

The bounded private-export lead screen reports that lowering a worn positive-base Heavy Armor item's displayed rating to zero did not prevent hit XP; a separate level-one negative-rating report says hit XP increased ([EV-0283]). This aligns with the GOG trace's positive base-DNAM worn-ARMO selector: changing effective/displayed rating alone does not clear that eligibility predicate ([EV-0222]). The reports remain untrusted, build-unspecified, and lack numeric AVSK/protection controls. The GOG trace does not establish Steam 1.6.1170.0 behavior, and zero base DNAM plus independent protection remains a distinct unresolved possibility.

## M-0010 — Invulnerability clears the armor eligibility field

Legacy static analysis reports that the invulnerability branch clears total hit damage before armor skill credit, while also removing the physical damage payload. The ordinary player writers identified in that report are protected transitions with paired cleanup; no persistent useful-hit route is established ([EV-0039]).

## M-0011 — No generic official EP22 XP-negation multiplier found

The legacy clean-master scan reports only positive `Mod Skill Use` perk multipliers, including one furniture-gated 0.05 staff-enchanter entry. This rules out that audited record family as an arbitrary skill-XP suppressor but does not rule out caller-side non-positive amounts or runtime state mismatches ([EV-0051], related `EV-0038`).

## M-0012 — Native finite-effect cleanup and timer lifecycle

Historical GOG static reports say finite potion effects finish through native `Finish`/Recover cleanup before Papyrus `OnEffectFinish`; race transformation does not clear arbitrary alchemy effects. No ordinary official writer for the cited non-finite timer or bypass state was found in the audited scope ([EV-0058], [EV-0079], [EV-0096]). Zero-duration Thistle still finishes at elapsed zero ([EV-0098]); the scanned ENIT bit did not bypass that path, and deferred Dispel retries ordinary finish instead of providing an identified alchemy caller ([EV-0097], [EV-0099]). This is not an all-load-order negative or a runtime permanence test.

## M-0013 — Self-poison inventory ownership and transfer boundary

Historical static reports place weapon poison in inventory-entry `ExtraPoison` data and show the incoming hit path does not rewrite its target. Transfer helpers may carry extra data, but do not prove stable stack identity or a deterministic NPC attack on the player ([EV-0062], [EV-0063], [EV-0101]). Fixed poison-gas and Poison Rune controls remain distinct from arbitrary crafted-poison delivery; the gas audit reports a fixed explosion payload that does not read weapon poison, and inspected shield reflection scripts cast fixed spells ([EV-0102], [EV-0103]).

## M-0014 — Base ActorValue skill cap

The historical Enchanting audit reports that the native cap checks base skill rather than the effective ActorValue, so temporary effective-skill shifts do not evade that check ([EV-0087]). This is a GOG static finding, not a tested XP-threshold bypass. A separate Shalidor scroll scan reports fixed perk grants rather than school PowerModifier writes, with an adjacent AV156 Magicka effect ([EV-0104]).

## M-0015 — Direct spell-list serialization and cleanup

A historical Karstaag audit reports that Power cast membership is native actor state, serialized in the save, and checked before another cast; losing a Papyrus removal callback can leave list membership or an icon without proving another usable cast ([EV-0088]). The separate player-spell inventory reports synchronous Apocrypha `SetPower` replacement, not a queued cleanup gap ([EV-0100]).

## M-0016 — DA14 Story Manager level predicate and script handoff

The installed Steam AE official-master records contain a `DA14QuestStartNode` with a `GetLevel` CTDA at comparison value 14 on PlayerRef and a single child `DA14Start` ([EV-0108], [EV-0212]–[EV-0214]). The screened `DA14`/`DA14Start` QUST conditions and linked DA14 INFO conditions contain no later `GetLevel` function entry in that source scope ([EV-0212], [EV-0213]). The `QF_DA14Start` PEX has a fragment that sets stage 5 on `DA14` and then stops itself ([EV-0215]); the fragment's triggering stage is not identified. This supports one explicit Story Manager level gate in the screened path, not the absence of every alternate route, a profile-specific winner, or a level-one bypass. The record/Papyrus chain has no demonstrated shared primitive with the incoming-hit armor XP path M-0009.

VMAD fragment-to-stage mapping now identifies DA14Start stage 30/50 as the calls that start its two Sam drinking scenes; their own scripts advance the owning quest to stages 40/60. Stage 70 sets DA14 stage 5 and stops DA14Start ([EV-0264]). This places the resolved scene chain downstream of the already-started DA14Start quest. A separate Dragonborn QUST property `DA14Gleda` references DA14 alias 3, but its caller PEX is unavailable and no start behavior is inferred. The alternate writer and runtime bypass questions remain open; no edge to armor mitigation or XP is supported.


## M-0017 — Hit-data skill routing and positive points gate

Fresh GOG AE 1.6.1179.0 analysis identifies an inline hit-resolution function at RVA 0x6BCAA0 and a preceding hit-data population helper at RVA 0x7DD220 ([EV-0222], [EV-0223]). For a player receiver, the unblocked branch scans worn ARMO entries, requires positive base armor rating and a Heavy/Light category, then calls virtual slot 0xF7 with AV11 or AV12 and a points value from `[RSP+0xA4]`. The blocked flag branch selects AV9 using the difference between the physical and total damage fields and does not call AV11/12. CommonLib maps the fields to `physicalDamage` +0x54 and `totalDamage` +0x50, and maps Heavy/Light to AV11/12 ([EV-0217], [EV-0218]). The concrete PlayerCharacter `UseSkill` override returns for points that are not strictly positive before forwarding to the skill-progress callee ([EV-0220], [EV-0221]).

The separate `[RSP+0xA0] > 0` branch precedes the attacker-side UseSkill call and jumps directly to the player-receiver check when it fails; it is not a direct guard on receiver armor XP ([EV-0222]). This disambiguates the older report's internal branch attribution. The GOG trace establishes a distinct skill-use gate from the armor-form rating scan, but it does not show a vanilla state that preserves measurable protection while suppressing the armor XP delta, nor does it establish the Steam 1.6.1170 path. See contradiction C-OBJ2-ARMOR-GATE and experiment EXP-0012.

Q-0031 queried the direct caller context: `FUN_1406bcaa0` has one observed direct caller, `FUN_1406bb690`; that caller is reached from event-dispatch case 11 and from `FUN_1407ba3e0` after an Actor state predicate/process-target check ([EV-0291]). This does not establish that the function handles every ordinary actor hit, nor does it connect the Papyrus `ObjectReference.ProcessTrapHit` native used by physical traps to this function. Keep `FUN_1406bcaa0` as a build-attested HitData/skill-routing candidate, while ordinary-hit and trap producer edges remain open.

Q-0032 resolves the GOG ProcessTrapHit registration and PlayerCharacter dispatch. The exact Papyrus native entry points to `FUN_140a30e80`; its receiver slot `0x58` reaches `FUN_140679da0` for both Actor and PlayerCharacter. That function calls `FUN_1407dd110`, whose body calls the common `FUN_1407ddf50` HitData population/resistance pass, then sends the receiver to `FUN_1406b9df0` ([EV-0293], with builder semantics in EV-0261). This establishes a trap-payload edge into M-0017's HitData builder/armor-related calculation subpath, followed by a distinct actor-hit handler rather than a direct call to `FUN_1406bcaa0`. The captured handler includes an AV15 Sneak `UseSkill` branch at slot `0xF7`; no AV11/AV12 route is identified in that bounded path. Downstream/indirect award routes, live damage, effective protection and armor AVSK remain unresolved. This shared builder edge does not establish an armor-XP bypass or a Steam mapping.

Q-0034 traces the ActorValue-update callback branch and selected HealthDamage descendants. `FUN_1406b49d0` calls `FUN_1406b4c70`, which indexes the runtime-initialized table at `0x14319b880`; initialization assigns AV11 and AV12 to `FUN_1406b65c0`. That callback dispatches Actor slot `0xCA`: the base Actor target is a `RET`, and the PlayerCharacter target `FUN_140729110` resets fields at `+0x270/+0x274` and calls `FUN_1406d2850` on the `+0x208` container. The selected callback contains no `UseSkill` award or direct return to `FUN_1406bcaa0` ([EV-0295]). The table's zero-valued static bytes precede its runtime initialization and are not treated as runtime state.

The same initializer maps Health AV24 to `FUN_1406b6050`; the screened callback and PlayerCharacter `HandleHealthDamage` target `FUN_1406bbb80` route through health/state/event helpers without an identified AV11/AV12 award. The full `FUN_1406b9df0` census has 89 direct edges and 28 unresolved indirect sites; its visible Actor::UseSkill slot `0xF7` branch uses AV15 Sneak, and its direct call list has no edge back to `FUN_1406bcaa0` ([EV-0295]). This supports only the mapped callback/HealthDamage route. Other indirect dispatches, positive trap damage, effective protection, raw AVSK and Steam equivalence remain open; the frontier continues the unclassified virtual slots and the exact live discriminator.

The extended GOG builder trace shows the source order: `FUN_1407ddf50` snapshots HitData `totalDamage` at `+0x50` into `physicalDamage` at `+0x54`, then reads AV39 through the ActorValueOwner `GetActorValue` virtual entry and calls Actor `GetArmorBaseFactorSum` (slot `0xE7`) before applying the combined factor to `totalDamage`. The same helper later sets the blocked flag and may further reduce total damage. The following helpers do not rewrite `+0x50` or `+0x54`, and the receiver routing occurs after population ([EV-0261], [EV-0222]). This supports separation in source order between mitigation and the receiver skill branch, but not a vanilla candidate or a measured protection/XP outcome. The hit-builder call site does not directly call `GetClampedActorValue`; the concrete virtual `GetActorValue` implementation remains unresolved, so negative AV39 survival is still unknown.

The official award-side record screen identifies eight EP22 `Mod Skill Use` PERKs across the five official masters. `doomWarriorPerk` has a positive 1.20 modifier conditioned on AV11 HeavyArmor and AV9 Block advancement; `doomThiefPerk` has a positive 1.20 modifier conditioned on AV12 LightArmor advancement. The only 0.05 row is Dragonborn's Enchanting-only staff-furniture modifier ([EV-0262]). These are award-side records; there is no supported causal edge from them to AV39 mitigation or HitData damage, and no player-reachable suppressor or runtime XP outcome is established.

The PlayerCharacter slot-0xE7 trace resolves the dynamic target of the hit builder's armor-base-factor call: GOG `VTABLE::Actor` slot `0xE7` is a zero-returning base stub, while the PlayerCharacter vtable entry resolves to `FUN_140728e50`, which returns a float from `this+0x274` and calls two unidentified virtual helpers only when that value is negative ([EV-0263]). The HitData builder applies this virtual result before it sets the blocked flag ([EV-0261]); the later blocked receiver selects AV9 and omits AV11/12 ([EV-0222]). This strengthens the source-order link between armor-factor calculation and blocked routing but does not identify the field from an independent layout, establish a positive value or numeric worn-armor protection, or measure any skill XP. The natural next test is EXP-0017.

EXP-0033 extends the receiver def-use trace across both HitData population paths. In GOG AE 1.6.1179.0, the AV11/AV12 receiver call loads its points input from `physicalDamage` (`+0x54`), normally copied from the current `totalDamage` (`+0x50`) in `FUN_1407ddf50` before AV39 and armor-base-factor reduction update `totalDamage`. The separate fields explain why the standard armor points input is not the final mitigated damage. A conditional later call to `FUN_1407dda40` writes eight zero bytes at `+0x50`, clearing both floats before receiver routing. EV-0286 maps the predicate to attacker `middleHigh->doNoDamage`, followed by `!IsInCombat || ignoringCombat`; this is a whole-hit cancellation path, not a protection-preserving candidate. The only observed direct setter call that can pass true comes from `FUN_14048a390`; it reads bit 1 from parameter slot 7 while the actor process is High/MiddleHigh. The callback constructs TESActionData/BGSActionData, but its dispatch owner and parameter schema remain unresolved (Q-0028) [EV-0287]. This is not a direct HitData resolver edge. The trace adds a causal edge from the pre-resistance damage snapshot to AV11/AV12 points and a separate attacker-side cancellation edge; it does not link AV39 mitigation to the normal armor points argument or connect OBJ-1 quest gates to OBJ-2. No Steam or live protection/XP result exists.

## M-0018 — AV39 candidates and target-route limits

The corrected GOG trace shows ValueModifierEffect `OnAdd` compares MGEF Detrimental bit 2 with ActorValueInfo bit 9 and conditionally flips ActiveEffect magnitude; `ModifyOnStart` passes the ActiveEffect's generic target and value through the actual `ModifyActorValue` method. MFD's Recover flag selects the temporary modifier path. AV39's bit-9 value remains unknown, so the effective sign is conditional and no PlayerRef route is established ([EV-0258]). The bounded `ActorValueInfo` Load/ClearData/InitItemImpl bodies show no direct write to the flags member at `+0x60`, and the installed official-five-master AVIF screen contains no `DATA` field; indirect/global/runtime setters remain unsearched ([EV-0259], CL-L090).

The five installed official masters contain an AV39 MGEF candidate surface including Marked for Death, Doom Lord, a test spell, and Haknir's scimitar effect ([EV-0224]–[EV-0227], [EV-0242], [EV-0243]). Marked-for-Death spell tiers reference MGEF 0010319D, which Update.esm overrides. The raw MGEF schema decode identifies a Value Modifier for AV39; the Update override sets Hostile, Recover, and Detrimental flags. The three tiers store magnitudes 25/50/75 for 60 seconds ([EV-0224]–[EV-0226], [EV-0257]). Those fields identify a detrimental AV39 candidate but do not establish its effective raw-value delta sign or target. The spells' raw SPEL/SPIT fields decode to Type=Voice, Cast Type=Fire and Forget, Delivery=Aimed, and Range=0; that does not specify Self delivery or establish that an NPC aims the effect at PlayerRef ([EV-0225], [EV-0255]). The local UESP page describes its armor-rating reduction, but no natural player-targeted ActiveEffect, cleanup, or hit result was observed ([EV-0230], [EV-0239]). WICastMagic03/04 bind a Player-conditioned CastingActor to CAST/R1 and a separate SpellTarget alias to CAST/R2; the Papyrus Index's CK-Wiki-derived `OnStoryCastMagic` signature defines caster and target parameters but notes that `akSpellTarget` always returns None ([EV-0241], [EV-0244]). This supports an inference that the event is a response to the player's cast, not a writer that applies MFD to PlayerRef; actual alias fill remains unobserved. The separate forced Player alias does not create a causal edge to AV39 ([EV-0229], [EV-0230]). A bounded NPC_ scan found no direct MFD spell/shout references. The exact shout screen found four other raw references, all dialogue conditions checking `GetEquippedShout`, not effect application; these bounded screens do not exclude other scripts, lists, or native writers ([EV-0227], [EV-0228], [EV-0256]). Haknir's proc places its effect at `akTarget`; its weapon belongs to a separately gated actor/encounter path, not a demonstrated level-one player writer ([EV-0231]–[EV-0234], [EV-0245]).

No causal edge is yet supported from M-0018 into the GOG HitData AV9 formula in M-0017. The needed bridge is a natural player AV39 state plus same-build measurements of blocked points, effective armor protection, and raw AVSK progress. See Q-0015/Q-0016 and EXP-0010/EXP-0013.

## M-0019 — Haknir level-36 Story Manager gate and stage writers

Dragonborn.esm SMQN 02024003 links child QUST 02038FB0 behind a raw CTDA interpreted as `GetLevel >= GLOB 02024004`; the global is 36.0 ([EV-0233], [EV-0234]). The child quest is tied to the `LEVL` event and references main QUST 02024002. The main quest is not Start Game Enabled in its first DNAM flag byte. Its Haknir alias carries the documented Initially Disabled bit and an ALRT/LCRT location-reference fill; the placed ACHR 02037FEA is listed in `DLC2GyldenhulBarrowLocation` ([EV-0231]–[EV-0234]). The inspected DLC2WE13 encounter has a top-level `GetStage(main treasure QST)==20` condition and grants the book to its Actor1 alias, placing that encounter downstream of main-quest stage 20 ([EV-0233], [EV-0234]).

Eleven Deathbrand book references exist in cells outside the Barrow ([EV-0235], [EV-0236]). Follow-up extraction from the supported `Skyrim - Misc.bsa` route recovered the book script and QFs after the earlier loose-file/root inventory ([EV-0237], [EV-0270], [EV-0271]). The book `OnRead` checks `GetStageDone(mainQ,20)` and only then requests `mainQ.SetStage(1)`, so its serialized `myPrereqStage=20` is an actual precondition, not an independent book-first start ([EV-0270]). The QUST VMAD maps main-Q stage 10 to the fragment that registers `OnUpdate`; that handler reads PlayerRef location and the Shoal bandit-boss alias/3D state and branches between polling again and `SetStage(20)`. Stage 20 refreshes the Shoal setup and starts its scene. Stage 90 maps to `Fragment_23`, which calls `StartBattlePhase(0)` on the Haknir alias. The boss phase-0 code moves/enables Haknir and starts combat; its `OnDying` later requests main-Q stage 100 ([EV-0245], [EV-0270]).

EV-0271 resolves two identified main-Q stage-10 writers. The LEVL helper's stage-10 fragment calls `mainQ.SetStage(10)`, but its child QUST is downstream of the `GetLevel >=36` SMQN event. DLC2Init stage 100 maps to `Fragment_4`, which reads Player `GetLevel` and a global property bound to GLOB 02024004, then calls `mainQ.SetStage(10)` only on the `level >= minLevel` branch (the installed static global is 36.0; [EV-0233], [EV-0271]). The miscellaneous Haknir QF reads main-Q stage 20 to update its own objective/map state and contains no main-Q start/stage write in the complete bounded PEX ([EV-0271]). Thus the audited book, initializer, LEVL helper and misc-quest paths support gated progression and weaken an ordinary level-one start/death model. They do not exclude uninspected dynamic/native/profile/runtime writers, prove current runtime alias fill, or establish a level-one transition. The CK-Wiki-derived `SetStage` reference does not establish that this quest bypasses the level condition or fills aliases ([EV-0246]). No level-one start, actor enable, death or stage-100 transition was observed. See C-OBJ1-HAKNIR-BOOK-START, C-OBJ1-HAKNIR-DEATH-STAGE and EXP-0014.

## M-0020 — Metadata-driven ActorValue clamp lead

EV-0258 corrects the prior effect-vtable label: decimal query index 20 was CommonLib slot `0x14` (`Start`), while `ModifyActorValue` is slot `0x20`; its OnAdd sign normalization also consults ActorValueInfo bit 9. The generic value modifier's mode-2 path uses the same bit for its clamp direction, but MFD's Recover flag selects mode 1 (`kTemporary`) in the captured method. This connects two native reads of the same bit, not a proven value for AV39 or a claim that the AV39 read in hit construction is clamped.

In the build-attested GOG AE 1.6.1179.0 project, `ActorValueOwner::GetClampedActorValue` reads ActorValueInfo flags at offset `+0x60` and selects lower/upper-bound behavior from those flags. The decompilation includes a zero-floor path and a separate-bound path ([EV-0249]). The bounded direct-reference audit found 13 calls across 12 callers; one caller loads a dynamic AV index from a `+0x190` field and checks only for the `-1` sentinel before calling the clamp ([EV-0252]). Ghidra reports three DATA references to that dynamic caller, with raw words matching its 32-bit RVA in compact unresolved records; their type, consumer and dispatch are unknown, and the project found no exact-address users for those storage locations ([EV-0253], [EV-0254]). These results do not identify AV39's exact flags, connect this caller to HitData, or establish a bridge to the blocked AV9 points formula. EV-0259 bounds the `ActorValueInfo` Load/ClearData/InitItemImpl methods and official-master AVIF fields: no direct `+0x60` write or `DATA` field was found, while the base load route retains indirect dispatch. The source/value of AV39 bit 9 therefore remains unknown, rather than proven absent or defaulted. The installed Steam Skyrim.esm `AVDamageResist` AVIF has no DATA clamp range in the direct parser result; that does not establish absence of engine metadata. This is a static mechanism lead, not proof that negative AV39 is clamped or survives. Do not transfer GOG RVAs to Steam.

EV-0261 narrows the relationship to the hit builder: the GOG HitData resistance pass calls the virtual `ActorValueOwner::GetActorValue` slot with AV39 and does not directly call `GetClampedActorValue` at that site. This weakens only a direct-clamp-call explanation; it does not falsify a clamp performed inside the concrete virtual override or another earlier value path. No implementation of that override, AV39 flag value, or Steam behavior is inferred.

## M-0021 — DA14 stage-406 trigger inside the quest interior

The installed Steam AE record screen places REFR `00000EC8` and its `defaultsetStageTrigSCRIPT` VMAD in CELL `0003D62B` (`DA14Interior`). Schema-backed decoding gives `myQuest=DA14`, `stage=406`, `doOnce=true`, and `disableWhenDone=true`. The bounded group-context screen found one XTEL-linked reference in the interior, REFR `0003DC3F`, targeting exterior REFR `0003DC45` in `Morvunskar01`; the destination is persistent and initially disabled ([EV-0250]). The QUST VMAD maps `QF_DA14 Fragment_53` to stage 135/log entry 0 in both checked official records, and the PEX fragment enables alias 36's initially-disabled XMarker REFR `0003DC43`. That marker is the XESP parent of initially-disabled portal trigger REFR `0003DC42`; its base ACTI carries `dunda14PortalScript` with a `myDoor` property pointing to REFR `0003DC45` ([EV-0216], [EV-0251]). A follow-up exact-FormID screen across the official five masters found no new direct record candidate that moves the player into DA14Interior or starts/enables DA14 before the helper ([EV-0275]). The Update.esm `Patch1_4_UpdateQuest` branch is separately bound to DA14 and the portal references but only disables the portal objects after DA14 stage 200; it contains no DA14 Start, SetStage or MoveTo call ([EV-0264], [EV-0275]). The activation PEX `dunda14PortalScript` remains unrecovered outside the tested Skyrim - Misc.bsa/exact loose scopes, so dynamic/script/native entry behavior remains open. The examined marker/trigger chain is downstream of defined DA14 stage 135; no profile winner, undefined-stage runtime effect, or level-one transition is established. See C-OBJ1-DA14-STAGE-406 and EXP-0015.

## M-0022 — DA07 pamphlet alias lifecycle

The installed Steam official-master records place the pamphlet BOOK as ALCO on DA07intro's `Pamphlet` alias. The QF stage-0 fragment adds that alias to WICourier; the attached ReferenceAlias script calls DA07intro.SetStage(5) on player equip or container receipt after the alias exists ([EV-0265]). The base BOOK itself has no VMAD, and the two inspected INFO TIF fragments transfer the item from player to speaker without a SetStage call. This supports the conclusion that this alias callback is downstream of DA07intro startup and falsifies the standalone alias-first mechanism within the bounded screen. It does not rule out other stage/start writers; the DA07IntroTrigger is a separate candidate in M-0023. No level-one gameplay result is established.

## M-0023 — DA07IntroTrigger stage-7 scene candidate

The installed Steam official-master records place REFR `000B1403` in DawnstarExterior04, using a base script configured to wait for both Madena and Silus inside the trigger and then call DA07intro.SetStage(7) ([EV-0266]). DA07intro stage 7 starts `DA07IntroScene`; its scene actor IDs match the unique-actor aliases Madena (2) and Silus (0), and the scene completion fragment calls SetStage(10). Neither trigger PEX body contains a player-level condition. This is a concrete pre-gate candidate, but actor co-entry timing, SetStage startup semantics on the exact Steam runtime, quest/alias startup, and scene completion remain untested. Papyrus Index documentation is secondary evidence; there is no level-one reproduction. It shares no identified causal record, ActorValue, or native hit/skill primitive with OBJ-2 mechanisms M-0017/M-0018.

## M-0024 — DA07 actor-pair readiness depends on quest setup in the screened records

The official-five-master placement screen found Silus ACHR `000240CE` initially disabled in `DawnstarSilussHouse` and Madena ACHR `0001A6C3` in `DawnstarTheWhiteHall`; it found no second placed actor reference for either NPC base. DA07intro stage 0 is the known writer that enables/moves Silus to his scene marker and moves Madena to hers ([EV-0267]). Because DA07intro is under the level-20 Story Manager branch in the screened setup ([EV-0265]), the stage-7 trigger is not shown to bootstrap itself from those initial placements. Other writers and runtime/profile behavior remain untested. No causal edge connects this quest setup to the OBJ-2 armor-hit/skill path.

## M-0025 — DA07 Museum trigger-to-intro scene candidate

Four player trigger references inside DawnstarSilussHouse call `DA07MuseumScenes.SetStage` with artifact-specific stages. SCEN `00096FDB` has raw FNAM `0x15`; the TES5Edit SCEN schema maps bit 0 to Begin on Quest Start. Its begin fragment starts the tapestries scene, and its completion fragment calls `DA07intro.SetStage(200)` and `DA07.SetStage(5)`. The direct trigger path has no identified player-level predicate, but the house is described as inaccessible until level 20 by local UESP revision 3429231, and the intro scene has a `HasLoaded3D` condition plus a Silus alias without the schema's Allow Disabled bit ([EV-0268]). The REFR XLOC schema resolves interior door `000240CA` as level 255 (Requires Key), requiring KEYM `000960F0`; the four trigger centers are 277.28–671.21 coordinate units from that door ([EV-0269]). The bounds and centers help prioritize an entry search but do not expose NIF collision or prove a player-only clip. This is a high-value access candidate, not a proven bypass: scene eligibility, alias filling, quest startup, and useful main-quest progression need a clean level-one observation. There is no identified causal edge to OBJ-2.

## M-0026 — GOG Quest.Start, SetCurrentStageID, and SetStage callback paths

In GOG AE 1.6.1179.0, CommonLib and the matching Address Library map `TESQuest::EnsureQuestStarted` to RVA `0x3C9D30` and `BGSStoryTeller::BeginStartUpQuest` to RVA `0x532E60` ([EV-0272], [EV-0289]). Direct registration in `FUN_140a48e10` maps `Quest.Start` to `FUN_140a48c50` and `Quest.SetCurrentStageID` to `FUN_140a48aa0` ([EV-0313]). The event-ID/flag guard and deferred scheduling captured in EV-0272 belong to SetCurrentStageID; they are not the registered Quest.SetStage callback.

The separate `SetStage` literal/reference row and peer `GetStage` callback support `FUN_14034de90` as the registered Quest.SetStage callback [EV-0313]. Its entry requires quest `+0xDC` bit 0 or event ID `-1`, then invokes EnsureQuestStarted in start-now mode. On an accepted internal state path, EnsureQuestStarted calls the shared quest-initialization helper and BeginStartUpQuest; that path resets current-stage/entry state, processes reference-promotion work, marks a readiness bit, and inserts the quest in a manager list before stage lookup and stage-fragment dispatch. The inspected path has no explicit player `GetLevel` comparison. Event-ID/ready-bit and other state guards still limit which stopped quests pass. Running-state semantics, complete alias fill, journal/dialogue availability, and functional access are not established. The `TESQuest::Start` relocation remains absent from the Address Library; the registered Papyrus Start method is nevertheless visible in the GOG native registration routine.

The association between Steam QUST ENAM=CLOC/LEVL and the GOG runtime event-ID field remains an inference from source/layout evidence ([EV-0288], [EV-0289]). Haknir's two identified main-stage-10 callers remain behind `GetLevel >= 36` ([EV-0271]); DA02/DA09/DA06 record-specific callback availability and runtime state remain open. This adds no edge to OBJ-2, Steam runtime, vanilla bypass, or reproduction. Reproduction steps and raw query hashes are in EXP-0022, EXP-0037, EV-0272, EV-0289, and EV-0313.

## M-0027 — MFD words paired with a custom Drain Vitality spell payload

The three captured Dawnguard Drain Vitality-labelled SHOU records reuse the Skyrim MFD word FormIDs, but their linked Dawnguard SPELs reference Health, Magicka, Stamina, Script-archetype, and stagger MGEFs. The three Value Modifier MGEFs target AV24/25/26; none of these custom SPEL effect lists includes MFD MGEF `0010319D` (AV39) ([EV-0273], compared with the MFD candidate in [EV-0257]). This supports a record-level label/word versus payload distinction for the captured path. It does not resolve the Script archetype, how the shout is acquired, its runtime target, profile-specific winners, or other MFD application paths. The custom effects add no demonstrated causal edge to Player AV39, HitData mitigation, or armor XP. See C-OBJ2-DV-MFD-WORDS-AV39 and EXP-0023.

## M-0028 — VQ01 book alias and Dimhollow stage-trigger candidates

In the installed Steam AE official source records, VQ01 (`DLC1VQ01`, `0200352A`) owns the `Book` alias; its forced reference `0200D072` points to BOOK `0200D070` in `DLC1DimHollowCrypt02`. The alias script's `onRead` requests VQ01 stage 17; pickup requests the same stage only after VQ01 stage 15. The placed book is parented to `VQ01EnableMarker` `02002F66`, which VQ01's stage-10 fragment enables ([EV-0276]). This corrects EV-0019's historical alias-owner attribution and weakens the standalone base-book bootstrap model, but it does not prove alias-fill timing or Steam `SetStage` startup.

The bounded screen also finds `defaultsetStageTrigSCRIPT` references for VQ01 stages 15 (Crypt01, optional prerequisite 10), 17 (Crypt02, no serialized prerequisite property), and 18 (Crypt02, optional prerequisite 17). The generic script PEX was not recovered by the tested Misc-BSA extractor, and the candidate trigger's activation state is unresolved. The screened Crypt entrance/intercell door refs set record flag `0x400`, which EV-0250's TES5Edit schema maps to Persistent; they do not set `0x800` (Initially Disabled) and have no direct XESP parent. Those flags do not establish a disabled-door barrier or the actual rubble/route behavior. Q-0021 tracks the stage-17 access candidate; no level-one transition is claimed. These records and scripts have no identified shared causal primitive with OBJ-2 armor mitigation or armor/Block skill XP.

## M-0029 — Dimhollow portcullis activation is separate from VQ01 stage progression

Dawnguard REFR `02009742` (`NorPortcullisLarge01`) uses ACTI `0003E726` with `default2StateActivator` and is XESP-parented to `DLC1VQ01LeverGateEnableMarker` REFR `02017772`; that marker uses Skyrim STAT `0000003B` (`XMarker`) ([EV-0277]). TES5Edit dev-4.1.6 maps the child's XESP flags byte 0 to no opposite-parent or Pop In bit; its trailing three bytes are unused. In the ACTI REFR variant, header flag `0x40000000` is Navmesh - Ground and bit 11 Initially Disabled is clear. The marker's STAT REFR flags identify `0x400` as Persistent and leave Initially Disabled `0x800` clear ([EV-0282]). These base fields encode ordinary parent-state inheritance, not the loaded reference state or a source of marker writes. The recovered complete PEX toggles open/close animation and keyword-linked collision on activation and contains no `SetStage` or explicit marker-enable call. The bounded five-master raw-field screen found no other direct reference to the marker among its declared fields, but does not exclude alias-passed, compiled PEX, native, profile or runtime writers. Physical reachability and passage remain unknown. The UESP rubble description is revision-cited but secondary. This physical-gate mechanism has no identified causal edge to OBJ-2 armor mitigation or armor/Block XP.
## M-0030 — ActiveEffect base timer-field save/load serialization

In GOG AE 1.6.1179.0, a fresh Address Library mapping identifies the ActiveEffect vtable, and read-only Ghidra queries show base SaveGame/LoadGame writing and restoring the class fields mapped by the matching CommonLib header as elapsed time, duration, magnitude, flags, references, and a 16-bit usUniqueID. FinishLoadGame rebuilds associated ReferenceEffect state. Base Update and Finish are no-op stubs; CanFinish is a separate flag/spell-type predicate, and the inspected Compare body uses base-effect flags plus conditional duration/magnitude without reading the unique ID (EV-0279). This supports serialized logical-state recovery in these base routines, not functional persistence after a wait, travel, save/load, or recalculation. The timer-update loop, expiry dispatcher, derived overrides, and Steam 1.6.1170 behavior remain unresolved. No causal edge connects this path to OBJ-2 HitData or armor/Block skill XP.

## M-0031 — Enchanting craft credit enters the shared skill-progress sink

In GOG AE 1.6.1179.0, the `EnchantMenuCraftCallback::Run` success branch reaches a function with one visible `Actor::UseSkill` virtual dispatch site. The dispatch reads the skill ID from `TESFurniture::WorkBenchData.usesSkill` at furniture offset `+0xE1` and passes a shared global float as points; CommonLib maps Actor slot `0xF7` to `UseSkill` ([EV-0280]). The installed base Skyrim.esm `CraftingEnchantingWorkbench` record `FURN:000BAD0D` stores raw WBDT bytes `03 17`, whose second byte maps to AV23/Enchanting ([EV-0281]). The concrete PlayerCharacter override rejects non-positive points and sends positive points into the float skill-progress/threshold path ([EV-0280], with the earlier bounded override query in [EV-0221]).

This gives Enchanting and incoming-hit armor/Block XP a shared award-side sink (`Actor::UseSkill` slot `0xF7` and PlayerCharacter skill progress); the points producers differ. It does not establish the numeric global points value, a raw AVSK delta, a Steam RVA/path, or a way to suppress armor XP while preserving mitigation. The UESP one-base-XP statement remains unverified by raw measurement ([EV-0124]). See Q-0005, C-OBJ3-ENCHANT-CREDIT, and EXP-0029.

## M-0032 — Ebony Warrior CLOC selection and city-to-Last-Vigil handoff

Dragonborn.esm `SMEN 0001320E` (`CLOC`) -> `SMQN 0202C49F` `DLC2EbonyWarriorNode` (`GetLevel >= 80` on PlayerRef plus event-data location conditions) -> sole child `QUST 0202C49E` `DLC2EbonyWarriorQuest` [EV-0288]. The QUST is CLOC and Start Game Enabled is clear. Its stage-10 QF fragment enables the unique `DLC2EbonyWarrior` alias, moves its reference to `CityCenter`, and adds the pickpocket modifier perk. The player alias `OnLocationChange` script later checks stage 100, moves the actor to `LastVigil`, and starts combat after the player enters that location; the actor alias `OnDeath` requests stage 200. This supports the serialized arrival/quest/stage path and distinguishes it from later greeting and relocation.

No separate pre-gate `Quest.Start`/`SetStage` caller was established by this trace. Q-0029 found event-scope rejection in the inferred GOG start wrappers and no external direct QUST reference in the official QUST/DIAL/INFO screen; the Steam/GOG interaction is an inference. Q-0030's all-signature official-master scan found one placed ACHR for the unique NPC base, marked Initially Disabled with no XESP, and the target QUST's Unique Actor alias is filled from that same base; stage 10 enables and moves it [EV-0290]. The remaining openings are dynamic script/native lookups, BSA script bodies, profile plugins, parent-cell/runtime enable state, and live behavior. This record/PEX path has no identified causal edge to OBJ-2 armor mitigation, AV39, or hit-earned armor XP. See CL-L118–CL-L124, EV-0289/0290, and EXP-0036–0038.

## M-0033 — Physical trap Papyrus handoff to native ProcessTrapHit

Skyrim.esm ACTI `00079923` `TrapFallingRockLg01` -> VMAD `PhysicsTrap` damage-tier selection -> `PhysicsTrapHit.damage` -> `PhysicsTrapHit.OnTrapHitStart` velocity/ghost/faction checks -> `akTarget.ProcessTrapHit(trapRef, damage, pushback, velocity, position, material, stagger)` [EV-0292]. The base `ObjectReference.psc` declares `ProcessTrapHit` as native; the installed source declaration and PEX expose no native body. `TrapHitBase` also uses the native method for its `OnTrapHitStart` route.

The GOG 1.6.1179 registration maps the Papyrus method to `FUN_140a30e80`, which dispatches through receiver slot `0x58`. The PlayerCharacter slot resolves to `FUN_140679da0` -> `FUN_1407dd110` -> common HitData population/resistance helper `FUN_1407ddf50` -> actor receiver handler `FUN_1406b9df0` [EV-0261], [EV-0293]. This establishes a causal edge from the trap payload to the shared HitData builder/armor-related calculation subpath in M-0017.

EV-0294 finds that `FUN_1406bcaa0`, the known AV11/AV12 receiver resolver, also calls `FUN_1406b9df0` after its player receiver skill branch. The ProcessTrapHit call chain reaches `FUN_1406b9df0` directly, without a direct edge through `FUN_1406bcaa0`. `FUN_1406b9df0` reads HitData `totalDamage`, calls `FUN_1406b49d0` in a conditional damage path, and the latter dispatches Actor::HandleHealthDamage when its selected ActorValue is Health (`0x18`) and the delta is negative [EV-0217], [EV-0218], [EV-0222], [EV-0294]. Two other screened helpers contain conditional AV15 Sneak `UseSkill` calls; these are not AV11/AV12 awards. This is a static candidate for damage after armor-related calculations while bypassing the known inline armor resolver, not evidence that all descendants omit AV11/AV12 or that positive damage/protection occurs.

`FUN_1406b9df0`, `FUN_1406bc140`, and `FUN_1406bc400` contain conditional AV15 Sneak `UseSkill` calls through slot `0xF7`; these share the generic skill-use sink with M-0017 armor/Block credit and M-0031 Enchanting but use a different ActorValue and trigger. The static direct trap chain enters the same `FUN_1406b9df0` continuation that `FUN_1406bcaa0` calls after its AV11/AV12 branch. Q-0034's GOG callback trace finds AV11/12 table entries mapped to `FUN_1406b65c0`, which dispatches Actor slot `0xCA`; the selected PlayerCharacter target updates fields/container state without a visible `UseSkill` award or direct return to `FUN_1406bcaa0` [EV-0295]. This supports a bounded damage path after armor-related calculations but does not establish that every other indirect descendant omits armor XP. Positive final trap damage, effective armor protection, raw AVSK change and Steam equivalence remain unmeasured. The configured positive trap tiers remain record values, not observed player damage. See CL-L125–CL-L129 and EXP-0039; the frontier continues the other virtual slots and exact live test discriminator.

Q-0035 mapped the remaining calls on the Actor receiver: slot `0x99` is the masked state test `FUN_140677100`; slots `0x5C` and `0x70` are `FUN_1406c4300` and `FUN_1402e55a0`. Actor and PlayerCharacter slot `0x5C` share the same target, which can retrieve or construct an `ActorMagicCaster` object. PlayerCharacter slot `0x70` adds a slot-`0x71` flag predicate before delegating to the slot-`0x70` state lookup; its slot-`0x99` target also matches Actor's [EV-0291], [EV-0296]. None of these selected targets or captured direct callees shows AV11/AV12 `UseSkill` or a direct edge to `FUN_1406bcaa0`. This resolves only the matching Actor/PlayerCharacter slots and bounded call depth; the other indirect objects in `FUN_1406b9df0` remain separate.

Q-0036 followed the ActorMagicCaster methods reached after `FUN_1406b9df0` stores the HitData `+0x38` pointer. ActorMagicCaster slots `0x14` and `0x10` lead to caster field/state checks, a player-caster list update, owner/flag reads, and a scalar float conversion. No AV11/AV12 award or direct edge to `FUN_1406bcaa0` appears in the selected bodies or bounded direct callees [EV-0297]. The pointer's concrete subtype and nested calls at offsets `0x298`, `0x320`, and `0x2B8` remain unresolved. This adds a bounded caster-state branch to the graph but no armor-XP, ActiveEffect-serialization, or OBJ-1 edge. Claim mapping: CL-L131 -> ActorMagicCaster branch screen [EV-0296], [EV-0297].

## M-0034 — Dawnguard level-gated Durak messenger versus quest-start alternatives

Dawnguard.esm SMQN `0200D911` (`DLC1VQ00Node`) contains `GetLevel >= DLC1VQMinLevel`; GLOB `0200D912` sets that threshold to 10. Its selected QUST child `0200D90B` (`DLC1VQ00ChangeLocation`) binds the Messenger alias to NPC_ `0201541D` (`DLC1Durak`) [EV-0298]. The level predicate therefore gates the Durak messenger/location-helper route in the inspected source. Captured QUST `0200D90E` (`DLC1VQ00`) and QUST `0200352A` (`DLC1VQ01`) use stage/cell conditions and do not contain `GetLevel`; targeted INFO rows use actor-identity conditions. Local UESP revision 3603039 reports guard-rumor, Agmaer/Dayspring Canyon, and Fort Dawnguard alternatives, including a route into `Awakening` without the starter quest journal entry.

This narrows the blanket “Dawnguard requires level 10” premise: the installed base records place the explicit level gate on the Durak helper, while the documented alternate routes remain candidate low-level paths. No exact level-one `Awakening` start, negative control, replication, or level preservation was observed. The native five-master xEdit call failed before process enumeration; the raw direct-parser result is not a profile winner, and Dawnguard BSA/PEX behavior remains unknown. Claim mapping: CL-L132 -> Durak helper gate and separately reported VQ00/VQ01 start paths [EV-0298]. No causal edge to M-0017 armor mitigation, ActiveEffect serialization, AV39, or armor/Block skill XP is supported.


Q-0038 enumerated all 36 Dawnguard.esm SMQN and its single SMEN record. The only function-80 `GetLevel` CTDA remains `DLC1VQ00Node` -> `DLC1VQ00ChangeLocation` -> Durak. The adjacent AM/PM vampire-attack nodes use function-74 `GetGlobalValue`; the SMEN contains no CTDA [EV-0299]. This is a Dawnguard.esm file-content census only: it does not screen a five-master winner, other record signatures, scripts, profile overrides, or runtime selection. Claim mapping: CL-L133 -> bounded Story Manager census [EV-0298], [EV-0299]. No OBJ-2 causal edge is supported.

## M-0035 — Five-master Story Manager level-gate inventory

The direct-parser census covers 535 SMQN and 28 SMEN records physically present in the five official masters. It identifies 15 distinct function-index-80 `GetLevel` CTDAs on 15 SMQN nodes after same-origin/local-FormID comparison; 12 are additional to DA14, Dawnguard's Durak helper, and Ebony Warrior [EV-0300]. Source-context resolution maps the thresholds and children. The DA14, DA07, and DA04 nodes parent to Skyrim-origin SMBN `QuestNode`; most others arrive through Level Increase or CLOC event branches. Some selected quests are helpers: DA04 selects `DA04SeptimusSendForPlayerQuest`, DA08 selects `DA08RumorPointer`, and Haknir selects its increase-level helper.

This falsifies the known-three-exhaustive model only for serialized SMEN/SMQN content in these five source files and supports additional Story Manager gate nodes within the same boundary. The native xEdit query failed before process enumeration; no profile winner, script/native caller completeness, or runtime transition was established. DA04's reported Elder Knowledge/book entry is queued for a separate gate-versus-start-path investigation. No shared native call, ActorValue, HitData, ActiveEffect, or serialization primitive connects this quest-record inventory to OBJ-2 armor mitigation or armor/Block XP. Claim mapping: CL-L134 and CL-L135 -> EV-0300.

## M-0036 — DA04 level-15 courier helper versus Ruminations book start path

In the prepared Skyrim.esm source, SMQN `0010481D` selects helper QUST `0010481C` (`DA04SeptimusSendForPlayerQuest`) under the GetLevel >=15 node [EV-0300]. The helper's `Fragment_0` adds `SeptimusLetter` to `CourierQuest`. Main QUST DA04 `0002D512` is serialized with DNAM flags `0x0111`, including Start Game Enabled. Its ALST alias ID 19 (`RuminationsBook`) is forced to REFR `00032787`, whose NAME points to BOOK `00032785`; QUST VMAD binds alias ID 19 to `DA04RuminationsScript`. That script's `OnRead` calls owning-quest `SetStage(1)`. QUST VMAD maps stage 1 to main-QF `Fragment_18`, which sets `ReadCrazyBook` and `SetStage(5)` [EV-0301].

This supports a serialized ordinary route to DA04's early stages independent of the level-15 courier helper and falsifies the all-entry-gated model for this path. The direct parser is not a winning-record export; a runtime level-one run, physical access, alias fill, later stage progression, and actual Steam behavior remain unverified. Dialogue INFO coverage was EditorID-bounded and is not an exhaustive child-topic census. No shared native call, HitData field, armor/Block ActorValue, ActiveEffect, skill-progress helper, or serialization primitive links this quest route to OBJ-2 armor XP, so no cross-domain causal edge is supported. Claim mapping: CL-L136 -> EV-0300/EV-0301.

## M-0037 — Shared HitData mitigation helper and ProcessTrapHit resolver bypass

In GOG AE 1.6.1179.0, the ProcessTrapHit PlayerCharacter route reaches `FUN_140679da0` -> trap builder `FUN_1407dd110` -> shared HitData helper `FUN_1407ddf50` -> receiver handler `FUN_1406b9df0`. Ordinary-hit builders `FUN_1407dd220` and `FUN_1407dd5b0` also call `FUN_1407ddf50`. The helper snapshots HitData `totalDamage` (+0x50) into `physicalDamage` (+0x54), reads AV39 through the ActorValueOwner path, calls Actor slot 0xE7 (`GetArmorBaseFactorSum`), and applies the resulting factor to `totalDamage` before blocked-hit bookkeeping [EV-0302].

The known ordinary resolver `FUN_1406bcaa0` contains a player AV11/AV12 award branch before it calls `FUN_1406b9df0`; the captured ProcessTrapHit wrapper enters the shared handler directly without a direct call through that resolver [EV-0302]. This supports a shared armor-related calculation and a bypass of the known award branch in the bounded GOG call graph. It does not establish that the PlayerCharacter inputs yield positive effective protection or that the installed Steam 1.6.1170.0 behaves identically. EV-0303 partitions the 28 handler indirect sites and identifies no AV11/AV12 award among the mapped families; the thirteen release-style dispatch targets and possible derived reference overrides remain residuals [EV-0303]. Ten indirect sites in the shared helper remain open for Q-0043. No causal edge to OBJ-1 is supported. Claim mapping: CL-L137 -> EV-0302; CL-L138 -> EV-0303.

## M-0038 — Bounded ProcessTrapHit receiver indirect-site classification

EV-0303 partitions the 28 unresolved `FUN_1406b9df0` indirect sites in GOG AE 1.6.1179.0: thirteen vtable slot-1 calls behind reference-count decrement checks; seven Actor/ActorMagicCaster calls at slots 0x99, 0x5C, and 0x70; one Actor::UseSkill slot-0xF7 call passing AV15 Sneak; three ActorValueOwner operations (GetActorValue(Health), GetBaseActorValue(Health), RestoreActorValue(modifier 2, Stamina, value)); and four source-reference `TESObjectREFR` calls at slots 0x8E, 0x8F, and 0x51 [EV-0295]–[EV-0297], [EV-0303]. Fresh matching-GOG queries show the base `AsExplosion` and `AsProjectile` targets return zero, and `GetActorCause` accesses cause data before a handle/form-table check. No mapped site awards AV11/AV12 or directly returns to `FUN_1406bcaa0`.

This supports the no-award model only for the typed and queried site families. The concrete release/destructor targets, all possible derived `TESObjectREFR` overrides, and runtime dispatch are not exhaustively resolved; positive protection, unchanged raw AVSK, Steam equivalence, and a vanilla level-one result remain unknown. No causal edge to OBJ-1 is identified. Claim mapping: CL-L138 -> EV-0303; Q-0043 continues the ten unresolved indirect sites in the shared mitigation helper.

## M-0039 — Conditional weapon-selected input in the shared HitData helper

In GOG AE 1.6.1179.0, `FUN_1407ddf50` has a conditional `ActorValueOwner::GetActorValue` whose index is read from `HitData.weapon +0x194`; pinned CommonLibSSE-NG layout identifies that offset as `TESObjectWEAP::Data.resistance`. With a non-null weapon and non-`-1` index, the returned target ActorValue is bounded and used to reduce HitData `totalDamage` beyond the separately mapped AV39 and Actor slot `0xE7` inputs [EV-0304]. The actual official weapon-record indices and target ActorValue values were not screened; this input is not identified with AV39 or an armor-rating factor.

The same helper's weapon `GetAttackDamage` value, AV66 ShieldPerks, and AV9 Block feed `percentBlocked`; AV163 ReflectDamage contributes to `criticalDamageMult` under the bounded local condition. Actor `+0xA0`/MagicTarget slot 4 is identified as `IsInvulnerable` from pinned headers and the matching-GOG base-vtable target is a false stub; if true, the helper clears selected HitData fields but not the pre-mitigation `physicalDamage` snapshot. Actor/PlayerCharacter secondary-vtable dispatch remains inferred rather than directly enumerated [EV-0304].

The captured ProcessTrapHit builder calls the common initializer, which zeros `HitData.weapon`, and does not rewrite that field; its route therefore skips the weapon-selected resistance and weapon attack-damage branches while retaining the common AV39/slot-`0xE7` calculation and later invulnerability check [EV-0302], [EV-0304]. This does not establish positive worn-armor protection, zero armor AVSK, Steam equivalence, or a vanilla level-one result. No OBJ-1 causal edge is identified. Claim mapping: CL-L139 -> EV-0304; Q-0043 bounded helper-indirection classification.

## M-0040 — DA08 level-20 rumor helper versus main-quest startup

Skyrim.esm SMQN `000DC9E1` (`DA08KickerNode`) selects QUST `000DC9E0` (`DA08RumorPointer`) under `GetLevel >=` GLOB `000DC9E2` (`DA08MinLevel` = 20) [EV-0300], [EV-0305]. Main DA08 QUST `0004A37B` has Start Game Enabled set under the EV-0301 QUST schema mapping, and 17 of 18 captured DA08-named DIAL records are owned by main DA08. The helper's bounded `Fragment_1` sets `DA08QuestScript.PlayerGotRumor`; `Fragment_2` completes its objective and stops the helper. Main-QF `Fragment_14` can advance helper state after main objective setup, so this is a helper/main-state interaction, not evidence that the level-20 node gates main-Q startup [EV-0305].

This supports a separate serialized main-quest start configuration and falsifies the all-entry-gated model for main DA08 startup within the inspected records. It does not prove INFO availability, live quest state, level-one dialogue/access, door reachability, a profile winner, or a vanilla reproduction. No shared native call, ActorValue, HitData field, armor-skill writer, ActiveEffect, or serialization primitive links this OBJ-1 path to OBJ-2 armor/XP mechanisms. Claim mapping: CL-L140 -> EV-0300/EV-0301/EV-0305; Q-0044.

## M-0041 — DA09 level-12 event start, Beacon placement, and stage callbacks

Skyrim.esm `SMQN 0009E1AD DA09IncreaseLevelNodeSHARES` selects main DA09 QUST `0004E4E1` at `GetLevel >= DA09MinLevel` (GLOB `0009E1AE` = 12) [EV-0300], [EV-0306]. The Update.esm override serializes `ENAM=LEVL` and Start Game Enabled clear under EV-0301's QUST schema mapping. The MISC Beacon `0004E4E6` has no VMAD; its callback is attached to the main quest's Gem alias. `DA09GemScript.OnContainerChanged` requests stage 100 when Player receives it while the quest stage is below 100; `DA09StatueScript.OnActivate` requests stage 200 when Player activates the statue while carrying the Gem. Neither bounded body has an explicit GetLevel predicate [EV-0306].

The separate CLOC helper QUST `00081C59 DA09ChangeLocation` has Start Game Enabled clear. Its Story Manager child `00081C5A` requires a function-56 DA09 stage-0 condition and uses the DA09ChangeLocChance global; the helper's stage fragment adds the main quest's Gem alias reference to a BossContainer alias. This is item placement after main DA09 has reached stage 0, not a pre-start quest caller. The beam-shooter is conditioned on stage 300, the Shade death callback requests stage 400, and Update's fix-up fragment relocates the alias under a stage/location condition; none is an independent start call in the inspected PEX bodies [EV-0306].

The five-master raw-reference screen contains no direct Beacon REFR/LVLI placement and no external main-DA09 start script among the interpreted VMAD candidates. A group-aware full Skyrim.esm DIAL/INFO screen maps 20 DA09-owned topics and 25 INFO children; none contains a function-80/GetLevel condition. GOG EV-0313 shows that the registered SetStage callback can conditionally initialize a quest before stage application, and EV-0314 maps DA09's source `ENAM=LEVL` to the GOG runtime event field. Its ready-bit value, alias completion, Steam callback behavior, and low-level Beacon route remain unresolved. EV-0272's separate event guard belongs to `Quest.SetCurrentStageID`. No active-profile winner or level-one vanilla reproduction is established.

Cross-domain assessment: these quest flags, aliases, item placement, and stage transitions share no identified native call, HitData field, ActorValue, armor-skill writer, ActiveEffect, or serialization primitive with OBJ-2 armor/XP paths [EV-0306], [EV-0217]–[EV-0223], [EV-0302]–[EV-0304]. No causal edge is added. A same-build state/call dependency or discriminating experiment linking quest startup to the armor/XP route would falsify this no-edge assessment. Claim mapping: CL-L141 -> M-0041; Q-0045.

## M-0042 — DA13 level-10 Refugee/helper start below the main level-12 node

The main DA13 SMQN `000C4CC5` selects QUST `0008998D` at `GetLevel >= 12`. A separate WEJS14 QUST `000BED92` has `GetLevel >= 10`; its Afflicted Refugee INFO `000BECE9` requests WEJS14 stage 100 when WEJS14 is at stage 0, main DA13 is below stage 10, and the speaker fills alias 39. WEJS14's stage-100 fragment sets `Da13Intro` stage 1; the helper starts its intro scene; the scene fragment sets helper stage 100; and the helper stage-100 fragment calls `Start()` on main DA13 [EV-0307]. This supports a serialized alternate start below the ordinary level-12 node at the level-10 threshold.

The full group-aware DA13 DIAL/INFO join maps 23 main-owned topics plus the helper topic. Captured main-owned TIFs request DA13 stages 1, 5, 10, 15, 20, 21, 31, 40, 45, 81, and 100, but contain no `Start()` call on the main quest. Unconditioned INFO `000A1A65` requests stage 21; whether its owner dialogue is available while DA13 is stopped remains unknown. The Empty Vessel activator also requests stage 21, but placed REFR `000E6C89` is Initially Disabled and its only identified enabler belongs to main DA13's Kesh alias. Goo/Orchendor callbacks and WEJS15 are downstream. The generic alias script attached to Orchendor alias 6 was not found through the supported base-Misc extractor; its serialized properties are `preReqStage=40` and `StageToSet=75`, but callback semantics are not established [EV-0307].

This is bounded prepared-official-source and base-Misc PEX evidence, not an active-profile winner or runtime result. It does not establish level-one access, actual Refugee encounter/alias availability, Steam SetStage behavior, physical access, or a vanilla reproduction. No shared call, HitData field, ActorValue, armor-skill award, ActiveEffect, or serialization primitive links this OBJ-1 chain to OBJ-2 mechanisms [EV-0307], [EV-0217]–[EV-0223], [EV-0302]–[EV-0304]. No causal edge is added. Claim mapping: CL-L142 -> M-0042.

## M-0043 — DA06 level-9 Story Manager path and Largashbur stage callbacks

Prepared Skyrim.esm places main DA06 `QUST 0003B681` under level-9 `SMQN 000A0E73` / `GLOB 000A0E71`; its Start Game Enabled flag is clear. The initial exterior hostile trigger only changes faction hostility. The fixed giant's XESP parent is an initially disabled XMarker enabled by DA06 stage-0 Fragment_0, so that placed giant route has a serialized downstream dependency on startup [EV-0308]. The Atub dialogue callback requests stage 50 without an INFO level or stage condition, and Orc/Atub death callbacks may request stage 255. No captured DA06 TIF calls `Start()`.

This narrows the pre-level-9 candidates to stopped-owner stage delivery and alias/dialogue availability; those behaviors remain unknown for installed Steam 1.6.1170.0. GOG EV-0313 shows a conditional startup-before-stage path for the registered Quest.SetStage callback, and EV-0314 maps DA06's source `ENAM=LEVL` to the GOG runtime event field. DA06's exact ready bit, stopped-owner dialogue execution, and Steam behavior remain unknown. EV-0272's Event-ID guard applies to Quest.SetCurrentStageID, not Quest.SetStage. The bounded five-master/base-Misc PEX screen is not a profile winner or runtime test and establishes no level-one progression. The quest, faction, and placement evidence shares no supported mechanism with armor protection or hit-earned armor XP. Claim mapping: CL-L143 -> M-0043; Q-0047.

## M-0044 — Clothing classification candidate and cached armor factor (Q-0048)

The prepared five official masters contain 40 source rows / 36 unique ARMO FormIDs with BOD2 Clothing and positive DNAM; their 56 resolved ARMA links are likewise typed Clothing [EV-0309]. GOG AE 1.6.1179.0's unblocked hit receiver skips worn ARMO subtype 2 and requires positive base DNAM for its AV11/AV12 selection [EV-0222]. The PlayerCharacter slot `0xE7` getter used by the GOG hit builder returns a cached float at `this+0x274` [EV-0261], [EV-0309].

Q-0048 left the cache writer and Clothing contribution open. Q-0050 later mapped the BOD2 parser and cache visitor: runtime `ARMO+0x1BC` is serialized Armor Type, and the visitor excludes value 2 before accumulating rating [EV-0311]. `ClothesBeggarRobes` remains a source acquisition lead but does not contribute to this GOG cached factor. The original question was source-side; Steam protection, AVSK, and acquisition remain untested. No causal edge connects the armor path to OBJ-1 quest startup. Claim mapping: CL-L144 -> M-0044; Q-0048; detailed mapping in M-0046.

## M-0045 — DA02 level-30 entry, WEDA02 helper, and book callback (Q-0049)

Prepared Skyrim.esm selects main DA02 `QUST 0004D8D6` through `SMQN 0009E1AF`, whose `GetLevel` threshold is global `DA02MinLevel=30`; the main QUST has Start Game Enabled clear and `ENAM=LEVL`. WEDA02 `QUST 0004A602` is reached through the `WEStart`/`WERoadStart` event family but its serialized QUST conditions require DA02 already running and at stage <1, so this is a downstream event helper in the inspected source path [EV-0310]. The four fixed book references run `DA02BookScript.OnCellLoad`, which enables at or above the same global and disables below it. `OnRead` can still request DA02 stage 1 below stage 1. GOG EV-0313 shows that the registered SetStage callback can conditionally call EnsureQuestStarted before stage application, but the record's exact event-ID/ready-bit runtime values and Steam effect remain unresolved. The generic book lists begin at level 24; `QABooksContainer` is source-placed in QASmoke.

This supports the level-30 Story Manager gate and rejects WEDA02 as an independent main-quest start in the inspected official source. It does not prove this is the only practical route: the registered GOG SetStage path is conditional, and EV-0314 maps DA02's `ENAM=LEVL` to the GOG `+0xE0` field tested by its entry guard. Natural player-level book acquisition, the exact target ready bit, dialogue, alias fill, Steam event selection, and Sacellum access remain open. The five-master direct-parser screen is not a profile winner; native xEdit failed before enumeration; no level-one Steam run occurred. No objective edge to OBJ-2 is justified: these quest/event records share no identified HitData field, armor ActorValue, skill-award call, ActiveEffect, or serialization primitive with the armor mechanisms. Claim mapping: CL-L145 -> M-0045.

## M-0046 — BOD2 Armor Type exclusion from the cached factor (Q-0050)

In GOG AE 1.6.1179.0, `FUN_140278170` handles the BOD2 record subrecord and reads its two adjacent 32-bit words beginning at `ARMO+0x1B8`; its endian path swaps the second word at `+0x1BC`. The pinned TES5Edit dev-4.1.6 schema places Armor Type at serialized BOD2 byte offset 4 and defines Clothing as value 2 [EV-0309], [EV-0311]. Thus the inspected GOG parser maps BOD2 Armor Type to runtime `ARMO+0x1BC`.

`FUN_140728b70` traverses inventory changes through `FUN_1402318d0` and stores its visitor aggregate at PlayerCharacter `+0x274`. The visitor method `FUN_14072a500` requires ARMO form type byte `0x1A` and `ARMO+0x1BC != 2` before computing and adding rating [EV-0311]. PlayerCharacter slot `0xE7` returns this cache value to the GOG hit damage builder [EV-0261]. The cached path therefore excludes Clothing before hit mitigation. It does not prove that any Light/Heavy armor configuration can achieve zero AVSK in Steam, but it falsifies Clothing DNAM as the protection half of the proposed Clothing/no-armor-XP candidate.

This adds an OBJ-2 causal chain from serialized BOD2 Armor Type, through the runtime field and visitor filter, to the cached value read by hit calculation. It adds no OBJ-1 edge: the quest-start records expose no shared call, state field, or ActorValue with this armor path. A same-build dependency between this visitor/cache chain and a quest Story Manager predicate would change that assessment. Claim mapping: CL-L146 -> M-0046; Q-0050.

## M-0047 — Physical-trap cached Light/Heavy rating candidate (Q-0052)

GOG AE 1.6.1179.0 `FUN_140278170` loads the ARMO `DNAM` subrecord at runtime `+0x200`; `FUN_140223b20` reads its low word and combines it with helper data and actor-supplied factors. The inventory visitor `FUN_14072a500` excludes BOD2 type 2, but types 0 and 1 select separate actor-derived factor values and enter this rating calculation. The cache writer `FUN_140728b70` accumulates and scales those contributions at PlayerCharacter `+0x274`, which PlayerCharacter slot `0xE7` supplies to the hit builder [EV-0312], [EV-0311], [EV-0261].

Physical trap builder `FUN_1407dd110` shares the AV39/cache mitigation helper `FUN_1407ddf50` with ordinary hit builders. Its wrapper enters the shared receiver handler without calling normal resolver `FUN_1406bcaa0`, where the known AV11/AV12 branch occurs [EV-0302]. The bounded handler-site census finds no mapped AV11/AV12 award but retains cleanup-target, derived-reference, and runtime-dispatch uncertainty [EV-0303], [EV-0304]. EV-0315 traces two temporary handles through generic conversion/resolution and the HitData `+0x20` sourceRef handle; it does not identify concrete cleanup target classes or exhaust derived reference dispatch.

EV-0319 refines the first two receiver cleanup sites for the captured ProcessTrapHit route. The wrapper initializes HitData `+0x18/+0x1C` to zero; the builder writes a receiver-derived value only to `+0x1C`; and `FUN_1407ddf50` / `FUN_1407df220` do not write `+0x18`. The first conditional release at `0x1406BA047` is therefore skipped on this route. The second, receiver-derived release at `0x1406BA070` resolves the PlayerCharacter `+0x20` secondary table, whose slot `+0x8` thunk dispatches to the PlayerCharacter destructor chain when its refcount branch is taken. That teardown body has eight unresolved indirect sites, so this does not establish a global no-award result.

The static source therefore supports a Light/Heavy physical-trap candidate, not proof that a qualifying hit reduces damage without armor XP in Steam.

Direct Skyrim.esm parser outputs show positive DNAM values for one type-1 Heavy and one type-0 Light cuirass; the record query did not emit the plugin byte hash, and these are not active-profile winners [EV-0312]. The actor entry-point visitor selector `0x55` remains unnamed and unmeasured. EV-0315 narrows handle provenance but leaves the actual Steam receiver dispatch unresolved. Exact Steam 1.6.1170.0 protection, repeated-hit AVSK, player level, and a normal positive-damage control remain required. No OBJ-1 causal edge is proposed. Claim mapping: CL-L147 -> M-0047; Q-0052.

## M-0048 — Conditional GOG Quest.SetStage startup path (Q-0053)

GOG AE 1.6.1179.0 native registration evidence distinguishes three Papyrus methods: `Quest.Start` (`FUN_140a48c50`), `Quest.SetCurrentStageID` (`FUN_140a48aa0`), and a separate `Quest.SetStage` candidate (`FUN_14034de90`) [EV-0313]. The SetStage callback's table association is strongly supported by its method-name slot, the matching GetStage peer layout and diagnostic, and the callback's stage lookup/write path, although the registration table has no indexed code xrefs. EV-0272's event-ID/flag-gated deferred-queue behavior therefore belongs to SetCurrentStageID and must not be attributed to SetStage.

On the accepted SetStage state path, `FUN_14034de90` calls `TESQuest::EnsureQuestStarted` (GOG RVA `0x3C9D30`) in start-now mode before stage lookup. The inspected stopped-state branch can call `BGSStoryTeller::BeginStartUpQuest` (GOG RVA `0x532E60`), reset stage-entry/current-stage bookkeeping, process quest-reference promotion work, set readiness state, and add the quest to a manager list before applying the requested stage fragment [EV-0272], [EV-0313]. The callback path contains no explicit player `GetLevel` comparison, but event-ID, ready-bit, and internal-state guards remain. This falsifies the universal claim that SetStage only works on an already-running quest, while leaving stopped LEVL-quest acceptance, complete running/alias/journal state, functional access, Steam behavior, and level-one reproduction unresolved.

EV-0310 records DA02 `ENAM=LEVL`; EV-0306 and EV-0308 record LEVL main quests DA09 and DA06. EV-0314 resolves the GOG loader field map; exact ready state, callback reachability, functional access, Steam behavior, and a vanilla level-one transition remain open. No causal edge to OBJ-2 is justified. Claim mapping: CL-L148 -> M-0048; Q-0053.

## M-0049 — GOG QUST ENAM field and conditional SetStage guard (Q-0055)

The GOG AE 1.6.1179.0 TESQuest constructor initializes the dword at `+0xE0` to `0xFFFFFFFF`. Its installed TESQuest vtable maps the bounded QUST parser slot to `FUN_1403c7a50`; the parser's `ENAM` case reads four bytes into object offset `+0xE0`, while its separate `DATA` case writes through `+0xDF` [EV-0314]. Direct source records DA02 `0004D8D6`, DA09 `0004E4E1`, and DA06 `0003B681` contain serialized `ENAM=LEVL` [EV-0314], [EV-0310], [EV-0306], [EV-0308].

The distinct registered GOG `Quest.SetStage` callback admits its initial path when quest `+0xDC` bit 0 is set or `+0xE0 == -1` [EV-0313]. EV-0316 maps the load-time `+0xDC.0` value to serialized `DNAM.General.Flags` bit 0 (`Start Game Enabled`) for the inspected GOG parser path; DA02/DA06/DA09 source flags are clear while DA04's is set. A TESQuest virtual method can later clear bit 0, but its dispatch timing is unresolved. Therefore the source-to-guard field mapping is established only at load-time: the installed Steam value, callback timing/reachability, later startup guards, running state, alias fill, functional access, and level-one progression remain unobserved. This is a GOG/source mechanism map, not a level-one bypass. No causal edge to OBJ-2 is justified. Claim mapping: CL-L149 -> M-0049; Q-0055.

## M-0050 — Serialized QUST Start Game Enabled input to TESQuest guard bit (Q-0056)

In GOG AE 1.6.1179.0, QUST vtable slot 6's parser `FUN_1403c7a50` reads `DNAM` and writes its first U16 to `TESQuest+0xDC`; the versioned TES5Edit schema identifies that U16 as `General.Flags` and bit 0 as `Start Game Enabled` [EV-0316]. Exact direct-parser source values set bit 0 for DA04 (`0x0111`) and clear it for DA02, DA06, and DA09 (`0x0100`) [EV-0316], [EV-0301], [EV-0306], [EV-0308], [EV-0310]. The inspected constructor and helper only OR `0x0100` into the word. TESQuest vtable slot 19 maps to `FUN_1403c8420`, whose body can clear bit 0 when set [EV-0316]. EV-0318 resolves the GOG load-finalization path: source-file records call slot 6 with the record buffer, parsed forms are registered by FormType, and the manager's post-file-load pass includes QUST type `0x4D` and dispatches slot 19. This establishes a post-parse slot-19 call path and falsifies an only-later-lifecycle model for GOG. The first natural `Quest.SetStage` callback order remains a load-order inference, not a direct observation. Connect the loaded field and finalization call to the initial guard in M-0049, but do not infer a target quest's callback reachability, running state, alias fill, access, Steam equivalence, or level-one progression. No OBJ-2 edge is supported. Claim mapping: CL-L150 and CL-L151 -> M-0050; Q-0056/Q-0057.

Q-0059 / EV-0320 classifies a second GOG file-load path: both `FUN_1401b9510` and `FUN_1401be290` call the QUST-inclusive `FUN_1401bdf20` sweep after per-file record work. The second loader's direct caller, `FUN_1403753b0`, has no analyzed direct code caller; its one incoming reference is data in an unclassified table/metadata region. The registered `Quest.SetStage` binding is likewise table-based without indexed code xrefs [EV-0313]. No class-resolved natural callback dispatch is linked to either loader, so the first natural callback order remains unresolved rather than proven to follow finalization. This refines only M-0050's load-timing boundary and does not establish a level-one start or callback reachability. Claim mapping: CL-L153 -> M-0050; Q-0059 [EV-0320].

## M-0051 — Additional official GetLevel fields and DA03Start guard dialogue (Q-0060)

The complete five-official-master CTDA census finds function-index-80 `GetLevel` conditions in INFO, SMQN, ENCH, MGEF, PACK, PERK, QUST and SPEL records. The fixed official-source-layer comparison retains 320 of 327 source hits; it is not an active-profile winner. The concrete progression-related path is `PACK 000E0D53 DA03StartGuardStartQuestGreet` (`GetLevel >= 10`, `GetStage(DA03Start) < 5`) -> `DIAL 000E0D44 DA03StartGuardGreetBranchTopic` -> type-7-group child `INFO 000E0D46` (same level/stage predicates) [EV-0321]. This establishes a level gate on that guard-greeting selection path.

The INFO record has no VMAD/direct fragment subrecord, and the tested base-Misc-BSA extractor found no `TIF__000E0D46` stream. The separately serialized `QF_DA03Start` `Fragment_27` method calls `DA03.SetStage(5)`, but the captured source does not connect that method to INFO `000E0D46` [EV-0321]. Therefore the guard path is gated while Lod's separate topics and any alternate main-quest start remain open. This is a candidate access boundary, not a level-one glitch or complete quest-start mechanism. No causal edge to OBJ-2 armor protection or hit-earned XP is justified. Claim mapping: CL-L154 -> M-0051; Q-0060.

## M-0052 — Lod DA03Start level-gated handoff and unlevelled reward route (Q-0061)

The fixed-official-order DA03Start topic join identifies the Lod alias and maps the stage-10 helper handoffs to GetLevel >= 10. The helper's stage-10 fragment calls DA03.SetStage(5). The separately unlevelled stage-20 goodbye callback only advances DA03Start into a reward fragment; stage 20 grants 25 gold and stage 200 stops the helper [EV-0322], [EV-0323]. This closes the direct Lod callback candidate in source scope, not every profile/runtime route. No level-one access/reproduction or causal edge to OBJ-2 is established. Claim CL-L155 -> M-0052; Q-0061.

## M-0053 — Physical-trap direct receiver path past inline armor skill routing (Q-0062)

In GOG AE 1.6.1179.0, ProcessTrapHit's PlayerCharacter receiver reaches the shared HitData construction/resistance path and then calls FUN_1406b9df0 directly. The known FUN_1406bcaa0 wrapper contains the visible AV11/AV12 armor or AV9 Block skill call before it calls the same downstream handler. The trap handler's mapped UseSkill call is AV15 Sneak, making physical traps a vanilla candidate for functional armor with suppressed hit-earned armor XP [EV-0324], with route context in EV-0293, EV-0261, and EV-0217–EV-0223.

The candidate remains unverified: the handler has 28 unresolved indirect sites, and no positive final damage, effective protection, raw AVSK, Steam mapping, profile winner, or vanilla reproduction exists. No causal edge to OBJ-1 is supported. Claim CL-L156 -> M-0053; Q-0062.

## M-0054 — Dawnguard Fort dialogue stage request outside the level-10 helper (Q-0063)

In the fixed official-master source view, start-enabled `DLC1VQ00` -> Durak INFO/TIF stage 20 -> Durak INFO/TIF stage 50 -> `DLC1VQ01MiscObjective` stage 10 -> Isran stages 120/150 -> Tolan stage 180 -> helper QF `Fragment_16` calling `DLC1VQ01.SetStage(10)` -> main VQ01 stage-10 Dimhollow objective/map marker [EV-0326]. The mapped INFO and stage callback conditions contain no serialized `GetLevel >= 10` predicate. Separate VQ00 approach INFOs retain the level-10 condition. Native xEdit reports VQ00 `Start Game Enabled=1`, while VQ01 has that flag clear; its `GetInCell` conditions belong to objective targets.

This supports a strong level-one source candidate and falsifies the claim that the captured Fort dialogue route only reaches rumor/helper state. It does not establish stopped-quest startup, natural dialogue availability, alias fill, useful access/progression, Steam 1.6.1170.0 behavior, a profile winner, or vanilla reproduction. GOG AE 1.6.1179.0 `Quest.SetStage` startup evidence EV-0313 remains separate-build context. The evidence changes the OBJ-1 route model only; no shared ActorValue, HitData, armor-skill writer, ActiveEffect, or serialization primitive links it to OBJ-2. Claim CL-L157 -> M-0054; Q-0063.

## M-0055 — PlayerCharacter cell-change cleanup of `+0x730` (Q-0064)

Primary PlayerCharacter vtable slot `0x98` at GOG RVA `0x18ACD70` resolves to `FUN_1407373e0`. Its transition path reads field `+0x730`, may invoke inner slot `+0x1C0`, clears the field, and conditionally invokes refcount-final slot `+0x8` [EV-0327]. Complete displacement and writer analysis found no non-null direct/computed PlayerCharacter writer; alias/copy propagation remains untested. Field type and skill-award reachability remain unresolved. No OBJ-1 edge is supported. Claim CL-L158 -> M-0055.

## M-0056 — PlayerCharacter global callback reaches PlayerCamera cleanup (Q-0064)

The PlayerCharacter cleanup's global slot-0 callback uses the global initialized through `FUN_1408e3f50` with a `PlayerCamera::vftable` object. Slot 0 targets `FUN_1408e8b50` -> `FUN_1408e4070`; that cleanup body retains five indirect resource calls and has no direct mapped skill-progress edge in the captured census [EV-0327], [EV-0325]. Dynamic targets and descendants remain unresolved. No OBJ-1 edge is supported. Claim CL-L159 -> M-0056.

## M-0057 — PlayerCharacter `+0x8F8` resource-backed release field (Q-0064)

The complete GOG displacement scan ties PlayerCharacter `+0x8F8` to `FUN_140736be0`, which calls `FUN_140e05900` with `Actors\Character\1stPerson\Skel` and stores the returned object; teardown helper `FUN_140737210` clears the field and conditionally invokes refcount-final vtable slot `+0x8` [EV-0328]. The actual object class, destructor target, and descendant skill behavior remain unknown. The other screened fields remain untyped or only partially attributed. No OBJ-1 edge is supported. Claim CL-L160 -> M-0057.

## M-0058 — PlayerCharacter +0x9A0/+0x9A8 refcount-final callback fields (Q-0064)

PlayerCharacter teardown FUN_14072fd60 decrements the references stored at +0x9A0/+0x9A8 and calls each object's vtable slot +0x8 when the old count is one. FUN_1407445d0 stores candidate values into those offsets; its direct callers pass DAT_143188918, now resolved as the PlayerCharacter object constructed by FUN_14064cac0/FUN_14072ed70 [EV-0344]. The stored resource-derived values and finalizer targets remain unresolved [EV-0329]. Claim CL-L161 -> M-0058. No ActorValue/skill sink edge is supported or excluded; no OBJ-1 edge is supported.

## M-0059 — AutoVanity queued HUD Scaleform branch (Q-0064)

The AutoVanity callback constructs queued message type 0x17 under the HUD Menu key. The exact HUDMenu slot+0x20 callback matches that payload and calls Scaleform ShowElements with UI values; the optional native callback argument is zero [EV-0330]. This resolves one PlayerCamera callback subbranch away from native Actor skill progress, but does not resolve other teardown callbacks, ActionScript behavior, or Q64-H1/H2. No OBJ-1 edge is supported. Claim CL-L162 -> M-0059.

## M-0060 — Conditional NiNode finalizer candidate for +0x8F8 (Q-0064)

The GOG NIF parser registry maps the serialized name NiNode to FUN_140d1e880, which installs vtable RVA 0x19AC3F0. Slot +0x8 reaches a deleting-destructor thunk and primary NiNode destructor that final-releases child objects and delegates to NiAVObject cleanup [EV-0331]. The exact first-person skeleton asset root/subtree is not observed, child finalizers and the slot+0x128 callback remain dynamic, and no AV11/AV12 sink result follows. No OBJ-1 edge is supported. Claim CL-L163 -> M-0060.

## M-0061 — Cell/resource metadata producer candidate for +0x9D0 (Q-0064)

Candidate writer FUN_140766540 stores a FUN_1401a19c0 result at receiver+0x9D0 and releases a replaced value through slot+0x8. The lookup chooses a nested TES-owned object and calls FUN_1402b8cf0; its receiver layout and Havok ray-query caller are consistent with TESObjectCELL, whose constructor clears +0x130. The type-0x11 branch and type-2/type-1 resource metadata fallback expose no concrete result vtable or finalizer [EV-0332]. FUN_1402e8580 in the writer derives a separate local and is not the stored pointer. No AV11/AV12 edge or OBJ-1 edge is supported; Q64-H1/H2 remain open. Claim CL-L164 -> M-0061.

## M-0062 — Data-selected model-resource adapter for +0x9A0/+0x9A8 (Q-0064)

FUN_140216b40 loads a generic resource, conditionally calls FUN_140d19980, and passes its output into the EV-0329 candidate PlayerCharacter setter path. FUN_140d19980 invokes unresolved slots +0xB8 and +0xE8; the recursive hierarchy check does not recover a concrete loaded root. The final slot+0x8 target and descendants remain dynamic [EV-0333]. No edge to Actor::UseSkill AV11/AV12 is added or excluded. Claim CL-L165 -> M-0062.

## M-0063 — PlayerCharacter +0x730 cell-scene child lifecycle (Q-0064)

FUN_1407373e0 adds the +0x730 object through a cell-scene child node's slot+0x1A8 and removes it through the parent pointer at child+0x30 via slot+0x1C0. The GOG NiNode candidate add method stores child+0x30 as parent; its remove wrapper delegates to slot+0x1B8 and the child-array remover clears the parent and releases references [EV-0334]. The actual runtime parent table and child finalizer remain unresolved. Claim CL-L166 -> M-0063.

## M-0064 — PlayerCamera active-state transition callback (Q-0064)

FUN_140551300 invokes the current PlayerCamera+0x28 state's slot+0x10 before swapping the state pointer, then balances references through slot+0x8. State-array selection is routed by FUN_1408e8e00. The index-9 ThirdPersonState vtable maps slot+0x10 to FUN_1408e9990; that body resets camera fields, conditionally calls two helpers, and final-releases a member at +0xA0 through an unresolved slot+0x8 target [EV-0335]. No direct AV11/AV12 sink is present in this body; all descendants and other state targets remain open. Claim CL-L167 -> M-0064.

## M-0065 — ThirdPersonState+0xA0 named-child resource candidate (Q-0064)

FUN_1408ea490 stores and refcounts ThirdPersonState+0xA0. FUN_1408e6500 obtains an object through PlayerCharacter vtable+0x378, calls that object's slot+0x150 with a converted input, and passes the result into the state setter. NiNode slot+0x150 maps to FUN_140d1f3c0 recursive child traversal, but the actual receiver vtable and returned member finalizer are unresolved [EV-0336], [EV-0329], [EV-0334]. This is a conditional NiAVObject-family candidate only; no causal edge or AV11/AV12 result is established. Claim CL-L168 -> M-0065.

EV-0337 refines M-0065: PlayerCharacter slot +0x378 is FUN_1407371f0, whose flag-zero branch selects either a TLS context field or a nested +0x68 member through FUN_1402e55a0. The helper has no outgoing call sites, but its returned class and the consumer's slot +0x150 target remain unresolved. The exact slot mapping does not establish a NiNode edge. Claim CL-L169 -> M-0065.

EV-0338 extends M-0064 with two state-specific slot+0x10 callbacks. FirstPersonState clears +0x68 and calls the shared array helper; BleedoutCameraState releases +0x120 through slot+0x8 and calls playback/event helpers. Their callback bodies have no direct Actor::UseSkill AV11/AV12 sink, but the Bleedout finalizer, shared helper descendants, other initialized states, and state selection remain open. Claims CL-L170 and CL-L171 -> M-0064.

EV-0339 extends M-0064 with FreeCameraState and IronSightsState callbacks. FreeCamera updates its state arrays and two fields through a no-call helper; IronSights uses a return-only slot+0x10 target. Neither sampled body contains a direct AV11/AV12 sink. Other state classes, shared array-helper descendants, member finalizers, and teardown selection remain open. Claims CL-L172 and CL-L173 -> M-0064.

EV-0340 extends M-0064 with FurnitureCameraState and PlayerCameraTransitionState. Furniture resolves a handle, applies a bounded float update, and performs a nested slot+0x8 finalizer; transition reuses the no-op callback shared with IronSights. Furniture's exact finalizer and state selection remain open. Claims CL-L174 and CL-L175 -> M-0064.

EV-0341 extends M-0064 with the four helper-created PlayerCamera states. VATS uses a shared no-op slot+0x10 target, TweenMenu copies one state field, and Horse/Dragon share FUN_1408e9990. That helper releases a +0xA0 member and may dispatch its dynamic slot+0x8 finalizer. Neither concrete finalizer type nor ProcessTrapHit reachability is established. Claims CL-L176 and CL-L177 -> M-0064.

EV-0342 extends M-0064: ThirdPersonState+0xA0 receives the return of a type-erased slot+0x150 call on the PlayerCharacter slot+0x378 result. Setter/reset/destructor paths refcount and may finalize the prior object through slot+0x8. The getter branch, concrete return type/finalizer, and ProcessTrapHit reachability remain unknown. Claims CL-L178 and CL-L179 -> M-0064.

EV-0343 refines M-0065: the PlayerCharacter slot+0x378 / slot+0x150 path receives a pointer whose wrapper performs header refcounting, consistent with a string reference. NiNode recursively searches children with an opaque argument at the same slot, so the named-child model is compatible but not a class identity. CL-L180 -> M-0065.

EV-0344 refines M-0065: FUN_1408e6500's slot +0x378 receiver is the PlayerCharacter global constructed by FUN_14064cac0/FUN_14072ed70. Its flag-zero getter selects a TLS +0x5F0 member guarded by owner +0x5F8, or a nested PlayerCharacter +0x68/+0x68 member. The caller wrapper is entry 1 of AnimatedCameraStartHandler::vftable. The selected object's concrete type and its slot +0x150 target remain unresolved. Claims CL-L181 and CL-L182 refine the provenance; no trap-cleanup or skill-XP edge is added.

EV-0345 refines M-0065: paired AnimatedCameraStartHandler/AnimatedCameraDeltaStartHandler methods forward a BSFixedStringCI-type-consistent argument into FUN_1408e6500 with flags 0/1. This supports a named-lookup interpretation but not a NiNode receiver match; the concrete slot +0x150 target and returned member finalizer remain unresolved. Claim CL-L183 -> M-0065.

## M-0066 — ProcessTrapHit PlayerCharacter final-release site map (Q-0064)

The complete FUN_14072fd60 census has eight indirect sites. Five formerly missing contexts are conditional refcount-final slot +0x8 calls on PlayerCharacter fields +0x9D0, +0x9A8, +0x9A0, +0x8F8, and +0x730 [EV-0346]. The other three are the +0x730/+0x30 interface slot +0x1C0, its child slot +0x8 release, and the PlayerCamera global slot-0 cleanup [EV-0325], [EV-0327]. The site fields are mapped, but the resource-selected vtables and destructor descendants remain unresolved; this is not a no-skill result. Claim CL-L184 -> M-0066.

## M-0067 — First-person skeleton resource lifetime at PlayerCharacter+0x8F8 (Q-0064)

FUN_140736be0 passes the named first-person skeleton path `Actors\\Character\\1stPerson\\Skel` to FUN_140e05900; the generic mesh loader prepends `meshes\\`, returns a refcounted resource object through handle member +0x28, and the caller retains it at PlayerCharacter+0x8F8 [EV-0347]. The caller uses slots +0x28 and +0x150, while teardown final-releases the field through dynamic slot +0x8 [EV-0346]. This supports a scene-resource role but does not prove the exact NIF root class, concrete finalizer, or any AV11/AV12 descendant. Claim CL-L185 -> M-0067; no causal sink edge is resolved.

## M-0068 — Descriptor-selected +0x9D0 fallback values (Q-0064)

The mapped metadata fallback checks key 2 and then key 1 in descriptor-backed arrays; the helpers return 64-bit entry values without establishing the selected object's class or vtable [EV-0348]. The separate type-0x11 path remains conditional [EV-0332]. Claim CL-L186 -> M-0068. This does not establish or exclude an AV11/AV12 skill-progress descendant.

## M-0069 — Model-resource adapter and sorted member lookup (Q-0064/Q-0065)

The candidate +0x9A0/+0x9A8 producer loads a generic mesh resource, passes its retained object through an adapter that returns virtual slot +0xB8 and invokes slot +0xE8, then resolves named members through a sorted pointer array helper [EV-0349], [EV-0333]. This differs from the +0x8F8 slot +0x150 lookup callsite [EV-0347] but does not identify either concrete root class or prove distinct vtables. No finalizer descendant reaches or is excluded from the AV11/AV12 sink. Claim CL-L187 -> M-0069.

## M-0070 — +0x9A0/+0x9A8 mode-selected reference setter (Q-0064)

FUN_1407445d0 selects +0x9A8 for mode zero and +0x9A0 otherwise, AddRefs the incoming object, and final-releases a replaced pointer through dynamic slot +0x8. FUN_140215660 passes the model-resource producer output on one caller path [EV-0350], [EV-0349], [EV-0333]. The incoming object's concrete class and finalizer chain remain unresolved; no AV11/AV12 edge is added or excluded. Claim CL-L188 -> M-0070.

## M-0071 — Cell scene member helper at +0x130 (Q-0064)

FUN_1402b8510 reads receiver+0x130 and returns the 64-bit member at +0x130+8 when non-null; it has no direct or indirect calls in its body. Its caller census includes FUN_1407373e0, but the non-null writer and returned object's class/finalizer remain unresolved [EV-0351], [EV-0332], [EV-0334]. Claim CL-L189 -> M-0071. No AV11/AV12 edge is established or excluded.

## M-0072 — PlayerCamera cleanup object dispatch (Q-0064)

FUN_1408e3f50 stores PlayerCamera in DAT_1430febf8 and installs the table whose slot 0 is the deleting-destructor wrapper FUN_1408e8b50. Its destructor FUN_1408e4070 clears the global and releases owned references through five unresolved indirect calls. The 13-entry pointer array uses generic refcount release; the TESCamera +0x28 member and array entries initialize null. No AV11/AV12 edge is established or excluded [EV-0352], [EV-0325], [EV-0327]. Claim CL-L190 -> M-0072.

## M-0073 — PlayerCamera cell-transition bhkRigidBody cleanup (Q-0064)

FUN_1407373e0 passes DAT_1430febf8 to FUN_1408e7230, which creates a bhkRigidBody and stores it at PlayerCamera+0x128. That member's slot+8 path resolves through the exact bhkRigidBody table to FUN_140d28f40 -> FUN_1402f2d10 -> FUN_140e92c60. The body destructor releases a body+0x28 pointer array through dynamic slot+8 calls. No direct AV11/AV12 sink is established, but the child targets remain unresolved [EV-0353]. Claim CL-L191 -> M-0073.

## M-0074 — Empty initial bhkRigidBody child cleanup (Q-0064)

The PlayerCamera+0x128 bhkRigidBody initializes body+0x28 to null and body+0x38 to zero. Its first state install calls slot+0x150 FUN_140e94580, whose loop is guarded by the +0x38 count and dispatches child slot +0x150; the initial pass executes no child iteration. Later producers and the terminal bhkRigidBody cleanup remain unresolved [EV-0354], [EV-0353]. Claim CL-L192 -> M-0074.

## M-0075 — Trap-hit scene traversal updates rigid-body constraints (Q-0064)

FUN_1406b9df0 calls FUN_1407c9980, which requests the flag-1 recursive scene traversal. The traversal routes recognized rigid-body objects through FUN_140e95df0, which can append bhkFixedConstraint or bhkMalleableConstraint objects. Their mapped callbacks attach, detach, update, or release physics state and wrapped resources. This is a bounded physics-path result; unresolved helper descendants and live armor XP remain open [EV-0355]. Claim CL-L193 -> M-0075.

## M-0076 — hkpConstraintInstance gate skips conditional removal (Q-0064)

The child constraint factory installs hkpConstraintInstance::vftable. Its slot +0x30 target returns zero, while FUN_140b3a830 calls the related-object removal helper only when that result is one. The removal branch is therefore skipped for this factory-created class; the finding is limited to the captured producer and does not cover other helper callers [EV-0356]. Claim CL-L195 -> M-0076.

## M-0077 — hkpConstraintInstance final-release callback and member cleanup (Q-0064)

For the factory-created constraint passed through FUN_140b3a830, its generic reference release may dispatch slot 0 when the count reaches one. The exact hkpConstraintInstance table maps that slot to FUN_140b36b20 and its body to FUN_140b487e0. The destructor walks a callback array at +0x40 through slot +0x18, releases member references at +0x18/+0x28/+0x30, frees storage through a TLS allocator, and restores hkBaseObject::vftable. The constructor starts the callback pointer null and low count zero, but later callback writers and member classes/finalizers are unresolved; no transitive no-skill result follows [EV-0357], [EV-0356]. Claim CL-L196 -> M-0077.

## M-0078 — hkpConstraintInstance callback-array consumer boundary (Q-0064)

The ProcessTrapHit factory path can reach FUN_140b67350, which iterates the exact constraint's +0x40 callback array using the low +0x48 count and calls each non-null entry through virtual slot +0x10. The constructor begins with null pointer/count zero. The direct call census finds FUN_140b43ab0 and FUN_140b439e0; nearby and global +0x40/+0x48 matches do not prove a writer for this receiver. Callback population and concrete callback/member descendants remain open; no no-skill conclusion follows [EV-0358], [EV-0356]. Claim CL-L197 -> M-0078.

## M-0079 — shared constraint-cleanup callers (Q-0064)

FUN_140b439e0 is called through three routes: hkpConstraintChainInstance table entry +0x8, the hkpSimulationIsland method-table cleanup entry, and a type-1 post-collision command record. EV-0362 corrects the earlier adjacent-byte interpretation of the island name. Its serializer enumerates EntityPtrs and per-entity constraint records; the exact factory object is not tied to those entries or the command record. No AV11/AV12 conclusion follows [EV-0359], [EV-0362], [EV-0356]. Claim CL-L198 -> M-0079.

## M-0080 — ProcessTrapHit hkp constraint attachment (Q-0064)

The ProcessTrapHit child factory creates a bhk constraint wrapper holding an hkpConstraintInstance. The wrapper's +0x148 path can call FUN_140e860d0 with that exact instance. In the immediate non-queued branch, FUN_140b3a710/FUN_140b43a20/FUN_140b678a0 attach it to the selected entity, read endpoint +0x130 into instance +0x10, separately insert a 0x40-byte record into endpoint +0x100/+0x108, and set the instance +0x60 record back-pointer. FUN_140b67200 then notifies existing add callbacks; the constructor begins with an empty callback array, but later writers/types are unresolved. No no-skill conclusion follows [EV-0360], [EV-0364]. Claim CL-L199 -> M-0080.

## M-0081 — hkp callback dispatch caller boundary (Q-0064)

The exact add-and-notify wrapper FUN_140b439a0 has two analyzed direct caller functions, one in a post-collision type-0 handler and one island/entity thunk. It inserts the entity constraint record, sends world callbacks, then invokes hkp add callbacks. Those callbacks use entry slot +0x8; removal uses +0x10. The retained `hkpConstraintListener` string has no analyzed references, so no concrete entry class or producer is established. No AV11/AV12 result follows [EV-0361]. Claim CL-L200 -> M-0081.

## M-0082 — hkpSimulationIsland entity/constraint collection (Q-0064)

The direct type-name handoff identifies `hkpSimulationIsland` (size 0xb8) adjacent to a method table whose serializer enumerates EntityPtrs at +0x60/+0x68 and each listed entity's +0x100/+0x108 constraint records. The table also contains add/remove callback bridge functions. This supplies a candidate owner route for the ProcessTrapHit constraint, but exact entity membership and AV11/AV12 descendants are unresolved [EV-0362]. Claim CL-L201 -> M-0082.


## M-0083 — hkpSimulationIsland EntityPtrs ownership and merge (Q-0064)

FUN_140b60b10 installs hkpSimulationIsland::vftable and initializes island +0x60 EntityPtrs storage and +0x68 count. FUN_140b60780 serializes this array and each endpoint's +0x100/+0x108 records. FUN_140b44470 appends endpoint pointers, writes endpoint +0x130 to island, and stores its member index at +0xfc. FUN_140b43f90 merges arrays, rewrites moved endpoint +0x130, and updates endpoint constraints +0x10. The static model is supported; exact live membership and AV11/AV12 remain unknown [EV-0362], [EV-0364]. Claim CL-L203 -> M-0083.


## M-0084 — constructor callback-offset false-positive screen (Q-0064)

The ProcessTrapHit factory reaches FUN_140ecdfc0 and FUN_140b48720. The exact constructor initializes its callback pointer/count at +0x40/+0x48 empty. FUN_140b91bb0's same-offset stores belong to a distinct 0xB0/0xD0 constraint-data payload passed as constructor argument four and stored at instance +0x18. FUN_140ecdfc0 then invokes wrapper slots +0x128/+0x188; their targets may still alter callback state. This rejects one false positive only and does not settle Q64-H1/H2 or AV11/AV12 [EV-0365]. Claim CL-L205 -> M-0084.


## M-0085 — ProcessTrapHit constraint wrapper callback setup boundary (Q-0064)

The fixed and malleable wrappers share +0x128 FUN_140ecd680, +0x130 FUN_140ece1a0 and +0x188 FUN_140ebeaa0. The setter updates wrapper +0x10 and the observer sets the hkpConstraintInstance +0x58 backlink while generic reference-count helpers acquire/release the object. Slot +0x188 forwards mode 1 to class-specific +0x158 cleanup that releases separate wrapper +0x18 data. Neither traced branch writes callback fields +0x40/+0x48. FUN_140b48720 and FUN_140b48a20 initialize callback pointer/count empty; the latter also seeds hkpConstraintChainInstance and hkpSimpleConstraintContactMgr constructions. The two whole-program offset scans remain receiver ambiguous and do not establish global callback emptiness or no AV11/AV12 path [EV-0366]. Claim CL-L206 -> M-0085.


## M-0086 — hkpConstraintInstance deletion callback dispatch (Q-0064)

The exact hkpConstraintInstance slot-0 destructor calls FUN_140b487e0, which invokes FUN_140b674a0 before freeing callback storage. FUN_140b674a0 walks non-null entries at instance +0x40 with count +0x48, invokes entry vtable slot +0x18 with the instance pointer, compacts null entries and decrements the count. The destructor frees the pointer array according to its encoded count/capacity bits. The entry class, producer, target and any Actor::UseSkill AV11/AV12 path remain unresolved [EV-0367]. Claim CL-L207 -> M-0086.

## M-0087 — ProcessTrapHit hkpConstraintInstance creation-time reference balance

The constructor initializes count 1 and the callback array empty. Wrapper association retains the instance to 2; FUN_140ecdfc0 drops its temporary reference to 1, so the immediate release does not invoke slot 0 or FUN_140b674a0. A later terminal release remains necessary for deletion callbacks. Claim CL-L208 -> M-0087 [EV-0368].

## M-0088 — hkp offset candidates require exact receiver identity

In the queried hkp-region candidates, +0x40/+0x48 denote curve fields, chain-data scalar parameters or GenericConstraintData-owned arrays depending on receiver type. The offset-only scan therefore does not identify the hkpConstraintInstance callback writer. Claim CL-L209 -> M-0088 [EV-0369].

## M-0089 — hkpConstraintChainInstance inherited callback phases

The chain subtype's slot +0x20 removal route reaches FUN_140b67350, which calls populated +0x40/+0x48 entries through entry slot +0x10. Its slot-0 finalizer calls FUN_140b5d520 -> base FUN_140b487e0 -> FUN_140b674a0, which uses entry slot +0x18 on the same inherited array. Callback producers, entry classes and ActorValue arguments remain unresolved. Claim CL-L210 -> M-0089 [EV-0370].

## M-0091 — Q-0065 class-family comparison boundary

The captured ProcessTrapHit factory installs hkpConstraintInstance and wraps it with either bhkFixedConstraint or bhkMalleableConstraint; the wrapper tables are distinct and their +0x158 destructor targets differ [EV-0355], while the exact hkpConstraintInstance table and slot+0x30 behavior are mapped [EV-0356]. These physics identities do not type PlayerCharacter +0x730, +0x8F8, +0x9D0, +0x9A0/+0x9A8, or ThirdPersonState +0xA0. The latter paths remain structural or data-selected [EV-0331], [EV-0334], [EV-0336], [EV-0347], [EV-0348], [EV-0349], [EV-0350]. Therefore Q65-H1/H2 remain proposed; common slot+0x8 dispatch is not a class edge. No direct Actor::UseSkill AV11/AV12 descendant is established in the mapped bounded branch, and unresolved finalizers prevent a route-wide negative. Claim CL-L218 -> M-0091; Q-0065.

## M-0090 — VQ01 conditional SetStage startup candidate (Q-0066)

The fixed five-master Fort Dawnguard route requests `DLC1VQ01.SetStage(10)` outside the separate level-10 Story Manager helper [EV-0326]. In the identity-checked GOG AE 1.6.1179.0 trace, the registered SetStage candidate can call `TESQuest::EnsureQuestStarted` in start-now mode before stage application [EV-0313], [EV-0380]. VQ01 has no serialized ENAM in the direct parser capture, while the GOG constructor defaults set +0xE0 to -1 and +0xDC bit 0x100; those values pass the observed initial SetStage and helper predicates [EV-0379], [EV-0381]. The helper still runs dynamic reference/alias preflight and may reject missing or failed required entries [EV-0382]. Thus the route is a conditional static candidate, not proof of Steam startup, alias fill, level-one reproduction, or usable Dimhollow access. No causal edge to armor XP is identified. Claims CL-L219/CL-L220 -> M-0090; Q-0066.


## M-0092 — WE13 Story Manager encounter scheduling and quest gate

The ordinary WEStart/WERoadStart route reaches SMEN 0001379A -> SMBN WEQuestNode 000896A8 -> SMQN WEQuests 0004A601 -> WE13 QUST 0009F32F. A second Solstheim route reaches SMEN 0001379A -> SMBN DLC2WENode 0401E7D9 -> SMBN DLC2WERegionNorthNode 0401E7DF -> SMQN DLC2WERegionNorthQuestNode 0401E7E1 -> the same WE13 QUST. The regional branch checks WEEnabled, DLC2 event keywords, and DLC2RegionNorthLocation; it changes scheduling context, not the selected QUST's serialized GetLevel >= LevelGateTrollCave (12) condition [EV-0387], [EV-0321]. The four tested linked PEX files show trigger-event dispatch and no direct quest start/stage writer; the fixed official-master scan and trigger-placement extraction bound that source map [EV-0388], [EV-0389], [EV-0390]. This supports a level-12 condition on the mapped selector paths, not a global claim that WE13 cannot be started or aliased by another route. Physical cave access and clean level-one state remain unobserved [EV-0260]. No edge to armor XP is supported: no shared call, ActorValue, HitData field, callback owner, or serialized state is identified [CL-L223].


## M-0093 — Grotto TopicInfo helper-to-main stage chain (Q-0069)

INFO 00095585 is owned through DIAL 00095582 by helper QUST 000955CF and is conditioned on alias 57 (`Hunter00_JKier`) [EV-0391]. Its TIF extends TopicInfo and calls `GetOwningQuest().SetStage(20)`, which targets that helper quest; the TIF separately sets `DA05.PlayerTalkedToHunter` through its main-quest property [EV-0393]. Helper stage 20 maps to a fragment that kills the Hunter alias and requests main DA05.SetStage(60). In the ordinary route, main DA05 stage 50 requests helper stage 10; helper Start Game Enabled is clear, and the bounded placed setter candidates have prior helper-stage conditions [EV-0391], [EV-0392], [EV-0394]. This supports downstream source sequencing but leaves independent helper availability and Steam fresh-state SetStage behavior open. The GOG AE 1.6.1179.0 callback is not transferred to Steam AE 1.6.1170.0 [EV-0313], [EV-0380]. No OBJ-2 edge is justified: no shared native call, ActorValue, HitData field, callback owner, or serialized state is identified [CL-L226], [CL-L227].


## M-0094 — WE13 event-anchored troll encounter placement (Q-0070)

WE13 QUST 0009F32F fills its `TRIGGER` reference alias and `myHoldLocation` location alias from Story Manager event data R1/L1. It filters `myAppropriateLocation` against selected hold locations, resolves `TravelMarker1/2` as WETravel linked-reference children of `TRIGGER`, and creates `EncTroll` at `TravelMarker1` [EV-0395]. This record therefore describes encounter placement relative to an event anchor; the name `LevelGateTrollCave` does not identify a fixed cave cell or door [EV-0321], [EV-0395], [EV-0396]. The record map does not establish alias fill, actor spawn, physical access, or a global start-path negative. Physical cave trolls remain a separate location question. No causal edge to OBJ-2 is justified: no shared native call, ActorValue, HitData field, callback owner, or serialized state links this encounter to armor XP [CL-L228], [CL-L229].

## M-0095 — Bounded caller routes into the HitData skill resolver (Q-0073)

In GOG AE 1.6.1179.0, `FUN_140659160` switches on an event tag; case 0xB forwards an Actor pointer and two event bytes to `FUN_1406bb690`. The dispatcher is reached from `FUN_14065b800` after its callback method does not consume the event. A separate `FUN_1407ba3e0` function calls `FUN_1406bb690` only after Actor virtual slot 0x99 returns false and a current-process target pointer matches the supplied actor [EV-0397], [EV-0291]. EV-0442 now identifies a direct producer among the 62 initially uninspected worker callers: `FUN_140657a70` writes tag 0xB, and its sole captured caller `FUN_1406bb690` routes its parameters through that worker and returns when `FUN_1406d4110` reports another active thread. Worker case 0xB re-enters the same function. With the gate clear, `FUN_1406bb690` continues through its work, which includes conditional calls to the known `FUN_1406bcaa0` receiver skill resolver [EV-0442]; that resolver's mapped HitData handler call occurs after its player skill-routing block [EV-0430], [EV-0291]. This supports H1 for a static tag-0xB continuation into the resolver family and rejects H2's no-tag-0B model. It does not establish an ordinary physical attack or a live skill award. The source of `FUN_1407ba3e0`, actual event timing, effective protection and AVSK remain unknown. Fourteen of the original 62 bodies have been reviewed, leaving 48. Claim CL-L230 -> M-0095; Q-0073/Q-0079.

## M-0096 — Clothing resistance ActorValues at the GOG CheckResistance path (Q-0074)

The exact official-five-master source screen identifies Clothing ARMO 000FC061 -> ENCH 000FC05B -> constant/self Peak Value Modifier MGEF 000B7A35, primary AV44, magnitude 10, with no captured conditions [EV-0398]. A separate Health-primary MGEF screen finds source Fire/Shock/Frost effects whose configured ResistValues are AV41/42/43 [EV-0399]. In the verified GOG AE 1.6.1179.0 build, CommonLib Actor layout and the ten-entry RTTI census identify the Actor `MagicTarget` vtable at subobject offset 0xA0; slot 0x0A resolves to `FUN_1406c45a0` [EV-0400], [EV-0401]. The function calls ActorValueOwner's GetActorValue slot through Actor+0xB8, selects AV44 or AV40, conditionally reads the incoming Effect's `baseEffect` ResistValue, and sends two values to a residual-factor helper [EV-0402]. This supports an independent magic/element resistance candidate outside the type-2 Heavy/Light hit-XP selector [EV-0222], [EV-0261].

This does not establish a direct virtual caller/use-site, exact multiplier constants, level-one item access, active Steam behavior, measured health-damage reduction, a qualifying hit, or numeric Heavy/Light AVSK. The candidate necklace has no physical DNAM armor rating; the separate physical cached armor-factor question remains unresolved [EV-0311]. No shared quest state, Quest-start call, HitData route, or serialization field links this mechanism to OBJ-1, so no causal edge is added [CL-L231], [CL-L232], [CL-L233]. Claim CL-L231/CL-L232/CL-L233 -> M-0096; Q-0074.

## M-0097 — College quarter key and fixed-item progression route (Q-0076)

The fixed Arch-Mage boots are in the owned Arch-Mage quarters cell [EV-0404]. The linked Hall of the Elements and Arcanaeum door references store level-255 XLOC locks requiring CollegeArchMageKey `000C5140`; two additional min-use refs also name that key [EV-0410], [EV-0411]. Tolfdir post-forcegreet INFO `00107E3D` requires MG02 stage 200 and its bounded attached TIF fragment calls `Game.GetPlayer().AddItem` for both ArchMageRobes and CollegeArchMageKey [EV-0412], [EV-0413]. The owner quest script exposes `TolfdirPostQuestFG`; the exact INFO variable operand and complete stage/door-property bindings are not resolved.

The exact MG01/MG02 QUST records and linked DIAL/INFO contain no direct GetLevel CTDA [EV-0407], [EV-0409]; the complete Story Manager level-node map selects no MG01/MG02 child [EV-0300], and the captured door/base records plus four attached PEX bodies contain no direct GetLevel CTDA/call [EV-0410], [EV-0412], [EV-0413]. QF_MG01 has a fragment that starts MG02, while QF_MG02 has a fragment that locks its two ArchMageDoor properties. This supports a quest-stage/key acquisition model rather than a direct player-level predicate in the inspected path. No clean level-one completion, physical entry, active-profile winner, or theft legality is established [EV-0260]. No shared call, ActorValue, HitData field, or serialized state connects this route to the incoming armor XP selector M-0009 or the separate resistance route M-0096.


## Q-0077 addendum — Savior's Hide source candidate for M-0096

Base Skyrim.esm ARMO `0002AC61` is a positive-DNAM Light Armor record (`DNAM=2600`, BOD2 type 0) with EITM `001097B7`. DA05 stage 100 binds its `Fragment_20` reward path to that item, and the fragment adds one to the player [EV-0415]. The linked ENCH includes a Resist Magic AV44 magnitude-15 MGEF and a Resist Poison AV40 magnitude-50 MGEF; both are archetype-34 Peak Value Modifier effects in the source records [EV-0416]. This extends the item side of M-0096 while keeping clean level-one acquisition open.

The fresh GOG `MagicTarget::CheckResistance` target query found no direct code xref, as expected for a virtual entry, and did not identify a callsite into the armor selector. The `physicalDamage` scan and bounded HitData caller queries likewise do not prove that a pure magic hit reaches the AV11/AV12 resolver with non-positive points [EV-0417]–[EV-0421]. No causal protection-to-armor-XP edge is added; a magic-only no-award case may be selector bypass rather than XP suppression. Claims CL-L239/CL-L240 refine the source candidate; Q-0077.


## M-0098 — MS06 helper and note route boundary (Q-0078)

The exact official-five-master SMQN child `MS06IncreaseLevelNodeSHARES` selects main QUST `MS06` at the mapped level-10 threshold [EV-0300]. The separate helper QUST `MS06Start` has source start flags enabled; its stage-5 fragment starts `MS06StartAppealForHelpScene`, whose script sets its owning helper quest to stage 10. Helper stage 10 requests `MS06Rumor.SetStage(20)`, while the helper ritual scenes advance their owning helper quest to stages 65/75 [EV-0422]. The helper Falk-note `MS06StageSetter` directly requests main `MS06.SetStage(10)`, but the stopped main QUST source fields (Start Game Enabled clear; ENAM=LEVL) fail the inspected GOG initial callback predicate [EV-0313], [EV-0314], [EV-0316]. This conditional GOG comparison does not transfer to Steam. The five-master dialogue/scene screen contains no direct `GetLevel` CTDA in the 85 INFO rows or captured SCEN conditions; no TIF directly starts the main QUST or requests its stage 10 [EV-0422], [EV-0214]. A main-target placed trigger requires stage 50 before its configured stage-60 write; `PotemaBossFightScene` has a bound stage-125 write, but natural scheduling with stopped MS06 is unresolved [EV-0422]. No clean level-one transition, active-profile winner, or vanilla bypass is established [EV-0260]. No causal edge to M-0009 or M-0096 is supported: the screen identifies no shared native call, ActorValue, HitData field, ActiveEffect or serialized dependency [EV-0422]. Claims CL-L241–CL-L243 -> M-0098; Q-0078.


## M-0099 — Tag-0x28 positive-scalar recursive property update (Q-0079)

Worker tag 0x28 forwards a float to `FUN_140e8f270`, which proceeds only for a positive value and then reaches `FUN_140e905e0` [EV-0477], [EV-0480]. The bounded helper recurses over nested object pointers at +0x118/count +0x122, selects a branch using a virtual +0x10 lookup, and multiplies an object-derived scalar by the input before a virtual +0x18 setter or `FUN_140b31ba0` [EV-0481]. This supports a recursive scalar/property-update mechanism for the captured route, with object and property types unresolved. The three indirect sites and deeper descendants remain open; the direct path contains no mapped HitData handler or ActorValue/skill edge. The decompiler's literal-zero first argument conflicts with caller-preserving RCX instruction flow and remains explicit [CL-L295], [CL-L296]. No effective-protection, AV11/AV12, armor-XP, or OBJ-1 edge is established.

## M-0100 — Tag-0x3C recursive callback and object-reference route (Q-0079)

Worker tag 0x3C forwards a retained object and three byte arguments to `FUN_140e89260` [EV-0482], [EV-0468]. Under its captured object/state gate, the handler builds a record with field +0x0C equal to 0x0D and dispatches through a global callback pointer into `FUN_140e898f0`, which walks nested pointers at +0x118/count +0x122, obtains node values through vtable +0x90, invokes callbacks, and recurses through vtable +0x18 [EV-0483], [EV-0484]. The selected pointer resolves to `FUN_140e89ee0`; when its vtable +0x98 lookup returns an object, it increments or decrements that object's +0x40 reference count according to record byte +0x10 [EV-0485]–[EV-0487]. This supports a bounded recursive callback/lifetime route, not a runtime class identity or gameplay meaning. Two dynamic node virtual targets and callback slot +0x98 remain unknown; no mapped direct HitData or ActorValue edge is established. The decompiler omits R8's callback argument at the call to `FUN_140e898f0`, so preserve the instruction/pseudocode discrepancy [CL-L302]. No armor-XP, effective-protection, or OBJ-1 causal edge is supported.

Tag-0x28 and tag-0x3C helpers share the observed nested child-array offsets +0x118/+0x122 and a parent vtable +0x18 lookup. This is a structural analogy only; separate producers and dynamic type identities remain unverified [CL-L303]. The next discriminant is a producer-backed RTTI/vtable comparison; differing dynamic types or layouts would falsify a common-node-type model.

## M-0101 — Tag-0x4C gated/deferred helper route (Q-0079)

`FUN_140657fc0` builds a tag-0x4C event with a retained object and one byte argument. Three captured producer functions test the shared `FUN_1406d4110` gate: the set-gate branch queues the event, while the clear-gate branch calls `FUN_1406940d0` directly with the same captured object and byte [EV-0488]. Dispatcher case 0x4C also sends the queued payload/byte pair to `FUN_1406940d0` [EV-0397]. This supports a deferred/gated route to one common helper, with a direct fallback in the three callers. It does not identify the helper's semantics or prove the same runtime effects occur across scheduling states. Inspect `FUN_1406940d0`'s body and descendants before assigning a state, HitData, ActorValue, or armor-XP interpretation; no OBJ-1 edge is supported.

## M-0102 — Tag-0x4C process-context value propagation (Q-0079)

`FUN_1406940d0` obtains process/global context, conditionally computes and stores a value at context offset +0x15c, and in a captured branch calls `FUN_14065c6e0` with a composed value before invoking `FUN_140e8f210` on an object/value pair [EV-0489]. `FUN_14065c6e0` is the same target already traced from tags 0x24/0x25/0x27 to event-value storage and Havok broadphase overlap/filter updates [EV-0477], [EV-0478]. This establishes a static causal edge from the tag-0x4C helper into that shared engine path; the other object/value helper and six indirect sites remain unresolved. No direct mapped HitData/ActorValue or armor-skill handler appears in the bounded body. This is not a transitive no-hit, runtime, effective-protection, AVSK, or armor-XP result.

## M-0103 — Shared two-word object/value forwarding wrapper (Q-0079)

`FUN_140e8f210` packages its two 32-bit arguments into a local eight-byte pair and forwards the object/pair to `FUN_140e90750` [EV-0490]. Eleven direct caller functions include tag-0x4C helper `FUN_1406940d0`, tag-0x0D target `FUN_140712d10`, and dispatcher `FUN_140659160`, plus eight other callers; the captured pairs vary by callsite. This is a shared object/value forwarding primitive, not a tag-0x4C-specific handler. Its target's operation semantics and relationship to tag 0x28's recursive scalar/property path are unresolved. Trace `FUN_140e90750` next; do not infer combat, ActorValue, or armor-XP effects from the generic pair alone.

## M-0104 — Recursive object-tree packed-value update route (Q-0079)

In GOG AE 1.6.1179.0, `FUN_140e90750` checks each node's associated object for a linked-list entry equal to `DAT_14328f300`, gets a record through `FUN_1402f39c0`, and conditionally changes the low 7 bits from input word 0 and the high 16 bits from input word 1. It obtains a storage pointer through `FUN_140e83cb0`, writes the packed result at +0x2c, and calls `FUN_140e83d30`; that helper reaches the previously mapped `FUN_140e8bd30` update route. The helper then obtains children through parent vtable +0x18 and recursively visits pointers at +0x118 with count +0x122 [EV-0491].

The shared selector, record lookup, child array offsets, and parent slot link this route structurally to tag-0x28 recursive scalar/property helper `FUN_140e905e0`, but the update operations differ: `FUN_140e90750` conditionally replaces packed bit ranges and writes +0x2c, whereas `FUN_140e905e0` multiplies a positive scalar and invokes a setter [EV-0480], [EV-0481], [EV-0491]. This supports a recurring object-tree traversal/update substrate, not a proven common dynamic type or identical gameplay effect. The two indirect call sites in `FUN_140e90750` remain unresolved. No direct HitData or ActorValue/armor-skill edge, effective-protection result, or armor-XP effect is established.

## M-0105 — Tag-0x4D gated deferred/immediate continuation (Q-0079)

`FUN_140658000` writes worker tag 0x4D, retains its two +0x28 objects and two +8 pointer arguments, copies two three-word blocks plus 32-bit and byte values, then calls `FUN_14065b800` [EV-0492]. Its captured producer `FUN_1407bcdf0` reaches this builder when shared gate `FUN_1406d4110` is nonzero; when clear, it directly calls `FUN_140e8fc90` with the corresponding pointer/value family. The already captured dispatcher case 0x4D also calls `FUN_140e8fc90` with payload-derived and retained arguments [EV-0490]. This supports a static deferred/immediate route to one helper, not equivalence of scheduling or runtime effects. Trace `FUN_140e8fc90` next to test whether it reaches the recursive object-tree update or any HitData/ActorValue path; no OBJ-1, protection, or armor-XP effect is inferred.

## M-0106 — Paired-object packed update and Havok constraint route (Q-0079)

`FUN_140e8fc90` checks two paired objects for the `DAT_14328f300` selector, obtains their records through `FUN_1402f39c0`, and searches one record's children for nodes matching selectors `DAT_14328f6e0` and `DAT_1432905e8`; virtual slots +0x1a0/+0x1a8 compare associated objects [EV-0493]. If a node matches and `param_9` is zero, it builds a two-word input from the matched node and calls `FUN_140e90750`, then calls `FUN_140e86bf0` and `FUN_140e950e0`. If there is no match and `param_9` is nonzero, it reads packed values, makes two +0x1a8 virtual calls, builds either a Havok ball-and-socket constraint (`param_1==0`) or fixed constraint (`param_1!=0`), then calls `FUN_140e95190` and `FUN_140e860d0` [EV-0493].

The helper has 26 direct edges, nine indirect sites and four incoming direct caller functions; the complete direct scan has no mapped HitData or ActorValue/armor-skill call [EV-0493]. This establishes a bounded paired-object update/physics-constraint mechanism, not its gameplay label or runtime consequence. The virtual targets, effective protection, combat-hit coverage, and armor-XP behavior remain unknown.

## M-0107 — TLS-marked selector-gated object-array append (Q-0079)

`FUN_140e95190` saves TLS field +0x768, sets it to 0x33, and checks `param_2` for selector entries `DAT_14328f6e0` or `DAT_14328f710` using two indirect vtable +0x10 list walks. If either selector is present, it appends `param_2` to the BSTArray at `param_1+0x28`, using the helper `FUN_140cc8350` and array size/capacity metadata +0x38/+0x30, then increments the stored object's +8 reference count; it restores the prior TLS value [EV-0494]. The helper has 11 incoming callers, including the tag-0x4D route `FUN_140e8fc90`. There, a newly built Havok constraint is passed as the candidate array item, but the selector condition, resulting owner semantics, and separate world/physics call `FUN_140e860d0` must be traced before calling this registration or physics attachment. The direct body has no mapped HitData/ActorValue/armor-skill edge; no protection or armor-XP result follows.

## M-0108 — Shared constraint attachment/queue primitive (Q-0079; cross-link to Q-0064)

In the tag-0x4D branch, `FUN_140e8fc90` constructs a Havok constraint cinfo and passes `plVar9[2]` from the `FUN_140ef2e70` result to `FUN_140e860d0` [EV-0493], [EV-0495]. The helper first queries owner vtable +0x138 and context vtable +0x140. When owner field +0xc5d8 is zero, it validates constraint/endpoint fields and calls `FUN_140b3a710`; otherwise it may clean up a full queue, calls `FUN_140a89da0`, stores the pointer in the owner's indexed area and increments count +0xc5e4 [EV-0495]. The immediate route through `FUN_140b3a710` is the exact shared helper reached by the ProcessTrapHit-created hkpConstraintInstance path; that separate path maps endpoint +0x130, entity constraint records, and the instance back-pointer [EV-0360], [EV-0364].

This supports static convergence on one polymorphic constraint attachment/queue primitive, not identical dynamic types or owner semantics across callers. The two indirect owner/context slots, deeper attachment callbacks, ordinary-hit coverage, effective protection, and armor-XP effects remain unresolved; no combat interpretation follows solely from the shared helper [EV-0495].

## M-0109 — Gated tag-0x4A object/value update route (Q-0079)

`FUN_1406580f0` writes worker tag 0x4A, increments its object's +0x28 reference count, stores the byte argument, and calls `FUN_14065b800`. Its two captured producers, `FUN_1407bc650` and `FUN_1407bc6f0`, use the shared `FUN_1406d4110` gate: the set branch queues tag 0x4A with byte 1 or 0, while the clear branch calls `FUN_140664b20`, obtains a float through `FUN_1402ef0c0`, calls `FUN_140ea0760`, and conditionally raises an object field at +0x20 when the new value is greater [EV-0496]. The matched dispatcher case 0x4A in the EV-0455 raw capture repeats this helper/update sequence using the payload object and byte.

This supports static deferred/immediate convergence on an object/value update under the shared gate; it does not identify the value's gameplay meaning. The direct builder/producer/dispatcher bodies contain no mapped HitData or ActorValue/armor-skill call, but `FUN_140ea0760` and related descendants remain unresolved. No ordinary-hit, effective-protection, or armor-XP conclusion follows [EV-0496], [EV-0455].

## M-0110 — Tag-0x4A byte-gated selector-list transition (Q-0079)

`FUN_140ea0760` proceeds only when receiver byte +0x321 is set and input byte differs from receiver byte +0x320; it stores the new byte, obtains a refcounted object through `FUN_140ea6200`, and requires a returned object's +0x10 target to have type field +0x18 equal to 9. It obtains a list through receiver virtual +0x80 and scans the +0x38 count for entries whose record +0x20 matches `DAT_14328f338`. The byte selects `FUN_140b250b0` (set the indexed bit) or `FUN_140b25080` (clear it; the helper also writes three per-entry fields to sentinel/zero values). The routine then dispatches through the manager returned by virtual +0x140 to `FUN_140b39940` or `FUN_140b3ae10` based on record fields [EV-0497].

This supports a bounded static selector-list and manager-state transition downstream of tag 0x4A. The selector, concrete types, five virtual targets and deeper descendants remain unresolved. No mapped direct HitData, ActorValue or armor-skill target appears in the captured direct callees; no transitive/runtime negative, protection result, or armor-XP result follows [EV-0496], [EV-0497], [EV-0260].

## M-0111 — Tag-0x60 worker route to `FUN_140e88fd0` (Q-0079)

`FUN_140658130` writes tag 0x60, retains its nonnull payload by incrementing the object's +8 reference count, and calls the shared worker. Its query finds no incoming direct code-call edges and one source-less DATA reference around adjacent worker-related code addresses, so the producing/scheduling route is unidentified. The build-matched dispatcher case 0x60 calls `FUN_140e88fd0(payload,1)` when the stored pointer is nonnull [EV-0498], [EV-0455].

This establishes only the builder/dispatcher target mapping. `FUN_140e88fd0`, its dynamic payload type, and any HitData/ActorValue/armor-skill relation remain unresolved; no ordinary-hit, effective-protection, or armor-XP claim follows [EV-0498], [EV-0260].

## M-0112 — Tag-0x60 recursive hierarchy callback (Q-0079)

`FUN_140e88fd0` rejects a null receiver. If its third argument is zero, it calls `FUN_140e0f510`, which searches for key `DAT_14327f4f8`, checks returned-object vtable identity `DAT_14327f4e8`, and requires bit 2 in the +0x18 flags; failure returns false. When global callback pointer `PTR_FUN_14202d630` is nonnull, it builds a `{0, input byte, 4}` record and calls `FUN_140e898f0` on the receiver [EV-0499].

`FUN_140e898f0` obtains each node's value through virtual +0x90, calls the supplied callback when that value is nonnull, and recursively walks child pointers +0x118/count +0x122 through virtual +0x18 when the record byte is nonzero. Tag-0x60 dispatcher case 0x60 enters `FUN_140e88fd0` with arg2=1 and arg3=1, bypassing its optional selector/type/flag guard and enabling recursion [EV-0498], [EV-0499], [EV-0500], [EV-0455]. The address-context query for `PTR_FUN_14202d630` reports one READ xref from `FUN_140e88fd0` at VA 0x140e88ffa, but does not expose the pointer value or initialization/writer path [EV-0501]. The one-entry pointer query resolves `PTR_FUN_14202d630` to `FUN_140e89be0` [EV-0502]. That callback reads the object at `param_1+0x10`, clears its +0x40 pointer, atomically decrements the pointed object +0x8 count, and invokes vtable +0x8 if the prior count was 1. It then re-reads +0x40 and conditionally tail-jumps through vtable +0x128 when the pointed object +0x10 differs from the original object [EV-0503]. This is a bounded reference-release/cleanup pattern; the dynamic types and virtual targets remain unresolved, so no HitData, ActorValue, protection, or armor-skill effect follows.

## M-0111 — Tag-0x60 worker route to `FUN_140e88fd0` (Q-0079)

`FUN_140658130` writes tag 0x60, retains its nonnull payload by incrementing the object's +8 reference count, and calls the shared worker. Its query finds no incoming direct code-call edges and one source-less DATA reference around adjacent worker-related code addresses, so the producing/scheduling route is unidentified. The build-matched dispatcher case 0x60 calls `FUN_140e88fd0(payload,1)` when the stored pointer is nonnull [EV-0498], [EV-0455].

This establishes only the builder/dispatcher target mapping. `FUN_140e88fd0`, its dynamic payload type, and any HitData/ActorValue/armor-skill relation remain unresolved; no ordinary-hit, effective-protection, or armor-XP claim follows [EV-0498], [EV-0260].

## M-0113 — Actor +0x380 TLS/nested context selector shared across hit and tag-0x17 routes (Q-0079; cross-link Q-0035/Q-0064)

Primary GOG `VTABLE::Actor` slot +0x380 maps to `FUN_1402e55a0`; the same helper is Actor slot +0x70 in the captured HitData receiver `FUN_1406b9df0` [EV-0512], [EV-0295], [EV-0296]. In the tag-0x17 base fallback, Actor slot +0x378 forwards through runtime slot +0x380 and `FUN_14066dfa0` passes the returned pointer to `FUN_1406a19b0`, which performs keyed object/node lookup and child-state operations [EV-0511], [EV-0509], [EV-0510]. The helper selects TLS +0x5f0 when the receiver matches TLS +0x5f8; otherwise it returns a nested +0x68/+0x68 field or null. EV-0636 adds the tag-0x54 Actor update and tag-0x32 slot-0x65 cleanup as additional consumers; this route reads nested state and can enter the recursive object-tree helper, but it does not establish the same returned pointer as the HitData route.

The exact helper identity is a supported shared code primitive. The two consumers do not establish the same runtime returned object or a shared hit/skill mechanism: `FUN_1406b9df0` still has unresolved indirect sites, while the bounded tag-0x17 helper uses object/node state. A source-backed vtable/class match or same-instance pointer observation would support shared context identity; distinct producer-backed runtime types or separate continuations would falsify it. No edge to armor protection, AV11/AV12, armor XP, or OBJ-1 quest gates is established. Claim CL-L328 -> M-0113.

## M-0114 — Tag-0x19 process/object-hierarchy update candidate (Q-0079)

The exact worker builder FUN_1406582d0 writes tag 0x19; producer FUN_140687370 reaches it after process/type predicates, an unresolved virtual +0x2b8 call and a state helper, while dispatcher case 0x19 calls FUN_140687430(payload,0) [EV-0513], [EV-0455]. The handler has a complete direct-call census: 49 sites to 38 unique functions, nine unresolved virtual calls and two direct callers. Its bounded body selects a context, obtains a process-associated object, uses the fixed DismemberedLimb1_Head1 string, creates/updates hierarchy nodes and child state, and conditionally calls the previously mapped tag-0x55 helper FUN_1406e5da0. The second caller FUN_1406883b0 traverses body-part records including a Torso string and invokes the handler with flag 1 [EV-0514], [EV-0464]–[EV-0466].

These observations support a bounded object/hierarchy update interpretation for the captured direct paths. They do not establish a full runtime event meaning or exclude an indirect hit/skill continuation: nine virtual calls and descendants are unresolved, and the producer virtual +0x2b8 remains untraced. No causal edge to effective armor protection, AV11/AV12, armor skill XP, or OBJ-1 level-gate state is established. Continue with the producer census and retain Q79-H48 as open against bounded direct-body model Q79-H49/H50.

## M-0115 — Tag-0x19 producer-side indexed Actor callback (Q-0079)

`FUN_140687370` is the only captured producer of tag 0x19 and has one direct caller, `FUN_1407baca0` [EV-0513], [EV-0515]. On the path that reaches the builder, it obtains a scalar from `FUN_1403a8f30(param_1[8])`, checks indexed storage through `FUN_1403e0d20`, loads an entry at `param_1[0x3f]+0x270+index*8`, and passes that pointer plus flags to receiver virtual slot +0x2b8. It then calls `FUN_1402e8f30`, which writes a state record and dispatches receiver slot +0x50 with value 0x20000, before tail-jumping to the tag-0x19 builder `FUN_1406582d0` [EV-0515].

The producer establishes a structural call/dataflow link between an indexed callback and the worker event. It does not establish the callback's semantic role or dynamic implementation. The caller's branch on AL after `FUN_1402e9000` conflicts with the separate callee decompilation's `void` rendering; retain this as an analysis discrepancy until instruction/dataflow evidence resolves it. Resolve primary Actor slot +0x2b8 in the exact GOG project, then trace only the mapped target with subclass uncertainty preserved. No armor protection, AV11/AV12, armor XP, ordinary-hit, or OBJ-1 edge is established.

## M-0116 — Actor +0x2b8 base implementation in item/equipment workflow (Q-0079; cross-domain OBJ-2 candidate)

Primary GOG Actor slot +0x2b8 maps to `FUN_1406a2cd0`; the same target is called four times from `FUN_1406a1bf0` [EV-0516]. The bounded caller contains item/use branches and equip/quest-item messages. The target obtains an actor list through virtual +0x3f0, iterates slot-like entries, tests BGSBipedObjectForm records, performs item/container operations and calls `FUN_14022b7a0`. This supports reuse in an item/equipment operation for the base Actor implementation.

The tag-0x19 producer passes an indexed pointer into this same base slot before a state helper and worker submission [EV-0515], [EV-0513]. The producer-supplied record's exact identity is not yet mapped. This weakens the body-part-specific callback model for the base target but does not establish whether its direct descendants alter effective armor/protection or call AV11/AV12 award paths; complete direct edges, unresolved virtuals, runtime overrides, and Steam mapping remain open. Use this as a new OBJ-2 exploration lead, not as an armor-XP glitch claim. No causal edge to M-0009 or OBJ-1 is established.

## M-0117 — Bounded direct route of base Actor +0x2b8 item operation (Q-0079)

Complete call-edge coverage for `FUN_1406a2cd0` finds 22 direct sites to 19 functions, four unresolved virtual calls and four incoming sites all from item/equipment caller `FUN_1406a1bf0` [EV-0517]. Its body obtains an actor list through slot +0x3f0, iterates item/slot records, checks `BGSBipedObjectForm`, and uses item/container helpers including `FUN_1406cc240` and `FUN_14022b7a0`. The direct list contains no mapped HitData, ActorValue or armor-skill award function.

This is a bounded static direct-body result only. Four virtual targets, deeper descendants, the indexed payload passed by the tag-0x19 producer, effective protection, armor XP, and Steam mapping remain unresolved. Next trace `FUN_14022b7a0`, then select producer-backed virtuals. No causal edge to M-0009/M-0096 or OBJ-1 is established.

## M-0118 — Item/list helper branches into actor-state and shared-context routes (Q-0079)

`FUN_14022b7a0` is called from `FUN_1406a2cd0` and `FUN_1402e1b20`; its complete direct census has 115 call sites to 51 functions, three virtual sites and no direct mapped HitData or ActorValue/armor-skill award target [EV-0518]. The bounded body has item/list branches that call `FUN_1406b98f0`, select context through `FUN_1402e55a0`, and then call `FUN_140661f60`; another branch checks shared gate `FUN_1406d4110`, selecting direct `FUN_1402e90d0` or helper `FUN_1406581b0` [EV-0518]. The selector is also used by the tag-0x17 base path and the HitData receiver [EV-0512], [EV-0295], [EV-0296].

This supports a shared context-selector primitive and multiple item/actor-state branches. It does not establish that calls return the same context object, that `FUN_1406b98f0` is a hit/skill route, or what `FUN_1406581b0` schedules. Trace `FUN_1406b98f0` first against mapped HitData/protection/AV11/AV12 functions, then inspect the context consumer and gated helper as justified. No armor XP or OBJ-1 edge is established.

## M-0119 — FUN_1406b98f0 nested-record selector (Q-0079)

Complete coverage finds 69 incoming callsites across 51 functions, one direct call and no indirect call sites for `FUN_1406b98f0` [EV-0519]. The body reads `param_1+0xf8`, delegates selection to `FUN_14070fd50`, and returns the selected entry's first pointer-sized field. The bounded selector reads a nested +8 pointer, chooses +0x220 or +0x260 according to a second argument, then requires a nonnull first entry and marker byte +0x1a == 0x29. The item/list caller `FUN_14022b7a0` decompiles as passing selector 0 and uses the result in a TESActionData-related branch [EV-0518], [EV-0519].

The target's one-argument decompiler signature conflicts with the downstream selector's use of a second argument; preserve this unresolved calling-convention/register question. The 51 incoming functions are heterogeneous and the helper body contains no direct HitData/ActorValue/armor-skill call. This is not a transitive negative. Next inspect `FUN_140661f60`, which consumes the shared context selected by `FUN_1402e55a0` in the same item/list path.

## M-0120 — Shared hierarchy-node selection and component pointer update (Q-0079; cross-link OBJ-2)

`FUN_140661f60` is directly called from item/list helper `FUN_14022b7a0` and tag-0x55 process-update target `FUN_1406e5da0`, among 11 caller functions [EV-0520], [EV-0518], [EV-0464]–[EV-0466]. Its bounded body selects a node using context data from `FUN_140e1a040` or a child walk at +0x118/+0x122, skips names beginning `BIP`, and passes the selected object to `FUN_1407158f0`. That helper updates nested field +0x178 with refcount operations. The child selection helper `FUN_1414ae8a0` filters through a dynamic identity check against `DAT_14332c3a0`.

This supports a shared hierarchy/object-state operation on two producer routes. It does not establish that the routes use the same runtime object or connect to HitData, effective protection, AV11/AV12, armor skill, or armor XP. The dynamic node selector and two virtual +0x18 targets remain open. Map `FUN_1414ae8a0` and its identity comparison next; preserve the exact GOG build and do not infer a Steam result.

## M-0121 — Recursive hierarchy selection by dynamic identity comparison (Q-0079)

`FUN_1414ae8a0` walks child records through virtual +0x18/+0x38 accessors, reads a nested object at +0x128, and returns a candidate when its virtual +0x10 result equals `DAT_14332c3a0` [EV-0521]. The target has one direct fallback call to `FUN_1414ae980`, four unresolved virtual call sites, and two callsites from `FUN_140661f60`. The bounded fallback decompilation recursively walks children and repeats the identity comparison. `FUN_140661f60` passes the selected result to `FUN_1407158f0`, which updates nested field +0x178 [EV-0520].

This supports recursive identity-filtered hierarchy selection as a structural mechanism. The global value/type, virtual method contract, selected object type and +0x178 consumers are unknown. No edge to HitData, ActorValue, effective protection, armor skill/XP, or OBJ-1 quest gating is established. Resolve the global's data/code references and inspect producer-backed +0x178 readers before drawing a gameplay conclusion; preserve the uninspected fallback edge descendants and GOG/Steam boundary.

EV-0523 qualifies the candidate `DAT_14332c3a0` WRITE xref: the source address has no recovered function boundary and its bounded instructions perform two register-indirect stores through RCX, with 410 incoming xrefs [EV-0523]. The prior address query labels this source as WRITE/DATA against the global [EV-0522], but the visible operands do not name the global and no caller dataflow is mapped. Preserve the xref-classification discrepancy; add no global-initialization mechanism or gameplay edge.

## M-0122 — Actor-update consumer of nested +0x178 component (Q-0079)

`FUN_140715940` is called from two actor-update routines, `FUN_140773750` and `FUN_140734890`, and has 13 direct callees with no unresolved indirect sites in its own body [EV-0525]. Under state/flag conditions it reads a nested qword at `(*(param_1+8))+0x178`; in one branch it passes a pointer obtained at selected-object +0x70 to `FUN_1414fdb10`, combines the returned float with other fields, then updates through `FUN_1406eeb00` and `FUN_1406e68a0` and clears a byte at +0x328. In another branch it calls the shared selector `FUN_1402e55a0` and `FUN_140661f60` [EV-0525], [EV-0520].

This is a direct actor-update consumer of a +0x178 component and a numeric calculation, but no dataflow proof equates the reader's receiver/pointer with the exact object written by `FUN_1407158f0`. The calculation helper and final update routines remain semantically unresolved; no HitData, ActorValue, protection, armor-skill or XP conclusion follows. Trace `FUN_1414fdb10` and its producer-backed descendants next.

## M-0123 — Distance-attenuated float aggregation from nested context entries (Q-0079)

`FUN_140715940` passes a nested +0x70 pointer from its +0x178 read into `FUN_1414fdb10` [EV-0525]. The latter iterates a pointer/count array and sums `FUN_14150aea0` results; that callee reads per-entry position coordinates and float fields, computes a square-root distance, applies a capped distance factor, and returns a weighted float [EV-0526]. The path then returns to `FUN_140715940`, which combines the value with other inputs and calls `FUN_1406eeb00`/`FUN_1406e68a0` [EV-0525].

This supports an object/context numeric calculation in the captured actor-update route. It does not identify the array entry/gameplay type, equate the read pointer with the setter's selected pointer, or show the final update as armor, HitData, ActorValue, or skill processing. Trace `FUN_1406eeb00` next; keep descendant/runtime uncertainty open.

## M-0124 — Aggregate stored in actor-update object field +0x3a8 (Q-0079)

`FUN_140715940` sends its calculated float to `FUN_1406eeb00`; that setter performs one conditional store at `(*(param_1+0x10))+0x3a8`, with no outgoing calls and one captured caller [EV-0527], [EV-0525]. This completes the immediate numeric aggregation-to-field-write edge for the bounded route.

The field type/meaning and its readers are not identified. Do not label it an ActorValue, armor property, or hit result without a producer-backed reader. The paired `FUN_1406e68a0` call remains the next discriminator. No armor-XP or OBJ-1 edge is supported.

## M-0125 — Paired nested actor-update field stores at +0x3a8/+0x3b0 (Q-0079)

`FUN_140715940` computes the context aggregate and calls `FUN_1406eeb00(param_1,fVar12)`, which stores the float at `(*(param_1+0x10))+0x3a8`; it immediately calls `FUN_1406e68a0(param_1,DAT_14319c47c)`, which stores its 32-bit argument at the same nested-base expression +0x3b0 [EV-0527], [EV-0528], [EV-0525]. Both setters have no outgoing calls, and `FUN_1406e68a0` has only this captured caller.

This supports a paired state update in the bounded actor-update route. The field and global types/meanings and all readers are unknown. No causal edge to mapped HitData, effective armor protection, ActorValue/AV11/AV12, armor-skill XP, the OBJ-1 quest gates, or M-0096 resistance is established; those are unsupported analogies without a shared path. Next trace producer-backed readers of the pair, keeping offset collisions and GOG/Steam boundaries explicit. Claim CL-L344.

EV-0529 adds a complete +0x3a8 scan: 54 accesses across 38 functions, with 15 writer-candidate and two computed-writer functions. The closest direct reader candidate is `FUN_1406eeae0`, which loads a dword at +0x3a8 immediately before setter `FUN_1406eeb00` in address order [EV-0529]. This is only an offset/proximity candidate; the receiver is not shown to match the nested object in the +0x178 actor-update path. Query `FUN_1406eeae0` callers/callees to discriminate same-field consumption from collision; preserve H59/H60 and H57/H58.

## M-0126 — Nested +0x3a8 getter in detection/light consumers (Q-0079)

`FUN_1406eeae0` returns the dword at `(*(param_1+0x10))+0x3a8` or zero and has four direct callers [EV-0530]. `FUN_1406807c0` and `FUN_140692aa0` pass an outer +0xf8 object pointer; the former clamps the result and compares it with a threshold. `FUN_14032ada0` uses the value in a `GetDetected >> %i and light %i` debug message. Separately, actor-update caller `FUN_140734890` passes its +0xf8 field expression to `FUN_140715940`, whose route writes nested +0x3a8 [EV-0525], [EV-0527]. This supports a shared structural +0xf8 state-slot route and a light/detection use of the getter.

The exact class/instance identity between these getters and the setter is not proven; the `FUN_1406936f0` decompiler signature omits a visible argument. Other scan hits at +0x3a8 remain collisions. The observed use is detection/light-related, with no mapped edge to armor protection, HitData, ActorValue/AV11/AV12, armor XP, or OBJ-1 quest gates. Resolve the +0xf8 source type and preserve the GOG/Steam boundary. Claim CL-L346.

## M-0127 — Shared +0xf8 source for actor/process and context-state updates (Q-0079)

`FUN_140734890` calls both `FUN_1406e5da0(param_1[0x1f],param_1)` and `FUN_140715940(param_1[0x1f],param_1,0)` [EV-0531]. The qword at `param_1[0x1f]` is byte offset +0xf8, matching the outer slot expression passed to the +0x3a8 getter `FUN_1406eeae0` by its detection/light callers [EV-0530]. `FUN_140715940` performs the paired +0x3a8/+0x3b0 writes [EV-0525], [EV-0527], [EV-0528], while `FUN_1406e5da0` is the separate Actor/process update route previously traced from the worker [EV-0464]–[EV-0466].

This supports a shared structural source slot across actor/process and detection/light state paths. `FUN_140734890` has no analyzed direct incoming caller, 33 unresolved virtual calls, and its primary Actor vtable slot remains to be mapped. Do not infer exact class/instance identity or a HitData/armor effect. Next resolve primary Actor slot +0x718 and compare the table target. Claim CL-L347.

EV-0532 rejects the proposed primary Actor base-slot mapping: slot index 0xE3 (+0x718) resolves to FUN_1406b9000 under RTTI .?AVActor@@, subobject offset 0; it is not FUN_140734890 [EV-0532], [EV-0531], [EV-0400]. FUN_140734890 remains a no-direct-caller function with unresolved virtual ownership. The +0xf8 dataflow stays structural only; next inspect code/data references to FUN_140734890 for another table or registration source.

## M-0128 — Thread-gated paired tag-0x1A/0x1B registry updates (Q-0079)

Producer `FUN_140640910` checks global/object/type state, a payload flag, and `FUN_1406d4110`; under the thread gate it queues tag 0x1A or 0x1B through builders `FUN_140658310`/`FUN_140658350`, which retain the payload and call worker `FUN_14065b800`. When the gate is clear, the producer calls corresponding handlers `FUN_1404c2480`/`FUN_1404c2650` immediately [EV-0544], [EV-0547]. Dispatcher cases 0x1A/0x1B route to those same handlers [EV-0545].

Both handlers use TLS +0x768 marker 0x4F, lock `DAT_1431463f0`, inspect payload ID +0x14 and a nested byte/bit gate, then conditionally move payload pointers and IDs among hash buckets and arrays. Tag 0x1A can remove a payload pointer from manager +0xe8 storage and append its ID to integer array +0x100; tag 0x1B can remove the ID from +0x100 and append the pointer to +0xe8. Their gated helpers update secondary pointer storage and a reference-counted child-record list [EV-0546], [EV-0548]. This supports a paired worker/immediate registry update mechanism only; concrete manager/type/event semantics remain unknown, and nested `FUN_1404c7d60` plus one virtual release remain unresolved. No direct HitData, ActorValue, effective armor protection, AV11/AV12, armor-XP, or OBJ-1 edge follows [EV-0544]–[EV-0548], [EV-0260].

## M-0129 — Tag-0x1c serialized Actor/process update continuation (Q-0079)

FUN_140729140 can submit its object through worker builder FUN_140658390, which stores tag 0x1c and retains the pointer. Dispatcher case 0x1c calls FUN_140729140(payload,0) [EV-0549], [EV-0545]. The literal-zero branch skips the helper's three indirect virtual sites, then tests the shared FUN_1406d4110 gate; on the clear path it reaches Actor/process update calls including FUN_1406e5da0 [EV-0550]. This is a bounded static deferred-continuation route. The helper has eight other direct callers; gate scheduling and FUN_1406e5da0 descendants remain unresolved. The shared worker gate also appears in hit continuation, registry, actor update and physics routes [EV-0432], [EV-0464]–[EV-0470], [EV-0544]–[EV-0548], supporting a generic scheduling/state primitive interpretation rather than hit-specific evidence. No edge to ordinary hit coverage, effective armor protection, AV11/AV12, armor XP, or OBJ-1 quest gates is supported. Claim CL-L366.

## M-0130 — Tag-0x1d object-state and paired registry route (Q-0079)

FUN_1401d4620 accepts nested object type bytes 0x18, 0x1c, or 0x1d. Under the shared thread-state/TLS-owner condition it queues tag 0x1d with an object pointer and two byte arguments; dispatcher case 0x1d returns them to the same helper [EV-0551], [EV-0545]. The direct path performs object-state/property operations including strings Open or Close, and under separate global/type/helper gates calls FUN_1404c2480 or FUN_1404c2650 [EV-0552]. These are the guarded registry handlers mapped for tags 0x1a/0x1b [EV-0546], [EV-0548].

This supports a bounded object-state and shared-registry mechanism, not a combat interpretation. FUN_1401d4620 has 3 indirect sites; FUN_1401d4ed0 has additional virtual calls, and runtime object identity/scheduling remain unknown. No direct HitData, effective armor, ActorValue/AV11/AV12, armor-XP, or OBJ-1 edge is established. Claims CL-L367/CL-L368.

## M-0131 — Tag-0x21 generation-handle Actor continuation (Q-0079)

Primary VTABLE::Actor slot 0xD9 (+0x6c8) targets FUN_14067e960 [EV-0557]. When FUN_1406d4110 reports the thread gate set, this Actor method obtains or reuses a generation-managed handle through FUN_140178cf0, stores the key and scalar in tag-0x21 builder FUN_140658480, and submits it to FUN_14065b800 [EV-0553], [EV-0554]. Dispatcher case 0x21 passes the key through FUN_14018a7e0, which checks generation state, recovers the object base from the retained +0x20 pointer, and calls the object's virtual +0x6c8 slot with the scalar [EV-0545], [EV-0555]. On the primary Actor base table this re-enters FUN_14067e960, the same method that queued the continuation [EV-0557].

When the gate is clear, FUN_14067e960 follows Actor +0xf8 through the +8/+0x250 nested accessor and calls FUN_140ea05c0; an independent Actor caller reaches the same nested object and wrapper [EV-0556]. The wrapper tail-dispatches via receiver +0x190/vtable slot +0x8. This supports a static deferred Actor/process continuation with a generation-checked handle, not an armor-XP bypass. The dynamic nested target, Actor overrides, runtime gate state, scalar meaning, and any ActorValue/HitData/AV11/AV12 descendant remain unresolved. The worker gate's use across hit, object-state, actor-update, physics, and this Actor continuation supports generic scheduling semantics; no OBJ-1 edge is established. Claims CL-L369–CL-L372.

## M-0132 — Tag-0x2c/0x2d spatial water-effect pair (Q-0079)

Producer FUN_14051d020 computes a scalar and three-coordinate payload after object, position, and threshold checks. When FUN_1406d4110 is clear it calls FUN_14051cdd0 and FUN_140525820 directly; when the gate is set it queues tags 0x2c and 0x2d through worker builders [EV-0559]. Dispatcher cases route those tags to the same two functions [EV-0545]. FUN_14051cdd0 selects CWaterSmall/Medium/Large and uses Effects_waterSplash.NIF; it has one unresolved virtual +0xd8 site. FUN_140525820 performs distance-gated writes into two global coordinate arrays [EV-0560], [EV-0561]. Their consumers are unknown; describing them as ripple-like is inference from the shared water-effect context.

This bounded route is spatial water/effect work, not an armor-XP candidate in the captured direct path. No HitData, ActorValue, effective protection, AV11/AV12, armor-skill, or OBJ-1 edge is established. The shared worker gate also schedules this route alongside Actor, object-state, registry, physics, and combat continuations; gate presence alone is not combat evidence. Claims CL-L373–CL-L375.

## M-0133 — Additional tag-0x2d source through masked record code (Q-0079)

The exact tag-0x2d worker builder FUN_140658550 has three direct producers: water/effect functions FUN_14051cdd0 and FUN_14051d020, plus FUN_1407ed990 [EV-0562]. In FUN_1407ed990's state-bit-clear branch, `(param_5+0x2c)&0x7f` is copied into a record field; code 0x0b selects the same direct FUN_140525820 target or queued FUN_140658550 builder according to the shared FUN_1406d4110 gate [EV-0563], [EV-0564]. FUN_1407e25b0 has one analyzed direct caller, FUN_1407cb9d0; that wrapper's complete direct-edge set has no call to the mapped HitData/tag-0x0b/ProcessTrapHit functions, while three indirect sites remain unresolved [EV-0565], [EV-0566].

This widens the source set of the bounded spatial coordinate path beyond the two captured water/effect producers. The code's semantic type, water relation, runtime owner, four indirect sites in FUN_1407ed990, and buffer consumers are unresolved. No causal edge to HitData, ActorValue, effective protection, AV11/AV12, armor skill/XP, or OBJ-1 is supported. Claims CL-L376–CL-L378.

## M-0134 — Tag-0x2e Actor process continuation beside a shared Health update (Q-0079)

FUN_1406585a0 builds tag 0x2e with an Actor pointer and two bytes; its captured caller FUN_14068b3a0 queues this record when the shared thread gate is set, and dispatcher case 0x2e returns the fields to FUN_14068b3a0 [EV-0567], [EV-0570], [EV-0545]. On the gate-clear path, the handler checks the primary Actor slot +0x4c8 predicate, reads process field `*( *(process+0x10) + 0x328 )`, compares it with Actor+0x260, and conditionally writes a value based on Actor+0x260. The paired process helpers are exact no-call getter/setter bodies with one observed caller [EV-0568], [EV-0569]. Player-only branches can resolve a TESImageSpaceModifier and call visual/sound helpers. One captured parent caller contains FSTLandHardLight/Heavy selection; another contains an NPCHumanDrowning string branch [EV-0570].

A separate shared helper, FUN_140668f50, can pass ActorValue code 0x18 through FUN_1406b49d0; prior mapping identifies that code as Health. The helper is also called by the mapped HitData handlers FUN_1406b9df0/FUN_1406bcaa0 and by landing/Actor-update paths [EV-0571], [EV-0294], [CL-L128]. Some parent paths call this Health helper and FUN_14068b3a0 in the same routine, but the tag-0x2e body itself has no direct HitData, AV11/AV12, protection, armor-skill, or XP target. Do not equate the shared Health helper or thread gate with an armor-XP route. The dynamic +0x4c8 override, FUN_1408044e0 descendants, other producer meaning, Steam behavior, and exact field identity remain open. Claims CL-L379–CL-L382.

## M-0134 addendum — shared effect helper parameter distinction (EV-0572)

FUN_14068b3a0 selects FUN_1408044e0 with mode 3/code 0x1d, but passes zero for both source-data and final-pointer arguments and flag 0. The mapped HitData handler FUN_1406b9df0 calls the same helper with code 0x1d plus a nonnull source-data pointer, flag 1, and a nonnull final pointer at one captured site; it also calls code 0x23 separately [EV-0572]. FUN_1408044e0 has 22 direct calls and three unresolved dynamic sites. This is a shared helper with different argument paths, not proof that the tag-0x2e event carries HitData or invokes armor skill. Keep H67 proposed only for its broader upstream source context; no direct tag-0x2e-to-AV11/AV12/UseSkill edge is added. Claim CL-L383.

## M-0135 — tag-0x34 deferred Actor/process vector update (EV-0573/0574)

In GOG AE 1.6.1179.0, `FUN_140658660` builds tag `0x34` with an Actor pointer and submits it through the shared worker dispatcher. Its only captured direct producer, `FUN_1406c1d40`, uses `FUN_1406d4110`: the clear-gate branch updates an Actor-associated process vector directly; the set-gate branch queues the Actor pointer. Generic worker fallback `FUN_140659160` case `0x34` obtains the associated process-selected nested object using `FUN_140664b20`, passes Actor coordinates to virtual slot `+0x18`, passes a constant vector to slot `+0x38`, and clears object state [EV-0573], [EV-0574], [EV-0556]. This supports a deferred Actor/process vector/state continuation for the captured route. The two virtual targets, broader producer ancestry, and Steam/runtime behavior remain unresolved. No direct HitData, AV11/AV12, `UseSkill`, effective-protection, or quest-gate edge is established; no causal graph edge to the armor-XP or level-one objectives is added. Claims CL-L384–CL-L385.

## M-0136 — tag-0x35 process-associated object update (EV-0575/0576)

In GOG AE 1.6.1179.0, `FUN_1406586a0` creates a reference-managed tag-`0x35` payload containing an Actor-associated object and an optional second pointer. Its two captured producers, `FUN_1407bc060` and `FUN_1407bc1f0`, use `FUN_1406d4110` to choose queued tag delivery or direct execution of `FUN_140ea04c0` against the object selected by `FUN_140664b20` [EV-0575], [EV-0556]. Dispatcher case `0x35` returns the optional pointer to that helper and releases retained references [EV-0576]. The helper compares a receiver's current object through virtual slot `+0x78`, conditionally invokes nested-object slots `+0x150`/`+0x148` for differing old/new objects, and tail-dispatches receiver slot `+0x70`; targets and concrete object types are unresolved. Another dispatcher case and other callers use the same helper in different contexts, so no common combat semantics follow. No direct HitData, ActorValue, `UseSkill`, protection, or quest-gate edge is established. Keep Q79-H71 supported only as a bounded object-update model and H72 proposed for the unresolved dynamic path; add no causal graph edge to M-0017 or OBJ-1. Claims CL-L386–CL-L387.

## M-0137 — tag-0x2a Papyrus Actor.StartCombat continuation (EV-0577/0578/0579)

GOG AE 1.6.1179.0 registers Papyrus `Actor.StartCombat` to `FUN_1409ec930`. The wrapper checks two existing Actor arguments and process/state predicates, then queues tag `0x2a` through `FUN_1406586f0`; fallback case `0x2a` resolves the Actor handles and calls `FUN_1406e4ba0`, which enters `FUN_14071e250` [EV-0577], [EV-0578]. A player-target branch compares `DAT_141ffda78` with `FUN_140766520(player)`, but neither the global threshold nor its purpose is identified [EV-0578]. The accessor reads Actor+`0x9d8` component offset `+0x18`; that field is used as a loop bound over `0xa8`-byte records and is passed with record-size `0xa8` to an array helper [EV-0579]. This falsifies the direct `Actor.Level` interpretation of this accessor, while exact container semantics and threshold meaning remain unresolved. This existing-Actor combat continuation does not establish a quest/encounter start or level-one bypass. No causal edge to OBJ-1 or armor mitigation/skill progression is supported. Claims CL-L388–CL-L390.

## M-0138 — tag-0x5d object-membership update (EV-0580/0581)

In GOG AE 1.6.1179.0, `FUN_140658810` constructs tag `0x5d` with a converted 32-bit value and an 8-byte payload; its sole observed producer is `FUN_1409e90c0` [EV-0580]. Worker fallback case `0x5d` resolves the handle and calls `FUN_1406c36e0(resolved_object, payload)` [EV-0581]. The helper locates and removes the supplied object from a pointer-backed collection, updates related list/fixed-slot members, invokes state helpers, and releases/compacts the collection. It has three indirect call sites and four other direct callers; concrete types, payload meaning, and dynamic effects remain unresolved. The bounded route supports a generic object-membership/state update and has no direct mapped HitData, AV11/AV12, UseSkill, effective-protection, or quest-start edge. No causal edge to OBJ-1 or OBJ-2 is added. Claim CL-L392.

### Native-name refinement: Actor.RemoveSpell (EV-0582)

The Actor native registrar binds `FUN_1409e90c0` to Papyrus `Actor.RemoveSpell`; the wrapper converts one object to a handle/default value and queues tag `0x5d` with its second argument [EV-0582], [EV-0580]. The matched worker case resolves the object and reaches the bounded collection-membership update helper [EV-0581]. Keep the exact native name as registration evidence; do not infer dynamic callback semantics, spell-effect lifetime, armor XP, or Steam behavior from the binding alone.

## M-0139 — tag-0x5e Actor.DispelSpell dispatch (EV-0583)

The GOG Actor native registrar binds `FUN_1409e9120` as `Actor.DispelSpell` with native type `NativeFunction1<class_Actor,bool,class_SpellItem*>`. The wrapper serializes its Actor handle and forwards the SpellItem argument under worker tag `0x5e`; the matched fallback case resolves that Actor and calls `FUN_1405c4800(Actor+0xa0, SpellItem, default, 0)` [EV-0583]. The helper's receiver type, collection semantics, ActiveEffect consequences, and runtime behavior remain unresolved. Do not add a causal edge to effective armor protection, HitData, AV11/AV12, armor XP, or level-gated quests until its exact dataflow is traced.

## M-0140 — Actor.DispelSpell spell-linked effect-record transition (EV-0583/0584)

The exact `Actor.DispelSpell` tag-0x5e path passes its SpellItem to `FUN_1405c4800` on Actor+`0xa0` [EV-0583]. The helper obtains a record list through an unresolved vslot `+0x38`, selects candidates by candidate+`0x40` SpellItem identity and optional fields, then either calls `FUN_1405aed00(candidate,1)` or queues `FUN_1405c74e0` depending on receiver bit `+0x10` [EV-0584]. The immediate helper sets candidate flag bit `0x40000` (bit 18) at `+0x7c` and, for the tag-0x5e argument `1`, sends a candidate whose bit was clear to shared handler `FUN_1405b0730(candidate,0)` [EV-0585]. The handler changes record timing/status state and may call further virtual and direct helpers; their exact meanings and terminal effect remain open. A second caller walks `0xa8`-stride records and uses the same matcher [EV-0584]. This supports a spell-linked record-state/lifecycle operation, but the candidate is not RTTI-confirmed as `ActiveEffect`, the list provider and queued branch are unresolved, and no link to HitData mitigation, effective armor, AV11/AV12, UseSkill or quest gates is established. Claims CL-L395–CL-L397; no objective causal edge is added.

## M-0141 — Tag-0x3d indexed state continuation (EV-0574/0586)

`FUN_140658890` serializes tag `0x3d`, a retained object, an index and two byte flags, then submits the payload to `FUN_14065b800` [EV-0586]. Four producer functions supply distinct flag/index combinations; the `FUN_1406c9160` context also writes the string property `iMagicEquipped` and conditionally invokes an object getter and receiver slot `+0x688` [EV-0586]. Worker fallback case `0x3d` calls `FUN_1406c6ee0` with the object/index/flags [EV-0574]. That helper uses unresolved receiver slots `+0x380` and `+0x2e0` to gate and select indexed state, then calls state/update/cleanup helpers. The exact object RTTI and dynamic targets remain unknown. No direct mapped HitData, effective-armor, AV11/AV12, UseSkill, or quest-initiation edge is established; no objective causal edge is added. Claim CL-L398.

## M-0142 — Tag-0x3f immediate/deferred state-cleanup convergence (EV-0574/0587)

`FUN_1405d3900` selects an immediate call to `FUN_1405d4bf0` when the shared gate is clear, or serializes tag `0x3f` and clears source field `+0x110` when queued [EV-0587]. Worker case `0x3f` calls `FUN_1405d3680`; the wrapper copies the same four source values into the same `FUN_1405d4bf0` parameter order [EV-0574], [EV-0587]. The shared helper performs form/global checks and uses unresolved object virtual slots `+0x378`/`+0x380`, `FUN_140179420`, and `FUN_140266e40`; the latter traverses child/object entries and may call `FUN_140267bd0` on a matching entry [EV-0587]. This supports queue/direct convergence for the bounded route. Exact object RTTI, virtual meanings and downstream effects remain unknown; no direct HitData/effective-armor/AV11/AV12/UseSkill or OBJ-1 edge is established. Claim CL-L399.

## M-0143 — Tag-0x40 scalar/state update handler (EV-0588)

Worker case 0x40 reaches `FUN_14040e300` with an object and byte flag [EV-0574]. The exact handler resets/sets state fields, conditionally retains the supplied object, calls `FUN_14040e420`, reads a shared scalar through `FUN_140635730`, and updates two scalar fields plus a bitfield [EV-0588]. The direct update helper includes a form lookup and RTTI cast to `TESImageSpace` for form ID `0x167`; the submitted payload's RTTI and that form's plugin provenance are unknown. The handler has three direct callees, zero indirect call sites, and no direct mapped HitData/effective-protection/AV11/AV12/UseSkill edge. This is a bounded negative, not a transitive or gameplay negative. Producer `FUN_140357c70` and its `FUN_14033e470` result remain to be traced. Claim CL-L400.

## M-0144 — Typed-value decode before tag-0x40 submission (EV-0589)

`FUN_140357c70` initializes object/flag outputs, calls shared decoder `FUN_14033e470` with descriptor and byte-stream context, and submits the outputs to tag-0x40 builder `FUN_140658950` only if decoding succeeds [EV-0587], [EV-0589]. The decoder walks typed entries and includes RTTI-checked `TESForm` conversions for `SpellItem`, `MagicItem`, and `EffectSetting`; it has hundreds of call xrefs and four indirect sites [EV-0589]. The exact descriptor selected by this wrapper, its input producer, decoded object type, and any indirect callback behavior remain unknown. This narrows the direct source path but does not establish that the payload is unrelated to gameplay, HitData, or armor. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L401.

## M-0145 — Tag-0x40 producer xref matches x64 unwind metadata (EV-0590/0591)

`FUN_140357c70` directly calls only the shared decoder and tag-0x40 builder, has no analyzed direct callers, and has one data xref at RVA `0x362ffb4` [EV-0590]. EV-0591 shows that the neighboring words `0x357c70`, `0x357ce7`, and `0x1c70fcc` align with the documented x64 `RUNTIME_FUNCTION` start/end/unwind-info fields; the same pattern appears around known handler `FUN_14040e300` [EV-0588], [EV-0591]. The xref is therefore likely exception/unwind metadata, not application registration. The exact containing section, selected decode descriptor and gameplay input provenance remain unknown. No OBJ-1/OBJ-2 causal edge is established. Claims CL-L402/CL-L403.

## M-0146 — Tag-0x43 object/dword queued state update (EV-0592/0593)

`FUN_1406589f0` serializes tag `0x43`, an object pointer and a dword, retaining the object through an increment at `+0x28` before sending it to the shared worker [EV-0592]. All seven direct producers are captured: their tag-0x43 branch preserves the same object and values 0–6 across gate-set queueing and gate-clear direct calls to `FUN_14069e070` [EV-0593]. The worker case also forwards its object/dword to that helper [EV-0574]. `FUN_14069e070` updates a three-bit field at object `+0xc8` and performs component/reference/state work; its direct callee census has no mapped HitData/effective-protection/AV11/AV12/UseSkill sink [EV-0593]. Three indirect callbacks, runtime type, and downstream `FUN_140717d10` remain unresolved; no whole-path/runtime negative or OBJ-1/OBJ-2 edge is claimed. Claims CL-L404/CL-L405.

## M-0147 — Nested-state reset may emit a separate worker update (EV-0594)

`FUN_140717d10` checks a supplied byte against nested field `+0x332`, clears nested fields `+0x2f8`/`+0x332`, and conditionally calls `FUN_1406671b0` [EV-0594]. That helper may derive and store a value at the parent `+0x108`, then call worker builder `FUN_140657870`. The builder's tag and downstream behavior remain unknown; the bounded inspected route shows no mapped HitData/protection/AV11/AV12/UseSkill target. No OBJ-1/OBJ-2 edge is established. Claim CL-L406.

## M-0148 — Tag-0x0A worker event performs a handle/vector update before a virtual callback (EV-0595)

`FUN_140657870` builds tag `0x0A` with handle-like, scalar, float/vector, pointer-sized and byte payload fields before submitting to `FUN_14065b800`. Dispatcher case 10 resolves the handle, conditionally applies vector state, changes an object state, resolves a second handle, and calls recipient vtable byte offset `+0x870` [EV-0595]. The receiver RTTI and virtual target remain unknown. No direct HitData/armor-skill edge is established; no OBJ-1/OBJ-2 causal edge is added. Claim CL-L407.

## M-0149 — Tag-0x0A event has an Actor-vtable-compatible producer route (EV-0596)

Of the three direct callers to `FUN_140657870`, `FUN_140665950` passes its object `param_1` after invoking virtual byte offset `+0x4c8`, which matches primary `VTABLE::Actor` slot `0x99` and target `FUN_140677100` [EV-0596], [EV-0291]. This supports Actor-vtable compatibility for that producer route; exact RTTI for all callers is not proven. Dispatcher slot `+0x870` remains unresolved. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L408.

## M-0150 — Tag-0x0A callback resolves to primary Actor method FUN_140699500 (EV-0598)

Matching GOG `VTABLE::Actor` slot `0x10e` (`+0x870`) resolves to `FUN_140699500` at RVA `0x699500` under primary Actor RTTI [EV-0597], [EV-0598]. The method body includes Actor/process state and cleanup operations; a complete direct-call census and mapped combat/skill screen remain pending. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L410.

## M-0151 — Tag-0x0A Actor callback converges on shared helper FUN_1406be430 (EV-0599)

The primary Actor callback `FUN_140699500` has 195 direct call edges and 45 unresolved indirect sites. One process-conditioned branch calls `FUN_1406be430` with Actor/process-derived scalar/vector values and a pointer to Actor `+0x54`, then invokes Actor vtable byte offset `+0x50` [EV-0599]. `FUN_1406be430` is also called from the earlier candidate hit/damage route [EV-0429]; the shared function identity does not prove shared HitData, protection, or XP semantics. No direct resolver/HealthDamage edge is present in the callback census. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L411.

## M-0152 — Shared FUN_1406be430 transforms vectors through an ActorValue-scaled physics-like sink (EV-0600)

`FUN_1406be430` normalizes/transforms 3D vectors, queries an ActorValueOwner-like object at Actor `+0xb8` through virtual slot `+0x8` with numeric value `0x24`, then routes a computed vector to `FUN_1403fd6b0` and a nested virtual `+0x80` sink [EV-0600]. Its tag-0x0A caller passes Actor/process-derived state and Actor `+0x54`, while candidate HitData caller `FUN_1406b9df0` passes HitData-record fields; this is a shared utility with distinct data sources, not proof of the same damage or XP operation. The helper has no direct AV11/AV12/UseSkill sink. No OBJ-1/OBJ-2 edge is added. Claim CL-L412.

## M-0153 — Actor slot `+0x50` forwards to a global state manager (EV-0601)

Primary GOG `VTABLE::Actor` slot `0xA` resolves to `FUN_1401dfdc0`. If global `DAT_14317bfc0` is nonzero, this method calls `FUN_140606580(global, Actor, selector, 0)`; otherwise it returns a false-like result [EV-0601]. The manager target is not yet traced. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L413.

## M-0154 — Tag-0x0A follow-up updates selector bits in a gated manager map (EV-0602)

Actor slot `+0x50` reaches `FUN_140606580`, which checks TLS/global/Actor flags and conditionally calls `FUN_140602e40(manager+0x330, Actor+0x14, selector)`. The helper hashes and looks up the integer key, ORs the selector into stored state, and calls generic update helper `FUN_140603310` [EV-0602]. One Actor virtual slot `+0x160` and generic update behavior remain unresolved. No direct OBJ-1/OBJ-2 sink or causal edge is established. Claim CL-L414.

## M-0155 — Tag-0x44 worker event re-enters a gated object producer (EV-0603)

`FUN_140658a30` builds tag `0x44` from a dword and byte. Producer `FUN_1401fa010` queues the same data under `FUN_1406d4110`; the worker's case `0x44` calls that producer again. The clear-gate route conditionally calls `FUN_1401fdb80` on an acquired object's `+0x170` member [EV-0603]. The object type and helper behavior remain open. No OBJ-1/OBJ-2 edge is established. Claim CL-L415.

## M-0156 — Tag-0x44 helper is a pointer-array cleanup/keyed fallback (EV-0604)

`FUN_1401fdb80` scans a pointer array at `param_1+0x128` for `param_2`, removes a match through `FUN_1401fe380`, or calls object vtable `+0x148` and forwards the returned key to `FUN_140d1ed80` [EV-0604]. Its other caller enters from a float/time branch. Dynamic types and effects remain open. This weakens a combat-specific interpretation but does not establish a broad negative or an OBJ-1/OBJ-2 edge. Claim CL-L416.

## M-0157 — Tag-0x44 keyed fallback manipulates a manager-owned object array (EV-0605)

`FUN_140d1ed80` scans a manager-owned refcounted array by pointer identity when the object key at `+0x38` is `-1`, clears object state and removes the array slot through `FUN_140d20780`; other key values dispatch through unresolved manager vtable `+0x1c8` [EV-0605]. Four callers share the helper, including sibling collection code. The direct branch is object-registry state work without a mapped HitData/armor-skill sink; virtual and transitive effects remain open. No OBJ-1/OBJ-2 edge is added. Claim CL-L417.

## M-0158 — Worker collection cleanup is a structural analogy (EV-0581, EV-0604/0605)

The Actor.RemoveSpell tag-0x5d route removes an object from a pointer-backed collection [EV-0581]. The unrelated tag-0x44 path uses `FUN_1401fdb80` and `FUN_140d1ed80` to update manager-owned pointer arrays with reference counting [EV-0604], [EV-0605]. These are distinct GOG call paths with no shared direct helper, RTTI identity, or proven class; the resemblance is an analogy, not an ActiveEffect or gameplay edge. To upgrade it, find a common concrete removal helper or compatible receiver type and trace its producer. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L418.

## M-0159 — Tag-0x44 object factory shares a keyed registry with BGSDecalNode cleanup (EV-0606)

`FUN_1404a27f0` finds a global-array entry by its +0x28 key, retains it, then removes the entry through `FUN_1401fe280`. Two other callers are Ghidra-labeled BGSDecalNode cleanup routines that call the same factory on child +0x28 keys [EV-0606]. This associates the registry with scene/decal-object cleanup and further weakens a combat interpretation; it does not type the returned object or resolve the alternate factory and finalizer. No OBJ-1/OBJ-2 edge is added. Claim CL-L419.

## M-0160 — Tag-0x44 selects between parallel keyed object arrays (EV-0607)

`FUN_1404a28a0` scans a second global object array by field +0x28 and removes a match through the same `FUN_1401fe280` array helper used by `FUN_1404a27f0` [EV-0607], [EV-0606]. Its only observed caller is the tag-0x44 producer. The decompiler omits arguments at that call despite the callee's two-parameter prototype; producer register flow and returned type remain unresolved. The bounded helper is generic registry lifecycle work with no direct HitData/armor-skill edge. No OBJ-1/OBJ-2 edge is added. Claim CL-L420.

## M-0161 — Tag-0x44 callback is keyed object-list lifecycle work (EV-0608)

`FUN_1401fa010` passes identical `&local_18`/key arguments to the two parallel array factories, then conditionally sends the acquired object and its `+0x170` manager to `FUN_1401fdb80`. One direct caller traverses child objects, filters by unresolved vtable `+0x10`/owner identity, and calls the producer with child `+0x28` and `+0x54`; another drains a dword list. The keyed factories' shared registry is also used by BGSDecalNode cleanup [EV-0606], [EV-0607], [EV-0608]. This bounds caller 47 as generic object lifecycle work with unresolved virtual callbacks, not a direct tag-0x0B/armor-skill constructor. No global negative or OBJ-1/OBJ-2 edge is added. Claim CL-L421.

## M-0162 — Caller 48 tag-0x45 byte event returns to a gated state helper (EV-0609)

The builder at function start `FUN_140658a60` (requested caller-list address `0x658a80` is inside this function) queues tag `0x45` plus a byte. Its sole observed producer `FUN_140774b80` routes through `FUN_1406d4110`; the gate-clear branch calls `FUN_1401fa100(manager,1)`, while the deferred branch call's byte argument is omitted by decompilation. Dispatcher case `0x45` returns to `FUN_1401fa100` with the payload byte [EV-0609]. The producer register flow, helper descendants, and runtime effect remain open. No direct HitData/armor-skill edge is established. Claim CL-L422.

## M-0163 — Tag-0x45 target performs flag-dependent manager-list cleanup (EV-0610)

`FUN_1401fa100` walks and clears manager child lists, invokes unresolved child vtable `+0x1c0`, and in the nonzero mode calls `FUN_1401fdab0`, a gated `FUN_1414a33c0`, and an array compaction helper [EV-0610]. Its callers include the tag-0x45 immediate path, dispatcher case 0x45, and a flag-0 teardown path. The bounded body is manager/list state work with no direct mapped HitData or armor-skill sink; dynamic effects and deferred argument flow remain open. No OBJ-1/OBJ-2 edge is added. Claim CL-L423.

## M-0164 — Tag-0x45 immediate/deferred selector parity confirmed (EV-0611)

`FUN_140774b80` loads `RDX=1` before testing `FUN_1406d4110`; the immediate branch calls `FUN_1401fa100(manager,1)`, while the queued branch calls `FUN_140658a60(manager)` with `RDX` still 1 [EV-0611]. The builder copies that byte and dispatcher case 0x45 forwards it to `FUN_1401fa100` [EV-0608], [EV-0609]. This confirms queue/direct parameter parity for the flag-1 manager-list cleanup path. The route has unresolved virtual callbacks but no direct HitData/armor-skill sink. No global negative or OBJ-1/OBJ-2 edge is added. Claim CL-L424.

## M-0165 — Caller 49 tag-0x48 object-pair event enters list iteration (EV-0612)

Builder `FUN_140658ac0` writes tag `0x48` with a retained object pointer and a second pointer-sized payload, then queues it. Dispatcher case 0x48 obtains a list through the first object+`0x38` virtual slot `+0x10`, iterates its `+0x14` entries and calls `FUN_14054e390` [EV-0612], [EV-0608]. The builder has zero analyzed incoming direct calls and one unclassified DATA xref; RTTI, helper semantics, and runtime behavior remain open. No direct HitData/armor-skill or OBJ-1 edge is established. Claim CL-L425.

## M-0166 — FUN_14054e390 is a generic virtual list callback primitive (EV-0613)

The helper loads a non-null entry object, calls its vtable slot `+0x20` with the supplied context, sets context byte `+8`, and returns 1. Four direct callers include the tag-0x48 case in `FUN_140659160`; the concrete interface and callback effects remain unknown. This is a structural operation, not evidence of armor-skill behavior. Claim CL-L426.

## M-0168 — Caller 50 tag-0x49 retained-object list/update route (EV-0615)

`FUN_140658b10` queues tag `0x49` with a retained object pointer. Its sole producer `FUN_1407bbb90` traverses an object list through `FUN_14054e3c0`/`FUN_14054e340` and selects an immediate virtual `+0x1a8` path or queued tag 0x49 followed by `FUN_140657c30`; the dispatcher traverses the object list through `FUN_14054e340` [EV-0615]. Type identity, callback contracts, virtual target and runtime effects remain open. No direct HitData/armor-skill edge is established. Claim CL-L428.

## M-0169 — Caller 50 producer has unresolved immediate and queued object-update branches (EV-0616)

`FUN_1407bbb90` directly traverses an object list through `FUN_14054e3c0`/`FUN_14054e340` and calls `FUN_140657c30` after queuing tag `0x49`; a branch instead invokes unresolved virtual slot `+0x1a8` [EV-0616]. It has 7 unresolved indirect sites and no analyzed direct caller. A source-less data xref lies among adjacent code-pointer qwords at candidate table RVA `0x18bb240`; RTTI identity is not yet known. No HitData/armor-skill causal edge is established. Claim CL-L429.

## M-0170 — Caller 50 producer is AddRagdollHandler vtable slot 1 (EV-0617)

RTTI identifies the table at RVA `0x18bb240` as primary `AddRagdollHandler` (subobject offset 0). The table's slot 1 points to `FUN_1407bbb90` [EV-0616], [EV-0617]. This identifies class membership only; method name, argument type, triggering event and gameplay effect remain unknown. No armor/HitData causal edge is established. Claim CL-L430.

## M-0171 — AddRagdollHandler queues tag 0x12 for its slot +0x1a8 operation (EV-0618)

The direct branch in `FUN_1407bbb90` invokes receiver slot `+0x1a8` with object `lVar8`, constants `1,1`, selector `uVar13`, and final argument 0. The queued branch builds tag `0x12` with the corresponding receiver/object/selector fields through `FUN_140657c30`; case 0x12 invokes the same slot with matching visible arguments [EV-0615]–[EV-0618]. Exact final-argument equality remains pending disassembly; slot target and effect remain unresolved. No armor-XP edge is established.

## M-0172 — Earlier case-0x12 mismatch attribution (superseded by M-0184)

EV-0619 correctly captured the instructions at RVA `0x65939c`, but those instructions belong to dispatcher case `0x4`, not case `0x12`. Applying them to tag `0x12` created a false mismatch model. The actual case-0x12 call is at RVA `0x659c92`; EV-0631 records its exact arguments and the correction. Preserve EV-0619 as provenance for the misattributed case; use M-0184 for the corrected route. Claim CL-L432 is retracted.

## M-0173 — Worker wrapper passes the event pointer; dispatcher builds call arguments (EV-0620, EV-0631)

At the sole direct call to `FUN_140659160`, `FUN_14065b800` explicitly loads only `RCX` with the event pointer [EV-0620]. The dispatcher reads case-0x12 values from that event and constructs the downstream virtual call arguments itself: receiver/object pointers, `1,1`, the selector dword and a zero sixth argument [EV-0631]. The wrapper's callsite therefore does not establish a mismatch or preclude parity. This remains static argument construction, not semantic, runtime or armor-XP equivalence. Claim CL-L433.

## M-0174 — FUN_14054e340 performs a short-circuit any-match predicate over a list (EV-0621)

For each non-null entry, if the context byte is false, the helper invokes element vtable `+0x10`; a true result sets the byte and short-circuits later predicate calls. False/null results preserve 0. It has six direct callers, including AddRagdollHandler producer/dispatcher and `FUN_140699500` [EV-0621]. This proves shared helper reuse, not shared semantic outcome; element types and predicate behavior are unresolved. No HitData/armor-skill causal edge is established.

## M-0175 — FUN_14054e3c0 applies a per-entry virtual +0x28 callback and seen flag (EV-0622)

For each non-null list entry, the helper calls its vtable `+0x28` with no explicit arguments, writes the context byte to 1, and returns success. It has two direct callers, `FUN_1407bbb90` and `FUN_140713d90` [EV-0622]. In caller 50 it precedes the separate +0x10 any-match list pass [EV-0621]. The element type and callback effect remain unresolved; no HitData/armor-skill edge is established.

## M-0176 — Caller 50 selects +0x1a8 receiver through optional-object/global fallback (EV-0623)

The AddRagdollHandler producer passes its `param+0x60` subobject to `FUN_1402b8b60`. Bit 0 at subobject `+0x40` selects `FUN_1401699e0(subobject+0x48)`; otherwise the resolver returns `DAT_1420f9d28` [EV-0616], [EV-0623]. That result becomes the receiver for slot `+0x1a8`. Type identity and slot target remain unknown; no HitData/armor edge is established.

## M-0177 — FUN_140179080 resolves a bitmap-gated numeric key through a cached holder list (EV-0624)

The helper locks the holder, checks a bitmap bit for the requested numeric key, then consults a thread-local cache keyed by holder and key. On a miss it scans the holder's linked entries, compares the key against each entry's virtual slot `+0x8` result, caches a match, releases the lock, and returns the entry [EV-0624]. `FUN_1401699e0` requests key `1` and extracts the matched entry's object at `+0x10` [EV-0623], [EV-0624]. This identifies generic keyed-holder infrastructure only; concrete type, slot `+0x1a8` target, and gameplay effect remain unknown. Claim CL-L437.

## M-0178 — DAT_1420f9d28 is a runtime-populated global receiver cell (EV-0625)

The static GOG image stores zero at `DAT_1420f9d28`, but analyzed code reads the cell widely. A reference census finds 47 reads and two writes to the exact cell: `FUN_1402c65b0` assigns `RDI`, while `FUN_1402c6720` stores zero [EV-0625]. Therefore the captured file value does not identify the active runtime receiver. Trace the assignment's RDI provenance and type and the clearing path before reading caller 50 slot `+0x1a8`. Claim CL-L438.

## M-0179 — FUN_1402c65b0 populates caller 50's global fallback holder (EV-0626)

`FUN_1402c65b0` obtains an 8-byte holder, calls `FUN_1402c6810` with a local three-dword value copied from `DAT_1432740d8..0xe0`, stores the holder in `DAT_1420f9d28` and stores the returned pointer at `*holder`, retaining it when nonnull [EV-0626]. The sole analyzed direct caller `FUN_140221790` invokes the setter only when its second argument is nonzero. `FUN_1402b8b60` later returns `*DAT_1420f9d28` on the fallback branch [EV-0623]. The factory result's type and gameplay meaning remain unresolved. Claim CL-L439.

## M-0180 — Caller 50 global fallback constructs bhkWorldM (EV-0627)

`FUN_1402c65b0` passes zero to factory `FUN_1402c6810`, selecting its false branch and constructor `FUN_140ebdf30`. That helper performs common `FUN_140e84cf0` initialization and installs `bhkWorldM::vftable` [EV-0626–EV-0627]. The fallback resolver returns the first qword stored in the global holder, so the missing optional key-1 object falls back to this bhkWorldM receiver [EV-0623], [EV-0627]. A separate branch constructs bhkWorld. The exact vtable address, slot `+0x1a8` target and gameplay effect remain open; no HitData/armor edge is established. Claim CL-L440.

## M-0181 — bhkWorldM fallback vtable is at GOG RVA 0x19e9078 (EV-0628)

`FUN_140ebdf30` writes vtable address `0x1419e9078` into the returned object after common initialization; GOG image base `0x140000000` gives RVA `0x19e9078` [EV-0628]. Caller 50's global fallback selects this constructor through `FUN_1402c6810(param2=0)` [EV-0626–EV-0627]. Validate the table RTTI and zero-based slot `0x35` for byte offset `+0x1a8`; method identity and gameplay effect remain unknown. Claim CL-L441.

## M-0182 — RTTI confirms caller 50 fallback vtable as primary bhkWorldM (EV-0629)

The table at GOG RVA `0x19e9078` has MSVC type descriptor `.?AVbhkWorldM@@`, signature 1, and subobject offset zero [EV-0629]. This validates the constructor label and identifies a primary bhkWorldM fallback receiver [EV-0627–EV-0629]. Its byte-offset `+0x1a8` slot remains unresolved; no HitData or armor-skill edge is established. Claim CL-L442.

## M-0183 — bhkWorldM slot +0x1a8 contains a flag-gated object callback path (EV-0630)

RTTI-verified bhkWorldM slot `0x35` targets `FUN_140e884d0`. With sixth argument zero, it requires nonnull `FUN_140e0f510(object)` and bit `1` in the returned record's `+0x18`; nonzero skips this eligibility test. Passing the guard sets receiver byte `+0xc5f8` and emits optional callback records through `FUN_140e898f0` [EV-0630]. Both the immediate producer and deferred case-0x12 call pass zero in argument six [EV-0615], [EV-0631], so the proposed nonzero-argument eligibility bypass is falsified for this captured static path. Callback execution, runtime effect and Steam behavior remain open. No direct HitData/armor-skill sink is present. Claim CL-L443.

## M-0184 — Tag-0x12 deferred call exactly matches immediate slot +0x1a8 arguments (EV-0631)

The immediate AddRagdollHandler branch calls slot `+0x1a8` as `(receiver, object, 1, 1, uVar13, 0)`. Its deferred builder stores tag `0x12`, the same object and receiver pointers, and `uVar13` at event `+0x18`. The correct dispatcher case is at RVA `0x659c92`: it sets `RCX=R14`, `RDX=R15`, `R8D=1`, `R9B=1`, copies event `+0x18` to stack argument five, and explicitly stores zero at stack argument six. The formerly cited `0x65939c` site is a different case (`0x4`) [EV-0631]. This establishes exact static argument parity and falsifies the proposed `param6 != 0` check bypass, while leaving dynamic object state, callback outcome, runtime behavior and armor/skill causality untested. Claims CL-L432 (retracted), CL-L433, CL-L443 and CL-L444.

## M-0185 — Caller 51 tag-0x4b PlayerCharacter state update (EV-0632)

`FUN_140658b50` queues a tag-0x4b byte event; case 0x4b calls `FUN_140738380` with the PlayerCharacter global [EV-0632], whose constructor and primary vtable were independently verified [EV-0344]. The producer's clear-gate path gets two objects through PlayerCharacter slot `+0x378`, tests a conditional primary slot `+0x4c8` predicate over PlayerCharacter `+0xc8`, toggles bit 0 at both selected objects `+0xf4`, and updates PlayerCharacter byte `+0xbe3`. It later runs paired-record and nested-object callbacks, including recursive `FUN_1402df6d0`. The bounded direct bodies contain no mapped HitData, protection, AV11/AV12 or UseSkill sink. Ten producer virtual sites and deeper dynamic callbacks remain open; do not generalize the bounded result into a global no-hit claim. Caller 50 and 51 also pass the same adjacent data tuple `DAT_1432740d8..+8` to different helpers [EV-0626], [EV-0632]; this is a configuration/registration lead only. Claim CL-L445; no OBJ-2 causal edge is established.

## M-0186 — Shared tuple reused by distinct factory and event-record paths (EV-0633)

Caller 50's `FUN_1402c6810` consumes a local copy of `DAT_1432740d8..+8` as a three-dword constructor input. In its false/fallback branch it sends the first two values to `FUN_140e854e0` and sets the third to zero. Caller 51 reaches `FUN_140cb4ae0`, which copies all three supplied values into a queued event record before scheduling it through `FUN_140cbc770` [EV-0626], [EV-0632], [EV-0633]. These are distinct direct mechanisms, not a shared registration/update primitive. The tuple values and field semantics remain unknown; this synthesis adds no causal HitData/armor/quest edge. Claim CL-L446.

## M-0187 — Caller 52 tag-0x56 retained-object collection callback (EV-0634)

`FUN_140658be0` queues tag `0x56` with a retained object. Its producer `FUN_140778a20` tests shared gate `FUN_1406d4110` and either queues the object or calls its virtual `+0x138` slot. Dispatcher case `0x56` calls `FUN_140777f40(DAT_1420f7db0, object)` before invoking the same receiver slot without explicit arguments [EV-0634]. The producer's sole analyzed caller, `FUN_140774b80`, walks a manager collection at `+0xe8`, calls the wrapper for each member, decrements references and clears the collection; this owner is itself called by `FUN_140643ec0` in a broad cleanup sequence. The extra manager helper performs keyed membership/state work across multiple collections. Receiver RTTI and virtual descendants remain unresolved; no direct HitData/protection/AV11/AV12/UseSkill edge appears in the captured tag-specific route. Claim CL-L447; no causal armor-XP edge is established.

## M-0188 — Actor slot-0x89 tag-0x50 process-state callback (EV-0635)

The primary Actor vtable's slot `0x89` (`+0x448`) is `FUN_140664cf0`; it excludes one global and Actor objects with flag bit 11, then queues tag `0x50` with the same object pointer [EV-0400], [EV-0635]. Case 0x50 dispatches through thunk `FUN_140664d20` to `FUN_1402ec610`. That handler returns when the receiver is PlayerCharacter or bit 11 is set; otherwise it performs Actor/process and object-state updates. Its direct census contains 51 edges and 17 unresolved virtual sites; no direct mapped HitData, protection, AV11/AV12 or UseSkill target appears [EV-0344], [EV-0635]. The bounded route adds no OBJ-2 causal edge; dynamic descendants remain open. Claim CL-L448.

## M-0189 — Tag-0x54 spatial/context Actor update and tag-0x32 state callback (EV-0636)

Caller 54 builder FUN_140658c50 writes tag 0x54 with a retained Actor and producer-selected context field. Sole producer FUN_14066b6e0 selects this branch only under Actor process/flag conditions and when FUN_1402bec30 rejects the Actor's horizontal coordinates against a process-grid pair; a separate FUN_14019ca70 rectangle check gates different worker/direct callbacks [EV-0636]. These field and coordinate patterns support a spatial/context inference; the globals and runtime object semantics remain unnamed.

Dispatcher case 0x54 enters FUN_1402eb6f0, whose complete direct census has 63 edges and 21 unresolved virtual sites. No mapped direct HitData, protection, AV11/AV12 or UseSkill target appears [EV-0636]. A shared-gate branch queues tag 0x32 with Actor and its slot-0x380 context or calls Actor slot +0x328 immediately. The dispatcher case and immediate route converge on slot +0x328, mapped to FUN_140666770; its body clears nested state, uses FUN_1402e55a0, and may call recursive object-tree helper FUN_140e88c50 [EV-0400], [EV-0635], [EV-0636]. The context selector is also used by the HitData receiver [EV-0295], [EV-0296], [EV-0512], while the recursive helper is mapped on tag 0x3C [EV-0483]–[EV-0486]. Shared call targets establish code reuse, not same-pointer identity or hit/armor causality. No OBJ-2/OBJ-1 edge is added; 21 virtual sites and nested descendants remain open. Claim CL-L449.

## M-0190 — Tag-0x57 gated numeric notification and registry helper (EV-0637)

Caller 55 builder FUN_140658c90 writes tag 0x57 with a supplied 32-bit value. Its sole analyzed producer FUN_14075a430 gates category/value/limit arguments, using distinct literal categories 0x18–0x1A, threshold globals, and codes 0xFC–0xFE; caller FUN_14074b720 updates separate bits at receiver +0xbe4 [EV-0637]. The captured comparisons do not establish a previous-value crossing or the names of these categories/codes.

Dispatcher case 0x57 passes the code to FUN_140971910. Its complete direct census has six calls and zero indirect sites; the bounded body searches an integer list and may initialize/insert the code through FUN_1409786e0 and FUN_140971e00 [EV-0637]. No mapped direct HitData, protection, AV11/AV12 or UseSkill target appears, and no quest/ActorValue interpretation is established. Shared registry code is not a causal edge. Claim CL-L450.

## M-0191 — Tag-0x58 PlayerCharacter collection and perk-rank cleanup (EV-0638)

Caller 56 FUN_140658cc0 writes tag 0x58 with an object pointer and mode byte; two nonnull-gated producers pass modes 0 and 1 [EV-0638]. Dispatcher case 0x58 supplies PlayerCharacter DAT_143188918 to FUN_14074b350 [EV-0344], [EV-0637], [EV-0638]. The handler scans/removes from object collections at +0x4e8/+0x4f8 and +0x4d0/+0x4e0, with a paired reference-count branch, and conditionally enters FUN_140750f70 [EV-0638].

FUN_140750f70 uses an RTTI-verified BGSPerk::FindPerkInRanksVisitor to compare object pointers and may remove a matching entry from the PlayerCharacter list at +0x4b8 [EV-0638]. Its dynamic PlayerCharacter slot +0x650 remains unresolved; the primary Actor base slot is a no-op but is not proof of the derived runtime target. The bounded path shows cleanup, not perk granting, level eligibility, HitData, protection, AV11/AV12, UseSkill, or armor XP. No causal OBJ-1/OBJ-2 edge is added. Claim CL-L451.

## M-0192 — Tag-0x5F perk-rank addition and per-rank callback fanout (EV-0639)

Caller 57 FUN_140658d00 writes tag 0x5F with an object-derived dword, another object pointer, and two rank bytes; worker case 0x5F resolves a handle and calls FUN_1403906c0 [EV-0637], [EV-0639]. The sole analyzed producer FUN_140750d80 uses a Ghidra-labeled AddPerkVisitor to scan PlayerCharacter+0x4b8, adds or updates a perk-rank pair, and emits old rank 0/new requested rank. Rank 0 defaults to current matching rank+1, and the explicit bound is the byte at perk+0x52 [EV-0639].

The current-rank lookup uses FUN_14068f020/FUN_1407177b0 and a FindPerkInRanksVisitor label, returning a matched rank byte through PlayerCharacter slot +0x7D0. FUN_1403906c0 fans old/new ranks to per-entry slots +0x58/+0x50; both remain unresolved. Wrapper FUN_14074b150 and FUN_14074b220 have no analyzed incoming direct callers; their candidate six-entry pointer region has no identified table-base references and fails the RTTI check. No Player-level eligibility check, verified level-one caller, HitData, protection, AV11/AV12, UseSkill, armor XP, or quest-start edge is established. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L452.

## M-0193 — Tag-0x5A handle-keyed coordinate state update (EV-0640)

Caller 58 FUN_140658dd0 writes tag 0x5A with an object-derived dword and boolean byte. Dispatcher case 0x5A resolves the handle and calls FUN_1405259c0 on manager DAT_1420f9d78 [EV-0637], [EV-0640]. When the handle and boolean permit, the target reads PlayerCharacter and object coordinates and creates or updates a handle-keyed record; false/null cases remove or clean state. The target has five direct calls and 13 unresolved manager virtual sites [EV-0640].

Producer FUN_140686320 is primary Actor vtable slot 0x9C under verified RTTI .?AVActor@@. It checks process/object predicates and a float threshold from Actor state, then emits the event; FUN_140731e80 is its sole analyzed direct caller, compares a supplied float against geometry-derived state, and updates the same manager [EV-0400], [EV-0640]. Producer FUN_14051df20 removes matching collection entries and can emit a false-byte cleanup event; one of its callers processes Havok contact pairs with hkpAllCdBodyPairTempCollector [EV-0640]. The route is bounded spatial/physics state, not a mapped quest level check or incoming-hit/armor-skill path. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L453.

## M-0194 — Tag-0x5B deferred disarm-related Actor action (EV-0641)

Caller 59 `FUN_140658e10` writes tag 0x5B with two dwords; sole analyzed producer `FUN_1405b93a0` emits it when the object at `param_1+0x50` resolves and its `+0xCC` bit 13 is set. It derives the payloads from `FUN_140676b60` and `param_1+0x34`, queues the event, then calls `FUN_1405aed00(param_1,0)` [EV-0641]. Dispatcher case 0x5B resolves both dwords as handles and calls `FUN_14067aea0`. On a successful result that function calls primary Actor slot +0x658 and, when its first Actor pointer is the PlayerCharacter global, emits “You have been disarmed.” [EV-0400], [EV-0641].

The Actor table slot +0x658 is slot 0xCB and resolves to `FUN_14067a400`; its complete captured body has 25 direct edges and 16 unresolved virtual sites. No explicit level check or mapped direct HitData/protection/AV11/AV12/UseSkill sink appears in the bounded bodies [EV-0641]. The immediate producer helper sets/tests bit `0x40000` and may call `FUN_1405b0730(param_1,0)`; no direct convergence with the deferred receiver is captured, so keep immediate state/update and deferred Actor action as separate routes. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L454.

## M-0195 — Tag-0x5C HitData-derived serialized branch to shared vector helper (EV-0642)

Caller 60 `FUN_140658e50` builds tag 0x5C, clones its second argument through `FUN_1407dce10`, derives a byte flag through virtual slot +0x478, and queues the context. Its sole analyzed producer is `FUN_1406b9df0`, the mapped HitData handler [EV-0295], [EV-0296], [EV-0642]. EV-0431 maps the clone helper's copied fields at 0x50/0x54/0x5C/0x80 against fields consumed by that handler [EV-0431].

In the producer, one guarded branch queues tag 0x5C when `FUN_140667430` is nonzero; the alternate zero branch calls `FUN_1406be430` directly. Dispatcher case 0x5C resolves an object identifier from the copied context and calls `FUN_1406be2c0`, which uses three direct calls and three unresolved virtual sites and conditionally calls the exact same `FUN_1406be430` helper [EV-0642]. The common function identity supports a direct/deferred shared-helper relationship, not identical receiver or arguments. EV-0600 maps the helper as vector transformation, numeric ActorValue query 0x24, and a vector/physics-like `FUN_1403fd6b0` sink, without a direct AV11/AV12/UseSkill call [EV-0600]. No level/protection/armor-XP or ordinary-hit result follows. No OBJ-1/OBJ-2 edge is added. Claim CL-L455.

## M-0196 — Tag-0x61 eye-headpart texture replacement (EV-0643)

Caller 61 `FUN_140658f70` retains an object, stores a supplied TextureSet-like payload, and queues tag 0x61. Its sole analyzed producer `FUN_1409ebcb0` checks for target 3D and eye-tagged headparts, resolves eye geometry, then queues that geometry with the supplied TextureSet [EV-0643]. Dispatcher case 0x61 checks the object's nested `+0x25` member against two untyped identity pointers, resolves the new texture value, swaps a nested `+0x78` pointer when different, and invokes a virtual +0x48 callback plus geometry/resource helpers [EV-0643]. This supports a render/texture-update interpretation; exact types and dynamic callbacks remain unresolved. No level-gate, HitData, protection, AV11/AV12, UseSkill, or armor-XP edge is established. No OBJ-1/OBJ-2 edge is added. Claim CL-L456.

## M-0197 — Tag-0x62 serialized Actor/process response route (EV-0644)

Caller 62 builds tag 0x62 from producer `FUN_1406c72d0`; dispatcher case 0x62 resolves its retained object/value payload and calls `FUN_1406bc400` [EV-0644]. That function also has a direct caller in mapped HitData handler `FUN_1406b9df0`, and it conditionally calls `FUN_140672640`, whose captured body processes Actor/PlayerCharacter state and related Actor entries [EV-0644]. The exact shared callee is supported; runtime event/argument identity is not. `FUN_1406bc400` has 13 unresolved indirect sites and `FUN_140672640` has five. No explicit level/quest gate or mapped effective-protection, AV11/AV12, or UseSkill sink is established in this bounded path. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L457.

## M-0198 — Actor effect scaling through MagicTarget resistance (EV-0651)

In GOG SkyrimSE.exe 1.6.1179.0, `FUN_1406c68d0` loops target-effect entries, applies entry predicates, and dispatches vtable slot +0x50 at RVA `0x6C6AEB` with `this=param_1+0xA0`. The slot maps to `Actor::MagicTarget::CheckResistance` at RVA `0x6C45A0`; the receiver also matches ActorValueOwner at `param_1+0xB8` [EV-0400]–[EV-0402], [EV-0650]–[EV-0651]. The function uses the resistance return to scale accumulated effect values and queries ActorValueOwner values before producing its outputs. This establishes a GOG static effect-resistance consumer, not a live damage result or Steam-equivalent attack event.

The bounded target has three direct call edges from `FUN_1407ee620` and `FUN_140764c30` [EV-0651]. `FUN_1407ee620` also directly calls `FUN_1406be430`, a shared vector/physics-like helper that is separately reached by mapped HitData code [EV-0600], [EV-0652]. The captured arguments differ from the HitData-shaped call; the helper has no direct AV11/AV12/UseSkill sink in the reviewed body [EV-0600]. Treat the shared helper as code reuse, not evidence that magic resistance and a qualifying physical hit are the same event or that armor XP is suppressed.

The candidate ARMO `000FC061` is Clothing with zero physical DNAM and an AV44 Resist Magic enchantment; official lists admit it at levels 8–11 and reach it through the common citizen pocket list, which is an inventory-list reference on level-8 Madesi [EV-0398], [EV-0645]–[EV-0648]. Whether the nested request uses actor, player, or encounter-zone level remains open. No physical armor protection, level-one acquisition, live Health damage, or zero Heavy/Light AVSK result is established. No OBJ-1 or armor-XP causal edge is added. Claim CL-L458–CL-L460.

## M-0199 — TESCondition OR-run grouping and Dragonborn world-encounter condition (EV-0668)

The GOG AE 1.6.1179.0 function at RVA `0x49FBB0` iterates condition-list nodes, tests the item flag bit 0, maintains a pending OR run across consecutive flagged nodes, short-circuits later terms after a successful term, and combines the completed run with the prior unflagged accumulator [EV-0667]–[EV-0669]. The wrapper disassembly preserves the original condition-list argument in RCX into this evaluator; its decompiler's literal-zero argument is contradicted by the instruction sequence [EV-0669].

Dragonborn.esm QUST `DLC2WE09`'s native `QUST\\9 Conditions` rows are `GetRandomPercent`, `GetStage MQ105`, `GetStage DLC2MQ06`, `GetLevel`, and `GetInCurrentLoc` [EV-0657]. Raw CTDA bytes and the revision-pinned TES5Edit decoder identify the final pair as GetLevel `>=25` with OR set and a Solstheim location condition with OR set [EV-0665], [EV-0666]. Applying the captured GOG evaluator gives the bounded expression `earlier chance/stage conditions AND (GetLevel >=25 OR GetInCurrentLoc Solstheim)` for this serialized row sequence. This is a cross-build static mechanism inference: it does not transfer a GOG RVA to Steam, establish when the QUST list is evaluated, or prove a natural level-one world-encounter start.

The separate main-quest CLOC node selects QUST `DLC2CultistAmbush`; the world SCPT branch selects QUST `DLC2WE09` [EV-0656]–[EV-0664]. Their shared stage-10 `DLC2MQ01` handoff is source-level reuse, not identity or causal evidence for armor/XP behavior [EV-0663]. No causal OBJ-1/OBJ-2 edge is added. Claims CL-L462–CL-L464.

## M-0200 — Synchronous HitData mitigation-to-armor-skill phase order (EV-0670–EV-0685)

In the identity-checked GOG AE 1.6.1179.0 path, `FUN_1407ddf50` snapshots `physicalDamage` before AV39/armor-factor mitigation changes `totalDamage`. Its synchronous builder/selector path reaches `FUN_1406bcaa0`, where the unblocked player-receiver worn-ARMO scan routes eligible armor to AV11/AV12 and UseSkill; the later `FUN_1406b9df0` call is a distinct health/trap continuation [EV-0670], [EV-0673]. The hit builder invokes selectors 0x25/0x27 through `FUN_140386070`; its callback walks entrypoint data synchronously before returning to the builder [EV-0671].

The official five-master screen found 13 selector-37 and 10 selector-39 file rows, but EV-0683 corrects the field attribution: DATA[1] carries handler IDs 1 (one row), 3 (19 rows), and 14 (three file rows); EPFT separately selects function-data classes 1/2 [EV-0675], [EV-0683]. Generic handlers 1/2 remain mapped in EV-0672, but they are not the complete official-row handler set. The captured GOG IDs 3/14 gate on type-1/type-2 data objects and write numeric entrypoint results; ID14 additionally reads numeric AV index 138 and a coefficient from the TwoValue payload [EV-0684]. Its ActorValue getter can populate derived-value caches on a miss; direct stores observed in that bounded path target caches, not the underlying permanent/temporary/damage inputs, equipment, HitData, UseSkill/AVSK, or an event queue [EV-0685]. A dynamic ActorValueInfo callback remains unresolved, so this is not a global negative. No equipment-interposition window is identified in the captured GOG source path. The blocked branch routes AV9 and remains a separate control [EV-0222], [EV-0261]. No measured protection/AVSK result or qualifying OBJ-2 outcome is established; keep EV-0260 open. No OBJ-1 edge is added. Claims CL-L465, CL-L467, CL-L471–CL-L473.

## M-0201 — Dragonborn CLOC cultist actor record chain and template-copy candidate (EV-0677–EV-0680)

The official-record source walk distinguishes the main CLOC route from the world encounter: `DLC2CultistAmbush` is selected by the CLOC branch, while `DLC2WE09` is the separate SCPT/world QUST with the level/location OR group [EV-0654]–[EV-0669]. The screened CLOC parent/node/QUST and loose PSC material contain no explicit `GetLevel` predicate before the QUST start [EV-0654], [EV-0656], [EV-0658], [EV-0660], [EV-0663], [EV-0664]. This is a bounded static result, not a natural level-one start or proof that no unexamined native callback/profile override can add a gate.

Direct TES4 parser captures link both CLOC alias NPCs through `DLC2LvlCultist*` NPC_ records to `DLC2LCharCultistSummoner` and `DLC2LCharCultist` LVLN roots. Each root has `LVLF=0x03`, entries at levels 1 through 46, and a level-1 nested list whose child entries point to NPC_ leaves; the selected leaves encode actor level 12 [EV-0677]. The alias/intermediate NPC_ records encode zero actor-base flags, clear `PCLevelMult` and `UsesTemplate` bits, non-null TPLT links, and nonzero per-field template-use masks [EV-0677]. TES5Edit source definitions label these serialized fields but do not determine runtime selection [EV-0680].

The GOG AE 1.6.1179.0 TESNPC slot-4 override is identified as `CopyFromTemplateForms`; its body reads the base-template pointer and per-field mask and branches on ACBS bit 0x100, while a helper can initialize template-chain state [EV-0678]. This shows a general GOG template-copy mechanism. It does not prove that these specific Steam alias records follow their TPLT chain or that the leveled lists are evaluated using player level. H3 (level-dependent actor selection) and H4 (stored links not consumed by this alias-fill path) remain competing runtime hypotheses under EV-0260.

No causal edge connects the cultist record/template route to OBJ-2 mitigation, armor classification, AV11/AV12, or hit-earned armor XP. The current evidence neither identifies a level-gated CLOC initiation nor a level-one bypass. Claims CL-L468, CL-L469, CL-L470.

## M-0202 — Conditional Dragonborn world-cultist location route (EV-0389–EV-0390, EV-0657–EV-0669, EV-0686–EV-0687)

The official Dragonborn DLC2WE09 world QUST's bounded expression is the event-chance predicate AND MQ105 >= 160 AND DLC2MQ06 < 550 AND (GetLevel >= 25 OR current location is DLC2SolstheimLocation, 04016E2A) [EV-0657], [EV-0665]–[EV-0669]. The captured GOG evaluator groups the consecutive OR-flagged level/location rows; this is cross-build static inference, not Steam evaluator evidence. The SCPT parent, priority selector, and child node carry event/keyword conditions but no extra level test in the screened official records [EV-0661], [EV-0662], [EV-0664], [EV-0686]. Official Solstheim trigger placements and the bounded WETriggerScript source submit the DLC2 event keywords without an explicit level read [EV-0389], [EV-0390].

The initial Windhelm ferry topic's six INFO children, associated by its DIAL TIFC count and serialized order, contain no function-index-80 GetLevel condition [EV-0686]. Revision-pinned UESP describes paid passage before the cultists appear and an alternate post-cultist dialogue check [EV-0687]. Neither source establishes the player's current level or when the engine evaluates DLC2WE09. The exact MQ105 stage reachability, chance-global value, Steam event timing, winning profile, natural level-one quest start, and alias fill remain unresolved under EV-0260.

No causal edge connects this Story Manager/Papyrus/location route to OBJ-2 M-0200/M-0017. The screened evidence exposes no shared native call, ActorValue, ActiveEffect, equipment, HitData, serialization field, or armor-XP sink. Claims CL-L462–CL-L464, CL-L474.

## M-0203 — Stored ActorBaseData level getter is separate from skill-XP accumulation (EV-0688–EV-0689)

In GOG AE 1.6.1179.0, Actor::GetLevel loads the actor's base-form pointer and forwards the TESActorBaseData subobject to a helper that reads its 16-bit actorData.level field. Only the flagged PCLevelMult path scales from Player level and applies bounds [EV-0689]. The resolved PlayerCharacter skill-progress routine instead tracks per-skill progress and a separate cumulative character-level XP value, then dispatches a skill-level event. The resolved event listener updates a misc statistic; the bounded LevelUpMenu apply helper refreshes thresholds/attributes and reads GetLevel for display/profile processing without a direct store to the level field [EV-0689].

Q87 later identifies `FUN_1401d7ba0` as the field setter and a threshold-gated StatsMenu update path to it [EV-0691]–[EV-0693]. The getter input is still separate from the accumulator as a field, but the pending progress pair can be advanced by skill XP and later consumed by the UI update. The exact player action and relative order to attribute acceptance remain unresolved; EV-0688 is secondary UESP grounding only, and GOG RVAs do not transfer to Steam. Claim CL-L475.

## M-0204 — Hit-earned armor skill points enter the shared Player skill-progress path (EV-0690)

In the captured GOG AE 1.6.1179.0 HitData receiver path, the unblocked Player branch selects armor skill 11 or 12 and calls vtable byte offset +0x7b8 (slot 0xF7) with the calculated points. The exact PlayerCharacter slot target is FUN_140739050 [EV-0674]; its positive-points branch reaches FUN_14077d090 [EV-0221], the skill-progress/threshold routine mapped in EV-0689. That routine adds a separate cumulative character-level XP value [EV-0689]. This establishes a GOG static causal connection from the bounded armor skill award path into general skill and character-XP progression [EV-0690].

The captured source path does not prove an ordinary incoming live hit, effective protection, a qualifying zero-XP result, Steam equivalence, or when the Player GetLevel field changes. EV-0694 further identifies the same PlayerCharacter+0x9b8 progress object at the skill-award input and at the StatsMenu threshold check; see M-0206. The connection is to XP routing, not to the armor mitigation result itself. No bounty outcome follows. Claim CL-L476.

## M-0205 — StatsMenu update checks pending level progress and writes stored Player level (EV-0691–EV-0693)

GOG FUN_14077d630 compares the two floats behind the Player's level-progress pointer and returns true when the threshold is due. FUN_14077d650 then emits `UILevelUp`, reads Player GetLevel+1, and calls FUN_1401d7ba0, which stores the halfword at TESActorBaseData+0x10 [EV-0691]. Its bounded UI caller FUN_1409611e0 is RTTI-identified as StatsMenu::ProcessMessage at slot 4; pinned CommonLib identifies message type 0 as `kUpdate` [EV-0692]. The same function passes the global Player's +0x9b8 progress pointer into the predicate/writer and performs additional UI-state gates.

The StatsMenu factory registration maps the string `StatsMenu` to FUN_14096e280, which obtains an instance through the UI manager and calls constructor FUN_1409607f0 [EV-0693]. Correction: FUN_140960d40 is a cleanup/destructor path called by the vtable's first-entry wrapper FUN_14096df50; EV-0692's constructor attribution to that body was mistaken. The RTTI identification and ProcessMessage slot mapping remain supported.

This bounds a menu-update threshold writer outside the resolved ConfirmLevelUpAttributeCallback body. It does not show whether the `kUpdate` occurs before or after the player action that counts as accepting a pending level, nor does it establish the untyped registration paths for other direct level writers or Steam behavior. Claim CL-L478.

## M-0206 — Hit-earned armor skill XP can feed the StatsMenu level threshold (EV-0690–EV-0694)

The Player receiver's positive worn-armor skill points reach PlayerCharacter slot 0xF7 and FUN_140739050; that target passes PlayerCharacter+0x9b8 to FUN_14077d090 [EV-0690]. The skill-progress helper mutates the accumulated-progress float at the start of the inner progress object [EV-0689]. StatsMenu's kUpdate handler loads the same global Player+0x9b8 pointer, and its threshold helper compares the same inner float pair before calling the stored-level writer [EV-0691], [EV-0692]. The pointer/dataflow cross-check is retained in EV-0694.

This is a GOG-only static causal chain from positive HitData-derived armor skill points to level progress and, when the threshold is due and a StatsMenu kUpdate runs, to the field read by GetLevel. The update is a separate stage; no same-frame live event is observed. This does not establish physical protection with zero armor XP, a natural level-one quest start, the exact pending-versus-acceptance order, or Steam behavior. Claims CL-L476 and CL-L479.


## M-0207 — Data-driven per-item armor-rating cache adjustment (EV-0696–EV-0697)

In GOG AE 1.6.1179.0, the PlayerCharacter cached armor-factor visitor computes an equipped non-clothing item's candidate rating, calls the Actor entry-point visitor with selector `0x55` and a pointer to that float, reloads the value, and adds it to its cache accumulator [EV-0311], [EV-0696]. CommonLib source identifies selector `0x55` as `kModArmorRating`; the handler dispatch is through each entry's DATA handler ID, separate from EPFT's function-data class [EV-0681], [EV-0683].

The official five-master screen contains three SetValue-zero and 28 positive Multiply rows. Native MGEF records link Dragonhide and Earth Stone effects to their corresponding zero-setting perks; Earth Stone's selector-0x55 row is conditioned on `HasMagicEffect(ArmorFFSelf100) == 0` in the serialized CTDA [EV-0697]. This supplies a source-backed candidate route for zeroing an item contribution in the cache. It does not establish ActiveEffect/perk lifetime, condition evaluation timing, profile winners, final protection, or runtime invocation.

Cross-domain assessment: the cache callback and the later hit-earned armor-skill route are distinct code/data paths in the currently mapped GOG findings. No causal edge from this cache adjustment to zero AV11/AV12 is supported here; test the HitData points field and raw-DNAM eligibility separately in Q-0090. Steam matched-hit/protection/raw-AVSK evidence remains under EV-0260. Claims CL-L481–CL-L482.


## M-0208 — HitData mitigation field is distinct from the armor XP points input (EV-0670, EV-0690, EV-0699)

In the captured GOG AE 1.6.1179.0 HitData route, `FUN_1407ddf50` copies the current `+0x50` value into `+0x54`, then performs later target-side AV39/armor-factor reduction on `+0x50` [EV-0699]. The unblocked Player resolver separately scans worn ARMO items for positive raw DNAM rating; after selecting armor AV11 or AV12 it passes the `+0x54` field as the points argument through PlayerCharacter vtable slot `+0x7b8` [EV-0670], [EV-0690], [EV-0699]. The captured bodies do not directly dispatch selector `0x55` on this points field [EV-0696], [EV-0699].

This is a bounded static ordering: `+0x54` is pre target-side AV39/armor-factor reduction, but it is populated after earlier builder modifiers and later shared-field scaling can occur. It does not show that the award is positive on every hit, or that zeroing the cached armor rating leaves armor itself protective. Q91 screens earlier selectors; EV-0260 remains the Steam landed-hit/protection/raw-AVSK test. Claim CL-L484–CL-L485.


## M-0209 — conditional Deft Movement zero before the armor-points snapshot (EV-0221, EV-0699–EV-0701)

In the GOG AE 1.6.1179.0 builder path, selector `0x24` is dispatched against HitData `+0x50` before the current value is copied to `+0x54` [EV-0699]. The official Skyrim.esm DeftMovement PERK row uses selector `0x24`, handler 3 / Multiply Value, and EPFD 0.0; native xEdit decodes a random-percent condition plus worn Light Armor conditions, with record-level Light Armor/perk conditions [EV-0701]. The PlayerCharacter UseSkill wrapper checks that points are strictly greater than zero before the skill-progress helper [EV-0221]. Therefore a successful Deft Movement application is statically predicted to pass zero points to that guard and skip progress for that proc [CL-L487].

This is a conditional cross-source mechanism inference, not a Steam or runtime observation. A zero-damage proc does not demonstrate positive armor-provided protection, and the record does not establish a level-one route or repeated zero XP across qualifying hits. The other official zero rows are tied to non-player actors/content in the bounded raw reference census [EV-0700]. No prize edge to OBJ-2 is added. Claims CL-L486–CL-L487; Q91.


## M-0210 — award-side skill-use transformation precedes skill progress storage (EV-0221, EV-0262, EV-0703–EV-0704)

In GOG AE 1.6.1179.0, the PlayerCharacter UseSkill wrapper rejects non-positive points, then calls `FUN_14077d090` [EV-0221], [EV-0703]. The helper reads the skill AVIF's AVSK coefficients, conditionally forms `useMult * points + offsetMult`, dispatches selector decimal 22 / hex `0x16` (`kModSkillUse`) against the float, and adds the returned credit to the per-skill progress field before the threshold loop [EV-0700], [EV-0703]. This is an award-side control point downstream of the captured HitData points argument, distinct from the armor mitigation path.

The five-master source screen gives Heavy/Light use multipliers 3.8/4.0 with zero offsets; all eight official EntryPoint 22 records have positive amounts and the targeted Heavy/Light rows are positive 1.20 multipliers [EV-0262], [EV-0704]. No zero-capable source is established in this scoped layer. This does not exclude optional plugin records, runtime state, unqueried native routes, or a separate source mechanism. No effective armor protection or zero raw AVSK result is claimed. Claims CL-L488–CL-L489; Q92.
