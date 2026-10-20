# Results — Q-0040 / TX-20261016-0036

## Question and models

Q-0040 asked whether DA04's level-15 Story Manager node gates only the Septimus send-player helper or all ordinary starts/early progress of main DA04.

- **H1 helper-only:** the GetLevel >= 15 node selects the letter-delivery helper; a separate book path starts/advances main DA04 below that level.
- **H2 all-ordinary-entry gate:** the book or dialogue path depends on that helper or another serialized level condition before DA04 starts or reaches its early stages.

Predictions were recorded before captures in the frontier and EXP-0043 protocol. Source facts below are from the prepared Skyrim.esm file through the direct TES4 parser, not a native xEdit view or a winning record export.

## Observations

1. The earlier complete five-official-master SMQN/SMEN census [EV-0300] found DA04's `GetLevel >= 15` SMQN node `0010481D` (`DA04SeptimusFindPlayerNode`) selects QUST `0010481C` (`DA04SeptimusSendForPlayerQuest`), not main DA04 (`0002D512`). The helper QF PEX `Fragment_0` adds the `SeptimusLetter` item to `CourierQuest`.
2. Skyrim.esm QUST `0002D512` (`DA04`) has raw DNAM `11013c000000000007000000`. Under the versioned TES5Edit `dev-4.1.6` QUST schema, the first two bytes are flags `0x0111`; bit 0 is `Start Game Enabled`. The QUST has stage INDX entries 1 and 5, and the captured QUST CTDA set contains no function-index-80/GetLevel predicate.
3. TES5Edit's `dev-4.1.6` QUST VMAD schema stores the fragment-to-stage mapping and alias script table in VMAD. The retained decoder maps `Alias_RuminationsBook` to alias ID 19, binds `DA04RuminationsScript` to alias 19, and maps DA04 stage 1 to `QF_DA04_0002D512.Fragment_18`.
4. The QUST ALST entry for alias ID 19 is named `RuminationsBook` and carries ALFR `00032787`. REFR `00032787` (`DA04Book1Ref`) has NAME `00032785`, resolving to BOOK `00032785` (`DA04RuminationsOnElderScrolls`). The BOOK itself has no VMAD; the read script is attached to the quest alias.
5. The extracted base Misc.bsa PEX for `DA04RuminationsScript` shows `OnRead` calling `GetOwningQuest()` followed by `SetStage(1)`. `Fragment_18` then sets the `ReadCrazyBook` quest property true and calls `SetStage(5)` on DA04. The local Skyrim Papyrus API index reproducing the CK Wiki description says `SetStage` waits for quest startup if it needs to start the quest; the main QUST is also configured Start Game Enabled.
6. The captured Septimus DIAL/INFO subset and UESP revision 3564369 are retained, but the direct-parser INFO query was an EditorID-substring query rather than a full child-INFO relation census. They do not settle every later dialogue condition. UESP is treated only as a route lead.

## Assessment

H1 is supported and H2 is falsified for the serialized initial-start and stage-1/5 Ruminations-book path. The >=15 node gates the helper that places a letter in the courier's inventory; the source contains a separate book-alias route into main DA04's first stages. The source configuration is inconsistent with interpreting the >=15 node as the main DA04 start gate.

This is a mechanism inference from source records and extracted Papyrus bytecode. It is **not** proof of a vanilla level-one run, physical route availability at level one, the active-profile winning records, or DA04 progression beyond stage 5. No causal edge to the armor/HitData/XP mechanism is supported.

## External lane and limits

The native five-master xEdit retry failed before process enumeration at PowerShell step `processes-before` with WSL `UtilBindVsockAnyPort:307: socket failed 1`. It produced no native record fields. The direct-parser records and VMAD decoder remain the only record interpretation in this investigation. No profile-specific order was verified; Steam runtime identity is EV-0109; no loaded Observer or clean level-one game result was available.

The discriminating runtime follow-up is a fresh, unmodified level-one save at the verified target/order: ordinary no-read control, read the fixed alias book without level/quest forcing, observe numeric level and DA04 running/stage state, and repeat. The predicted transition is DA04 stage 1 followed by stage 5 while the player remains level 1. Any console stage/level forcing or injected script is diagnostic only.

## Provenance

- EV-0300 source identity for prepared Skyrim.esm: SHA-256 `2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107`. This investigation queried the same prepared Skyrim.esm copy; no target-specific override resolution is claimed.
- Extracted script archive: base `Skyrim - Misc.bsa`, SHA-256 `ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d`.
- Relevant PEX hashes: `DA04RuminationsScript.pex` `b30b132ebf9cee2c0bb6c9c5107cc0bd0d16f390378ff0e402f261027a6b9672`; `QF_DA04_0002D512.pex` `d9ba59e5972f1d89cf11b74ec39e1dd5575d4f4154f6c025f905804d6811b58c`; `QF_DA04SeptimusSendForPlayer_0010481C.pex` `ed4935e7e0c70bd21b042076938f504f40211dfccf0149cfe81ad7ceec0fb9bb`.
- Fragment VMAD layout: TES5Edit `dev-4.1.6`, `Core/wbDefinitionsTES5.pas`, `wbVMADFragmentedQUST` and `wbRecord(QUST)` definitions: https://raw.githubusercontent.com/TES5Edit/TES5Edit/dev-4.1.6/Core/wbDefinitionsTES5.pas
- `SetStage` documentation route: Papyrus Index entry referencing the Skyrim Creation Kit Wiki: https://papyrus.bellcube.dev/skyrimse/script/quest/function/setstage/ (queried 2026-10-16; CK Wiki target returned HTTP 403 through the browser tool).
- Local UESP DA04 capture: revision 3564369 in `uesp-da04.json`; secondary only.
- All raw wrappers, PEX files, disassemblies, decoded VMAD, tool receipts and hashes are in the TX-20261016-0036 ignored capture directory and its manifest.
