# Skyrim AE research tool routing

Use retained upstream tools before writing a new parser. Every result needs the
exact command, exit status, tool version, input identity/hash, target runtime,
and coverage denominator. An empty result without verified coverage is
`unknown`, not negative evidence.

## Mandatory target and order gate

Before xEdit or DevBench, run:

```sh
node tools/ae-preflight.js
```

The gate reads `SkyrimSE.exe`'s Windows ProductVersion and requires 1.6.318 or
newer. `SKYRIM_EDITION=AE` is a scope declaration only. The preflight hashes the
executable and validates the active order. The exact profile/load-order path
must be recorded. MO2 users set `PLUGINS_TXT` to the chosen profile's
virtualized file. No cross-edition path search or inferred profile is allowed.

## Tool matrix

| Evidence need | Tool and command | Compatibility / caveat |
|---|---|---|
| Final winning record / override chain | `bash tools/skyrim-winner.sh winner <FormID>` or `chain <FormID>` | Windows xEditLib; full active order; wrapper exit 0=success, 2=reported error, 3=no result marker. |
| Base plugin/script discovery | `bash tools/automod-cli.sh archive info|list|validate|diff <AE.bsa> --json` | AutoMod optional; this wrapper blocks extraction and archive writes. |
| Readable record serialization | Spriggit serialize a copied plugin | .NET tool; use installed package version and unknown-field checking; do not deserialize or overwrite plugins. |
| Papyrus source hypothesis | Inspect preserved or decompiled source as derived evidence | Decompilation is optional and external; preserve the original `.pex` hash. This harness does not compile or deploy scripts. |
| Save/changeform/global inspection | `bash tools/resaver-cli.sh info|dump|find|find-refs|worries|recon|changeform|extradata-scan|changeform-diff|freeze-report|globaldata|globaldata-diff ...` | JDK 17+ and operator-supplied ReSaver jar/lib; all listed operations are read/diagnostic. Never pass `--apply` or choose cleanup/write operations. |
| Co-save structure | `bash tools/cosave-cli.sh <save.skse>` | Read-only structural plugin-container survey; does not prove ActorValues or ActiveEffect state. |
| Papyrus log coverage | `python tools/papyrus-triage.py [log]` | Counts entries, not continuation lines; keep denominator and not-shown bucket. |
| Crash dump signatures | `python tools/crash-triage.py [file-or-dir]` | Reads `.log` and `.txt`; preserve total, unreadable, and matched file counts. |
| Live state | `bash tools/devbench-cli.sh alive`, then approved read-only inspect | Windows + user-installed DevBench; AE preflight; verify process identity. Do not expose console, save/load, raw mutators, or scenarios to unattended runs. |

## xEditLib operational constraints

xEditLib is a Delphi native DLL and is Windows-only. Its AE plugin format uses
xEdit `GM_SSE` (enum value 4); this setting is not an edition detector.
`tools/xelib/active-plugins.js` passes the explicitly resolved complete active
order to xEdit. Do not use hand-picked plugin subsets to support a negative
claim. The wrapper exists because the raw Node process exit status may be
unreliable with the native library; trust `skyrim-winner.sh`'s `RESULT` marker
and wrapper status.

Other API details preserved from the upstream instructions: Delphi strings are
UTF-16LE; `WordBool` is a 16-bit value; `InitXEdit()` and `CloseXEdit()` are
void. Registry setup is a local Windows prerequisite and is never edited by
this harness. Do not use Node inline evaluation for native calls; run tested
scripts as files.

## Platform evidence boundary

Linux tests may validate pure parsers, fixtures, JSON schemas, workflow policy,
and shell syntax. They cannot validate the real Windows PE version resource,
xEditLib registry/DLL behavior, the profile MO2 actually launched, Windows
binary versions, DevBench, or an in-game result. Mark those checks
`awaiting-windows-ae` and follow the exact local steps in
`docs/getting-started.md`.
