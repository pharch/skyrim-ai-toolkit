# Results

## Static GOG evidence

EV-0312 records the GOG AE 1.6.1179.0 rating and trap-path evidence. `FUN_140278170` stores the ARMO `DNAM` subrecord at runtime `+0x200`; `FUN_140223b20` reads the low word at that offset and combines it with helper data and two actor-supplied float factors. `FUN_140279460` routes BOD2 types 0 and 1 to separate actor-derived factor values. The `+0x274` cache visitor skips only BOD2 type 2 before its rating path, passes the contribution through Actor `HandleEntryPointVisitor` selector `0x55`, then accumulates it. `FUN_140728b70` stores the scaled visitor aggregate at PlayerCharacter `+0x274`.

EV-0261 connects PlayerCharacter slot `0xE7` to the hit builder's cached armor-factor input. EV-0302 shows the physical-trap builder uses the shared AV39/cache mitigation helper and directly calls the shared receiver handler without calling normal resolver `FUN_1406bcaa0`, which contains the known player AV11/AV12 branch. EV-0303 and EV-0304 bound relevant receiver/helper indirect sites; they do not establish a whole-program or live no-award proof.

Direct file-parser captures show positive Skyrim.esm DNAM values for `ArmorIronCuirass` (Heavy, 25) and `ArmorLeatherCuirass` (Light, 26), using the schema recorded in EV-0309. These are file-level source reads, not active-order winners or proof that either item is acquired/equipped in the target run.

## Status and limits

The source evidence supports a **static vanilla candidate**: Light/Heavy rating data can enter the cached factor used by the physical-trap damage path, while the known resolver armor-skill branch is bypassed. The exact meaning/effect of selector `0x55`, residual indirect/derived dispatch, positive live protection, Steam code equivalence, raw AVSK, and level-one reproduction remain unresolved. No runtime test was run.

EV-0315 traces two temporary receiver handles and the HitData sourceRef through generic GOG handle helpers. It finds no new mapped AV11/AV12 skill-progress sink but does not resolve concrete cleanup target classes or derived sourceRef vtables. Preserve the candidate as static only; a Steam test must still show positive damage and effective protection alongside unchanged raw AVSK.
