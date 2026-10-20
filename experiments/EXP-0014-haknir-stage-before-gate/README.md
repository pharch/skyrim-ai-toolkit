# EXP-0014 — Haknir quest and death-stage path before level 36

**Status:** official-master gate trace updated; no gameplay result.

**Objective:** OBJ-1 / Q-0010. Determine whether the level-one player can start the Haknir treasure quest or enable Haknir before the Story Manager level-36 gate.

**Current result:** the official-master record chain gates the child quest at `GetLevel >= 36`; the main QUST Haknir alias is marked Initially Disabled and resolves through the Gyldenhul Barrow location. A downstream world encounter requires main-quest stage 20. Eleven Deathbrand book references exist outside the Barrow, but the attached book PEX is unavailable in the configured data roots; its alternate-start behavior remains open. No pre-gate death event or vanilla bypass was observed.
