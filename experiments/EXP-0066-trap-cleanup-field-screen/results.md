# Results — final-release-field scans

EV-0328 records four complete GOG whole-program displacement scans: `+0x9D0` (21 operand hits, 9 writer candidates), `+0x9A8` (24, 7), `+0x9A0` (22, 5), and `+0x8F8` (32, 8). All four report zero computed writer candidates. PlayerCharacter setup and teardown access the first three offsets; same-offset matches elsewhere remain untyped. `+0x9A8` and `+0x9A0` share a `FUN_140744xxx` access cluster that warrants receiver tracing.

For `+0x8F8`, `FUN_140736be0` calls the resource routine with `Actors\Character\1stPerson\Skel` and stores the returned object in PlayerCharacter `param_1[0x11f]`. Cleanup method `FUN_140737210`, called by PlayerCharacter teardown, clears and final-releases that field through vtable slot `+0x8`. The actual class/vtable target remains unknown.

Q-0064 H1/H2 remain unresolved; no complete no-award result or Steam runtime comparison exists [EV-0328], [EV-0327], [EV-0325], [EV-0319], [EV-0324], [EV-0260].
