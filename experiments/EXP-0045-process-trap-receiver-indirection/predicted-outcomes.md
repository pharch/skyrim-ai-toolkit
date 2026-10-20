# Predicted outcomes and discriminants

| Question | H1: hidden armor award | H2: no award in mapped scope | Required distinction |
|---|---|---|---|
| What does a receiver indirect call target? | A candidate dispatch reaches an award or shared skill-progress routine | The selected target handles state, effects, or damage without armor skill credit | Preserve callsite, receiver type, initialized table/store, target function, and call depth |
| What skill is credited? | AV11 Heavy Armor or AV12 Light Armor is passed through `UseSkill` or equivalent | Visible `UseSkill` use is AV15 Sneak, another skill, or no credit | Trace concrete skill ID and points argument to PlayerCharacter progress sink |
| Does dispatch return to the known resolver? | A target returns to `FUN_1406bcaa0` or reproduces its award branch | No enumerated target returns to that resolver | Distinguish direct xrefs from vtable, callback, and data-driven dispatch |
| Is the negative complete? | One mapped target falsifies no-award for that route | All enumerated relevant targets are resolved with no AV11/12 path | Report all residual unresolved sites; never generalize past them |

AV15 Sneak and AV9 Block are not armor awards. A call to generic `Actor::UseSkill` counts only when its concrete AV and PlayerCharacter route are established. A static GOG result does not predict the installed Steam runtime without an independent mapping or live result.
