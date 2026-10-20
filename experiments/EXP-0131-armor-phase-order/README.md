# Armor protection to skill-award phase order

This experiment tests whether a player-accessible equipment transition can occur after incoming-hit armor mitigation but before the worn-armor scan that selects Heavy/Light Armor skill XP. It was opened from Q-0082 after earlier records established that the HitData builder and the receiver-side award selector are distinct functions [EV-0222], [EV-0261].

The offline GOG AE 1.6.1179.0 trace places AV39/armor-factor mitigation before the receiver award branch. The normal unblocked player-receiver path scans worn ARMO and selects AV11/AV12 synchronously inside `FUN_1406bcaa0`; `FUN_1406b9df0` is a later, separate health/trap continuation [EV-0670], [EV-0673]. The builder invokes selector visitors synchronously. In the five official masters, matching selector 37/39 PERK rows use EPFT function IDs 1/2, which the bounded GOG dispatch resolves to numeric SetValue/AddValue operations [EV-0671], [EV-0672], [EV-0675], [EV-0676].

This narrows the captured vanilla source path against a synchronous equipment-interposition model. It does not prove a live protection value, raw AVSK delta, Steam call-path equivalence, profile winner, or absence of side effects in unresolved typed virtual predicates. A blocked hit's AV9 route remains a separate diagnostic branch; it is not counted as a qualifying bypass without positive armor-caused protection and matched XP measurements [EV-0260].

Raw Ghidra outputs, metadata, and the official-master screen remain below ignored `.local/`. This experiment directory contains the reproducible question, method, and evidence-bounded result.
