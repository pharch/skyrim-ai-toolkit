# Windows AE verification checklist

This repository cannot prove a live Windows Skyrim AE installation or in-game behavior from Linux. Use the exact steps below on the user's Windows machine before interpreting any runtime result, xEdit record, MO2 profile, or DevBench observation.

## Required prerequisites
- Windows 10/11 machine with the user's Skyrim AE installation.
- `SkyrimSE.exe` present under the actual game root.
- Optional: MO2 profile + active `plugins.txt` for the selected AE profile.
- Optional: xEdit/xEditLib, SKSE, DevBench, or a disposable save for later read-only inspection.
- Do not run these steps inside the repository checkout. Keep the repo separate from the game installation.

## 1. Confirm the exact game root and executable
PowerShell:
```powershell
$GameRoot = "C:/Games/Skyrim Special Edition"
$Exe = Join-Path $GameRoot "SkyrimSE.exe"
Get-Item $Exe | Select-Object FullName,Length
(Get-Item $Exe).VersionInfo.ProductVersion
```

Accept only `SkyrimSE.exe` with ProductVersion `1.6.318` or newer. If the version is older or the file is missing, stop and do not continue with live-game attempts.

## 2. Verify the active AE load order
PowerShell:
```powershell
$Plugins = "$env:LOCALAPPDATA\Skyrim Special Edition\plugins.txt"
Get-Item $Plugins | Select-Object FullName,Length
Get-Content $Plugins -TotalCount 25
```

For MO2, use the selected profile's `plugins.txt` instead of the global file. The list must begin with `*Skyrim.esm` and include the full active master set, not a guessed or partial order.

## 3. Run the repository preflight
From the repo checkout:
```powershell
node tools/ae-preflight.js
```

The script reads the Windows ProductVersion, requires AE runtime 1.6.318+, hashes the executable and active plugin list, and rejects non-AE or partial orders. Do not treat a manually typed version value as proof.

## 4. Record runtime evidence
Capture and preserve:
- `SkyrimSE.exe` path and hash
- ProductVersion output
- `plugins.txt` path and hash
- exact MO2 profile name/path used, if applicable
- xEdit/xEditLib version and registry mapping
- any SKSE or DevBench versions used

## 5. Only then proceed to read-only analysis
Allowed Windows-only actions after preflight passes:
- `bash tools/skyrim-winner.sh winner <FormID>` or `chain <FormID>` with the verified active load order
- `bash tools/automod-cli.sh archive info|list|validate|diff ... --json`
- `bash tools/resaver-cli.sh info|dump|find|find-refs|worries|recon|changeform|extradata-scan|changeform-diff|freeze-report|globaldata|globaldata-diff ...`
- `bash tools/cosave-cli.sh <save.skse>`
- `python tools/papyrus-triage.py [log]`
- `python tools/crash-triage.py [file-or-dir]`
- `bash tools/devbench-cli.sh alive` and approved read-only inspection only

Do not use any mutating or write operation during research without separate explicit consent for a disposable runtime experiment.

## 6. Report results honestly
The repo can claim repository/cloud readiness only when the local validation checks pass. It cannot claim gameplay proof or AE runtime verification from Linux or from a not-yet-executed Windows preflight. Mark the result as `WINDOWS AE RUNTIME: UNVERIFIED` until the commands above succeed in the user's Windows environment.
