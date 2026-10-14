# Local setup resume

At a new session, read `AGENTS.md`, `NORTH_STAR.md`, `STATE.md`, `ROADMAP.md`,
`research/FRONTIER.json`, `protocols/TOOL_ROUTING.md`, and this file.

## Current state

- Agent-facing tools and skills use Python entrypoints. Start them with
  `python3 scripts/python_env.py run ...`; the dispatcher uses
  `skyrim-ae-research` via Conda when available and states when it uses the
  system-Python fallback.
- Create the named environment with `conda env create -f environment.yml`.
  This shell had Python 3.12.3 but no Conda or pytest; the Conda environment and
  complete pytest suite remain unverified.
- The 86-item checklist is terminal: 62 PASS and 24 BLOCKED_EXTERNAL, with no
  TODO/IN_PROGRESS/FAIL rows. Read criterion evidence in
  [`LOCAL_SETUP_CHECKLIST.md`](LOCAL_SETUP_CHECKLIST.md).
- Six-domain probe responses are recorded in
  [`TOOL_CAPABILITY_MATRIX.md`](TOOL_CAPABILITY_MATRIX.md). SKSE was tested on
  a synthetic fixture; UESP/Apocrypha local queries respond; Ghidra,
  CommonLibSSE, and SSEEdit report their external blockers.
- Raw local corpora and investigation captures belong under ignored `.local/`.
  Tracked research belongs in Markdown/JSON or the evidence database. The
  reviewer artifact/ignore result is in
  [`PRE_PUSH_SETUP_SUMMARY.md`](PRE_PUSH_SETUP_SUMMARY.md).

## Required before SSEEdit or live-game use

1. On Windows, set `SKYRIM_EDITION=AE`, `GAME_ROOT`, and the selected profile's
   explicit full `PLUGINS_TXT` in ignored `config/local.env`.
2. Run `python3 scripts/python_env.py run tools/ae_preflight.py`. Stop if the
   executable ProductVersion is below 1.6.318, the executable identity is
   ambiguous, or the profile order is incomplete.
3. Compare the reported order identity with the selected MO2 profile. Only
   after that gate may the agent test a Python SSEEdit binding or schedule a
   controlled user observation.

## Research continuation

Continue OBJ-1/OBJ-2 P0 work in `research/FRONTIER.json`. Q-0001's next action
is to select a named candidate from authorized dated source material, then
verify its prerequisite against the winning record in the complete active AE
order. If runtime access is unavailable, continue with independently useful
offline source work and preserve the exact blocker. Keep raw output in ignored
local storage and summarize findings/negative results in the linked experiment
and evidence records.

No commit or push was made; the user will review, commit, and push.
