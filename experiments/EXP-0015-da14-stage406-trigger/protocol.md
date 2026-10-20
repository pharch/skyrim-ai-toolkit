# Protocol

## Static lane

1. Verify the installed executable identity and reuse the exact official-file hashes already registered for Skyrim.esm and Update.esm.
2. Read REFR `00000EC8`, its base ACTI, its parent cell group, and the cell's XTEL-linked references using read-only file parsing.
3. Resolve each linked destination REFR and CELL. Decode the destination record flags and any XESP enable parent against the pinned TES5Edit record schema.
4. Read the target DA14 QUST in Skyrim.esm and its Update.esm override. Decode VMAD object format and stage-index fields against the pinned TES5Edit schema; do not treat direct parser output as native xEdit or a profile winner.
5. Inspect the existing QF_DA14 PEX for the alias/enable relation and decode the QUST VMAD's stage/log-entry mapping against the pinned TES5Edit schema. Inspect a bounded XESP-child relationship for the portal marker. Keep the portal script's behavior unknown unless its PEX is independently sourced and decoded.
6. Keep all plugin, archive, save, and game files read-only. Store raw captures below ignored `.local/` and record their hashes.

## Conditional level-one validation

Run only after a disposable profile with its complete order, a clean level-one save, exact executable verification, and a loaded read-only Observer are available. Record numeric level, DA14/DA14Start running state and stage, portal-door enabled state, cell transitions, and the natural trigger event. Preserve a matched no-trigger control. Do not use console stage/level commands, injected scripts, or altered plugins as validation.

## Stop criteria

If the only ordinary record link into `DA14Interior` is unavailable before the gate and no independent player-reachable start writer is found, narrow this trigger as a non-candidate and continue to another open P0 line. This does not resolve the bounty or exclude every possible entry path.
