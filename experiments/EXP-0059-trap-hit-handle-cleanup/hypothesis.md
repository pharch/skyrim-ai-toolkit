# Competing models

## H1 — Captured trap route skips the HitData-handle cleanup

The ProcessTrapHit builder initializes HitData `+0x18/+0x1C` to zero, stores its receiver-derived handle only at `+0x1C`, and neither called builder helper changes `+0x18`. The receiver later resolves the zero `+0x18` field, so the first conditional slot `+0x8` release is skipped on this route. The second handle is the PlayerCharacter receiver and its conditional release dispatches through the PlayerCharacter `+0x20` secondary table into teardown.

**Predicted discriminant:** preserve initialization, all builder writes and helper calls, the downstream handle lookup, and the first cleanup branch; identify the receiver's exact secondary-vtable entry and slot-0 target.

## H2 — A builder helper supplies a nonzero HitData handle

At least one helper writes a nonzero value to HitData `+0x18`, allowing the first cleanup to reach a concrete release target on the captured trap path.

**Predicted discriminant:** a direct or indirect helper write to `+0x18` after the initializer, or a preserved nonzero value reaching the handler's `local_3c0` lookup.

## Separate XP interpretation

A descendant of the receiver teardown could still reach skill progress through one of the unresolved indirect sites. Finding a destructor chain does not establish the absence of such behavior. The Steam positive-damage / effective-protection / raw-AVSK experiment is an independent gameplay test.
