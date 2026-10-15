# First deep autonomous research session

This is the prepared first-research prompt. In a new interactive Codex session,
bootstrap or repair the host-specific Python environment first, then verify
the strict dispatcher and research-state validation. Reproduce any failed
preflight by rerunning bootstrap and strict validation before treating it as
an external blocker. Check `docs/HARNESS_READINESS.md` for the separately
verified GOG, record-parser, MO2, native export, and live SKSE gates.

## Exact first command

Windows PowerShell:

```powershell
py -3.12 scripts/bootstrap_python.py
py -3.12 scripts/setup_research.py init
py -3.12 scripts/python_env.py check --strict
py -3.12 scripts/python_env.py run scripts/research_state.py validate
```

Linux/WSL:

```sh
python3 scripts/bootstrap_python.py
python3 scripts/setup_research.py init
python3 scripts/python_env.py check --strict
python3 scripts/python_env.py run scripts/research_state.py validate
```

If it fails, repair the recovery state from `STATE.md`,
`research/SESSION_LOG.md`, `research/FRONTIER.json`, and
`research/RECOVERY.json`; preserve evidence and continue once valid.

## Exact first transaction command

Run this only when the first research session begins, after reading the
frontier and readiness gates:

```sh
python3 scripts/python_env.py run scripts/research_state.py begin \
  --transaction-id TX-0005 \
  --frontier-id Q-0001 \
  --next-action "Identify candidate vanilla quest/event level gates and state H1/H2 discriminants before source inspection."
```

In Windows PowerShell, replace the leading `python3` with `py -3.12`.

## Initial Codex prompt

```text
Begin the first deep Skyrim AE glitch-research session only if
`docs/HARNESS_READINESS.md` records passing strict persistent Python 3.12,
GOG function/xref/decompilation, and research-state gates. If strict Python or
a preflight fails, run the documented bootstrap repair and recheck first. If a
required gate still fails, stop before bounty analysis and report its
evidence-backed blocker. The current STATE.md / FRONTIER.json define the
verified local capabilities.
Read AGENTS.md, NORTH_STAR.md, STATE.md, ROADMAP.md, research/FRONTIER.json,
research/EVIDENCE_MODEL.md, protocols/TOOL_ROUTING.md, and
docs/HARNESS_READINESS.md. Load only the skills and source documents
needed for the chosen frontier item.

Start with P0 OBJ-1 / Q-0001: determine which level-gated vanilla quest or
encounter has the strongest tractable evidence for its actual initiation
transition. Treat the retained DA14 >=14 scan and UESP prerequisite as leads,
not as proof of the native start gate. Keep Q-0001's rival models explicit:
(H1) a level predicate is checked at one start transition; (H2) it is checked
later or repeatedly across aliases, dialogue, story-manager, or encounter
transitions. State a discriminating prediction for each before choosing the
cheapest reliable source. If another P0 item now has higher expected
information gain, record why and select it instead.

Use the read-only record reader for explicit plugin-file observations and the
configured existing GOG Ghidra project for static native code. The current
GOG query used `GHIDRA_PROJECT_REP_PATH`; the WSL adapter snapshots that
existing project under ignored `.local/` only because the source mount is
read-only. It uses `-process -noanalysis -readOnly` and never imports or
reanalyzes a binary. Preserve GOG 1.6.1179.0 identity and hash separately from
Steam runtime 1.6.1170.0. Never transfer a GOG address to Steam without
independent mapping. The `xedit_bridge.py file-records` smoke result is a
direct read-only TES4 parser observation, not native SSEEdit or a winning
override. The selected MO2 profile and full order remain unavailable; do not
make profile-specific winner claims or negative findings. Native SSEEdit
export and live SKSE are not prerequisites for this static investigation.
The installed SKSE file identity matches Steam AE 1.6.1170.0, but no game
process, Observer deployment/load, handshake, event, snapshot, or DevBench
connection was tested. Do not launch Skyrim or native xEdit during this
session. If live access is later needed, write the exact profile/save/
deployment test protocol and continue independent static work meanwhile.

For each transaction: preserve raw output under ignored .local/, record command,
build/input hash, coverage, evidence IDs, and uncertainty; update CLAIMS,
CONTRADICTIONS, FRONTIER, SESSION_LOG, STATE, and RECOVERY as warranted. Keep
diagnostic_intervention, vanilla_candidate, vanilla_reproduction, and
mechanism_inference separate. Never infer a negative from missing or partial
coverage.

After every completed or blocked item, re-evaluate the frontier and continue
with the next independent high-information item. Do not stop after one
investigation or because a checkpoint was written. Keep OBJ-1 and OBJ-2 P0;
after each three completed core investigations, perform cross-domain
synthesis, and use at most one bounded breadth item before returning to P0.
Test multiple causal models, record negative results and contradictions, and
revisit model predictions when evidence disagrees.

Before each context or CLI boundary, write the exact next action to STATE.md,
FRONTIER.json, and SESSION_LOG.md. At a fresh session, resume from those files
without requesting a recap. Recovery is a continuation step, not a stop
condition. Do not install or rebuild native tools; use the configured local
bindings. Do not run a time-based supervisor or claim uninterrupted Codex
execution.

Continue until the current tractable frontier has been exhausted, all
independent questions have been reconsidered, and the next exact user action
or frontier decision is recorded. Do not claim a glitch result unless evidence
meets the repository's reproduction and provenance rules.
```

This is a prepared handoff only. The alignment session does not execute the
research prompt.
