# Competing models

- **Q64-H1:** the teardown descendants do not award AV11/AV12 skill progress. Resolved object targets and arguments stay away from the skill-progress sink.
- **Q64-H2:** at least one cleanup callback routes AV11/AV12 into skill progress. A concrete descendant reaches the mapped sink with one of those ActorValues.

An unresolved dynamic object or indirect call is inconclusive. EV-0328 is intended to identify candidate producer/cleanup pairs, not decide H1/H2.
