# Results

## Bounded private lead screen

Fifteen summary-only queries covered armor skill XP, zero armor XP, Heavy/Light Armor XP, armor experience, zero/negative armor rating, negative Damage Resist, Marked for Death, and related wording. Twenty focused message neighborhoods were captured privately; the export doctor reported 60,873 indexed messages and source SHA-256 `f2462adbb2b4c76e53fe5a0019215a8f5fee9b8ee6f455b4e785aafcc1143698`. Exact private pointers and raw hashes are in EV-0283's ignored provenance note.

The relevant untrusted reports describe negative armor at level one as increasing hit-earned armor XP and a positive-base Heavy Armor piece at displayed rating zero as still awarding XP on hit. Another message attributes the result to base armor rating and enemy damage. These reports have no verified target build, numeric AVSK delta, raw `UseSkill` points, or matched protection control. Other retrieved zero-rating and Dragonhide/transformation discussions do not report the required armor XP and protection measurements.

## AE source comparison

The GOG AE 1.6.1179.0 hit-resolution trace scans worn ARMO entries for positive base rating before selecting AV11/12; the receiver's points argument is a separate value and passes through a positive-points guard ([EV-0221], [EV-0222]). This is consistent with the report that changing displayed/effective rating alone does not clear armor XP eligibility. It is not installed Steam 1.6.1170.0 evidence, a live test, or proof of the points amount/protection result.

## Outcome

The targeted export screen produced no lead meeting the bounty criteria: a natural level-one setup, qualifying hits, numeric zero Heavy and Light Armor XP, and measured retained protection. The specific “overflow armor rating to zero” idea is a negative lead, not a candidate. H2 is supported by the scoped GOG source trace and the untrusted report; H1 is not supported in that scope. H3 remains open. No Steam runtime test, profile winner, raw AVSK measurement, or vanilla reproduction was obtained.
