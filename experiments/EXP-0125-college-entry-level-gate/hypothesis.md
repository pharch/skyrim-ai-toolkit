# Competing hypotheses

## Q76-H1 — an explicit level gate is present in the College records or room door

The First Lessons or Under Saarthal QUST, a linked DIAL/INFO entry, or the Arch-Mage quarters access record has a player-level condition that excludes level one.

**Predicted discriminant:** A schema-decoded `GetLevel` CTDA with a threshold above one appears on a relevant quest, dialogue or door record, or a source-defined entry/encounter gate requires a higher level.

## Q76-H2 — quest progression and ownership/lock state gate the fixed item, without a player-level predicate

The relevant source records gate the item through College quest progression and ownership/lock state, while the player-level census contains no `GetLevel` condition attached to the First Lessons or Under Saarthal quests.

**Predicted discriminant:** Exact QUST and linked DIAL/INFO FormIDs plus a complete five-master `GetLevel` census show no matching `GetLevel` rows; source door and quest-state records identify only stage, lock or ownership prerequisites.

## Q76-H3 — indirect quest-variable/script or live access conditions remain possible

The QUST records lack a direct `GetLevel` predicate, but quest-variable values, dialogue, aliases, room access, hazards, or runtime behavior can still prevent a level-one character from obtaining the boots.

**Predicted discriminant:** Exact QUST/DIAL/INFO records lack `GetLevel`, but quest-variable scripts, Story Manager, door, hazard or controlled level-one evidence reveals an indirect condition or remains unresolved.

## Source-screen outcome

The direct explicit-level model is falsified within the screened QUST, linked DIAL/INFO, Story Manager GetLevel node, quarters DOOR/REFR, and four attached PEX scope [EV-0300], [EV-0321], [EV-0407], [EV-0409], [EV-0410], [EV-0413]. The source route instead supports a stage/key mechanism: the Tolfdir post-forcegreet INFO requires MG02 stage 200 and its TIF adds the CollegeArchMageKey and Arch-Mage robe; the linked door endpoints name that key [EV-0410]–[EV-0413]. The `GetVMQuestVariable` operand, fragment-to-stage bindings, hazards, active profile and clean level-one entry remain unresolved, so H3 stays open and H2 is source-supported but not a level-one reproduction.

