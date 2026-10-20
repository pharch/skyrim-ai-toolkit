# EntryPoint handler and function-data side effects

This experiment corrects the Q82 field interpretation and bounds the handler
path for official HitData selectors 37/39. BGSEntryPointPerkEntry returns
DATA[1] as the handler ID; EPFT selects the separate function-data class
[EV-0683]. The official file rows therefore use handler IDs 1, 3, and 14,
not operation IDs inferred from EPFT.

GOG handler 3 uses OneValue data and updates a numeric result. Handler 14 uses
TwoValue data, reads ActorValue index 138 and a coefficient, and updates the
numeric result [EV-0684]. On a getter cache miss, handler 14's ActorValue call
can populate per-Actor and ActiveEffect derived-value caches [EV-0685]. No
direct equipment, HitData, source ActorValue, armor skill-progress, or event
writer was identified in the bounded capture. The ActorValueInfo callback
target for AV138 is unresolved.

The scope is the existing read-only GOG project plus the official five-master
selector/EPFT/EPFD screen. This cannot establish Steam equivalence, profile
winners, a live hit, effective armor protection, raw AVSK, or a vanilla
exploit. EV-0260 remains open.
