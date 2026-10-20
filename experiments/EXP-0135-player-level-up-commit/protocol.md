# Protocol

## Scope and approved actions

- Objective: determine which state transition changes the Player Level consumed by GetLevel.
- Target: Steam AE 1.6.1170.0 identity [EV-0109]. GOG AE 1.6.1179.0 may be queried statically after fresh ProductVersion/hash verification; never transfer an RVA to Steam.
- Current limitation: no selected active profile/full order, designated disposable test save, deployed/loaded Observer, or live binding is configured [EV-0260]. Do not launch Skyrim or schedule an in-game action.
- Approved now: revision-pinned local UESP grounding, existing-project GOG read-only code queries, and read-only inspection of a specifically designated disposable save if one becomes available.
- Save baseline/rollback: no test save is presently bound. If the exact Steam trace becomes available, use a duplicate disposable baseline, retain an untouched baseline hash, and create separate copies for threshold-pending and accepted states. Never edit, overwrite, or clean the source save.

## Competing models and observables

H1 predicts that pending skill experience/level-up state is separate from the stored Player Level. H2 predicts that the gate-visible Player Level advances at threshold or notification.

Required observables are numeric Player Level/GetLevel, the relevant skill's level and progress, cumulative level-up experience or pending flag, player perk points, and save-state values before the threshold, after threshold while the level-up remains pending, and after acceptance. Record game time and whether a level-up menu was opened.

## Offline instrument route

1. Read existing EV-0109/EV-0260 and the current capability report. Verify the separate GOG executable identity and matching Address Library before any Ghidra query.
2. Search and retrieve revision-pinned local UESP leveling pages as secondary grounding; retain raw response, revision ID, URL, local corpus hash, and retrieved response hash.
3. Resolve any CommonLib candidate such as PlayerCharacter level/skill-advance functions with the matching Address Library, then query the existing GOG Ghidra project via the strict Python dispatcher using -process, -noanalysis, and -readOnly. Trace callers, fields, and the level writer rather than relying on names.
4. Check only configured disposable save paths. If none is designated, record the missing runtime artifact and continue static analysis.

## Exact Steam discriminator

When an approved exact-target test profile and disposable save exist, capture the same character at three states: before threshold; after crossing threshold with level-up pending but not accepted; immediately after accepting. Verify exact executable, complete active order, numeric level, and observer liveness before interpreting values. Use no console, forced skill levels, injected scripts, or altered plugins. Preserve all raw outputs privately under .local and retain controls for a character that has not crossed the threshold.

## Interpretation

H1 is supported only if both source flow and the natural Steam transition show the stored level remains unchanged until acceptance. H2 is supported only if the threshold/notification state advances the value that GetLevel reads before acceptance. If GOG and Steam differ, keep build-specific results separate. Neither result by itself proves a quest-start bypass or an armor-XP exploit.
