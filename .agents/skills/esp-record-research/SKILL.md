---
name: esp-record-research
description: Trace Skyrim quest gates, combat XP entry points, perks, magic effects, and record overrides from game plugins without modifying them.
---

# ESP and record research

Use this workflow when a hypothesis depends on a plugin record, condition, script
attachment, or effective override.

1. State the falsifiable claim, target game edition/build, relevant records, and the
   observation that would disprove it. Treat EditorIDs and wiki descriptions as
   search aids, not proof of runtime behavior.
2. Resolve the complete active AE load order for the exact profile before
   drawing a conclusion. For MO2, use the selected profile's active
   `plugins.txt`; a file from another profile is not a substitute.
3. Use `python3 scripts/python_env.py run tools/plugin_reader.py doctor` to
   verify the local parser, then query an exact plugin with
   `python3 scripts/python_env.py run tools/plugin_reader.py record <plugin>
   --signature QUST --form-id <local-id>`. The Python reader exposes record
   fields without third-party libraries. It does not resolve winning records
   across the active order; do not claim a winner or complete override chain
   until Windows SSEEdit has passed the exact target/profile gate.
4. For quests, follow the actual initiation path across QUST, dialogue INFO,
   story-manager nodes, aliases, scripts, and attached conditions. Distinguish
   quest start from journal display, stage completion, alias fill, and encounter
   spawn.
5. For armor XP, trace candidate perks/conditions/effects separately from armor
   rating and hit registration. A record-level observation does not establish the
   native award path.
6. Summarize useful fields and query provenance in the experiment's Markdown
   result or evidence database. Keep raw plugin files in local game storage;
   never copy them into the repository. Record
   empty searches with the load-order identity and coverage; an empty result from
   an incomplete load is not negative evidence.
7. Do not save changes to plugins. Use copied fixtures for serializer round trips;
   this skill is for read-only evidence collection.
