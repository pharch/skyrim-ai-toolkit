# Protocol

1. Use the strict Python dispatcher and the configured `SKYRIM_EXE_PATH` and `SKYRIM_DATA` only. Read the actual PE ProductVersion and executable bytes; require EV-0109's Steam AE 1.6.1170.0 ProductVersion and SHA-256.
2. Traverse all records and subrecords of each required official master via `tools.plugin_reader.read_plugin`; do not use incomplete active-order data to select winners.
3. Hash every input and retain all GetLevel CTDA records and any non-32-byte CTDA anomalies in `.local/alignment/transactions/TX-20261017-0007/`.
4. Only mark the condition census complete after all five masters parse and every CTDA is decoded under the existing 32-byte decoder. Otherwise preserve the partial/error capture and report the exact boundary.
5. Compare results with EV-0039 and EV-0306, and source-check each novel hit before calling it a progression gate.
6. Do not launch the game, force a stage or level, modify a plugin, or write to game data.
