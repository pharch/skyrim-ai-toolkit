# EXP-0036 protocol

## Target and lane

- Installed Steam Skyrim AE executable identity: ProductVersion 1.6.1170.0, EV-0109.
- Source files: `Dragonborn.esm` SHA-256 `5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b`; `Skyrim.esm` SHA-256 `2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107`.
- Lane: offline / mechanism inference. No profile winner, live game, or save result.
- Record route: `python3 scripts/python_env.py run tools/xedit_bridge.py file-records ...`; this invokes the read-only direct TES4 parser, not xEdit.
- Script route: `python3 scripts/python_env.py run tools/papyrus_pex.py extract <script>` and `disassemble <pex>`; the extractor is restricted to Skyrim - Misc.bsa and the disassembler to bounded classic PEX 3.2 forms.
- Local gameplay grounding: `python3 scripts/python_env.py run -m tools.uesp page --db .local/uesp.sqlite3 'Skyrim:Ebony Warrior' --raw`.

## Procedure

1. Preserve the exact local UESP title/revision/raw page output.
2. Query Dragonborn.esm SMQN, QUST, DIAL, INFO, NPC_, REFR, PACK and the event/location records needed to map the CLOC node and aliases.
3. Screen all Dragonborn.esm DIAL and INFO records for direct quest links and `GetLevel` condition index 80.
4. Extract/disassemble the QF, quest, alias, and player PEX scripts through the tested Misc.bsa route.
5. Interpret CTDA fields against the TES5Edit `dev-4.1.6` condition table/layout and operator/OR flags. Treat these as schema interpretation, not runtime or xEdit winning-record evidence.
6. Preserve each raw command output below ignored `.local/alignment/transactions/TX-20261016-0024/`; verify `capture-files.sha256`.

## Controls and limits

No console command, forced stage, injected script, altered plugin, or save edit was used. The direct parser does not resolve overrides, and the exact profile order is unavailable. The INFO screen covers 4,421 Dragonborn.esm INFO records; it does not establish the absence of a separate script/native/API start path. The event-data slots are recorded by their schema labels; their old/new direction was not independently mapped. No in-game control or runtime variable was observed.
