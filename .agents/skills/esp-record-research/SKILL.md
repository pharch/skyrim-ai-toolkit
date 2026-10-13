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
2. Resolve the complete active load order for the exact edition/profile before
   drawing a conclusion. For MO2, use the profile's virtualized view; never treat a
   stale SSE `plugins.txt` as the VR order.
3. Inspect the winning record and full override chain with xEdit/xelib or the
   applicable record tool. Capture plugin names, FormIDs, winning values, relevant
   conditions, and the tool/version used.
4. For quests, follow the actual initiation path across QUST, dialogue INFO,
   story-manager nodes, aliases, scripts, and attached conditions. Distinguish
   quest start from journal display, stage completion, alias fill, and encounter
   spawn.
5. For armor XP, trace candidate perks/conditions/effects separately from armor
   rating and hit registration. A record-level observation does not establish the
   native award path.
6. Preserve raw record output and an independently reproducible query. Record
   empty searches with the load-order identity and coverage; an empty result from
   an incomplete load is not negative evidence.
7. Do not save changes to plugins. Use copied fixtures for serializer round trips;
   this skill is for read-only evidence collection.
