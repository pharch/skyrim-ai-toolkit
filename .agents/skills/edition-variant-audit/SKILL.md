---
name: edition-variant-audit
description: Separate Skyrim SE, AE, VR, and LE evidence before reusing a quest, combat, save, or native-code claim across editions.
---

# Edition and build audit

1. Record the target edition, exact executable version, SKSE build, relevant
   address-library/runtime version, load order, and whether the tested state is
   modified. If any field is unknown, keep the claim edition-unverified.
2. Tag every source observation with the edition it actually describes. Do not
   transfer VR collision, physics, input, camera, UI, SKSE address, or save
   behavior to SE/AE without a discriminating check.
3. For native analysis, capture the executable hash and version, Ghidra project or
   database identity, module/address space, and offsets. An offset from another
   runtime is not corroboration.
4. For a candidate shared mechanic, formulate one prediction that differs between
   editions, then choose the cheapest source that can test it: record comparison,
   decompiled script, native path, or controlled runtime observation.
5. Compare winning records and masters across the edition-specific load order.
   Separate an edition difference from a mod override or stale profile.
6. Keep diagnostic interventions, instrumented observations, and
   vanilla-compatible reproductions in separate result categories.
7. Update `research/CONTRADICTIONS.md` when apparently conflicting sources actually
   describe different editions, builds, or instrumentation.
