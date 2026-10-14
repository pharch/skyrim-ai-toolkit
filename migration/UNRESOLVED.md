# Current external blockers and research limits

The authoritative setup audit is the 86-item ledger in
[`LOCAL_SETUP_CHECKLIST.md`](LOCAL_SETUP_CHECKLIST.md). There are no unfinished
status labels after final reconciliation; external blockers remain explicit.

## Windows and runtime

- The configured `SkyrimSE.exe` ProductVersion could not be obtained from this
  WSL session. Run `python3 scripts/python_env.py run tools/ae_preflight.py` on
  Windows and preserve the result before any xEdit/live-game operation.
- Configure the selected MO2 profile's explicit full `plugins.txt`. A present
  candidate file is not a verified active order.
- Ghidra returned a doctor response but could not run because Java is missing.
  CommonLibSSE returned a doctor response but could not build because CMake is
  missing. SSEEdit's candidate exists, but its Windows call remains blocked by
  the unverified target and profile.
- SKSE parsing responded on a synthetic fixture only; no live bridge handshake
  or real co-save was available.
- No controlled runtime snapshot or immutable raw runtime capture exists. The
  experiment protocols are ready for a verified Windows target and disposable
  level-one save.

## Corpus and source provenance

- UESP doctor, search, and revision-specific page retrieval respond from the
  local index. Official acquisition URL, license, and completeness remain
  unverified.
- Apocrypha's ignored local index reports 60,873 messages matching its
  declared count. Search was aggregate-only for this audit; community content
  remains private and untrusted.
- The separate source checkout has no usable `.git` metadata, so its source
  commit, branch, original status, and submodule state cannot be recovered.

## Python environment

- `environment.yml` defines `skyrim-ae-research` on Python 3.12. Create it with
  `conda env create -f environment.yml`; `scripts/python_env.py` dispatches
  agent commands through `conda run` when available.
- Conda and pytest are absent from the current shell. Available standard
  library tests and Python probes can run on Python 3.12.3; the complete pytest
  suite and a clean Conda install were not verified here.

Linux validation does not establish Windows MO2/xEdit behavior, Ghidra or
CommonLib execution, or in-game AE behavior.
