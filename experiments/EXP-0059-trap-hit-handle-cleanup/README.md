# Trap-hit handle cleanup and receiver teardown

**Frontier:** Q-0058, OBJ-2. **Status:** completed as a bounded GOG AE 1.6.1179.0 static trace.

EV-0319 traces the two first refcount-gated `+0x8` cleanup sites in `FUN_1406b9df0` against the captured ProcessTrapHit builder. The builder zeros HitData `+0x18/+0x1C`, then writes the PlayerCharacter-derived handle only at `+0x1C`; its two called helpers do not write `+0x18`. The first cleanup's HitData-derived local is therefore null on this route and its conditional release is skipped. The receiver-derived handle uses the PlayerCharacter secondary table at `+0x20`; under the handler's refcount condition, its release thunk dispatches to the PlayerCharacter destructor chain.

The destructor's large teardown body has eight unresolved indirect sites. The finding does not prove zero armor XP, positive effective protection, Steam behavior, or a vanilla reproduction. The exact Steam repeated positive-damage / protection / raw-AVSK experiment remains open [EV-0260]. No OBJ-1 causal edge is supported.
