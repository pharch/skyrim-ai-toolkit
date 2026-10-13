---
name: ae-target-verification
description: Verify the exact Skyrim AE executable, runtime, active load order, and compatible evidence before interpreting any record or runtime result.
---

# Skyrim AE target verification

This repository targets Skyrim Anniversary Edition runtime 1.6.318 or newer.
Research and runtime claims must be tied to the exact verified executable and
active profile. Do not use this workflow to compare other editions.

1. Run `node tools/ae-preflight.js` on Windows. It reads `SkyrimSE.exe`'s
   ProductVersion from the executable metadata, verifies the AE runtime range,
   hashes the executable, and validates the configured active plugin list.
   `SKYRIM_EDITION=AE` is a required scope declaration, not a substitute for
   executable inspection.
2. Set `GAME_ROOT` to the verified installation and `PLUGINS_TXT` to the
   active AE list. For MO2, select the exact AE profile's virtualized
   `plugins.txt`; never choose a global or stale list by filename alone.
3. Record executable hash/runtime, SKSE build, load-order path/hash, profile,
   and all instrumentation with every observation. Unknown metadata keeps the
   claim `edition-unverified`.
4. xEditLib uses `GM_SSE` for AE's record format but does not itself establish
   that the target is AE. The target guard must pass before it is initialized.
5. Stop on an unsupported runtime, missing executable, empty/incomplete order,
   or identity mismatch. Do not fall back to another game folder or trust a
   typed version string.
6. Linux tests can exercise parsers and policy with fixtures. Only Windows can
   verify the real PE version resource, xEditLib DLL/registry behavior, and MO2
   virtualized load order; only a controlled game test can verify live behavior.
