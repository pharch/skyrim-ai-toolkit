# Protocol

1. Through the strict Python 3.12 dispatcher, parse the exact official five masters and resolve ARMO, ENCH, and MGEF records by FormID. Treat the result as source winners, never as an active-profile winner.
2. Classify Clothing using both schema-valid ARMO BOD2 and BODT Armor Type fields. Preserve short or ambiguous forms as unclassified. Decode ENIT, EFID, EFIT, MGEF DATA, conditions, archetype, and primary ActorValue.
3. Separately screen exact-five-master MGEFs whose primary ActorValue is Health and whose ResistValue is an applicable magic, elemental, poison, or disease resistance ActorValue.
4. Resolve the CommonLib Actor vtable entries against the matching GOG Address Library. Use the GOG vtable RTTI subobject offset to choose the Actor's `MagicTarget` subobject; query slot `0x0A` and follow its bounded direct callees in the existing GOG project read-only.
5. Compare the CommonLib method/field declarations with the decompiled function and the decoded source records. Do not infer live damage, Steam behavior, item accessibility, or zero AVSK from static mapping.
6. Keep the clean level-one Steam comparison under EV-0260: equipped candidate versus matched unequipped control, qualifying incoming spell/element hit, exact target order, damage measure, raw Heavy/Light AVSK, other skill deltas, and level preservation.

Primary schema reference: [TES5Edit dev-4.1.6 `wbDefinitionsTES5.pas`](https://raw.githubusercontent.com/TES5Edit/TES5Edit/dev-4.1.6/Core/wbDefinitionsTES5.pas). Local source hashes and per-run GOG metadata are recorded in [results](results.md).
