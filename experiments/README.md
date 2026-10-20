# Experiment records

New investigations use a separate `EXP-####-slug/` dossier with `hypothesis.md`, `protocol.md`, `predicted-outcomes.md`, `raw/`, `results.md`, and `implications.md`. Record build/profile identity, baseline, controls, exact observations, tool versions, raw hashes and rollback plan. Raw evidence is immutable and stays under ignored `.local/`; tracked results cite stable evidence IDs.

`EXP-0001`–`EXP-0005` and `EXP-0007` are verbatim imported historical dossiers, not current test authorization. Their source hashes and evidence links are in `research/LEGACY_SOURCE_PROVENANCE.tsv`; status statements remain historical until independently reproduced. No `EXP-0006` source dossier was present in the imported source inventory.

Current work includes `EXP-0010` (WICast/Marked-for-Death static candidate), `EXP-0011` (DA14 gate), `EXP-0012` (GOG hit-to-skill path), `EXP-0013` (negative AV39 blocked-hit protocol), `EXP-0014` (Haknir pre-gate start path), `EXP-0015` (DA14 stage-406 trigger path), `EXP-0016` (official armor skill-advance record screen), `EXP-0017` (blocked-hit armor-protection protocol), and `EXP-0018` (DA14 alternate writer and scene screen). These records preserve static/runtime boundaries; no live result is claimed in EXP-0013, EXP-0014, EXP-0015, EXP-0017, or EXP-0018.

`EXP-0019` bounds the DA07 pamphlet alias mechanism, `EXP-0020` records the DA07IntroTrigger actor-pair stage-7 path, and `EXP-0021` records the separate DA07 Museum-trigger scene route. None has a live level-one result. EXP-0020's static placement screen disfavours ordinary actor-pair co-entry from the initial state; EXP-0021 retains the player-accessible house-entry clip and scene-readiness discriminants.

`EXP-0022` records a GOG-only trace of the inferred Papyrus Quest.SetStage startup path and its Story Manager Event-ID guard. It does not establish alias fill or Steam/runtime behavior.

`EXP-0023` audits the Dawnguard Drain Vitality-labelled shout records that reuse MFD words; their custom SPELs omit the MFD AV39 MGEF in the captured records. Acquisition, Script-archetype semantics, runtime target and WICast behavior remain open.

`EXP-0024` records a bounded read-only tool/interface audit, with current strict-dispatcher and research-state outputs kept private. It distinguishes direct parsing, native Windows xEdit, GOG Ghidra, exact-profile, and live Observer scopes; it does not run software tests or establish gameplay behavior.

`EXP-0025` records the corrected VQ01 Book alias owner, its stage-10 enable parent, and the separate Crypt02 stage-17 trigger candidate. It is a static record/PEX investigation; alias filling, trigger behavior, player-only access and level-one progression remain unobserved.

`EXP-0026` records the Dimhollow portcullis child's XESP parent and the recovered generic activator PEX. That script toggles animation and linked collision without a quest-stage call; marker/child enable state, rubble collision and level-one access remain unresolved.

`EXP-0027` resolves the source meaning of Dimhollow's UESP `Min: 6` field as an encounter-zone summary, not an entrance gate. Official cell records point to the same ECZN; physical level-one access and profile-specific behavior remain untested.
EXP-0028 records a fresh GOG ActiveEffect base-vtable audit: save/load serializes timer, magnitude, flags, references and logical ID fields, while base Update/Finish are stubs. Functional persistence and exact Steam behavior remain untested because no designated save or ActiveEffect observer is configured.

EXP-0029 traces the GOG Enchanting craft-confirm callback to one station-selected `UseSkill` dispatch and the shared skill-progress helper, then decodes the base Skyrim.esm Enchanting workbench's `WBDT.usesSkill` as AV23. Raw Enchanting progress, input-factor comparisons, and the 15→16/20→21 thresholds remain unmeasured because the live Observer and a raw AVSK reader are unavailable.

EXP-0030 records the schema-decoded Dawnguard portcullis child/parent enable flags. The base records encode ordinary parent-state inheritance with no Initially Disabled bit; loaded state, collision, passage and level-one access remain unobserved.

