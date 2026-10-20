# Expected discriminants

| Question | H1 prediction | H2 prediction | Evidence required |
|---|---|---|---|
| Does the receiver path use armor mitigation? | A build-attested field/dataflow affects final trap damage from worn armor | A path bypasses the armor inputs or does not use them | Exact `ProcessTrapHit` path, field provenance, protection calculation and final damage sink |
| Can indirect dispatch award AV11/AV12? | All relevant receiver/callback targets are resolved without armor-credit calls | At least one relevant target reaches AV11/AV12 credit | Enumerated unresolved callsites, runtime-initialized tables and concrete player targets; state any remaining unresolved sites |
| Does the in-game result preserve protection without XP? | Same-level positive unblocked trap damage falls with functional armor while raw Light/Heavy Armor AVSK is unchanged | Armor does not reduce damage, or AVSK changes | Exact Steam identity and full order, clean level-one save, positive damage, armor/control runs, raw AVSK before/after and repeated control |

Misses, sub-threshold impacts, blocks, zero damage, nonfunctional armor, console changes, injected scripts and altered plugins do not discriminate vanilla behavior.
