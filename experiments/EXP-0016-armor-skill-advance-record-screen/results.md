# EXP-0016 results

## Static evidence

The official five-master scan and schema-backed interpretation are preserved in EV-0262 and the [private capture note](../../.local/alignment/transactions/TX-20261016-0002/skill_advance_record_screen.md). The five files contain 1,633 MGEF and 523 PERK records. The MGEF primary-ActorValue screen found only four AV9/11/12/117/119/120 matches: two Fortify Armor enchantment effects and two Fortify Armor alchemy effects, all primary AV11 or AV12. It found no direct primary-AV target for Block or AV117/119/120.

Eight PERK records use EP22 (`Mod Skill Use`). Three entries have `EPMagic_IsAdvanceSkill` conditions for the targeted award skills: `doomWarriorPerk` applies a positive 1.20 multiplier for AV11 Heavy Armor and AV9 Block; `doomThiefPerk` applies a positive 1.20 multiplier for AV12 Light Armor. The remaining Skyrim entries are positive rested/lover/skill multipliers. Dragonborn's `DLC2StaffEnchantingMult` is 0.05 and requires both `IsCurrentFurnitureObj` for FURN `02017736` and skill AV23 Enchanting. No targeted armor/Block EP22 amount is non-positive. No player ownership, winning override, or runtime award behavior is inferred.

H3 is supported only for the existence of an official award-side skill-use modifier path and decoded skill conditions. H4 is supported only for the bounded negative: no AV117/119/120 MGEF primary target and no non-positive EP22 multiplier for AV9/11/12 in these five files. No causal edge connects the award-side records to HitData mitigation.

## Runtime result

Not applicable to this static screen. No live hit, armor protection, or XP result is claimed.

## Next discriminant

Q-0004 remains unresolved. A later candidate test must use a verified target/profile and read-only observer to compare a valid incoming hit, effective armor mitigation, and raw AVSK deltas against an XP-positive control. EV-0260 records that the selected disposable profile, complete order, save, deployed/loaded Observer, and live bindings are unavailable. Continue independent P0 static work while that environment lane is unavailable.
