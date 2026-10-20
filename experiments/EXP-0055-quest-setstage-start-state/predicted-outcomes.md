# Predicted outcomes

- **H1, accepted stopped-quest startup:** a stopped quest that passes the entry and EnsureQuestStarted guards reaches startup manager work before the stage callback. EV-0313 supports this branch in GOG; a level-one natural Steam callback still must establish running state, aliases, and functional progress.
- **H2, guarded rejection:** a stopped event-scoped quest with a nondefault event ID and a clear ready bit exits before startup/stage work. EV-0313 exposes a relevant guard, but DA02's runtime field mapping and Steam values remain unresolved.
- **H3, stage without functional access:** stage storage or manager/reference initialization occurs without usable quest progress. The live observer must distinguish running state, alias fill, journal/dialogue readiness, and physical access.
- **Static-only narrowing:** if decompilation omits an indirect or queued start path, classify the result as unresolved and create a focused successor; do not turn missing xrefs into a negative.
- **Diagnostic only:** a console/script SetStage call may distinguish low-level state handling but is not a vanilla level-one reproduction.
