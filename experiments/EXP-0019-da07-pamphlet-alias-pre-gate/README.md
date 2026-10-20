# EXP-0019 — DA07 pamphlet alias before the level-20 helper

**Status:** bounded official-five-master static path resolved; no runtime result.

**Question:** Q-0009 / OBJ-1. Can the pamphlet alias's `SetStage(5)` event start DA07intro before the level-20 Story Manager child fills the alias?

**Result:** The alias is a quest-created object on DA07intro, and stage 0 adds it to WICourier. The attached script sets stage 5 only after that alias reference is equipped by or transferred to the player. The base BOOK has no script; the two screened dialogue fragments only transfer a BOOK from player to speaker. The alias path therefore does not provide its own pre-start transition in the inspected five-master/PEX route. EV-0265 preserves scope and hashes.

**Follow-up:** A distinct `DA07IntroTrigger` in DawnstarExterior04 calls DA07intro stage 7 when Silus and Madena both enter it. That independent writer remains the Q-0019 candidate (EV-0266); do not treat it as proof that the pamphlet alias bypasses the helper.

See [protocol](protocol.md) and [results](results.md). This static result does not establish the active profile, alias fill in a live save, or a level-one quest transition.
