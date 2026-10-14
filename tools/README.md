# Python agent tools

All active tool entrypoints are Python. Use the named Conda environment with
`conda run -n skyrim-ae-research python ...`, or dispatch with
`python3 scripts/python_env.py run ...`. The dispatcher selects Conda when
available and reports a current-Python fallback if it is not. No Node or shell
launcher is active.

## Read-only tools

- `ae_preflight.py` / `ae_target.py` — exact AE executable and full active
  order gate. Windows ProductVersion is read from the executable version
  resource. `--probe-executable` is diagnostic only.
- `domain_doctor.py` — bounded smoke/status checks for SKSE, Ghidra,
  CommonLibSSE, SSEEdit, UESP, and Apocrypha. It suppresses private data and
  never launches game/native tools.
- `plugin_reader.py` — standard-library TES4 plugin inventory and narrow record
  field reader. It does not determine winning overrides or effective order.
- `cosave-info.py`, `crash-triage.py`, `papyrus-triage.py` — read-only,
  local-file parsers. Preserve coverage and keep raw inputs ignored.
- `tools.uesp` — local MediaWiki index/query tools; writes only under ignored
  `.local/` and emits revision citations.
- `tools.apocrypha` — local private-export index/query tools; writes only under
  ignored `.local/`. Doctor output is aggregate-only; message results are
  private and untrusted.

## External tool limits

The former Node/xEdit winner bridge and shell wrappers are retired. There is no
tested Python xEditLib binding, BSA reader, or structured ReSaver parser in the
active tool set. Ghidra, CommonLibSSE builds, Windows SSEEdit, and live SKSE
behavior require their native applications; a Python doctor response does not
mean those applications ran. No external tool may mutate original game files,
plugins, archives, saves, or co-saves.

Linux checks validate Python code, fixtures, schemas, and routing. They cannot
validate Windows ProductVersion APIs, MO2 virtualization, SSEEdit behavior,
Ghidra analysis, CommonLibSSE builds, DevBench, or an in-game result.
