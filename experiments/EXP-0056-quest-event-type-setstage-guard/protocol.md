# Protocol

## Static source and native-field trace

1. Read EV-0313's bound Quest.SetStage guard and EV-0289's CommonLib/layout evidence for quest event ID; keep `Quest.SetCurrentStageID` behavior separate.
2. Recheck the exact official-source QUST `ENAM` fields for DA02, DA09, and DA06 using EV-0310, EV-0306, and EV-0308; record each source plugin/hash and distinguish parser output from active-order winners.
3. Trace the GOG QUST/event-type loading path only in the existing 1.6.1179.0 project, read-only with auto-analysis disabled. Look for a build-attested write of serialized event type into the field read at `quest+0xE0`; do not assume field identity from offsets alone.
4. Compare source types and callback predicates. Keep a source/layout mapping, a native GOG observation, and a Steam runtime observation as separate evidence classes.

## Runtime discriminator

The decisive target test requires verified Steam AE 1.6.1170.0, complete exact load order, a disposable clean level-one save, and a read-only observer for numeric level, quest running state, serialized/runtime event type if exposed, ready flags, stage, Story Manager context, aliases, journal/dialogue, and functional access. Compare ordinary no-callback and natural callback runs; never force stage, level, event context, flags, aliases, or plugin state. If the observer lane remains unavailable under EV-0260, continue static work and checkpoint the precise runtime test.
