# BOUNTY-0001 — Level-1 Access and Armor-XP Independence

**State:** Ready for researcher review; not yet launched  
**Class:** Open-ended exploit discovery, vanilla Skyrim Anniversary Edition  
**Priority:** P0; two independent highest-reward objectives  
**Research harness:** Use the repository's existing `AGENTS.md`, skills, protocols, tool routing, evidence/transaction model, and frontier. **This bounty defines the target and evidence needed, not a second research methodology.**

## Mission

Discover **player-reproducible vanilla-compatible engine exploits** enabling the following outcomes without raising the character above level 1. Investigate both in parallel, selecting whichever line can make meaningful progress; a local dead end on either bounty is not completion of the research program.

### P0-A — Trigger level-gated content at level 1

**Prize condition:** A genuinely level-gated vanilla quest, encounter, or event whose normal eligibility requires a player level above 1 can be **initiated by a level-1 player** using a reproducible player-accessible sequence, without directly editing game state via console, scripts, plugins, external tools, or a modified save.

**Scope includes:** quest startup, story-manager dispatch, dialogue/alias pathways, leveled encounter selection, scene/event scheduling, script-driven start conditions, persistent trigger state, and legitimate interactions that bypass or alter the gating path.

**Distinguish carefully:**
- Quest *appearing in the journal* vs actual quest `Start()` success and event-specific start/selection conditions.
- An actor or location existing vs the gated encounter actually starting.
- Content already accessible through a documented alternate vanilla route vs a newly discovered bypass.
- Console `setstage`/`startquest`, SKSE, Papyrus diagnostic forcing, custom ESPs, or level changes as **diagnostic only**.
- Anniversary Edition content and optional Creations require explicit installed-content assumptions; do not generalize availability from a single profile.

**High-value initial case studies** (starting hypotheses, not mandatory limits): `DA07`, `DA14`, Haknir's quest/encounter, and Dawnguard gated entry paths from the existing frontier. Derive exact actual gate conditions before assuming these cases are level-gated in the tested build.

**Minimum proof for a candidate:**
1. A direct source or controlled observation establishes the level condition and expected ordinary behavior.
2. A proposed player-accessible trigger path and exact sequence are documented, including character level, prerequisites, location/timing, equipment/effects and game build/content profile.
3. Negative control: comparable level-1 setup without the proposed trigger does not satisfy the target condition.
4. Positive result: captured game evidence proves the targeted gated transition occurred (not merely forced stage flags or superficial UI state).
5. Replication: a fresh/disposable save or independently replayed sequence, with an explanation of variability and limits.
6. Mechanistic account or explicit remaining uncertainty, linked to records, scripts/native functions and evidence IDs. If only static evidence is available, classify **candidate**, not exploit confirmed.

### P0-B — Functional armor with zero hit-earned Heavy/Light Armor XP

**Prize condition:** A level-1 player equips armor that **functions protectively against incoming attacks** yet earns **zero Heavy Armor and zero Light Armor skill XP from the relevant hits**, reproducibly, without requiring total avoidance of qualifying hits.

**Scope includes:** the hit event / skill-use pathway, equipment classification, slot and stack state, armor rating, damage calculation, ActiveEffects/perks, attack types, Block substitution, and timing of XP attribution.

**Distinguish carefully:**
- No XP because no qualifying hit occurred vs a hit occurred but awarded no armor XP.
- Armor with a visual model only vs armor with an effective defensive effect (prove against controlled baseline).
- Zero XP vs very small/delayed/batched XP below UI visibility.
- Heavy/Light armor XP vs Block XP or experience redirected elsewhere. Any transferred XP must be recorded, since staying level 1 is the broader objective.
- Armor type and enchantment effects vs claimed generalization to **any** armor. One working item is a *partial* outcome, not proof of universal applicability.
- Native diagnostic force, custom plugins, or debug commands vs vanilla player-accessible setup.

**Minimum proof for a candidate:**
1. Identify exact skill-use functions/conditions or instrumented equivalent for the verified game/runtime build; do not blindly transfer GOG native RVAs to Steam.
2. Capture a pre/post **numeric** XP or skill-use measure from an appropriately instrumented *diagnostic* trial, with tool identity and raw artifact. Compare with a vanilla reproduction path if found.
3. Establish that a qualifying attack landed and that the equipped armor measurably protected the actor, using controlled naked/unarmored or equivalent baselines.
4. Cover multiple hits and enough repetitions to exclude delayed or rounded-away increments.
5. Check both Heavy and Light XP, plus Block/other skill XP, with explicit level-1 preservation criterion.
6. Document armor slot/type/strength limitations and evidence supporting (or refuting) generality across armor classes.
7. Reproduce under a player-accessible vanilla setup before claiming bounty completion.

## Boundary conditions common to both bounties

