# Results

## Complete five-master census

The read-only parser completed all five official masters after verifying each source hash recorded in EV-0321. Across 1,178,548 records it parsed 117,272 CTDA subrecords; all had the expected 32-byte size. It found 327 function-index-80 (`GetLevel`) conditions across eight signatures: INFO 43, SMQN 15, ENCH 40, MGEF 50, PACK 1, PERK 36, QUST 57 and SPEL 85. The exact installed Steam executable identity matches EV-0109 (AE 1.6.1170.0); this is source data for the installed files, not evidence of the active load-order winner.

A fixed official-master source-layer comparison leaves 320 conditions in winning official records: ENCH 40, INFO 42, MGEF 50, PACK 1, PERK 36, QUST 51, SMQN 15 and SPEL 85. No candidate record lost every GetLevel condition under this source-layer comparison. It is not an MO2/profile winner query. Applying the versioned QUST field order classifies the 51 winners as 36 Story Manager Conditions and 15 alias Match Conditions. Three conditions use globals: `LevelGateSpriggan` (`000EC42A`, 8), `LevelGateTrollCave` (`000EC42C`, 12) and `LevelGateIceWraith` (`000FC4E2`, 10). These labels describe serialized fields, not observed runtime dispatch.

## DA03Start guard greeting lead

The winning official Skyrim.esm package candidate `PACK 000E0D53 DA03StartGuardStartQuestGreet` has `GetLevel >= 10` and `GetStage(DA03Start 000D7939) < 5`. `DA03Start` has the serialized Start Game Enabled flag. Its PDTO points to `DIAL 000E0D44 DA03StartGuardGreetBranchTopic`; a GRUP type-7 parent join finds one linked INFO child, `000E0D46`, with the same `GetLevel >= 10` and `GetStage(DA03Start) < 5` conditions. Four additional INFO conditions use function index 566 with parameters 7, 8, 9 and 10; their function name remains unresolved and their raw CTDA bytes are retained.

INFO `000E0D46` has no VMAD or direct quest-fragment subrecord. The DA03Start QUST VMAD stores its quest-stage `QF_DA03Start_000D7939` fragments; the bounded `Skyrim - Misc.bsa` lookup did not find a `TIF__000E0D46` PEX stream. The extracted QF disassembly maps `Fragment_27` to `DA03.SetStage(5)`, `Fragment_29` to adding 25 gold and `self.SetStage(200)`, and the remaining inspected fragments to objective/stop operations. No captured call connects the guarded INFO response to `DA03.SetStage`. Local UESP revision 3582964 (2026-06-28) says the level-10 Falkreath guard encounter points the player to Lod and identifies DA03Start as the helper. This supports a gated guard-greeting path; it does not establish that all DA03 starts are gated.

## Hypothesis outcomes and boundaries

- **Q60-H1 — falsified within the complete five-official-master source corpus.** GetLevel appears outside the known SMQN/DIAL/INFO families. The PACK/INFO pair provides a progression-related DA03Start guard-greeting candidate.
- **Q60-H2 — supported.** PACK and QUST add GetLevel conditions, and the DA03Start package/INFO records connect one to a named guarded dialogue path.
- No level-one reproduction or effective access was observed. No full active order, profile winner, native xEdit winner, or runtime dialogue state is available. The INFO response text is localized by string ID in the raw record; its player-facing wording here is grounded only by the captured local UESP page.
- The complete census includes unrelated ENCH/MGEF/PERK/SPEL conditions. Their presence alone does not make them quest-entry gates.
