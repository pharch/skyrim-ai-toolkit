# Legacy mechanism ledger

Stable M IDs are retained from snapshot `LEGACY-20261014-A`. Entries below summarize source claims; they are not current-build confirmation. See `research/EVIDENCE.json` for per-file hashes and the external source-revision limit.

<a id="m-0001"></a>
## M-0001 — Cached dialogue result / late skill-use calculation

Legacy model: a success result may be selected while effective Speech is high, followed by a later non-positive skill-use amount. The family matrix adds an Intimidate-only quest-state suppression candidate; the claimed no-XP outcome is an unlogged historical observation ([EV-0068], [EV-0069]). Dialogue-family breadth remains open.

Legacy mechanism record: [M-0001](MECHANISMS.md#m-0001) (`EV-0004`). Related glitch record: `glitches/G-0001-speech-xp-exploit.md`.

<a id="m-0002"></a>
## M-0002 — Float32 ActorValue accumulation and cleanup

Legacy numeric model: independent temporary writers can round when aggregated and leave a cleanup delta; raw bits, source identity, operation order, and reachable writers are required. The root numeric examples are retained as unverified illustrations ([EV-0040]); the detailed source model is [EV-0005]. A later report corrects the cleanup operand: Recover subtracts the negated effective magnitude, while `+0x94` receives an observed modifier-slot delta afterward ([EV-0057]).

Legacy mechanism record: [M-0002](MECHANISMS.md#m-0002) (`EV-0005`). Related glitch record: `glitches/G-0003-shifting-float-residue.md`.

<a id="m-0003"></a>
## M-0003 — Alchemy classification, cost ordering, and Peak key

Legacy static model separates poison/potion classification, costliest effect, Peak comparison key, and resistance behavior. Ingredient order alone does not prove commit order. Follow-up reports add the 89.2167511 Conjuration-poison XP prediction, the null-key AV148 CC writer, and a scoped VMAD writer inventory ([EV-0059]–[EV-0061], [EV-0064], [EV-0082], [EV-0083], [EV-0093]–[EV-0095]); these are static findings with recipe, reachability, and plugin-scope limits. A separate report models item class from the first raw matched effect before scaling; the Jarrin edge case is only predicted under extreme scaling ([EV-0094]).

Legacy mechanism record: [M-0003](MECHANISMS.md#m-0003) (`EV-0006`). Related glitch record: `glitches/G-0002-mixed-poison-classification.md`.

<a id="m-0004"></a>
## M-0004 — Poison Resistance-sensitive effect scaling

Legacy reports tie scaling to item classification and effect data. One inventory reports 50 PoisonResist MGEFs, 319 reverse-reference rows, and 148 possible mixed-effect recipes; an older probe supports hostile-first classification only ([EV-0056]). No exact recipe, resistance amplification, delivery, or XP result is imported, and no general rule that every beneficial effect scales is imported.

Legacy mechanism record: [M-0004](MECHANISMS.md#m-0004) (`EV-0007`). Related glitch record: `glitches/G-0002-mixed-poison-classification.md`.

<a id="m-0005"></a>
## M-0005 — Deadload queue/load boundary

Legacy static model: the load worker can revert VM state and drain queued callbacks. A historical user report says game time freezes during deadload, which weakens expiry-inside-deadload models but is not executable-verified ([EV-0078]). Direct spell membership, favorites hand-slot assignment, and MGR21 perk cleanup are distinct paths ([EV-0075]–[EV-0077]); a retained icon or membership is insufficient functional evidence.

Legacy mechanism record: [M-0005](MECHANISMS.md#m-0005) (`EV-0008`). Related glitch record: `glitches/G-0004-deadload-cleanup-retention.md`.

<a id="m-0006"></a>
## M-0006 — Positive skill-use amount guard

Legacy native analysis reports a shared non-positive amount guard. Caller-specific formulas and effective outcome remain separate questions ([EV-0009], [EV-0038]). Historical skill-use scans also distinguish scroll from ordinary spell paths and report no valid-skill exact-zero MGEF in the scanned corpus ([EV-0072], [EV-0073], [EV-0086]); these do not establish a current-order XP suppressor.

Legacy mechanism record: [M-0006](MECHANISMS.md#m-0006) (`EV-0009`). Related glitch record: `glitches/G-0001-speech-xp-exploit.md`.

<a id="m-0007"></a>
## M-0007 — Synchronous craft transaction boundary

Legacy static analysis reports synchronous alchemy/enchanting calls and no known player-controlled interposition. The ordinary enchanting callback produces output before a fixed skill-use call; condition functions inspect/register data without creating an inventory transaction ([EV-0067], [EV-0084]). Signed `usesSkill` values outside 6–23 skip the skill call, but no accessible type-3 furniture was found; fixed COBJ outputs and the Staff Enchanter furniture lead do not establish an XP bypass ([EV-0065], [EV-0066], [EV-0085]). A transaction boundary is not itself a bypass.

Legacy mechanism record: [M-0007](MECHANISMS.md#m-0007) (`EV-0010`). Related glitch record: `glitches/G-0006-enchanting-preview-mismatch.md`.

<a id="m-0008"></a>
## M-0008 — No-caster hazard path

Legacy native model reports a stack `NonActorMagicCaster` route. A later static audit reports player-created hazards receive the player `ActorCause` before ticking and finds no official cause-less writer in its scope; environmental non-actor hazards remain controls, not player routes ([EV-0031], [EV-0106]).

Legacy mechanism record: [M-0008](MECHANISMS.md#m-0008) (`EV-0011`). Related glitch record: `glitches/G-0005-blizzard-no-xp-candidate.md`.

## M-0009 — Incoming armor skill-use routing

Legacy static analysis reports that incoming player damage reaches Heavy/Light Armor `UseSkill` only after positive damage and a positive-DNAM worn-armor scan; a blocked hit takes the Block AV9 path instead. Projectile owner-death checks are on the outgoing branch, and pure spell projectiles avoid the physical sink by taking another damage path. Neither the blocked redirect nor alternate damage type proves a zero-XP physical hit with useful protection. Source/build identity and all runtime outcomes remain unverified ([EV-0036], [EV-0049], [EV-0050], related `EV-0020`, `EV-0023`).

## M-0010 — Invulnerability clears the armor eligibility field

Legacy static analysis reports that the invulnerability branch clears total hit damage before armor skill credit, while also removing the physical damage payload. The ordinary player writers identified in that report are protected transitions with paired cleanup; no persistent useful-hit route is established ([EV-0039]).

## M-0011 — No generic official EP22 XP-negation multiplier found

The legacy clean-master scan reports only positive `Mod Skill Use` perk multipliers, including one furniture-gated 0.05 staff-enchanter entry. This rules out that audited record family as an arbitrary skill-XP suppressor but does not rule out caller-side non-positive amounts or runtime state mismatches ([EV-0051], related `EV-0038`).

## M-0012 — Native finite-effect cleanup and timer lifecycle

Historical GOG static reports say finite potion effects finish through native `Finish`/Recover cleanup before Papyrus `OnEffectFinish`; race transformation does not clear arbitrary alchemy effects. No ordinary official writer for the cited non-finite timer or bypass state was found in the audited scope ([EV-0058], [EV-0079], [EV-0096]). Zero-duration Thistle still finishes at elapsed zero ([EV-0098]); the scanned ENIT bit did not bypass that path, and deferred Dispel retries ordinary finish instead of providing an identified alchemy caller ([EV-0097], [EV-0099]). This is not an all-load-order negative or a runtime permanence test.

## M-0013 — Self-poison inventory ownership and transfer boundary

Historical static reports place weapon poison in inventory-entry `ExtraPoison` data and show the incoming hit path does not rewrite its target. Transfer helpers may carry extra data, but do not prove stable stack identity or a deterministic NPC attack on the player ([EV-0062], [EV-0063], [EV-0101]). Fixed poison-gas and Poison Rune controls remain distinct from arbitrary crafted-poison delivery; the gas audit reports a fixed explosion payload that does not read weapon poison, and inspected shield reflection scripts cast fixed spells ([EV-0102], [EV-0103]).

## M-0014 — Base ActorValue skill cap

The historical Enchanting audit reports that the native cap checks base skill rather than the effective ActorValue, so temporary effective-skill shifts do not evade that check ([EV-0087]). This is a GOG static finding, not a tested XP-threshold bypass. A separate Shalidor scroll scan reports fixed perk grants rather than school PowerModifier writes, with an adjacent AV156 Magicka effect ([EV-0104]).

## M-0015 — Direct spell-list serialization and cleanup

A historical Karstaag audit reports that Power cast membership is native actor state, serialized in the save, and checked before another cast; losing a Papyrus removal callback can leave list membership or an icon without proving another usable cast ([EV-0088]). The separate player-spell inventory reports synchronous Apocrypha `SetPower` replacement, not a queued cleanup gap ([EV-0100]).
