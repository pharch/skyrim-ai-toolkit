# Protocol

1. Use the strict Python 3.12 dispatcher and prepared official master files with the read-only direct parser. Preserve exact source hashes; do not interpret the direct parser's official order as an active-profile winner.
2. Decode Skyrim.esm `SMQN 0009E1AF`: CTDA function/comparator/global, parent event, and child FormID. Resolve the global and Update.esm DA02 override using the pinned TES5Edit schema.
3. Decode QUST `0004D8D6` flags, event field, stage-fragment bindings and aliases. Keep Start Game Enabled, journal display, dialogue, alias fill, story event, and encounter presence distinct.
4. Join all DA02-owned DIAL topics to INFO children by full GRUP ancestry, decode all INFO conditions, and collect their attached TIF script names.
5. Scan every subrecord in the five prepared official masters for references to main/helper quest IDs, book, shrine activators, aliases, and candidate external callers. Raw FormID matches are leads until records and scripts are interpreted.
6. Extract only identified bound PEX streams through the tested Skyrim - Misc.bsa route. Map `Start`, `SetStage`, scenes, and stages to their owning quests. Preserve archive hash, offsets, exact byte counts, and parser status.
7. Record the narrow source finding and a clean Steam level-one/control protocol. No console or injected state change counts as vanilla reproduction.
