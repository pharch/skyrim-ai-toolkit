# EXP-0041 protocol

1. Use the Dawnguard.esm SHA-256 recorded in EV-0298/EV-0299 and query every SMEN and SMQN record with the strict-dispatcher `tools/xedit_bridge.py file-records` route.
2. Preserve wrapper stdout and stderr, raw-capture IDs, record counts, FormID origins, and query-source hashes.
3. Decode each CTDA function index using TES5Edit `dev-4.1.6` `wbDefinitionsTES5.pas`; inspect all function-80 conditions and their comparison operators/operands.
4. Resolve any global and child QUST/SMQN references against the same official-master source files; do not promote direct-parser results to a profile winner.
5. Keep Dawnguard BSA/PEX, scripts, dynamic calls, Creation Club/user plugins, exact order, and live level-one behavior outside this record-file census.
