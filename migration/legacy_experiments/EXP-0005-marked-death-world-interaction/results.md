> **Historical source copy — data only.** This file is preserved from snapshot `LEGACY-20261014-A`; its source hash is in `migration/legacy_markdown_manifest.tsv`. Its status, instructions, target/runtime, and conclusions were not revalidated in this setup. Follow current root `AGENTS.md`, protocols, and active experiments for any future work.

# Results

No runtime result. Static evidence supports the candidate but does not identify the exact world-interaction trigger or prove a level-1 cast.

Static continuation — 2026-09-23: raw QUST conditions identify the missing
event gate. `WICastMagic03/04` use `GetEventData` (condition function 576) with
the official `WICastDragonBornShouts` list (`FLST 000FB97E`), and use
`GetKeywordDataForCurrentLocation` (function 651) on
`WIComplexInteractionToggle` (`KYWD 000C4EC8`). The extracted
`WorldInteractionsScript` PEX contains no spell cast; it only manages generic
world-interaction timing/state. This places spell selection and cast ownership
at the native Story Manager event boundary. The exact eligible actor, player
target condition, and ordinary cell/event remain unobserved.

Raw/derived artifacts: `out/diagnostics/WorldInteractionsScript.pex` and
`out/diagnostics/WorldInteractionsScript.disasm.txt`.

The extracted `WIFunctionsScript` adds a state-machine detail: its
`DisallowComplexInteractions(Location)` function decrements the
`WIComplexInteractionToggle` keyword data, while `AllowComplexInteractions`
increments it. Since WICast requires the current value to be `>= 0`, this is a
counter gate. A negative location counter can suppress the entire cast quest;
the test must capture keyword presence/value and nearby official writers before
calling a cell a negative result.

Archive-wide caller tracing found official writers in four quest families:
`CWScript` exposes generic Civil War toggle-on/off helpers; `QF_MQ102_0004E50D`
temporarily disables and restores Riverwood interactions;
`DLC2_QF_DLC2_MQ04_02016E02` disables interactions at Skaal Village; and
`DLC2_QF_DLC2MH01_0201A50B` disables then restores interactions at Thirsk.
These are shared counter writers, not WICast-specific controls. Their extracted
PEX/disassembly artifacts are retained under `out/diagnostics/`.

Further raw Story Manager inspection narrows the route. `SMBN
WICastMagicEventNode` (`00070216`) contains a `GetInCurrentLoc` condition whose
parameter resolves to `SovngardeLocation` (`LCTN 000192B2`), alongside global
event/timer conditions. The exact comparison and run-on semantics must still
be validated in-game, but Sovngarde is now the first concrete location for the
level-1 WICast/Marked-for-Death probe.