`EXP-0031` screens the zero-effective-rating armor-XP lead. A bounded private export reports that positive-base Heavy Armor at displayed rating zero still earned hit XP, consistent with the GOG source selector's positive base-DNAM check. No current Steam runtime, raw AVSK, or matched protection result was captured.

`EXP-0032` audits the current read-only archive route. The supported Papyrus CLI extracts from `Skyrim - Misc.bsa` and its literal scan optionally adds `cc*.bsa`; no tested Dawnguard archive route is exposed. The archive itself was not opened, so this is a tool-scope blocker and not a script-absence result.

`EXP-0044` records the ProcessTrapHit/ordinary-hit shared HitData mitigation helper and bypass of the known AV11/AV12 resolver branch in the bounded GOG static call graph (EV-0302). Positive protection, complete award absence, Steam behavior, and raw AVSK remain unresolved.

`EXP-0045` classifies the 28 indirect receiver-handler sites and uses EV-0315 to trace two temporary handles plus the HitData sourceRef through generic GOG handle helpers. Concrete cleanup target classes, derived sourceRef overrides, and the exact Steam clean-save protection/AVSK comparison remain unresolved.

`EXP-0046` classifies the ten indirect calls in shared GOG `FUN_1407ddf50`. A weapon-selected target ActorValue conditionally scales `totalDamage` for weapon-bearing calls, while the captured ProcessTrapHit route leaves the weapon null and skips that branch. It keeps this input distinct from AV39/armor rating and from Steam protection, AVSK, and level-one reproduction.

`EXP-0047` finds that the DA08 level-20 Story Manager node selects `DA08RumorPointer`, while main DA08 is serialized Start Game Enabled and owns the main quest dialogue topics (EV-0305). This narrows the gate to the rumor helper; INFO conditions, physical level-one access, profile winners, and live state remain untested.

`EXP-0053` resolves the GOG BOD2 Armor Type field to runtime `ARMO+0x1BC` and shows the inventory visitor used by the `+0x274` armor-factor cache skips Clothing before rating accumulation (EV-0311). This falsifies the Clothing protection candidate for this GOG cache path; Steam damage, AVSK, and level-one reproduction remain open.

`EXP-0054` traces Light/Heavy DNAM rating inputs through the GOG cached armor factor used by physical-trap mitigation and its bypass of the known normal resolver AV11/AV12 branch (EV-0312). EV-0315 narrows receiver handle provenance without resolving concrete cleanup classes. This is a static candidate only; Steam damage, AVSK, and level-one reproduction remain open.

`EXP-0055` investigates whether native Papyrus `Quest.SetStage` starts, requires, or only partially mutates a stopped level-gated quest, using DA02/DA04 book callbacks as source examples. EV-0313 supports a conditional GOG start-now path before stage application and corrects the earlier `SetCurrentStageID` identity; DA02 runtime guards, functional access, and the exact Steam level-one transition remain open.

`EXP-0056` resolves the GOG/source `ENAM=LEVL` to `TESQuest+0xE0` field map and its conditional SetStage entry guard for DA02, DA09, and DA06 (EV-0314). The exact Steam event/ready state, callback reachability, and gameplay transition remain unresolved.

`EXP-0057` traces serialized QUST `DNAM.General.Flags` bit 0 into GOG `TESQuest+0xDC.0` and compares DA02/DA04/DA06/DA09 source values (EV-0316). `EXP-0058` and EV-0318 resolve the GOG post-file-load slot-19 sweep after QUST parsing/registration; first natural `Quest.SetStage` callback order, Steam state, and level-one access remain unresolved.

`EXP-0058` resolves the GOG post-parse, post-file-load TESQuest slot-19 dispatch path (EV-0318); its first natural `Quest.SetStage` callback ordering, Steam state, and level-one progression remain unresolved under Q-0057's bounded result.

`EXP-0065` / EV-0327 follows Q-0064's PlayerCharacter cleanup global to PlayerCamera teardown, maps primary slot 0x98 to the transition handler for +0x730, and records the complete direct/computed writer scan with unknown origin/type limits. Indirect descendants and Steam protection/AVSK behavior remain unresolved.

