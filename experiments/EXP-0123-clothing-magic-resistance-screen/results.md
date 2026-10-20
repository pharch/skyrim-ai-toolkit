# Results

## Source-record screen

`screen_clothing_enchantments.py` parses the exact five official masters through `tools/plugin_reader.py`. The v2 capture hashes each source file and resolves 3,675 unique ARMO winners. It classifies 1,076 records as Clothing from valid BOD2/BODT fields; 572 link to ENCH, producing 790 effect rows with no unresolved ENCH/MGEF links. Nine BODT rows are short of the optional Armor Type field and remain unclassified.

Example candidate chain:

- Skyrim.esm ARMO `000FC061`, `EnchNecklaceResistMagic01`, BOD2 Armor Type 2 (Clothing), links to ENCH `000FC05B` `EnchArmorResistMagic01`.
- ENIT is constant-cast/self-delivery. The effect has magnitude 10.0 and no ENCH CTDA condition.
- EFID resolves to MGEF `000B7A35` `EnchResistMagicConstantSelf`; DATA gives archetype 34 (Peak Value Modifier), primary ActorValue 44 (Resist Magic), with no MGEF CTDA condition.
- The ARMO DNAM armor rating is zero. This candidate supplies an enchantment resistance route, not physical armor rating.

Capture: `.local/alignment/transactions/TX-20261018-0008/clothing-enchantment-scan-v2.json`, SHA-256 `5cf9403e9bcc87f2c856d1b84ae3abfad5570a72dad3d52565349199b2d31e7f` [EV-0398]. The five source hashes are Skyrim.esm `2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107`, Update.esm `c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9`, Dawnguard.esm `1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4`, HearthFires.esm `ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97`, and Dragonborn.esm `5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b`.

The independent MGEF screen resolves 1,573 unique MGEFs and finds 231 Health-primary effects with ResistValue AV40–44: AV40=37, AV41=87, AV42=44, AV43=35, AV44=28. Examples include Skyrim.esm `0010FDD1` `crFireDamageConcAimed` (Health/AV24, ResistValue AV41), `0010FDD2` `crShockDamageConcAimed` (AV42), and `0010FDD3` `crFrostDamageConcAimed` (AV43). The capture is `.local/alignment/transactions/TX-20261018-0008/health-damage-mgef-screen.json`, SHA-256 `15bac62390a917d18c2b404766e0b154582b51fbfd9c852bd6a4d22ec5951cf0` [EV-0399].

## GOG native trace

The configured CommonLib headers declare Actor's `MagicTarget` base at AE offset `0xA0`; the exact header hashes are in the RTTI capture. Resolving all ten `VTABLE::Actor` entries against the GOG 1.6.1179.0 Address Library and reading their x64 RTTI identifies entry 4, RVA `0x189F638`, as class Actor subobject offset `0xA0`. The GOG vtable slot `0x0A` at that address targets `FUN_1406c45a0` (RVA `0x6C45A0`), matching the CommonLib `MagicTarget::CheckResistance(MagicItem*, Effect*, TESBoundObject*)` declaration.

The bounded decompilation shows the function reading a resistance ActorValue through the ActorValueOwner subobject at `param_1 + 0x18` and virtual slot `+0x8` (the source-declared `GetActorValue` slot 1). It selects AV `0x2C` (44) or `0x28` (40), reads the incoming `Effect`'s `baseEffect` pointer at `+0x10`, and conditionally reads the effect setting's configured ResistValue when it differs from the selected default. The Health MGEF examples above configure AV41/42/43. The function then passes two resistance values to `FUN_14041ac40`, which computes a residual factor using build-specific data constants; those constants and a live damage reduction are not claimed here.

The GOG captures independently verify the executable SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`, ProductVersion 1.6.1179.0, read-only existing project, disabled auto-analysis, and no import/overwrite/project creation. RTTI raw capture: `.local/alignment/transactions/TX-20261018-0008/actor-vtable-rtti-census-20261018T164503Z.json`, SHA-256 `c5dc8a4de30ea40c59fb8b9f5d709cfb9c2061626b0b85e63b6c6fadf56379b2` [EV-0400]. CheckResistance query stdout `.local/ghidra/gog-query-20261018T164515Z.stdout.raw`, SHA-256 `65903ddf5d9fccaac100ba4f35ca4fd190eead6cba8c0ef81b7a5329416e8eb0` [EV-0401]. Direct-helper query stdout `.local/ghidra/gog-query-20261018T164714Z.stdout.raw`, SHA-256 `e8fbef866347d1fc1ebfc9d1ff6e8dac8127d641ff0983f2f0bc595dacc217d9` [EV-0402].

## Scope and uncertainty

This is a GOG source/code candidate, not a Steam runtime observation. It does not show that this necklace is naturally available at level 1, that a qualifying incoming attack occurred, that the measured damage changes, that AV11/AV12 stay numerically unchanged, or that the exact Steam build follows the same path. Official-master source winners do not establish a profile-specific winner. The resistance candidate is separate from the unresolved physical cached armor-factor contribution in C-OBJ2-CLOTHING-FACTOR.
