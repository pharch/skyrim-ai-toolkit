# Skyrim AE research tool routing

The user starts or resumes work with the natural-language prompt in
`docs/RESEARCH_START_PROMPT.md`. Read `AGENTS.md` and
`docs/LOCAL_RUNTIME_CONTRACT.md`; the command lines below are internal Codex
operations. Bootstrap or repair the current host environment before research.
On Windows use `py -3.12`; on Linux/WSL use `python3`. Then route every
research command through the strict dispatcher:

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

For vanilla official-master xEdit, the `native-query` wrapper validates the
executable's ProductVersion and the generated five-master list internally;
MO2 is not required. For profile-specific xEdit or live-game claims, validate
the actual executable and complete target order:

    python3 scripts/python_env.py run tools/ae_preflight.py

An explicit profile directory and `plugins.txt` are required only when the
target load order is MO2-managed. An empty, partial, stale, or unverified order
cannot support profile-specific winning-record or negative claims. A
disposable profile has separate keys and a separate gate, used only when that
test lane is selected:

    python3 scripts/python_env.py run tools/ae_preflight.py --test-profile

A generated five-master list is the exact vanilla scope for native inspection:

    python3 scripts/python_env.py run tools/ae_preflight.py --scoped-five-master <session>/plugins.txt

It verifies the generated Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm,
and Dragonborn.esm list; it does not claim to represent any user profile.

## Route by evidence type

| Evidence need | Entry point | Limit |
|---|---|---|
| Current setup/readiness | python3 scripts/python_env.py run scripts/harness_doctor.py all | Read-only readiness checks; never deploys, launches Skyrim or selects an xEdit record. It may run the existing GOG query only after ProductVersion and Address Library checks pass. |
| Local bindings | python3 scripts/python_env.py run scripts/local_paths.py doctor | Reads config/local.env and reports presence without printing values. |
| xEdit helper bindings | python3 scripts/python_env.py run tools/xedit_bridge.py doctor | Stages eight configured source/template files into ignored .local and checks helper bindings. It does not launch SSEView. |
| Bridge record retrieval (direct parser) | python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature QUST --plugin Skyrim.esm --editor-id CreatureDialogueWerewolf | Read-only TES4 record retrieval through the documented bridge. It does not launch native xEdit or resolve winning overrides. |
| Scoped xEdit view preparation | python3 scripts/python_env.py run tools/xedit_bridge.py prepare | Writes a five-master SSEView session under ignored .local; launch is false. |
| Native xEdit record export | python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature QUST --plugin Skyrim.esm --editor-id dunDA14MorvunskarQST (or `--signature INFO --plugin Skyrim.esm --form-id 00095585`) | Launches configured SSEView 4.1.5f in `-view`; scopes `-D:` to a `.local` official-master view; runs the original hotkey Apply Script walker; exports decoded fields and loaded-file inventory. Choose exactly one of EditorID or an eight-digit source-plugin-local FormID; FormID lookup supports nested records without EditorIDs. No MO2 profile is needed. |
| Existing GOG static project | python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x... --timeout 600; add `--list-call-edges` for a direct/indirect call-site census, `--pointer-table-rva 0x... --pointer-count N` for a bounded pointer table, `--vtable-rtti-rvas 0x...,0x...` for bounded MSVC vtable identity/subobject-offset capture, `--address-rva 0x...` for a code-address context, or `--search-displacement 0x...` for a whole-program analyzed-memory-operand scan | Existing GOG project only; adapter uses -process -noanalysis -readOnly and checks GOG executable identity first. The census lists every direct edge and unresolved indirect call site without decompiling every target; direct-callee decompilation remains capped at eight. Pointer-table output lists references to each entry, preserves each raw pointer and only labels a target when it belongs to an analyzed function. Vtable RTTI output is bounded to at most 32 explicitly supplied table RVAs and reports the class descriptor identity and subobject offset. Address-context output retains references and a bounded instruction window where no function boundary exists. Displacement scans report scan markers and bounded candidate writer/method output; inspect caps and per-run metadata. |
| Named CommonLib relocation | python3 scripts/python_env.py run tools/address_library_probe.py --symbol Namespace::Name [--vtable-index N] | Resolves a GOG-specific RVA from CommonLib and the matching GOG Address Library. The optional zero-based index selects a distinct subobject vtable from a multi-entry `VTABLE::Type` declaration. Never transfer it to Steam without mapping evidence. |
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
second user-edited source of truth. Native `prepare` and `native-query` create
an ignored Data view containing hash-verified, read-only copies of the five
configured official masters and any matching vanilla string tables; it
excludes `Skyrim.ccc`, CC, and user plugins. The configured game Data path is unchanged. This avoids the
observed xEdit behavior of auto-loading CC and user plugins from the full Data
folder despite the generated five-entry `plugins.txt`.

`native-query` is the reproducible Codex interface. It uses the original
`skyrim_tool.py prepare-xedit` arguments and generated `launch.ps1`, the
original UIAutomation status helper and focused Ctrl+Alt+F9 dispatcher, and a
session-scoped `-S:` query script. The script reuses the field walker/schema
from original `scripts/xedit/export-records.pas`; it executes its targeted
lookup in `Initialize`, following original `investigation-export.pas`, so no
record-tree selection is needed. Only known first-run/module dialogs are
handled. The script writes an exact loaded-file inventory, status marker, and
native TSV; Python validates the record identity, fields, hashes, and five
master scope before saving structured JSON and a local doctor receipt.

The query target is selected by exactly one of `--editor-id` or `--form-id`.
The FormID is eight hexadecimal digits local to the requested source plugin
and is resolved with xEdit's `RecordByFormID`; use it for nested records such
as INFO records with no EditorID. The bridge verifies the exported FormID and
signature against the request before accepting the result.

The reproduced query is `Skyrim.esm` QUST `dunDA14MorvunskarQST`, form
`000427A0`, with 149 field rows and stage indices 20 and 100. The stage 100
flags include `Shut Down Stage=1`. Its native winning plugin is Skyrim.esm
within the five-master view only. These observations are preserved as EV-0207,
the compact fixture at `tests/fixtures/xedit/native_quest_smoke.json`, and raw
TSV/UI captures below ignored `.local/`. Direct `file-records` parsing remains
a separate TES4 parser and must not be labeled an xEdit query. A profile
specific winner still requires a complete order from the actual target; if
MO2 manages that target, configure and preflight its explicit profile list.

## GOG and runtime separation

The existing GOG analysis executable/project is separate from the live Steam
runtime. The remembered 0x14C020 example is specific to GOG AE 1.6.1179.0.
Fresh WSL GOG query evidence is recorded in
[`docs/HARNESS_READINESS.md`](../docs/HARNESS_READINESS.md). When the configured
project is on `/mnt`, the adapter copies that existing project to the
WSL-native path in `GHIDRA_PROJECT_CACHE_WSL`; this is necessary because the
WSL-mounted checkout cannot provide Ghidra's project lock. The query remains
`-process -noanalysis -readOnly`, uses the configured source project, and never
imports or reanalyzes a binary. EV-0165–EV-0167 remain historical unless a
current query artifact independently supports a claim.

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
