# Results — EXP-0028

- The matching GOG Address Library maps VTABLE::ActiveEffect ID 205813 to RVA 0x187C738 for GOG AE 1.6.1179.0; all addresses remain GOG-scoped (EV-0279).
- Base SaveGame/LoadGame write and restore elapsed time, duration, magnitude, flags, reference fields, and usUniqueID; FinishLoadGame reattaches associated reference-effect entries (EV-0279).
- Base Update and Finish are one-instruction return stubs. CanFinish is a separate conditional gate, and the inspected Compare body does not read usUniqueID (EV-0279). These findings do not identify the outer timer/expiry dispatcher or every derived override.
- No save/co-save input or ActiveEffect observer is configured; no wait, travel, save/load, reapplication, or in-game behavior was tested (EV-0260). The functional models remain unresolved.

No Steam RVA transfer, active-order winner, or vanilla reproduction is claimed.
