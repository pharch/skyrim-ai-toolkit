# Results

## Starting evidence

EV-0300 maps SMQN `000DC9E1` (`DA08KickerNode`) to helper QUST `000DC9E0` (`DA08RumorPointer`) under `GetLevel >= DA08MinLevel` (GLOB `000DC9E2`, 20.0). The prior census did not inspect the main DA08 start/alias/dialogue path. The local UESP lead is revision 3578672; it is not engine evidence.

## New record and script results — EV-0305

Fresh direct-parser queries reproduce SMQN `000DC9E1` (`DA08KickerNode`) -> helper QUST `000DC9E0` (`DA08RumorPointer`) under `GetLevel >= DA08MinLevel`, GLOB `000DC9E2` = 20.0. The level-gated child is not main QUST `0004A37B` (`DA08`).

Main DA08's QUST `DNAM` first word is `0x0111`; EV-0301's QUST schema mapping interprets bit 0 as Start Game Enabled. The helper's `DNAM` first word is `0x0100`, with bit 0 clear. The DIAL capture returned 18 DA08-named topics, 17 with QNAM main DA08 and one (`DA08BalgruufRumorsTopic`) with QNAM the helper. The main-owned set includes the Balgruuf and Nelkir quest-start branch topics.

Six attached PEX files were extracted from the version-105 `Skyrim - Misc.bsa` (SHA-256 `ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d`) and bounded-disassembled. The helper's `Fragment_1` sets main `DA08QuestScript.PlayerGotRumor=true`; `Fragment_2` stops the helper. Main QF `Fragment_14` displays objective 10 and, if the helper is at stage 10, advances that helper to 20. The door alias `OnActivate` handler advances main DA08 from stage 40 to 50 only after that stage check. These are helper-state and later-progression interactions, not a level-20 condition on main-Q startup.

H1 is supported and H2 is falsified for main DA08 startup in the inspected source records. UESP revision 3578672 lists ReqLevel 20 and Dragon Rising context, but that is a gameplay lead; it does not override the direct source distinction. No active-profile winner, live quest state, level-one dialogue/access, INFO child conditions, or vanilla reproduction is established. See the capture manifest for raw query, archive, PEX, and UESP hashes.
