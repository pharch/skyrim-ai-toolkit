# Contradictions and Competing Models

Historical source claims are retained as competing models. The assessments below record the source report's current view, not a fresh test in this setup.

## C-LEG-0001 — Tied alchemy ordering and item class

- **Model A:** ingredient or insertion order controls the first matched hostile flag and therefore potion/poison classification.
- **Model B:** a stable cost-sorted matcher determines class; apparent order changes reflect a different recipe or hidden state.
- **Source:** `EV-0003`, `EV-0025`, `EV-0094`, `EV-0107`, user-reported context in `EV-0041`.
- **Current legacy assessment:** static preview/commit analysis keeps both open; commit effect order and dynamic item flags are required.
- **Discriminant:** same ingredients in both selection orders; capture dynamic ENIT and ordered EFIT before consuming.

## C-LEG-0002 — Beneficial effect under negative Poison Resistance

- **Model A:** poison item class plus effect flags/archetype can scale a beneficial effect.
- **Model B:** beneficial effects bypass resistance; observed changes reflect another effect or route.
- **Source:** `EV-0003`, `EV-0026`, user-reported context in `EV-0041`.
- **Current legacy assessment:** source user report/static flags favor scaling for specific cases only; no universal rule.
- **Discriminant:** matched effect as potion and poison, with positive/negative resistance controls and isolated application.

## C-LEG-0003 — Deadload timer versus cleanup queue

- **Model A:** finite effect timers advance during the buffer while cleanup is missed.
- **Model B:** the boundary is primarily an input/load-worker queue; elapsed time does not explain the retained state.
- **Source:** `EV-0003`, `EV-0027`, `EV-0028`, `EV-0075`–`EV-0078`, `EV-0105`.
- **Current legacy assessment:** static analysis favors a queue/load boundary, and a historical user report says game time freezes during deadload. That report weakens expiry-inside-deadload models but has no raw trace here. A direct `RemoveSpell` inverse and a separate MGR21 save/revert mismatch remain hypotheses; neither is the same as finite timer expiry.
- **Discriminant:** compare timer, source, membership, and functional payload at first load and after a second save/load.

## C-LEG-0004 — Weakness-to-Poison Peak stacking

- **Model A:** null/non-Keyword associated forms prevent Peak-chain collision.
- **Model B:** magnitude differences make a normally superseded effect visible.
- **Source:** `EV-0003`, `EV-0025`, user-reported context in `EV-0041`.
- **Current legacy assessment:** static key analysis favors A; magnitude-separated controls remain required.
- **Discriminant:** same-key Fortify and null-key Weakness effects at equal and separated magnitudes; record instance membership and raw values.

## C-LEG-0005 — Armor XP redirect versus zero total XP

- **Model A:** a blocked physical hit skips Heavy/Light Armor awards but may credit Block.
- **Model B:** a blocked hit awards no skill XP when the selected Block points are non-positive.
- **Source:** `EV-0020`, `EV-0021`, `EV-0036`, `EV-0037`.
- **Current legacy assessment:** ordinary blocked points may be positive; a negative-resistance route is only a static candidate. “No armor XP” and “no skill XP” remain distinct.
- **Discriminant:** capture hit flags, physical and total damage, AV9/11/12 calls, and raw AVSK deltas under a verified control/candidate pair.

## C-LEG-0006 — Simplified Shift Kit arithmetic versus measured cleanup model

- **Model A:** the root summary's signed-magnitude overflow and illustrative float32 ULP calculation directly predict the residual for a candidate item pair.
- **Model B:** float32 aggregation can leave a residual, but its sign and amount depend on effective source magnitudes, source identity, operation order, and cleanup values; the root arithmetic is only illustrative.
- **Source:** `EV-0040`, `EV-0005`, `EV-0014`.
- **Current legacy assessment:** the detailed mechanism report supports float32 aggregation as a numeric primitive and explicitly requires raw values/order. The root summary's exact numeric examples are not independently reproduced and must not be treated as a current-build prediction.
- **Discriminant:** capture raw ActorValue bits and each source's applied/cleanup magnitude at every equip/unequip boundary on the verified target.

## C-LEG-0007 — Float32 cleanup operand and observed slot delta

- **Model A:** `+0x94` is the Recover cleanup operand.
- **Model B:** cleanup adds the negated current effective magnitude through the actor modifier path; `+0x94` is updated afterward with the observed slot delta.
- **Source:** [EV-0057].
- **Current legacy assessment:** the later static report explicitly corrects Model A. Its float32 residue values remain modeled predictions and do not establish player-reachable same-slot writers.
- **Discriminant:** on a verified build, capture the exact modifier source, effective magnitude, aggregate bits, cleanup argument, and post-cleanup `+0x94` value.

## C-LEG-0008 — Finite potion cleanup versus a persistent timer bypass

- **Model A:** a reachable non-finite timer or expiration-bypass writer lets a useful alchemy effect avoid native finish and Recover cleanup.
- **Model B:** finite alchemy effects finish through native cleanup before Papyrus callbacks; no ordinary official writer for the proposed non-finite/bypass state was found in the audited scope.
- **Source:** [EV-0058], [EV-0078], [EV-0079], [EV-0096]–[EV-0099].
- **Current legacy assessment:** static reports support synchronous cleanup and did not identify an ordinary writer; a zero-duration ingredient still finishes at elapsed zero, the scanned record flag does not bypass expiry, and no official Dispel caller was identified. Transformation does not clear arbitrary potion effects. Fresh GOG EV-0279 finds base Update/Finish stubs and confirms that base SaveGame/LoadGame persist timer and identity fields, but it does not identify the outer expiry dispatcher or functionally test cleanup after load; it neither proves nor falsifies the proposed bypass. This remains a scoped static negative, not proof that no writer exists in all AE load orders.
- **Discriminant:** verify the executable and full active order, then trace a concrete ordinary writer and compare effect source, flags, timer, and raw ActorValue before/after finish and save/load.

## C-LEG-0009 — “Confirmed” mixed-poison delivery versus missing route evidence

- **Model A:** the old candidate index and poison domain summary describe a confirmed hostile-first Fortify Destruction route with follower/frenzy delivery.
- **Model B:** the linked result and later inventory establish only a historical hostile-first classification observation; exact recipe, resistance amplification, dynamic item state, delivery, and XP budget remain unverified.
- **Source:** [EV-0090], [EV-0091], [EV-0053], [EV-0056].
- **Current legacy assessment:** the “confirmed” labels are historical status text and are not supported as a reproduced exploit by the available report set. Preserve the disagreement; do not upgrade the candidate.
- **Discriminant:** on a verified target, test both ingredient orders, capture dynamic ENIT/EFIT, then record the exact ordinary follower/frenzy delivery and raw resistance/effect/skill deltas against controls.

## C-LEG-0010 — Speech “confirmed” label versus unlogged user observation

- **Model A:** the source root state calls Speech success without skill XP a confirmed exploit.
- **Model B:** the detailed Speech report describes an unlogged user observation after temporary Speech removal, with no save, form, timing, or raw AVSK delta.
- **Source:** [EV-0092], [EV-0068], [EV-0069].
- **Current legacy assessment:** static selection/result ordering supplies a plausible mechanism, but the source does not preserve an instrumented reproduction. The root status label is not runtime proof.
- **Discriminant:** repeat one specified dialogue family on a verified target while recording the selected INFO, effective Speech at selection and result, raw AVSK before/after, and source-effect lifecycle.

## C-OBJ1-DA14 — One DA14 level gate versus another start check or entry route

- **Model A:** the explicit DA14 level predicate is evaluated at `DA14QuestStartNode`; the screened `DA14Start`/`DA14` quest conditions and linked dialogue contain no later `GetLevel` predicate.
- **Model B:** a later or repeated level check exists outside the scanned records, or a player-accessible route can reach a distinct DA14 start transition without passing the Story Manager node.
- **Source:** [EV-0108], [EV-0212]–[EV-0216], [EV-0264].
- **Current assessment:** the official-five-master scan supports Model A for the resolved DA14Start path: stages 30/50 start the Sam scenes, the scenes advance the same quest at 40/60, and stage 70 hands off to DA14 stage 5. The Dragonborn QUST property `DA14Gleda` points to DA14 alias 3, but its script body was unavailable, so it neither establishes nor excludes a distinct start route. VMAD array decoding, non-VMAD/native writers, the active profile, and live level-one behavior remain unresolved.
- **Discriminant:** recover and inspect `DLC2DialogueRavenRockQuestScript` from a supported identified source, finish candidate owner decoding, then compare any distinct ordinary route with a clean level-one control while capturing actual DA14/DA14Start running state and stage. Console or injected-state forcing is diagnostic only.


## C-OBJ2-ARMOR-GATE — Positive damage guard belongs to attacker-side call

- **Model A (legacy attribution):** the strictly positive `[RSP+0xA0]` comparison gates the receiver's AV11/12 armor award.
- **Model B (fresh GOG disassembly):** that comparison gates the earlier attacker-side UseSkill call; its JBE target is the receiver/player check. The receiver branch separately selects armor AV11/12 and supplies `[RSP+0xA4]`, which is then checked by the PlayerCharacter points guard.
- **Source:** [EV-0036], [EV-0217]–[EV-0223].
- **Current assessment:** Model B is supported by the GOG 1.6.1179 instruction flow at 0x1406bcce6, 0x1406bcd72, 0x1406bcd78 and 0x1406bcf00. The two stack values remain distinct; the exact live HitData/UseSkill arguments and outcome require instrumentation.
- **Discriminant:** on the exact target build, log receiver identity, `[RSP+0xA0]`/`[RSP+0xA4]` or their mapped HitData fields, selected AV, points and raw AVSK deltas for unblocked, blocked and non-positive points cases.

## C-OBJ2-ARMOR-POINTS-VERSUS-MITIGATED-DAMAGE — Receiver points source and later clearing

- **Model A:** the unblocked AV11/AV12 points argument uses post-mitigation `totalDamage`, so AV39 and armor-factor reductions directly determine armor-skill points.
- **Model B:** the ordinary default and alternate hit-data paths snapshot `totalDamage` into `physicalDamage` before AV39/armor-factor mitigation, and the receiver uses that separate `+0x54` field. A distinct conditional helper can later clear both damage floats.
- **Source:** [EV-0217], [EV-0222], [EV-0223], [EV-0261], [EV-0285]–[EV-0287].
- **Current assessment:** Model B is supported for both captured builder paths. The receiver loads `physicalDamage` at HitData `+0x54`; the mitigation helper changes `totalDamage` at `+0x50` afterward. A conditional `FUN_1407dda40` path performs an 8-byte zero store across both fields before receiver routing, yielding zero points independently of the normal mitigation formula. The condition consumes attacker `middleHigh->doNoDamage`, then clears HitData when the attacker is not in combat or `AIProcess::ignoringCombat` is set. This is a whole-hit cancellation state, not evidence of useful armor protection. The only observed direct setter xref capable of passing true is `FUN_14048a5b0`, which reads bit 1 from parameter slot 7 and is reached from a High/MiddleHigh process-gated action-data callback. The slot schema and callback dispatch remain unknown, so this does not establish an ordinary attack route. No Steam runtime or AVSK result exists.
- **Discriminant:** resolve the callback table consumer and parameter slot-7 schema from a tested static route; only consider a runtime candidate if this proves a naturally reachable qualifying incoming hit, then require a matched protection control and raw AVSK capture on the exact verified target.

## C-OBJ2-BASE-DNAM-VERSUS-EFFECTIVE-RATING — Armor XP eligibility under zero displayed rating

- **Model A:** current effective/displayed armor rating gates the unblocked Heavy/Light XP route, so reducing rating to zero suppresses the award while protection remains.
- **Model B:** a positive base DNAM on a worn ARMO is the equipment eligibility check; changing current effective/displayed rating alone does not remove AV11/12 selection.
- **Source:** scoped GOG hit-resolution evidence [EV-0222]; bounded untrusted private lead and its source pointers [EV-0283].
- **Current assessment:** Model B is supported for the GOG AE 1.6.1179.0 source: the hit receiver scans worn ARMO entries for positive base rating before selecting AV11/12. The private report that a displayed-zero Heavy item still gained XP is consistent but is not an independent, build-verified test. Neither model has a Steam 1.6.1170.0 runtime comparison, and no protection result is measured.
- **Discriminant:** on the verified target, compare the same positive-DNAM item at normal and zero effective rating under matched qualifying hits; capture the selected AV, raw `UseSkill` points, AVSK progress, and damage/protection. Test a true zero-DNAM item only if a separate defensive effect can be measured.


## C-OBJ2-WICAST-PLAYER-TARGET — WICast event R2 versus separate Player alias

- **Model A:** a natural WICast CAST event fills R2 with PlayerRef and its quest path causes a player AV39 change.
- **Model B:** WICast's Player-conditioned R1 is the casting actor; R2 is nominally the spell target, but may not fill (the indexed event documentation says `akSpellTarget` always returns None), and the inspected fragments do not apply a spell to the Player alias.
- **Source:** [EV-0229], [EV-0230], [EV-0234], [EV-0241], [EV-0244]; the MFD effect candidate is [EV-0224]–[EV-0226].
- **Current assessment:** Model B is better supported as an interpretation of the record/API pairing: R1 is inferred to be the caster and R2 the nominal target, with a documented target-None caveat. WICast appears to be a player-cast response, not evidence of an MFD writer on the player. This is secondary API documentation plus record inference; actual event payload, alias fill, and player AV39 remain unobserved.
- **Discriminant:** in a natural eligible event, capture caster, target, spell, location, alias fills, and raw player AV39. If no verified live observer is available, keep the WICast candidate narrowed and screen independent AV39 writer paths; do not force casts/effects.

## C-OBJ2-DV-MFD-WORDS-AV39 — MFD word forms versus actual Drain Vitality payload

- **Model A:** the Drain Vitality-labelled Dawnguard shout that reuses MFD word forms also applies MFD's AV39 damage-resistance MGEF to its target.
- **Model B:** the shout records reuse MFD word FormIDs but link to custom Drain Vitality SPELs, whose captured effect lists contain Health, Magicka, Stamina, Script-archetype, and stagger effects rather than MFD MGEF `0010319D`.
- **Source:** untrusted private lead and revision-cited UESP pages summarized in [EV-0273]; direct installed-source SHOU/SPEL/MGEF captures [EV-0273]; MFD AV39 record candidate [EV-0257].
- **Current assessment:** Model B is supported for the three captured Dawnguard SHOU/SPEL records. This narrows that particular early-MFD-labelled path, but does not explain acquisition, the Script-archetype effect, live target, profile overrides, or other spell writers. It does not decide WICast's natural CAST/R2 behavior and adds no edge to armor protection or armor XP.
- **Discriminant:** compare the full winning record graph and inspect the Script-archetype implementation; if the live path is later available, capture the acquired shout/spell, target, ActiveEffects and raw AV39. Do not infer a target or runtime effect from the shout words or label.

## C-TOOL-HARNESS-BASELINE — Prior all-clear summary versus later validator findings

- **Model A:** the retained harness readiness summary and EV-0211's `READY` report with 204 passing tests describe the current checkout state.
- **Model B:** those are dated baselines; later changes exposed repository-validator findings and one fixture failure in EV-0260, while current EV-0274 only rechecks strict Python and research-state validation.
- **Source:** [EV-0211], [EV-0260], [EV-0274], and `docs/HARNESS_READINESS.md`.
- **Current assessment:** Model B is the safe current reading. Strict Python and transaction/evidence validation pass now, but the full repository validator and test suite are unresolved for the changed ledger. EXP-0024 did not rerun tests; the readiness summary now separates prior suite status from current checks.
- **Discriminant:** a future explicitly authorized full repository/test validation after ledger metadata updates; until then, do not describe the whole current checkout as all-clear based only on the strict dispatcher and research-state validator.

## C-OBJ1-HAKNIR-BOOK-START — Deathbrand book before versus after level gate

- **Model A:** reading an outside-Barrow copy invokes a direct Start/SetStage path that starts `DLC2dunHaknirTreasureQST` before its `GetLevel >= 36` Story Manager node.
- **Model B:** all identified official-record start/stage routes remain level-gated: the LEVL helper descends from the `>=36` Story Manager node, DLC2Init tests the same min-level global before setting main-Q stage 10, and the book callback requires main-Q stage 20. The misc quest only reads stage 20.
- **Model C:** a dynamic/native writer, uninspected archive source, or active-profile override bypasses these record/Papyrus gates.
- **Source:** [EV-0233]–[EV-0240], [EV-0270], [EV-0271].
- **Current assessment:** EV-0270 recovered the book PEX and resolved main-Q stage 90 -> `StartBattlePhase(0)` -> Haknir enable/combat. EV-0271 then traced both identified stage-10 writers: the LEVL helper is downstream of the gated SMQN node, and DLC2Init stage 100 calls main-Q `SetStage(10)` only when Player `GetLevel >= GLOB 02024004` (36.0 in the installed record). The book requests stage 1 only after stage 20 is done; the misc quest does not start or advance main Q. This supports Model B within the inspected official-master and PEX scope, weakens Model A, and leaves Model C and runtime behavior open. UESP revision 3547873 is secondary grounding only ([EV-0238]).
- **Discriminant:** the static audit of identified sources is bounded. A remaining test needs a verified target/profile, disposable clean level-one save, and a read-only method for numeric player level, main-Q running/stage state, and Haknir enabled/dead state, followed by a matched level-36 control. EV-0260 lacks these prerequisites and the staged Observer does not capture Story Manager state. Console, forced stage, injected scripts, or altered plugins are diagnostic only.

## C-OBJ1-HAKNIR-DEATH-STAGE — Haknir death callback versus pre-gate reachability

- **Model A:** an ordinary level-one route enables and reaches Haknir before the level-36 Story Manager event; his `OnDying` call then requests main quest stage 100 and may start the stopped quest.
- **Model B:** the only identified actor enable is main-Q stage 90, and all inspected routes to main-Q stage 10 are gated; the book and misc quest do not provide a pre-stage-20 writer.
- **Model C:** an uninspected runtime/native/profile route enables or reaches the placed actor independently.
- **Source:** [EV-0231]–[EV-0234], [EV-0245], [EV-0246], [EV-0270], [EV-0271].
- **Current assessment:** the actor and scimitar are placed in the Barrow, and the alias is initially disabled. EV-0270 maps stage 90 `Fragment_23` to `Alias_Haknir.StartBattlePhase(0)`; that phase moves/enables the actor and begins combat, while `OnDying` requests stage 100. EV-0271 identifies two external main-Q stage-10 writers and shows both remain behind a 36-level test. This supports Model B for the examined chain, but does not prove that the main quest starts or fills aliases from those writes, rule out all other actor enables, or establish a level-one death. The Papyrus `SetStage` reference does not prove this exact quest bypasses the separate level condition or fills aliases. No runtime transition was observed.
- **Discriminant:** a clean level-one test must capture numeric level, main-Q running/stage state, and Haknir enabled/dead state through a verified read-only route, with a level-36 control. EV-0260 lacks the save/profile/state-observer prerequisites; no stage/level forcing is a vanilla validation.

