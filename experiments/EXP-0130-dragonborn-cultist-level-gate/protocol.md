# Protocol

## Competing models

- **H1:** The level-25 condition belongs to the separate world-encounter route `DLC2WE09`; `DLC2CultistAmbush` is a main-quest-stage route after The Way of the Voice and has no player-level predicate.
- **H2:** The two UESP labels conceal a shared or additional level condition; the main-quest ambush also requires a player-level threshold, or it joins the level-gated route before quest startup.
- **H3 (falsified as an identity model):** `DLC2WE09` is an event/node/script identity attached to the same `DLC2CultistAmbush` QUST. Native records instead show separate CLOC and SCPT Story Manager branches selecting distinct QUSTs [EV-0656], [EV-0658], [EV-0664]. Shared stage-10 handoff PSC does not erase that identity distinction [EV-0663].
- **H4 (supported, bounded cross-build inference):** `DLC2WE09`'s `GetLevel >=25` row and Solstheim location row form a trailing OR group after earlier chance/stage conditions. Raw CTDA bits and pinned schema establish `>=` and OR flags [EV-0657], [EV-0665], [EV-0666]; the identity-checked GOG evaluator groups consecutive OR rows [EV-0667], [EV-0668]. This does not establish Steam behavior, evaluation timing, or a natural level-one start [EV-0669], [EV-0260].

## Discriminants

1. Inspect the exact official-master `QUST` records for `DLC2CultistAmbush` and `DLC2MQ01`, then locate whether `DLC2WE09` names a quest, story-manager node, script, or only related data. Include start flags, aliases, objectives, and condition functions.
2. Trace the story-manager/dialogue/script writers and level conditions for each path. Distinguish quest startup from actor spawn and journal state; use separate QUST and Story Manager identities, preserving the shared but non-identifying stage handoff evidence [EV-0654], [EV-0656], [EV-0658], [EV-0663], [EV-0664].
3. Keep the exact five-master source scope separate from a profile-specific winner. Do not transfer GOG RVAs to Steam.
4. Interpret `DLC2WE09`'s raw condition operators with build-identified code. The GOG static evaluator supports a location alternative after the earlier chance/stage conditions, but do not transfer its RVA or assert a Steam/runtime start result [EV-0665]–[EV-0669]. A documented route is not a newly discovered glitch.
5. Preserve the clean level-one trigger test as a separate Steam experiment under EV-0260. It requires the full active order, disposable level-one save, read-only observation of the actual QUST transition, an appropriate higher-level/control path, and repetition. Do not use console, Papyrus forcing, altered plugins, or modified saves as positive proof.

## Sources

- Local UESP pages, revision-pinned in `.local/uesp/q81/` [EV-0653].
- Exact official Skyrim AE masters through the read-only plugin/xEdit routes.
- Installed Papyrus source and GOG Ghidra only after executable identity and source scope are verified.
