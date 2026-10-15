---
name: ae-target-verification
description: Verify the exact Skyrim AE executable, runtime, active load order, and compatible evidence before interpreting any record or runtime result.
---

# Skyrim AE target verification

> Startup: read [the local runtime contract](../../../docs/LOCAL_RUNTIME_CONTRACT.md) and [current readiness](../../../docs/HARNESS_READINESS.md). Bootstrap with `python3 scripts/bootstrap_python.py` (Linux/WSL) or `py -3.12 scripts/bootstrap_python.py` (Windows), then use the strict dispatcher (`python3` or `py -3.12`, respectively). If a preflight fails, rerun bootstrap and strict validation before declaring an external blocker. A blocked capability cannot support a negative finding.

This repository targets Skyrim Anniversary Edition runtime 1.6.318 or newer.
Research and runtime claims must be tied to the exact verified executable.
Profile-specific record and runtime claims also require the target's complete
active order. Do not use this workflow to compare other editions.

1. Run the host bootstrap from `docs/LOCAL_RUNTIME_CONTRACT.md`, then use the
   strict dispatcher (`python3` on Linux/WSL; `py -3.12` on Windows). If
   bootstrap or preflight fails, repair and recheck before handing off an
   environment blocker. `--probe-executable` reads ProductVersion/hash only;
   it is diagnostic and does not pass an xEdit or live gate.
2. For native vanilla records, use
   `python3 scripts/python_env.py run tools/xedit_bridge.py native-query
   --signature QUST --plugin Skyrim.esm --editor-id <exact-editor-id>`. That
   route verifies the configured executable and the exact isolated five
   official masters using `--scoped-five-master`; no MO2 profile is required.
   For profile-specific winners, negative findings, or live-game access, run
   `python3 scripts/python_env.py run tools/ae_preflight.py` against the actual
   complete target order. Set `MO2_PROFILE_DIR` and its explicit `PLUGINS_TXT`
   only when that target order is managed by MO2. Never use a global or stale
   list. Use `--test-profile` only for the separately designated disposable
   profile.
3. Record executable hash/runtime, SKSE build, load-order path/hash, profile,
   and all instrumentation with every observation. Unknown metadata keeps the
   claim `edition-unverified`.
4. xEditLib uses `GM_SSE` for AE's record format but does not itself establish
   that the target is AE. The target guard must pass before it is initialized.
5. Stop on an unsupported runtime, missing executable, wrong scoped list, or
   identity mismatch. An empty/incomplete full order blocks profile-specific
   winner/negative and live findings, but it does not block the isolated
   official-master xEdit route. Do not fall back to another game folder or
   trust a typed version string.
6. The Python PE-resource reader can verify real executable ProductVersion on
   Linux/WSL as well as Windows. A real WSL-to-Windows native xEdit operation
   is evidence only when it launches SSEView and records its loaded-file list
   and native output. MO2 virtualized order behavior still requires checking
   the selected profile; only a controlled game test verifies live behavior.