## C-OBJ2-AV39-CLAMP — Generic ActorValue clamp versus AV39 survival

- **Model A:** the AV39 value used to build hit damage passes through `GetClampedActorValue` with metadata selecting a zero lower bound, so a negative AV39 state cannot produce non-positive blocked-hit points.
- **Model B:** the damage path reads an unclamped/raw or differently bounded AV39 value, so a negative value may survive into HitData construction.
- **Source:** [EV-0249], [EV-0252]–[EV-0257], [EV-0261]; blocked receiver formula and positive-points sink are [EV-0220]–[EV-0223].
- **Current assessment:** a generic GOG getter reads ActorValueInfo flags at `+0x60` and contains a zero-floor path, but AV39's exact flags and the hit-construction caller are unresolved. The direct-call audit found one dynamic AV index caller with no local AV39-excluding bound; its three data references have unresolved record and dispatch semantics, with no exact-address users in the analyzed project. The MFD MGEF is a Value Modifier for AV39, and Update marks it Detrimental, but its aimed spell delivery and the bounded official reference screen do not establish an ordinary player-target route. All four other shout references are INFO conditions checking equipped-shout dialogue state, and the NPC_ scan has no direct shout/spell references ([EV-0256], [EV-0257]). This neither selects Model A nor Model B. The Steam AVIF record has no DATA clamp range in the direct parser capture. No GOG RVA is transferred to Steam.
- **Native correction:** EV-0258 shows the previous decimal-index-20 probe selected CommonLib slot `0x14` (`Start`), not slot `0x20` (`ModifyActorValue`). The corrected effect path can update a generic target's ActorValue; OnAdd conditionally flips magnitude using MGEF Detrimental bit 2 versus ActorValueInfo bit 9. AV39 bit 9, effective sign, and a natural PlayerRef route remain unresolved. This does not select Model A or Model B.
- **Initialization screen:** EV-0259 finds no direct `+0x60` write in the bounded GOG `ActorValueInfo` Load/ClearData/InitItemImpl bodies and no `DATA` subrecord among installed official-five-master AVIF records. The generic base-load route retains indirect dispatch, so this narrows the source search without determining AV39 bit 9. It neither selects Model A nor Model B and adds no edge from the generic clamp/effect path to HitData, protection, or XP.
- **Hit-builder call site:** EV-0261 shows the GOG resistance pass calls the virtual `GetActorValue` entry with AV39, then combines that result with `GetArmorBaseFactorSum` to reduce HitData total damage before blocked-hit bookkeeping. It does not directly call `GetClampedActorValue` at that site. This weakens a direct clamp-call account but cannot rule out a clamp inside the unresolved concrete virtual method or an upstream value path; neither model is selected.
- **Discriminant:** establish AV39's ActorValueInfo bit 9 and the read feeding HitData, then identify a natural player-targeted application of MFD (or another negative writer). Alternatively, capture raw/effective AV39 plus physicalDamage and totalDamage on the exact verified target. A positive armor-protection control and raw AVSK measurements remain prerequisites for EXP-0013.

## C-OBJ1-DA14-STAGE-406 — Pre-gate trigger versus interior quest route

- **Model A:** REFR `00000EC8` is reachable through an ordinary level-one route and its `DA14.SetStage(406)` property starts or advances the stopped quest before the level-14 helper.
- **Model B:** the trigger is inside `DA14Interior`; its only screened XTEL link targets a persistent, initially-disabled Morvunskar portal reference, and the portal marker/trigger chain is controlled by defined DA14 stage 135. Neither checked DA14 QUST defines stage 406.
- **Source:** [EV-0212]–[EV-0216], [EV-0250], [EV-0251], [EV-0264], [EV-0275].
- **Current assessment:** Model B is supported for the examined portal chain. Both checked QUST files map `Fragment_53` to stage 135, the PEX fragment enables alias marker `0003DC43`, and that marker is the XESP parent of the initially-disabled portal trigger `0003DC42`. The five-master raw FormID screen found no new direct record-level pre-gate MoveTo/Enable/start candidate. The Update.esm portal branch only removes portal objects after DA14 stage 200; the Dragonborn DA14 alias caller remains unresolved. The activation PEX `dunda14PortalScript` was not available in the tested Misc-BSA/loose scopes, so the actual portal callback and dynamic/native entry behavior remain unknown. A profile override and undefined-stage behavior remain open. No clean level-one trigger or quest-state transition was observed.
- **Discriminant:** inspect the portal PEX from an identified supported source if available; screen independent official-script and native start/MoveTo/Enable writers, then test a clean level-one save with complete order and read-only quest-state capture. Do not force the stage, cell, or level.

## C-OBJ2-EP22 — Award-side skill-use modifier versus armor suppression candidate

- **Model A:** an official PERK `Mod Skill Use` entry could reduce an armor/Block skill award independently from HitData mitigation.
- **Model B:** the bounded official EP22 records conditioned on AV9/11/12 have positive 1.20 multipliers; the separate 0.05 entry is constrained to Enchanting at a Dragonborn staff furniture object.
- **Source:** [EV-0262]; mitigation source order is separately traced in [EV-0261].
- **Current assessment:** Model B is supported for the screened entries. The record layer does contain award-side skill conditions, but none observed here suppresses Block or armor credit. This does not establish whether EP22 modifies skill credit during an incoming-hit route, nor whether any owner is player-reachable. No causal edge connects these PERKs to HitData protection.
- **Discriminant:** trace the exact-build EP22 invocation through the receiver skill progression call and, if a reachable candidate appears, measure raw AVSK alongside effective armor mitigation on matched hits. The current live observer/profile prerequisites remain unavailable in [EV-0260].

## C-OBJ2-BLOCKED-PROTECTION — Armor-factor source order versus useful protection on a blocked hit

- **Model A:** the GOG player hit builder obtains the PlayerCharacter armor-base-factor value and applies its factor before setting the blocked flag; blocked receiver routing therefore does not itself bypass that earlier calculation.
- **Model B:** the stored factor may be zero/ineffective for the selected worn armor, later damage/block reductions may dominate, or the candidate may incur an unacceptable AV9/level-budget cost; source order alone may not satisfy OBJ-2.
- **Source:** [EV-0261], [EV-0263], [EV-0222], [EV-0221].
- **Current assessment:** Model A is supported for GOG 1.6.1179 source order. The PlayerCharacter slot returns an unnamed field at `+0x274`; its positive value and relation to a particular worn armor set are not measured. Model B remains unresolved for practical effect and skill budget. No installed-Steam live hit has been observed.
- **Discriminant:** run EXP-0017 only after EV-0260's exact profile/save/Observer prerequisites are satisfied. Compare same-attack unarmored and qualifying-armor blocked/unblocked hits, with HitData, effective damage reduction, AV9/11/12 UseSkill arguments, and raw AVSK deltas. Keep AV9 cost separate from armor XP.

## C-OBJ2-HIT-RESOLVER-COVERAGE — Bounded direct callers versus ordinary incoming attacks

- **Model A:** the tag-0xB continuation and Actor-state callback identify routes into the resolver family; the ordinary physical-hit producer may be one of them but is not yet identified.
- **Model B:** the captures establish only a tagged event-dispatch case and a state/process-gated Actor callback; the ordinary physical-hit producer and any other indirect routes are still unknown.
- **Source:** [EV-0291], [EV-0397].
- **Current assessment:** Model B is supported for the bounded caller evidence. `FUN_140659160` case 0xB passes an Actor and two event bytes to `FUN_1406bb690`; `FUN_140657a70` constructs tag 0x0B, and its sole captured caller `FUN_1406bb690` sends that event and returns when `FUN_1406d4110` is true, while the clear-gate path contains conditional `FUN_1406bcaa0` calls [EV-0442]. `FUN_1407ba3e0` separately uses an Actor slot-0x99 check and current-process target comparison [EV-0291]. The repeated table and attached data target do not identify that state-route owner. The tag-0xB continuation supports a static route into the resolver family, but neither it nor the separate state/process route is tied to an ordinary physical-hit producer. Effective protection and any AV11/AV12 award attempt remain unknown. This does not prove those routes are never used for ordinary attacks.
- **Discriminant:** trace `FUN_1407ba3e0`'s caller/source and arguments against the tag-0xB continuation to test whether either is an ordinary incoming-hit route; continue the exact worker census for other paths. Independently test the qualifying Steam incoming-hit/block path with positive effective protection and raw AV9/AV11/AV12 measurements once EV-0260 prerequisites exist.

## C-OBJ2-CLOTHING-FACTOR — Clothing XP exclusion versus protection-factor contribution

- **Model A:** at least one positive-DNAM Clothing ARMO contributes to the PlayerCharacter armor-factor value used by hit mitigation, while the GOG unblocked receiver skips subtype 2 when selecting Heavy/Light AV11/AV12. This could preserve armor protection without Heavy/Light hit XP.
- **Model B:** although positive-DNAM Clothing records exist and the receiver skips subtype 2, the code that populates the cached armor-factor field excludes Clothing or otherwise does not give it useful hit protection.
- **Source:** five-master ARMO/ARMA and candidate-reference screen plus separate-build GOG getter/receiver evidence [EV-0309], [EV-0222], [EV-0261]; separate Clothing resistance ENCH/MGEF and GOG CheckResistance evidence [EV-0398–EV-0402].
- **Current assessment:** the record-existence premise in A is supported: 36 unique prepared-master Clothing ARMO records have positive DNAM, and all screened linked ARMA records are Clothing. The GOG selector's class exclusion is supported. Neither model is selected for **physical armor-factor** protection: the getter returns cached `this+0x274`, and the field writers/item contribution remain unknown. Q-0074 adds a separate magic/element resistance candidate: ARMO 000FC061 has no physical DNAM rating but modifies AV44, and the mapped GOG Actor CheckResistance reads resistance ActorValues and effect ResistValue. This supports a source/code candidate outside the Heavy/Light selector, but it does not establish a live protected hit. `ClothesBeggarRobes` and Brenuin's outfit remain only physical-factor source leads. Steam protection and AVSK are unmeasured.
- **Discriminant:** keep mapping the physical factor-field writer and type branch on the same build. Separately, compare a naturally acquired AV44 clothing item with a matched unequipped control against qualifying magic/element hits on verified Steam AE 1.6.1170.0; measure damage, Heavy/Light AVSK, other skills, and level. A source/code candidate is not a measured protection result.

## C-OBJ1-DA07-PAMPHLET-ALIAS — Quest-owned pamphlet callback versus standalone book start

- **Model A:** obtaining or equipping the base Museum Pamphlet can fill or invoke DA07intro's alias callback before the level-20 Story Manager helper.
- **Model B:** the callback belongs to an ALCO alias created by DA07intro's stage-0 fragment; the base BOOK and inspected dialogue transfers do not create that alias or call SetStage.
- **Source:** [EV-0019], [EV-0265].
- **Current assessment:** Model B is supported for the bounded official-five-master/PEX screen. The alias script's stage-5 call is downstream of the quest-owned alias, and the base BOOK has no script attachment. This resolves only the pamphlet alias mechanism; the separate stage-7 REFR remains a candidate in C-OBJ1-DA07-INTRO-TRIGGER. No profile-specific or runtime negative is established.
- **Discriminant:** no further test of the standalone alias callback is warranted unless a new ordinary alias-fill/start writer appears; test the independent trigger only through a clean level-one natural route with quest/alias/scene state observation.

## C-OBJ1-DA07-INTRO-TRIGGER — Actor-pair exterior trigger versus gated helper

- **Model A:** Silus and Madena naturally co-enter REFR `000B1403` before level 20; its stage-7 SetStage starts DA07intro and the matching-alias scene progresses to stage 10.
- **Model B:** the actor pair does not co-enter the trigger before the helper, or SetStage/scene startup does not complete the quest path from a stopped quest.
- **Model C:** stage 7 changes quest state, but aliases or the scene fail to produce functional introduction/progression.
- **Source:** [EV-0019], [EV-0260], [EV-0266].
- **Current assessment:** the trigger/PEX path itself has no level predicate, but the bounded placement screen finds Silus initially disabled inside his house and Madena in the White Hall; the known stage-0 writer that enables/moves Silus is downstream of DA07intro startup ([EV-0267]). The ordinary actor-pair bootstrap model is disfavored for the screened initial state, not proven impossible: an alternate pre-gate start writer or player glitch may change the state. Exact Steam SetStage behavior and scene execution remain unobserved. The independent Museum-trigger clip path is tracked in C-OBJ1-DA07-MUSEUM-TRIGGER.
- **Discriminant:** retain a no-trigger control, then test ordinary travel without moving actors; separately test the Museum-trigger route only through a player-accessible house-entry glitch. Capture numeric level, both quests' running/stage state, alias fill, loaded 3D, and scene start/completion with read-only observation. EV-0260 records that the current save/profile/Observer prerequisites are absent.

## C-OBJ1-DA07-MUSEUM-TRIGGER — House artifact triggers versus level-20 quest setup

- **Model A:** a level-one player clips into Silus's house, enters one artifact trigger, and its SetStage starts DA07MuseumScenes; the Begin-on-Quest-Start intro scene completes and sets DA07intro stage 200 plus main DA07 stage 5.
- **Model B:** the museum quest starts, but the scene cannot complete while Silus's alias is unfilled/not loaded because Silus is initially disabled and the alias lacks Allow Disabled; the HasLoaded3D condition is the key scene gate.
- **Model C:** the trigger's SetStage does not start the stopped quest on the target runtime, or the stage-200/5 changes do not produce functional gated content.
- **Source:** [EV-0019], [EV-0260], [EV-0265], [EV-0268].
- **Current assessment:** static records confirm a separate player trigger path inside the house, no identified level condition on the trigger script, a scene flagged Begin on Quest Start, and completion fragments aimed at DA07intro/main DA07. Local UESP says the house is inaccessible until level 20. TES5Edit's XLOC schema decodes the interior door as level 255 (Requires Key) with KEYM 000960F0; the trigger centers lie 277.28–671.21 coordinate units from the door ([EV-0269]). The scene's HasLoaded3D run-on/alias target and exact alias-fill behavior remain unresolved. Geometry is only a route lead; the candidate is neither a confirmed bypass nor a negative result.
- **Discriminant:** identify a vanilla player-only way through the keyed door boundary using a collision-aware mesh route, then use a clean level-one control/candidate under the exact verified order. Capture the physical sequence, numeric level, DA07MuseumScenes running/stage, Silus alias fill and loaded 3D, intro/tapestries scene state, DA07intro running/stage, main DA07 state, and actual dialogue/quest progress. Do not use console, injected scripts, moved actors, or altered plugins. EV-0260 records missing profile/save/Observer prerequisites; EV-0269 records that the current WSL route lacks a general BSA/NIF reader and native xEdit still fails before SSEView.

## C-OBJ1-SETSTAGE-START — Conditional Quest.SetStage startup versus event scope

- **Model A:** The registered Papyrus `Quest.SetStage` callback can request startup before applying a stage when its entry and quest-state guards accept a stopped quest.
- **Model B:** An event-ID/ready-bit or internal-state guard can reject a stopped event-scoped quest outside its Story Manager context; `Quest.SetCurrentStageID` is a separate callback with its own event-ID guard and deferred-work path.
- **Model C:** A stage write or manager/reference initialization by itself proves the quest is running, aliases are filled, and level-gated content is functionally accessible.
- **Source:** secondary Papyrus API transcription [EV-0246], GOG AE 1.6.1179.0 traces [EV-0272], [EV-0289], registered callback and state-path capture [EV-0313], QUST loader/constructor trace [EV-0314], Haknir's caller predicates [EV-0271], source quest records [EV-0306], and runtime capability gap [EV-0260].
- **Current assessment:** Model A is supported conditionally for the GOG callback path. EV-0313 maps the SetStage literal/reference row to candidate `FUN_14034de90`, supported by the neighboring GetStage callback's matching method-name-to-callback offset and `GetStage` diagnostic. The accepted SetStage branch calls Address Library-mapped `TESQuest::EnsureQuestStarted` in start-now mode; one branch reaches `BGSStoryTeller::BeginStartUpQuest`, performs stage/reference initialization work, queues the quest in a manager list, then allows stage lookup and fragment dispatch. No explicit player GetLevel comparison appears in the inspected callback path. Model B is also supported as a guard limit: SetStage requires quest `+0xDC` bit 0 or event ID `-1`, with more internal predicates downstream. EV-0314 resolves the GOG/source field bridge: the TESQuest QUST parser stores serialized `ENAM` at `+0xE0`, the constructor default is `-1`, and DA02/DA09/DA06 source records carry `LEVL`. Thus a nondefault LEVL field plus clear ready bit fails the initial guard; a set ready bit can satisfy that predicate without proving later startup. Direct registration in `FUN_140a48e10` corrects the older EV-0272 identity: `FUN_140a48aa0` is `Quest.SetCurrentStageID`, and `FUN_140a48c50` is `Quest.Start`; EV-0272's event-ID/flag rejection and deferred queue result apply to SetCurrentStageID, not the registered SetStage callback. Model C remains unresolved because running-state, alias, journal/dialogue, and functional-access outcomes were not observed. All Steam 1.6.1170.0 field/runtime behavior remains separate and untested. The five-master QUST/DIAL/INFO screen found no external direct Ebony Warrior QUST reference beyond the recorded Dragonborn DIAL/INFO set; Haknir's identified stage callers retain `GetLevel >= 36`. No level-one transition or vanilla reproduction was observed.
- **Additional DA06 case:** main DA06 is an event-scoped `ENAM=LEVL` quest selected at level 9 with Start Game Enabled clear. The giant trigger does not start or stage it; Atub's INFO requests stage 50 and Orc/Atub death callbacks may request failure stage 255, but stopped-owner acceptance and alias availability remain unresolved [EV-0308]. The GOG wrapper trace remains a separate-build predictor, not Steam proof.
- **Discriminant:** on the exact verified Steam target and complete active order, observe clean level-one source-specific callbacks without forcing level, stage, event context, or aliases. Record numeric level, callback availability, quest running/stage, Story Manager context, aliases, journal/dialogue, and functional access; compare with ordinary controls. DA02's book and DA09's Gem/statue callbacks are high-value LEVL cases. EV-0260 records missing profile/save/Story Manager/alias Observer prerequisites, so continue static work independently.

## C-OBJ1-VQ01-BOOK-ALIAS — Main-quest-owned book callback versus a pre-helper bootstrap

- **Model A:** the placed base book or an already-filled alias provides an ordinary pre-VQ00 read/pickup route that starts VQ01 at stage 17.
- **Model B:** the callback is owned by VQ01's main-quest alias, the forced book reference is behind VQ01's own stage-10 marker enable, and pickup additionally checks VQ01 stage 15; no independent base-book callback is shown.
- **Source:** legacy owner report [EV-0019], corrected VQ01 record/PEX and placement screen [EV-0276], and SetStage startup scope [EV-0272].
- **Current assessment:** Model B is supported for record ownership, serialized properties and placement. `onRead` calls SetStage(17), but runtime alias fill, read reachability and stopped-quest startup on Steam 1.6.1170.0 remain unknown. Model A is not demonstrated; this is not a runtime negative or profile-winner claim.
- **Discriminant:** if a separate pre-stage-10 route to REFR `0200D072` or an independently filled VQ01 alias is found, test it on a clean level-one save with VQ01 running/stage/alias state observed. Otherwise retain the static result and investigate the independent Crypt02 stage-17 trigger under C-OBJ1-VQ01-STAGE17-TRIGGER.

