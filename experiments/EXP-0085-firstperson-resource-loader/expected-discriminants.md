# Expected discriminants

1. Identify the exact root class for Actors\\Character\\1stPerson\\Skel through a supported read-only asset or runtime observation.
2. Map its concrete vtable slot +0x8 and descendants.
3. Screen the full release chain for Actor::UseSkill AV11/AV12.
4. Trace +0x9D0 and +0x9A0/+0x9A8 independently while the NIF class remains unresolved.
