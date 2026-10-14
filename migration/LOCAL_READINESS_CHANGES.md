# Local Research Readiness Changes

## 2026-10-14 — Evidence-backed local readiness audit

- Reconciled the new 74-criterion mission with the existing setup/finalization records without inheriting old PASS statuses; recorded source hashes for 242 legacy Markdown candidates and 108 unique source paths in `migration/KNOWLEDGE_IMPORT_AUDIT.md`.
- Reworked the active AE-only instructions, onboarding, routing, and retained skills around exact ProductVersion preflight, read-only evidence collection, local `.local/` storage, and repeated frontier investigation.
- Added or repaired Python routes for local path resolution, AE target checks, plugin records, Ghidra read-only queries, PEX inspection, SKSE metadata, save/co-save inventory, research transactions, and Markdown/reference auditing. Kept original-game and private-source data ignored.
- Converted pytest-only tests to stdlib `unittest` discovery so the suite can run in this environment; updated CI and docs to use the checked-in supported commands. Full pytest and Windows/remote CI remain environment-dependent.
- Added transaction lifecycle and restart tests, including blocked-path reselection and separate fresh-process recovery/resume. Four real audit transactions exercised quest gate, armor XP, AV39 candidate, and Enchanting breadth investigations.
- Registered EV-0130 for an actual AE CommonLibSSE-NG library build (200,524,092-byte `.lib`, SHA256 `230929f4ac49b5dbd8c3c143c43e3983ad788891a3c83baa9201060f32addda2`). A subsequent local-copy repair used CommonLib's AE subobject accessors and PCH; the Observer Release DLL built and its x64 PE/SKSE exports were verified (EV-0154/EV-0155). The original source tree was not modified and no runtime handshake occurred.
- Repaired the Ghidra query payload to export function lookup, bounded disassembly, optional decompilation, and explicit xref status. Added hash-bound query-only support for the recorded attempt2 and longanalysis projects; the latter verifies EV-0139 raw output and metadata plus current executable bytes. Nine adapter tests cover admission and rejection paths (EV-0140). The actual query now passes (EV-0152), though its generic sample near image entry is not gameplay-identified and the project auto-analysis remains incomplete.
- Ran an independent ephemeral read-only Codex context against a sanitized state subset. It returned the correct profile-dependent next action without receiving repository documents or private source (EV-0153).
- Recorded the terminal 7,200-second Ghidra analysis timeout and incomplete saved project (EV-0139), the final post-closeout 139-test and research/transaction/overlay/compile suite (EV-0164), final Markdown inventory (EV-0161), staged privacy audit (EV-0162), and 74-row/status/checkpoint audit (EV-0163).
- Added the mission-specific checklist, readiness report, blockers, resume contract, and active Markdown inventory. No source files in the original Skyrim research repository, game installation, plugins, archives, or saves were modified.

## Validation boundary

The local Linux Python tests and validators establish repository/tool behavior only. They do not establish Windows MO2 profile behavior, xEdit winners, successful Observer DLL load, a live SKSE handshake, ReSaver parsing of a real save, or in-game AE mechanics.

- The successful query, Observer build/PE inspection, and independent Codex recovery move C07/C08/F08 to PASS. Current tally is 67 PASS, 7 BLOCKED_EXTERNAL, and no pending rows; five root blockers cover profile/load order, live runtime, real save, UESP provenance, and Windows/CI. Final test/validator rerun is EV-0160. Markdown inventory, staged privacy, and final cross-record audit captures are EV-0161–EV-0163.
