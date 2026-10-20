# EXP-0014 results

## Record and script observations

- Dragonborn.esm SMQN `02024003` has a `GetLevel >= GLOB 02024004` condition, with global value 36.0, and points to child QUST `02038FB0` (`LEVL`) which references main QUST `02024002` ([EV-0233], [EV-0234]).
- Main QUST `02024002` has no Start Game Enabled bit in its first DNAM flag byte. Its Haknir alias has schema flag `0x8000` (Initially Disabled) and an ALRT/LCRT location-reference fill resolving to ACHR `02037FEA` in `DLC2GyldenhulBarrowLocation` ([EV-0231]–[EV-0234]).
- QUST `DLC2WE13` has a top-level `GetStage(mainQ)==20` condition and assigns book `0203661A` to its Actor1 alias. This inspected encounter is downstream of main-Q stage 20 ([EV-0233]).
- Eleven Deathbrand book references lie outside Gyldenhul Barrow, with no raw XESP field. Placement is not access proof ([EV-0234], [EV-0235]). The earlier loose-root inventory failed to locate the book script; EV-0270 corrected that bounded inventory by recovering its PEX from `Skyrim - Misc.bsa`.
- The recovered book `OnRead` checks `GetStageDone(mainQ,20)` and only then calls `SetStage(mainQ,1)`. It does not call quest `Start()` ([EV-0270]).
- Main-QF stage mapping identifies stage 10 -> `Fragment_0`, stage 20 -> `Fragment_11`, and stage 90 -> `Fragment_23`. Stage 10 registers an update whose handler checks PlayerRef's location and the Shoal boss alias/3D state before it may set stage 20. Stage 20 resets Shoal aliases and starts its scene. Stage 90 calls `Alias_Haknir.StartBattlePhase(0)` ([EV-0270]).
- EV-0271 expands the official-master raw-reference audit. DLC2Init QUST `02016E02` stage 100 maps to `Fragment_4`; it reads Player `GetLevel` and `DLC2dunHaknirTreasureQSTMinLevel` (bound to GLOB `02024004`), compares `level >= minLevel`, and only on true calls main-Q `SetStage(10)`. The current static global value is 36.0 ([EV-0233], [EV-0271]).
- The level-event helper QUST `02038FB0` stage 10 maps to `Fragment_0`, which calls main-Q `SetStage(10)` and stops the helper. Its LEVL event is behind the SMQN's `GetLevel >= 36` condition ([EV-0233], [EV-0271]).
- Misc QUST `0203661B` stage 10 maps to `Fragment_0`, which only reads main-Q `GetStage`; if it equals 20, it displays its own objective and map marker. Its stage-20 fragment completes its own objective and stops itself. The complete bounded PEX contains no call to main-Q `Start()` or `SetStage()` ([EV-0271]).
- The boss script calls main-Q `SetStage(100)` from `OnDying`; phase 0 moves Haknir, calls `EnableNoWait(self,true)`, and starts combat ([EV-0245], [EV-0270]). This is downstream of the stage-90 fragment in the examined chain.
- The exact little-endian screen for GLOB `02024004` found only two non-NAVM raw references in the five official masters: DLC2Init VMAD and the SMQN CTDA. The main-Q scan found no non-NAVM matches in Update.esm, Dawnguard.esm, or HearthFires.esm; Dragonborn.esm has raw references requiring record/PEX semantics. Both scans and their false-positive NAVM payload matches are preserved in EV-0271.
- Native xEdit QUST retrieval failed before SSEView launch when WSL interop returned `UtilBindVsockAnyPort:307: socket failed 1`; no native fields were produced and an unchanged retry is not planned ([EV-0247]). These results are direct-parser/PEX evidence, not native xEdit exports or a profile winner.

## Assessment

The bounded five-master and recovered-PEX audit supports gated progression for every inspected writer that can set main-Q stage 10: the level-event helper descends from the `>=36` Story Manager gate, and DLC2Init's stage-100 fragment tests the same min-level global before setting stage 10. The book waits for stage 20, the inspected misc quest reads stage 20 without starting or advancing the main quest, and the main-Q stage-90 fragment owns the known Haknir enable/combat call. This weakens the book-as-independent-start and ordinary pre-gate death models.

This supports H2 only within the inspected static scope. It does not exclude dynamic/native or uninspected runtime writers, establish profile-specific winners, prove current runtime alias filling, or demonstrate a level-one result. No clean level-one transition, actor enable, Haknir death, or stage-100 result was observed. EV-0260 still records missing profile/order/save/read-only state-capture prerequisites. No causal edge to OBJ-2 armor mitigation or hit-earned armor XP is supported.

## Next discriminant

The exact static step is complete for the identified book, DLC2Init, LEVL-helper, misc-quest, and main-QF paths. A remaining discriminant requires a user-controlled Windows run on a verified target/profile with a disposable clean level-one save and a read-only method that captures numeric player level, main-Q running/stage state, and Haknir's enabled/dead state; compare the same observations at level 36. Do not force level or stage. The currently staged Observer does not capture Story Manager state (EV-0260), so use only a separately verified read-only quest-state observer if one becomes available. Until those prerequisites exist, continue with another independent P0 investigation.
