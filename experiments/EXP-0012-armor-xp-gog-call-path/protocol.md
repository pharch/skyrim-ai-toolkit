# EXP-0012 protocol

## Competing models and predictions

- **H1 — inline hit-resolution award:** the same function that consumes populated HitData routes an incoming player hit to AV11/12 or Block AV9. A direct call/virtual dispatch should appear in the hit-resolution routine after hit data is populated.
- **H2 — separate or deferred award event:** armor XP is delivered by a later callback or different event whose call path is independent of the hit-resolution function. The function should not dispatch armor AVs itself.
- **Protection coupling question:** armor protection and the skill award may share a required input, or the award may have its own branch and positive-points gate. Static separation alone does not prove useful protection remains in a vanilla suppression state.

## Source identity

- GOG analysis executable: ProductVersion 1.6.1179.0, SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`.
- GOG Address Library: 1.6.1179.0, SHA-256 `3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e`.
- CommonLibSSE-NG source commit: `b93280e832f263dbef44e44cbe2936622a02f91a`.
- Installed Steam AE target is separately verified as 1.6.1170.0 in EV-0109; no GOG RVA is transferred to it.

## Read-only steps

1. Read CommonLib declarations for Actor::UseSkill, HitData damage fields, Heavy/Light AV IDs and PlayerCharacter skill progression.
2. Resolve `VTABLE::PlayerCharacter` through the matching GOG Address Library; query slot 0xF7 in the existing GOG project.
3. Query the hit-resolution candidate at RVA 0x6BCAA0 and its direct caller, then inspect the full target disassembly around its virtual UseSkill calls.
4. Query hit-data helper candidate RVA 0x7DD220 and compare structure fields with the CommonLib HitData declaration.
5. Treat the older EV-0036 as an untrusted navigation lead. Recheck each branch against current disassembly before using its interpretation.

## Controls and exclusions

All Ghidra queries were read-only with auto-analysis disabled against a copy/cache of the configured existing project; no binary was imported or reanalyzed. No game, save, plugin, or active order was modified. No live game or observer test was run. WSL/Linux static output does not establish Windows UI or in-game behavior.
