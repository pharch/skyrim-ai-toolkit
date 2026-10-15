# First deep autonomous research session

This is a prepared first-research prompt, not an instruction to bypass failed
setup gates. Use it in a new interactive Codex session at the repository root
only after the strict Python 3.12 `.venv`, existing GOG Ghidra query, and
research-state validation pass. Check `docs/HARNESS_READINESS.md` first.

## Exact first command

Windows PowerShell:

```powershell
& .\.venv\Scripts\python.exe scripts/python_env.py run scripts/research_state.py validate
```

Linux/WSL:

```sh
python3 scripts/python_env.py run scripts/research_state.py validate
```

If it fails, repair the recovery state from `STATE.md`,
`research/SESSION_LOG.md`, `research/FRONTIER.json`, and
`research/RECOVERY.json`; preserve evidence and continue once valid.

## Initial Codex prompt

```text
Begin the first deep Skyrim AE glitch-research session only if
`docs/HARNESS_READINESS.md` records passing strict Python 3.12, GOG
function/xref/decompilation, and research-state gates. If any of those gates
does not pass, stop before bounty analysis and report the exact blocker. The
current STATE.md / FRONTIER.json define the verified local capabilities.
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
existing GOG Ghidra project for static native code. Preserve GOG
1.6.1179.0 identity and hash separately from Steam runtime 1.6.1170.0. Never
transfer a GOG address to Steam without independent mapping. The selected MO2
profile and full-order xEdit winner route remain unavailable. The approved
SSEView opened and completed background loading for an isolated five-official-master
`-view` session (EV-0184/0185/0189), and the exact authoritative bridge/config
replay plus fresh post-edit validation passed (EV-0191); UI Automation exposed
no safe record
selector and no record was queried/exported, so do not use it for winners or
profile-level negative claims. An Observer DLL matching Steam 1.6.1170 was freshly built and
a no-launch session manifest was prepared (EV-0186–0188); it remains staged
under `.local`, with no deployment or handshake. Do not start another xEdit
instance or launch Skyrim for this research session. If live access is later
needed, write the exact profile/save/deployment approval protocol and continue
with independent static work.

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
