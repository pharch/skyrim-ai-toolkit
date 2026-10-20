# Results

- GOG AE 1.6.1179.0 slot `0xE3` maps to `Actor::IsInCombat` in the pinned CommonLib header. The queried Actor and Character vtables resolve this slot to `FUN_1406b9000`; the PlayerCharacter vtable overrides it with `FUN_14075a660` ([EV-0286]).
- Actor runtime data uses the 1.6.629+ layout in GOG 1.6.1179. The native resolver's `[Actor+0xF8]` is `currentProcess`; `[Actor+0x160]` is the combat-controller pointer read by the queried base implementation ([EV-0286]).
- `FUN_140717420` and `FUN_140717440` test/clear `*(currentProcess+0x08)+0x324`, mapped by the pinned headers to `middleHigh->doNoDamage`. The resolver consumes this one-shot byte, then calls `FUN_1406b9020`. That function returns false if `IsInCombat` is false or the process byte at `+0x139` is nonzero; the header names the latter `ignoringCombat` ([EV-0286]).
- When the predicate returns false, `FUN_1407dda40` clears the 8-byte HitData region at `+0x50`, zeroing both totalDamage and physicalDamage before receiver routing ([EV-0285], [EV-0286]).
- The analyzed project reports six direct calls to the setter. Four pass zero. `FUN_14048a5b0` passes a bit derived from an input byte and is the only observed direct xref that can set a nonzero value. Its callers/source meaning remain unresolved, so Q-0027 follows.
- H1 is supported and H2 is falsified as an armor-specific mechanism. No natural occurrence, actual AVSK delta, effective protection, or Steam result was measured.
