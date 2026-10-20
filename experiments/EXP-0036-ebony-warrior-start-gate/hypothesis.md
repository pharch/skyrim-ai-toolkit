# EXP-0036 hypotheses

## H1 — Story Manager selection gates the initial encounter

The level-80 predicate is attached to the Ebony Warrior's initial CLOC Story Manager child-selection node. The selected child is the Ebony Warrior quest; its later stage fragments and aliases place the NPC in a city and then move him to Last Vigil.

**Prediction:** the SMQN node contains a PlayerRef `GetLevel >= 80` condition and points to the Ebony Warrior QUST; dialogue and downstream scripts use quest-stage/location state rather than adding a separate level predicate.

## H2 — The threshold is downstream, or a separate early route exists

The level-80 requirement is only a prompt/approach/dialogue check, or another quest, alias, script, API caller, or placed actor can start the encounter before the level-gated node.

**Prediction:** no level check appears on the initial selection path, or an independently configured pre-gate quest/actor/script path is found.

## Assessment

H1 is supported for the inspected official-file path. The downstream-dialogue-only portion of H2 is contradicted by the SMQN predicate and the full Dragonborn INFO screen. The broad separate-start-route portion is not falsified: no full cross-plugin caller inventory or runtime transition was completed. It continues as Q-0029 ([EV-0288]).