## C-OBJ1-VQ01-STAGE17-TRIGGER — Crypt02 stage-17 trigger candidate versus gated access

- **Model A:** a player-only vanilla route reaches REFR `0200FB21` at level 1; its trigger requests VQ01 stage 17 and produces useful pre-gate progression.
- **Model B:** ordinary traversal beyond the entrance remains blocked by the quest-dependent rubble/puzzle path, while the stage-trigger/door records provide no independent pre-gate enable chain; a player-only collision route is still possible.
- **Model C:** the reference is physically reachable, but its generic script does not start a stopped quest or produces no useful progression; the script body and exact Steam behavior decide this separately from reachability.
- **Source:** bounded trigger/door records and failed stage-trigger PEX extraction [EV-0276], portcullis child/PEX screen [EV-0277], GOG-only SetStage trace [EV-0272], and live readiness boundary [EV-0260].
- **Current assessment:** the stage-17 reference remains a candidate because it serializes VQ01/stage 17 without an optional prerequisite property. Its generic trigger PEX, activation, physical route and player-only reachability are unresolved. The screened door refs set `0x400` Persistent, not `0x800` Initially Disabled, under the EV-0250 schema; they have no XESP parent, so their flags do not support an initially-disabled-door barrier. Local UESP revision 3586850 describes a quest-dependent rubble gate but does not establish collision geometry or exclude clipping. A separate portcullis child `02009742` is parented to marker `02017772`; its recovered generic activator toggles animation/linked collision but contains no quest-stage call [EV-0277]. EV-0282 decodes the child XESP flag byte as zero and its ACTI header `0x40000000` as Navmesh - Ground; the child and STAT parent both lack the Initially Disabled bit. This supports ordinary serialized parent-state inheritance but does not establish loaded enable state or collision traversal. No level-one bypass, VQ01 start, or stage transition was observed.
- **Discriminant:** the decisive access test requires the exact active order, clean level-one candidate/control, observed player route and cell, marker/child enable state, rubble crossing, trigger callback, VQ01 running/stage, alias fill, useful progression and numeric level. EV-0260 records the missing profile/save/Observer prerequisites. Continue static work independently; do not treat the generic portcullis PEX as evidence of a stage transition.

## C-OBJ1-DIMHOLLOW-MIN-LEVEL — encounter-zone summary versus entrance predicate

- **Model A:** UESP's Dimhollow `Min: 6` field is the encounter-zone level summary; it does not set a hard player-level entrance requirement.
- **Model B:** `Min: 6` is a hard entrance-level gate, or the local template/source does not distinguish that meaning.
- **Source:** raw Dimhollow page and Place Summary template/subtemplate, the linked Encounter Zone Level redirect and Dungeons Levels section, plus installed Crypt CELL-to-ECZN records [EV-0278].
- **Current assessment:** Model A is supported for the field's documented meaning. The template labels the value “Level” and links to Encounter Zone Level; that page redirects to Dungeons#Levels, whose revision 3575803 says minimum/maximum levels do not determine entry. Both Crypt cells reference ECZN `02004EE7`. This removes `Min: 6` as evidence of a hard gate, but says nothing about the quest-dependent rubble path, trigger reachability or runtime encounter behavior. UESP remains secondary; the local dump's completeness is unknown.
- **Discriminant:** if a separate record or reliable runtime observation shows an entrance check against player level 6, evaluate that gate independently from ECZN scaling. Any profile-specific or live claim requires EV-0260's exact target order and observer prerequisites.

## C-OBJ1-VQ01-PORTCULLIS-ENABLE — Parent inheritance versus serialized disable state

- **Model A:** child REFR 02009742 follows parent REFR 02017772 under ordinary XESP semantics; neither reference is marked Initially Disabled in Dawnguard.esm.
- **Model B:** the child reverses the parent's enable state or the child/parent REFR header marks it Initially Disabled.
- **Source:** direct-parser captures and TES5Edit dev-4.1.6 XESP/REFR schema decode [EV-0282], with the parent/child relationship and generic activator PEX in EV-0277.
- **Current assessment:** Model A is supported and Model B is falsified for these installed base fields: XESP Flags is zero, the ACTI child's 0x40000000 maps to Navmesh - Ground, and both the child and STAT parent have the Initially Disabled bit clear. The distinct names VQ01EnableMarker 02002F66 and DLC1VQ01LeverGateEnableMarker 02017772 must not be conflated. This does not identify a parent-state writer, profile winner, loaded cell state, collision route, or level-one passage.
- **Discriminant:** on the exact profile/build, observe the marker and child enable state across the ordinary VQ01 stage-10 setup, then observe portcullis activation/collision and player passage with a clean level-one candidate/control. EV-0260 records the missing exact-order save and Observer prerequisites.

## C-OBJ3-ENCHANT-CREDIT — Input-sensitive craft XP versus station-selected craft credit

- **Model A:** Enchanting progress varies with item value, soul size, or selected effect count, with quantized or rounded raw progress.
- **Model B:** A successful craft confirmation issues one station-selected `UseSkill` award with a fixed points argument; raw progress accumulates and may remain below the displayed skill threshold.
- **Source:** UESP revision 3538992 is an attributed one-base-XP/nonfactor statement [EV-0124]; fresh GOG callback/progress trace [EV-0280]; base Skyrim.esm workbench record and schema mapping [EV-0281].
- **Current assessment:** The GOG callback has one visible `UseSkill` dispatch site whose skill ID comes from `WBDT.usesSkill` and whose points come from one global float. The downstream helper accumulates a float progress value before a skill-level threshold check. This favors Model B at the visible callback boundary and narrows a direct item/soul/effect-count input formula. It does not identify the points value, quantify modifiers or rounding, validate UESP's numeric statement, map GOG code to Steam, or measure raw XP.
- **Discriminant:** On verified Steam 1.6.1170.0, capture raw Enchanting progress and its next threshold before/after matched one-craft item-value/soul-size controls and two identical crafts, holding the skill-use modifier state constant. A two-effect craft is a separate diagnostic control because the Extra Effect perk is not an ordinary level-15/20 baseline. The required disposable save and raw AVSK observation route are unavailable under EV-0260.

## C-OBJ1-EW-STORYMANAGER-LEVEL80-VERSUS-PROMPT — initial event gate versus downstream dialogue-only threshold

- **Model A:** the Ebony Warrior's level-80 predicate is evaluated on the initial CLOC Story Manager selection node, which selects the quest before the city alias stage.
- **Model B:** the level-80 requirement exists only as a later dialogue/approach prompt, after an independently available quest/actor path.
- **Source:** Dragonborn.esm CLOC SMEN/SMQN/QUST records, full INFO scan, attached PEX traces, and UESP revision 3580051 as secondary grounding [EV-0288], [EV-0134].
- **Current assessment:** Model A is supported for the inspected source path: `DLC2EbonyWarriorNode` contains `GetLevel >= 80` and has the Ebony Warrior QUST as its sole child; the QUST has Start Game Enabled clear and no `GetLevel` CTDA, and no function-80 condition appears in 4,421 Dragonborn INFO records. This falsifies the dialogue-only placement in Model B. Q-0029 found event-ID rejection in the two inferred GOG Papyrus start wrappers and no external direct QUST caller in the official QUST/DIAL/INFO scan. The link between the separate Steam CLOC record and GOG native guard remains an inference. Other record types, dynamic script paths, profile overrides, and runtime behavior are still open under Q-0030.
- **Discriminant:** inspect remaining actor/placement/scene/package and VMAD-bearing records for a configured start or independent placement path; test only under the exact target order with read-only quest/alias/level observation. Console-forced stages or injected scripts are diagnostic interventions only.

## C-OBJ1-DAWNGUARD-REQLEVEL-VS-ALT-START — level-10 metadata versus separate reported quest paths

- **Model A:** the level-10 threshold is attached to the Durak messenger/location helper, while guard rumor, Dayspring Canyon/Agmaer, or Fort Dawnguard interactions can separately begin or progress Dawnguard content below level 10.
- **Model B:** the level-10 threshold blocks actual Dawnguard quest transitions; alternate routes only reveal a rumor/journal marker or stage NPC behavior until level 10.
- **Source:** Dawnguard.esm SMQN `0200D911`, GLOB `0200D912`, QUST `0200D90B` and VQ00/VQ01 records, plus local UESP Dawnguard page revision 3603039 [EV-0298]; complete Dawnguard.esm SMEN/SMQN census [EV-0299]; joined DIAL/INFO/VMAD/PEX callbacks and native xEdit five-master QUST exports [EV-0326].
- **Current assessment:** The serialized level-10 predicate selects the Durak messenger/helper route, and the VQ00/VQ01 QUST conditions do not place a global level-10 gate on the main quest [EV-0298], [EV-0299]. EV-0326 adds a source-linked Fort dialogue route: start-enabled VQ00 advances through Durak dialogue, starts the Isran/Tolan helper path, and the helper's stage-180 fragment requests VQ01 stage 10 without a mapped `GetLevel` condition. This falsifies Model B's broad claim that every alternate path only reveals rumor/helper state in the captured official-source route. Model A is supported as a strong source-level candidate, but not yet as an executed level-one bypass: VQ01 is not Start Game Enabled, and actual stopped-quest startup from `SetStage`, dialogue availability, alias fill, useful Dimhollow access, Steam behavior and profile winners remain unobserved. The native xEdit scope is the fixed five official masters, not a selected profile. GOG EV-0313 provides separate-build conditional SetStage startup evidence and is not transferred to Steam.
- **Discriminant:** on verified Steam AE with the complete target order and a clean level-one save, compare an ordinary no-trigger control against guard rumor, Dayspring Canyon/Agmaer, and Fort entry. Capture numeric level; VQ00, helper and VQ01 running flags/stages; aliases; journal state; and Dimhollow access before and after each ordinary dialogue path. Repeat on a fresh save, without console or injected stage/script changes.

## C-OBJ1-STORYMANAGER-KNOWN-ONLY — three known gates versus additional official-master nodes

- **Model A:** DA14, the Dawnguard Durak helper, and Ebony Warrior exhaust serialized `GetLevel` selections in official-master SMEN/SMQN records.
- **Model B:** additional official-master SMQN records select distinct quests or helper quests through `GetLevel` predicates.
- **Source:** complete five-master direct-parser SMEN/SMQN census, source-context-aware same-origin FormID comparison, threshold/parent/child resolution, and versioned TES5Edit condition schema [EV-0300].
- **Current assessment:** Model A is falsified and Model B is supported within this five-file/signature scope: 15 function-index-80 conditions appear on 15 SMQN nodes, including 12 beyond the known three. The native xEdit DA07 query failed before process enumeration and does not alter that file-content result. No active-profile winner, other-signature/script/native completeness, or runtime selection follows. DA04's selected child is a Septimus helper rather than main DA04, making its ordinary alternate entry a separate question.
- **Discriminant:** inspect DA04's main QUST, Story Manager node, book and Elder Knowledge entry records for distinct low-level start/progression routes; then require a clean level-one transition with ordinary controls before calling it a bypass.

## C-OBJ1-DA04-LEVEL15-HELPER-VS-BOOK — courier helper gate versus main quest's ordinary book route

- **Model A:** DA04's >=15 Story Manager node gates main DA04's ordinary start/early progress; the reported book path depends on that helper or a separate level check.
- **Model B:** the node selects only the Septimus courier-letter helper, while main DA04 is Start Game Enabled and its fixed RuminationsBook alias starts the early main-quest stages without that helper.
- **Source:** five-master Story Manager mapping [EV-0300]; Skyrim.esm DA04/SMQN/helper/MQ205/BOOK/REFR/DIAL/targeted INFO records; decoded QUST VMAD and extracted PEX scripts [EV-0301]; TES5Edit `dev-4.1.6` QUST/VMAD schema.
- **Current assessment:** Model B is supported and Model A is falsified for the serialized initial-start and stage-1/5 book route. DA04's QUST DNAM includes Start Game Enabled; QUST alias ID 19 targets REFR `00032787`/BOOK `00032785`; its OnRead script calls DA04 `SetStage(1)`, and stage 1's Fragment_18 calls SetStage(5). The >=15 node selects the distinct courier helper. This remains source-level evidence, not a target-profile winner or clean level-one reproduction. Physical route availability, dialogue child coverage, alias fill, later progress and Steam runtime behavior are open.
- **Discriminant:** under a verified complete target order and fresh level-one save, compare an ordinary no-read control with reading the fixed book; capture numeric level and DA04 running/stage state before/after, without console forcing or script injection, and repeat.

## C-OBJ1-DA13-LEVEL12-VS-LEVEL10-REFUGEE — ordinary level-12 node versus alternate helper start

- **Model A:** DA13's level-12 SMQN is the only main-start path; the Afflicted Refugee only directs the player to Kesh after DA13 has begun, and shrine callbacks advance a running quest.
- **Model B:** the distinct WEJS14 level-10 encounter/dialogue path starts `Da13Intro`, whose scene/helper chain calls `Start()` on main DA13 below level 12.
- **Source:** Skyrim.esm SMQN/QUST/DIAL/INFO/SCEN records, full group-aware DA13 and WEJS14 topic joins, five-master raw FormID reference scan, and bound base-Misc PEX disassemblies [EV-0300], [EV-0301], [EV-0307].
- **Current assessment:** Model B is supported within the prepared official-record and captured base-Misc PEX scope. WEJS14 carries `GetLevel >= 10`; its Refugee alias dialogue sets WEJS14 stage 100, then the linked helper/scene fragments culminate in main DA13 `Start()`. This falsifies the claim that the level-12 node is the only serialized start route. It does not prove the level-10 event or alias executes live, establish level-one access, or resolve the unconditioned main-owned stage-21 INFO while DA13 is stopped. The Empty Vessel's stage-21 activator is initially disabled and the only identified enabler is main DA13's Kesh alias. The generic Orchendor alias PEX was not found through the tested base-Misc extractor. No active-profile winner or Steam runtime result was observed.
- **Discriminant:** on a verified Steam 1.6.1170.0 target with a complete disposable order, compare clean level-one and level-10 saves with ordinary no-trigger controls. Record numeric level, WEJS14/Da13Intro/DA13 running state and stages, and Refugee alias/encounter state before and after ordinary inputs. Do not force stages, inject scripts, or alter plugins. A separate stopped-owner dialogue observation is needed for INFO `000A1A65` and DA13 `SetStage(21)`.

## C-OBJ2-TRAP-DIRECT-ROUTE — Direct wrapper bypass versus hidden armor award

- **Model A:** ProcessTrapHit retains the common damage/armor calculation and routes to the receiver handler without traversing the known AV11/AV12 or AV9 skill-routing wrapper.
- **Model B:** an unresolved receiver virtual call or a deeper callback awards AV11/AV12, or the damage path fails to preserve positive damage and effective armor protection.
- **Evidence:** [EV-0334], [EV-0333], [EV-0332], [EV-0331], [EV-0330], [EV-0329], [EV-0328], [EV-0327], [EV-0325], [EV-0324], [EV-0293], [EV-0261], [EV-0294], [EV-0295], [EV-0315], [EV-0217]–[EV-0223].
- **Current assessment:** EV-0330 resolves only the AutoVanity type-0x17 HUD branch to Scaleform ShowElements, with no native skill sink; other cleanup descendants remain open. Model A is supported as a bounded GOG 1.6.1179.0 path comparison. EV-0327 resolves the PlayerCharacter global callback to PlayerCamera cleanup, which retains five indirect calls; the primary PlayerCharacter slot 0x98 also reads/clears +0x730, whose producer and dynamic type remain unknown. EV-0329 maps PlayerCharacter +0x9A0/+0x9A8 teardown to refcount-final virtual slot +0x8 and traces a resource-derived setter value, but the stored object's class/finalizer and AV11/AV12 descendants remain unresolved. EV-0332 traces a candidate +0x9D0 producer through a TES-owned cell/resource query; both returned-object branches remain dynamically untyped. EV-0333 traces the +0x9A0/+0x9A8 producer through a data-selected model-resource adapter, but its loaded root and finalizer remain unresolved. EV-0334 maps +0x730 as a scene-child attach/detach candidate through NiNode methods; actual parent table and child finalizer remain unresolved. Model B remains unresolved because the main receiver has 28 indirect sites and teardown descendants remain open; no matched live Steam result exists.
- **Discriminant:** map descendants tied to FUN_1406b9df0 for AV11/AV12 sinks, then test the exact Steam 1.6.1170.0 profile/save for positive hit damage, effective protection, and raw Light/Heavy Armor AVSK before/after. No debug forcing validates a vanilla exploit.

## C-OBJ2-HAVOK-ISLAND-TYPE-BOUNDARY — island owner type label versus adjacent field names

- **Model A:** the table owner is `hkpSimulationIslandAndEntity`, as the earlier EV-0359 note read the adjacent bytes.
- **Model B:** the referenced type-name is `hkpSimulationIsland`; `EntityPtrs` and `ConMstPtr` are following field labels.
- **Source:** table and caller capture [EV-0359], full table, direct type-name address/decompilation, serializer fields, and paired displacement scans [EV-0362].
- **Current assessment:** Model B is supported for the referenced name boundary. FUN_1400d8fe0 passes address 0x1419775b0 to FUN_140a98d50, whose decompilation prints `hkpSimulationIsland` and size 0xb8. EV-0359's prior combined label is superseded. The table's entity/constraint array schema is supported, but whether the exact ProcessTrapHit instance occupies it remains unresolved.
- **Discriminant:** trace the selected entity pointer from FUN_140b678a0/FUN_140b43a20 into the island EntityPtrs list and its per-entity ConMstPtr records. If static identity cannot be resolved, keep the owner route as a candidate and use the exact Steam matched hit/armor/raw-AVSK experiment.

## C-OBJ2-HAVOK-OFFSET-SCAN-CAP — full displacement count versus truncated access output

- **Model A:** completed whole-program +0x60/+0x68 counts plus no printed 0x140b candidate show the island entity-list fields have no writers in that code range.
- **Model B:** the query prints only the first 2,048 accesses; those lines stop before 0x140b, so writer status there is unknown.
- **Source:** GOG scan outputs and completion/output-cap markers [EV-0362], plus the exact `accessOutputLimit = 2048` source and corrected raw-output audit [EV-0363].
- **Current assessment:** Model B is supported. The full access totals are 14,003 and 8,295, but the visible lists are capped at 2,048 and writer-function details are separately capped. EV-0362's earlier no-writer statement is withdrawn. No field-writer negative is established.
- **Discriminant:** trace the exact selected entity and constraint from FUN_140b678a0/FUN_140b43a20 into EntityPtrs and ConMstPtr, or run a targeted query that returns the relevant writer functions with complete receiver lineage.


