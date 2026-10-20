# Predicted outcomes

- **H1:** serialized `ENAM=LEVL` reaches a nondefault runtime event ID; a quest with ready bit clear fails the SetStage entry guard before EnsureQuestStarted. The GOG/source field-map branch is supported by EV-0314.
- **H2:** a set ready bit passes the initial OR predicate even with a nondefault event ID; later initialization and stage dispatch remain conditional. This guard logic is supported by EV-0313/0314, but the target's runtime bit is unknown.
- **H3:** the GOG/source mapping is incomplete or cannot be transferred to Steam; the exact target observer is required for a gameplay decision.

Regardless of outcome, callback availability, running state, alias fill, journal/dialogue, physical access, and numeric level remain separate observations.
