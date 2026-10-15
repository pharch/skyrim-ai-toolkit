---
name: esp-record-research
description: Trace Skyrim AE quest gates, combat XP entry points, perks, effects, and record overrides from installed plugins without modifying them.
---

# ESP and record research

> Startup: read [the local runtime contract](../../../docs/LOCAL_RUNTIME_CONTRACT.md) and [current readiness](../../../docs/HARNESS_READINESS.md). Bootstrap with `python3 scripts/bootstrap_python.py` (Linux/WSL) or `py -3.12 scripts/bootstrap_python.py` (Windows), then use the strict dispatcher (`python3` or `py -3.12`, respectively). If a preflight fails, rerun bootstrap and strict validation before declaring an external blocker. A blocked capability cannot support a negative finding.

Use this workflow when a hypothesis depends on a plugin record, condition,
script attachment, or effective override.

1. State a falsifiable claim, target build, relevant records, and the
   observation that would disprove it. EditorIDs and wiki descriptions are
   search aids, not proof of runtime behavior.
2. Resolve the complete active AE order for the target before a profile winner
   or negative claim. Require an explicit `plugins.txt` when that target is
   MO2-managed. Vanilla official-master inspection does not require MO2.
3. Run `python3 scripts/python_env.py run tools/plugin_reader.py doctor`, then
   query a named file with
   `python3 scripts/python_env.py run tools/plugin_reader.py record <plugin>
   --signature QUST --form-id <id> --include-subrecords`. The reader returns
   file-level fields and raw CTDA/ALST/ALID/VMAD values. It does not load the
   active order or decode every subrecord semantically.
4. The tested `resolve_record_winner(candidates, active_order)` helper selects
   the last matching candidate only when given a complete validated order; its
   current test is synthetic. File-level reads are not xEdit winner output.
5. For native xEdit fields in the five official masters, run
   `python3 scripts/python_env.py run tools/xedit_bridge.py native-query
   --signature QUST --plugin Skyrim.esm --editor-id
   dunDA14MorvunskarQST`. The wrapper verifies the executable ProductVersion,
   uses an official-master-only `.local` Data view, launches the configured
   SSEView through the recovered original helper, and returns structured
   native field values plus the exact loaded-file inventory. This route does
   not require MO2 and reports winners only within the five-master scope.
6. For native code, query the existing GOG project through
   `python3 scripts/python_env.py run tools/ghidra_probe.py [--rva 0x...]`.
   Resolve named relocations with
   `python3 scripts/python_env.py run tools/address_library_probe.py --symbol
   Namespace::Name`. Keep GOG build identity separate from runtime and never
   transfer its addresses to another build. Static work remains possible when
   the active plugin profile is missing.
7. For quests, follow the initiation path across QUST, INFO, story-manager
   nodes, aliases, scripts, and conditions. Distinguish quest start, journal
   display, stage completion, alias fill, and encounter spawn.
8. For armor XP, separate candidate perks/conditions/effects from armor rating
   and hit registration. A record observation does not establish native award
   logic.
9. Record plugin filename/hash, runtime/build, exact record, output hash,
   coverage, and EV ID. Empty searches against an incomplete order are not
   negative evidence. Keep raw game files outside Git and never save plugin
   changes.

## Failure modes

Parser errors, missing records, incomplete orders, and absent overrides are
coverage limits. The tracked tools/xedit_bridge.py doctor/prepare route is
documented in docs/LOCAL_RUNTIME_CONTRACT.md. Its file-records command is a
direct TES4 parser and is not an xEdit query. The cold-start prepared an
isolated view and completed a native Apply Script QUST export (EV-0207). The
five-master view does not establish an active-profile winner. For winner or
negative research against a profile, require its complete actual order and a
passing `python3 scripts/python_env.py run tools/ae_preflight.py`; when MO2
manages it, use that selected profile's explicit `plugins.txt`.
