# Competing models

- H1: PlayerCharacter slot +0x378 with flag zero returns an NiAVObject/NiNode-compatible context root; slot +0x150 performs named-child lookup.
- H2: the context getter returns another interface implementation sharing a slot layout; NiNode is only a comparator.

The captured getter selects either a TLS context field or a nested +0x68 field. Neither branch supplies a concrete class.
