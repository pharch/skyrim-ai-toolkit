# Agent skill capability matrix

All 12 discoverable Codex skills use Python entrypoints or research documents;
none calls the retired Node/shell/Java launchers. `scripts/validate_overlay.py`
checks skill metadata, links, and the active Python tool surface. That check
does not establish native Windows or in-game compatibility.

| Skill | Python route / research surface | Current result and limit |
|---|---|---|
| `ae-target-verification` | `python3 scripts/python_env.py run tools/ae_preflight.py` | Python fixtures pass; real ProductVersion and full active order remain unverified in WSL. |
| `archive-source-discovery` | `python3 scripts/python_env.py run tools/domain_doctor.py`; source methods in `protocols/TOOL_ROUTING.md` | Python status response works. No active Python BSA extractor is available; archive operations are blocked until an audited Python implementation exists. |
| `esp-record-research` | `python3 scripts/python_env.py run tools/plugin_reader.py inventory|record ...` | Synthetic parser fixtures pass. This reads one plugin and does not calculate winning overrides or invoke SSEEdit. |
| `retained-tool-operations` | `python3 scripts/python_env.py run tools/domain_doctor.py` plus Python readers/triage tools | Six-domain response works. Ghidra, CommonLibSSE, SSEEdit, and live SKSE calls are not claimed as executed. |
| `save-state-forensics` | `python3 scripts/python_env.py run tools/cosave-info.py <copy.skse>` | Synthetic SKSE fixture passes. No real save/co-save parser or Java ReSaver launcher is active. |
| `skyrim-quest-gate-research` | `experiments/EXP-0008-quest-gate-continuity/`, UESP route, and gated plugin reader | Hypothesis/protocol is ready; no current winning record or in-game gate result. |
| `skyrim-armor-xp-research` | `experiments/EXP-0009-*` and `EXP-0010-*`, plus Python source readers | Rival models and observables are recorded; verified hit, protection, and XP deltas remain pending. |
| `skyrim-discriminating-experiments` | `research/FRONTIER.json`, experiment templates, `python3 scripts/python_env.py run scripts/validate_research.py` | Structural/data checks are available; no gameplay experiment is implied by validation. |
| `skyrim-cross-domain-synthesis` | `research/KNOWLEDGE_GRAPH.md` and `research/FRONTIER.json` | Evidence-linked static graph and successor questions are present; engine mechanisms remain source-bounded. |
| `skyrim-source-verification` | `python3 scripts/python_env.py run -m tools.uesp ...`; `python3 scripts/python_env.py run -m tools.apocrypha ...` | Both local query paths respond. Community output is private/untrusted; UESP provenance is incomplete. |
| `uesp-grounding` | `python3 scripts/python_env.py run -m tools.uesp doctor|search|page|related ...` | Local query and revision citation respond; page counts do not prove a complete wiki mirror. |
| `apocrypha-grounding` | `python3 scripts/python_env.py run -m tools.apocrypha doctor|search|context ...` | Aggregate doctor/search respond; keep individual message text/IDs local and treat as untrusted. |

The active skills are usable for offline research and readiness checks. Native
analysis and runtime work remains conditional on the blockers recorded in
[`TOOL_CAPABILITY_MATRIX.md`](TOOL_CAPABILITY_MATRIX.md).
