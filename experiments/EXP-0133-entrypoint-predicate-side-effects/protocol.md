# Protocol

1. Read EXP-0131 results, then validate every GOG capture against the existing
   GOG AE 1.6.1179.0 executable hash, read-only mode, and disabled auto-analysis.
2. Keep wrapper fields distinct: DATA[0] is the selector, DATA[1] is the
   handler ID returned by BGSEntryPointPerkEntry, DATA[2] is a separate byte,
   and EPFT/EPFD specify function-data class and payload [EV-0683].
3. Reconcile all official selector-37/39 file rows with handler IDs 1/3/14 and
   EPFT classes 1/2; preserve duplicate rows and do not claim profile winners.
4. Inspect concrete handler bodies and type gates, then trace any ActorValue
   getter side effects to bounded cache helpers. Separate cache writes from
   source ActorValue, equipment, HitData, skill-progress, and event writes.
5. Preserve raw Ghidra stdout/metadata under ignored .local; never modify the
   GOG project, game files, plugins, saves, or co-saves.
6. Keep the unresolved AV138 ActorValueInfo+0x68 callback target explicit.
   Do not transfer GOG RVAs or static behavior to Steam AE.
7. Keep EV-0260's exact Steam test requirements: verified target and complete
   order, clean level-one save, ordinary matched hits, positive effective
   protection, raw AVSK and HitData observations, controls, and repetitions.
   Console forcing, injected scripts, and altered plugins are diagnostic only.
