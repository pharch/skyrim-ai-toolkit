# Hypotheses

- **H1 — resistance path is used:** a Clothing ARMO ENCH modifies an ActorValue read by the target's incoming spell/element resistance check. Expected evidence: an exact ARMO -> ENCH -> MGEF chain, a Health MGEF with a matching ResistValue, and a build-attested target check that reads those values.
- **H2 — no source candidate:** no official-five-master Clothing ARMO has a resolved resistance MGEF chain. Expected evidence: a schema-correct exact-five-master screen with no matching effects.
- **H3 — nominal-only effect:** the item has a resistance-like effect, but the target check does not consume it for a Health MGEF or the effect is not applied to the wearer. Expected evidence: a source/code mismatch between the Clothing effect, the Health MGEF ResistValue and the target's check.

H1 is supported as a GOG static candidate. H2 is falsified for the resolved BOD2/BODT Clothing subset. H3 is disfavored by the mapped Actor `CheckResistance` implementation, but actual Steam health-damage reduction remains unmeasured.
