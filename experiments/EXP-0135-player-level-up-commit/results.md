# Results

## Bounded static result — 2026-10-20

EV-0688 captures local UESP `Skyrim:Leveling` revision 3636185. The page describes earned level-ups being held pending and the accepted level updating to the highest earned. This is secondary grounding only; the local corpus doctor does not verify dump acquisition, completeness, or license provenance.

EV-0689 preserves identity-checked, read-only GOG 1.6.1179.0 Ghidra queries, the matching Address Library, and CommonLibSSE-NG revision `b93280e832f263dbef44e44cbe2936622a02f91a` source declarations. `Actor::GetLevel` at RVA `0x668F30` forwards to `TESActorBaseData::GetLevel` (AE ID 14384; current GOG RVA `0x1D7B20`). Its body reads the 16-bit actor-data `level` field. When `PCLevelMult` is set, it scales from the Player level and applies the record's min/max bounds.

The PlayerCharacter `UseSkill` slot `0xF7` calls the skill-progress helper at RVA `0x77D090`. That helper accumulates per-skill progress, advances a skill actor value at its threshold, adds separate character-level XP, and dispatches a skill-level event. The one statically identified listener is `SkillIncreaseToMiscStatHandler`; its resolved callback updates a miscellaneous statistic using the skill actor value. The LevelUpMenu Accept override registers `addHealth`, `addMagicka`, `addStamina`, and sound callbacks. The attribute callback calls `FUN_14077d700`, which refreshes skill thresholds and attribute values and reads GetLevel for display/profile processing. No direct write to the Player base-data `level` field appears in these resolved bodies.

This narrows the timing models without selecting one. The `GetLevel` getter does not derive its return from cumulative skill XP in the resolved path. An automatic threshold/notification writer to the Player base-data field remains possible, and the acceptance-time writer was not identified. The capped broad displacement scan found 3,136 writer-candidate functions and analyzed only its first 16, so it is not a negative writer census. Steam before-threshold, pending, and accepted states remain unobserved under EV-0260; no vanilla level-one bypass or OBJ-2 outcome is established. EV-0690 subsequently identifies a GOG-only causal route from the HitData worn-armor AV11/AV12 call into that shared skill-progress/character-XP routine, as documented below.

## Exact next actions

1. Resume static tracing only with producer-backed writes to the Player's `TESActorBaseData.actorData.level` field; do not treat broad displacement hits as evidence about the Player.
2. Preserve the runtime discriminator under EV-0260: verified Steam 1.6.1170.0, complete disposable profile order, clean save before threshold, natural pending-level state before acceptance, then accepted state; capture numeric GetLevel and relevant serialized fields with a read-only observer.
3. Continue other independent P0 frontier work while those live prerequisites remain unavailable.


## Cross-domain update — EV-0690

A fresh identity-checked GOG query of `FUN_1406bcaa0` shows the unblocked Player receiver branch calling vtable byte offset `+0x7b8` (slot `0xF7`) with armor skill index 11/12 and the calculated point value. EV-0674 maps that exact PlayerCharacter slot to `FUN_140739050`; EV-0221 shows its positive-points branch entering `FUN_14077d090`; EV-0689 maps that routine to per-skill progress and separate cumulative character-level XP. This establishes a static causal edge from the bounded armor-skill award path into character-XP accumulation. It does not establish live ordinary-hit coverage, protection, a zero-XP exploit, Steam behavior, or when the gate-visible Player level field changes.

### Exact next investigation — Q-0087

Map the GOG `TESActorBaseData.actorData.level` read offset from `FUN_1401d7b20`, then identify producer-backed stores to that exact field with Player/base-form provenance. Compare the writers' direct incoming call paths to `FUN_14077d090` threshold/event handling and the LevelUpMenu apply path. An acceptance-only writer supports the deferred-field model; a threshold/notification writer supports automatic advancement. A capped displacement scan is not a negative census. Preserve the Steam before-threshold/pending/accepted discriminator under EV-0260.

## Q87 result and cross-domain update — EV-0691–EV-0694

The GOG field is `TESActorBaseData+0x10`, the 16-bit value read by `GetLevel`. `FUN_1401d7ba0` stores the new halfword there and then notifies through the containing actor base form. Its threshold helper `FUN_14077d650` compares the Player progress pair (`pfVar1[1] <= pfVar1[0]`), emits `UILevelUp`, reads current Player GetLevel+1, and calls the setter [EV-0691].

