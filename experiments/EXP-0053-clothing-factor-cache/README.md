# Clothing rating in the cached armor factor

This experiment resolves whether positive-DNAM Clothing records contribute to the GOG PlayerCharacter cache at `this+0x274`, which the GOG hit builder reads. It compares the BOD2 loader destination with the inventory rating visitor's subtype guard. It is static, read-only evidence for GOG AE 1.6.1179.0.

## Result

The BOD2 parser stores the second 32-bit word at runtime `ARMO+0x1BC`. The pinned TES5Edit schema identifies that word as Armor Type, with value 2 meaning Clothing. The visitor invoked by the `+0x274` cache writer skips records with value 2 before adding rating. Thus positive-DNAM Clothing does not contribute to this cached factor in the inspected GOG build. The existing EV-0261 trace connects the cached value to hit damage calculation.

This does not establish the Steam 1.6.1170.0 mapping, a live protection delta, zero Armor AVSK, or a vanilla reproduction. The exact level-one Steam test remains separate.

Evidence: EV-0311, with prior schema/record context EV-0309 and getter/hit-builder trace EV-0261.
