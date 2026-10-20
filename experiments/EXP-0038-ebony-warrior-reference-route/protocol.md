# EXP-0038 protocol

## Target and lane

- Installed target identity: Steam AE 1.6.1170.0, EV-0109. No complete selected profile order is configured.
- Lane: read-only official-master record analysis. No game launch, save edit, console command, plugin modification, or live observation.
- Record route: strict-dispatcher `tools/xedit_bridge.py file-records` and the read-only standard-library parser in `tools/plugin_reader.py`. Neither route resolves winning overrides.
- Interpretation reference: TES5Edit `dev-4.1.6` record definitions retrieved 2026-10-16. Branch URLs are not pinned to a commit.

## Procedure

1. Read EV-0288, EV-0289, EXP-0036, and EXP-0037; state H1/H2 and their predicted discriminants before scanning.
2. Query the Dragonborn.esm ACHR records and the specific `DLC2EbonyWarriorRef` record. Query the complete Dragonborn REFR, NPC_, PACK, SCEN, ACTI, and QUST signatures. Preserve raw command outputs. The empty TRIG route response is retained but is not treated as a general negative.
3. Run `scan_formid_refs.py` over each of the five official master files for `0202C49E`, `02030CC9`, and `020285C3`. The helper calls the existing `plugin_reader.read_plugin` parser once per file, emits every raw subrecord containing a target byte sequence, and ends with a scan-count/hash summary.
4. Treat byte matches as candidates. Inspect the matching record/subrecord signatures and the exact ACHR, QUST alias, and stage-10 evidence before assigning meaning.
5. Preserve each source file hash, parser coverage, exact commands, raw outputs, and the script hash. Do not infer a profile winner, live enabled state, complete script caller census, or level-one result.
6. Verify the private capture manifest and record a no-edge rationale to armor protection and hit-earned armor XP.

## Limits

The direct parser reports record/subrecord contents but does not include parent cell-group context or resolve overrides. A raw FormID-byte scan can miss dynamic string/API lookups and does not inspect PEX bodies inside BSA archives. The screen covers the five official masters only; Creation Club/user plugins and runtime behavior remain open.