`EXP-0066` / EV-0328 screens the four PlayerCharacter final-release fields; `+0x8F8` is set from a resource path ending in `1stPerson\Skel` and released by a teardown helper, but its class and destructor target remain unknown. Q-0064 remains unresolved.

EXP-0067 / EV-0329 maps PlayerCharacter +0x9A0/+0x9A8 refcount-final releases and traces the shared setter to a generic resource-derived value. The stored object's class, finalizer, and skill-progress descendants remain unresolved; Q-0064 stays active.

EXP-0068 / EV-0330 traces the AutoVanity HUD callback through type-0x17 dispatch to Scaleform ShowElements. This bounds one PlayerCamera callback branch away from native skill progress; Q-0064 remains active.

EXP-0069 / EV-0331 maps a conditional NiNode finalizer candidate for PlayerCharacter +0x8F8. The exact first-person skeleton NIF root and child tree remain unobserved; Q-0064 remains active.

EXP-0070 / EV-0332 traces a candidate PlayerCharacter +0x9D0 producer through a TES-owned cell/resource query; the stored object's class and finalizer remain unresolved. Q-0064 stays open.

EXP-0071 / EV-0333 traces the +0x9A0/+0x9A8 producer through a data-selected model-resource adapter. Slots +0xB8/+0xE8, loaded root class, and final slot+0x8 target remain unresolved; Q-0064 stays open.

EXP-0072 / EV-0334 maps PlayerCharacter +0x730 cell-scene attach/detach through NiNode candidate methods and an NiAVObject-compatible child/parent field at +0x30. The concrete child finalizer remains unresolved; Q-0064 stays open.

EXP-0073 / EV-0335 maps PlayerCamera+0x28 as the active camera-state pointer and the index-9 ThirdPersonState slot+0x10 callback. Two helper descendants, the +0xA0 finalizer, other state targets, and the selected teardown state remain open; Q-0064 is unresolved.

EXP-0074 / EV-0336 traces ThirdPersonState+0xA0 through PlayerCharacter slot+0x378 and a dynamic slot+0x150 lookup. NiNode's same-offset method is only a conditional comparator; the runtime receiver and member finalizer remain unresolved.

EXP-0075 / EV-0337 maps PlayerCharacter slot +0x378 to a TLS/nested-field context getter; its returned class, slot +0x150 target, and finalizer remain unknown.

EXP-0076 / EV-0338 maps FirstPersonState and BleedoutCameraState slot+0x10 callbacks. Other camera states, the Bleedout finalizer, and teardown state selection remain open.

EXP-0077 / EV-0339 maps FreeCameraState and IronSightsState slot+0x10 callbacks; shared helpers and remaining camera states are still open.

EXP-0078 / EV-0340 maps FurnitureCameraState and PlayerCameraTransitionState slot+0x10 callbacks; Furniture's nested finalizer and state indices 2, 7, 10, and 12 remain open.

EXP-0079 / EV-0341 resolves PlayerCamera constructor states 2, 7, 10, and 12 and their slot+0x10 callbacks; the shared +0xA0 member finalizer and ProcessTrapHit reachability remain open.

EXP-0080 / EV-0342 traces ThirdPersonState+0xA0 from a type-erased slot+0x150 producer to refcounted slot+0x8 cleanup; the member type and ProcessTrapHit link remain open.

EXP-0081 / EV-0343 maps the reference-counted argument and wrapper caller for the PlayerCharacter+0x378 slot+0x150 lookup; the receiver class remains unresolved.

EXP-0082 / EV-0344 resolves the PlayerCharacter global receiver and AnimatedCameraStartHandler callback owner for the slot +0x150 lookup; the selected context class and returned member finalizer remain unknown.

EXP-0083 / EV-0345 maps the two AnimatedCamera handler wrappers and their BSFixedStringCI-type-consistent argument flow into FUN_1408e6500; the lookup receiver class remains unknown.

EXP-0084 / EV-0346 captures the five formerly omitted PlayerCharacter cleanup callsites; all eight indirect sites now have field/interface context, while dynamic target tables remain unresolved.

