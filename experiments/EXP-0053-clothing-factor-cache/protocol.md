# Protocol

1. Confirm the configured GOG `SkyrimSE.exe` ProductVersion and hash through the read-only Ghidra adapter. Keep GOG findings separate from installed Steam AE 1.6.1170.0.
2. Run `python3 scripts/python_env.py run tools/ghidra_probe.py --search-displacement 0x274 --timeout 600`; preserve wrapper metadata, raw Ghidra output, stderr, adapter hash, and query-script hash.
3. Refine the `+0x274` scan to separate stack references and likely stores. Inspect the cache writer, direct inventory traversal, bounded method table, and candidate visitor methods.
4. Run `python3 scripts/python_env.py run tools/ghidra_probe.py --search-displacement 0x1bc --timeout 600`; inspect the ARMO BOD2 parser and all relevant field consumers. Preserve the complete scan and report its instruction/access/function counts and any output caps.
5. Compare the parsed BOD2 second word with the TES5Edit dev-4.1.6 field schema recorded in EV-0309. Use the fresh GOG Address Library `VTABLE::TESObjectARMO` probe only as a class/build anchor, not as standalone field-name proof.
6. Join the result to EV-0261's GOG getter/hit-builder trace. Do not infer a Steam hit, effective protection, AVSK delta, or vanilla reproduction from static evidence.
