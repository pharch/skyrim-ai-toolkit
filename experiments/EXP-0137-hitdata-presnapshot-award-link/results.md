# EXP-0137 results

Fresh read-only GOG AE 1.6.1179.0 captures of `FUN_1407ddf50`, `FUN_1407ded20`, and the callers show the target-side mitigation helper copies its current `+0x50` value to `+0x54`, then reduces `+0x50` through the target-side AV39/armor-factor path. The Player resolver's unblocked armor branch separately counts worn ARMO items with positive base DNAM, selects AV11 or AV12, and passes HitData `+0x54` as the skill points argument [EV-0670], [EV-0690], [EV-0699].

This `+0x54` value includes earlier builder adjustments and is not proven immutable after the copy. The captured direct bodies do not invoke selector `0x55` on the award points field. This supports the bounded model that zeroing a cache contribution does not directly zero the armor award argument; it may change the separate protection calculation. Earlier selectors before the snapshot remain open for Q91.

No live game, Steam match, measured armor protection, AVSK delta, or vanilla reproduction was performed. EV-0260 remains required.
