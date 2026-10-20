# Protocol

1. Preserve H1/H2 and their predicted discriminants before querying new DA06 source records.
2. Verify the retained UESP local corpus identity and retrieve `Skyrim:The_Cursed_Tribe` with revision 3597866. Use its page text only to identify actors, locations, and claimed ordinary route steps; preserve the revision URL and response hash.
3. Through the strict dispatcher, query Skyrim.esm SMQN `000A0E73`, GLOB `000A0E71`, child QUST `0003B681`, and all directly linked DA06 QUST/helper/alias/scene/actor/reference records. Confirm the serialized threshold and whether the child is main DA06 in the exact prepared file.
4. Follow DA06 QUST start flags, event field, alias definitions, stage-to-fragment map, attached scripts, NPC bases, placed references, packages/scenes, and any native or quest callbacks represented in official records.
5. Join the full Skyrim.esm DIAL/INFO group context for DA06-owned topics, decode relevant conditions, and extract/disassemble only bound scripts through the supported Skyrim - Misc.bsa route. Treat failed or unsupported archive extraction as a scoped limit.
6. Search every parsed record/subrecord in the five prepared official masters for direct references to main DA06 and any identified helper/alias actor or trigger FormIDs. Interpret hits by signature and script evidence; do not infer runtime reachability from raw references.
7. Keep official source-file evidence separate from active-profile winners. The later runtime discriminator requires verified Steam 1.6.1170.0, a complete disposable profile order, clean level-one and level-nine saves, numeric level and quest-state observation, ordinary no-trigger controls, and no console/stage/script intervention.
