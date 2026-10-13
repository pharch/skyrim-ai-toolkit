# Getting started: Skyrim AE research checkout

## 1. Set up the Codex workspace

Clone the research repository somewhere outside the Skyrim installation and
open that checkout in VS Code or the Codex CLI. Do not copy this repository into
the game directory. Install Node.js 20+, Python 3.11+, Git, and Codex using the
official Codex installation instructions.

```sh
git clone https://github.com/pharch/skyrim-ai-toolkit.git
cd skyrim-ai-toolkit
python scripts/setup_research.py init
python scripts/setup_research.py check
npm ci
npm test
python -m pytest -q
```

`init` creates `config/local.env` from the example only when it does not
already exist. It does not detect, install, configure, or write to Skyrim.
Keep private local paths in that ignored file; never commit it.

## 2. Configure and verify the AE installation (Windows only)

Edit `config/local.env` on the Windows machine that has the research
installation. Set `SKYRIM_EDITION=AE`, `GAME_ROOT`, and the active load-order
file. Leave `SKYRIM_EXE_PATH` blank to use `GAME_ROOT/SkyrimSE.exe`, or set the
exact executable path if needed.

For a stock AE profile, the default load-order location is
`%LOCALAPPDATA%/Skyrim Special Edition/plugins.txt`. For MO2, use the active
profile's `plugins.txt`; the global profile is not a safe substitute. Ensure it
begins with active `*Skyrim.esm` and contains the complete current order.

```powershell
node tools/ae-preflight.js
```

The preflight reads the PE ProductVersion, requires AE runtime 1.6.318+, hashes
the executable and load-order file, and validates all five required official
masters plus the selected active list. It does not prove
that MO2 launched the same profile; compare the path and hash with MO2's active
profile before interpreting a result. Do not type a version into config and
treat it as detection.

### xEdit/xelib requirements

xEditLib's Delphi DLL is a Windows-only integration. Install it only on the
Windows research machine, following the upstream xEditLib instructions; do not
attempt an xEdit load from Linux. The tools use `GM_SSE` (enum value 4) for
AE's plugin record format, but that API mode alone does not establish the game
edition. The target preflight must pass first. Check that the installed
registry mapping points to the same AE `GAME_ROOT`; this harness does not edit
the Windows registry.

## 3. Validate offline

On any supported development host:

```sh
node --test tools/ae-target.test.js tools/xelib/active-plugins.test.js
npm test
python -m pytest -q
python scripts/validate_overlay.py
git diff --check
```

These checks cover code, schema, and fixtures only. They are not a Windows game
integration test.

## 4. Route tools by evidence need

- **Records and winning overrides:** on Windows, use `tools/skyrim-winner.sh`
  with the complete profile order.
- **Saves:** use read-only `tools/resaver-cli.sh` operations on a copy or
  preserved original. Never use write modes during research.
- **Co-save structure:** `tools/cosave-cli.sh` reports plugin containers, not
  player stats or ActiveEffects.
- **Papyrus/crash logs:** use the triage scripts and preserve denominators.
- **Archives:** inspect `.bsa` files with the read-only AutoMod JSON wrapper;
  extraction and archive mutation are deliberately disabled.
- **Live state:** DevBench is optional and user-installed. Run `alive`, verify
  the instance identity, then restrict work to approved read-only inspection.
  Do not configure its mutating endpoints for an unattended Codex run.

See [protocols/TOOL_ROUTING.md](../protocols/TOOL_ROUTING.md) and the
[retained-tool skill](../.agents/skills/retained-tool-operations/SKILL.md) for
specific commands, formats, known failure modes, and platform boundaries.

## 5. Recover a research session

Read `STATE.md`, the latest entry in `research/SESSION_LOG.md`, and the active
frontier item. The frontier must identify its source IDs and next discriminating
action. If a Codex or supervisor process stopped unexpectedly, inspect its run
metadata/logs before resuming; do not infer success from a process launch or
partial output.
