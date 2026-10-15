---
name: skyrim-quest-gate-research
description: Investigate Skyrim AE quest, encounter, and event level gates and design reproducible level-one bypass tests.
---

# Skyrim AE quest/event gate research

> Startup: read [the local runtime contract](../../../docs/LOCAL_RUNTIME_CONTRACT.md) and [current readiness](../../../docs/HARNESS_READINESS.md). Bootstrap with `python3 scripts/bootstrap_python.py` (Linux/WSL) or `py -3.12 scripts/bootstrap_python.py` (Windows), then use the strict dispatcher (`python3` or `py -3.12`, respectively). If a preflight fails, rerun bootstrap and strict validation before declaring an external blocker. A blocked capability cannot support a negative finding.

1. Choose a precisely identified quest, encounter, or event with a plausible
   level prerequisite; ground the lead in UESP and game data.
2. Distinguish quest startup, journal display, dialogue availability, alias
   fill, story-manager event, and actual encounter spawn.
3. Enumerate entry points and conditions across QUST, story-manager records,
   INFO branches, aliases, scripts, and native callbacks.
4. Identify when the player-level predicate is read and whether the value is
   cached, reevaluated, or bypassed through another vanilla entry source.
   Never invent native offsets.
5. State rival causal models and the predicted observation that would
   discriminate them. Use diagnostic intervention only in a separate lane;
   console `setstage`/`startquest` is not a vanilla reproduction.
6. For native code, use the existing GOG project via
   `python3 scripts/python_env.py run tools/ghidra_probe.py [--rva 0x...]`.
   Resolve named CommonLib symbols with
   `python3 scripts/python_env.py run tools/address_library_probe.py --symbol
   Namespace::Name`. Keep GOG binary evidence distinct from the runtime build.
7. For a native vanilla QUST field query, use
   `python3 scripts/python_env.py run tools/xedit_bridge.py native-query
   --signature QUST --plugin Skyrim.esm --editor-id <exact-editor-id>`. The
   wrapper verifies ProductVersion, loads only the five official masters, and
   does not require MO2. Before a profile-specific winner/negative claim or
   live-game access, run
   `python3 scripts/python_env.py run tools/ae_preflight.py` and query exact file
   records with
   `python3 scripts/python_env.py run tools/plugin_reader.py record <plugin>
   --signature QUST --form-id <id> --include-subrecords`. Record queries do
   not establish the profile's winning override without its complete active
   order. If MO2 manages that order, use its selected profile's explicit
   `plugins.txt`.
8. Preserve page revision, executable/plugin hashes, raw record bytes,
   transition coverage, and EV IDs. If the active profile is absent, keep
   winner/runtime claims blocked and continue static GOG or other independent
   offline work.

## Failure modes

A wiki prerequisite or level condition does not prove the quest initiation
transition. Missing aliases, conditions, scripts, story-manager edges, or
native callbacks leave the gate unresolved. An empty result from an incomplete
order is not negative evidence. Linux tests do not establish Windows xEdit,
MO2, or in-game behavior.
