# EXP-0052 results — DA02 level gate and ordinary entry paths

## Finding

Prepared official records put main DA02 behind `DA02IncreaseLevelNodeSHARES` with `GetLevel >= DA02MinLevel` (30); the QUST Start Game Enabled flag is clear. The event-driven WEDA02 helper is not an independent main-quest start in its serialized conditions: it requires DA02 running at a stage below 1. The four fixed book placements run an `OnCellLoad` level check and disable below 30.

The book path remains unresolved. `DA02BookScript.OnRead` requests DA02 stage 1 whenever its stage is below 1. No direct `Start()` appears in the captured branch, but static PEX cannot establish what `SetStage(1)` does when DA02 is stopped. The book is in generic leveled lists with minimum level 24, not a level-one source in those lists. `QABooksContainer` has a single source reference in `QASmoke`, not an ordinary-world placement.

The DIAL/INFO group join maps 73 DA02 topics to 95 INFO records and finds no function-80/GetLevel condition in those INFO children. This does not remove QUST, alias, event, scene, reference, plugin-override, or runtime gates.

## Hypothesis update

- **H1, narrowed:** supported for the inspected Story Manager and WEDA02 helper paths, and for fixed book-placement availability below level 30. It is not established as the only practical initiation route because the book stage callback's stopped-quest effect remains unknown.
- **H2, unresolved:** the main independent-start claim is not shown by WEDA02, but `DA02BookScript.OnRead` is an unresolved stage writer. The source list does not establish level-one acquisition or a successful start.

## Reproduction boundary

EV-0310 contains a clean level-one/no-trigger versus natural event and book-read control protocol. The staged Observer does not capture Story Manager state, and the selected full profile order is not configured. Native xEdit failed before enumeration. No console, script injection, altered plugin, or live-game test was used. No level-one progression or Sacellum access is established.

## Next useful research

Q-0050 continues OBJ-2 by locating writes to the PlayerCharacter cached armor-factor field at `this+0x274` in the existing GOG 1.6.1179.0 project. Rival source models are that clothing DNAM contributes to the mitigation factor or that the factor aggregation excludes clothing. Any result remains GOG-specific until independently checked on Steam.
