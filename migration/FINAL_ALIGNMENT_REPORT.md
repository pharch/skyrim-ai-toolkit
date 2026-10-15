# Final local harness alignment report

Date: 2026-10-15 follow-up. Scope: the 52 criteria in
[`FINAL_LOCAL_HARNESS_ALIGNMENT.md`](FINAL_LOCAL_HARNESS_ALIGNMENT.md). This
was a tooling and handoff pass; no open-ended Skyrim glitch investigation was
started.

## Result

The existing GOG Ghidra route is verified and ready for static work. The
user-designated `skyrim` xEdit bridge configuration was copied into ignored
local config, its isolated five-master session passed scoped runtime/order
preflight, and SSEView opened after approval. Its Module Selection dialog was
confirmed against the generated list and the background loader finished
(EV-0189). This verifies launch and isolated module loading: no record query
ran and the selected full MO2 order remains unknown. The Observer was rebuilt
from an isolated authoritative source copy and its prepare-only manifest was
verified; it remains undeployed with no live handshake. The criterion-by-
criterion disposition is in
[`FINAL_ALIGNMENT_CHECKLIST.md`](FINAL_ALIGNMENT_CHECKLIST.md); remaining
external dependencies stay explicit. EV-0191 records the user's requested exact
xEdit bridge replay: eight helper/template files match the authoritative source
byte-for-byte, all five xEdit-relevant config values match, and the copied
bridge's doctor, isolated session preparation, and scoped AE preflight pass.
This replay did not launch a duplicate SSEView process or run a record export;
the selected MO2 profile remains unconfigured.

The repository began on `glitch-hunting-setup` at
`7e24ba61fff01d5da5c88b629a0da7744b408c78` with a clean worktree. The original
`skyrim` research checkout and its ignored local sources were inspected
read-only. Its `.git` metadata is unavailable, so legacy provenance is carried
by preserved source aliases and hashes rather than a source commit. The
alignment edits remain local and uncommitted; this session's workspace
permissions expose `.git` as read-only. No push occurred.

## Three readiness gates