EXP-0085 / EV-0347 traces the PlayerCharacter+0x8F8 first-person skeleton resource path through the generic mesh loader; the exact NIF root class and finalizer remain unresolved.

EXP-0086 / EV-0348 maps the +0x9D0 descriptor fallback's key-2/key-1 table lookup; selected object classes remain data-dependent.

EXP-0087 / EV-0349 maps the +0x9A0/+0x9A8 model-resource adapter and sorted member lookup; concrete output classes remain data-selected.

EXP-0088 / EV-0350 maps the +0x9A0/+0x9A8 setter modes, reference counts, and model-resource caller; stored object type remains unresolved.

EXP-0089 / EV-0351 maps FUN_1402b8510's cell+0x130+8 return; its non-null producer and result class remain unresolved.

EXP-0090 / EV-0352 maps the PlayerCamera global table and destructor; five owned-object dispatches remain unresolved.

EXP-0091 / EV-0353 resolves PlayerCamera+0x128 to bhkRigidBody and its slot+8 destructor; the body's child array remains unresolved.

EXP-0092 / EV-0354 proves the initial PlayerCamera rigid-body child array is empty during its first slot+0x150 cleanup pass; later population remains unresolved.

EXP-0093 / EV-0355 traces the ProcessTrapHit scene traversal into rigid-body physics constraint updates; remaining helper and indirect branches stay open.

EXP-0094 / EV-0356 resolves the factory-created hkpConstraintInstance slot+0x30 gate to zero, excluding one conditional physics list-removal branch for that exact class.

EXP-0095 / EV-0357 maps the factory-created hkpConstraintInstance slot-0 finalizer to callback/member cleanup and TLS allocation. Its callback and embedded member descendants remain unresolved.

EXP-0096 / EV-0358 maps the hkpConstraintInstance callback-array consumer and direct call boundary; callback population and concrete targets remain unresolved.

EXP-0097 / EV-0359 separates chain-instance cleanup from potential island/entity and post-collision command carriers; exact factory-object membership remains unresolved.

EXP-0098 / EV-0360 maps the ProcessTrapHit-created hkpConstraintInstance into its entity constraint record; callback producers and descendants remain unresolved.

EXP-0099 / EV-0361 maps direct callers and virtual slots for the exact hkp add/remove callback consumers; no producer or callback class is identified.

EXP-0100 / EV-0362 corrects the island owner type label and maps its serialized entity/constraint collections; factory-object membership remains unresolved.

EXP-0101 / EV-0363 withdraws the EV-0362 broad-scan writer negative because only the first 2,048 accesses were printed.

EXP-0102 / EV-0364 maps hkpSimulationIsland EntityPtrs insertion/merge and corrects EV-0360's constraint +0x10 interpretation. Live membership and AV11/AV12 remain open.

EXP-0103 / EV-0365 separates constraint-data +0x40/+0x48 fields from the hkpConstraintInstance callback array; fixed/malleable wrapper slots +0x128/+0x188 remain open.

EXP-0104 / EV-0366 maps ProcessTrapHit constraint wrapper setup, two empty callback constructors and the bounded hkpConstraintInstance vtable. Callback writer candidates and terminal finalizers remain unresolved.

EXP-0105 / EV-0367 maps hkpConstraintInstance finalization and deletion callback dispatch at entry slot +0x18; callback entry producers and targets remain open.

EXP-0106 / EV-0368 maps the ProcessTrapHit hkpConstraintInstance creation-time wrapper retain/release balance; later callback writers and terminal releases remain open.

EXP-0107 / EV-0369 classifies six hkp-region +0x40/+0x48 candidates by exact receiver; the 1,271-function overlap remains open.

EXP-0108 / EV-0370 maps hkpConstraintChainInstance removal and final-delete callback phases; chain-factory ownership remains open.

EXP-0109 / EV-0371 screens the chain factory's pointer-window and direct-call ownership context; no ProcessTrapHit edge is established, so Q-0064 continues at receiver-backed callback writers.

EXP-0110 / EV-0372 classifies FUN_140b48150 as a transform vector writer on constraint-data storage; the callback producer search continues.

