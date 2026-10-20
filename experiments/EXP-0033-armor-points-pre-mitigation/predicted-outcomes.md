# Predicted outcomes

| Observation | H1: post-mitigation input | H2: pre-resistance snapshot | H3: downstream whole-data clear |
|---|---|---|---|
| AV11/AV12 points load | Reaches mitigated `totalDamage` or a later value | Reaches HitData `physicalDamage` (`+0x54`) copied before AV39/armor reduction | A later helper can overwrite the `+0x54` source |
| Default and alternate builder order | Either builder must pass or derive the reduced value | Both call the common resistance helper before the receiver branch | Clear helper is called after builder and before the receiver branch |
| Clear-path effect | Not required | Must leave points source intact to support an unconditional claim | A store spanning `+0x50..+0x57` zeros both `totalDamage` and `physicalDamage` |
| Gameplay conclusion | Static points can vary with final mitigation | Static normal-path points are separate from final damage | Zero points are possible on the branch; protection and reachability remain separate tests |
