# EXP-0040 predicted outcomes

| Observation | H1: Durak helper only | H2: questline-wide gate |
|---|---|---|
| `GetLevel` condition on a Story Manager node | Expected; its child selects the Durak helper | Expected, but it must also gate actual quest startup or every alternate path |
| VQ00/VQ01 QUST conditions | Stage/cell/actor conditions; no `GetLevel` in the inspected records | A required `GetLevel` condition appears on the actual transition or attached start path |
| Guard rumor or Fort route below level 10 | Possible separate start/progression path | Can reveal location/journal state but cannot execute actual gated transition |
| Clean level-one Fort test | `Awakening` starts/progresses while level remains 1 | No actual quest transition until the gate condition is satisfied |

The current captures support H1 at the serialized helper boundary. The final row remains a live-runtime discriminator.
