# Local setup report

Date: 2026-10-14

## Readiness

**Tier: `READY_FOR_STATIC_RESEARCH`. The verified Windows/AE runtime lab and
deep autonomous continuity pilot are not ready.** Skills and Python tools return usable offline
responses, research outputs have compact Markdown/JSON records, and private
corpora stay in ignored local storage. Runtime experiments must wait until the
exact AE executable and complete active profile are verified.

The 86-item checklist records **62 PASS and 24 BLOCKED_EXTERNAL** criteria, with
no TODO, IN_PROGRESS, or FAIL entries. The blocked rows name the missing
machine, source-provenance, or independent-session evidence.

## Verified in this shell

- Python 3.12.3 runs the fallback path. `environment.yml` defines the
  `skyrim-ae-research` Conda environment, and `scripts/python_env.py` dispatches
  to it when Conda is installed. Conda and pytest are absent here, so this
  session did not create or verify the Conda environment or full pytest suite.
- Thirty-one focused standard-library tests pass across AE target policy,
  TES4 parsing, Python dispatch, SKSE fixture parsing, UESP/Apocrypha privacy,
  local paths, recovery/successor rules, and Markdown entity schemas.
  `scripts/validate_research.py` passes. Papyrus triage accounted for two
  synthetic entries and crash triage parsed one synthetic dump; both returned
  `RESULT: OK`.
- The six-domain doctor returns structured responses for SKSE, Ghidra,
  CommonLibSSE, SSEEdit, UESP, and Apocrypha. SKSE was a synthetic co-save
  fixture only. Ghidra is blocked by missing Java; CommonLibSSE is blocked by
  missing CMake; SSEEdit is blocked by Linux host plus unverified runtime/order.
  UESP and Apocrypha local databases respond to doctor/search queries.
- UESP reports 475,228 pages and 17,520 custom `Skyrim` namespace pages. A
  real local `Skyrim:Karstaag` lookup returned revision 3629292. Acquisition
  provenance, license, and completeness remain unverified.
- Apocrypha reports 60,873 indexed messages matching its declared count.
  The audit emitted aggregate results only; community content and identifiers
  remain private and untrusted.
- Claims, mechanisms, glitches, contradictions, and EXP records now have
  stdlib structural/provenance validation. The frontier requires evidence and
  successor links for terminal decisions.

## Git/privacy boundary

The final `python3 scripts/pre_push_audit.py` check passed. It found 0 tracked
raw artifacts, 0 tracked files at or above 5 MiB, and 0 unignored untracked raw
artifacts; all 11 synthetic ignore probes passed. Two ignored local SQLite
databases total 2,498.9 MiB. The audit emits aggregate counts and types only.
`session_prompt.md`, private path config, local SQLite indexes, compressed
archives, logs, saves/co-saves, exports, captures, and dumps are covered by
ignore rules. Results are recorded in
[`PRE_PUSH_SETUP_SUMMARY.md`](PRE_PUSH_SETUP_SUMMARY.md).

## External blockers

- WSL could not read the configured executable's Windows ProductVersion.
  `PLUGINS_TXT` is not configured, so no complete active MO2 order is verified.
  No xEdit or live-game call was made.
- No Ghidra analysis, CommonLibSSE build, real SKSE handshake, real save/co-save
  inspection, or controlled in-game snapshot was performed.
- The separate source checkout has no usable `.git` metadata, so checklist G01
  is blocked. Native Ghidra/SKSE/xEdit/CommonLib procedure validation remains
  blocked in this shell (G10). UESP official acquisition/license/completeness
  remain unknown.
- The fresh independent-context restart and forced separate-session resume
  pilots remain unperformed.

Linux fixture validation does not establish Windows MO2/xEdit behavior, native
Ghidra/CommonLib execution, or Skyrim AE runtime behavior.

## Handoff

No commit or push was made. The user will perform those actions after review.
Start with [`LOCAL_SETUP_RESUME.md`](LOCAL_SETUP_RESUME.md), then follow the
exact next action in `STATE.md` and `research/FRONTIER.json`.
