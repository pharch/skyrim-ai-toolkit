# Current harness state — 2026-10-15

## Setup result

The static research harness is ready. The persistent Python environment, GOG
Ghidra adapter, direct plugin parser, and recovered native xEdit/SSEView route
have passing evidence. Research recovery is idle and selects Q-0001 for the
next research session. This setup session did not begin bounty research or
launch Skyrim.

## Readiness gates

- `STATIC_RESEARCH_READY`: READY — Python 3.12 strict dispatch, configured GOG
  function/xref/decompilation, native official-five-master QUST export, local
  source access, and research-state validation pass.
- `PROFILE_OVERRIDE_RESOLUTION`: NOT_CONFIGURED — no MO2 profile is required
  for official masters. Profile-specific winners and negative findings require
  the target's actual complete load order.
- `SKSE_INSTALLED_IDENTITY`: PASS — installed files identify Steam AE
  1.6.1170.0.
- `SKSE_LIVE_OBSERVATION`: NOT_VERIFIED — no game process, deployed/loaded
  Observer, handshake, event, snapshot, or DevBench connection was observed.
  This is not a static-research blocker.

## Python environment

The current host is Ubuntu 24.04 / WSL2, CPython 3.12.3. Its persistent
ignored environment is `.local/python-envs/wsl`; `requirements.txt` is the
single pinned dependency source. EV-0203 records creation from an absent test
environment, reuse, and missing-package repair without recreating the active
environment. The latest strict check passes; 195 active pytest tests pass.
Use the bootstrap-first procedure in `docs/LOCAL_RUNTIME_CONTRACT.md`.

## Static tool evidence

- GOG `SkyrimSE.exe`: ProductVersion 1.6.1179.0; SHA-256
  `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`.
  Address Library maps `MagicItem::CalculateCost` to GOG RVA `0x14C020`.
- Existing GOG Ghidra project query: EV-0204 verifies function/RVA, incoming
  xref, disassembly, and decompilation in `-process -noanalysis -readOnly`
  mode. The configured source project was not imported, recreated, or
  reanalyzed.
- xEdit direct TES4 parser: EV-0205 returns raw file-level QUST data; it is
  separate from native xEdit and does not resolve a winner.
- Native SSEView: EV-0207 verifies a fresh SSEView 4.1.5f five-master load and
  149-field export for `dunDA14MorvunskarQST` (form `000427A0`). Stage 100 has
  `Shut Down Stage=1`. EV-0208 records the guarded discovery that direct game
  Data would auto-load CC/user plugins; the official query uses read-only
  copies in ignored `.local`.
- UESP and private Apocrypha local retrieval pass (EV-0170, EV-0171).

## Final readiness check

The final consolidated harness doctor is recorded by EV-0209. The active
readiness report is `docs/HARNESS_READINESS.md`; the canonical native command
and fresh-session QUST fixture are documented in
`docs/LOCAL_RUNTIME_CONTRACT.md` and `tests/fixtures/xedit/native_quest_smoke.json`.

## Research selection and exact next action

Recovery is idle; P0 `Q-0001` / `OBJ-1` is next. In the next research session,
run the documented bootstrap, strict Python check, and research-state
validation, read `docs/RESEARCH_START_PROMPT.md`, then begin `TX-0005` / `Q-0001`.
State rival gate models before source inspection. No bounty research was
started in this setup session.

## Historical xEdit recovery notes (superseded)

The following chronology records setup attempts before the successful native
query EV-0207. Its earlier next-action statements are historical; use the
current readiness and research-start instructions above.


Complete the user-requested xEdit integration recovery: execute the original
five-official-master SSEView workflow from a fresh command, retrieve a QUST
record's decoded fields through the original Pascal exporter, validate one
condition/stage relation, and record exact evidence. Do not start Q-0001
research in this setup task.

First canonical `native-query` attempt failed at initial UI-status parsing
(`xEdit UI status helper did not return JSON`). Inspect that attempt's private
raw output and launched process; repair the expected startup race and repeat
the complete fresh-session query.

The capture confirms the failure was a short startup race: a new SSEView PID
9904 appeared with an empty title, then became `SSEView 4.1.5f` seconds later;
the earlier session PID 8304 was already open. Continue the new process through
the guarded controller to validate the generated script, then make the
canonical runner wait for the window before parsing UIA output.

