# Unresolved migration and verification items

## Blocking specification input

`migration/FINAL_SETUP_BRIEF.md`, named as the authoritative definition of done,
is absent from the working tree, tracked history, and both visible remote
branches. The user requires its exact 82 acceptance criteria in
`migration/FINALIZATION_CHECKLIST.md`. They cannot be reconstructed from the
shorter `PORTING_CHECKLIST.md` without inventing criteria. Obtain the exact
brief, transcribe its 82 items verbatim, then execute and record evidence for
each one. Do not mark repository ready before that audit passes.

## Windows / game-specific validation

These tasks cannot be completed from the current Linux environment:

1. On the research Windows host, run `node tools/ae-preflight.js` against the
   intended `SkyrimSE.exe`; retain its JSON, executable SHA-256, and the
   reported ProductVersion.
2. Verify `PLUGINS_TXT` points to the active AE profile. On MO2, verify the
   selected virtualized profile in MO2 itself; compare its path and content
   hash with preflight output.
3. Verify xEditLib/DLL and registry mapping resolve to the same AE installation;
   test `tools/skyrim-winner.sh` on one known-present record and one known-absent
   record, preserving the complete result and exit code.
4. Test each optional retained tool only if its prerequisites are installed;
   capture exact versions, known-positive and known-negative fixtures, and
   coverage.
5. If live testing is authorized later, verify DevBench process identity and
   `alive` state before approved read-only inspection. No live call is approved
   by this checklist.

## Evidence import

No local legacy research v2 files, Ghidra project index, SKSE probes, UESP
snapshot, or Apocrypha export were identified as accessible evidence in this
checkout. Locate and import only authorized material with provenance. Do not
replace this unknown with a summary inferred from filenames.