## C-OBJ2-Q64-CONSTRAINT-OWNER-FIELD — constraint +0x10 versus endpoint +0x130 and record fields

- **Model A:** constraint +0x10 points to selected endpoint/entity owning its +0x100/+0x108 record.
- **Model B:** constraint +0x10 receives endpoint +0x130; endpoint +0x100/+0x108 and instance +0x60 are separate record relations.
- **Source:** exact attach body [EV-0360], typed island initializer, endpoint insertion, EntityPtrs serializer reference and merge body [EV-0364], with type/serializer context [EV-0362].
- **Current assessment:** Model B is supported for mapped static code. Island initialization/serialization match +0x60/+0x68 EntityPtrs; insertion writes endpoint +0x130; merge repairs endpoint +0x130 and constraint +0x10. EV-0360's earlier description is corrected. Live membership, callback population and AV11/AV12 remain unknown.
- **Discriminant:** capture exact endpoint/constraint identities during verified Steam positive damage and effective protection; measure raw AVSK. Static GOG RVAs do not substitute for runtime observation.


## C-OBJ2-Q64-CALLBACK-OFFSET-ALIAS — same-offset data fields versus callback array

- **Model A:** FUN_140b91bb0 writes at +0x40/+0x48 and therefore populates hkpConstraintInstance callbacks.
- **Model B:** those writes target a separately allocated constraint-data payload passed into the instance at +0x18; the callback array remains constructor-initialized empty in the direct creation path.
- **Source:** complete constructor caller census, argument mapping, and exact factory caller body [EV-0365], with callback consumer/initializer baseline [EV-0358].
- **Current assessment:** Model B is supported for the FUN_140b91bb0 candidate. No post-constructor callback-field write appears in the direct FUN_140ecdfc0 body. Wrapper virtual slots +0x128/+0x188 remain unresolved, so callback emptiness is not established beyond the mapped body.
- **Discriminant:** resolve the exact fixed/malleable wrapper slot tables and inspect producer-backed writes to the exact instance +0x40/+0x48.

EV-0366 confirms the wrapper setup path itself does not directly write the exact callback fields. The apparent FUN_140b91bb0 +0x48 decompilation store comes from one 16-byte machine copy at +0x40, which covers payload bytes +0x40 through +0x4f; receiver ambiguity and later writers remain open [EV-0366].


## C-OBJ2-Q64-INSTANCE-DELETE-CALLBACK — finalization callback and armor skill progress

- **Model A:** at least one hkpConstraintInstance deletion callback reaches Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.
- **Model B:** the deletion entries perform constraint cleanup without armor skill progress.
- **Source:** exact slot-0 finalizer and callback-array consumer show a +0x18 virtual call on each non-null entry [EV-0367].
- **Current assessment:** neither model is selected. The entry class, producer, virtual target and ActorValue arguments are unresolved. The TtconDeletedCb trace tag does not identify the concrete target.
- **Discriminant:** resolve receiver-backed writers of the exact +0x40/+0x48 array, identify each entry vtable and slot +0x18 target, and trace its instance/ActorValue arguments to the skill sink.

## C-OBJ2-Q64-TRAP-INSTANCE-LIFETIME — factory release and deletion callback timing

- **Model A:** FUN_140ecdfc0's immediate release reaches terminal count and dispatches slot 0.
- **Model B:** wrapper association increments the new instance, so the immediate release only balances the temporary reference.
- **Evidence:** constructor count 1, wrapper enable reaches FUN_140a89da0, then factory calls FUN_140a89e60 [EV-0365, EV-0366, EV-0368].
- **Assessment:** Model B is supported for this handoff; later release routes remain unresolved.
- **Discriminant:** trace later world releases with exact receiver and count to test reachability of FUN_140b674a0.

## C-OBJ2-Q64-HKP-OFFSET-RECEIVER — same-offset writer candidates

- **Model A:** selected hkp-region +0x40/+0x48 candidates populate the exact hkpConstraintInstance deletion callback array.
- **Model B:** the same offsets belong to other Havok receiver layouts.
- **Evidence:** exact constructors/vtables identify curve and constraint-data classes for six queried candidates [EV-0369].
- **Assessment:** Model B is supported for those six only. The 1,271-function intersection and remaining writer candidates are unresolved.
- **Discriminant:** continue exact receiver/caller checks and trace a concrete instance callback registration path.

## C-OBJ2-Q64-CHAIN-CALLBACK-ENTRY — chain callback descendants

- **Model A:** a removal or deletion callback entry on the chain subtype reaches Actor::UseSkill with AV11/AV12.
- **Model B:** callback entries only perform constraint cleanup.
- **Evidence:** exact chain virtual routes reach entry slots +0x10 and +0x18 on the inherited array [EV-0370].
- **Assessment:** neither model is selected; callback entry class, target and arguments are unknown. ProcessTrapHit ownership of the chain object is also unproven.
- **Discriminant:** trace the chain factory's incoming callers, then identify exact callback writers and resolve both entry slots.

## C-OBJ2-Q64-CHAIN-OWNER — chain factory ownership

- **Model A:** the chain factory or its table owner is reached from the ProcessTrapHit cleanup route.
- **Model B:** the queried pointer window belongs to a separate Havok chain helper path.
- **Evidence:** the factory has no analyzed direct incoming calls; its pointer-window bases have zero references; the differing index-2 helper initializes an object labeled hkBallSocketChainCinfo [EV-0371]. The mapped ProcessTrapHit route reaches ordinary hkpConstraintInstance construction [EV-0365, EV-0366].
- **Assessment:** neither model is selected. The captures establish no exact owner or cross-route call edge; zero Ghidra xrefs do not rule out runtime indirect dispatch.
- **Discriminant:** resolve the table owner or the exact callback writer and receiver on the ProcessTrapHit object before connecting these paths.

## C-OBJ2-Q64-WRITER-48150 — +0x40 writer candidate

- **Model A:** FUN_140b48150 populates the hkpConstraintInstance callback pointer/count.
- **Model B:** it writes a vector in separate constraint-data storage.
- **Evidence:** exact machine code uses a 16-byte MOVAPS at receiver +0x40, callers allocate 0xe0-byte objects and pass the result as hkpConstraintInstance data at +0x18 [EV-0372, EV-0365].
- **Assessment:** B is supported for the captured callers. Other callers or candidates are not classified by this result.
- **Discriminant:** inspect the next receiver-backed candidate's exact write width and constructor path.

## C-OBJ2-Q64-WRITER-49260 — typed record candidate

- **Model A:** the decompiler's +0x40/+0x48 pair is the hkpConstraintInstance callback pointer/count.
- **Model B:** the machine instruction writes one 16-byte vector in a typed record managed by a separate list.
- **Evidence:** type tag 0x1b, 0x50-byte allocation, MOVAPS at +0x40, and recipient list/counter operations [EV-0373].
- **Assessment:** B is supported for the queried path. Concrete class and ProcessTrapHit ownership remain unresolved.
- **Discriminant:** resolve an exact unresolved teardown indirect call and its receiver/target instead of inferring from same-offset candidates.

## C-SYN-OBJ1-OBJ2-DA04-HITDATA — quest state and armor skill route

- **Model A:** DA04 book-read/start state shares a causal engine call or state field with ProcessTrapHit armor mitigation or skill progress.
- **Model B:** the mapped DA04 and physical-hit paths are independent; shared generic callback/event names are analogy only.
- **Evidence:** DA04's ordinary book-read SetStage path [EV-0301]; HitData mitigation and trap-handler route [EV-0261, EV-0324]; bounded constraint callback ownership [EV-0365–EV-0373].
- **Assessment:** B is supported for the paths examined. No exact shared call, ActorValue, HitData field, or serialized state is identified [EV-0374].
- **Falsifier:** an exact shared native/data edge or a controlled clean runtime trace where changing DA04 state changes trap mitigation or raw AVSK without intervention.

## C-OBJ2-Q64-REMOVE-CALLBACK — constraint detach callback

- **Model A:** the ProcessTrapHit-associated detach path performs constraint/endpoint bookkeeping without armor-skill progress.
- **Model B:** a populated remove callback reaches Actor::UseSkill with AV11/AV12.
- **Evidence:** the exact factory instance reaches the +0x10 remove-callback dispatcher and endpoint record compaction; the callback target remains virtual and unresolved [EV-0375]. Constructor and wrapper setup evidence shows empty callback fields initially but does not exclude later population [EV-0365, EV-0366].
- **Assessment:** A is supported for the direct mapped body; B remains possible through an unresolved populated callback. Neither Q64 hypothesis is selected globally.
- **Falsifier for A:** producer-backed callback receiver/vtable and argument evidence that reaches the AV11/AV12 skill-progress sink.

## C-OBJ2-Q64-IDEMPOTENT-LISTENER-OWNER — candidate add helper callsite

- **Model A:** FUN_140b56a80 registers a listener on the ProcessTrapHit-selected manager.
- **Model B:** its data references are unrelated to the captured ProcessTrapHit route.
- **Evidence:** the direct-call census finds zero analyzed direct callers; the qword and metadata references lack an identified code consumer or owner [EV-0376]. The ProcessTrapHit dispatcher path is separately mapped [EV-0360].
- **Assessment:** neither model is selected. No exact manager argument or executable callsite is established; indirect use remains possible.
- **Discriminant:** a producer-backed callsite must pass the same manager argument used by FUN_140b43a20 to support Model A.

## C-OBJ2-Q64-SLOT-B8-CALLSITE — world listener method target

- **Model A:** a +0xB8 callsite invokes the constructor-attested hkpWorld slot 23 listener-registration method on the ProcessTrapHit manager.
- **Model B:** same-offset callsites dispatch to unrelated dynamic interfaces.
- **Evidence:** the displayed physics-range callsites resolve to a broadphase-shift object path and a cyclic-blend transition generator; neither exact query identifies the world table or manager [EV-0377].
- **Assessment:** neither model is selected. The scan prints only 2,048 of 2,747 accesses, and exact receiver tables remain unknown.
- **Discriminant:** a producer-backed hkpWorld receiver and exact manager argument at a concrete callsite supports Model A.

## C-OBJ1-Q66-SETSTAGE-START — VQ01 Fort SetStage startup

- **Model A:** the mapped Fort dialogue's SetStage(10) request conditionally starts stopped VQ01 before setting the stage.
- **Model B:** an event/state/readiness or required alias/reference preflight rejects the start or leaves it incomplete.
- **Evidence:** the fixed five-master route reaches VQ01.SetStage(10) outside the separate level-10 helper [EV-0326]; the GOG callback calls EnsureQuestStarted before stage application [EV-0313, EV-0380]; VQ01's source/constructor inputs satisfy the initial observed predicates [EV-0379, EV-0381]; the dynamic data-driven alias/reference preflight can fail required entries [EV-0382].
- **Assessment:** Model A is supported at the bounded callback/initial-guard level. Model B remains possible at helper preflight and runtime completion. Neither establishes a Steam AE level-one start or functional access.
- **Discriminant:** clean level-one Steam test with no-trigger control; read-only verification of quest running state, stage, all required aliases, and actual Dimhollow access while preserving numeric level 1.


## C-OBJ1-Q69-TIF-STAGE-RECEIVER — TopicInfo stage receiver

- **Earlier model:** TIF__00095585 directly requests main DA05.SetStage(20), based on its separate `DA05` quest property.
- **Corrected model:** the TIF calls `TopicInfo.GetOwningQuest().SetStage(20)`. The API returns the quest owning the TopicInfo; INFO 00095585 is under DIAL 00095582, owned by helper QUST 000955CF. Helper stage 20 maps to Fragment_2, which kills alias Hunter00_JKier and requests main DA05.SetStage(60). The TIF separately writes DA05.PlayerTalkedToHunter.
- **Evidence:** native INFO/DIAL/QUST owner and alias fields, QF stage-fragment maps, and the TIF/helper/main QF disassemblies [EV-0391], [EV-0393]. Papyrus API description: https://papyrus.bellcube.dev/skyrimse/script/topicinfo/function/getowningquest/ .
- **Assessment:** corrected source receiver and requested main stage are supported. Whether the INFO is available before main DA05 stage 50, and how Steam AE starts a stopped quest from this callback, remain unresolved.
- **Discriminant:** clean level-one pre-stage-50 no-contact control followed by natural INFO interaction with read-only capture of both quest states, alias 57, actor state, callback result, and player level.

## C-OBJ1-Q70-CAVE-IDENTITY — WE13's “Troll Cave” label

- **Model A:** `LevelGateTrollCave` denotes a fixed physical cave whose entrance, cell, or troll reference is part of WE13's source placement.
- **Model B:** the name labels a level-gated encounter selector; WE13 binds its actors to a Story Manager event reference and nearby WETravel markers, while ordinary cave trolls occupy separate world locations.
- **Evidence:** WE13 QUST 0009F32F uses event-filled TRIGGER/location aliases, linked travel markers, and creates EncTroll at TravelMarker1 without a fixed cave/cell/door alias [EV-0395]. The local Troll page describes multiple wilderness and underground settings and uses cave troll as a generic term [EV-0396].
- **Assessment:** Model B is supported within the exact QUST record and the cited secondary page; Model A is rejected only for that record's alias/spawn definition. Neither physical cave access nor a global alternate start path is established.
- **Discriminant:** inspect any independently proposed cave's exact official-master entrance/cell route, then on a clean numeric level-one Steam state separately observe traversal, WE13 running/stage state, aliases, actors, and player level. Runtime prerequisites remain unavailable under EV-0260.

## C-OBJ2-Q79-HIT-CONSUMER — `FUN_1406b9df0` structure and route identity

