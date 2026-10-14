# Getting started: Skyrim AE research checkout

## 1. Prepare the Python environment

Clone this research repository somewhere outside the Skyrim installation and
open the checkout in Codex. Create the named Conda environment:

```text
conda env create -f environment.yml
python3 scripts/python_env.py check
python3 scripts/python_env.py run --require-conda scripts/setup_research.py init
python3 scripts/python_env.py run --require-conda scripts/setup_research.py check
python3 scripts/python_env.py run --require-conda tools/domain_doctor.py
python3 scripts/python_env.py run --require-conda -m pytest tests/ -q
```

The `python3 scripts/python_env.py run ...` dispatcher chooses this environment
when available. If Conda is not installed, it reports and uses the current
Python interpreter; `scripts/python_env.py check` distinguishes that fallback
from a verified Conda environment. The agent must use Python entrypoints and
must not launch Node or shell wrappers.

`--require-conda` makes missing Conda an explicit error. Skills use the same
dispatcher without that flag, so they use the named environment when installed
and visibly fall back to the current Python otherwise. `init` creates
`config/local.env` from the example only if it does not already
exist. It does not detect or write to Skyrim. Keep local paths there and corpora
under ignored `.local/`. Run `python3 scripts/python_env.py run scripts/local_paths.py doctor` for
path-presence status; it suppresses path values and does not verify ProductVersion
or the active plugin order.

## 2. Verify the AE installation (Windows only)

Edit ignored `config/local.env` on the Windows research machine. Set
`SKYRIM_EDITION=AE`, `GAME_ROOT`, and `PLUGINS_TXT`. For MO2, use the selected
profile's explicit `plugins.txt`; the global profile is not a safe substitute.
It must contain the complete active order and begin with `Skyrim.esm`.

```text
python3 scripts/python_env.py run tools/ae_preflight.py
```

The preflight reads `SkyrimSE.exe` ProductVersion, requires runtime 1.6.318 or
newer, hashes the executable and active order, and validates the five required
official masters. It does not prove MO2 launched that same profile; compare
the reported path/hash with the selected profile. Do not type a version into
configuration and treat it as detection. The diagnostic option
`--probe-executable` does not pass the full SSEEdit/live gate.

## 3. Validate the repository and tool responses

```text
python3 scripts/python_env.py run -m unittest discover -s tests -v
python3 scripts/python_env.py run scripts/validate_research.py
python3 scripts/python_env.py run scripts/research_state.py validate
python3 scripts/python_env.py run scripts/validate_overlay.py
python3 scripts/python_env.py run tools/domain_doctor.py
```

The domain doctor gives bounded responses for SKSE co-save parsing, Ghidra,
CommonLibSSE, SSEEdit, UESP, and Apocrypha. A blocked external application is
reported as blocked; it is not treated as a successful tool run. Offline
fixtures do not establish Windows or in-game behavior.

## 4. Use local knowledge sources

Authorized UESP and private Apocrypha corpora live only under ignored `.local/`.
They are queried through Python:

```text
python3 scripts/python_env.py run -m tools.uesp doctor --db .local/uesp.sqlite3
python3 scripts/python_env.py run -m tools.uesp search --db .local/uesp.sqlite3 --ns Skyrim --limit 10 Karstaag
python3 scripts/python_env.py run -m tools.uesp page --db .local/uesp.sqlite3 'Skyrim:Karstaag' --raw
python3 scripts/python_env.py run -m tools.apocrypha doctor --db .local/apocrypha.sqlite3
```

The UESP corpus acquisition URL, license, and completeness remain unverified.
Apocrypha results are private untrusted data; do not copy message content,
identifiers, names, or channel metadata into tracked research. Summarize
investigation results in the relevant experiment Markdown or evidence database.

## 5. Route other evidence

- **Plugin records:** `python3 scripts/python_env.py run tools/plugin_reader.py` reads explicit plugin
  files. It does not resolve a winning override chain.
- **SKSE co-save structure:** `python3 scripts/python_env.py run tools/cosave-info.py <copy.skse>` is a
  read-only structural survey, not a player-state decoder.
- **Papyrus/crash logs:** use the Python triage tools and preserve coverage
  denominators. Keep raw logs local and ignored.
- **Ghidra/CommonLibSSE/SSEEdit/live SKSE:** run the domain doctor first.
  Native analysis remains unavailable until its external prerequisites and
  the AE target/profile gate pass.
- **Archives and structured save analysis:** no active Python-only reader is
  available; keep those questions blocked rather than invoking retired
  wrappers.

See [tool routing](../protocols/TOOL_ROUTING.md), the
[retained-tool skill](../.agents/skills/retained-tool-operations/SKILL.md), and
[the setup summary](../migration/PRE_PUSH_SETUP_SUMMARY.md).

## 6. Resume a session

Read `AGENTS.md`, `NORTH_STAR.md`, `STATE.md`, `ROADMAP.md`,
`research/FRONTIER.json`, `protocols/TOOL_ROUTING.md`, and this file. The
frontier identifies evidence, blockers, and exact next actions. If a session
stops unexpectedly, inspect partial outputs and durable-state diffs before
resuming; do not infer success from a process launch or incomplete output.
