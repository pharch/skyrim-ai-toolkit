# EXP-0123 — Clothing resistance effects and the GOG resistance check

**Status:** source-backed OBJ-2 protection candidate; live Steam protection and Heavy/Light AVSK results remain unmeasured.

**Question:** Does an official Clothing ARMO enchantment modify a resistance value used by the incoming spell/element check, while the item remains outside the Heavy/Light armor hit-XP selector?

**Result:** The exact official-five-master source screen resolves 3,675 unique ARMO records and classifies 1,076 as Clothing from valid BOD2/BODT fields. It finds a 10% Resist Magic necklace chain: Skyrim.esm ARMO `000FC061` `EnchNecklaceResistMagic01` -> ENCH `000FC05B` -> MGEF `000B7A35` `EnchResistMagicConstantSelf`, a constant self-targeted Peak Value Modifier to AV44. A separate MGEF screen finds 231 Health-primary effects with configured resistance ActorValues, including source Fire/Shock/Frost examples with AV41/42/43.

The RTTI-identified Actor subobject vtable at offset `0xA0` maps `MagicTarget::CheckResistance` slot `0x0A` to GOG function `FUN_1406c45a0`. That function reads ActorValues through the ActorValueOwner subobject and conditionally reads the incoming effect's configured resistance value; its result passes through a two-value residual-factor helper. This supports the record/code candidate for magic and elemental protection independently of Clothing's Heavy/Light selector exclusion [EV-0398–EV-0402].

**Boundary:** read-only official-master source and GOG AE 1.6.1179.0 static analysis. No item acquisition at level 1, live damage comparison, qualifying-hit record, numeric AVSK result, Steam 1.6.1170.0 mapping, or vanilla exploit is established. The physical cached armor-factor question remains separate.

See [hypothesis](hypothesis.md), [expected discriminants](expected-discriminants.md), [protocol](protocol.md), [results](results.md), and [implications](implications.md).