- **Model A:** the tag-0x10 path copies the HitData fields consumed by `FUN_1406b9df0` and re-enters the shared handler with the actor and copied context.
- **Model B:** when another guarded thread is active, the tag-0x10 route sends copied handler fields through the serialized worker and returns; event case 0x10 can re-enter the same handler. This is a deferred/serialized continuation candidate, with final side effects still unknown.
- **Evidence:** `FUN_1406bcaa0` conditionally calls `FUN_1406b9df0` with a mapped HitData object after its player skill-routing block, and dispatcher `FUN_140659160` case 0x10 calls the handler with an actor and event-data pointer [EV-0430], [EV-0302], [EV-0222]. The tag-0x10 builder clones its second argument through `FUN_1407dce10`; that helper copies offsets 0x50/0x54/0x5c/0x80 consumed by `FUN_1406b9df0`, and case 0x10 passes the clone to the handler [EV-0429], [EV-0431]. `FUN_1406d4110` checks the global state gate and whether other TLS-associated bits are set; it appears at 131 sites from 106 unique caller functions [EV-0432]. `FUN_1406d41c0` atomically sets/clears the current thread's bit, and several callers restore prior membership after their work [EV-0434]. The global mask has 29 references across eight nearby functions [EV-0433]. Worker `FUN_14065b800` waits for its reentrant global lock and calls `FUN_140659160` if an event callback does not consume the event [EV-0423]. Separately, `FUN_1406563b0` uses the same gate to send tag 0x42 [EV-0435]. Tag 9 has four callers, several gated on the same predicate; dispatcher case 9 routes the payload through virtual slot +0x210 or `FUN_140668f50`, and one captured caller `FUN_1407e7f00` contains a separate HitData-handler branch [EV-0437], [EV-0397].
- **Assessment:** Model A is supported for copied fields and direct re-entry. Model B is supported for the static other-thread gate, early-return tag-0x10 path, per-thread bit bracketing and worker serialization. The tag-0x42, tag-9 and tag-0x3B routes show the gate is reused outside the tag-0x10 hit candidate [EV-0435], [EV-0437], [EV-0439]. EV-0438 resolves that the tag-9 event and constructed-HitData handler call are alternate branches within `FUN_1407e7f00`; direct method identity, flag meanings, runtime branch and relationship to ordinary hits remain unknown. `FUN_140657980` builds tag 0x51 without captured direct callers, and `FUN_1406579f0` builds tag 0x53 from two callers under unresolved predicates [EV-0440], [EV-0441]. EV-0442 finds a tag-0xB producer among the subsequently reviewed callers and supports a gated continuation through `FUN_1406bb690` into conditional `FUN_1406bcaa0` calls; this rejects H2's “no tag-0xB producer” model for the full set but does not establish ordinary-hit coverage. Fourteen of 62 initially uninspected callers are reviewed; 48 remain. The source of `FUN_1407ba3e0`, runtime scheduling and whether re-entry reaches normal hit side effects remain unknown. This does not show XP suppression, Steam behavior, or an armor-XP bypass.
- **Assessment:** Model A is supported for copied fields and direct re-entry. Model B is supported for the static other-thread gate, early-return tag-0x10 path, per-thread bit bracketing and worker serialization. The tag-0x42, tag-9 and tag-0x3B routes show the gate is reused outside the tag-0x10 hit candidate [EV-0435], [EV-0437], [EV-0439]. EV-0438 resolves that the tag-9 event and constructed-HitData handler call are alternate branches within `FUN_1407e7f00`; direct method identity, flag meanings, runtime branch and relationship to ordinary hits remain unknown. `FUN_140657980` builds tag 0x51 without captured direct callers, and `FUN_1406579f0` builds tag 0x53 from two callers under unresolved predicates [EV-0440], [EV-0441]. EV-0442 finds a tag-0xB producer and supports a gated continuation through `FUN_1406bb690` into conditional `FUN_1406bcaa0` calls; this rejects H2's “no tag-0xB producer” model for the full set but does not establish ordinary-hit coverage. EV-0443 finds a separate static `FUN_1407ba3e0` route: after a virtual `+0x4c8` test it compares a process field at `+0x5d0` with `*param_3` and calls `FUN_1406bb690`, but it has no analyzed direct callers and only two DATA references without source-function identity. Its registration and relation to ordinary hits remain unknown. Fourteen of 62 initially uninspected worker callers are reviewed; 48 remain. Runtime scheduling and whether re-entry reaches normal hit side effects remain unknown. This does not show XP suppression, Steam behavior, or an armor-XP bypass.
- **Discriminant:** inspect the data contexts surrounding the two `FUN_1407ba3e0` references to identify a registration owner, then continue the exact 48-function worker review. Later inspect dispatcher callback consumption and observe a clean Steam hit with positive protection and raw AV9/AV11/AV12/AVSK values under EV-0260.
- **EV-0443–EV-0446 update:** the first corrected data cell has no function or xrefs [EV-0445]. The second cell has two DATA references from instructions in `FUN_1407c3400` [EV-0446], making it a candidate table consumer/initializer, not yet a proven callback registration. Inspect that function before assigning the structure's role. Ordinary-hit coverage remains open.
- **EV-0447 update:** `FUN_1407c3400` allocates a 0x10-byte object and stores the labeled `HitFrameHandler::vftable`; `FUN_1407ba3e0` is the next 8-byte entry (slot 1) [EV-0447], [EV-0443]. This makes a hit-frame-related class a plausible source family, but class naming and slot position alone do not prove ordinary enemy-hit initiation or AV11/AV12 effects. Next verify the vtable RTTI and inspect sibling methods as needed.
- **EV-0448 update:** RTTI at vtable RVA `0x18bae08` resolves to `.?AVHitFrameHandler@@` [EV-0448], independently confirming the class identity. This strengthens the hit-frame lead while leaving exact event semantics and ordinary-hit/armor-XP outcomes open. Next read slot 1 directly and inspect sibling methods only if they discriminate the source.
- **EV-0449 update:** direct slot lookup confirms `HitFrameHandler` slot 1 at address `0x1418bae10` resolves to `FUN_1407ba3e0` at GOG RVA `0x7ba3e0` [EV-0449]. This confirms the static dispatch-table relation, not its runtime call source or ordinary-hit behavior. Inspect sibling virtual slots if they expose a discriminating path.
- **EV-0450–EV-0452 update:** the apparent table boundary at entry 2 is RTTI for a separate complete `AnticipateAttackHandler` vftable at entry 3, not a HitFrameHandler sibling segment [EV-0451]. `FUN_1407c2320` allocates 0x10 bytes and stores that table but has no analyzed direct callers [EV-0452]. The initial secondary-segment hypothesis is falsified; no ordinary-hit, protection, AV11/AV12, or armor-XP link is established.
- **EV-0453 update:** `FUN_140657ab0` builds tag 0x0D from an Actor-like state/update caller that uses the shared virtual +0x4c8 predicate and `FUN_1406d4110` gate; the gate-clear branch may call `FUN_140712d10` [EV-0453]. This resembles the separate tag-0xB callback route at a control-flow level, but no shared HitData input or ordinary-hit meaning is mapped. Compare dispatcher case 0x0D and the gate-clear handler before drawing a cross-route edge.
- **EV-0454 update:** queued case 0x0D dispatches to `FUN_140712d10(object[0x1f], object)`, the same target as the gate-clear path in `FUN_1405cd570` [EV-0453], [EV-0454]. This is a separate immediate dispatcher target from tag 0x0B's `FUN_1406bb690`, although a deeper callee relationship remains untested. Trace `FUN_140712d10` before deciding whether the tag-0xD route touches HitData or armor XP.
- **EV-0455 update:** `FUN_140712d10` has 18 outgoing direct calls and one indirect site; its complete direct-edge list contains no call to `FUN_1406b9df0`, `FUN_1406bb690`, or `FUN_1406bcaa0` [EV-0455]. It calls `FUN_1406c21c0`, whose descendants remain open, so this is a bounded direct no-edge rather than proof about every indirect or transitive route. Continue through that state handler before closing the tag-0xD screen.
- **EV-0456 update:** `FUN_1406c21c0` has 38 direct calls, three indirect sites and 31 direct callers; its body creates `TESActionData`/`BGSActionData` and calls actor/process action helpers, with no direct edge to the mapped HitData/tag-0xB functions [EV-0456]. Across the inspected direct path from tag 0x0D through this broad action/state routine, no direct HitData/XP link is found. Indirect sites and deeper descendants remain open; the next exact worker caller is `FUN_140657b50`.
- **EV-0457 update:** tag 0x0E is selected by `FUN_1407bc3a0` when a virtual process query returns 1 or 2 and dispatcher case 0x0E routes its object to `FUN_1407136e0` [EV-0457], [EV-0454]. This is a distinct status-selected route, not evidence that it shares the tag-0xD gate or the tag-0xB HitData continuation. Competing handler models remain: a route into HitData/armor skill use, or a process/action handler with no direct hit edge. Trace `FUN_1407136e0`; no causal edge to HitData, protection, AV11/AV12, or XP is currently supported.
- **EV-0458 update:** `FUN_1407136e0` has 15 direct outgoing calls, five indirect sites, and four incoming caller functions. Its complete direct-call scan contains no edge to the mapped HitData/tag-0xB functions, while its decompiled body handles Actor/process state and calls virtual methods plus `FUN_1406653a0` [EV-0458], [CL-L272]. This supports the process/Actor-state model only for the direct body. `FUN_1406653a0`, indirect targets and deeper behavior remain open, so H15 (downstream HitData/skill route) is not falsified; no causal edge to protection or armor XP is supported.
- **EV-0459 update:** `FUN_1406653a0` has zero direct call edges and a single direct caller, `FUN_1407136e0`; its flag check conditionally tail-jumps through receiver vtable slot +0x530 [EV-0459], [CL-L273]. This keeps the tag-0x0E HitData/skill model open through unresolved virtual dispatch while narrowing the route to field +0xCC high bits 0x20/0x80. The virtual target's class and implementation remain the discriminating evidence; no ordinary-hit, protection, or armor-XP outcome follows.
- **EV-0460/EV-0461 update:** the `AVActor` literal scan found 35 byte-substring matches and zero analyzed string references; one candidate address query at RVA 0x203CDB8 found zero xrefs and no exposed type bytes/name [EV-0460], [EV-0461]. The candidate is not verified as an Actor type descriptor or receiver vftable. This fails to identify the +0x530 target but does not falsify its existence or the downstream HitData/skill model; no causal hit, protection, or armor-XP edge is added.
- **EV-0462/EV-0463 update:** primary `.?AVActor@@` table RVA 0x189EC20 slot 0xA6 (+0x530) resolves to `FUN_140665140` [EV-0462]. Its body updates field +0xCC state bits and calls action/process helpers; the complete 17-edge scan has no edge to the mapped HitData handler family [EV-0463]. This strengthens the base Actor process/action model, but the second table reference and runtime receiver class remain unknown, so a derived override or descendant is not excluded. H15 remains unresolved; no ordinary-hit, effective-protection, AV11/AV12, or armor-XP result follows. The verified worker census resumes at `FUN_140657b90` with 45 of 62 initially uninspected callers left.
- **EV-0464–EV-0466 update and count correction:** `FUN_140657b90` builds tag 0x55 under shared thread-mask gate `FUN_1406d4110`; worker case 0x55 re-enters the same `FUN_1406e5da0` Actor/process update routine [EV-0464], [EV-0465]. Its 31-edge direct scan has no edge to mapped HitData handlers, but 17 indirect sites and actual worker re-entry gate state remain open [EV-0466]. This provides another non-hit-specific use of the same gate already seen on tag 0x10 and other event families; a worker tag or thread gate does not establish ordinary-hit or armor-XP behavior. EV-0462/EV-0463 were vtable/body research rather than worker callers; the count after EV-0464 is 17 reviewed and 45 remaining, correcting the earlier overcounts in the 10:15 and 10:20 transaction notes. Continue with exact caller `FUN_140657bc0`.
- **EV-0467–EV-0470 cross-system synthesis:** tag 0x0F is produced by an Actor/process update branch under the same shared gate, then dispatches to `FUN_140713a20` and `FUN_140725340`; the latter's bounded body handles collision/position state and calls a Havok linear-cast wrapper that names `TtworldLinCast` and constructs `hkpWorldLinearCaster` [EV-0467]–[EV-0470]. This supports a process/physics route that is distinct from tag 0x0B's HitData resolver route. The reviewed direct edges contain no mapped HitData call, but unresolved indirect/downstream behavior prevents a transitive no-hit conclusion. Do not equate movement collision contacts with incoming combat hits. The 18/62 count includes this builder only; EV-0462/EV-0463 are not callers. No effective-protection, AV11/AV12, armor-XP, or OBJ-1 causal edge is added.
- **EV-0471/EV-0472 tag-0x14 continuation:** the 19th reviewed builder queues tag 0x14 from an entity-update loop under `DAT_14319a7c0` and state predicates, not the previously mapped `FUN_1406d4110` thread gate [EV-0471]. Dispatcher case 0x14 calls `FUN_1414a3950`; its direct scan contains no mapped HitData/ActorValue edge and hands the payload to `FUN_14021cd70` after TLS/thread-associated state work [EV-0465], [EV-0472]. This establishes two live hypotheses for the handoff: combat/skill descendants versus a state-only route. Trace the helper before preferring either. The current census is 19/62, 43 remain; no ordinary-hit, effective-protection, AV11/AV12 or armor-XP conclusion follows.
- **EV-0473 refines the tag-0x14 handoff:** `FUN_14021cd70` has one direct callee, `FUN_140cc8350`, and appends the payload to a BSTArray with a +8 refcount increment after successful insertion; eight caller functions include `FUN_1414a3950` [EV-0473]. This supports deferred reference storage for the immediate path, but the specific array consumers at `DAT_142034080+0x1c8/+0x1e0` are unknown. Do not collapse this to either a combat/skill route or a state-only route yet. The next discriminant is a producer-backed reader search for `DAT_142034080` at GOG RVA 0x2034080; caller census remains 19/62.
- **EV-0474 broad global-reference result:** the exact manager base `DAT_142034080` has 254 address xrefs across 168 deduplicated function labels, including three READ and one DATA references in dispatcher `FUN_140659160`, while the query does not resolve member offsets +0x1c8/+0x1e0 [EV-0474], [CL-L288]. The broad base address is not a discriminating consumer locator. Screen nearby method `FUN_1414a81f0`, which has five references to the global, as a hypothesis test only; its array-consumer status is unproven. No HitData/ActorValue or armor-XP edge is added.
- **EV-0475 nearby-method negative:** `FUN_1414a81f0` has a complete 56-edge direct scan and 17 indirect sites; its body references manager field +0x228 rather than +0x1c8/+0x1e0, and its direct list contains no mapped HitData/ActorValue handler [EV-0475], [CL-L289]. It calls generic BSTArray helper `FUN_14021cd70` twice with `param_3`, but the capture does not equate that pointer with the tag-0x14 array. This candidate does not resolve H19/H20. Resume the exact worker census at `FUN_140657d80`; the bounded candidate negative must not be generalized to all array consumers.
- **EV-0476 incoming-xref conflict:** the decompiled body of `FUN_140657d80` directly calls `FUN_14065b800` at `0x140657da7` and constructs tag 0x24, while the fresh incoming-call query reports zero callers and `XREF_CALL_EDGE=NOT_FOUND_IN_ANALYZED_PROJECT` [EV-0476]. EV-0423 also includes the builder in the original remaining-caller set. The direct body and inventory support retaining it as a worker caller; the query discrepancy remains unresolved and must not be used as a negative. Separately, dispatcher cases 0x24 and 0x25 share target `FUN_14065c6e0`, but pass differently constructed values [EV-0465]; their target semantics are unknown, not contradictory evidence of combat behavior.
- **EV-0479 recurring incoming-xref conflict:** adjacent builder `FUN_140657e40` also directly calls `FUN_14065b800` at `0x140657e6c` and appears in EV-0423's remaining list, but its fresh incoming-call scan again reports zero callers [EV-0479]. Together with EV-0476 this establishes recurrence for two inspected wrappers, not the cause or prevalence of the query behavior. Both bodies remain valid direct worker callers. Existing case 0x27 dispatch reaches the tag-0x24/0x25 target `FUN_14065c6e0` [EV-0477].
- **Tag-0x24/0x25 route boundary:** EV-0477–EV-0478 narrow the shared target to an event-derived +0x2c value update and entity/phantom broadphase overlap/filter branches, with no mapped direct HitData handler in the complete branch scans. The two/three indirect sites and deeper descendants remain open, so the bounded physics-state route does not resolve H21 or establish a system-wide/runtime no-hit result [EV-0477], [EV-0478], [CL-L291], [CL-L292].
- **EV-0482 fourth consecutive incoming-xref conflict:** `FUN_140657f70` appears in EV-0423's worker inventory and directly calls `FUN_14065b800` at `0x140657fa3`, but its fresh incoming scan again reports zero call xrefs [EV-0482]. This is the fourth consecutive inspected remaining-caller body with that discrepancy, following EV-0476, EV-0479, and EV-0480. A DATA reference lacks a source identity; neither the repeated query result nor that data row explains the cause or prevalence.
- **EV-0483 decompiler/instruction argument discrepancy:** `FUN_140e89260`'s pseudocode calls `FUN_140e898f0` with two arguments, while its captured disassembly loads the nonnull global callback pointer into R8 and passes the object in RCX and local record in RDX [EV-0483], [EV-0485]. The callee's decompilation uses the third callback-function argument [EV-0484]. Preserve both views as a static ABI/dataflow discrepancy; do not treat the omitted pseudocode argument as runtime null or absent.
- **Tag-0x3C route boundary:** the direct branch reaches a recursive object callback walker, and the resolved callback adjusts a returned object's reference count, but two node virtual targets and the callback's +0x98 target remain unresolved [EV-0483]–[EV-0487]. The bounded direct route has no mapped HitData/ActorValue call; this does not exclude deeper behavior or establish a runtime no-hit, no-XP, or effective-protection result.

## C-OBJ2-Q79-CALLER-XREFS — repeated zero incoming refs on inventoried builders

- **Model A:** the four inspected builders `FUN_140657d80`, `FUN_140657e40`, `FUN_140657e80`, and `FUN_140657f70` expose worker calls in their bodies and inventory membership but each fresh incoming scan reports zero call xrefs, suggesting a local query/index boundary may affect this wrapper cluster.
- **Model B:** the discrepancy is function-specific or limited to those four bodies; adjacent tag-0x4C builder `FUN_140657fc0` has three direct incoming call edges from captured callers.
- **Evidence:** [EV-0476], [EV-0479], [EV-0480], [EV-0482], [EV-0488], [EV-0423].
- **Current assessment:** the four zero-xref results are a genuine repeated observation, but EV-0488 is a counterexample to a universal omission across neighboring builders. Cause and prevalence remain unresolved; use explicit outgoing calls and verified census membership to retain builders as callers.
- **Discriminant:** compare further adjacent builder bodies and incoming-xref listings with inventory callsites; do not infer a project-wide index failure or discard a direct caller from a zero-xref result alone.

## C-OBJ2-Q79-TAG4C-DESCENDANT — process-state route versus combat/skill descendants

- **Model A:** tag 0x4C's immediate target is process/context value propagation and a shared event-value/physics-filter update; no mapped HitData or ActorValue handler appears in its complete direct-call list.
- **Model B:** one of `FUN_1406940d0`'s six indirect sites or its `FUN_140e8f210` object/value helper reaches HitData, ActorValue, protection, or armor skill-use processing.
- **Evidence:** [EV-0397], [EV-0477], [EV-0478], [EV-0488], [EV-0489], [EV-0260].
- **Current assessment:** Model A is supported for the bounded direct body, including its direct call into the previously mapped `FUN_14065c6e0` broadphase route. Model B remains proposed because indirect dispatch and the second helper are unresolved. The direct no-edge is not a transitive or runtime negative.
- **Discriminant:** inspect `FUN_140e8f210` and its exact receiver/value arguments, then follow only producer-backed virtual targets that could reach mapped HitData or ActorValue code; keep Steam effective-protection and raw-AVSK testing separate under EV-0260.

## C-OBJ2-Q79-E8F210-SEMANTICS — shared object/value wrapper purpose

- **Model A:** `FUN_140e90750` uses a recurring object-tree traversal/update substrate while applying its own packed-bit replacement and +0x2c storage write.
- **Model B:** the wrapper and target implement the same semantic scalar/property operation as tag 0x28's positive-float multiplication and setter.
- **Evidence:** [EV-0480], [EV-0481], [EV-0489], [EV-0490], [EV-0491].
- **Current assessment:** `FUN_140e90750` shares the `DAT_14328f300` selector, `FUN_1402f39c0` record lookup, child offsets +0x118/+0x122, and parent vtable slot +0x18 with `FUN_140e905e0`, supporting a recurring structural traversal/update substrate. The operations differ: one conditionally replaces packed bit ranges and writes +0x2c; the other multiplies a positive scalar and invokes a setter. This weakens Model B's identical-operation form, but does not resolve common runtime type or gameplay meaning. Two indirect sites in `FUN_140e90750` remain open.
- **Discriminant:** compare producer-backed RTTI/vtable identities and resolve the two indirect sites only where they can distinguish shared node type or downstream HitData/ActorValue behavior; keep structural similarity separate from semantic identity.

## C-OBJ2-Q79-TAG4D-CONSTRAINT-VS-COMBAT — paired-object update versus hit/skill descendants

- **Model A:** tag 0x4D's immediate helper `FUN_140e8fc90` manages paired object records, updates a matching node through the recursive packed-value route, or constructs/attaches a Havok ball-and-socket or fixed constraint when a node is absent.
- **Model B:** one of the helper's nine virtual call sites or descendants carries the tag-0x4D object/value payload into HitData, effective-protection, ActorValue, or armor-skill processing.
- **Evidence:** [EV-0490], [EV-0491], [EV-0492], [EV-0493], [EV-0494], [EV-0495], [EV-0360], [EV-0364], [EV-0260].
- **Current assessment:** Model A is supported for the bounded direct body and tag-0x4D producer/dispatcher convergence. EV-0495 shows that the tag-0x4D constraint path passes an object pointer to `FUN_140e860d0`, the same build-matched helper used by the separate ProcessTrapHit constraint route; its immediate branch calls `FUN_140b3a710`, while another branch queues the object on its owner. This is static convergence on a shared attachment/queue primitive, not evidence that tag 0x4D is itself a combat hit. The complete direct scans contain no mapped HitData or ActorValue/armor-skill target. Model B remains proposed because the helper's two virtual sites, the nine virtual sites in `FUN_140e8fc90`, and deeper descendants are unresolved; bounded direct no-edge evidence is not a transitive or runtime negative.
- **Discriminant:** resume the exact worker census at `FUN_1406580f0`; only resolve producer-backed virtual targets that can discriminate the remaining tag-0x4D HitData/ActorValue hypothesis. A mapped HitData/ActorValue edge with tag-0x4D dataflow supports Model B; continued constraint ownership/attachment behavior narrows it without establishing a runtime negative. Keep the Steam positive-protection/raw-AVSK observation under EV-0260 separate.

## C-OBJ2-Q79-TAG4A-STATE-VS-COMBAT — gated scalar update versus hit/skill descendants

- **Model A:** tag 0x4A and its object/byte payload form an incoming-hit, ActorValue, or armor-skill route through the worker dispatcher or its helper descendants.
- **Model B:** tag 0x4A is a gated continuation into the same object/value helper sequence used by its two gate-clear producers, which conditionally updates an object float field.
- **Evidence:** [EV-0496], [EV-0497], [EV-0455], [EV-0432], [EV-0260].
- **Current assessment:** Model B is supported for the bounded static producer/dispatcher/helper body: both producers use `FUN_1406d4110`, the set branch queues tag 0x4A, and the clear/dispatcher paths converge on `FUN_140664b20`, `FUN_1402ef0c0`, and `FUN_140ea0760`, followed by a conditional float update. `FUN_140ea0760` requires a byte change under receiver flag +0x321, scans selector-matched list entries, sets or clears per-index bits, and chooses one of two manager update functions. Its direct targets do not identify HitData or ActorValue/armor-skill processing. Model A remains proposed for unresolved virtual targets and deeper descendants; the bounded direct no-edge is not a transitive or runtime negative.
- **Discriminant:** resume the exact worker inventory at `FUN_140658130` (caller 27/62), recording tag and payload plus producer predicates. Separately trace only producer-backed virtual targets from `FUN_140ea0760` when they can resolve the manager route or discriminate a mapped HitData/ActorValue/skill continuation. Keep the Steam matched-hit/protection/raw-AVSK observation under EV-0260 separate.

