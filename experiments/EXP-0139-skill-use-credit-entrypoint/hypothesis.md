# EXP-0139 hypothesis outcome

- **H1 falsified within the screened official source layer:** the complete official five-master PERK EntryPoint 22 screen contains no non-positive Heavy/Light armor modifier, and the installed AVIF use coefficients for both skills are positive [EV-0262], [EV-0704]. This does not cover optional plugins or every possible runtime writer.
- **H2 supported for the captured GOG path:** after PlayerCharacter's positive-points guard, `FUN_14077d090` sends its computed skill credit through EntryPoint 22 before adding the returned float to the per-skill progress field [EV-0221], [EV-0703].
- **H3 falsified for the scoped official numeric sources:** Heavy and Light Armor base AVIF coefficients are nonzero, and every official `Mod Skill Use` row has a positive amount; the award-side layer therefore yields no source-record zero candidate in the screened five masters [EV-0262], [EV-0704].

This leaves an engine-level separation between HitData/protection and skill credit, but no vanilla player-accessible way to set that credit to zero from these records. A qualifying hit with armor-derived protection and zero AVSK still requires EV-0260 runtime evidence.
