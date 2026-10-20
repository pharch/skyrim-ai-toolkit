# Results

## Initial source lead

Revision-pinned local UESP describes two quest-giver paths for Dragonborn: two cultists via `DLC2CultistAmbush`, or three via `DLC2WE09`. The main-quest dialogue path follows The Way of the Voice and the first subsequent city/town entry. The Way of the Voice page separately labels a level-25 requirement for cultists in world encounters only. The Cultist article says player level affects which combat variant appears, which is distinct from the encounter's start eligibility [EV-0653].

These secondary-source statements suggest separate stage-driven and level-gated paths. They do not establish official record conditions, Story Manager behavior, or any level-one reproduction. The exact next action is to compare the official `DLC2WE09`, `DLC2CultistAmbush`, and `DLC2MQ01` records and their trigger writers for player-level predicates versus main-quest stage conditions.

## Native QUST first pass — EV-0654

The isolated native SSEView query passed the scoped AE preflight for Steam `SkyrimSE.exe` ProductVersion 1.6.1170.0 and loaded exactly Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm, and Dragonborn.esm plus the SkyrimSE.exe pseudo-file. It returned 483 field rows for Dragonborn.esm `DLC2CultistAmbush` QUST FormID `0403546D`; the winner is limited to this official-five-master view [EV-0654]. The TSV and result JSON hashes are recorded in the private receipt and the Q81 transaction summary.

The record's event field is `CLOC`; its stage indexes are 1, 10, and 255. The complete QUST export contains six CTDA function rows: `IsCommandedActor`, `GetInFaction`, `GetIsVoiceType`, and three `LocationHasKeyword` functions for habitation, capital, and town locations. No `GetLevel` function occurs in this QUST's own dialogue or alias conditions [EV-0654]. The record nevertheless attaches `DLC2WE09ActorScript` and `DLC2WECultistAmbushPlayerScript`, references `DLC2MQ01` FormID `04017F8E`, and carries a `DLC2WE09Chance` GLOB reference `04033C24` [EV-0654].

This does not settle H1 versus H2: a player-level condition could be in an attached PEX, an upstream Story Manager node, a linked INFO path, or native code. It raises H3 because the supposedly separate `DLC2WE09` world encounter has multiple record-level links into the `DLC2CultistAmbush` QUST. The event's `CLOC` field is not itself proof of the exact quest-start transition, and the absence of `GetLevel` here is record-bounded rather than a global negative.

## Native and source follow-up — EV-0655–EV-0664

The native five-master `DLC2MQ01` export has seven CTDA functions (GetDisabled, three GetInCurrentLoc, two GetInFaction, GetStageDone), no `GetLevel`, and 11 VMAD stage-fragment bindings including three stage-10 fragments [EV-0655]. The distinct Story Manager children are `DLC2CultistAmbushNode` -> `DLC2CultistAmbush` and `DLC2WEPriorityQuests`/`DLC2WENode` -> `DLC2WE09`; they descend through separate CLOC and SCPT branches under separate parents [EV-0656], [EV-0658]. Neither child node has a `GetLevel` CTDA in its own rows [EV-0656].

The official `DLC2WE09` QUST contains earlier chance/stage rows followed by `GetLevel` comparison 25 and `GetInCurrentLoc` Solstheim [EV-0657]. Its attached world-encounter script and stage aliases share the `DLC2MQ01` quest-state handoff with the main-quest path in loose PSC. The fragments are source evidence only: they differ in actor/note setup but both call `DLC2MQ01.Start`, wait, fill objective aliases, set stage 5, and write `DLC2WE09Chance=5`; the actor alias also writes owning-quest stage 10 under its hit/nearby-death conditions [EV-0663]. No compiled PEX was found loose. Dragonborn.bsa is absent from the configured archive path, and the available extractor is scoped to Misc BSA, so no archive-wide PEX absence is established [EV-0663]. `DLC2WENode` is an SMBN child of `DLC2WEPriorityQuests`, carrying `WEEnabled` and `DLC2WEStart`/`DLC2WERoadStart` event data [EV-0664].

## CTDA operator and GOG evaluator screen — EV-0665–EV-0669

The raw `DLC2WE09` CTDA bytes encode the `GetLevel` row as function index 80, comparison 25.0, type `0x61`, followed by `GetInCurrentLoc` function index 359, comparison 1.0, type `0x01`; both type bytes have bit 0 set [EV-0665]. At pinned TES5Edit commit `f8b209cb5bc9efcb2cd8c4aa8694de3227c3d783`, the decoder maps type operator bits `0x60` to >= and bit 0 to Or [EV-0666].

GOG Address Library version/hash evidence maps IDs 29888 and 29924 to RVAs `0x49FA30` and `0x4A0720` for GOG AE 1.6.1179.0 only [EV-0667]. The identity-checked GOG `FUN_14049fbb0` evaluator collects consecutive OR-flagged items, short-circuits that group, then ANDs it with the prior unflagged accumulator; applied to the separate native `DLC2WE09` record this supports `earlier chance/stage predicates AND (GetLevel >=25 OR GetInCurrentLoc Solstheim)` [EV-0668]. A wrapper/caller census retains register setup and 22 incoming callers but does not locate the QUST list's evaluation point [EV-0669]. Do not transfer these RVAs to Steam 1.6.1170.0 or infer when the condition list is evaluated.

The bounded result falsifies the same-QUST identity model: CLOC `DLC2CultistAmbush` and SCPT `DLC2WE09` are separate QUST branches despite sharing stage handoff code. It supports a Solstheim location alternative in the GOG evaluator model, not a verified level-one encounter. No profile-specific winner, Steam natural start, or vanilla reproduction is established. EV-0260 remains the exact clean Steam requirement: full active profile/order, disposable level-one save, read-only state observation, ordinary triggers, controls and repetition.