## C-OBJ2-Q79-TAG60-PAYLOAD-VS-COMBAT — tag-0x60 deferred handler versus hit/skill route

- **Model A:** tag 0x60 forwards its retained payload through dispatcher case 0x60 to `FUN_140e88fd0`, and this target or its descendants carry HitData, ActorValue, effective-protection or armor-skill semantics.
- **Model B:** tag 0x60 targets object/process/state work unrelated to incoming-hit skill credit; the current builder has an unidentified producer/scheduler.
- **Evidence:** [EV-0498], [EV-0499], [EV-0500], [EV-0501], [EV-0502], [EV-0503], [EV-0455], [EV-0260].
- **Current assessment [EV-0499], [EV-0500], [EV-0501]:** The bounded direct route is a recursive hierarchy query/callback. The dispatcher passes arg2=1 and arg3=1, so tag 0x60 bypasses the optional selector/type/flag guard and enables child traversal. The pointer-cell xref query reports one READ from `FUN_140e88fd0` at 0x140e88ffa; it does not expose the callback value or writer. Model B is supported only for this static structure. Model B is supported for the bounded callback body, which performs reference-release/cleanup work; Model A remains proposed through its unresolved vtable +0x8 and +0x128 targets, dynamic node types, and downstream effects. The direct no-edge remains non-transitive.
- **Discriminant:** screen the three adjacent callback pointer cells beginning at GOG RVA 0x202d628 with a bounded pointer-count-3 query; compare their resolved function bodies before deciding whether they form one callback family, then trace only producer-backed virtual targets from `FUN_140e89be0`. A mapped HitData/ActorValue/skill effect supports Model A; object/process/state-only effects narrow toward Model B without proving a runtime negative. Keep Steam protection/raw-AVSK observations separate.

## C-OBJ2-Q79-TAG60-PAYLOAD-VS-COMBAT — tag-0x60 deferred handler versus hit/skill route

- **Model A:** tag 0x60 forwards its retained payload through dispatcher case 0x60 to `FUN_140e88fd0`, and this target or its descendants carry HitData, ActorValue, effective-protection or armor-skill semantics.
- **Model B:** tag 0x60 targets object/process/state work unrelated to incoming-hit skill credit; the current builder has an unidentified producer/scheduler.
- **Evidence:** [EV-0498], [EV-0499], [EV-0500], [EV-0501], [EV-0502], [EV-0503], [EV-0455], [EV-0260].
- **Current assessment:** The exact builder writes tag 0x60 and retains a payload pointer. Its only captured incoming xref is source-less DATA; no direct producer or scheduling condition is mapped. Dispatcher case 0x60 calls `FUN_140e88fd0(payload,1)` for a nonnull payload. Neither model is resolved until that target and relevant producer context are inspected.
- **Discriminant:** trace `FUN_140e88fd0` with complete call edges and producer-backed payload flow. A mapped HitData/ActorValue/skill target with tag-0x60 dataflow supports Model A; object/process/state operations narrow toward Model B without proving a runtime negative. Keep the clean Steam protection/raw-AVSK test separate.

## C-OBJ2-Q79-ADJACENT-CALLBACK-CELLS — shared callback family versus independent handlers

- **Model A:** the three cells at GOG RVAs 0x202d628/630/638 supply a related callback family to `FUN_140e88e90`, `FUN_140e88fd0`, and `FUN_140e88d70`.
- **Model B:** they are merely adjacent global pointers; their targets have independent semantics and runtime types.
- **Evidence:** [EV-0504], [EV-0503], [EV-0502], [EV-0505], [EV-0506].
- **Current assessment:** the three one-to-one READ sites and adjacent pointer values are directly observed. Only the center target `FUN_140e89be0` has an analyzed boundary and its body is a bounded reference-release pattern. Both outer targets have no function boundary and use descriptor offsets +0x10/+0x18 through RDX, but their bounded operations differ: the first conditionally updates `[RCX+0x18]`, while the second derives arguments and dispatches through virtual slot +0x170. The common field offsets are compatible with a shared descriptor interface, but do not prove a callback family or common runtime type; Model A remains a structural lead and Model B remains viable. This bounded target comparison is complete, with no HitData/ActorValue/protection/armor-skill edge.
- **Discriminant:** reopen only if caller-census evidence identifies a target boundary, runtime type, or a common producer/consumer contract for these callbacks. Do not infer complete bodies from the linear contexts. Resume the independent exact worker-caller census at caller 28/62.


## C-OBJ2-Q79-TAG17-SLOT5A0 — tag-0x17 virtual recipient as hit route versus action/state event

- **Model A:** dispatcher case 0x17's recipient slot +0x5a0 reaches a base Actor implementation with a mapped HitData, ActorValue, or armor-skill continuation.
- **Model B:** the slot performs a separate Actor/process/action update; the shared worker gate only serializes the event and does not make it hit-specific.
- **Evidence:** exact caller `FUN_140658240` builds tag 0x17 under a nonnull guard, two direct callers gate it through `FUN_1406d4110`, the dispatcher maps case 0x17 to slot +0x5a0, and the primary Actor table maps that slot to `FUN_14066dfa0` [EV-0507], [EV-0465], [EV-0508], [EV-0432].
- **Current assessment:** EV-0510 completes the helper census: `FUN_1406a19b0` has 7 unique direct targets, four unresolved virtual sites, and three incoming callsites from two callers. Its direct path and bounded `FUN_1406551c0` target use object/child-node state and contain no mapped direct HitData/ActorValue/skill sink. EV-0511/EV-0512 resolve primary Actor slot +0x378 to a thunk through +0x380 and then to the TLS/nested-field selector `FUN_1402e55a0`. EV-0295/EV-0296 show the same helper is used by the HitData receiver `FUN_1406b9df0`. This confirms exact helper reuse, while the tag-0x17 consumer performs object/node operations and the hit consumer has separate unresolved indirect sites; shared returned-object identity and a hit/skill continuation remain unproven. No armor-XP/protection or runtime negative follows.
- **Discriminant:** compare the returned context's producer-backed type and use across `FUN_1406a19b0` and `FUN_1406b9df0`; identify whether both paths receive the same Actor/TLS-owned object and whether any tag-0x17 descendant reaches a mapped HitData/ActorValue/skill sink. A concrete shared type/continuation supports Model A; distinct context owners and object/node-only descendants support Model B. Resolve the actual event receiver type/subclass and retain live pointer identity as an unobserved runtime test.

## C-OBJ2-Q79-TAG19-UPDATE-VS-HIT — tag-0x19 worker handler

- **Model A:** tag-0x19 handler `FUN_140687430` or its descendants re-enter HitData, ActorValue, or armor-skill processing.
- **Model B:** tag 0x19 is a process/state update independent of incoming hits.
- **Evidence:** exact caller 29/62 `FUN_1406582d0` builds tag 0x19; sole producer `FUN_140687370` checks process/type predicates, performs an unresolved virtual +0x2b8 call and state helper, then queues the event; dispatcher case 0x19 calls `FUN_140687430(payload,0)` [EV-0513], [EV-0455].
- **Current assessment:** EV-0514 supports the bounded direct-body state/hierarchy model: `FUN_140687430` has 49 direct-call sites to 38 unique targets, nine unresolved virtual sites, and no mapped direct HitData/ActorValue/armor-skill target; its captured body and second caller use process/object hierarchy and body-part string references [EV-0514]. This narrows Model B only for the captured direct route. Model A remains open through virtual calls and descendants, and the producer virtual +0x2b8 is mapped to primary Actor base target FUN_1406a2cd0, which is also called from an item/equipment workflow; the producer-supplied indexed record and runtime override remain unresolved [EV-0515], [EV-0516]. Neither static path establishes a runtime hit/XP result.
- **Discriminant:** complete direct/incoming coverage for `FUN_1406a2cd0`, trace the indexed producer record, and follow only its mapped virtual descendants to HitData/protection/ActorValue/armor-skill functions. The current base target supports item/equipment handling but is not a complete transitive negative; retain runtime overrides and untraced edges.


## C-OBJ2-Q79-TAG19-SLOT2B8-BODY-PART-VS-EQUIP — indexed producer callback role

- **Model A:** the producer's indexed record and Actor +0x2b8 callback are specific to body-part/hierarchy updates that feed the tag-0x19 handler.
- **Model B:** the primary base Actor implementation is an item/equipment operation reused by the producer; the list entry may represent an item/equipment record, and the later hierarchy handler is a separate state stage.
- **Evidence:** FUN_140687370 loads an indexed pointer from `param_1[0x3f]+0x270+index*8` and calls receiver +0x2b8 before state writes/tag submission [EV-0515]. Primary Actor +0x2b8 maps to FUN_1406a2cd0; its bounded caller FUN_1406a1bf0 contains equip/quest-item branches and strings, while the target checks BGSBipedObjectForm records [EV-0516]. The tag-0x19 handler uses hierarchy/body-part string references [EV-0514].
- **Current assessment:** Model B is supported for the primary Actor base method, but the producer-supplied pointer's runtime type/identity and any subclass override are not established. Model A remains possible through dynamic receiver or through the later node handler. No armor-protection or XP effect is yet mapped.
- **Discriminant:** complete FUN_1406a2cd0 call-edge census and map the indexed record's type/producers; compare its dataflow with mapped effective-protection and AV11/AV12 routes. Preserve unresolved virtual targets and build boundaries.


## C-OBJ2-Q79-ITEM-HELPER-STATE-VS-COMBAT — FUN_14022b7a0 descendants

- **Model A:** the tag-0x19 item/equipment path reaches HitData, protection, ActorValue, or armor-skill processing through FUN_1406b98f0 or its descendants.
- **Model B:** FUN_14022b7a0 handles item/list and actor-context state; its shared context selector and gated helper do not enter hit/skill processing.
- **Evidence:** the full direct body has 115 callsites to 51 functions, three indirect calls, direct edges to FUN_1406b98f0/FUN_1402e55a0/FUN_140661f60/FUN_1406581b0, and no mapped direct HitData/AV award target [EV-0518]. The same selector is used by the HitData receiver and tag-0x17 route [EV-0295], [EV-0296], [EV-0512].
- **Current assessment:** neither transitive model is resolved. Exact helper reuse is established; pointer identity and combat/skill causality are not. The nearest distinct candidate is FUN_1406b98f0; the shared-gate branch and three virtual calls remain open.
- **Discriminant:** trace FUN_1406b98f0 and its producer-backed descendants; test for mapped HitData/protection/AV11/AV12 dataflow. Then inspect FUN_140661f60 or FUN_1406581b0 if the getter route stays bounded.


## C-OBJ2-Q79-NESTED-SELECTOR-VS-COMBAT — FUN_1406b98f0

- **Model A:** item/list getter FUN_1406b98f0 or a consumer of its selected record connects to HitData, protection, ActorValue or armor-skill behavior.
- **Model B:** FUN_1406b98f0 only selects a nested type-marked record; item-route use remains state/action-data handling with no mapped combat/skill effect.
- **Evidence:** the full getter body has one direct callee, no indirect sites and 69 incoming callsites from 51 functions; its callee selects a nested entry by byte marker +0x1a == 0x29 and returns its first qword [EV-0519]. FUN_14022b7a0 uses the result in a TESActionData-related branch [EV-0518], [EV-0519].
- **Current assessment:** the bounded selector model is supported; downstream consumer effects and the marker type are unknown. The decompiler gives FUN_1406b98f0 one formal argument while its callee uses a second selector value, so preserve the register-flow discrepancy.
- **Discriminant:** trace FUN_140661f60 (shared-context consumer) and any producer-backed uses of the selected pointer to mapped HitData/protection/AV11/AV12 targets; do not generalize a no-direct-edge result to the 51 caller functions.


## C-OBJ2-Q79-SHARED-CONTEXT-STATE-VS-COMBAT — FUN_140661f60

- **Model A:** context selected from the item/list route feeds an object used by HitData, armor protection, ActorValue or armor-skill processing.
- **Model B:** FUN_140661f60 performs hierarchy-node selection and a reference-counted component pointer update, shared with process-update code but separate from hit/skill sinks.
- **Evidence:** complete census maps two unresolved virtual +0x18 sites and 11 callers; direct body selects a named/child node and calls FUN_1407158f0 to assign nested +0x178 [EV-0520]. Callers include FUN_14022b7a0 and FUN_1406e5da0 [EV-0518], [EV-0464]–[EV-0466].
- **Current assessment:** Model B is supported for the bounded direct/setter route. Model A remains open through FUN_1414ae8a0, the two node virtuals, readers of +0x178 and runtime object identity. No hit/XP result follows.
- **Discriminant:** map FUN_1414ae8a0/DAT_14332c3a0, then trace producer-backed +0x178 readers into effective-protection and HitData/AV11/AV12 functions.

## C-OBJ2-Q79-HIERARCHY-IDENTITY-VS-COMBAT — FUN_1414ae8a0 / +0x178

- **Model A:** `DAT_14332c3a0` identifies an armor/protection or hit-relevant component, and the object selected by `FUN_1414ae8a0` enters such behavior through component +0x178.
- **Model B:** the global is a hierarchy/context identity token; selection updates process/object state and remains separate from HitData, ActorValue and armor-skill processing.
- **Evidence:** the selector has one direct fallback callee, four unresolved virtual sites and two calls from `FUN_140661f60`; it compares a nested object's virtual +0x10 result with `DAT_14332c3a0` before returning a candidate [EV-0521]. `FUN_140661f60` passes its result to the +0x178 setter and is shared by item/list and process-update callers [EV-0520], [EV-0518], [EV-0464]–[EV-0466].
- **Current assessment:** recursive identity-filtered hierarchy selection is directly supported. The data/type at the identity global is not resolved, the fallback helper has not had a separate full edge census, and no producer-backed +0x178 reader is tied here to HitData, protection or AV11/AV12. Model B is a compatible structural explanation, not a transitive negative; Model A remains open. EV-0522 adds 47 references to the global and one candidate write xref at RVA 0x0d2f660, but does not expose the written value or type.
- **Discriminant:** query GOG address RVA 0x332c3a0 for data contents and references; then locate producer-backed +0x178 readers and trace any selected-object dataflow into mapped effective-protection, HitData or AV11/AV12 paths. Keep direct identity comparison, dynamic dispatch and runtime evidence separate.

## C-OBJ2-Q79-GLOBAL-WRITE-XREF-SEMANTICS — DAT_14332c3a0

- **Model A:** the WRITE xref at VA 0x140d2f660 represents an actual writer that initializes or updates `DAT_14332c3a0`.
- **Model B:** the xref classification is insufficient to identify that global as the register-indirect store destination; the site is a generic unbounded two-field store and has not been dataflow-linked to the global.
- **Evidence:** the global address query reports 47 references, including WRITE at 0x140d2f660 and overlapping DATA at +3 [EV-0522]. Address context at that site shows `MOV [RCX],RDX`, `MOV RAX,RCX`, `MOV [RCX+8],R8`, `RET`, no function boundary, and 410 incoming xrefs [EV-0523].
- **Current assessment:** preserve the xref as a candidate only. The instructions do not contain the global address, and no caller argument/dataflow proof ties RCX to `DAT_14332c3a0`. Neither global mutation nor type/value is established.
- **Discriminant:** inspect the actual global-reference representation and the source instruction/reference operands in a more targeted Ghidra data query; independently resolve the global through other function-body uses. Do not use the generic store as proof of identity initialization.

## C-OBJ2-Q79-PLUS178-REUSE-VS-SELECTED-COMPONENT — broad offset collisions

- **Model A:** nearby readers `FUN_140715840` and `FUN_140715940` operate on the same component field +0x178 written by `FUN_1407158f0` after `FUN_1414ae8a0` selection; their descendants may reveal the selected object role.
- **Model B:** +0x178 is a common offset in unrelated objects and stack locals; the nearby readers are coincidental until receiver type and pointer flow are established.
- **Evidence:** the full scan reports 987 accesses across 722 functions, including 529 stack accesses, 199 writer candidates and eight computed-writer candidates. It lists a read in FUN_140715840, setter read/write in FUN_1407158f0, and compare/read sites in FUN_140715940 [EV-0524]. The specific selector-to-setter path is captured in EV-0520/EV-0521.
- **Current assessment:** Model B remains a live collision explanation. The adjacent functions are useful candidates because of location and same offset, but neither their object identity nor dataflow from the selected pointer is established. No armor/protection/HitData/AV11/AV12 conclusion follows.
- **Discriminant:** inspect FUN_140715940 and its callers, then FUN_140715840, looking for a producer-backed shared receiver/component type or flow from the FUN_140661f60 setter. A matching offset without identity/dataflow is not a causal edge.

## C-OBJ2-Q79-PLUS178-ACTOR-UPDATE-VS-ARMOR — FUN_140715940

- **Model A:** the selected component at +0x178 contributes to armor protection or another HitData/ActorValue path through the numeric calculation rooted at `FUN_1414fdb10`.
- **Model B:** `FUN_140715940` consumes a component for actor-update/process state, independent of incoming-hit skill credit; the formula's gameplay role remains separate/unknown.
- **Evidence:** complete `FUN_140715940` census has 13 direct targets, zero indirect sites, and callers `FUN_140773750`/`FUN_140734890`. It conditionally reads nested +0x178, routes an object +0x70 pointer to `FUN_1414fdb10`, then calls `FUN_1406eeb00` and `FUN_1406e68a0`; another branch calls `FUN_140661f60` through the shared selector [EV-0525], [EV-0520]. The +0x178 whole-program scan has 987 hits in 722 functions [EV-0524].
- **Current assessment:** a bounded actor-update numeric-consumer route is supported. Model B fits the captured caller/body shape, but the formula/update helper semantics and receiver identity are open; Model A remains possible. No direct mapped HitData/ActorValue award or armor-skill sink occurs in `FUN_140715940`, but descendants are uninspected.
- **Discriminant:** query `FUN_1414fdb10` with complete direct/incoming edges and bounded callees. A mapped protection, HitData or AV11/AV12 path with the selected-component arguments supports Model A; bounded actor-state math narrows toward Model B without creating a global negative.

EV-0526 strengthens the bounded state/context model: the nested +0x178 read from `FUN_140715940` reaches an array-based sum of per-entry distance-attenuated floats through `FUN_1414fdb10`/`FUN_14150aea0` [EV-0526], [EV-0525]. This is a concrete numeric consumer, not a mapped armor formula; final update helpers and exact selected-pointer identity remain open. Model A stays possible only through those descendants or runtime evidence; the next discriminator is `FUN_1406eeb00`.

EV-0527 strengthens the bounded context/state model: the distance-weighted aggregate reaches `FUN_1406eeb00`, whose sole body is a conditional field +0x3a8 store and whose only captured caller is `FUN_140715940` [EV-0527], [EV-0526], [EV-0525]. The field reader/meaning and paired `FUN_1406e68a0` remain unresolved, so this does not exclude a later consumer effect or establish a global negative.

