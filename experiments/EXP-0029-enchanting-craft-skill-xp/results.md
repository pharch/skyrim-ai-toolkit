# Results

## Static findings

- The GOG craft-confirm callback has one virtual `Actor::UseSkill` dispatch site. It reads the skill ID from the furniture `usesSkill` byte and passes a shared global float as the points value; the numeric value of that global was not resolved (EV-0280).
- The base official Skyrim.esm `CraftingEnchantingWorkbench` record `FURN:000BAD0D` stores `WBDT` bytes `03 17`; the hashed CommonLib layout identifies byte 1 as ActorValue `usesSkill`, and ActorValues.h identifies AV23 as Enchanting (EV-0281).
- The concrete GOG PlayerCharacter override rejects non-positive points. Positive points enter a helper that accepts skill IDs 6–23, adjusts a float amount, adds progress, and checks a threshold before increasing the base skill (EV-0280; the earlier bounded override result is EV-0221).
- The same `UseSkill` slot and progress sink are used by the incoming-hit armor/Block path (EV-0217–EV-0223). The craft callback and hit resolver supply different points and skill inputs.

## Assessment

The visible callback call site favors one station-selected award per craft confirmation over a credit formula directly parameterized by item value, soul size, or selected-effect count. The progress helper is consistent with accumulated sublevel progress. These are GOG static inferences; downstream modifiers and integer/float threshold math can still affect the result.

No raw Enchanting XP value, one-versus-two craft delta, value/soul-level comparison, useful-enchantment outcome, or 15→16 / 20→21 threshold test was captured. The Steam 1.6.1170.0 function path was not independently mapped. The live result remains blocked by EV-0260 and the lack of a verified raw AVSK observation route.
