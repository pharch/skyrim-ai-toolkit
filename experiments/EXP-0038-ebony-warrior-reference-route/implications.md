# EXP-0038 implications

The full official-master record scan narrows the question of an independently placed Ebony Warrior: Dragonborn.esm has one placed ACHR for the unique NPC base, marked Initially Disabled, and the CLOC quest alias is filled from that same base. Stage 10 is the serialized enable/move transition. The extra FormID hits belong to the quest's own dialogue, packages, perk, location, and story-node records; they do not establish an alternate pre-gate route ([EV-0290]).

This adds no causal edge to armor rating, AV39 mitigation, HitData, or AV11/AV12 armor-skill XP. The remaining OBJ-1 uncertainty is dynamic script/native dispatch, external/profile overrides, and live Story Manager/alias state. The Papyrus archive lane is narrower than this record scan: the tested extractor handles the classic PEX stream in `Skyrim - Misc.bsa`, not a general Dragonborn BSA. Continue with an available static OBJ-2 discriminator while preserving those exact runtime and archive limits.
