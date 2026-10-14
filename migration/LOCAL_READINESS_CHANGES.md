# Local Research Readiness Changes

## 2026-10-14 — Evidence-backed local readiness audit

- Reconciled the new 74-criterion mission with the existing setup/finalization records without inheriting old PASS statuses; recorded source hashes for 242 legacy Markdown candidates and 108 unique source paths in `migration/KNOWLEDGE_IMPORT_AUDIT.md`.
- Reworked the active AE-only instructions, onboarding, routing, and retained skills around exact ProductVersion preflight, read-only evidence collection, local `.local/` storage, and repeated frontier investigation.
- Added or repaired Python routes for local path resolution, AE target checks, plugin records, Ghidra read-only queries, PEX inspection, SKSE metadata, save/co-save inventory, research transactions, and Markdown/reference auditing. Kept original-game and private-source data ignored.
- Converted pytest-only tests to stdlib `unittest` discovery so the suite can run in this environment; updated CI and docs to use the checked-in supported commands. Full pytest and Windows/remote CI remain environment-dependent.
- Added transaction lifecycle and restart tests, including blocked-path reselection and separate fresh-process recovery/resume. Four real audit transactions exercised quest gate, armor XP, AV39 candidate, and Enchanting breadth investigations.
- Registered EV-0130 for an actual AE CommonLibSSE-NG library build (200,524,092-byte `.lib`, SHA256 `230929f4ac49b5dbd8c3c143c43e3983ad788891a3c83baa9201060f32addda2`). The combined Observer target failed; a `.local`-only include repair is staged but unverified because WSL process launch failed.
- Repaired the Ghidra query payload to export function lookup, bounded disassembly, optional decompilation, and explicit xref status. Added hash-bound query-only support for the recorded attempt2 and longanalysis projects; the latter verifies EV-0139 raw output and metadata plus current executable bytes. Nine adapter tests cover admission and rejection paths (EV-0140). Three native query launches then failed before Ghidra through the WSL process bridge (EV-0131/0138/0141).
- Recorded the terminal 7,200-second Ghidra analysis timeout and incomplete saved project (EV-0139), the final passing 139-test suite (EV-0145), and the final research/transaction/overlay/compile validators (EV-0146).
- Added the mission-specific checklist, readiness report, blockers, resume contract, and active Markdown inventory. No source files in the original Skyrim research repository, game installation, plugins, archives, or saves were modified.

## Validation boundary

The local Linux Python tests and validators establish repository/tool behavior only. They do not establish Windows MO2 profile behavior, xEdit winners, successful Observer DLL load, a live SKSE handshake, ReSaver parsing of a real save, or in-game AE mechanics.

- Final synchronized closeout recorded 64 PASS, 10 externally blocked criteria, and no pending rows; the Markdown inventory write/check passed after final checkpoint synchronization (EV-0151; prior passes EV-0147/EV-0149/EV-0150), and the staged privacy audit passed (EV-0148).
