# Protocol

## Static native trace

1. Verify the configured GOG `SkyrimSE.exe` ProductVersion and hash; query only the existing GOG Ghidra project with read-only mode and auto-analysis disabled.
2. Resolve the Papyrus `Quest.SetStage` binding through Address Library, registration tables, or a build-matched string/reference path. Preserve the exact native function identity and caller path; do not assume a CommonLib name matches without matching evidence.
3. Trace stage storage, running-state checks, `Start` or start-request calls, Story Manager dispatch, alias/event initialization, and return behavior. Use direct-call edges, disassembly, and xrefs as well as decompilation where signatures are ambiguous.
4. Compare the native mechanism with the source inputs in EV-0310 (DA02 QUST/Story Manager/book callback) and EV-0301 (DA04 book route). DA02's book is level-gated in its fixed placements and ordinary leveled lists; the source callback alone is not a naturally available level-one exploit.
5. Keep every GOG RVA scoped to GOG AE 1.6.1179.0. No Steam address transfer is permitted.

## Runtime discriminator

The decisive test requires verified Steam AE 1.6.1170.0, the complete exact target plugin order, a disposable clean level-one save, and a read-only observer for numeric player level, quest running flag, stages, journal state, aliases, dialogue/event availability, and functional access. Compare a no-callback control with a naturally reachable SetStage callback and a positive control for an already-running quest. Require unchanged level 1 and no console/script/plugin state forcing.

If a controlled manual SetStage invocation is ever used to isolate native semantics, label it `diagnostic_intervention`; it cannot validate a vanilla candidate and must not be run unattended. A natural level-one bypass requires an independently reachable unmodified callback and functional progression.
