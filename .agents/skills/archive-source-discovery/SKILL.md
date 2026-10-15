---
name: archive-source-discovery
description: Locate and extract Skyrim AE vanilla plugin, script, or other research inputs from BSA archives while preserving provenance and avoiding writes.
---

# Skyrim AE BSA source discovery

> Startup: read [the local runtime contract](../../../docs/LOCAL_RUNTIME_CONTRACT.md) and [current readiness](../../../docs/HARNESS_READINESS.md). Bootstrap with `python3 scripts/bootstrap_python.py` (Linux/WSL) or `py -3.12 scripts/bootstrap_python.py` (Windows), then use the strict dispatcher (`python3` or `py -3.12`, respectively). If a preflight fails, rerun bootstrap and strict validation before declaring an external blocker. A blocked capability cannot support a negative finding.

Use this only for Skyrim AE `.bsa` research inputs. BA2 and other game-edition
archive workflows are outside this harness.

1. Verify AE runtime and identify the exact archive source. Record its filename,
   size, SHA-256, archive version if available, and private source path; never
   modify or replace the original.
2. Run `python3 scripts/python_env.py run tools/domain_doctor.py` to record the
   available archive/toolchain status. For the tested classic PEX stream in
   `Skyrim - Misc.bsa`, use `python3 scripts/python_env.py run
   tools/papyrus_pex.py extract <script>`; it reads configured `SKYRIM_DATA`,
   validates the PEX source header, and writes only under ignored `.local/`.
   This is a narrow uncompressed-stream extractor, not a general BSA parser.
3. Inspect the extracted artifact with `python3 scripts/python_env.py run
   tools/papyrus_pex.py disassemble <pex>`. It supports bounded classic PEX 3.2
   forms and is not a complete decompiler. EV-0121/0122 record the actual
   DA14Script extraction, BSA/PEX hashes, output, and limitations.
4. Preserve archive-relative source identity, size, SHA-256, exact extraction
   command, output SHA-256, and raw results. Never write to the game, active
   profile, original archive, or a path outside ignored `.local/`.
5. Check for loose-file overrides and inspect the complete AE active load order
   before claiming which data the game uses.
6. `scan-literals` scans only the base Misc BSA by default; its Creation Club
   option traverses all installed `cc*.bsa` archives and can read several GB.
   Preserve exact archive coverage. A no-hit literal scan does not exclude
   dynamically built strings or native writers (EV-0123).
