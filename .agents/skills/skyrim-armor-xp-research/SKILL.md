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

## Tool route and evidence

- Use `python3 scripts/python_env.py run
  tools/ghidra_probe.py --analyze --analysis-timeout 7200` for a verified
  current-binary analysis, then query a completed ignored project read-only.
  Use `tools/plugin_reader.py record` for exact plugin fields only after the
  complete AE order is verified.
- A live XP/protection comparison requires a user-approved instrumented or
  player protocol. Store raw before/after values, controls, runtime/profile,
  and hashes under ignored `.local/`; classify diagnostic interventions
  separately from vanilla reproduction.
- Missing profile, incomplete analysis, failed xref, absent live process, and
  incomplete telemetry are explicit blockers. Never translate them into
  “zero XP” or an exploit result.
