# Research tool entrypoints

Normal tool execution uses the strict Python 3.12 environment dispatcher. Bootstrap and invocation rules are in [`docs/LOCAL_RUNTIME_CONTRACT.md`](../docs/LOCAL_RUNTIME_CONTRACT.md); ignored `config/local.env` is the only machine-path registry.

| Route | Entrypoint | Scope |
|---|---|---|
| Existing GOG Ghidra project | `tools/ghidra_probe.py` | Read-only function/xref/disassembly/decompilation; no import or reanalysis. |
| Native xEdit/SSEView | `tools/xedit_bridge.py native-query` | Native record fields in the guarded five-official-master scope. |
| Direct plugin parsing | `tools/xedit_bridge.py file-records` | TES4 file-level fields; separate from xEdit and winner resolution. |
| AE target verification | `tools/ae_preflight.py` | Executable ProductVersion and, when selected, complete target order. |
| SKSE identity | `tools/skse_probe.py` | Installed files only; no game process connection or telemetry. |
| Local UESP / Apocrypha | `python -m tools.uesp` / `python -m tools.apocrypha` | Local source lookup; preserve source revision/message provenance and privacy. |
| Research state | `scripts/research_state.py` | Frontier/evidence/transaction/recovery integrity. |

Tools must be invoked through `python3 scripts/python_env.py run ...` on Linux/WSL or `py -3.12 scripts/python_env.py run ...` in Windows PowerShell. Tool existence is not proof of an observed result; record exact inputs, build identity, scope and raw artifact hash.
