---
name: archive-source-discovery
description: Locate and extract Skyrim AE vanilla plugin, script, or other research inputs from BSA archives while preserving provenance and avoiding writes.
---

# Skyrim AE BSA source discovery

Use this only for Skyrim AE `.bsa` research inputs. BA2 and other game-edition
archive workflows are outside this harness.

1. Verify AE runtime and identify the exact archive source. Record its filename,
   size, SHA-256, archive version if available, and private source path; never
   modify or replace the original.
2. Run `python3 scripts/python_env.py run tools/domain_doctor.py` to record the
   available archive/toolchain status. This checkout has no active Python BSA
   parser; do not call retired shell/Node wrappers or claim archive coverage.
   Treat archive inspection as `AWAITING_TOOL_ACCESS` until a reviewed
   Python-only reader is installed and tested.
3. Search for the smallest relevant plugin/script set. Preserve archive-relative
   paths and map every extracted file to the archive hash and tool command.
4. Do not extract or mutate an archive in this harness. If an authorized offline source requires extraction, use a separately
   reviewed tool/procedure that verifies a new scratch destination outside the
   game, active profile, and original source before writing.
5. Check for loose-file overrides and inspect the complete AE active load order
   before claiming which data the game uses.
6. Do not use archive create, extract, add, remove, update, replace, merge, or
   optimize operations through this harness. Preserve raw listings and negative
   search results.
