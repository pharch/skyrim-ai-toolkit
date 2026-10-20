# Competing models

- **H1 — Clothing contributes:** the PlayerCharacter cache at `this+0x274` aggregates equipped item rating without excluding BOD2 Armor Type 2. Prediction: the visitor method reached by the cache writer adds positive-DNAM Clothing records.
- **H2 — Clothing is excluded:** the cache writer's inventory visitor rejects Armor Type 2 before rating accumulation. Prediction: an attested GOG parser maps BOD2 Armor Type to the runtime field read by the visitor, and the visitor branches on value 2 before adding rating.

Neither source model alone proves effective protection or zero skill progress in the installed Steam build.
