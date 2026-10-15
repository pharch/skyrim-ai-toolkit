# Agent skill capability matrix

All active repository Codex skills use tested Python entrypoints or research documents;
none calls the retired Node/shell/Java launchers. `scripts/validate_overlay.py`
checks skill metadata, links, and the active Python tool surface. That check
does not establish native Windows or in-game compatibility.

| Skill | Python route / research surface | Current result and limit |
|---|---|---|
| `ae-target-verification` | `python3 scripts/python_env.py run tools/ae_preflight.py` | Executable ProductVersion and a scoped five-master order were verified through approved Windows PowerShell (EV-0184); selected full MO2 order remains unknown. |
| `archive-source-discovery` | `python3 scripts/python_env.py run tools/domain_doctor.py`; source methods in `protocols/TOOL_ROUTING.md` | Python status response works. No active Python BSA extractor is available; archive operations are blocked until an audited Python implementation exists. |
| `esp-record-research` | `plugin_reader.py inventory|record`; authoritative `skyrim` xEdit bridge `doctor`/`prepare-xedit` and generated `-view` launcher | Five-master bridge launch and background load passed (EV-0184–0185/0189); UIA exposes no record selector, so no export or active-profile winner query. |
| `retained-tool-operations` | `tools/domain_doctor.py`, Python readers/triage, verified bridge/build routes | Ghidra/Address Library queries pass; SSEView launch and completed five-master load plus Observer build/prepare pass (EV-0184–EV-0189); full-profile winners and live SKSE handshake remain unavailable. |
| `save-state-forensics` | `python3 scripts/python_env.py run tools/cosave-info.py <copy.skse>` | Synthetic SKSE fixture passes. No real save/co-save parser or Java ReSaver launcher is active. |
| `skyrim-quest-gate-research` | `experiments/EXP-0008-quest-gate-continuity/`, UESP route, and gated plugin reader | Hypothesis/protocol is ready; no current winning record or in-game gate result. |
| `skyrim-armor-xp-research` | `experiments/EXP-0009-*` and `EXP-0010-*`, plus Python source readers | Rival models and observables are recorded; verified hit, protection, and XP deltas remain pending. |
| `skyrim-discriminating-experiments` | `research/FRONTIER.json`, experiment templates, research validator, and Observer prepare-only route | Structural checks pass; Observer build and prepare-only manifest are verified (EV-0186/0188), but no live gameplay experiment or handshake is established. |
| `skyrim-cross-domain-synthesis` | `research/KNOWLEDGE_GRAPH.md` and `research/FRONTIER.json` | Evidence-linked static graph and successor questions are present; engine mechanisms remain source-bounded. |
| `skyrim-source-verification` | `python3 scripts/python_env.py run -m tools.uesp ...`; `python3 scripts/python_env.py run -m tools.apocrypha ...` | Both local query paths respond. Community output is private/untrusted; UESP provenance is incomplete. |
| `uesp-grounding` | `python3 scripts/python_env.py run -m tools.uesp doctor|search|page|related ...` | Local query and revision citation respond; page counts do not prove a complete wiki mirror. |
| `apocrypha-grounding` | `python3 scripts/python_env.py run -m tools.apocrypha doctor|search|context ...` | Aggregate doctor/search respond; keep individual message text/IDs local and treat as untrusted. |

The active skills are usable for offline research and readiness checks. Native
analysis and runtime work remains conditional on the blockers recorded in
[`TOOL_CAPABILITY_MATRIX.md`](TOOL_CAPABILITY_MATRIX.md).