The configured xEdit executable has launched as `SSEView 4.1.5f` in the
isolated session. Its Windows UIA status helper completed but Python's default
UTF-8 decoder rejected a byte from Windows PowerShell output. Preserve raw
bytes, decode with replacement for inspection, verify the loaded masters, then
continue with the original Pascal export.

The byte-preserving UIA capture shows the main window title plus a `What's
New?` modal and the status `Loading active plugin list: <session>\plugins.txt`;
the session log is not present yet. Use the original dialog-dismiss helper for
this identified xEdit window, then check whether loading completes or requests
module selection.

The xEdit loader reports `Background Loader: finished` after accepting the
isolated official list. The original source confirms `-S:` supplies the script
directory, scans that directory for a `Hotkey:` line at startup, and routes the
hotkey through normal Apply Script execution. Next add a bounded native-query
entry point using the original field walker and hotkey bridge, then run it in a
new session and inspect the actual QUST fields.

The next implementation check is the focused xEdit wrapper suite. Correct any
template rendering or dispatch failures before running the fresh native query.

The focused `tests.test_xedit_bridge` suite now passes all seven tests. Exact
next action: run `python3 scripts/python_env.py run tools/xedit_bridge.py
native-query --signature QUST --plugin Skyrim.esm --editor-id DA14`, then inspect
the native TSV/JSON for real decoded fields and a condition/stage relationship.

The module-selection dialog is closed and SSEView remains responsive. Its
message pane reports `Background Loader: still building references...` after
the five-master list was accepted. Poll that same process until it reports
completion, then inspect the session log and native record route.

The developer notice is dismissed. SSEView now shows its Module Selection
dialog while reporting the isolated `plugins.txt`; its exact ordered contents
are the five official masters in the prepared manifest. Confirm that list with
the original module-selection helper and use the resulting session log to
verify the completed load.

The existing helper sent the Module Selection OK message, but no session log
has appeared and the next captured output was empty. Reinspect the window to
determine whether the dialog closed and check the process's private file
handles/session location before changing the wrapper.

The original helper dismissed the first-run `What's New?` notice. The live
window now presents the known `A message from the developer` dialog while the
same isolated plugin list is loading; dismiss only that named notice with the
helper, then inspect the module-selection dialog and loaded files.

The first native status call returned blank stdout before the new window was
ready. A separate manual diagnostic command passed a Python function instead
of the `.ps1` path; its PowerShell error is retained and does not implicate the
original helper. Add retry handling for empty status during process startup.

The repaired wrapper passes all eight focused xEdit tests and the strict Python
3.12 check. Exact next action: rerun `python3 scripts/python_env.py run
tools/xedit_bridge.py native-query --signature QUST --plugin Skyrim.esm
--editor-id DA14` in a fresh session, then inspect its actual decoded fields.

The second fresh native query still stopped on nonempty, non-JSON UIA output.
Inspect its per-step raw captures and process/window state to locate the exact
helper interaction, then repair and rerun the end-to-end command.

The second native run reached Module Selection, then exposed the exact parser
mismatch: the original UIA helper emits concatenated JSON objects for multiple
top-level windows. Update the parser to consume that form, add a regression,
then complete the native query.

The first concatenated-JSON parser regression found that unnamed hidden UIA
windows were included as empty status names. Exclude those blank titles and
rerun the focused suite before the next native operation.

All nine focused xEdit tests now pass, including a real-format fixture with
concatenated helper JSON and unnamed windows. Exact next action: run the fixed
canonical strict-dispatch native query for Skyrim.esm QUST DA14 in a fresh
session, then inspect the actual native fields.

The fresh query reached Module Selection, then stopped on malformed JSON at an
invalid accessibility control name emitted by PowerShell. Inspect its exact raw
bytes and sanitize this status text while preserving original click/hotkey paths.

The malformed field was a raw U+0007 bell character in a Delphi accessibility
name. The status parser now replaces raw JSON control characters inside names
with spaces while preserving the original xEdit dialog action and hotkey scripts.
Exact next action: run the focused xEdit suite, then retry native-query fresh.

All ten focused xEdit wrapper tests now pass, including blank startup output,
concatenated UIA JSON, unnamed windows, and raw control characters. Exact next
action: run the canonical fresh-session QUST DA14 native query and inspect its
field output.
