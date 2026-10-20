# Results — Q-0065 producer-backed class-family synthesis

## Question and competing models

Q-0065 asked whether PlayerCharacter +0x730, +0x8F8, +0x9D0, +0x9A0/+0x9A8, and ThirdPersonState +0xA0 share a concrete NiAVObject/NiNode finalizer family, or hold distinct data-selected scene/resource classes that happen to release through slot +0x8.

- H1 predicts exact producer-backed matching vtables and slot +0x8 targets for the cleanup values.
- H2 predicts exact differing tables or class provenance for those same values.
- A match requires the actual producer/result class for each field. A generic slot +0x8 call does not distinguish either model.

## Source-linked comparison

The identity-checked GOG AE 1.6.1179.0 evidence is bounded to the existing analysis executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; its RVAs do not transfer to Steam AE 1.6.1170.0.

- The NiNode parser candidate installs NiNode::vftable at RVA 0x19AC3F0. The +0x8F8 field loads the data-selected resource Actors\Character\1stPerson\Skel, but no supported NIF inspection identifies that asset's root or descendants [EV-0331, EV-0347].
- PlayerCharacter +0x730 follows a refcounted scene-child attach/detach pattern compatible with NiAVObject. NiNode slot +0x1A8/+0x1C0 methods are structural comparators; the actual parent and child tables and child finalizer remain unresolved [EV-0334, EV-0351].
- ThirdPersonState +0xA0 receives the result of slot +0x150 on an object returned by PlayerCharacter slot +0x378. The context receiver vtable, result class, and result finalizer remain unresolved [EV-0336, EV-0337, EV-0342, EV-0344, EV-0346].
- PlayerCharacter +0x9D0 returns opaque descriptor-selected values; +0x9A0/+0x9A8 receives a generic model-resource result through a two-slot adapter and sorted-name lookup. Neither path identifies the selected object's vtable or +0x8 finalizer [EV-0348, EV-0349, EV-0350].
- As a class-family comparator, the ProcessTrapHit child factory installs hkpConstraintInstance::vftable at RVA 0x1973D58. Its wrapper children select bhkFixedConstraint or bhkMalleableConstraint tables at RVAs 0x19EB9C0 and 0x19F50A8; their +0x158 destructor targets differ. These are exact physics classes on the captured factory path, not identified producer tables for the PlayerCharacter cleanup fields [EV-0355, EV-0356].
- Thus the observed physics tables show why slot +0x8 alone is not a class identity test. They do not prove that any unresolved cleanup field holds one of those classes or a class distinct from the other cleanup fields.

## Decision and limits

Neither Q65-H1 nor Q65-H2 wins. The source comparison separates known NiNode and physics table identities, but does not recover concrete producer-backed vtables for the target cleanup fields. No mapped descendant adds a direct Actor::UseSkill AV11/AV12 edge; unresolved field and child finalizers prevent a route-wide negative. No causal edge to OBJ-1 is supported.

This static line is blocked pending either a tested read-only NIF root inspector for the exact first-person skeleton asset and equivalent source-selected model roots, or verified same-build runtime class telemetry for the exact objects. Continue independent OBJ-1 and P0 static work while that discriminator is unavailable.
