# EXP-0139 results

## GOG progression code

Fresh identity-checked GOG 1.6.1179.0 query `gog-query-20261020T062010Z` resolves `FUN_14077d090` with two direct incoming calls: `FUN_140739050` and `FUN_14077d480` [EV-0703]. The PlayerCharacter override `FUN_140739050` rejects a points argument unless it is strictly greater than zero, then calls the progression helper [EV-0221], [EV-0703].

In the helper's supported skill-progress branch, it loads four floats from the skill's AVIF-backed AVSK data. CommonLib maps these fields as `useMult`, `offsetMult`, `improveMult`, and `improveOffset`; the code conditionally transforms the input as `useMult * points + offsetMult`. It then sets PlayerCharacter context fields identifying the current skill, dispatches selector decimal 22 / hex `0x16` through `FUN_140386070` on that float, clears the temporary context, and adds the resulting float to the per-skill progress field before the threshold/skill-advance loop. The CommonLib enum maps decimal 22 to `kModSkillUse` [EV-0700], [EV-0703]. The exact meaning of all auxiliary context fields and caller flags is not required for the observed selector-before-add order.

The direct path has no call from the `Mod Skill Use` visitor back into HitData construction in the captured scope. Thus the code presents a distinct award-side control point; this does not prove a player-accessible modifier exists or that armor protection remains positive under any particular effect.

## Five-master record results

The read-only source scan covered 153 AVIF records across the five official masters. `Skyrim.esm:00000451 AVHeavyArmor` has AVSK values `[3.8, 0.0, 2.0, 0.0]`; `Skyrim.esm:00000452 AVLightArmor` has `[4.0, 0.0, 2.0, 0.0]`, in CommonLib order. Native xEdit exports independently name these fields as Skill Use Mult, Skill Offset Mult, Skill Improve Mult, and Skill Improve Offset [EV-0704]. Both native xEdit queries loaded only the five official masters; they do not establish a profile-specific winner.

The complete five-master PERK EntryPoint 22 screen contains eight rows. All use positive function data; Heavy Armor and Light Armor `EPMagic_IsAdvanceSkill` rows are positive 1.20 multipliers. The remaining source screen includes positive Rested/Lover effects and an Enchanting-only Dragonborn staff-workbench multiplier [EV-0262]. No non-positive official AVIF use coefficient or `Mod Skill Use` row for AV11/12 appears in this scope.

## Assessment and limits

The Player skill progression route has an award-side modifier after the positive input guard and before the progress field update. The official source data screened here offers no zero/negative Heavy or Light Armor modifier. The result falsifies only a zero source within this exact record scope; other plugins, Creation Club files, runtime effects, and other native paths are not excluded.

No live hit, positive armor protection, Steam runtime result, raw AVSK delta, level-one state, or vanilla exploit was tested. The `Mod Skill Use` path remains a possible engine location for a new candidate if another player-accessible source is found, but this investigation did not find one. EV-0260 remains decisive for any eventual OBJ-2 claim.
