# Results

## Observed

- The captured Dawnguard Drain Vitality-labelled SHOU records reuse the three Skyrim MFD word FormIDs, but link to Dawnguard-specific Drain Vitality SPELs.
- Those custom SPELs reference Health, Magicka, Stamina, Script-archetype, and stagger MGEFs. Their decoded Value Modifier primary ActorValues are AV24, AV25, and AV26; the Script effect has no primary AV and was not traced.
- None of the three captured custom SPEL EFID lists contains MFD AV39 MGEF `0010319D`.
- EV-0241 separately identifies base MFD spell tiers in the WICast list. The custom Drain Vitality SPELs were not shown to be entries in that list.

## Assessment and limits

The records support a label/word versus effect-payload mismatch for this bounded Dawnguard path. They do not establish a player-targeted MFD AV39 effect through these custom SPELs. The untrusted lead's acquisition behavior, target mode, Script-archetype behavior, active-profile winner, WICast runtime event, and raw AV39 delta remain unresolved. No live test, vanilla reproduction, armor protection, or armor-XP effect was observed. Direct parser captures are not native xEdit exports and do not resolve profile-specific overrides.

See EV-0273 for revisions, source limits, file hashes, and cross-references.
