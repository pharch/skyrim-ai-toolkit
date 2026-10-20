# EXP-0136 results — Q89 bounded selector-0x55 screen

## GOG code path

Fresh read-only GOG AE 1.6.1179.0 captures identify `Actor` and `PlayerCharacter` vtable slot `0x100` as `FUN_14068f0c0`, which traverses entry-point perk records and dispatches handler IDs. In `FUN_14072a500`, each eligible non-clothing item's candidate armor rating is passed by pointer to `FUN_140386070(0x55, actor, item, &value)`; the value is reloaded and accumulated only after the callback. The adapter confirms the GOG executable hash and disables auto-analysis; no RVA is transferred to Steam [EV-0696].

CommonLib source commit `b93280e832f263dbef44e44cbe2936622a02f91a`, `BGSEntryPoint.h`, names selector `0x55` `kModArmorRating`. The handler ID is `PERK DATA[1]`; EPFT is the function-data class [EV-0681], [EV-0683].

## Official record screen

The complete configured official five-master screen contains 785 PERK entry rows and 31 selector-0x55 rows (Skyrim 15, Update 3, Dawnguard 7, Dragonborn 6; HearthFires 0). All 31 use EPFT 1 / OneValue. Three use DATA[1]=1 / SetValue with EPFD 0.0; 28 use DATA[1]=3 / Multiply with positive factors 1.1–2.0. No negative multiplier appears in this scope [EV-0697].

Two zero rows are linked from MGEFs by raw FormID references and accepted native xEdit exports:

- `ArmorFFSelf100` (Skyrim.esm `000CDB75`) is a Peak Value Modifier for Damage Resist and names `DragonhideSpellPerk`; `DragonhideSpellPerk` sets selector 0x55 to zero without a CTDA.
- `DLC2StandingStonesEarthEffect` (Dragonborn.esm `0201DFA0`) is also a Peak Value Modifier for Damage Resist and names `DLC2StandingStoneEarthPerk`; its selector-0x55 SetValue-zero row has one CTDA for `HasMagicEffect(000CDB75) == 0.0`. Its paired selector-0x24 row has a matching condition. TES5Edit dev-4.1.6 maps function index 214 to `HasMagicEffect`, with Param1 type Magic Effect. Equality-to-zero as absence is an inference from boolean condition semantics, not a runtime result [EV-0697].
- `dlc2BBDrunkenMaster` has a third SetValue-zero row but no raw FormID references in the five-master scan. Its actual source/application path remains unknown.

The native queries were accepted by exact EditorID against the official five-master view. An earlier Earth query using a Dragonborn-local FormID was rejected after load-order remapping and is not evidence. No profile winner, Creation Club coverage, active effect lifetime, or live condition evaluation is established [EV-0697].

## Outcome and cross-domain boundary

Q89 is complete as a bounded static source result: selector 0x55 can modify the cached per-item armor factor, and scoped official data includes rows that set it to zero. This result does not show that an equipped item remains protective, that total protection remains positive, or that armor XP becomes zero. The hit resolver's armor eligibility scan and skill points are separate; Q90 traces the HitData points input. The Steam discriminator still requires a matched landed hit, measured positive protection, and raw AVSK before/after under EV-0260.

Local UESP revision captures report Dragonhide's 80% physical-damage effect and stale displayed armor totals, and list Alteration Ritual Spell acquisition requirements; these remain secondary leads only [EV-0698].
