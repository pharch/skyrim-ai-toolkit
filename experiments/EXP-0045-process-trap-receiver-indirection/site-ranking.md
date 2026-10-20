# Preliminary callsite ranking

## Provenance and scope

This inventory reuses EV-0302's identity-attested GOG AE 1.6.1179.0 census of `FUN_1406b9df0`: metadata `gog-query-20261016T142837Z.meta.json` has `ok=true`, executable SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`, 89 direct edges, and 28 indirect sites. Raw stdout SHA-256 is `313c9d4f82f58d72db6884a2d749b652f24882553b2d4357144f358280b864b8`. CommonLib `HitData.h` in the pinned source snapshot (EV-0261) maps offset `0x20` to `sourceRef`; `ActorValueOwner.h` declares the virtual methods used below. No callsite here is a Steam RVA.

## Grouped census

| Rank | Site(s), GOG RVA | Receiver / operation | Current interpretation | Evidence / next step |
|---:|---|---|---|---|
| 1 | `0x6BA3F1`, `0x6BA649`, `0x6BAA42`, `0x6BAD3D` | `HitData.sourceRef` resolved to a `TESObjectREFR*`; slots `0x8E`, `0x8F`, and `0x51` | Fresh mapping identifies `AsExplosion` and `AsProjectile` base stubs returning zero, plus `GetActorCause` returning source-reference cause data; selected helper and handle-validation bodies show no skill award | EV-0303; derived-class overrides and runtime reference instances remain outside this base-slot screen |
| 2 | `0x6BA19C` | Actor vtable slot `0xF7` (`UseSkill`) on the player singleton; argument AV `0x0F` | Mapped AV15 Sneak award, not AV11/AV12 armor | EV-0295; preserve as a visible distinct skill branch |
| 3 | `0x6BA0B0`, `0x6BA215`, `0x6BA8F6` | Actor slot `0x99` | Mapped masked-state predicate | EV-0291/EV-0296; selected target and bounded callees show no armor award |
| 4 | `0x6BA331` | Actor slot `0x5C` | ActorMagicCaster object-provider path | EV-0296/EV-0297; concrete caster state branch has no mapped armor award |
| 5 | `0x6BA522`, `0x6BA884`, `0x6BAC43` | Actor slot `0x70` | Mapped state lookup/predicate path | EV-0296; selected targets and bounded callees show no armor award |
| 6 | `0x6BA283`, `0x6BA492`, `0x6BA952` | ActorValueOwner subobject at Actor `+0xB8`; vtable slots `0x01`, `0x03`, `0x06` | `GetActorValue(Health)`, `GetBaseActorValue(Health)`, and `RestoreActorValue(modifier 2, Stamina, value)` respectively; these are AV reads/resource mutation, not skill-credit sinks | GOG disassembly/decompilation plus EV-0261 CommonLib declaration; preserve the exact call arguments in the raw capture |
| 7 | `0x6BA047`, `0x6BA070`, `0x6BA6EA`, `0x6BA719`, `0x6BA870`, `0x6BA91D`, `0x6BADBC`, `0x6BADE6`, `0x6BAE36`, `0x6BAEF5`, `0x6BAF1F`, `0x6BAF48`, `0x6BAF6E` | `CALL [vtable + 0x8]` after refcount decrement checks | Thirteen destructor/release-style cleanup dispatches; target type remains untyped, but call position is conditional on reference-count cleanup rather than a visible skill-award producer | Existing decompilation around each decrement; lower priority unless a resolved object type or target contradicts the cleanup interpretation |

The groups partition all 28 sites (4 + 1 + 3 + 1 + 3 + 3 + 13). This is a triage classification, not a proof that every dynamic object or dispatch target is fully typed. The highest-ranked source-reference slots now have fresh base-target results; remaining uncertainty is concentrated in derived overrides and the thirteen release-style targets, not in an identified AV11/AV12 path.
