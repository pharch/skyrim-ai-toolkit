---
name: retained-tool-operations
description: Route and operate the retained Skyrim AE record, archive, save, log, and live-inspection tools safely, with exact input and compatibility checks.
---

# Retained tool operations (Skyrim AE)

Use this skill for research tooling only. Verify `SkyrimSE.exe` as AE runtime
1.6.318+ with `node tools/ae-preflight.js` before any xEdit or live-game operation.
The verifier reads the executable's Windows ProductVersion; a manually typed
version is not accepted. Keep `GAME_ROOT` and `PLUGINS_TXT` local and private.
The latter must identify the active AE profile; for MO2, use the selected
profile's virtualized `plugins.txt`, not a guessed global file. Record its hash
and active plugin count. Empty lists, a missing `Skyrim.esm`, and duplicate
plugins are hard errors.

## Records and archives

- `bash tools/skyrim-winner.sh winner 0x0003418E` / `chain` / `conflicts Plugin.esp`
  asks xEdit for the final record state against the full active order. Trust the
  wrapper's exit code: 0 is complete, 2 is a reported error, 3 means no valid
  result marker. Never infer absence from a failed or partial load.
- xEditLib uses `GM_SSE` for AE records and is Windows-only. Use the helper in
  `tools/xelib/active-plugins.js`; do not load hand-picked plugin subsets. Delphi
  string arguments are UTF-16LE, `WordBool` is 16-bit, and `InitXEdit` /
  `CloseXEdit` are void. Registry and native-library setup belong on the
  operator's Windows machine, not in Linux CI.
- Inspect an archive with `bash tools/automod-cli.sh archive info|list|validate|diff ... --json`.
  The wrapper blocks extraction and archive mutation; do not bypass it.
  Loose files take precedence over archive members; note that limitation in
  record/source claims.
- Use Spriggit only to serialize copied plugins for read-only inspection. Keep
  unknown-field warnings enabled (`-u` / `--ErrorOnUnknown`) and round-trip
  check any newly investigated field. Do not deserialize or save plugin edits.

## Saves, scripts, logs, and runtime

- `bash tools/resaver-cli.sh info|dump|find|find-refs|worries|recon|changeform|extradata-scan|changeform-diff|freeze-report|globaldata ...`
  are analysis operations. ReSaver requires JDK 17+ and the operator-provided
  `ReSaver.jar` plus `lib/`. The wrapper rejects save-writing, cleanup, and
  round-trip operations; analyze copies and preserve source hashes.
- `bash tools/cosave-cli.sh file.skse` is a read-only structural survey of
  stored plugin data; it does not prove player ActorValues or ActiveEffect state.
- `python tools/papyrus-triage.py [log]` counts entries, not continuation lines.
  `python tools/crash-triage.py [file-or-dir]` recognizes CrashLogger `.log` and
  `.txt` files. Preserve denominator, ignored/unreadable counts, and exact input.
- Decompilation output, if used from an operator-installed tool, is derived
  evidence and not original source. Record the exact tool version and preserve
  the compiled input; this harness does not compile or deploy scripts.
- DevBench is an optional, user-installed live-game plugin. Run `alive` before
  state reads, confirm the returned executable identity is the verified AE
  instance, and use the wrapper's read-only inspection calls. Console,
  Papyrus invocation, raw tools, save/load, and scenario endpoints are disabled.

For every tool result, retain command, tool version, exit status, edition/build,
input path/hash, coverage denominator, and raw output. Empty results without
those checks are unknown, not negative evidence. Linux CI can validate parsers,
fixtures, and routing logic; it cannot validate the Windows xEdit DLL, MO2
profile virtualization, DevBench, or an in-game Skyrim runtime.
