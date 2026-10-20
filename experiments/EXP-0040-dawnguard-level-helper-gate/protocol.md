# EXP-0040 protocol

1. Query Dawnguard.esm QUST, SMQN, GLOB, CELL, NPC_, DIAL, and targeted INFO records through the documented read-only file-record route. Preserve wrapper stdout hashes, raw output IDs, record counts, and exact plugin identity.
2. Decode CTDA function and compare fields against the versioned TES5Edit `dev-4.1.6` schema; resolve global-value operands and FormID parameters against the same Dawnguard.esm file.
3. Trace the Story Manager node's child reference to its QUST and alias target. Keep the helper quest distinct from VQ00/VQ01 progression.
4. Ground the gameplay path only as a revision-pinned local UESP lead. Distinguish quest journal appearance, quest startup, and `Awakening` start/progression.
5. Do not treat direct parsing as a loaded xEdit winner. Record the native xEdit attempt separately; it failed before process enumeration in this WSL session. Do not infer absent BSA PEX or runtime behavior.
6. Required candidate test: verified exact Steam build/order, clean level-one save, no-trigger control, ordinary guard/canyon/Fort sequence, numeric level preservation, and read-only QUST/`Awakening` running-stage observation. Repeat on a fresh save. Console-forced stages are diagnostic only.

Raw source pages and record outputs are stored under ignored `.local/alignment/transactions/TX-20261016-0033/`; the durable interpretation is EV-0298.
