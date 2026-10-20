# EXP — WICast Marked-for-Death negative-resistance candidate

**Status:** official-master static candidate narrowed with secondary event API documentation; no gameplay result.

OBJ-2: determine whether an ordinary WICast event can apply a Marked-for-Death AV39 effect to the player in a reachable eligible location, then test its interaction with blocked-hit points. The installed Steam AE raw record screen shows a Player-conditioned CAST/R1 `CastingActor` alias and a separate CAST/R2 `SpellTarget` alias. A CK-Wiki-derived Papyrus Index page defines the event parameters as caster and target but warns that `akSpellTarget` always returns None ([EV-0244]). This supports a player-cast response interpretation and weakens the claim that WICast targets the player; actual event payload and alias fill remain unobserved.

Linked source evidence: `EV-0022`, `EV-0035`, `EV-0021`, `EV-0037`, current official-master captures `EV-0224`–`EV-0230`, and event-schema follow-up `EV-0241`/`EV-0244`. WICast has a separate forced Player alias and event-filled SpellTarget alias; R1-to-caster/R2-to-target is an inference from the record plus API signature, and target `None` is a documentation caveat rather than a live observation. See `research/EVIDENCE.json` for hashes and source/build limits.
