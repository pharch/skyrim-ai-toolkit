# Retained tool audit

Status reports repository support and fixture behavior, not Windows/game
integration. No Windows Skyrim AE runtime was available during this migration.

| Tool | Research use | Required environment | Current verification |
|---|---|---|---|
| `tools/ae-target.js` / `ae-preflight.js` | Verify executable identity and active plugin order | Windows for PE ProductVersion; local absolute paths | Parser and fail-closed behavior tested on fixtures; no real PE tested. |
| xEditLib / `tools/xelib/active-plugins.js` | Full-order record inspection | Windows, matching registry mapping, xEditLib DLL; explicit AE profile | Pure load-order parsing tested; DLL/registry not tested. |
| `tools/skyrim-winner.sh` | Winning record and override chain | Windows + xEditLib + full load order | Argument/parser tests only; no live xEdit result. |
| Spriggit CLI | Read-only plugin serialization | .NET and a copied AE plugin | Not installed/fixture-tested in this environment. Never deserialize in research mode. |
| AutoMod archive commands | Inspect/extract AE BSA research inputs | AutoMod CLI, BSArch where required | Wrapper retained; binary not installed here. Archive writes excluded. |
| `tools/resaver-cli.sh` | Read-only save/changeform diagnostics | JDK 17+ and operator-supplied ReSaver jar/lib | Not installed/run; no save provided. |
| `tools/cosave-cli.sh` | Structural SKSE co-save survey | Python 3 | Read-only source and tests retained; no real AE co-save supplied. |
| Papyrus/crash triage | Count and attribute log entries/dumps | Python 3 | Offline script/test coverage; no AE logs supplied. |
| Champollion / Caprica | Decompile/compile isolated Papyrus probes | Windows binaries | Not available; no deployment or compilation performed. |
| DevBench | Optional live AE observational reads | Windows, user-installed compatible SKSE plugin, verified process | Wrapper gated by AE preflight; live server/game not available. |

Linux validation is not evidence of runtime compatibility. See
`docs/getting-started.md` for exact Windows steps and record all outcomes in
the evidence register.
