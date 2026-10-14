# Local Research Readiness Blockers

These are environment or source-provenance dependencies, not claims that the associated software is generally unavailable. Raw command results stay in ignored `.local/readiness/`.

## 1. Selected MO2 profile and complete load order — A04, C01, C03

The verified Steam AE executable is 1.6.1170, but the resolver reached the global `plugins.txt`, which contains zero active entries and omits all five required AE masters. The selected MO2 profile is unknown. The preflight therefore fails closed and xEdit was not launched. File-level Skyrim.esm/Update.esm queries do not establish a winner.

To unblock, set `PLUGINS_TXT` in ignored `config/local.env` to the explicit `plugins.txt` for the selected MO2 profile, then run:

```bash
python3 scripts/python_env.py run tools/ae_preflight.py
```

Proceed to xEdit or load-order winner resolution only after preflight reports the exact AE runtime, complete active profile and required masters. Evidence: EV-0110 through EV-0112.

## 2. Ghidra native query launch — C07, C08 (BLOCKED_EXTERNAL for this audit)

The correct AE executable was imported into Ghidra 12.0.4 with Java 21.0.10. The first analysis saved a partial project with 92,219 functions but timed out during entry-point analysis. A separate 7,200-second analysis in session 40253 has terminated after 7,260.809 seconds, reported timeout, and saved an incomplete project (EV-0139). The repaired read-only query emits function lookup, bounded disassembly, optional decompilation, and an explicit no-edge result. Its hash-attested fallback verifies the current executable bytes against the ProductVersion-backed EV-0109 and import EV-0113 evidence.

Three query attempts (EV-0131, EV-0138, and EV-0141) failed before launching Ghidra: WSL returned `UtilBindVsockAnyPort:307: socket failed 1`. The latest passed the EV-0139 metadata and executable hash checks before native invocation. No xref, disassembly, or decompilation is claimed. Session 40253 has now terminated at its analysis limit and saved an incomplete project (EV-0139). The process bridge must work before the query can run. Retry:

```bash
python3 scripts/python_env.py run tools/ghidra_probe.py --project-dir .local/readiness/ghidra/project_AE_SkyrimSE_1_6_1170_longanalysis --project-name AE_SkyrimSE_1_6_1170_longanalysis --timeout 300
```

This command reads the existing longanalysis project. Its query-only fallback checks the EV-0109 executable, EV-0139 output and metadata hashes, exact project path, and current binary bytes. Keep new imports on the normal ProductVersion check. If the bridge still fails, retain C07/C08 as externally blocked and restore Windows interop before claiming query capability.

## 3. Observer DLL and live SKSE handshake — C12

The CommonLibSSE-NG library built for AE, but the combined Observer DLL target failed in its generated metadata translation unit because CommonLib `REL/Version.h` saw missing standard-library declarations. A local-only header repair is staged in ignored `.local`; repeated build retries could not start because WSL Windows interop failed. The Observer DLL was not produced, so there is no plugin to stage and no runtime handshake. SKSE/Address Library file identities match the verified runtime, but that is metadata only (EV-0128, EV-0130).

After Windows interop is restored, retry the local build via `.local/readiness/tests/build-commonlib.cmd`. If it succeeds, select a disposable MO2 profile and save, stage only the read-only Observer in that profile, launch the verified AE runtime manually, and record the handshake under this checkout's ignored `.local/readiness/`. Do not use the original checkout's launcher unchanged: it writes session output into the original read-only repository. Never launch unattended gameplay.

## 4. Permitted real save and ReSaver data — C13

No copied disposable `.ess`/co-save was supplied. Synthetic co-save fixtures pass, while retained legacy co-save output does not preserve the original input path/hash; ReSaver/native structured save inspection was not exercised. `scripts/read-save.py` also cannot run here because the `lz4` module is absent.

To unblock, provide a copied disposable save and matching co-save with provenance, not the active user save. Then run the existing read-only routes from `protocols/TOOL_ROUTING.md`; keep raw captures in `.local/readiness/` and record input hashes. Do not edit or resave the source files.

## 5. UESP snapshot provenance — D09

The local SQLite snapshot is searchable and has a recorded database hash and namespace counts, but its original acquisition URL/date, license note, and completeness measure are absent. The missing provenance cannot be reconstructed from the retained local files reviewed in this audit. Article retrieval and revision citations remain useful secondary-source leads; they do not make the dump complete or establish runtime behavior.

To unblock, supply the original download URL or archived acquisition manifest with date and applicable reuse terms. Recheck the snapshot metadata and the relevant license before redistributing any extracted text.

## 6. Independent Codex-context recovery — F08

A separate Codex-context attempt was rejected by automatic review because the proposed external payload could contain internal repository documents. No internal documents were sent and no separate context was created. The required deterministic recovery test did run in fresh local Python processes; it does not certify independent Codex-session recovery.

To complete the stronger check, open a separate local Codex conversation and provide only `migration/LOCAL_READINESS_RESUME.md` plus the repository's normal startup instructions. Do not send internal repository files to an external service through an unreviewed payload.

## 7. Windows Python/pytest and remote CI suite — F10

The local stdlib suite passes on system Python 3.12.3. Conda, pytest, Windows Python, and a connected CI runner were unavailable in this environment; the named Conda environment is therefore unverified. The earlier pytest invocation failed because pytest is not installed. Linux tests do not establish Windows MO2/xEdit or in-game behavior.

To unblock, run the checked-in CI workflow in the supported Windows/Python environment or provide a Windows Python with the declared test dependencies, then preserve its complete result log.
