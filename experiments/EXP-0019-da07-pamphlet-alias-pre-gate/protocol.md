# EXP-0019 protocol

## Competing models and discriminants

- **H1 — alias-first start:** a normal player action can access the scripted pamphlet alias while DA07intro is still stopped; the alias callback then calls `SetStage(5)`. The discriminant is an ordinary pre-gate alias fill followed by stage 5 before DA07StartNode fires.
- **H2 — quest-owned alias:** the alias is created/filled only as part of DA07intro's own start sequence, while the base BOOK and other ordinary copies do not carry the alias script. The discriminant is the QUST alias/VMAD mapping, its stage-0 fill fragment, exact script attachment, and a complete official-master reference screen for ordinary base-book writers.

## Read-only procedure

1. Keep the verified Steam AE 1.6.1170 executable identity (EV-0109) separate from the five official master files; record every plugin hash and do not claim a profile winner.
2. Ground the level prerequisite and named book in dated local UESP revisions, treating them as leads rather than engine behavior.
3. Retrieve DA07StartNode, DA07intro, and the base BOOK with the direct parser. Decode the QUST alias fields against the pinned/local TES5Edit schema and retain raw bytes.
4. Extract and disassemble only the directly linked quest, alias, and INFO PEX scripts through the tested base Misc BSA route. Record PEX version, archive hash, parsed length, and output hash.
5. Scan all five official masters for raw occurrences of the BOOK, intro QUST, main DA07 QUST, and start-node FormIDs. Validate candidate fields before assigning semantics; report byte-pattern candidates and unsupported schema cases.
6. Keep the separate DA07IntroTrigger writer outside the pamphlet conclusion and open a successor investigation if it is plausible.
7. Do not test with `setstage`, `startquest`, forced level, injected scripts, or altered plugins. Any eventual natural level-one result needs a verified executable, complete target order, clean baseline, numeric level-preservation check, and state capture.

## Scope and exclusions

No game, save, archive, or plugin was modified. Direct parser output is not native xEdit. A five-master static result does not establish a user/profile winning record or an in-game bypass.
