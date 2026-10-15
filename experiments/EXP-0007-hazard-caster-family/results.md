# Results

## Static pass — 2026-09-23

The hazard factory copies `ActorCause` into `Hazard.ownerActor` for ordinary
actor casts. If the cause is absent, the tick path intentionally constructs a
stack `NonActorMagicCaster`; the internal SpellItem can still apply its effect,
but the active-effect caster lookup cannot reach `Actor::UseSkill`.

The alternate HAZD inventory did not identify a player action that clears the
copied cause while preserving a useful Blizzard payload. Walls and circles
are player-created actor-owned hazards; traps, environmental fire, Potema,
and quest hazards are fixed-payload controls. Empty-ground/wall Blizzard casts
avoid victim delivery rather than suppressing XP on useful damage.

Disposition: retain H-0005 for the actor/empty-ground/leave-before-tick
runtime controls, but close the “alternate caller alone supplies Blizzard
cause loss” sub-hypothesis.
