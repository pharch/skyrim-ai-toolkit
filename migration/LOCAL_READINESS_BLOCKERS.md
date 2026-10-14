# Local Research Readiness Blockers

These are genuine environment or source-provenance dependencies, not claims that the associated software is generally unavailable. Raw command results stay in ignored `.local/readiness/`. Seven checklist rows remain externally blocked across five root causes; C07/C08/F08 are resolved with EV-0152/EV-0153, and the Observer build is verified with EV-0154/EV-0155.

## 1. Selected MO2 profile and complete load order — A04, C01, C03

The verified Steam AE executable is 1.6.1170, but the resolver reached the global `plugins.txt`, which contains zero active entries and omits all five required AE masters. The selected MO2 profile is unknown. Preflight therefore fails closed and xEdit was not launched. File-level Skyrim.esm/Update.esm queries do not establish a winner.

To unblock, set `PLUGINS_TXT` in ignored `config/local.env` to the explicit `plugins.txt` for the selected MO2 profile, then run:

```bash
python3 scripts/python_env.py run tools/ae_preflight.py
```

Proceed to xEdit or load-order winner resolution only after preflight reports the exact AE runtime, complete active profile and required masters. Evidence: EV-0110 through EV-0112.

## 2. Live read-only SKSE handshake — C12

The Observer now builds as a 584,192-byte PE32+ x64 Windows DLL with `SKSEPlugin_Load`, `SKSEPlugin_Query` and `SKSEPlugin_Version` exports (EV-0154/EV-0155). SKSE and Address Library file identities match the verified runtime (EV-0128). No plugin was deployed, and no live AE process, handshake, or event capture was available.

To unblock, first identify the selected complete MO2 profile and provide a disposable test save/profile. Stage only the read-only Observer DLL in that disposable profile, manually start the verified AE runtime with SKSE, and capture the handshake under this checkout's ignored `.local/readiness/`. Do not use the active save or launch gameplay unattended. Do not use the original checkout's launcher unchanged because it writes session output into that original repository.

## 3. Permitted real save and ReSaver data — C13

No copied disposable `.ess`/co-save was supplied. Synthetic co-save fixtures pass, while retained legacy co-save output does not preserve the original input path/hash; ReSaver/native structured save inspection was not exercised. `scripts/read-save.py` also cannot run here because the `lz4` module is absent.

To unblock, provide a copied disposable save and matching co-save with provenance, not the active user save. Then run the existing read-only routes from `protocols/TOOL_ROUTING.md`; keep raw captures in `.local/readiness/` and record input hashes. Do not edit or resave the source files.

## 4. UESP snapshot provenance — D09

The local SQLite snapshot is searchable and has a recorded database hash and namespace counts, but its original acquisition URL/date, license note, and completeness measure are absent. The missing provenance cannot be reconstructed from the retained local files reviewed in this audit. Article retrieval and revision citations remain useful secondary-source leads; they do not make the dump complete or establish runtime behavior.

To unblock, supply the original download URL or archived acquisition manifest with date and applicable reuse terms. Recheck the snapshot metadata and the relevant license before redistributing any extracted text.

## 5. Windows Python/pytest and remote CI suite — F10

The local stdlib suite passes on system Python 3.12.3. Conda, pytest, Windows Python, and a connected CI runner were unavailable in this environment; the named Conda environment is therefore unverified. The earlier pytest invocation failed because pytest is not installed. Linux tests do not establish Windows MO2/xEdit or in-game behavior.

To unblock, run the checked-in CI workflow in the supported Windows/Python environment or provide a Windows Python with the declared test dependencies, then preserve its complete result log.
