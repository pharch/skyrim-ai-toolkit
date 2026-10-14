# Local tool path verification

Actual machine paths and candidate binary hashes remain in ignored
`.local/research-paths.toml` and `config/local.env`. The checked-in example
contains placeholders. Use `python3 scripts/python_env.py run -m scripts.local_paths
doctor` for status-only output; it does not print configured path values.

| Candidate | What was checked | Result |
|---|---|---|
| Skyrim AE executable | Two configured candidates exist; private hashes remain local. | **Blocked:** the Python preflight could not read ProductVersion through the WSL Windows bridge. Runtime remains unknown. |
| Active profile order | `PLUGINS_TXT` candidate and required-master policy inspected. | **Blocked:** no selected profile's complete `plugins.txt` is configured or verified. |
| xEdit/SSEEdit | Configured executable candidate exists. | **Blocked:** no call was made because host, target runtime, and complete profile gate are unverified. |
| Ghidra | Home/headless candidate and standard launcher paths exist. | **Blocked:** Java is unavailable in this shell; no analysis was run. |
| CommonLibSSE-NG | Source directory and CMake project candidates exist. | **Blocked:** CMake is unavailable; no build or target navigation was run. |
| Apocrypha | Local source and ignored SQLite index are present. | **Verified locally:** 60,873 messages match the declared count. The doctor and aggregate-only search returned without emitting message text or identifiers. |
| UESP | Local compressed XML source and ignored SQLite index are present. | **Verified locally:** import has 475,228 pages, including 17,520 custom `Skyrim` namespace pages. Real local search/page/revision retrieval responds. Acquisition URL, license, and completeness remain unknown. |

Path existence is not compatibility evidence. No xEdit, Ghidra, live-game,
save-write, plugin-edit, or original-game-file operation was performed.