EV-0528 resolves the paired immediate write only: `FUN_1406e68a0` stores `DAT_14319c47c` at nested +0x3b0 after `FUN_1406eeb00` stores the aggregate at nested +0x3a8, both through the same caller expression [EV-0528], [EV-0527], [EV-0525]. This strengthens the bounded actor/context state model but does not identify either field or their readers. H57 remains open only as a downstream-reader/runtime alternative; inspect producer-backed readers of the pair next and do not treat displacement matches as receiver identity.


## C-OBJ2-Q79-PLUS3A8-READER-IDENTITY — adjacent reader versus offset collision

- **Model A:** `FUN_1406eeae0` reads the same nested +0x3a8 field written by `FUN_1406eeb00` on the actor-update route.
- **Model B:** the +0x3a8 read is an unrelated same-offset access; adjacency does not establish shared receiver or call flow.
- **Evidence:** the complete scan finds 54 accesses across 38 functions, including `FUN_1406eeae0` reading dword [RAX+0x3a8] at RVA 0x6EEAE9 and `FUN_1406eeb00` writing float [RAX+0x3a8] at RVA 0x6EEB09. Other offset matches occur in distinct functions [EV-0529], while `FUN_140715940` is the sole mapped setter caller [EV-0527], [EV-0528].
- **Current assessment:** the adjacent function is a high-value reader candidate but no producer-backed edge or same-object identity is established. The scan's other accesses preserve the offset-collision model.
- **Discriminant:** query `FUN_1406eeae0` with complete direct/incoming edges and bounded callees; trace its callers' receiver registers and compare them with `FUN_140715940` and the nested +0x10 object. A direct shared call/object flow supports Model A; independent callers/types support Model B. No armor, HitData, ActorValue, or Steam result follows from the scan alone.

EV-0530 updates C-OBJ2-Q79-PLUS3A8-READER-IDENTITY: `FUN_1406eeae0` has four callers and is used in detection/light-related paths, while the setter route receives an object +0xf8 field expression from `FUN_140734890` [EV-0530], [EV-0525]. This supports a shared structural +0xf8 wrapper path (H59) and narrows the claim that the getter is wholly unrelated. Same class/instance identity remains unresolved (H60); the many other scan hits still include offset collisions [EV-0529]. Next resolve the caller type/source for `FUN_140734890`; do not infer an armor link from the shared field slot.

EV-0531 strengthens H59: `FUN_140734890` passes the same `param_1[0x1f]` (+0xf8) expression to both actor/process update `FUN_1406e5da0` and nested state updater `FUN_140715940` [EV-0531]. The matching +0xf8 getter callers in EV-0530 support a common structural slot. H60 remains open for different runtime type/instance because FUN_140734890 has no analyzed direct caller and no primary Actor vtable match yet; its 33 virtual sites remain unresolved. Query primary Actor slot +0x718 before promoting an exact type identity.

EV-0532 falsifies the narrow prediction that FUN_140734890 is the primary Actor slot +0x718 target. That slot is FUN_1406b9000 under primary .?AVActor@@ RTTI at subobject offset zero [EV-0532], [EV-0400]. H59 remains supported only for the shared +0xf8 structural call path; H60 remains open for the declaring runtime type. The separate table at RVA 0x18A7020 references FUN_1406b9000, not FUN_140734890. Inspect references to FUN_140734890 before asserting another vtable owner or unreachability.

EV-0533 narrows the no-caller uncertainty for FUN_140734890: its address has two source-less DATA references at RVAs 0x3660620 and 0x18ad2d8, but neither exposes a table or type [EV-0533]. The base Actor slot +0x718 remains a different target [EV-0532]. Inspect the nearer data reference context before promoting an alternate vtable/registration hypothesis.

EV-0534 shows that source RVA 0x18ad2d8 has no function identity, no captured incoming references to the source address, and no instruction at the address; it still does not expose the qword that EV-0533 references to FUN_140734890. This leaves an isolated data slot versus table/registration interpretation open. Query at most one pointer-sized entry, and only inspect neighbors if that result gives a justified boundary. Do not infer class, reachability, or HitData/armor semantics.

EV-0535 resolves the qword at RVA 0x18ad2d8 to FUN_140734890, while reporting zero references pointing to that entry [EV-0535]. The isolated-slot model and an untyped table/registration-entry model remain competing explanations; the exact pointer value alone does not show an owner or runtime dispatch. The other source RVA 0x3660620 is an independent discriminator.

EV-0536 complicates the second-reference interpretation: qword 0x735D6800734890 at RVA 0x3660620 is not a canonical 64-bit code pointer, although its low32 equals FUN_140734890’s RVA and its high32 is 0x735D68 [EV-0536], [EV-0533]. A packed pair of 32-bit RVAs and an unrelated/encoded 64-bit field remain competing models. Resolve the high-half candidate before treating the source as a function-pointer table or registration.

EV-0537 finds that RVA 0x735D68, the high word in EV-0536, follows a decoded RET at VA 0x140735D67 but has no function/instruction identity itself [EV-0537]. This raises an exclusive-end-boundary hypothesis for the qword, while a packed pair or unrelated field remains possible until the RET owner is identified. Do not connect the boundary to FUN_140734890 yet.

EV-0538 identifies RVA 0x735D67/VA 0x140735D67 as a RET inside FUN_140734890 [EV-0538]. Thus EV-0536’s low/high dwords match that function’s entry RVA and the byte immediately after the RET. A start/exclusive-end range pair is now a supported pattern candidate, but the data record owner and runtime registration are still unestablished; inspect one adjacent qword for replication.

EV-0539 shows the next qword at RVA 0x3660628 is 0x735D7001D74768; its high32 0x735D70 matches a decoded PUSH address following FUN_140734890’s RET, while low32 0x01D74768 is untyped [EV-0539], [EV-0538]. A 12-byte function-range row with unwind metadata is plausible, but the next function entry and record layout remain unverified.

EV-0540 confirms RVA 0x735D70 is FUN_140735d70 and finds a DATA ref to it from RVA 0x366062c, exactly 12 bytes after candidate row start RVA 0x3660620 [EV-0540], [EV-0539]. This is consistent with sequential 12-byte code-range records, but one matching address does not type the enclosing region or establish PE unwind metadata. Two other untyped data refs remain unexplained.

EV-0541 shows the qword at RVA 0x366062c is 0x735DA200735D70: low32 matches FUN_140735d70 entry RVA and high32 0x735DA2 is an unverified end candidate [EV-0541], [EV-0540]. A repeated begin/end-row model is stronger, but verify the preceding instruction before assigning range semantics or a section type.

EV-0542 weakens the second-row end interpretation: RVA 0x735DA1 is associated with FUN_140735d70, lacks an instruction boundary, and follows a decoded MOV at 0x735D9F rather than a RET [EV-0542]. Candidate high32 0x735DA2 has not yet been shown outside the function. The repeated begin/end model remains unverified.

EV-0543 resolves candidate high32 RVA 0x735DA2 as a MOVAPS instruction inside FUN_140735d70, with five DATA refs to that address [EV-0543]. This falsifies the second qword as a normal exclusive function end and weakens the repeated code-range-row model. The first qword’s start/end-like values remain unexplained; do not call the source `.pdata`, unwind metadata, table, or runtime registration.

EV-0545 shows worker dispatcher case 0x1A calls FUN_1404c2480(global,payload), while adjacent case 0x1B calls FUN_1404c2650 with the same argument shape [EV-0545]. The static route is known but its event semantics remain open; neither branch establishes ordinary incoming-hit or armor-skill behavior. Inspect the exact tag-0x1A target.

EV-0546 resolves the direct tag-0x1A target as guarded registry/list work over payload ID +0x14, not a direct HitData/ActorValue/armor-skill route [EV-0546], [EV-0545]. The deeper helper FUN_1404ca0f0 remains unexpanded and indirect/downstream semantics remain open; keep the practical hit/XP test decisive.

EV-0548 shows tag 0x1B conditionally removes payload ID from manager +0x100 integer array and adds payload pointer to +0xe8 array, with a secondary reference-counted child traversal [EV-0548]. This is complementary to the bounded tag-0x1A path, but neither event’s manager/type semantics or ordinary-hit relation is established; a nested virtual release remains unresolved.

## Q79 StartCombat player-target threshold field identity (EV-0579)

An initial reading of `DAT_141ffda78 <= FUN_140766520(player)` in `FUN_14071e250` admits a player-level-gate interpretation [EV-0578]. Follow-up source tracing shows `FUN_140766520` returns Actor+`0x9d8` component offset `+0x18`, and this field bounds traversal of `0xa8`-byte records in `FUN_1408062d0`; `FUN_140805c40` passes the field address and `0xa8` stride to an array helper [EV-0579]. The direct `Actor.Level` model is falsified for the accessor. The field's exact count/capacity meaning, global threshold identity and gate purpose remain unresolved; no level-gate conclusion follows.

## C-OBJ2-Q79-TAG12-CALL-PARITY — immediate/deferred slot +0x1a8 arguments

- **Model A (earlier):** the deferred case uses a selector in R8 and lacks matching R9/stack arguments, so it differs from the immediate AddRagdollHandler call [EV-0619], [EV-0620].
- **Model B (corrected):** the cited `0x65939c` instruction belongs to case `0x4`; tag `0x12` calls slot `+0x1a8` at `0x659c92` with `(receiver, object, 1, 1, selector, 0)`, matching the immediate call [EV-0631].
- **Discriminant and assessment:** address-only GOG captures at both RVAs, the dispatcher case decompilation, producer call and tag-0x12 builder offsets support Model B. Model A is falsified for this static call path; CL-L432 is retracted and corrected by CL-L444.
- **Implication:** the zero sixth argument enforces the `FUN_140e884d0` object-state check on both immediate and deferred routes. This removes the proposed nonzero-`param6` bypass mechanism, but it does not establish dynamic callback results, Steam behavior, protection, armor XP or a vanilla reproduction. No OBJ-2 causal edge is added.

## C-OBJ2-Q79-TAG4B-PLAYERSTATE — player state transition versus hidden hit route

- **Model A:** tag 0x4b is a hidden incoming-hit/armor-skill route. It predicts a producer-backed HitData/protection/AV11/AV12/UseSkill edge in the exact route or resolved virtual descendants.
- **Model B:** tag 0x4b is a PlayerCharacter/object-state transition. It predicts PlayerCharacter receiver identity, state-bit gating, object flag writes and state callbacks without a mapped direct hit/skill sink.
- **Evidence:** caller 51 builder/producer and call graph; PlayerCharacter global identity and `+0x4c8` RTTI slot; bounded recursive keyed-object helper [EV-0337], [EV-0344], [EV-0632].
- **Assessment:** B is supported for the captured direct static route; A has no direct support. Ten producer virtual sites and deeper callbacks remain unresolved, so this is not a global no-hit result and does not resolve OBJ-2.
- **Cross-caller lead:** both caller 50 fallback construction and caller 51 state callback pass `DAT_1432740d8..+8` to different helpers [EV-0626], [EV-0632]. Trace `FUN_140cb4ae0` and compare the actual helper contracts before adding any shared-mechanism or HitData edge.

## C-OBJ2-Q79-SHARED-TUPLE-CONSUMERS — shared mechanism versus shared input storage

- **Model A:** caller 50 fallback construction and caller 51's state callback share a registration/update primitive because both pass `DAT_1432740d8..+8`.
- **Model B:** the same adjacent input storage is reused by distinct mechanisms with caller-specific field transformations.
- **Evidence:** caller 50 factory provenance [EV-0626], caller 51 producer path [EV-0632], and the direct helper/factory/address captures [EV-0633].
- **Assessment:** B is supported for the captured direct paths: `FUN_140cb4ae0` serializes all three dwords into a queued event record, whereas `FUN_1402c6810` configures a factory object and zeroes the third fallback field. A's predicted shared direct primitive is falsified. The tuple's values/names and any deeper transitive relation remain unresolved; no causal HitData/armor edge is added.

## C-OBJ2-Q79-TAG56-LIFECYCLE-VS-COMBAT — collection callback versus hidden hit route

- **Model A:** tag 0x56 enters HitData, protection or armor-skill processing through its virtual +0x138 target.
- **Model B:** tag 0x56 is a retained-object callback in a manager collection/lifecycle path.
- **Evidence:** builder, producer/dispatcher slot parity, keyed manager helper and sole collection-owner caller [EV-0634].
- **Assessment:** B is supported for the captured direct source and helper route; A has no direct mapped sink. The +0x138 target and dynamic callback descendants remain unresolved, so this is not a global no-hit result and does not resolve OBJ-2.

## C-OBJ2-Q79-TAG50-ACTOR-STATE-VS-COMBAT — Actor state callback versus hit/armor route

- **Model A:** tag 0x50 is an ordinary player-hit/protection/armor-skill route.
- **Model B:** tag 0x50 is an Actor slot-0x89 process/object-state callback, whose target skips PlayerCharacter receivers.
- **Evidence:** Actor table identity and slot capture, tag builder/dispatcher, PlayerCharacter identity and target call graph [EV-0344], [EV-0400], [EV-0635].
- **Assessment:** B is supported for the captured direct path; A has no direct mapped sink. Seventeen dynamic virtual sites remain unresolved, so no global no-hit conclusion or bounty resolution follows.

## C-OBJ2-Q79-TAG54-SPATIAL-CONTEXT-VS-COMBAT — Actor update versus hit/armor route

- **Model A:** tag 0x54's Actor+0x128/context payload reaches HitData, effective protection, AV11/AV12 or armor-skill processing.
- **Model B:** producer FUN_14066b6e0 selects tag 0x54 from process/grid predicates; the target performs Actor/context and nested object-state work, including a tag-0x32 gated continuation.
- **Evidence:** producer coordinates and process fields, helper predicates, dispatcher and complete direct census, Actor slot-0x65 target, tag-0x32 builder/dispatcher [EV-0636]; Actor slot identity [EV-0400], shared selector [EV-0512], recursive helper [EV-0483]–[EV-0486].
- **Assessment:** B is supported for the captured direct path. A has no mapped direct sink, but 21 virtual sites, one slot-0x538 target and recursive descendants remain unresolved. No global no-hit, Steam, effective-protection, armor-XP, or bounty conclusion follows.
- **Discriminant:** resolve producer-backed virtual targets and preserve a clean Steam matched-hit/protection/raw-AVSK observation; same helper code alone cannot establish same-pointer identity.

## C-OBJ2-Q79-TAG57-NUMERIC-REGISTRY-VS-COMBAT — value/limit notification versus hit/armor route

- Model A: tag 0x57 or its registry descendants affect HitData, effective protection, AV11/AV12 or UseSkill.
- Model B: caller 55 applies a numeric value/limit predicate and routes one of codes 0xFC–0xFE through a registry helper.
- Evidence: builder/sole producer, literal category and code arguments, per-category state bits, dispatcher case, and six-call/zero-indirect registry-helper census [EV-0637].
- Assessment: B is supported for the captured direct route. A has no mapped direct sink in that bounded path. Literal categories and codes have no verified names, and wider registry descendants remain open. No global no-hit, Steam, armor-XP or bounty conclusion follows.
- Discriminant: map the code's data/record provenance and resolve relevant registry consumers before assigning named quest, ActorValue, combat, or armor semantics.

## C-OBJ2-Q79-TAG58-PERK-CLEANUP-VS-COMBAT — PlayerCharacter rank-list cleanup versus hit/armor route

- Model A: tag 0x58 or a dynamic descendant performs HitData/effective-protection/AV11/AV12/UseSkill work.
- Model B: tag 0x58 removes a PlayerCharacter collection object and conditionally removes its matching entry through BGSPerk::FindPerkInRanksVisitor.
- Evidence: two builder producers and modes, dispatcher case, collection-removal handler, visitor RTTI/method, and bounded cleanup helper chain [EV-0344], [EV-0637], [EV-0638].
- Assessment: B is supported for the captured static path. A has no mapped direct sink; one runtime PlayerCharacter virtual override at +0x650 remains unresolved. The captured path does not show perk granting or eligibility-level mutation. No global no-hit, Steam, armor-XP, or bounty conclusion follows.
- Discriminant: identify the runtime PlayerCharacter vtable target for +0x650 and trace any producer-backed continuation before changing the no-edge assessment.

## C-OBJ1-Q79-PERK-RANK-ADD-VS-LEVEL-GATE — rank-list API versus level-one perk access

- Model A: caller 57's AddPerkVisitor route can set a perk rank without evaluating a Player-level requirement, so a natural caller might expose a level-gated perk at level one.
- Model B: the observed native path mutates a rank list under a rank-count bound; a separate caller, record condition, or runtime path may enforce eligibility, and wrapper invokers are not identified.
- Evidence: tag-0x5F builder/dispatcher, AddPerkVisitor rank path, current-rank lookup, two wrappers, and bounded function-table/RTTI screen [EV-0637], [EV-0639].
- Assessment: Model B is the conservative result. The captured path checks perk+0x52 but does not read Player level; the wrappers have no analyzed incoming direct callers and the candidate table is not RTTI-validated. This does not prove a bypass, level-one perk access, quest gate change, or ordinary vanilla invocation. No OBJ-1 causal edge is added.
- Discriminant: identify runtime wrapper callers, trace a verified level-gated perk record into this route, and observe rank membership and gate state on a clean level-one path. Preserve callback uncertainty and the GOG/Steam boundary.

## C-OBJ2-Q79-TAG5A-SPATIAL-STATE-VS-HIT-ARMOR — coordinate manager versus hit/skill route

- Model A: tag 0x5A updates or removes handle-keyed coordinate state from Player/object geometry and Actor/physics predicates.
- Model B: an unresolved manager virtual callback converts the event into HitData, protection, AV11/AV12, or UseSkill processing.
- Evidence: builder, two producers, tag-0x5A dispatcher, coordinate manager body, Actor slot 0x9C identity, and Havok contact-pair caller [EV-0637], [EV-0640].
- Assessment: Model A is supported for the bounded static route. Model B has no mapped direct sink; 13 manager virtual sites and descendants remain open. This is not a transitive/runtime negative or a Steam result. No OBJ-2 causal edge is added.
- Discriminant: resolve only producer-backed manager virtual targets and show a data/control path into a mapped HitData/armor-skill sink; otherwise retain the spatial-state scope.

## C-OBJ2-Q79-TAG5B-DISARM-VS-HIT-ARMOR — deferred disarm action versus armor/XP route