| Gate | Assessment | Evidence and limit |
|---|---|---|
| `STATIC_RESEARCH_READY` | **READY** | EV-0165–EV-0167 verify the configured GOG 1.6.1179.0 executable against the existing `skyrim-gog` project, then run function lookup, xref, 24-instruction disassembly and decompilation in `-process -noanalysis -readOnly` mode. The GOG binary SHA-256 is `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. A targeted CommonLib AE ID 11321 resolves to GOG RVA `0x14C020`. This establishes the static tool path, not a gameplay mechanism or Steam address. |
| `NATIVE_RESEARCH_READY` | **PARTIAL** | EV-0184 reread Steam `SkyrimSE.exe` ProductVersion 1.6.1170.0 and verified a scoped list of the five official masters. EV-0185 confirms the approved generated SSEView 4.1.5f `-view` process opened; EV-0189 confirms the exact five masters loaded and Background Loader finished. EV-0191 replays the authoritative bridge helper/config and passes doctor, prepare, and scoped preflight. UI Automation exposed no record tree controls and no export was produced. EV-0120/EV-0181 attest SSEEdit 4.1.5.0. The scoped vanilla list is not the selected MO2 profile: no record query/export, full order, or winning-record result exists. File-level Python inspection remains available; profile-dependent negatives remain blocked. |
| `INSTRUMENTED_AUTONOMOUS_RESEARCH_READY` | **NOT_VERIFIED** | EV-0187 verifies installed SKSE/runtime/Address Library identities. EV-0186 verifies a fresh local Observer build and 7/7 analyzer tests; EV-0188 verifies a prepare-only manifest with no deployment or launch. No running game, Observer handshake, DevBench capture, designated test save, or ReSaver path exists. No game was launched and no user save was opened. |

These results do not collapse into one general “ready” status. The second and
third gate limits do not prevent the first session's offline GOG static work.

### SSEEdit identity correction

EV-0180 described SSEEdit as ProductVersion-verified using a field from the
EV-0172 domain-doctor output. That field reported the Skyrim target runtime,
not the SSEEdit executable's version. EV-0120 is the direct SSEEdit metadata
record for 4.1.5.0; EV-0181 confirms the current configured executable still
matches EV-0120's SHA-256 and fixes the doctor output to expose this separately
as `SSEEdit.runtime_target`. EV-0184 separately rereads Skyrim ProductVersion
through the approved host path. EV-0185 proves the isolated SSEView launch;
EV-0189 verifies its five-master load completed. The complete profile/order
and any record query remain unavailable.

## Tool verification

- **Ghidra:** The existing GOG project and imported binary identity were
  verified, with 172,782 functions and 1,050,918 symbols. A normal function
  query, real call edge, disassembly and decompilation passed (EV-0165). The
  Python adapter then passed through the single `config/local.env` binding
  (EV-0166). A build-attested Address Library lookup and targeted query of
  `FUN_14014c020` passed (EV-0167). No import, overwrite, deletion or full
  analysis ran. Ghidra refreshed four internal `~index.*` timestamps on open;
  existing program/user `.gbf` database sizes and modification times remained
  unchanged in the captured preservation check (EV-0165).
- **xEdit bridge:** The authoritative `skyrim` repo's `scripts/skyrim_tool.py`
  `doctor` and `prepare-xedit` commands passed; copied config bindings match the
  tested SSEEdit/Data/Edit Scripts installations. The generated list contains
  only five official masters, and the approved `-view`/no-`-autoload` SSEView
  process opened (EV-0184–0185). EV-0189 verifies guarded confirmation of
  exactly those five masters and `Background Loader: finished`. UI Automation
  exposed no record-tree controls; no record was queried or exported. This is
  not a selected MO2 profile or winner result.
- **Runtime and SKSE:** Steam ProductVersion/hash and matching SKSE loader,
  runtime DLL and Address Library identities were read (EV-0184/0187). The
  Observer was rebuilt from an isolated copy of authoritative `skyrim/observer`
  with reviewed local CommonLib/compiler compatibility edits; fresh objects,
  PE32+ x64 output, and 7/7 analyzer fixtures are recorded in EV-0186. The
  authoritative launcher prepared a manifest with `launch_requested=false`
  (EV-0188). The DLL remains staged, not deployed or loaded; no live handshake
  is established.
- **CommonLib / Address Library:** `MagicItem::CalculateCost` maps from CommonLib
  AE ID 11321 to GOG RVA `0x14C020` through the matching GOG database. The
  retained generic `target=ae` map is rejected as a GOG address source
  (EV-0167).
- **Papyrus / BSA:** A known `DA14Script` input was extracted from the configured
  base BSA and its 507-byte PEX stream parsed completely (EV-0169). This is a
  bounded archive/bytecode check, not an in-game result or general decompiler.
- **UESP / Apocrypha:** A real UESP page revision and a private Apocrypha
  message/context were retrieved (EV-0170, EV-0171). Private text and stable
  identifiers remain in ignored `.local/`; community content is only a lead.
- **Fresh checkout and recovery:** EV-0175 records an isolated checkout,
  generated private config, setup and binding doctors, startup validation, and
  a transaction recovered and resumed across separate processes. All steps
  exited 0; no game or xEdit process was involved.

## Remaining external blockers and unblock steps

1. **Complete runtime load order and xEdit record query.** Identify the actual
   selected MO2 profile, then set `MO2_PROFILE_DIR` and `PLUGINS_TXT` in ignored
   `config/local.env` to that profile and its explicit `plugins.txt`. The
   existing SSEEdit 4.1.5.0 executable matches the versioned file in
   EV-0120/EV-0181; the isolated bridge launch, scoped preflight, and five-
   master load pass in EV-0184/EV-0185/EV-0189, but no record query was run.
   UI Automation exposed no safe record selector, so no blind keyboard input
   or exporter invocation was attempted. Then run:

   ```text
   python3 scripts/python_env.py run tools/ae_preflight.py
   ```

   It must confirm the executable ProductVersion, all active plugins, and
   required masters before xEdit opens. Then use xEdit read-only for the
   winning-record query. The Python fallback command
   `python3 scripts/python_env.py run tools/plugin_reader.py record <plugin>
   --signature <signature> --form-id <local-id> --include-subrecords` reads one
   file and is not an xEdit winner result.

2. **Real save/co-save/ReSaver parse.** No designated disposable `.ess` copy or
   ReSaver executable/path was found (EV-0174). The current system-Python
   fallback also lacks `lz4`, so `scripts/read-save.py --help` fails at import.
   Conda is absent; if the named environment is available to the user, create
   and verify it with:

   ```text
   conda env create -f environment.yml
   conda activate skyrim-ae-research
   python3 scripts/python_env.py check
   ```

   Only then set `RESEARCH_TEST_SAVE` to a designated disposable copy and use
   `python3 scripts/python_env.py run scripts/read-save.py <copy.ess>` or
   `python3 scripts/python_env.py run tools/cosave-info.py <copy.skse>`. No
   original save may be used or modified.

3. **Live safe Observer handshake.** The fresh Observer DLL is built and
   staged under ignored `.local` (EV-0186), and its prepare-only manifest binds
   the exact DLL/runtime hashes with no deployment or launch requested
   (EV-0188). `SKSE_LOADER` is now bound to the metadata-verified loader, but no
   selected disposable profile, plugin list, safe MO2 mod directory, or test
   save is configured. Once those exist, set `SKYRIM_OBSERVER_DEPLOYED_DLL`,
   `SKYRIM_PLUGIN_LIST`, and `RESEARCH_TEST_SAVE` for that disposable lane,
   verify the deployed hash matches the staged DLL, and use a user-controlled
   launch to capture the read-only handshake. This alignment did not deploy or
   start Skyrim.

4. **Python environment / CI runner.** Conda and `pytest` are absent from this
   Linux system Python. Unittest and repository validators can run locally;
   the checked-in CI installs declared Python test dependencies. No CI service
   job was run from this session. Windows xEdit/MO2 behavior and in-game AE
   behavior remain unverified by Linux tests.

The local UESP dump source URL/license/completeness are also unknown (EV-0170).
Obtain corpus provenance metadata before treating it as a complete source.

## Portable validation

EV-0176 records the local run: **150/150 unittest tests passed**; compileall,
research/evidence, recovery, transaction, overlay, setup doctor, Markdown
inventory write/check, and pre-push audit all exited 0. All 13 active skill
files passed `quick_validate.py`. The pre-push audit counted 274 tracked files,
zero tracked raw/heavy files, zero unignored untracked raw candidates, and 11
passing ignore probes. EV-0177 repeats the portable setup and the same 150-test
suite in a fresh checkout with no Ghidra/game bindings or preexisting local
config; every command passed.

System Python 3.12.3 is active because Conda is unavailable. The `pytest`
availability probe fails because pytest is not installed; unittest is the
available suite runner. `read-save.py --help` fails at import because the
fallback lacks `lz4`. No package or native tool was installed or rebuilt, and
no hosted CI job was run. The final acceptance, path, gate, artifact and
worktree audits are recorded in EV-0178/EV-0179/EV-0180. EV-0181 corrects the
domain-doctor ProductVersion semantics and rechecks current executable hashes.
The final post-fix closeout EV-0182 records the October 14 baseline (151/151
unittest tests and 49 PASS / 3 BLOCKED_EXTERNAL criteria). The October 15
follow-up adds EV-0184–EV-0189: copied authoritative xEdit bridge config,
approved SSEView launch and completed five-master load, fresh
authoritative-source Observer build, SKSE identity probe, and prepare-only
manifest. EV-0190 records the initial final closeout. EV-0191 records the exact bridge/config replay, a fresh 151-test pass, all 13 active-skill checks, all post-edit repository validator exits, and the final direct audit of the 52-row tally, three gates, evidence hashes, Observer staging, and initial prompt. The current 52-row tally remains 50 PASS / 2 BLOCKED_EXTERNAL.

Linux validation does not establish Windows xEdit/MO2 behavior or in-game AE
behavior. The report makes no glitch-mechanism claim.

## Exact next research start

At the repository root, the first command is:

```text
python3 scripts/python_env.py run scripts/research_state.py validate
```

Then open a new interactive Codex session and use the full prompt in
[`docs/RESEARCH_START_PROMPT.md`](../docs/RESEARCH_START_PROMPT.md). It starts
with P0 OBJ-1 / Q-0001, states competing start-gate hypotheses and predicted
discriminants, and directs the session to keep investigating independent
frontier items across checkpoints. The alignment pass has not executed it.
