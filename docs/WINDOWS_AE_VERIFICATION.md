# Windows AE verification checklist

Linux cannot prove a live Windows Skyrim AE installation or in-game behavior.
Verify the exact target before interpreting runtime observations or records.
Keep the research checkout separate from the game installation.

## Prerequisites

- Windows 10/11 with `SkyrimSE.exe` under the actual game root.
- Ignored `config/local.env` with `SKYRIM_EDITION=AE`, `GAME_ROOT`, and the
  selected profile's explicit complete `PLUGINS_TXT`.
- For MO2, use the chosen profile's own `plugins.txt`; do not use a global or
  guessed profile list.

## Preflight

From the checkout, run the Python tool through the repository environment:

```text
python3 scripts/python_env.py run tools/ae_preflight.py
```

The preflight reads the executable ProductVersion from its Windows version
resource, requires 1.6.318 or newer, hashes the executable and active list, and
checks all five required official masters. It rejects a missing or incomplete
order. `--probe-executable` checks only the executable and does not authorize
SSEEdit or live-game access. Do not treat a typed version value as proof.

## What to preserve

Keep the preflight output local. Record the ProductVersion, executable hash,
active-order hash, and exact selected profile. Keep absolute paths in ignored
local configuration; tracked research only needs a source ID or redacted
identity where applicable.

## Available post-gate Python tools

- `python tools/plugin_reader.py record <plugin> --signature <SIG> --form-id <local-id>`
  reads a selected plugin. It does not resolve active winning overrides.
- `python tools/cosave-info.py <copy.skse>` surveys co-save structure only.
- `python tools/papyrus-triage.py <log>` and
  `python tools/crash-triage.py <file-or-dir>` summarize local logs.
- `python tools/domain_doctor.py` reports Ghidra, CommonLibSSE, SSEEdit, and
  live SKSE prerequisites. A candidate path is not proof that the external
  application ran.

The Node/xEditLib and shell wrappers are retired. Native SSEEdit winner lookup,
Ghidra analysis, CommonLibSSE build, and live SKSE inspection remain blocked
until their Python entrypoints and external prerequisites are verified. No
mutating or write operation is available through the agent tool set.

Do not claim AE runtime or gameplay verification from Linux or from a
not-yet-executed Windows preflight. Mark the target unverified until the full
preflight succeeds on the selected Windows installation/profile.
