---
name: skyrim-armor-xp-research
description: Analyze and test ways to wear light or heavy armor while incoming verified hits produce zero armor skill XP without losing effective protection.
---

# Skyrim AE armor XP investigation

> Cold-start gate: read [the local runtime contract](../../../docs/LOCAL_RUNTIME_CONTRACT.md) and [current readiness](../../../docs/HARNESS_READINESS.md) before invoking tools. Use the repository Python 3.12 .venv dispatcher only; there is no system-Python or Conda fallback. A blocked capability cannot support a negative finding.

1. Establish a verified baseline: equipped type/slot, source hit, actual
   hit/damage event, protection/armor rating, raw skill XP before/after,
   character level, and active effects.
2. Identify the award path from hit detection through armor skill/use
   calculation, including branching and clamping behavior.
3. Separate no XP caused by a miss, block, zero-damage event, or unequipped
   armor from the target mechanism.
4. Compare competing branches with before/after snapshots and an independent
   event trace. Check for missing or dropped samples.
5. Search vanilla-reachable state, timing, ActorValue, perk, and effect changes
   that suppress the award separately from armor protection.
6. Check light and heavy armor and representative pieces; verify sustained
   behavior and restoration of normal XP.
7. Record positive and negative cases, exact instrumentation, build
   dependence, causal-model changes, and the next frontier decision.

## Tool route and evidence

- For named native symbols, resolve the CommonLib AE ID against the matching
  GOG Address Library with
  `python3 scripts/python_env.py run tools/address_library_probe.py --symbol
  Namespace::Name`; query its returned RVA with
  `python3 scripts/python_env.py run tools/ghidra_probe.py --rva <RVA>`.
  Ghidra uses the existing GOG project with analysis disabled and read-only
  mode. Never transfer a GOG RVA to another runtime without an independent
  mapping. EV-0167 verifies the route, not an armor mechanic.
- Use `tools/plugin_reader.py record` for explicit plugin evidence only after
  the complete selected AE order is verified. File-level records do not
  establish winning overrides or native award logic.
- Live hit/XP/protection comparisons require a verified runtime/profile and a
  designated disposable baseline or an explicit user-player protocol. Store
  raw measurements under ignored `.local/` and classify diagnostic
  interventions separately from vanilla reproductions.
- Missing profiles, incomplete analysis, failed xrefs, absent live process,
  or incomplete telemetry are blockers. They do not establish zero XP or an
  exploit result; continue with independent offline analysis.
