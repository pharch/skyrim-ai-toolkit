# Plugin record inspection and the xEdit boundary

Use the Python reader for read-only inspection of an explicit plugin:

    python3 scripts/python_env.py run tools/plugin_reader.py doctor
    python3 scripts/python_env.py run tools/plugin_reader.py inventory Skyrim.esm
    python3 scripts/python_env.py run tools/plugin_reader.py record Skyrim.esm --signature QUST --form-id <local-id> --include-subrecords

--include-subrecords returns each subrecord's signature, byte length, raw hex
and a bounded CP1252 view. It exposes CTDA, ALST, ALID, and VMAD payloads for
review. It does not decode every condition function or Papyrus property.

The reader processes one file at a time. The tested
`resolve_record_winner(candidates, active_order)` helper can choose the final
candidate when supplied the same logical FormID candidates and a complete
validated AE order. It does not load every active file or discover the user's
profile. Its two-record test fixture is synthetic; it is not a real winner
query or a replacement for xEdit. The configured SSEEdit 4.1.5.0 executable
exists and its current SHA-256 matches the file whose ProductVersion was read
as 4.1.5.0 (EV-0120, EV-0181). EV-0172's `product_version_verified` field
describes the Skyrim runtime target, not SSEEdit. A native call is blocked
until the selected profile's full explicit `plugins.txt` passes:

    python3 scripts/python_env.py run tools/ae_preflight.py

The current WSL PowerShell bridge fails before returning a ProductVersion with
`UtilBindVsockAnyPort` (EV-0181). Retry preflight from a working WSL/Windows
host after the selected MO2 profile and complete order are configured.

Do not infer a winner from Skyrim.esm and Update.esm rows without verified
load-order evidence. Keep original plugins read-only; retain raw outputs under
ignored .local/ and cite plugin hashes in tracked research.
