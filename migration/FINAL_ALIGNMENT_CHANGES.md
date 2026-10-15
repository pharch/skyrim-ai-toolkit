# Final local alignment changes

Scope: final pre-research alignment on 2026-10-14. No gameplay glitch claim was
investigated or changed during this pass.

| Previous condition | Change made | Verification |
|---|---|---|
| The active Ghidra adapter selected a Steam build and could create/import or analyze a project. | Bound one existing GOG project from ignored `config/local.env`; query now requires the existing program and runs `-process -noanalysis -readOnly`. Added an optional RVA route and a build-attested Address Library probe. | EV-0165–EV-0167; targeted tests in the final report. |
| Runtime executable identity and static analysis identity shared assumptions. | Kept GOG 1.6.1179.0 static analysis separate from Steam 1.6.1170.0 runtime identity; no address transfer is assumed. | EV-0167–EV-0168. |
| Path doctor read an older TOML registry and exposed competing bindings. | Made `config/local.env` the single active registry; retired tracked TOML example/sync behavior while leaving the user's ignored legacy local TOML untouched. | EV-0172; EV-0175 fresh-config exercise. |
| Routing and skills did not consistently name the tested GOG route and its safety boundary. | Updated tool routing, Ghidra, experiment, quest, armor, record, retained-tool, and save-state instructions; added `ghidra-project-research`. | Skill validation and policy audit in the final report. |
| Previous readiness documents contained superseded Steam-Ghidra assertions. | Added historical/superseded notices and redirected current status to the final report. Replaced the capability matrix with the current evidence and gate state. | Final Markdown/policy audit in the final report. |
| Clone/start behavior had no tested end-to-end handoff. | Added portable local binding and first-session prompt; ran isolated clone, initialization, doctors, prompt validation and recovery/resume rehearsal. | EV-0175. |
| xEdit and runtime version fields conflated executable identity with target identity. | Confirmed the configured SSEEdit hash still matches EV-0120's versioned 4.1.5.0 file; clarified that EV-0172's version field is Skyrim runtime metadata; changed the domain doctor output to nest runtime-target status; documented the current WSL PowerShell interop failure and absent complete order. Save/ReSaver and `lz4` limits remain documented. | EV-0120, EV-0172, EV-0181; domain-doctor regression test. |
| Active docs lacked one concise distinction among the three gates. | Current matrix and report separately assess GOG static, record/native cross-check, and live observation. | Final report and criteria audit. |
| The domain-doctor correction needed a complete post-fix closeout. | The full suite passed 151/151; compileall, all 13 active skill checks, and repository validators passed; the 52-row, gate, evidence-hash, prompt, GOG-preservation, privacy and worktree audit passed. | EV-0182 and the post-registration terminal audit. |

No game, plugin, archive, save, private corpus, or Ghidra program/user database
was intentionally modified. The Ghidra headless read-only open refreshed four
internal project index timestamps; this side effect is disclosed in EV-0165.


| October 15 user-requested xEdit/SKSE follow-up. | Copied the authoritative xEdit bridge bindings into ignored local config and tested its doctor, isolated five-master preparation, scoped AE preflight, and approved SSEView `-view` launch. Confirmed exactly five official masters and completed background loading; no safe UI record selector was exposed. Rebuilt the Observer from a local copy of authoritative `skyrim/observer` using reviewed compile/API compatibility edits, reran 7 analyzer tests, and prepared a no-launch session manifest. Replayed the exact xEdit helper files and five relevant config settings (EV-0191); updated active routing and config template. | EV-0184–EV-0191; 151 tests, 13 skill checks, all repository validators, and the post-registration validation pass. |
