# Protocol

## Static source pass

1. Verify GOG `SkyrimSE.exe` ProductVersion and hash, resolve Address Library anchors from that same binary, and query only the configured existing Ghidra project read-only with auto-analysis disabled.
2. Trace `FUN_1407dd110` → `FUN_1407ddf50` → `FUN_1406b9df0`, compare with `FUN_1406bcaa0`, and preserve all direct/indirect call boundaries.
3. Trace PlayerCharacter slot `0x58`, slot `0xE7`, the cache writer at `this+0x274`, BOD2 subtype dispatch, rating inputs, and the DNAM parser destination.
4. Keep GOG RVAs separate from installed Steam AE 1.6.1170.0. Static source order and bounded xrefs cannot prove runtime behavior or a complete absence of indirect awards.

## Required live discriminator

Run only with the exact verified Steam runtime and complete selected load order, a disposable clean level-one save, a read-only numeric observer, and natural unmodified game state. Compare a naturally acquired, equipped positive-rating Light or Heavy armor candidate with an otherwise matched no-armor control. Use the same qualifying physical trap and capture multiple positive landed hits. Record numeric health before/after each hit, Light Armor and Heavy Armor AVSK before/after, level, armor item/condition/equipment state, and trap identity. Include a normal unblocked positive-damage hit as an armor-XP control.

The candidate passes only if the armor configuration measurably reduces incoming damage relative to control, both armor AVSK values remain exactly unchanged over repeated trap hits, and player level stays 1. The ordinary control must show the observer can detect relevant skill progression. Console stage/level forcing, injected scripts, and altered plugins are diagnostic interventions and cannot validate vanilla reproduction.
