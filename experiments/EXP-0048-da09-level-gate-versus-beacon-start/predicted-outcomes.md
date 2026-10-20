# Predicted outcomes and discriminants

| Observation | H1: independent Beacon/statue route | H2: all ordinary starts gated | Distinction needed |
|---|---|---|---|
| Main DA09 Start Game Enabled flag or fixed alias/script starts it independently | Supports H1 for that serialized route | Falsifies H2 for that route | Separate configured startup from observed live state and later stage gates |
| Beacon pickup/activation or statue callback calls `Start`/`SetStage` without a level condition | Supports H1 for that callback | Falsifies H2 for that route | Trace exact record/script, target quest, and conditions |
| Beacon is in a leveled list or boss chest but no start caller is linked | Establishes possible item placement only | Does not establish H2 | Distinguish loot availability from quest startup |
| Every inspected startup callback is gated by level 12 or depends on the Story Manager child | Weakens H1 within the inspected routes | Supports H2 only within that scope | Preserve incomplete dynamic, archive, profile, and physical-route coverage |
| UESP says Beacon acquisition triggers dialogue but also says level 12 is required | Competing gameplay leads | Competing gameplay leads | Resolve against source callbacks and, if possible, a clean live control |

No static source outcome proves physical access to a boss chest, a statue interaction, the active-profile winner, a live below-level-12 transition, or vanilla reproduction.
