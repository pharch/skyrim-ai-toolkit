# Contradictions and Competing Models

Historical source claims are retained as competing models. The assessments below record the source report's current view, not a fresh test in this setup.

## C-LEG-0001 — Tied alchemy ordering and item class

- **Model A:** ingredient or insertion order controls the first matched hostile flag and therefore potion/poison classification.
- **Model B:** a stable cost-sorted matcher determines class; apparent order changes reflect a different recipe or hidden state.
- **Source:** `EV-0003`, `EV-0025`, `EV-0094`, `EV-0107`, user-reported context in `EV-0041`.
- **Current legacy assessment:** static preview/commit analysis keeps both open; commit effect order and dynamic item flags are required.
- **Discriminant:** same ingredients in both selection orders; capture dynamic ENIT and ordered EFIT before consuming.

## C-LEG-0002 — Beneficial effect under negative Poison Resistance

- **Model A:** poison item class plus effect flags/archetype can scale a beneficial effect.
- **Model B:** beneficial effects bypass resistance; observed changes reflect another effect or route.
- **Source:** `EV-0003`, `EV-0026`, user-reported context in `EV-0041`.
- **Current legacy assessment:** source user report/static flags favor scaling for specific cases only; no universal rule.
- **Discriminant:** matched effect as potion and poison, with positive/negative resistance controls and isolated application.

## C-LEG-0003 — Deadload timer versus cleanup queue

- **Model A:** finite effect timers advance during the buffer while cleanup is missed.
- **Model B:** the boundary is primarily an input/load-worker queue; elapsed time does not explain the retained state.
- **Source:** `EV-0003`, `EV-0027`, `EV-0028`, `EV-0075`–`EV-0078`, `EV-0105`.
- **Current legacy assessment:** static analysis favors a queue/load boundary, and a historical user report says game time freezes during deadload. That report weakens expiry-inside-deadload models but has no raw trace here. A direct `RemoveSpell` inverse and a separate MGR21 save/revert mismatch remain hypotheses; neither is the same as finite timer expiry.
- **Discriminant:** compare timer, source, membership, and functional payload at first load and after a second save/load.

## C-LEG-0004 — Weakness-to-Poison Peak stacking

- **Model A:** null/non-Keyword associated forms prevent Peak-chain collision.
- **Model B:** magnitude differences make a normally superseded effect visible.
- **Source:** `EV-0003`, `EV-0025`, user-reported context in `EV-0041`.
- **Current legacy assessment:** static key analysis favors A; magnitude-separated controls remain required.
- **Discriminant:** same-key Fortify and null-key Weakness effects at equal and separated magnitudes; record instance membership and raw values.

## C-LEG-0005 — Armor XP redirect versus zero total XP

- **Model A:** a blocked physical hit skips Heavy/Light Armor awards but may credit Block.
- **Model B:** a blocked hit awards no skill XP when the selected Block points are non-positive.
- **Source:** `EV-0020`, `EV-0021`, `EV-0036`, `EV-0037`.
- **Current legacy assessment:** ordinary blocked points may be positive; a negative-resistance route is only a static candidate. “No armor XP” and “no skill XP” remain distinct.
- **Discriminant:** capture hit flags, physical and total damage, AV9/11/12 calls, and raw AVSK deltas under a verified control/candidate pair.

## C-LEG-0006 — Simplified Shift Kit arithmetic versus measured cleanup model

- **Model A:** the root summary's signed-magnitude overflow and illustrative float32 ULP calculation directly predict the residual for a candidate item pair.
- **Model B:** float32 aggregation can leave a residual, but its sign and amount depend on effective source magnitudes, source identity, operation order, and cleanup values; the root arithmetic is only illustrative.
- **Source:** `EV-0040`, `EV-0005`, `EV-0014`.
- **Current legacy assessment:** the detailed mechanism report supports float32 aggregation as a numeric primitive and explicitly requires raw values/order. The root summary's exact numeric examples are not independently reproduced and must not be treated as a current-build prediction.
- **Discriminant:** capture raw ActorValue bits and each source's applied/cleanup magnitude at every equip/unequip boundary on the verified target.

## C-LEG-0007 — Float32 cleanup operand and observed slot delta

- **Model A:** `+0x94` is the Recover cleanup operand.
- **Model B:** cleanup adds the negated current effective magnitude through the actor modifier path; `+0x94` is updated afterward with the observed slot delta.
- **Source:** [EV-0057].
- **Current legacy assessment:** the later static report explicitly corrects Model A. Its float32 residue values remain modeled predictions and do not establish player-reachable same-slot writers.
- **Discriminant:** on a verified build, capture the exact modifier source, effective magnitude, aggregate bits, cleanup argument, and post-cleanup `+0x94` value.

## C-LEG-0008 — Finite potion cleanup versus a persistent timer bypass

- **Model A:** a reachable non-finite timer or expiration-bypass writer lets a useful alchemy effect avoid native finish and Recover cleanup.
- **Model B:** finite alchemy effects finish through native cleanup before Papyrus callbacks; no ordinary official writer for the proposed non-finite/bypass state was found in the audited scope.
- **Source:** [EV-0058], [EV-0078], [EV-0079], [EV-0096]–[EV-0099].
- **Current legacy assessment:** static reports support synchronous cleanup and did not identify an ordinary writer; a zero-duration ingredient still finishes at elapsed zero, the scanned record flag does not bypass expiry, and no official Dispel caller was identified. Transformation does not clear arbitrary potion effects. This is a scoped negative result, not proof that no writer exists in all AE load orders.
- **Discriminant:** verify the executable and full active order, then trace a concrete ordinary writer and compare effect source, flags, timer, and raw ActorValue before/after finish and save/load.

## C-LEG-0009 — “Confirmed” mixed-poison delivery versus missing route evidence

- **Model A:** the old candidate index and poison domain summary describe a confirmed hostile-first Fortify Destruction route with follower/frenzy delivery.
- **Model B:** the linked result and later inventory establish only a historical hostile-first classification observation; exact recipe, resistance amplification, dynamic item state, delivery, and XP budget remain unverified.
- **Source:** [EV-0090], [EV-0091], [EV-0053], [EV-0056].
- **Current legacy assessment:** the “confirmed” labels are historical status text and are not supported as a reproduced exploit by the available report set. Preserve the disagreement; do not upgrade the candidate.
- **Discriminant:** on a verified target, test both ingredient orders, capture dynamic ENIT/EFIT, then record the exact ordinary follower/frenzy delivery and raw resistance/effect/skill deltas against controls.

## C-LEG-0010 — Speech “confirmed” label versus unlogged user observation

- **Model A:** the source root state calls Speech success without skill XP a confirmed exploit.
- **Model B:** the detailed Speech report describes an unlogged user observation after temporary Speech removal, with no save, form, timing, or raw AVSK delta.
- **Source:** [EV-0092], [EV-0068], [EV-0069].
- **Current legacy assessment:** static selection/result ordering supplies a plausible mechanism, but the source does not preserve an instrumented reproduction. The root status label is not runtime proof.
- **Discriminant:** repeat one specified dialogue family on a verified target while recording the selected INFO, effective Speech at selection and result, raw AVSK before/after, and source-effect lifecycle.