- Model A: tag 0x5B is a deferred Actor action with a disarm-related PlayerCharacter outcome. The receiver calls Actor slot +0x658 and emits the explicit disarm message on the PlayerCharacter branch.
- Model B: the producer/Actor descendants directly implement level-gated access, effective armor protection, or zero armor XP while retaining protection.
- Model C: the producer's immediate helper is equivalent to the deferred handler.
- Evidence: tag builder, producer, case 0x5B, receiver, Actor slot 0xCB map, and `FUN_1405aed00`/`FUN_1405b0730` captures [EV-0400], [EV-0641].
- Assessment: A is supported for the bounded deferred route. B has no mapped direct level/quest/HitData/protection/AV11/AV12/UseSkill edge; 16 Actor virtual sites, deeper descendants, and runtime remain unresolved. C is unsupported by the captured direct path: immediate state/update work does not directly call `FUN_14067aea0`. No OBJ-1/OBJ-2 causal edge is added.
- Discriminant: continue remaining worker callers; only extend this branch if a producer-backed virtual descendant maps to an exact level, protection, HitData, AV11/AV12, or UseSkill primitive, or if a clean Steam matched-hit test measures protection and armor XP.

## C-OBJ2-Q79-TAG5C-HITDATA-HELPER-VS-ARMOR-XP — serialized hit context versus armor-skill effect

- Model A: tag 0x5C is a HitData-derived serialized branch; its producer is FUN_1406b9df0, it clones handler context, and its dispatcher returns to shared FUN_1406be430 through FUN_1406be2c0.
- Model B: the route directly alters effective armor protection or changes hit-earned AV11/AV12/UseSkill credit while preserving protection.
- Evidence: caller 60 builder, producer, cloned fields, case 0x5C, target, and shared helper capture [EV-0295], [EV-0296], [EV-0431], [EV-0600], [EV-0642].
- Assessment: A is supported for the captured producer/copy/dispatcher/common-helper relationship. B has no mapped direct sink in the bounded bodies. The helper queries numeric ActorValue 0x24 and calls a vector/physics-like sink, but that is not an identified armor or XP effect. Three indirect sites, descendants, exact runtime receiver/data, ordinary-hit coverage, and clean Steam behavior remain open. No OBJ-1/OBJ-2 causal edge is added.
- Discriminant: only extend descendants if a producer-backed dynamic target reaches effective protection, HitData award logic, AV11/AV12, or UseSkill; independently complete the clean Steam matched-hit/protection/raw-AVSK test [EV-0260].

## C-OBJ2-Q79-TAG61-EYE-TEXTURE-VS-PROGRESSION-COMBAT — rendering update versus quest/armor route

- Model A: tag 0x61 replaces an eye-headpart geometry texture after producer-side 3D/headpart/geometry checks.
- Model B: the tag is a level-one access, HitData, effective-protection, or armor-skill route.
- Evidence: caller builder, sole producer, dispatcher type-identity guard and nested texture pointer update [EV-0643].
- Assessment: A is supported for the captured static route. B has no explicit level/quest predicate or mapped direct HitData/protection/AV11/AV12/UseSkill sink. Unresolved virtual/resource descendants and runtime behavior remain open. No OBJ-1/OBJ-2 causal edge is added.
- Discriminant: keep B closed unless a producer-backed descendant reaches a mapped quest gate, protection calculation, HitData, AV11/AV12 or UseSkill primitive.

## C-OBJ2-Q79-TAG62-SHARED-ACTOR-HANDLER-VS-ARMOR-XP — shared HitData-reached helper versus same hit/skill event

- Model A: caller 62/tag 0x62 is a distinct event that reuses `FUN_1406bc400`, an Actor/process handler also called by the mapped HitData handler.
- Model B: tag 0x62 itself represents the ordinary incoming HitData continuation and reaches the AV11/AV12 award path.
- Model C: tag 0x62 changes level-one eligibility or effective armor protection.
- Evidence: caller builder/sole producer, tag-0x62 dispatcher case, exact target direct-call census, mapped HitData caller, and direct helper census [EV-0644], [EV-0295], [EV-0296].
- Assessment: A is supported as call-graph reuse. B is not established: the caller is a different producer, the builder writes tag 0x62, and no same-event arguments or mapped armor-skill sink are shown. C has no direct gate/protection evidence. Unresolved indirect descendants and runtime effects remain open; no OBJ-1/OBJ-2 edge is added.
- Discriminant: reopen B only with producer-backed argument identity/ordinary-hit coverage or a clean Steam event trace; reopen C only with a mapped level/protection path or controlled effective-protection observation.

## C-OBJ2-Q80-RESISTANCE-CLOTHING-VS-FUNCTIONAL-ARMOR — effect resistance versus physical armor/XPCredit

- Model A: ARMO `000FC061` can provide defensive value against effects whose resistance type is AV44 because its enchantment modifies Resist Magic and GOG `FUN_1406c68d0` routes target effects through `Actor::MagicTarget::CheckResistance`.
- Model B: this Clothing ARMO has zero physical DNAM and sits outside the mapped positive-DNAM HitData AV11/AV12 armor-skill selector; a magic resistance path does not establish physical armor protection or an armor-XP bypass.
- Evidence: [EV-0398], [EV-0222], [EV-0400]–[EV-0402], [EV-0651].
- Assessment: A is supported as a GOG static candidate path. B is supported as the scope boundary for the bounty prize. Neither model proves a live Health damage reduction or numeric AVSK result. `FUN_1407ee620` also calls the shared vector helper `FUN_1406be430`, but EV-0600/EV-0652 show distinct caller arguments and no direct AV11/AV12/UseSkill sink; no shared-hit edge is added.
- Discriminant: on a verified clean Steam level-one save, compare matched resistable magic damage naked/equipped and physical-hit controls, while recording raw Heavy/Light/Block AVSK and effective protection [EV-0260].

## C-OBJ2-Q80-NPC-INVENTORY-REQUEST-LEVEL — Madesi actor level versus player/zone request level

- Model A: Madesi's fixed actor level 8 supplies the request level to `LootCitizenPocketsCommon` and its nested necklace lists, making ARMO `000FC061` eligible for a natural inventory roll at player level 1.
- Model B: nested inventory list resolution uses player level or an encounter-zone-derived value; with a request below 8, the candidate rows are ineligible.
- Evidence: exact list nesting and LVLO thresholds [EV-0646], native common-pocket-list flags/entries [EV-0647], Madesi NPC record level and list reference [EV-0648], revision-pinned UESP descriptions [EV-0645].
- Assessment: the official records establish list membership and the actor's encoded level but not the runtime requested-level argument. The UESP page is secondary grounding and does not answer this engine call. Both models remain open; no level-one acquisition is claimed.
- Discriminant: trace the NPC default-inventory list-resolution request from the verified GOG engine code, then test natural Madesi inventory on clean level-one and higher-level controls under the exact Steam profile; no console item grant counts [EV-0260].

## C-OBJ1-Q81-CULTIST-AMBUSH-ROUTE-IDENTITY — separate quest routes versus shared world-event machinery

- Model A: `DLC2WE09` is a separate level-25 world encounter, while `DLC2CultistAmbush` is an independent post-Way-of-the-Voice stage route with no player-level check.
- Model B: `DLC2CultistAmbush` includes an additional or shared level predicate in a script, Story Manager node, dialogue, or native callback.
- Model C: `DLC2WE09` is an event/node/script identity attached to the same `DLC2CultistAmbush` QUST, so the two wiki labels describe different layers or variants of shared event machinery.
- Evidence: revision-pinned UESP lead [EV-0653]; native five-master QUST `DLC2CultistAmbush` FormID `0403546D`, event `CLOC`, six CTDA functions with no `GetLevel`, and VMAD links to `DLC2WE09ActorScript`, `DLC2WECultistAmbushPlayerScript`, `DLC2MQ01`, and `DLC2WE09Chance` [EV-0654].
- Additional evidence: distinct official Story Manager branches select distinct QUSTs: CLOC `DLC2CultistAmbushNode` -> `DLC2CultistAmbush`, and SCPT `DLC2WEPriorityQuests`/`DLC2WENode` -> `DLC2WE09`; both eventually share stage-10 `DLC2MQ01` handoff code in loose PSC, which does not collapse the branches [EV-0656], [EV-0658], [EV-0663], [EV-0664]. The QUST `DLC2WE09` bytes encode GetLevel >=25 and GetInCurrentLoc Solstheim with both OR bits set [EV-0657], [EV-0665], [EV-0666]. The identity-checked GOG evaluator groups consecutive OR-flagged conditions, supporting the bounded expression earlier chance/stage predicates AND (GetLevel >=25 OR Solstheim location) [EV-0667]–[EV-0669].
- Assessment: Model C is falsified as an identity claim: the records show separate CLOC and SCPT QUST branches. Shared stage-10 handoff state does not prove shared event identity. The GOG condition evaluator supports a Solstheim alternative to the level-25 row for the `DLC2WE09` condition list, but this is a cross-build static inference and does not show when the list runs or that a level-one player naturally starts the encounter. Models A and B remain open for the main CLOC start chain because the native QUST has no own `GetLevel`, but script source and runtime start timing are unresolved. No vanilla level-one initiation is claimed.
- Discriminant: retain EV-0260 as the separate natural Steam test: exact active full profile/order, disposable level-one save, read-only observation of ordinary CLOC and world-event transitions, prerequisites, negative control, and repetition. The configured archive route lacks Dragonborn.bsa and the available PEX extractor is Misc-BSA-only; absence of loose PEX is not an archive-wide negative [EV-0663].

## C-OBJ1-Q81-WORLD-LEVEL-OR-LOCATION — hard level threshold versus Solstheim alternative

- Model A: `DLC2WE09` requires player level >=25; the Solstheim location row is an additional condition.
- Model B: the two consecutive OR-flagged rows are one alternative group, so GetLevel >=25 OR the Solstheim location satisfies that part of the condition list after its earlier chance/stage predicates.
- Evidence: native five-master `DLC2WE09` QUST row order and comparison values [EV-0657], raw CTDA bytes [EV-0665], pinned TES5Edit decoder for operator and OR bits [EV-0666], GOG 1.6.1179.0 identity-matched evaluator and caller screen [EV-0667]–[EV-0669].
- Assessment: B is supported as a static cross-build mechanism inference because the GOG evaluator collects consecutive OR-flagged condition items before combining the group with prior AND predicates. The captured list's trailing GetLevel and location rows therefore form an OR group under that evaluator. This does not establish the Steam evaluator's matching implementation, evaluation timing, satisfaction of the other conditions, actor spawn, quest startup, or a vanilla level-one result. A remains a build-transfer alternative until corroborated against Steam or a natural runtime observation.
- Q85 source screen: the official SMEN/SMQN/SMBN selector chain and the bounded trigger route add no explicit player-level predicate; the initial Windhelm passage topic's six INFO rows likewise contain no function-index-80 condition when associated by TIFC and serialized source order [EV-0389], [EV-0390], [EV-0661], [EV-0662], [EV-0664], [EV-0686]. Revision-pinned UESP describes ordinary paid ferry access before the cultists appear and a different dialogue check afterward [EV-0687]. This further supports B as a conditional static candidate; stage/chance satisfaction, Steam evaluation timing and natural level-one QUST startup remain unresolved.
- Discriminant: verify Steam condition-list grouping with build-attested code, or perform EV-0260's clean level-one Solstheim/world-event transition test while logging the exact QUST start and prerequisite state. Keep a level-25 control and the separate main-quest CLOC path.

## C-OBJ2-Q82-MITIGATION-INTERPOSITION-VS-SYNCHRONOUS-AWARD — equipment change window versus same-pass resolver

- **Model A:** a synchronous callback or player-accessible equipment transition occurs after armor mitigation but before the unblocked receiver scans worn ARMO, preserving protection while suppressing AV11/AV12.
- **Model B:** mitigation, selector callbacks, worn-armor scan, and UseSkill routing execute synchronously in the same resolver pass; official selector DATA[1] IDs 1/3/14 update a numeric result, with ID14 reading an ActorValue and potentially maintaining derived-value caches.
- **Model C:** a blocked hit takes the AV9 Block route and skips AV11/AV12 after the mitigation stage; this is a separate control, not by itself a bounty-qualified XP bypass.
- **Evidence:** GOG builder/receiver order and separate later `FUN_1406b9df0` route [EV-0670], [EV-0673]; synchronous selector visitor [EV-0671]; GOG function-ID handler dispatch [EV-0672]; PlayerCharacter UseSkill vtable target [EV-0674]; official five-master DATA/EPFT screen [EV-0675]; mutable enum/layout labels [EV-0676]; existing blocked route [EV-0222], [EV-0261].
- **Assessment:** EV-0683 retracts the EPFT-as-handler interpretation: official rows use DATA[1] IDs 1/3/14, while EPFT selects the function-data class. Captured handler 3/14 bodies write numeric results; handler 14's ActorValue getter may write derived-value caches on a miss in the traced direct path [EV-0683]–[EV-0685]. No equipment or HitData writer, authoritative ActorValue setter, UseSkill/AVSK sink, or event submission is identified in the bounded code. The exact ActorValueInfo callback target for AV138 remains unresolved. Model A is not identified; Model B is supported as synchronous result computation, with the cache side effect and callback limit retained. Model C is supported only as branch routing; positive protection, landed-hit eligibility, raw AV9/AV11/AV12, and raw AVSK are unmeasured. No OBJ-2 exploit or global negative follows.
- **Discriminant:** preserve EV-0260's exact Steam test: verified full order and disposable level-one save, ordinary unblocked physical hits with read-only event capture, naked/equipped protection controls, raw Heavy/Light/Block AVSK before and after repeated hits, plus blocked-hit controls. Map the unresolved function-data predicate only if it becomes the sole meaningful static uncertainty; do not transfer GOG RVAs.

## C-OBJ1-Q83-TPLT-WITHOUT-USES-TEMPLATE — serialized leveled links versus CLOC alias resolution

- **Model A:** the `DLC2CultistAmbush` aliases consume their serialized TPLT chain, resolve the `DLC2LCharCultist*` LVLN roots, and select actor variants using the list thresholds after the CLOC QUST starts.
- **Model B:** the TPLT/LVLN links are not consumed by the actual CLOC alias-fill route, or fixed NPC bases are assigned by another path; the serialized links alone do not establish level-dependent actor selection.
- **Evidence:** direct Dragonborn.esm parser linkage, LVLF/LVLO thresholds, NPC ACBS/TPLT fields and level-1 leaf records [EV-0677]; GOG 1.6.1179.0 TESNPC template-copy override and chain-state helper [EV-0678]; pinned record labels/layout [EV-0680]. The CLOC/world branch split and no explicit level row in the screened CLOC path are [EV-0654]–[EV-0669].
- **Assessment:** Both models remain open. The serialized chain supports a level-dependent actor candidate, while clear ACBS `UsesTemplate` bits complicate a direct inference. GOG generic template-copy code reads the base-template pointer/mask and branches on that bit, but does not identify these Steam aliases' runtime fill path. No level-one actor selection, pre-start native callback, profile winner, or CLOC bypass is established. The main CLOC route's screened records/fragments contain no explicit `GetLevel`; this bounded result does not exclude unexamined runtime/profile gates. No OBJ-2 causal edge follows.
- **Discriminant:** EV-0260 must capture a clean Steam level-one ordinary CLOC transition with exact active order, numeric Player level, QUST state/stage, alias fills and actor base FormIDs; compare a level-25 control and preserve the separate `DLC2WE09` world-event transition. A verified Steam call path from alias fill through TESNPC template resolution is an alternative static discriminator. Console, Papyrus, or plugin forcing is diagnostic only.

## C-OBJ1-Q87-LEVEL-WRITE-VS-LEVEL-UP-ACCEPTANCE — threshold update versus accepted menu action

- **Model A:** the stored Player level changes only after the player accepts a level-up by choosing an attribute; a prior pending threshold leaves GetLevel unchanged.
- **Model B:** once the Player progress pair reaches its threshold, StatsMenu `ProcessMessage(kUpdate)` writes GetLevel+1 outside the attribute-confirm callback.
- **Model C:** the `kUpdate` is dispatched only after an explicit level-up interaction, so the static threshold writer still occurs as part of acceptance.
- **Model D:** another registered writer such as FUN_140356a10 or FUN_140355210 commits the field independently before the StatsMenu path.
- **Evidence:** the exact getter and resolved attribute-confirm callback [EV-0689]; exact field setter, threshold predicate and candidate callers [EV-0691]; RTTI and slot-4 `kUpdate` mapping [EV-0692]; StatsMenu factory/constructor/destructor correction [EV-0693]; shared armor-skill progress object [EV-0694].
- **Assessment:** Model B is supported as a bounded GOG call path: StatsMenu's `kUpdate` handler checks the threshold and reaches the field writer, which is separate from the resolved attribute-confirm callback body. Model A is weakened if it requires that callback itself to be the only writer. Models A/C remain unresolved if “acceptance” includes opening or activating StatsMenu. Model D remains open because other direct callers/data references are not fully classified. No Steam or natural quest-gate result follows.
- **Discriminant:** resolve the data-table registrations of FUN_140356a10/FUN_140355210 and the UI message/input gate around the StatsMenu branch; then run EV-0260's natural Steam before-threshold, pending-before-interface, interface-open-without-attribute-selection, and accepted-state captures. Compare numeric GetLevel and the serialized base-data field without forcing stages or levels.

## C-OBJ1-Q88-STATSMENU-UPDATE-VS-LEVEL-UP-INPUT — periodic update versus user-triggered commit

- **Model A:** once threshold progress is due, an ordinary StatsMenu `kUpdate` can commit GetLevel before attribute selection; the menu's `+0x325` byte is an internal readiness condition.
- **Model B:** StatsMenu's due `kUpdate` is reached only after an explicit level-up UI/input transition, so its write occurs as part of the player's acceptance action.
- **Model C:** another registered Player writer such as `FUN_140355210` or `FUN_140356a10` commits the stored field earlier than the StatsMenu route.
- **Model D:** raw `+0x325` displacement matches from unrelated objects are mistakenly treated as the StatsMenu field's producer.
- **Evidence:** the exact stored-level setter and due-threshold paths [EV-0691]; StatsMenu RTTI/slot-4 `kUpdate` identity and factory lifecycle [EV-0692], [EV-0693]; shared armor-skill progress input [EV-0694]; complete bounded `+0x325` operand scan, soul-capture caller, unbounded store context, and 64-entry StatsMenu vtable prefix [EV-0695]. Natural Steam state remains unavailable under [EV-0260].
- **Assessment:** The GOG static update path supports a due-threshold write outside the resolved attribute-confirm callback. EV-0695 supports Model D as a methodological warning: `FUN_140717c50` is called on a soul-capture route, its target type is unresolved, and the separate `0x9628B0` code candidate is not in the first 64 StatsMenu vtable entries. This does not identify the StatsMenu byte's producer or decide whether the update is periodic or input-triggered. Model C remains unresolved because the two level-writer data-reference tables have no analyzed table-base refs and their runtime consumers are unknown. No Steam timing or level-one quest result follows.
- **Discriminant:** With verified Steam 1.6.1170.0, exact complete disposable-profile order, a naturally created clean save, and a read-only observer, record numeric GetLevel and serialized base-data level before threshold, after naturally pending progress, after the StatsMenu/update interface opens without attribute selection, and after attribute acceptance. Preserve ordinary menu/no-input controls; do not force levels or quest stages. If static work resumes, require a producer-backed same-object relation for the StatsMenu `+0x325` byte or a resolved registration/dispatch consumer for the extra writer tables.
