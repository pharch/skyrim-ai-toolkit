# Expected discriminants

| Model | Evidence that would support it | Evidence that would weaken it |
|---|---|---|
| H1: numeric result plus cache maintenance | Wrapper DATA[1]/EPFT split is producer-backed; handlers 1/3/14 only update the numeric result; the ActorValue getter's stores are bounded to derived caches; no gameplay setter, award, equipment, HitData, or queue write appears. | A matching handler or its concrete getter callback writes equipment, HitData, source ActorValue, skill progress, or queued state before the armor scan. |
| H2: relevant gameplay-state change | A producer-backed official row and reachable handler/function-data path reaches a relevant gameplay-state writer in the correct hit phase. | Complete target/call mapping restricts direct writes to numeric results and derived-value caches; unresolved dynamic callbacks are separately bounded. |

EV-0684/EV-0685 support H1 for the captured GOG bodies and direct stores, with
the AV138 ActorValueInfo+0x68 callback still unresolved. This does not prove
positive protection, zero XP, a profile winner, Steam behavior, or a vanilla
reproduction; EV-0260 remains required.
