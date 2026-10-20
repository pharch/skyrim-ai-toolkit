# Results — Dawnguard alternate entry source path

## Question and rival models

Q-0063 asked whether the level-10 `DLC1VQ00Node` → `DLC1VQ00ChangeLocation` route is the only natural route into `DLC1VQ01` / *Awakening*, or whether an ordinary Fort dialogue path can stage the main quest without that Story Manager helper.

- **H1:** A dialogue callback can advance `DLC1VQ01` without a `GetLevel >= 10` condition. The discriminant is a source-linked DIAL/INFO → TIF/QF path that reaches the main quest, separate from the level-gated messenger helper.
- **H2:** The other dialogue responses only set rumor/helper state or depend on the level-gated handoff, with no source path that stages the main quest.

## Captured route

The fixed official-master join covers 97 DIAL topics and 147 INFO children owned by `DLC1VQ00`, `DLC1VQ01`, `DLC1VQ01MiscObjective`, and `DLC1VQCastleGuard`. The source order is the five official masters only; it is not a user-profile winner. Dawnguard.esm is SHA-256 `1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4`.

The source-linked Fort route is:

1. `DLC1VQ00` (QUST `0200D90E`) has the native xEdit `DNAM - General\Flags\Start Game Enabled` field set to `1`. Its QUST-owned `DLC1VQ00IntroTopic` DIAL `0200D8D4` has Durak INFO `0200D908`; the attached `DLC1_TIF__0100D908` sets the owning quest to stage 20. Its conditions are actor identity and `GetStageDone(DLC1VQ00, 20) = false`; there is no `GetLevel` condition on this response.
2. Durak's `DLC1VQ00IntroC` DIAL `0200D8D0` has INFO `0200D8E2`, whose `DLC1_TIF__0100D8E2` sets `DLC1VQ00` to stage 50. Its conditions are Durak identity and `DLC1VQ00 < 50`; again, no `GetLevel` condition.
3. The VQ00 stage-50 QF fragment `Fragment_7` sets `DLC1VQ01MiscObjective` to stage 10. This starts the separate Isran/Agmaer helper path; it is not yet the Awakening quest.
4. The Isran INFO `0200D8E4` on `DLC1VQ01IntroB2` sets the helper to stage 120. The Isran INFO `0200D8ED` on `DLC1VQ01IntroC1` sets it to stage 150. Neither response has a level condition. Stage 150 enables Tolan's `DLC1VQ01TolanIntroTopic` INFO `0200E8A6`, whose `DLC1_TIF__0100E8A6` sets the helper to stage 180.
5. The helper's stage-180 QF `Fragment_16` calls `DLC1VQ01.SetStage(10)`. The main quest's stage-10 fragment enables the Dimhollow objective and map marker. This is a source-level main-quest transition from dialogue, beyond setting rumor state.

A second Tolan INFO, `02019AAB`, is owned by `DLC1VQ01` and its TIF calls `DLC1VQ01.SetStage(10)` directly. It is recorded as a corroborating callback, but its runtime availability before the main quest starts is unknown.

Separate VQ00 approach INFO records `0200D057` and `0200D058` do require `GetLevel >= DLC1VQMinLevel` (10). That preserves the known level-gated approach branch while distinguishing it from the Fort DIAL route above. The CastleGuard fragments examined only open/close the vampire-castle gate and do not supply a VQ01 start edge.

## Quest flags and attached scripts

The native xEdit export confirms `DLC1VQ00` has `Start Game Enabled = 1`, `Starts Enabled = 1`, and `Run Once = 1`. `DLC1VQ01` has `Run Once = 1` and `Start Game Enabled = 0`; its four `GetInCell` conditions are under its objective-target fields for the two Dimhollow cells, not whole-quest or level-start conditions. `DLC1VQ01MiscObjective` is also not Start Game Enabled. This makes the mapped `SetStage` callbacks the source-level handoff into those quests. VQ00's Messenger alias has `defaultsetstagealiasscript` with `stage=100` and `TriggerType=1`; that alias behavior is separate from the Fort dialogue chain above.

All 28 QF/TIF PEX files linked to the four joined QUST owners parsed as PEX 3.2 with all bytes consumed. The capture also contains the level-gated `DLC1VQ00ChangeLocation` helper QF and three attached alias scripts; the generic `defaultsetstagealiasscript` itself was not found by the narrow extractor, and that miss is not evidence of absence. The linked PEX streams were found in the installed `Skyrim - Misc.bsa` (17,713,449 bytes; SHA-256 `ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d`); the configured Data directory has no `Dawnguard.bsa`. Extraction used the existing narrow reader, and every recovered stream's source name, offset, size and SHA-256 is recorded in the ignored transaction capture. This establishes where these exact compiled streams came from, not which loose-file or profile override the game loads.

## Decision and limits

**H1 is supported as a strong source-level level-one candidate; H2 is falsified within the mapped official-source route.** The alternate chain starts from VQ00 dialogue and reaches `DLC1VQ01.SetStage(10)` without a serialized level condition; it is separate from `DLC1VQ00ChangeLocation`, the helper selected by the level-10 Story Manager node. The native xEdit field query confirms the VQ00 start-enabled flag in the fixed five-master scope.

This is **not** a level-one runtime result or vanilla reproduction. Dialogue availability, quest-running state, `SetStage` startup behavior on the Steam build, alias fill, the active profile winner, and useful access/progression remain unverified. Existing EV-0313/EXP-0055 GOG static research shows a conditional `Quest.SetStage` → `EnsureQuestStarted` path, but that is GOG AE 1.6.1179.0 evidence and cannot be transferred to Steam 1.6.1170. The exact next player test is a fresh verified Steam AE 1.6.1170 save held at level 1 with the complete selected profile order recorded; without console or injected stage/script changes, test the Durak/Fort dialogue chain and capture before/after quest-running flags, stages, aliases, journal entries, and Dimhollow access with the read-only observer. Retain EV-0260's missing full order/save/observer gate. This investigation adds no causal edge to the armor-XP objective.
