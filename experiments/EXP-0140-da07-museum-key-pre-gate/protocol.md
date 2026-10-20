# Protocol

1. Verify the installed Steam AE executable identity before interpreting source/runtime compatibility; do not transfer GOG RVAs.
2. Preserve the UESP lead with page title, revision, timestamp, URL and exact lines saying the key is carried by Silus and the house is inaccessible until level 20. Treat both as secondary and time-ambiguous.
3. Read exact Skyrim.esm records for KEYM `000960F0`, NPC_ `000240CC`, ACHR `000240CE`, keyed door REFR `000240CA`, and relevant DA07 quest/alias/scene records. Screen all five official masters for references to the key and Silus, resolving direct inventory, leveled-list, VMAD and enable-parent links where the parser exposes them.
4. Inspect only attached PEX sources extractable through the tested `Skyrim - Misc.bsa` route. Do not pass Dawnguard or mesh archives to the PEX helper, infer absence from an unscanned archive, or write to original game files.
5. Compare the key source path to DA07's level-20 Story Manager route and Silus's initially-disabled placement. Keep source findings separate from inventory state and player access.
6. If a plausible route survives, defer the candidate/control to a clean verified Steam AE level-one save, exact full active order, and read-only observer. Record Silus presence, pickpocket inventory, door state, trigger crossing, DA07MuseumScenes state, downstream scene/stage completion, and numeric level. Do not use console, injected scripts, edited plugins, moved actors, or modified saves as vanilla proof. EV-0260 lists the missing live prerequisites.
