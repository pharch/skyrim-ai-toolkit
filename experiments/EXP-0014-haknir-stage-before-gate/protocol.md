# EXP-0014 protocol

## Competing models and predictions

- **H1 — ordinary pre-gate writer:** a player-accessible book, encounter, quest, or alias route starts the main treasure quest, sets a relevant stage, or enables Haknir at level 1. A clean level-one observation should show a real quest/actor transition without console or injected state.
- **H2 — audited routes remain level gated:** the level-event helper is under the `GetLevel >= 36` Story Manager node; DLC2Init's stage-100 fragment applies the same min-level test before setting main-Q stage 10; the book requires main-Q stage 20; the misc quest only reads stage 20; and main-Q stage 90 owns the known Haknir enable call. A clean level-one observation should show no transition along these routes, with a matched level-36 control reaching the gated sequence.
- **H3 — uninspected runtime writer:** a dynamic/native writer, uninspected source archive, or profile override starts the main Q or reaches a relevant stage/actor state outside the bounded direct-reference/PEX chain. A complete profile/source audit or a clean runtime transition outside the traced routes would distinguish this model.

## Read-only source steps

1. Verify the Steam AE executable identity and hash the five official masters; do not infer a profile-specific winner from this source set.
2. Preserve the Haknir Story Manager node, global threshold, child and main QUSTs, placed ACHR, location alias, and exact raw FormID-reference candidates.
3. Use the supported narrow PEX stream extractor for the book and every identified attached QF PEX; label unsuccessful exact-name probes as scoped source limitations only.
4. Map QUST VMAD QF fragments to stages and trace every identified `Start`, `SetStage`, alias enable, and OnDying writer into the main quest. Distinguish DLC2Init, the LEVL helper, the misc quest, Deathbrand book, pirate encounter quest, and the main treasure quest.

## Live discriminant

On a clean level-one disposable save, use only an ordinarily acquired book/encounter and capture numeric level, main-quest running/stage state, `DLC2WE13` running/stage state, Haknir enabled/dead state, and any stage-100 writer trigger using a verified read-only method. Record a level-36 control separately. No console stage/level forcing, injected scripts, changed plugins, or altered saves count as a vanilla reproduction. EV-0260 currently lacks both the disposable target prerequisites and a Story Manager-state observer.

## Exclusions

An item being placed outside Gyldenhul Barrow does not prove level-one access or that reading it starts the quest. UESP is secondary grounding. Raw FormID byte matches are leads until semantically resolved. Direct parser and static PEX results do not establish dynamic enable behavior, profile winners, or runtime quest state.