- Target gameplay is **Skyrim AE**. Use the existing **GOG AE** Ghidra project for static research and the separately verified actual AE runtime for in-game observations. Never assume byte-identical native addresses or call paths across builds.
- Research tooling can inspect, instrument and force state to test hypotheses, but forced states are **not prize-winning exploits**.
- No game modification or save corruption; user-controlled disposable profile/save and permission for diagnostic live actions.
- Wikitext/UESP/Apocrypha are grounding and leads, not strong engine-mechanism proof by themselves.
- Continue useful offline research when a real user test, MO2 profile, or live handshake is unavailable; queue an exact reproducible test rather than waiting indefinitely.
- Do not spend the bounty's investigation budget rebuilding already validated harness infrastructure. If a capability genuinely fails, record a precise tool blocker and switch to an independent research line; only make a narrow tool repair when necessary for the current investigation.

## Research direction and test drive

The first session should start by reading the existing frontier and already-imported observations; **do not reset it**. Investigate one high-information-gain P0-A gate and one P0-B armor skill-use path early enough to test cross-domain continuity, while keeping one independent breadth branch available. Prioritize discrimination among rival mechanisms over collecting similar supporting anecdotes.

**Suggested first research episode (not a fixed checklist):** trace the level-gate implementation of one source-confirmed target using complete available records/Papyrus and static GOG native paths; in parallel trace a verifiable armor XP dispatch path and the point where hit damage, defensive armor effects, and skill-use awards diverge. Write falsifiable predicted outcomes and highest-value next probes. A blocked record or runtime interface should trigger another tractable branch.

## Completion / research quality checklist

A bounty remains **OPEN** until the user accepts proof or explicitly closes it. A thorough investigation can produce excellent results without solving the exploit.

### Required for every substantial research episode
- [ ] Competing explanations stated and linked to preexisting claims/frontier rather than repeated as new facts.
- [ ] Important basic gameplay assumptions grounded in actual AE records or appropriately attributed community/wiki sources.
- [ ] Raw outputs and source identities/hashes retained; notes cite stable source and evidence IDs.
- [ ] At least one discriminating test or static investigation materially advances, rejects, or constrains a hypothesis.
- [ ] Negative findings and scope limits recorded (build, profile, tools, state and experimental sensitivity).
- [ ] Cross-domain implications checked; generated successor hypotheses are specific and falsifiable.
- [ ] `FRONTIER`, evidence/claims ledger, graph, `STATE.md` and recovery pointers updated as required by the harness.
- [ ] Next tractable investigation is unambiguous without needing conversational memory.

### To claim P0-A achieved
- [ ] Exact target, genuine required level and baseline lock are proven.
- [ ] Player-accessible sequence documented step by step.
- [ ] Level 1 preserved throughout.
- [ ] Gate transition observed and distinguished from cosmetic/journal-only state.
- [ ] Negative control and at least one reproduction completed; diagnostic forcing excluded.
- [ ] Claim limited to confirmed versions/content/prerequisites.

### To claim P0-B achieved
- [ ] Equipped armor shown to provide real defense during qualifying incoming hits.
- [ ] Heavy and Light Armor XP increments both zero by sufficiently sensitive measurement.
- [ ] Other skill XP (especially Block) tracked and level-1 status preserved.
- [ ] Multiple hits, appropriate controls and replication completed.
- [ ] No developer-forced state is part of the vanilla reproduction.
- [ ] Claims of "any armor" supported by tests across relevant armor variants, or narrowed to verified subset.

## User-facing outcome report

When asked for a status update, report:

- **State:** `CONFIRMED_EXPLOIT` / `STRONG_CANDIDATE` / `MECHANISM_ONLY` / `NEGATIVE_RESULT` / `OPEN` / `BLOCKED_EXTERNAL` per objective.
- **What changed:** up to five most important supported findings and relevant claim/evidence IDs.
- **What is not established:** strongest alternative mechanisms, limitations and uncertainties.
- **Next experiments:** the two or three highest-information discriminating tests and whether they need user action.
- **Research continuity:** last completed transaction, exact active frontier item and next action.

Do not return a conclusive "no exploit exists" merely because the investigated branches were exhausted. Do not close the research program with a locally satisfactory report. Under the operating harness, continue into the next valuable frontier item until user intervention or an actual external execution limit.

## Later bounties (not part of this first test-drive acceptance)

- **P1-C:** craft useful enchantments while remaining under the relevant skill/character-level advancement threshold (including the 15→16 and 20→21 cases), distinguishing total XP earned from observed skill display.
- **P1-D:** retain normally temporary potion/poison effects indefinitely, distinguishing genuinely permanent engine state from repeated reapplication, UI persistence, and transient serialization artifacts.

They remain eligible as cross-system hypotheses, but this first bounty's claimed successes are **P0-A** and **P0-B**.
