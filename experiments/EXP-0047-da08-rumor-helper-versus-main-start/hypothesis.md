# Competing models

## H1 — level-20 node gates only the rumor helper

`DA08KickerNode` selects `DA08RumorPointer` to provide a rumor or courier handoff, while main quest DA08 has at least one ordinary serialized start path that does not require that helper.

**Prediction:** The main QUST is independently startable by its flags, a dialogue/script caller, an alias or stage event; the level-20 helper's records do not own every route into DA08.

## H2 — all ordinary starts depend on a level gate

Every ordinary route into main DA08 depends on `DA08RumorPointer` or an equivalent level predicate; the node is effectively a gate on quest startup rather than just a helper selection.

**Prediction:** Main DA08 has no independent startup flag or serialized caller, and all relevant dialogue, alias, script, and stage paths are helper-dependent or separately conditioned on the player's level.

## Starting evidence

EV-0300 maps Skyrim.esm SMQN `000DC9E1` (`DA08KickerNode`) to QUST `000DC9E0` (`DA08RumorPointer`) under `GetLevel >= DA08MinLevel`; GLOB `000DC9E2` stores 20.0. The same census identifies this QUST as a child helper. Local UESP revision 3578672 lists level 20 and Dragon Rising context for *The Whispering Door*, but does not establish how the engine starts either quest.
