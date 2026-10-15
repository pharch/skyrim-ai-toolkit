# First deep research session

This prompt is a prepared handoff. Do not execute its transaction command in
the setup session. In a new research session, bootstrap or repair Python,
check the strict dispatcher, and validate recovery state before starting.
Review `docs/HARNESS_READINESS.md` for separate static, profile, and live gates.

## Startup commands

Linux/WSL:

```sh
python3 scripts/bootstrap_python.py
python3 scripts/python_env.py check --strict
python3 scripts/python_env.py run scripts/research_state.py validate
```

Windows PowerShell: replace `python3` with `py -3.12` in each command.
`setup_research.py init` is optional when `config/local.env` already exists;
it only creates a missing local configuration and preserves existing values.
If preflight fails, repair the environment or binding, then rerun validation.

## First transaction command

Run this only in the first research session after reading the frontier and
readiness gates:

```sh
python3 scripts/python_env.py run scripts/research_state.py begin \
  --transaction-id TX-0005 \
  --frontier-id Q-0001 \
  --next-action "Identify candidate vanilla quest/event level gates and state H1/H2 discriminants before source inspection."
```

In Windows PowerShell, use `py -3.12` in place of `python3`.

## Initial Codex prompt

```text
Begin the first deep Skyrim AE glitch-research session only if
`docs/HARNESS_READINESS.md` records passing strict persistent Python 3.12,
existing GOG Ghidra, and research-state gates. If a preflight fails, run the
documented bootstrap or local-configuration repair and recheck it first.
Report any remaining blocker with its evidence. The current STATE.md and
FRONTIER.json identify the selected question and verified local capabilities.

Read AGENTS.md, NORTH_STAR.md, STATE.md, ROADMAP.md, research/FRONTIER.json,
research/EVIDENCE_MODEL.md, protocols/TOOL_ROUTING.md, and
docs/HARNESS_READINESS.md. Load only skills and source documents relevant to
the selected question.

Start with P0 OBJ-1 / Q-0001: identify which candidate level-gated vanilla
quest or encounter has the strongest tractable evidence for its initiation
transition. Treat the retained DA14 >=14 scan and UESP prerequisite as leads,
not proof of the native start gate. Keep the rival models explicit:
(H1) a level predicate is checked at one start transition; (H2) it is checked
later or repeatedly across aliases, dialogue, story-manager, or encounter
transitions. State a discriminating prediction for each before choosing the
cheapest reliable source. If another P0 item now has higher expected
information gain, record why and select it instead.

Use the read-only plugin reader for explicit file-level observations. For
native xEdit fields in the five official masters, use:
`python3 scripts/python_env.py run tools/xedit_bridge.py native-query
--signature QUST --plugin Skyrim.esm --editor-id <EditorID>`.
This opens configured SSEView through the recovered original helper and
returns native fields plus the exact loaded-file inventory. It uses the
official-master-only read-only `.local` Data view and does not require MO2.
`file-records` is a separate direct TES4 parser route. The five-master native
view reports winners only within those masters. For profile-specific winners
or negative findings, resolve the target's complete actual load order; when
MO2 manages that target, use its selected profile's explicit `plugins.txt`.
Do not infer a profile winner from an incomplete order.

For native code, use the configured existing GOG project via
`GHIDRA_PROJECT_REP_PATH` and `ghidra-project-research`. Its adapter uses the
existing project read-only with `-process -noanalysis -readOnly`; it does not
import or reanalyze a binary. Keep GOG 1.6.1179.0 identity and hash separate
from the installed Steam runtime 1.6.1170.0. Never transfer a GOG address to
Steam without independent mapping.

Installed SKSE file identity is verified, but live game process, Observer
deployment/load, handshake, event, snapshot, and DevBench connection are not
verified. Do not claim live capability. Live SKSE is not required for static
research. Do not launch Skyrim or use console interventions for this static
question; if a clean live test later becomes necessary, write its exact
baseline and observation protocol and continue independent static work.

For every transaction, preserve raw output under ignored `.local/`, record
command, build/input hash, coverage, evidence IDs, and uncertainty; update
CLAIMS, CONTRADICTIONS, FRONTIER, SESSION_LOG, STATE, and RECOVERY as warranted.
Keep diagnostic_intervention, vanilla_candidate, vanilla_reproduction, and
mechanism_inference separate. Never infer a negative from missing or partial
coverage.

After each completed or blocked item, re-evaluate the frontier and continue
with the next independent high-information item. Keep OBJ-1 and OBJ-2 P0;
after each three completed core investigations, perform cross-domain synthesis,
and use at most one bounded breadth item before returning to P0. Test multiple
causal models, record negative results and contradictions, and revisit model
predictions when evidence disagrees.

Before each context or CLI boundary, write the exact next action to STATE.md,
FRONTIER.json, and SESSION_LOG.md. At a fresh session, resume from those files
without requesting a recap. Recovery is a continuation step, not a stop
condition. Do not install or rebuild native tools; use the configured local
bindings. Do not run a time-based supervisor or claim uninterrupted Codex
execution.

Continue until the current tractable frontier has been exhausted, independent
questions have been reconsidered, and the next exact user action or frontier
decision is recorded. Do not claim a glitch result unless evidence meets the
repository's reproduction and provenance rules.
```

The setup session prepares this handoff only and does not execute Q-0001.
