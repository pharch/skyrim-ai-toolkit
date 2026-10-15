# EXP-0005 — Marked-for-Death world-interaction armor routing

Status: IMPLEMENTATION-SUPPORTED CANDIDATE; awaiting observer-ready runtime validation.

Question: Can an ordinary world-interaction event cast a Marked-for-Death word at a level-1 player, drive DamageResist (AV39) negative, and make a blocked hit produce non-positive Block XP while the armor branch remains understood?

Static basis: `WICastDragonBornShouts` contains all three voice forms; `WICastMagic03/04` aliases `CastingActor`, `SpellTarget`, `Location`, and `Player`; `VoiceMarkedForDeathArmorEffect01` modifies AV39 for 60 seconds at magnitudes 25/50/75.

The winning QUST conditions also require a Story Manager cast event whose
spell/event data passes the `WICastDragonBornShouts` list and a current-location
`WIComplexInteractionToggle` keyword-data condition. This is a native event
selection gate, not a Papyrus `Cast` call.

`WIFunctionsScript` exposes the corresponding counter writers:
`DisallowComplexInteractions` decrements location keyword data and
`AllowComplexInteractions` increments it. Runtime cell selection must record
that value because a negative counter suppresses the WICast branch.
Static caller tracing identifies official counter writers in Civil War,
MQ102/Riverwood, Dragonborn MQ04/Skaal Village, and Dragonborn MH01/Thirsk.
This makes location suppression a cross-quest shared state surface.
