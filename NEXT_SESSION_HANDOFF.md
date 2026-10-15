# Next session handoff

No additional setup or glitch research was started in this handoff pass.

1. At the repository root, run:

   ```text
   python3 scripts/python_env.py run scripts/research_state.py validate
   ```

2. Read `migration/FINAL_ALIGNMENT_REPORT.md`, then follow
   `docs/RESEARCH_START_PROMPT.md` for the first deep research session. It
   starts with P0 OBJ-1 / Q-0001 and records rival H1/H2 models and discriminants.
3. For xEdit winners, first identify the selected MO2 profile and set its
   explicit `MO2_PROFILE_DIR` and `PLUGINS_TXT`, then pass AE preflight. The
   verified five-master SSEView session is not the active profile and produced
   no record export. The bridge implementation is only in the sibling
   `skyrim` repository plus an ignored local copy; see
   `docs/LOCAL_TOOL_HANDOFF.md` and `protocols/TOOL_ROUTING.md`.
4. For an SKSE experiment, the Observer is built and staged only. A designated
   disposable profile, plugin list, save and deployment path are still absent;
   there was no game process, DLL load, handshake or observed game state.

Remaining uncertainties: UESP dump provenance/completeness; selected MO2
profile and winners; actual save/ReSaver parsing (`lz4` is missing); and live
SKSE/Observer handshake and state retrieval. Current Python fallback is system
Python 3.12.3; Conda is unavailable. The three gates remain `READY`, `PARTIAL`,
and `NOT_VERIFIED`, respectively.

The private local path note is ignored. The tracked handoff does not include
machine paths, game/plugin bytes, saves, Ghidra project data, or private
Apocrypha message content.
