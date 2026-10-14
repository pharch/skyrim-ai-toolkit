# Python plugin inspection and SSEEdit boundary

The old Node/xEditLib winner bridge has been retired. The active Python
replacement is a standard-library TES4 reader:

```text
python3 scripts/python_env.py run tools/plugin_reader.py doctor
python3 scripts/python_env.py run tools/plugin_reader.py inventory Skyrim.esm
python3 scripts/python_env.py run tools/plugin_reader.py record Skyrim.esm --signature QUST --form-id <local-id>
```

It inspects one explicit plugin file and reports record/subrecord fields. It
does not establish a full active order, resolve a winning override, or replace
SSEEdit. Before a native SSEEdit call, run
`python3 scripts/python_env.py run tools/ae_preflight.py` and verify the exact
Windows executable plus selected full profile order. No tested Python binding
to the xEdit native library is currently available, so winning-record claims
remain blocked until that integration is implemented and tested.

The Python parser is read-only and never opens the game or saves plugin data.
Summarize relevant record fields and provenance in Markdown or the evidence
database. Keep original plugins and raw tool outputs in local game storage or
ignored `.local/`, never in the repository.
