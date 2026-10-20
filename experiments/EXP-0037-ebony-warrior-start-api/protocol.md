# EXP-0037 protocol

## Target and lane

- Installed target identity: Steam AE 1.6.1170.0, EV-0109; no complete profile order.
- Native analysis identity: GOG AE 1.6.1179.0, executable SHA-256 preserved in EV-0289 metadata; never transfer RVAs to Steam.
- Lane: offline mechanism inference. No game launch, save edit, console command, plugin change, or live Observer.
- Record route: strict-dispatcher `tools/xedit_bridge.py file-records`, which parses plugin files and does not run xEdit or resolve overrides.
- Native route: strict-dispatcher `tools/ghidra_probe.py` against the existing project with analysis disabled and read-only mode.

## Procedure

1. Read EV-0272/M-0026 and EV-0288/EXP-0036 before proposing the API and direct-reference models.
2. Inspect the raw QUST `0202C49E` ENAM/DNAM and the CLOC SMQN path.
3. Query the GOG `BeginStartUpQuest` and `EnsureQuestStarted` targets and inspect observed direct callers, focusing on the inferred `Quest.Start` and `Quest.SetStage` wrappers.
4. Request `TESQuest::Start` through the matching GOG Address Library. Treat a missing relocation as a route limit, not evidence that the method is absent; do not guess an RVA.
5. Scan QUST, DIAL, and INFO records in the five official-master files for the target FormID bytes and preserve per-plugin output counts and hashes. Attribute only record classes actually scanned.
6. Preserve native GOG results separately from Steam plugin data; leave aliases, profile overrides, and game state unobserved.
7. Verify the private capture manifest and register the bounded result with explicit remaining coverage.

## Limits

The direct parser does not resolve overrides or inspect signatures outside QUST/DIAL/INFO for this transaction. A raw FormID reference scan does not find dynamically built form lookups. The Papyrus wrapper names are inferred rather than symbolically registered. No alias-fill behavior or Steam runtime equivalence is established.
