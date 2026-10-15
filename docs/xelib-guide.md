# Plugin record inspection and the xEdit boundary

For the active setup and exact commands, use
[`docs/LOCAL_RUNTIME_CONTRACT.md`](LOCAL_RUNTIME_CONTRACT.md) and
[`protocols/TOOL_ROUTING.md`](../protocols/TOOL_ROUTING.md).

There are three distinct routes:

1. `python3 scripts/python_env.py run tools/xedit_bridge.py file-records
   --signature QUST --plugin Skyrim.esm --editor-id <substring>` parses a
   configured plugin file directly. It returns raw record data and is not an
   xEdit field query or winner resolution.
2. `python3 scripts/python_env.py run tools/xedit_bridge.py native-query
   --signature QUST --plugin Skyrim.esm --editor-id <exact-editor-id>` opens
   configured SSEView in `-view`, loads only the five official masters from
   the `.local` Data view, and returns the native xEdit field tree. It needs
   no MO2 profile. EV-0207 preserves the cold-start QUST smoke result.
3. A profile-specific winner or negative claim requires the complete active
   order from the actual target. If MO2 manages it, configure that profile's
   explicit `plugins.txt` and run the full `ae_preflight.py`.

The underlying direct parser exposes ordered subrecords and raw CTDA, ALST,
ALID, and VMAD payloads; it does not decode every condition function or
Papyrus property. Native `WinningOverride` output is scoped to the actual
loaded five-master view and must not be represented as an active-profile
winner.

## Historical setup note (superseded)

Earlier readiness notes EV-0181–EV-0206 described the native export as blocked
by a missing MO2 profile and manual record selection. That was the state before
the original SSEView workflow was restored. EV-0207 records the tested native
query and the exact loaded-file list. The older notes remain as setup history;
they are not the current xEdit capability report.
