# EXP-0021 results

## Static observations

- EV-0268 confirms four player-trigger references inside DawnstarSilussHouse, each calling DA07MuseumScenes.SetStage at an artifact-specific stage, with no identified player-level predicate in the trigger script.
- SCEN `00096FDB` has raw FNAM `0x15`; the cited TES5Edit schema maps bit 0 to Begin on Quest Start. Its begin fragment starts the tapestries scene; its completion fragment calls DA07intro.SetStage(200) and DA07.SetStage(5).
- The scene has a HasLoaded3D condition. DA07MuseumScenes' Silus alias lacks the schema's Allow Disabled bit while Silus's sole placed ACHR is initially disabled. The raw condition run-on and exact alias/scene runtime behavior remain unresolved.
- The interior door REFR 000240CA XLOC schema decode says level 255 (Requires Key) and KEYM 000960F0 DA07SilussHouseKey. The only placed QAKeyContainer reference found is in QASmoke; dynamic key writers/acquisition remain outside this bounded scan.
- The four trigger boxes' record centers are 277.28–671.21 coordinate units from the interior door reference. This prioritizes the entry region for a collision-aware movement study but does not prove any trigger can be reached by walking or clipping.
- The available archive route extracts classic PEX streams from Skyrim - Misc.bsa, not NIF collision meshes. No general BSA/NIF reader was found in the WSL toolset, and a native xEdit SCEN query failed before SSEView with the WSL socket interop error. Neither limitation is a gameplay negative.

## Runtime status

No clean level-one save, selected complete profile order, deployed read-only observer, clip sequence, trigger activation, quest transition, or scene result was observed. H1/H2/H3 remain open. EV-0260 records the live prerequisites that are currently absent.

## Next discriminant

First acquire a tested read-only BSA/NIF collision route or a native Windows inspection session to determine whether any plausible player-only clip can cross the keyed boundary; do not infer traversal from the recorded box centers. Then run the control and candidate sequence in [protocol.md](protocol.md) only after exact target, full active order, disposable level-one save, and observer prerequisites are available. Preserve the physical sequence and record quest, alias, scene, and numeric-level state separately.

## Cross-domain assessment

No causal edge links this DA07 trigger/scene path to OBJ-2 HitData, armor mitigation, or armor/Block XP mechanisms M-0017/M-0018.
