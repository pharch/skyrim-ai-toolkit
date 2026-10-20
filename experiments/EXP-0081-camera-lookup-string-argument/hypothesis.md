# Competing models

- Q65-H1: the PlayerCharacter slot+0x378 result is a NiNode-compatible object and slot+0x150 performs a named-child lookup.
- Q65-H2: the getter returns another interface object with its own slot+0x150 behavior.

The argument is a reference-counted pointer copy, but the receiver vtable and runtime value remain unknown.
