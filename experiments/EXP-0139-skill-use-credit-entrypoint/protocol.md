# EXP-0139 protocol

## Competing models and source route

1. Query the existing GOG AE 1.6.1179.0 Ghidra project read-only for `FUN_14077d090`, its exact caller(s), and direct callees. Validate the executable hash and save metadata/stdout/disassembly/decompilation hashes under ignored `.local/ghidra/`.
2. Use the pinned CommonLib `ActorValueInfo::Skill` and `BGSEntryPoint::ENTRY_POINT` declarations to map the AVIF fields and selector; do not assign gameplay meaning from function names alone.
3. Capture all official AVIF records with their `AVSK` raw values, source plugin hashes, and CommonLib field mapping. Native-query exact AVHeavyArmor and AVLightArmor AVIF records through the tested five-master xEdit route.
4. Reuse the full official five-master EntryPoint 22 screen [EV-0262] and review each targeted amount/condition. It is not a profile-winner result and does not cover optional Creations.

## Decision rules

- Support an award-side control point only if code order shows the modified points float precedes the per-skill progress accumulation.
- Support a zero-capable record source only if its exact AVIF coefficient or schema-decoded PERK row for AV11/12 is non-positive and its owner/conditions are not mistaken for source-level presence.
- Keep the award path distinct from HitData mitigation. A downstream skill-credit modifier is not evidence that armor still protects.
- Do not transfer GOG RVAs to installed Steam 1.6.1170.0. No active profile winner or live result follows from the five official masters.

## Runtime test (not run)

EV-0260 remains the required matched-hit protocol: verified Steam target and full order, clean disposable level-one save, read-only observer, no-armor/equipped controls, positive landed hits, positive protection, raw Heavy/Light AVSK and Block deltas, repeated trials, and character-level preservation. No console/forced state is vanilla validation.
