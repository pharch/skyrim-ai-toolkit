# EXP-0032 — Dawnguard BSA route scope

**Status:** Bounded current-harness route audit complete; Dawnguard archive extraction lane blocked.

**Objective:** Determine whether this checkout exposes a tested, read-only route to inspect `Dawnguard.bsa` for the generic `defaultSetStageTrigSCRIPT` PEX beyond its narrow Misc-BSA extractor.

**Result:** The strict domain doctor exposes no archive-reader capability. The documented Papyrus CLI fixes `extract` to `Skyrim - Misc.bsa`; `scan-literals` covers that archive and can optionally add `cc*.bsa`. The internal helper's path argument does not make it a supported general BSA parser: it scans raw bytes, lacks archive table/decompression handling, and its fixture is synthetic. The Dawnguard archive was not opened, so no script-absence claim follows ([EV-0284], [EV-0274], [EV-0276]).

See [hypothesis](hypothesis.md), [protocol](protocol.md), [predicted outcomes](predicted-outcomes.md), [results](results.md), and [implications](implications.md). Raw doctor/help/source captures remain under ignored `.local/alignment/transactions/TX-20261016-0020/`.
