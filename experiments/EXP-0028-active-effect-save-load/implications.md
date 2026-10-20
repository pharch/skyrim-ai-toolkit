# Implications — EXP-0028

- Use source/base-effect/target, usUniqueID, timer fields, active-list membership, and apply/remove events together to distinguish restoration from replacement. usUniqueID alone is not a universal identity guarantee.
- The GOG base serializer establishes which fields are persisted by these routines, not that a particular potion/poison effect remains functionally active after load.
- The timer writer/update loop, higher-level finish/Recover dispatcher, wait/travel behavior, derived effect overrides, and exact Steam implementation remain open.
- This ActiveEffect path has no evidenced shared native function, ActorValue, HitData field, or serialization routine with OBJ-2 armor/Block skill XP; no causal edge is added. Return to the P0 quest-access and armor-XP investigations after this static line.
