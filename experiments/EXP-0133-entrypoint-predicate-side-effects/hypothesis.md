# Competing models

## Q84-H1 — numeric handler with cache-only ActorValue maintenance

For the exact GOG path and official selector 37/39 rows, DATA[1] chooses the
handler and EPFT selects the function-data class. Handler IDs 1/3/14 compute
numeric entrypoint results; handler 14's ActorValue getter may maintain
derived-value caches on a miss but does not alter equipment, HitData, source
ActorValue inputs, skill progress, or queued gameplay state in the captured
path.

**Prediction:** exact wrapper, class, record, handler, and cache stores map to
the numeric result and derived-value caches. No authoritative gameplay writer,
UseSkill/AVSK sink, equipment mutation, HitData mutation, or event submission
appears in the captured path.

## Q84-H2 — relevant gameplay-state change

At least one matching handler, function-data implementation, or dynamic
ActorValueInfo callback changes equipment, HitData, source ActorValue state,
skill progress, or queued gameplay state before the later worn-armor scan.

**Prediction:** a producer-backed target reaches a relevant field store,
setter, progress sink, or event submission in the phase before
FUN_1406bcaa0 scans worn ARMO.

The captured direct bodies support H1 within the resolved scope [EV-0684],
[EV-0685]. The AV138 ActorValueInfo+0x68 callback remains unresolved, so H2 is
not globally excluded. No runtime or Steam behavior is inferred.
