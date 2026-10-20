# EXP-0138 results

## Primary selector names and complete record screen

The CommonLibSSE source commit maps the nine pre-snapshot selectors as follows: `0x00 kCalculateWeaponDamage`, `0x01 kCalculateMyCriticalHitChance`, `0x02 kCalculateMyCriticalHitDamage`, `0x11 kModEnemyCriticalHitChance`, `0x12 kModSneakAttackMult`, `0x1A kModBashingDamage`, `0x1C kModPowerAttackDamage`, `0x23 kModAttackDamage`, and `0x24 kModIncomingDamage` [EV-0700]. These are enum labels, not an independent proof of call behavior.

The configured five-master source screen contains 785 PERK entry-point DATA rows, including 160 rows across the nine selectors [EV-0700]. Four rows have a decoded four-byte `EPFD` value of `0.0`:

- `Skyrim.esm:00107831 DeftMovement`, selector `0x24`, handler ID 3 / Multiply Value, float function data, six entry conditions.
- `Skyrim.esm:000E863F MQ105PhantomFormPerk`, selector `0x24`, Multiply Value by zero, no entry CTDA; raw PRKR linkage is to `MQ105PhantomFormActor`.
- `Skyrim.esm:000EB24A InvulnerableActorZeroIncomingDamage`, selector `0x24`, Set Value to zero, no entry CTDA; source references are carriage drivers/horses and `MQ101CartHorse`.
- `Dragonborn.esm:0201E7F0 DLC2BlackBookCompanionsSafePerk`, selector `0x23` (outgoing attack damage), Multiply Value by zero; the raw MGEF/ACTI occurrences point into the companion safety content.

The raw whole-record scan found eleven exact little-endian FormID occurrences across these rows (3, 1, 5, and 2 per candidate, respectively). These are candidate references, not a semantic decoder or active-effect observation [EV-0700].

## Deft Movement field review

The accepted native xEdit query loaded the official five-master scope, selected the `Skyrim.esm` PERK `DeftMovement`, and exported 147 fields [EV-0701]. Its record-level conditions include Light Armor skill 100 and perk checks for Wind Walker and Matching Set; the condition flags determine their logical grouping and are not inferred here. The entry-level conditions include `GetRandomPercent <= 10`, `WornHasKeyword ArmorHeavy == 0`, and worn boot, cuirass, gauntlet, and helmet keywords. The DATA row is selector `0x24`, handler ID 3, EPFT float, EPFD `0.0`.

The revision-pinned local UESP Light Armor page describes Deft Movement as a chance to avoid damage and reports its Light Armor 100 prerequisite. It is secondary context only; exact page provenance is revision 3602632, timestamp 2026-08-03, URL `https://en.uesp.net/w/index.php?title=Skyrim:Light_Armor&oldid=3602632` [EV-0702].

## Cross-source static inference

GOG AE 1.6.1179.0 `FUN_1407ded20` dispatches selector `0x24` against HitData `+0x50` before `FUN_1407ddf50` copies the then-current `+0x50` value into `+0x54` [EV-0699]. PlayerCharacter slot `0xF7` rejects points that are not strictly greater than zero before entering the skill progress helper [EV-0221]. Together with the zero-multiplier Deft Movement record, these sources predict no armor skill progress from the `+0x54` input on a proc for which all Deft Movement conditions are true. This is a conditional mechanism inference across a GOG analysis build and installed source records; it is not live Steam behavior.

The other zero rows are not player-use candidates within the raw five-master reference screen. Deft Movement is intermittent and its stated effect is to avoid damage; neither it nor the other rows demonstrates a qualifying hit where the worn armor itself provided effective protection. Light Armor 100 plus the record conditions also leave level-one reachability unresolved. Thus Q91 does not meet OBJ-2's no-total-avoidance, positive-protection, repeatability, or level-one requirements.

## Negative results and limits

- No active-profile winner was resolved; only the official five-master scope was queried.
- No Creation Club records, active effects, effect duration, live hit, Steam address mapping, measured armor protection, raw AVSK, Block XP, or level-one perk route were observed.
- The four source-level zero values do not establish when a handler runs, whether its conditions are true, or whether a hit event is retained after zero damage.
- EV-0260 remains the required Steam landed-hit/protection/raw-AVSK test. Q92 now follows the distinct award-side `Mod Skill Use` entry point to check whether XP credit can be controlled after a positive hit-points input.
