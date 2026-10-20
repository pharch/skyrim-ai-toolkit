# Protocol

1. Verify the existing GOG AE 1.6.1179.0 binary identity and use the strict-dispatcher Ghidra adapter in read-only, `-noanalysis` mode.
2. Inspect references to the TESQuest vtable slot-19 function-pointer entry, the slot address, and `FUN_1403c8420`. Preserve direct and indirect xref distinctions.
3. Search the analyzed project for indirect calls using vtable offset `0x98` (slot 19). Treat this displacement as a broad candidate screen because unrelated vtables can use the same byte offset.
4. Classify candidate functions only when receiver/vtable provenance ties them to TESQuest; follow their caller paths far enough to compare QUST parser completion, load/finalization, and registered Quest.SetStage callback delivery.
5. Preserve all raw outputs and metadata under ignored `.local/`, with exact binary identity and bounded-output limitations. If the project cannot resolve dispatch order, retain both models and specify the read-only Steam before/after observer needed.
