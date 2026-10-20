# Protocol

1. Verify the existing GOG analysis executable identity and preserve read-only/no-analysis metadata; do not transfer its RVAs to installed Steam AE.
2. Trace the player receiver's AV11/AV12 `UseSkill` points load to the HitData stack base and map the offset with EV-0217.
3. Inspect both hit-data population paths and the common mitigation helper to locate the snapshot, AV39/armor-factor calculation, and any later writes to the points field.
4. Trace any helper that can clear the points field after mitigation, recording its caller condition without assigning names or gameplay semantics that the evidence does not establish.
5. Compare source order with the positive-points PlayerCharacter sink. Do not infer an XP delta, functional protection, player reachability, or Steam behavior from static code.
