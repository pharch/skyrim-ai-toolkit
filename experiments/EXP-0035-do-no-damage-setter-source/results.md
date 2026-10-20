# Results

- `FUN_14048a5b0` has one observed direct code caller: `FUN_14048a390`. The setter input is bit 1 from byte `+0x08` of parameter slot 7, obtained through `FUN_140455010` ([EV-0287]).
- `FUN_14048a390` calls it only when currentProcess exists and its processLevel byte at `+0x137` is 0 or 1. The pinned CommonLib layout names those High and MiddleHigh ([EV-0287]).
- The callback constructs `TESActionData`/`BGSActionData` objects and processes multiple indexed parameters. The direct caller and setter bodies have no observed direct HitData resolver call ([EV-0287]).
- The Ghidra project reports no direct incoming code-call xref for `FUN_14048a390`, but has a data reference to it in an unresolved adjacent code-address table. Its dispatch owner and the meaning of parameter slot 7 are unknown.
- H1's direct hit-resolution caller model is falsified; H2 is supported for the bounded static route. The callback could still be selected indirectly for an attack animation, so ordinary attack reachability and live occurrence are unresolved.
