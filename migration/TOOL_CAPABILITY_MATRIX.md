# Python tool capability matrix

All checked-in agent entrypoints under `tools/` and `scripts/` are Python. Use
`python3 scripts/python_env.py run ...` to select the named Conda environment
when it exists. The retired Node, shell, and Java launchers are preserved only
as historical source under `archived_tools/legacy_nonpython/`.

| Domain | Python response tested | Readiness and limit |
|---|---|---|
| AE executable/profile gate | `python3 scripts/python_env.py run tools/ae_preflight.py --probe-executable` returns a structured fail-closed response. | **BLOCKED_EXTERNAL:** this WSL session cannot retrieve the Windows executable ProductVersion; the complete selected profile `plugins.txt` is not configured. No SSEEdit or live call is allowed. |
| Plugin record inspection | `python3 scripts/python_env.py run tools/plugin_reader.py doctor` and synthetic record/compression fixtures. | **PASS (limited parser):** standard-library TES4 file reader responds and is read-only. It does not load the active order or select winning overrides. |
| SKSE co-save | `python3 scripts/python_env.py run tools/cosave-info.py <copy.skse>`; domain doctor uses a synthetic fixture. | **PASS (fixture only):** one synthetic chunk parsed with 100% fixture coverage. No real co-save or live SKSE handshake was tested. |
| Ghidra | `python3 scripts/python_env.py run tools/domain_doctor.py`. | **BLOCKED_EXTERNAL:** doctor responds; configured installation/headless paths exist, but Java is unavailable and no analysis ran. |
| CommonLibSSE-NG | `python3 scripts/python_env.py run tools/domain_doctor.py`. | **BLOCKED_EXTERNAL:** doctor responds; source and CMake project candidates exist, but CMake is unavailable and no build ran. |
| SSEEdit/xEdit | `python3 scripts/python_env.py run tools/domain_doctor.py`; narrow file parsing uses `tools/plugin_reader.py`. | **BLOCKED_EXTERNAL:** an executable candidate exists, but this is Linux and neither exact AE ProductVersion nor the full active order is verified. No SSEEdit call ran. |
| UESP local corpus | `python3 scripts/python_env.py run -m tools.uesp doctor|search|page|related ...`. | **PASS (local retrieval):** doctor, search, and revision-cited `Skyrim:Karstaag` page lookup responded (revision 3629292). Corpus provenance, license, and completeness remain unverified. |
| Apocrypha local corpus | `python3 scripts/python_env.py run -m tools.apocrypha doctor|search|context ...`. | **PASS (private local index):** doctor and aggregate-only search responded; indexed and declared totals are 60,873. Search content/identifiers remain private and untrusted. |
| Local Python environment | `python3 scripts/python_env.py check`; create with `conda env create -f environment.yml`. | **PARTIAL:** Python 3.12.3 fallback is available; environment manifest is present, but Conda is absent and the named environment is not installed in this shell. |
| Raw/heavy artifact boundary | `python scripts/pre_push_audit.py`. | Run the final audit before review. Local corpora stay in ignored `.local/`; tracked findings are summarized in Markdown/JSON. |

Linux fixture checks do not validate Windows MO2/xEdit behavior, Ghidra
analysis, CommonLib builds, or in-game AE behavior. Current target and profile
verification are prerequisites for those operations.
