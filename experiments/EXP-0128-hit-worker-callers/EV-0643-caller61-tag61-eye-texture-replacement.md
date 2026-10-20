# EV-0643 — Caller 61/tag-0x61 eye-texture replacement

## Competing models and discriminants

- H1, render/texture update: caller 61 queues a retained object and texture payload; its producer reaches the builder only after finding eye headpart geometry, and dispatcher case 0x61 replaces a nested texture pointer for two recognized object-type identities. It predicts the producer strings, tag, object/texture payload, and nested pointer update.
- H2, level-gated quest/encounter or HitData/armor-skill route: the payload or consumer also gates level-one content or reaches effective protection, HitData, AV11/AV12, or UseSkill. It predicts an explicit gate or mapped producer-backed edge; a shared worker queue alone is insufficient.

## Direct GOG evidence

Captures use the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Metadata confirms read-only execution, disabled auto-analysis, and matching executable identity. This project is distinct from Steam AE 1.6.1170.0; no GOG RVA is transferred to Steam.

- Caller 61 `FUN_140658f70` writes tag 0x61, retains its object argument by incrementing its reference count, stores the supplied second payload, and queues through `FUN_14065b800`. Its sole analyzed direct producer is `FUN_1409ebcb0` [EV-0643].
- The producer reports errors when the TextureSet is null, the target has no 3D, there are no eye-tagged headparts, or eye geometry cannot be found. On success, it resolves a texture-related value from the passed TextureSet and eye headpart, resolves the eye geometry, then queues tag 0x61 with the geometry object and supplied TextureSet [EV-0643].
- Dispatcher case 0x61 reads the two payloads, checks an object stored at receiver `+0x25` against two exact type-identity pointers (`DAT_14332c3a0` and `DAT_14332c3d8`), resolves the supplied value with `FUN_140326ef0`, replaces a nested pointer at `+0x78` when it differs, then calls a nested virtual slot +0x48 and three geometry/resource helpers [EV-0643]. The type identities and deeper rendering behavior remain unnamed.
- The builder has one direct outgoing call and the producer/dispatcher bodies show no explicit player-level predicate or mapped direct HitData, effective-protection, AV11/AV12, or UseSkill operation [EV-0643]. This is a bounded direct-body result, not a transitive or runtime negative.

## Result and limits

H1 is supported as an eye-geometry texture replacement route. H2 is unsupported by the captured direct producer and dispatcher bodies: no level, quest-start, HitData, protection, AV11/AV12, or UseSkill edge appears. Dynamic type descendants and runtime scheduling remain open. This is not a level-one bypass, armor-XP result, Steam result, or bounty resolution. No OBJ-1/OBJ-2 causal edge is added.

## Next action

Inspect the final exact worker caller 62/62, `FUN_140658fb0`, then reconcile the complete 62-body census and reselect an independent P0 line; caller completion does not resolve the bounty.
