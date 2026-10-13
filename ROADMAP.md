# Rolling Research Roadmap

This is a *map of Skyrim AE research programs*, not a fixed completion
checklist. Rebuild it after major discoveries and at regular synthesis
checkpoints. Do not reuse non-AE evidence without an AE-specific verification.

## A. Objective 1 — Level-gated world / quest triggers (P0, main focus)

1. Compile a version- and DLC-aware inventory of level-gated quests and encounters using records + UESP + legacy logs.
2. Classify gates: dialogue condition, story-manager event condition, native/event callback, leveled spawn list, alias fill, trigger box, Papyrus check, delayed timer, encounter-zone state, save-state cache.
3. Find the authoritative enforcement path per representative gate. Identify whether there is a player-level read, an intermediate snapshot, or an alternate entry point.
4. Derive a *vanilla-accessible* manipulation/ordering/composition that bypasses a gate without `setstage`/mod edits as final solution.
5. Test against uninstrumented clean saves; generalize across multiple gates only after evidence.

## B. Objective 2 — Wear any armor with zero XP from hits (P0)

1. Establish a controlled repeatable attack protocol and measure armor skill XP directly before/after.
2. Separate damage reduction, contact registration, armor classification, and skill-use routing.
3. Trace event and native XP grant path in Ghidra / SKSE / game records as supported by available binaries.
4. Seek independent switch, state, temporary effect, actor flag, race/perk mechanism, or timing trick that blocks XP without disabling armor protection.
5. Validate both armor types and distinct hit sources.

## C. Enchanting with tiny XP budget (P1)

Trace native crafting XP computation; measure discontinuities and edge cases; integrate known numeric/ULP research; verify cumulative thresholds across 15→16 and 20→21.

## D. Permanent alchemy (P1)

Trace duration, ActiveEffect lifetime and serialization; compare poison vs potion application and numeric shifting; differentiate true indefinite instance from sustained/reapplied effects.

## Shared workstreams

- Source verification (UESP and Discord, explicit attribution and conflicting observations).
- Record-layer truth (xEdit, full active load order, binary data).
- Native code pathways (Ghidra offsets/version provenance).
- Runtime instrumentation (DevBench, SKSE probes, possible SkyLink MCP bridge).
- Session durability, causal graph, hypotheses, experiment lifecycle, and synthesis.
