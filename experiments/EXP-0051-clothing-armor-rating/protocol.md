# Protocol

1. Use TES5Edit dev-4.1.6's `wbDefinitionsTES5.pas` as the field schema: BOD2 contains first-person flags followed by the Armor Type enum (`Light Armor`, `Heavy Armor`, `Clothing`); ARMO DNAM is signed armor rating divided by 100; ARMO header flag bit index 2 is Non-Playable.
2. Read only the five configured official master files using the strict Python 3.12 dispatcher and `tools.plugin_reader.read_plugin`. Preserve each exact source-file SHA-256; do not infer active-profile winners from file order.
3. Count every ARMO by source plugin and BOD2 armor type. List records with type 2 and positive DNAM, retaining record flags and source FormID; distinguish records marked Non-Playable.
4. Query the existing GOG Skyrim AE 1.6.1179.0 Ghidra project read-only at the `Actor::GetArmorBaseFactorSum` vtable target already used by the HitData builder. Compare its implementation with the EV-0222 worn-ARMO eligibility selector. Treat GOG findings as separate-build predictions only.
5. If a player-usable record and plausible protection path remain, specify an exact Steam 1.6.1170.0 level-one hit/control test with numeric Heavy/Light AVSK and measured protection. Do not force armor or quest state.
