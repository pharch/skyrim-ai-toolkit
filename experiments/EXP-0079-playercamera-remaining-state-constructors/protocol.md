# Protocol

Use only the existing GOG AE 1.6.1179.0 Ghidra project through the strict dispatcher in read-only/no-analysis mode. Retain constructor and vtable raw captures; map only observed vtable addresses. Query slot+0x10 and complete call-site censuses; follow the shared helper only to the observed depth. Do not transfer GOG RVAs to Steam or treat missing direct calls as proof about unresolved dynamic targets.
