# Protocol

1. Preserve EV-0300's exact level-gate mapping and retrieve the local UESP revision-specific page only as a gameplay lead.
2. Verify the strict Python route and use `tools/xedit_bridge.py file-records` or `tools/plugin_reader.py record` against one explicit official source file. These direct-parser queries do not establish an active-order winner.
3. Query the exact SMQN, threshold GLOB, helper QUST, and main DA08 QUST with full subrecords. Resolve child QUST IDs in Skyrim.esm source context.
4. Inspect main/helper start flags, aliases, stage transitions, attached scripts, dialogue topics/INFO conditions, scenes, and any serialized references that can call `Start`/`SetStage` or change aliases.
5. Classify journal display, dialogue availability, quest startup, alias fill, and actual encounter access separately. Keep unresolved BSA scripts, dynamic/native callers, profile overrides, physical access, and live behavior explicit.
6. If an independent route is supported, write a level-one positive/negative test sequence without console, script, plugin, external state edit, or level change. Do not call it a reproduction until observed and repeated in a disposable save.