EXP-0111 / EV-0373 classifies a same-offset candidate as a typed vector record/list path; Q-0064 returns to exact ProcessTrapHit teardown indirect calls.

EXP-0112 / EV-0374 synthesizes DA04 initiation and physical-trap armor routing as separate P0 candidates; Q-0064 moves to +0x8F8 resource/finalizer resolution.

EXP-0113 / EV-0375 maps ProcessTrapHit constraint removal callbacks and endpoint record cleanup; Q-0064 continues at PlayerCharacter+0x8F8.

EXP-0114 / EV-0376 bounds the unowned FUN_140b56a80 data references and selects an exact +0xB8 callsite census.

EXP-0115 / EV-0377 records a capped +0xB8 callsite scan and exact receiver screening for two displayed physics-range candidates.

EXP-0116 / EV-0378 compares exact mapped physics tables with the still data-selected cleanup fields. Q65-H1/H2 remain proposed; common slot +0x8 is not a class discriminator.

EXP-0117 / EV-0379–EV-0382 traces VQ01's Fort SetStage request through the GOG startup and required-alias preflight guards. Static conditional candidate; runtime and functional access remain open.

EXP-0120 / EV-0391–EV-0394 corrects the Grotto TIF receiver: `GetOwningQuest().SetStage(20)` targets helper QUST 000955CF; its stage-20 fragment kills the Hunter alias and requests main DA05 stage 60. The ordinary main stage-50 route requests helper stage 10. Clean dialogue availability and Steam fresh-state startup remain unresolved.

EXP-0121 / EV-0395–EV-0396 maps WE13 troll creation to event-linked WETravel markers and grounds the generic “cave troll” label to a revision-cited local UESP page. No fixed cave route or level-one runtime result is established; the clean trigger/state discriminator remains open.

EXP-0122 / EV-0397 maps two bounded GOG caller routes into the HitData skill resolver; the event producer, callback owner, ordinary-hit coverage, and all Steam protection/XP outcomes remain unresolved.

EXP-0123 / EV-0398–EV-0402 maps official Clothing resistance enchantments to Health MGEF ResistValues and the GOG Actor `MagicTarget::CheckResistance` calculation. This is a separate magic/element protection candidate; level-one acquisition, measured Steam damage, and numeric Heavy/Light AVSK remain untested.

EXP-0124 / Q-0075 screens exact official-master references and inventory/list chains for deterministic acquisition paths to the Clothing resistance candidates; source-defined availability remains separate from physical level-one access and the Steam protection/AVSK test.
EXP-0125 / Q-0076 follows the fixed Arch-Mage boots source into the First Lessons and Under Saarthal quest records, checking explicit player-level CTDAs against the complete five-master GetLevel census while keeping dialogue, door and live access separate.

EXP-0126 records Savior's Hide's exact Light Armor DNAM, linked Resist Magic/Poison enchantment fields, and DA05 stage-100 reward path, then bounds the GOG magic-resistance and HitData `physicalDamage` routes. A magical producer-to-AV11/12 link, natural level-one acquisition, effective Steam protection, qualifying hit, and numeric AVSK result remain unestablished [EV-0414]–[EV-0421], [EV-0260].

EXP-0127 / Q-0078 maps the five-master MS06/MS06Start Story Manager, dialogue/TIF, placed-trigger and scene routes. The helper scenes stage the helper/rumor quests; the Falk-note request to main stage 10 fails the inspected GOG initial guard, while Steam startup, alias fill, missing trigger-script behavior, and the clean level-one transition remain open [EV-0422], [EV-0260].

EXP-0128 / Q-0079 resumes the GOG HitData worker caller screen. EV-0423 corrects EV-0397's worker census to 95 unique direct callers, 33 decompiled bodies, and 62 remaining; the reported 64 is the stored-caller array cap. Review the remaining exact callers for a tag-0xB event producer, while keeping ordinary-hit coverage and the exact Steam protection/AVSK observations open.

EXP-0140 investigates whether Silus carries the DA07 Museum key before the level-20 start and whether a natural level-one key path can open the keyed house boundary; UESP's holder summary is not treated as proof of timing or gameplay.
