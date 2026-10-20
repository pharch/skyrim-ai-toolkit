# Expected discriminants

1. Exact Steam `SkyrimSE.exe` ProductVersion and SHA-256 match EV-0109 before source scanning.
2. Source hashes and byte sizes for Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm, and Dragonborn.esm.
3. Per-master record counts by all record signatures, total subrecord and CTDA counts, and parser completion/error status.
4. Every 32-byte CTDA with function index 80, including source plugin/hash, record signature/FormID/EditorID, subrecord index, comparison, global-or-float operand, params, run-on/reference, and raw bytes.
5. All CTDA length anomalies retained with record provenance; such anomalies prohibit a complete negative.
6. Compare new hits to EV-0039 and EV-0306; then inspect the owner record and any linked quest/encounter transition for each novel signature.
