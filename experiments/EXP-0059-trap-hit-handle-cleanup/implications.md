# Implications

- The first handle cleanup in the trap receiver is not exercised by this captured ProcessTrapHit builder path because HitData `+0x18` remains zero.
- The receiver-side conditional cleanup is a destruction dispatch through the PlayerCharacter `+0x20` secondary vtable.
- The handler-level static census and this narrower cleanup trace still do not prove that trap hits award no armor XP; eight teardown virtual sites and Steam runtime behavior are unresolved.
- This evidence changes the OBJ-2 handle/release model only. No shared quest state, ActorValue, call edge, ActiveEffect, or serialization dependency links it to OBJ-1.
- Keep the exact Steam positive-damage, protection, and raw-AVSK experiment at P0.
