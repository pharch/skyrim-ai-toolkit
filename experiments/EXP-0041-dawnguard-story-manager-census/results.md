# EXP-0041 results

Dawnguard.esm contains 36 SMQN entries (26 Dawnguard-origin FormIDs, 10 Skyrim-origin FormIDs) and one Skyrim-origin SMEN entry. A function-index-80 scan finds exactly one `GetLevel` CTDA across all 37 serialized records: SMQN `0200D911` (`DLC1VQ00Node`). The CTDA type byte `0x64` decodes as `>=` with a global operand. EV-0298 resolves the operand as GLOB `0200D912`, `DLC1VQMinLevel`, value 10.0, and the node's child as QUST `0200D90B`, whose Messenger alias points to Durak.

The sibling `DLC1VQ00VampireAttackNodeAM` and `DLC1VQ00VampireAttackNodePM` records have function-index-74 (`GetGlobalValue`) conditions. No other Dawnguard.esm SMEN/SMQN record has function index 80. The direct-parser census is not a native xEdit field export, merged official-master view, profile winner, BSA script census, or runtime observation ([EV-0299], with GLOB/alias mapping in [EV-0298]).
