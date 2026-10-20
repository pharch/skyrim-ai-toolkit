# Competing models

## Q85-H1 — conditional Solstheim alternative

`DLC2WE09` evaluates a chance row, `MQ105 >= 160`, and `DLC2MQ06 < 550`, followed by `GetLevel >= 25 OR GetInCurrentLoc(DLC2SolstheimLocation)`. The Solstheim trigger/Story Manager path can submit the DLC2 event without an explicit player-level predicate in the bounded source chain.

**Prediction:** CTDA bytes and the identity-checked evaluator establish the OR group; official event selectors and the captured trigger script/property chain contain no additional explicit Player-level condition.

**Status:** supported as a conditional static model [EV-0657], [EV-0665]–[EV-0669], [EV-0686]. It does not establish precondition reachability or a level-one Steam start.

## Q85-H2 — upstream explicit level gate

A screened official trigger, Story Manager selector, or pre-start quest condition has a separate Player-level predicate that prevents the location branch from being used below level 25.

**Prediction:** the upstream event selector, trigger, or ferry topic contains a `GetLevel` predicate or equivalent explicit player-level read required before the location branch can be used.

**Status:** falsified only within the screened official parent/node/selector and trigger path, plus the source-order-derived initial ferry topic [EV-0389], [EV-0390], [EV-0661], [EV-0662], [EV-0664], [EV-0686]. Unexamined Steam callbacks, profile overrides, stage reachability, and runtime dialogue remain open.

## Q85-H3 — static route is possible, natural level-one start unresolved

The serialized route admits a Solstheim alternative, but stage reachability, chance state, event timing, aliases, or a Steam-specific callback may still prevent a natural level-one start.

**Prediction:** only the clean Steam observation can show the level, stages, chance value, submitted event keyword, `DLC2WE09` running state, and alias result at the transition.

**Status:** unresolved; EV-0260 is still required.
