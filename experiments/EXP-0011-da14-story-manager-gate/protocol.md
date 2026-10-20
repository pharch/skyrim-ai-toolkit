# EXP-0011 protocol

## Competing models and predictions

- **H1 — one explicit start gate:** the player-level predicate is evaluated on a single start transition. The node should contain the predicate; the child quest, downstream quest conditions and linked dialogue should not repeat `GetLevel`.
- **H2 — repeated or alternate gate:** a later quest/dialogue/alias transition repeats the predicate, or an ordinary player-accessible start route reaches another transition. The scan should find a later level condition or a distinct start writer that bypasses the Story Manager node.

The record screen discriminates repeated record predicates in its stated scope. It cannot by itself rule out another route or dynamic native behavior; that requires an exhaustive start-writer review and ultimately a clean level-one gameplay observation.

## Source and identity

Target identity is Steam `SkyrimSE.exe` ProductVersion 1.6.1170.0, recorded in EV-0109. Read the installed Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm and Dragonborn.esm only. Their hashes and scan scope are in EV-0213. Do not infer a user-profile winner: its complete order is not configured (EV-0110).

## Read-only steps

1. Retrieve Skyrim.esm SMQN `DA14QuestStartNode` (form `0003FA1A`), QUST `DA14Start` (`0003FA17`), QUST `DA14` (`0001BB9B`), their CTDA bytes, child links, aliases and stage counts.
2. Screen the five official masters for those QUST/SMQN forms, 61 DA14 DIAL topics and linked INFO records. Count condition function index 80 without changing a plugin.
3. Map condition index 80 and PlayerRef form `00000014` with the xEdit schema source, not by assumption. Use the corrected historical CTDA decoder EV-0108 for the raw comparison operator; keep raw bytes in the capture.
4. Extract and inspect the `QF_DA14Start` and `QF_DA14` PEX files. Record calls in the disassembly while preserving the limits of the narrow PEX reader. The initial fragment-stage mapping gap was resolved for the DA14Start scenes and stage-70 handoff in the follow-up screen EV-0264.
5. If a static xEdit native export cannot launch, record the exact failure, use the documented read-only raw-file parser for a bounded screen, and label the route correctly. Do not retry an unchanged WSL interop path without a new discriminant.

## Controls and exclusions

No game was launched, no save/plugin/game file was modified, and no console, Papyrus injection or forced stage was used. The direct parser does not resolve winning records and the five-master scan does not represent an optional Creation Club or user mod order. Neither a journal entry nor a script call is treated as proof that the quest started in gameplay.
