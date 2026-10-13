# North Star: Vanilla Level-One Capability Expansion

The project's primary reward is obtaining capabilities in an unmodified Skyrim playthrough that appear inaccessible to a level-one character, without raising the player beyond level 1. The larger scientific objective is an explanatory map of Skyrim's engine mechanisms that predicts *new* interactions, not merely a catalog of tricks.

## Ordered objectives

| ID | Priority | Outcome | Acceptance test |
|---|---|---|---|
| OBJ-1 | P0 / highest reward | Trigger any normally level-locked quest, encounter, or event | Record a specific vanilla lock, its ordinary prerequisite, and a level-1 in-game sequence that causes the real event/quest initiation; distinguish `setstage`, script injection, record patching and diagnostic interventions from vanilla-valid solutions. Repeat from clean save. |
| OBJ-2 | P0 | Equip any armor without accumulating armor XP from incoming hits | Character wears representative Light and Heavy Armor, receives verified physical hit(s), and measured armor skill XP is unchanged while the armor functions. Test coverage of arbitrary armor type and equip conditions separately. |
| OBJ-3 | P1 | Craft enchantments without leveling thresholds | Demonstrate successful useful enchantments while cumulatively staying below skill XP to go 15→16 or 20→21 (version-specific), with explicit starting XP and control. |
| OBJ-4 | P1 | Permanently maintain potion or poison effects | Demonstrate indefinite effect persistence, compare across waiting/travel/save-load/re-equip, and distinguish replacement by permanent magic effects from persistence of an alchemical ActiveEffect. |

## Core research themes

- Native quests and leveled encounters: gate predicates, story manager, quest starts, changeforms, Papyrus, aliases, level checks, timing, serialization, delayed tasks.
- Armor XP: hit events, armor skill experience calculation, use-skill routing, protection computation, perks, flags, actors, spell effects, event short-circuiting.
- Enchanting: crafting XP computation, perk trees, magnitude/chance, dynamic scaling, XP credit boundary and clamp order.
- Alchemical effect duration: active-effect instances, poison scaling, duration updates, unequip/re-equip, ref identity, save serialization, floating point.
- Generalizable primitives: event dispatch, entry points, conditions, numeric conversions, ActorValues, ActiveEffects, inventory stacks, animation/combat flags, save/load transitions.

## What success is NOT

- Character power produced by console commands alone.
- A new mod that disables the level gate or XP award; useful diagnostically, not a vanilla exploit.
- A claim supported only by one wiki/editor or an unreplicated report.
- An intervention that inadvertently removes the underlying event, the hit, or the alchemical effect rather than bypassing the gate.

## Research quality metrics

Evidence-backed coverage; causal depth to native code; number of cross-domain links; predictive tests; reproducible positive and negative results; progress towards OBJ-1/2; quality of instrumentation; no loss of provenance.
