---
name: skyrim-armor-xp-research
description: Analyze and test ways to wear light or heavy armor while incoming verified hits produce zero armor skill XP, without losing effective armor protection.
---

# Skyrim AE armor XP investigation

1. Establish valid baseline: equipped type/slot, source hit, actual hit/damage event, protection/armor rating, raw skill XP before/after, character level and active effects.
2. Identify the award path from hit detection through armor skill/use calculation and all branching or clamping behavior.
3. Do not confuse no XP from an attack that missed, a blocked/no-damage event, or unequipped armor with the target.
4. Test competing branches with before/after snapshots and independent event trace; diagnose any silent sample drops.
5. Search for vanilla-reachable state/timing/AV/perk changes that suppress the award *separately* from armor function.
6. Check light/heavy and representative different pieces. Confirm sustained behavior and restoring normal XP afterward.
7. Record positive/negative test cases, exact instrumentation and possible version dependence.
