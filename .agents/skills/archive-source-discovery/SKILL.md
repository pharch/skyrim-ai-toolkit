---
name: archive-source-discovery
description: Locate and extract vanilla plugin, script, or other research inputs from BSA/BA2 archives while preserving provenance and avoiding writes.
---

# BSA/BA2 source discovery

1. Identify the exact game/archive edition and hash the archive. Record its source
   path privately; never modify or replace the original.
2. Start with `archive info`, `archive list`, or `archive validate` in the existing
   AutoMod wrapper, if installed. Always request JSON output and retain raw output.
3. Search the listing for the smallest relevant source set: plugin masters,
   scripts, records or assets needed to answer the stated research question.
   Preserve the archive-relative path and archive identity for each extracted file.
4. Extract only to an explicit scratch directory outside the game installation.
   Before extraction, confirm the output path is a new research scratch location;
   do not extract over `Data/` or any mod-manager directory.
5. Check whether a loose file overrides the archive entry before claiming what the
   game loads. For record conclusions, inspect the complete active load order and
   winner, not just the base archive.
6. Treat parser errors, empty listings, and missing tools as unknown coverage.
   Record tool version, exit code, archive hash, and a known-present control when
   available.
7. Do not use archive create/add/remove/replace/merge/optimize commands in this
   research workflow.
