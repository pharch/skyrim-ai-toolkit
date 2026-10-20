# Results

## Starting evidence

EV-0300 identifies Skyrim.esm `DA09IncreaseLevelNodeSHARES` as a level-12 Story Manager node whose child is main DA09; the child QUST comes from Update.esm. Local UESP revision 3539493 lists *The Break of Dawn* at level 12 and describes Beacon and statue routes. The wiki evidence does not resolve whether the threshold gates item availability, dialogue, quest startup, or later progression.

## New evidence — EV-0306

Fresh direct-parser captures reproduce the node/global and main DA09 QUST. The Update.esm main quest override has `ENAM=LEVL` and its Start Game Enabled bit is clear under the QUST schema mapping in EV-0301. The MISC Beacon has no VMAD. Its callback is attached to main DA09's Gem alias: `OnContainerChanged` requests stage 100 when Player receives the Gem and the current stage is below 100. The statue alias callback requests stage 200 when Player activates the statue while carrying the Gem. Neither bounded PEX body has an explicit GetLevel check.

The separate `DA09ChangeLocation` helper is a CLOC quest whose Story Manager child requires a main-DA09 stage-0 condition and uses `DA09ChangeLocChance`. Its fragment adds the main quest's Gem alias reference to a BossContainer alias. It does not start main DA09. The beam-shooter callback checks for main stage 300; Shade death requests stage 400; the Update patch fragment only relocates the Gem alias under stage/location conditions. No independent main-DA09 `Start` call was found in these interpreted candidates.

The five-master byte-level candidate scan found no direct Beacon REFR/LVLI reference; its Beacon candidates include a QA container and quest aliases. A group-aware join of all 15,037 Skyrim.esm DIAL and 31,465 INFO records maps 20 DA09-owned topics and 25 INFO children. None contains a function-80/GetLevel condition. Forty GetLevel conditions occur elsewhere in the full INFO corpus. This repairs the direct parser's omitted nested DIAL parent context and is still a source-file screen, not an active-profile winner.

## Assessment

The source supports the level-12 LEVL Story Manager path as the only main-DA09 startup route found in the screened official corpus. The Beacon/statue callbacks request stages but do not prove that a stopped event-scoped quest starts. The CLOC placement helper is downstream of main stage 0, not an independent pre-start Beacon path. H1 is therefore not supported by the inspected source; H2 is supported within this boundary, but the exact Steam outcome remains unverified. GOG EV-0272 provides a predictive event-scope guard model only; it is a separate 1.6.1179.0 build.

The required discriminating run is a clean, exact Steam AE 1.6.1170.0 level-one save with a verified complete active order. Acquire the Beacon through ordinary gameplay, then activate the statue while recording DA09 running state, stage, alias fill, and Story Manager context. Repeat at level 12. Do not use console stages, injected scripts, or altered plugins. Current Observer readiness does not verify this telemetry, so no live result is claimed. See the EV-0306 private capture manifest for source and artifact hashes.
