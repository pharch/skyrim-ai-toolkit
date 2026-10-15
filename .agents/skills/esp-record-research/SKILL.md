---
name: esp-record-research
description: Trace Skyrim AE quest gates, combat XP entry points, perks, effects, and record overrides from installed plugins without modifying them.
---

# ESP and record research

Use this workflow when a hypothesis depends on a plugin record, condition,
script attachment, or effective override.

1. State a falsifiable claim, target build, relevant records, and the
   observation that would disprove it. EditorIDs and wiki descriptions are
   search aids, not proof of runtime behavior.
2. Resolve the complete active AE order for the selected profile before a
   winner or negative claim. For MO2, require that profile's explicit
   `plugins.txt`.
3. Run `python3 scripts/python_env.py run tools/plugin_reader.py doctor`, then
   query a named file with
   `python3 scripts/python_env.py run tools/plugin_reader.py record <plugin>
   --signature QUST --form-id <id> --include-subrecords`. The reader returns
   file-level fields and raw CTDA/ALST/ALID/VMAD values. It does not load the
   active order or decode every subrecord semantically.
4. The tested `resolve_record_winner(candidates, active_order)` helper selects
   the last matching candidate only when given a complete validated order; its
   current test is synthetic. File-level reads are not xEdit winner output.
5. For native code, query the existing GOG project through
   `python3 scripts/python_env.py run tools/ghidra_probe.py [--rva 0x...]`.
   Resolve named relocations with
   `python3 scripts/python_env.py run tools/address_library_probe.py --symbol
   Namespace::Name`. Keep GOG build identity separate from runtime and never
   transfer its addresses to another build. Static work remains possible when
   the active plugin profile is missing.
6. For quests, follow the initiation path across QUST, INFO, story-manager
   nodes, aliases, scripts, and conditions. Distinguish quest start, journal
   display, stage completion, alias fill, and encounter spawn.
7. For armor XP, separate candidate perks/conditions/effects from armor rating
   and hit registration. A record observation does not establish native award
   logic.
8. Record plugin filename/hash, runtime/build, exact record, output hash,
   coverage, and EV ID. Empty searches against an incomplete order are not
   negative evidence. Keep raw game files outside Git and never save plugin
   changes.

## Failure modes

Parser errors, missing records, incomplete orders, and absent overrides are
coverage limits. The authoritative `skyrim` bridge's exact xEdit config and helper files were
replayed from an isolated copy; all five relevant settings match, and its
`doctor`, `prepare-xedit`, and scoped five-master preflight pass (EV-0191). The
approved generated `-view` session loaded the five official masters
(EV-0184–0185/0189), but this list is not the active MO2 order and no record
was queried/exported. For winner research, require the selected profile's
complete explicit `plugins.txt` and a passing
`python3 scripts/python_env.py run tools/ae_preflight.py`; keep winner and
profile-dependent negative findings blocked until then. Linux record tests do
not establish Windows xEdit or MO2 behavior.