RTTI identifies `FUN_1409611e0` as StatsMenu `ProcessMessage`; the pinned vtable slot and CommonLib declarations map it to slot 4 and `UI_MESSAGE_TYPE::kUpdate`. That path loads the global Player's +0x9b8 progress pointer and runs the threshold test/writer. A separate factory registration associates the name `StatsMenu` with `FUN_14096e280`; that callback obtains an instance through the UI manager and calls constructor `FUN_1409607f0` [EV-0692], [EV-0693]. Correction: EV-0692 called `FUN_140960d40` a constructor based on its vtable store. The lifecycle query shows it releases owned fields and is a cleanup/destructor body reached from the vtable's first-entry wrapper. The actual constructor is `FUN_1409607f0`; the RTTI and ProcessMessage slot mapping remain valid [EV-0693].

The cross-domain trace now connects positive HitData-derived armor skill points to the same progress value used by the level threshold. PlayerCharacter slot 0xF7 reaches `FUN_140739050`, which passes PlayerCharacter+0x9b8 to `FUN_14077d090` for positive points. The skill helper increments the accumulated-progress float in the inner progress object; StatsMenu independently loads the same Player+0x9b8 pointer and checks the same float pair. When due and the StatsMenu update path runs, it can write the stored level field [EV-0689]–[EV-0694]. This is a GOG static causal bridge from hit-earned armor skill points to level progress and eventually the `GetLevel` field.

This does not establish the exact menu action or whether that update precedes attribute-selection acceptance. The direct caller registrations for `FUN_140356a10` and `FUN_140355210`, two setter callers, and Steam behavior remain open. It is not a natural level-one quest start, a live ordinary-hit result, a protection measurement, or a zero-armor-XP bypass. Keep EV-0260 for those runtime observations.

### Exact next investigation — Q-0088

Determine when the registered StatsMenu factory/update path runs relative to the player's level-up input, and classify the remaining Player level-field writer registrations. Resolve the untyped data references for `FUN_140356a10` and `FUN_140355210`; identify the UI message/input gate around StatsMenu `kUpdate`; compare the first update after menu display with attribute confirmation. Do not infer acceptance timing from the static menu name or GOG RVAs. Preserve the natural Steam pending/open-menu/accepted discriminator under EV-0260.

## Q88 result — bounded displacement discrimination (EV-0695)

The complete GOG memory-operand scan for displacement `+0x325` reports five accesses across four functions. They include the StatsMenu `ProcessMessage` read, a set-true wrapper (`FUN_140717c50`), a byte-zero writer in `FUN_1406ebea0`, a comparison, and a byte-one store at RVA `0x9628B9` for which Ghidra reports no function owner [EV-0695]. The set-true wrapper has one analyzed direct caller, `FUN_1406c8d10`; its bounded route uses `InventoryChanges::FindBestSoulGemVisitor` and displays soul-capture feedback on the Player branch. The target object's dynamic class is not identified, so the call does not establish that it writes the StatsMenu instance's byte.

The no-function store at `0x9628B9` loads a pointer through `[RCX+0x18]`, checks it, sets byte `+0x325`, then returns. Its queried address has zero analyzed xrefs. The candidate address `0x9628B0` does not appear among the first 64 entries read from the RTTI-identified StatsMenu vtable at RVA `0x19026C0` [EV-0695]. This is a bounded prefix only: the table end, nonvirtual helper relations, and indirect dispatch are not established.

This result corrects an offset-only assumption, not the Q87 threshold writer. Equal numeric displacement matches are not evidence of a shared object field. The StatsMenu byte's producer and the order of `kUpdate` relative to level-up input remain unresolved; the `FUN_140355210`/`FUN_140356a10` table consumer is also unknown. No new causal edge is added, and the Q87 GOG bridge from positive armor-skill points into shared level progress remains unchanged [EV-0694]. No Steam timing, natural level-one access, effective protection, or zero-XP armor outcome follows.

### Exact next action

Close Q88 as a bounded static result while keeping the competing timing models open. Continue with the highest-information ready frontier question. Retain EV-0260's natural Steam sequence: verify exact build and full disposable-profile order; capture a clean pre-threshold save, natural pending progress, StatsMenu/update display without attribute selection, and accepted attribute state; compare numeric GetLevel and serialized base-data level through a read-only observer. Do not force level, stage, or plugin state.
