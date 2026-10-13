# Tool registry and operating limits

This folder stores the retained read-only and Windows-only tooling needed for a Codex-first Skyrim AE research checkout.

## Scripts and wrappers
- `ae-preflight.js` — read the Windows ProductVersion of `SkyrimSE.exe`, enforce 1.6.318+, and validate the active `plugins.txt`.
- `ae-target.js` — AE-only target resolution and fail-closed validation logic.
- `automod-cli.sh` — archive inspection and JSON validation; extraction and archive mutation remain disabled.
- `cosave-cli.sh` and `cosave-info.py` — read-only co-save container inspection.
- `crash-triage.py` — crash and log triage with preserved denominators.
- `devbench-cli.sh` — optional Windows DevBench connectivity check only; no mutating live session is enabled.
- `papyrus-triage.py` — Papyrus log summary and coverage counts.
- `resaver-cli.sh` and `resaver-resolve-names.js` — read-only save inspection and name resolution.
- `skyrim-winner.js` and `skyrim-winner.sh` — record winner/override resolution when a verified active AE order is available.
- `xelib/active-plugins.js` — parse and validate the active plugins list against the AE master set.

## Platform boundary
Linux validation can exercise the repo logic, schemas, fixtures, and safety checks. It cannot validate the real Windows PE metadata, MO2 profile, xEditLib registry, DevBench, or in-game AE state. Treat those as separate Windows-only verification steps.

## Safety rules
- Do not write to game files, saves, co-saves, or plugins.
- Do not use mutating modes or automated game modification.
- Use the exact documented invocation and preserve raw output in the research evidence traces.
