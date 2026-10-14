# Current agent-tool audit

Current tools are Python entrypoints. The prior Node, shell, and Java launchers
and their retired tests are stored under
[`archived_tools/legacy_nonpython/`](archived_tools/legacy_nonpython/README.md)
and must not be called by a skill.

| Entry point | Purpose | Current evidence | Boundary |
|---|---|---|---|
| `tools/ae_preflight.py` / `tools/ae_target.py` | Verify executable ProductVersion and complete active plugin order. | Six Python policy fixtures pass; direct probe fails closed when ProductVersion is unavailable. | Windows executable identity and active order are still unverified. |
| `tools/plugin_reader.py` | Read TES4 headers, record inventory, and one-plugin record fields. | Three synthetic fixtures pass, including a compressed record. | It does not resolve winning overrides or replace xEdit. |
| `tools/cosave-info.py` | Read-only SKSE co-save structure survey. | Synthetic domain-doctor fixture returns one chunk and full fixture coverage. | Real co-save and live SKSE bridge were not tested. |
| `tools/domain_doctor.py` | Bounded readiness/query checks for six requested domains. | Produces a structured response for SKSE, Ghidra, CommonLibSSE, SSEEdit, UESP, and Apocrypha. | Native tools are reported honestly; doctor does not invoke them. |
| `tools/uesp/` and `tools/apocrypha/` | Query ignored local SQLite corpora. | Local doctor and query paths respond; output policy separates UESP citations from private Apocrypha text. | Corpus acquisition provenance/license remain unverified for UESP. |
| `scripts/python_env.py` | Dispatch to `skyrim-ae-research` with Conda when installed. | Dispatcher fixtures pass; `run -m` now forwards arguments. | Conda is missing in this shell; current Python fallback is explicit. |
| `tools/papyrus-triage.py`, `tools/crash-triage.py` | Analyze supplied logs/dumps without modifying inputs. | Python CLI entrypoints are documented. | No user log/dump or live failure was supplied for a real-file example. |

No current native analysis or game integration is claimed. See
[`TOOL_CAPABILITY_MATRIX.md`](TOOL_CAPABILITY_MATRIX.md) for domain-specific
status and [`PRE_PUSH_SETUP_SUMMARY.md`](PRE_PUSH_SETUP_SUMMARY.md) for the
reviewer status.
