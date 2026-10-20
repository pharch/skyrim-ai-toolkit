# Protocol

1. Verify the existing GOG 1.6.1179.0 project and query Actor, Character, and PlayerCharacter vtable slot `0xE3` read-only; preserve slot lookup, target body, and xref limitations.
2. Trace `FUN_1406bcaa0`, `FUN_140717420`, `FUN_140717440`, and `FUN_1406b9020` for the process flag, actor combat predicate, and zero-data call.
3. Map native offsets only through the pinned CommonLibSSE-NG commit recorded with EV-0261 and EV-0286; distinguish repository layout interpretation from native engine observation.
4. Inspect bounded direct callers of the doNoDamage getter/setter to identify reset sites and any setter capable of passing true. Do not claim global writer absence from a bounded xref screen.
5. Keep natural occurrence, protected-damage outcomes, Steam behavior, and raw AVSK changes open unless directly measured on a verified exact target.
