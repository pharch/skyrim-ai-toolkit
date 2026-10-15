# Skyrim AE research tool routing

Read docs/LOCAL_RUNTIME_CONTRACT.md first. Bootstrap or repair the current
host environment before research. On Windows use `py -3.12`; on Linux/WSL use
`python3`. Then route every research command through the strict dispatcher:

    python3 scripts/bootstrap_python.py
    python3 scripts/setup_research.py init  # preserves an existing local config
    python3 scripts/python_env.py check --strict
    python3 scripts/python_env.py run <script-or-module>

PowerShell forms:

    py -3.12 scripts/bootstrap_python.py
    py -3.12 scripts/setup_research.py init
    py -3.12 scripts/python_env.py check --strict
    py -3.12 scripts/python_env.py run <script-or-module>

The bootstrap can run before a venv exists and repairs the persistent
`.local/python-envs/<host>` environment from pinned `requirements.txt`. A
failed preflight triggers bootstrap repair, then a fresh strict check. The
dispatcher never runs research children from system Python, Conda, or another
ambient environment. Do not run research tools directly as a substitute.
Local tool paths come only from ignored config/local.env. The old
.local/research-paths.toml is retired.

## Runtime and profile gates

Before native xEdit or live-game access, validate the executable's actual
ProductVersion and selected full MO2 order:

    python3 scripts/python_env.py run tools/ae_preflight.py

The profile directory and its explicit plugins.txt are mandatory. A global,
empty, partial, or stale plugin list cannot support winning-record or negative
claims. A disposable profile has separate keys and a separate gate:

    python3 scripts/python_env.py run tools/ae_preflight.py --test-profile

A generated five-master view list has a distinct diagnostic-only scope:

    python3 scripts/python_env.py run tools/ae_preflight.py --scoped-five-master <session>/plugins.txt

It proves only that the generated Skyrim.esm, Update.esm, Dawnguard.esm,
HearthFires.esm, and Dragonborn.esm list is complete; it does not verify MO2's
selected order.

## Route by evidence type

| Evidence need | Entry point | Limit |
|---|---|---|
| Current setup/readiness | python3 scripts/python_env.py run scripts/harness_doctor.py all | Read-only readiness checks; never deploys, launches Skyrim or selects an xEdit record. It may run the existing GOG query only after ProductVersion and Address Library checks pass. |
| Local bindings | python3 scripts/python_env.py run scripts/local_paths.py doctor | Reads config/local.env and reports presence without printing values. |
| xEdit helper bindings | python3 scripts/python_env.py run tools/xedit_bridge.py doctor | Stages eight configured source/template files into ignored .local and checks helper bindings. It does not launch SSEView. |
| Bridge record retrieval (direct parser) | python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature QUST --plugin Skyrim.esm --editor-id CreatureDialogueWerewolf | Read-only TES4 record retrieval through the documented bridge. It does not launch native xEdit or resolve winning overrides. |
| Scoped xEdit view preparation | python3 scripts/python_env.py run tools/xedit_bridge.py prepare | Writes a five-master SSEView session under ignored .local; launch is false. |
| Native xEdit record export | Prepare, pass the matching AE preflight, then use the generated launch.ps1 on Windows and manually select a record before Apply Script | The selection-based exporter/UI path is not reproduced in the cold-start session. No safe record-tree selection automation is available. |
| Existing GOG static project | python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x... --timeout 600 | Existing GOG project only; adapter uses -process -noanalysis -readOnly and checks GOG executable identity first. |
| Named CommonLib relocation | python3 scripts/python_env.py run tools/address_library_probe.py --symbol Namespace::Name | Resolves a GOG-specific RVA from CommonLib and the matching GOG Address Library. Never transfer it to Steam without mapping evidence. |
| Installed SKSE identity | python3 scripts/python_env.py run tools/skse_probe.py | File/version identity only. Does not launch game, load plugin, connect, handshake, or observe game state. |
| Known Papyrus/BSA input | python3 scripts/python_env.py run tools/papyrus_pex.py extract DA14Script | Narrow base Misc BSA extraction and classic PEX 3.2 inspection. |
| Save/co-save structure | python3 scripts/python_env.py run tools/cosave-info.py <designated-copy.skse> | Structural parser; use designated disposable copies only. |
| UESP citation | python3 scripts/python_env.py run -m tools.uesp page --db .local/uesp.sqlite3 <title> --raw | Preserve page revision/URL; local dump provenance may remain unknown. |
| Private Apocrypha lead | python3 scripts/python_env.py run -m tools.apocrypha search --db .local/apocrypha.sqlite3 --summary-only <terms> | Keep text and stable IDs in ignored .local; treat as untrusted leads. |

## xEdit bridge contract

The tracked tools/xedit_bridge.py is the toolkit entrypoint. It reads only the
root ignored config/local.env, then copies the fixed helper/template list from
LEGACY_SKYRIM_REPO into ignored .local/xedit-authoritative-copy/ after
SHA-256 verification. The original source checkout remains read-only. The
helper copy's derived config is generated from canonical bindings, not a
second user-edited source of truth. Doctor/prepare/file-records retain raw
stdout and stderr under ignored .local/alignment/xedit-bridge/; helper calls
have a 120-second timeout.

The real native export interface remains incomplete: the Pascal exporter
expects a selected SSEView record and an Apply Script action. The current
automation cannot safely select a record from the UI tree. A file-parser result
must never be presented as an xEdit record query. Native SSEView cleanup is
manual: close the visible process normally and verify it exited. The helper
timeout does not supervise or kill an SSEView process.

## GOG and runtime separation

The existing GOG analysis executable/project is separate from the live Steam
runtime. The remembered 0x14C020 example is specific to GOG AE 1.6.1179.0.
The cold-start GOG address and Ghidra probes stopped before launch because this
WSL host could not read ProductVersion through its Windows PowerShell bridge.
See docs/HARNESS_READINESS.md for current evidence; historical EV-0165–EV-0167
do not count as a current-session reproduction.

## SKSE / Observer boundary

The Observer source docs describe bounded event and requested snapshot capture
to a session directory plus offline analysis. They explicitly say it does not
instrument native skill use, ActiveEffect lifetime, craft transactions, hit
routing, inventory ExtraData, perk/spell lists, or Story Manager state.
Installed files and a successful build are not evidence of a loaded plugin.
The current cold-start found no deployed DLL, selected disposable profile/list,
test save, game process, handshake, snapshot, or DevBench connection. Do not
start Skyrim from an unattended readiness run.

All failures and missing inputs are blockers, never evidence that a record,
function, event, or game state is absent. Linux/WSL validation does not
establish Windows MO2/SSEEdit behavior or in-game AE behavior.
