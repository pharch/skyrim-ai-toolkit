# EXP-0137 — HitData snapshot and armor skill award

**Status:** Q90 completed as a bounded static GOG trace; Q91 continues with earlier entry-point data.

**Objective:** Determine whether selector-0x55 cached armor-rating adjustments directly change the points argument to the Player's unblocked armor-skill award.

**Build:** GOG Skyrim AE 1.6.1179.0, executable SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. This is distinct from installed Steam AE 1.6.1170.0 [EV-0109].

**Result:** In the captured path, `FUN_1407ddf50` copies HitData `+0x50` into `+0x54` before later target-side AV39/armor-factor reductions to `+0x50`. The resolver's unblocked branch checks positive raw ARMO DNAM and passes `+0x54` as the armor skill points argument. The bodies do not directly dispatch selector 0x55 on that field [EV-0670], [EV-0690], [EV-0699].

**Limit:** Earlier builder modifiers run before the copy. No live landed hit, effective protection, Steam behavior, or raw AVSK delta is measured; preserve EV-0260. This experiment provides no vanilla exploit result.
