---
name: ae-target-verification
description: Verify the exact Skyrim AE executable, runtime, active load order, and compatible evidence before interpreting any record or runtime result.
---

# Skyrim AE target verification

> Startup: read [the local runtime contract](../../../docs/LOCAL_RUNTIME_CONTRACT.md) and [current readiness](../../../docs/HARNESS_READINESS.md). Bootstrap with `python3 scripts/bootstrap_python.py` (Linux/WSL) or `py -3.12 scripts/bootstrap_python.py` (Windows), then use the strict dispatcher (`python3` or `py -3.12`, respectively). If a preflight fails, rerun bootstrap and strict validation before declaring an external blocker. A blocked capability cannot support a negative finding.

This repository targets Skyrim Anniversary Edition runtime 1.6.318 or newer.
Research and runtime claims must be tied to the exact verified executable and
active profile. Do not use this workflow to compare other editions.

1. Run the host bootstrap from `docs/LOCAL_RUNTIME_CONTRACT.md`, then run
   `python3 scripts/python_env.py run tools/ae_preflight.py` (Windows PowerShell
   uses `py -3.12` to start the dispatcher). If bootstrap or strict preflight
   fails, repair and recheck before handing off an environment blocker. The
   gate reads executable ProductVersion, verifies AE 1.6.318+, hashes the
   binary, and validates the configured full order. `--probe-executable` is
   diagnostic only. `SKYRIM_EDITION=AE` is not executable evidence.
2. Set `GAME_ROOT`, `MO2_PROFILE_DIR`, and `PLUGINS_TXT` for the exact selected
   profile. Its explicit `plugins.txt` must belong to that profile; never use
   a global or stale list. Use `--scoped-five-master` only for isolated view
   preparation and `--test-profile` only for the separately designated
   disposable profile.
3. Record executable hash/runtime, SKSE build, load-order path/hash, profile,
   and all instrumentation with every observation. Unknown metadata keeps the
   claim `edition-unverified`.
4. xEditLib uses `GM_SSE` for AE's record format but does not itself establish
   that the target is AE. The target guard must pass before it is initialized.
5. Stop on an unsupported runtime, missing executable, empty/incomplete order,
   or identity mismatch. Do not fall back to another game folder or trust a
   typed version string.
6. The Python PE-resource reader can verify the real executable ProductVersion
   on Linux/WSL as well as Windows. Windows is still required to verify native
   xEditLib DLL/registry behavior and MO2 virtualized load order; only a
   controlled game test can verify live behavior.
