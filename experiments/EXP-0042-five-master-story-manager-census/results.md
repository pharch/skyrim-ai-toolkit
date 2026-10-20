# Results

## Census

The strict-dispatcher `file-records` captures returned all five source-file signatures: Skyrim.esm has 448 SMQN and 24 SMEN; Update.esm has zero of either; Dawnguard.esm has 36 SMQN and one SMEN; HearthFires.esm has eight SMQN and one SMEN; Dragonborn.esm has 43 SMQN and two SMEN. That is 535 SMQN and 28 SMEN physical records. A separate hash-verified scan of the prepared five-master copies found 99/0/11/2/15 SMBN records in those files and resolved targeted `PNAM` parents. The full-source counts and SHA-256 identities are in the private capture manifest.

The raw CTDAs contain 15 function-index-80 conditions on 15 distinct SMQN records. A source-context-aware comparison by originating plugin and local FormID found no additional function-80 override to change those 15 conditions. This comparison is a direct-parser observation; native xEdit did not start.

| Story Manager node | Serialized gate | Child QUST | Child event field | Parent record |
|---|---:|---|---|---|
| `WIChangeLocationThiefNode` | `GetLevel >= 5` | `WIThief01` | `CLOC` | SMEN `CLOC` |
| `DA14QuestStartNode` | `GetLevel >= 14` | `DA14Start` | `CLOC` | SMBN `QuestNode` |
| `DA07StartNode` | `GetLevel >= 20` | `DA07intro` | `CLOC` | SMBN `QuestNode` |
| `DA09IncreaseLevelNodeSHARES` | `GetLevel >= DA09MinLevel (12)` | `DA09` | `LEVL` | SMEN `LEVL` |
| `DA02IncreaseLevelNodeSHARES` | `GetLevel >= DA02MinLevel (30)` | `DA02` | `LEVL` | SMEN `LEVL` |
| `DA06IncreaseLevelNodeSHARES` | `GetLevel >= DA06MinLevel (9)` | `DA06` | `LEVL` | SMEN `LEVL` |
| `MS04IncreaseLevelNodeSHARES` | `GetLevel >= MS04MinLevel (14)` | `MS04` | `LEVL` | SMEN `LEVL` |
| `DA13IncreaseLevelNodeSHARES` | `GetLevel >= DA13MinLevel (12)` | `DA13` | no ENAM in captured child | SMEN `LEVL` |
| `MS06IncreaseLevelNodeSHARES` | `GetLevel >= MS06MinLevel (10)` | `MS06` | `LEVL` | SMEN `LEVL` |
| `DA08KickerNode` | `GetLevel >= DA08MinLevel (20)` | `DA08RumorPointer` | `LEVL` | SMEN `LEVL` |
| `DA04SeptimusFindPlayerNode` | `GetLevel >= DA04MinLevel (15)` | `DA04SeptimusSendForPlayerQuest` | `CLOC` | SMBN `QuestNode` |
| `FFR09KickerNode` | `GetLevel >= FFRiften09Gate (14)` | `FreeformRiften09` | `LEVL` | SMEN `LEVL` |
| `DLC1VQ00Node` | `GetLevel >= DLC1VQMinLevel (10)` | `DLC1VQ00ChangeLocation` | `CLOC` | SMEN `CLOC` |
| `DLC2dunHaknirTreasureNodeSHARES` | `GetLevel >= DLC2dunHaknirTreasureQSTMinLevel (36)` | `DLC2dunHaknirQSTIncreaseLevel` | `LEVL` | SMEN `LEVL` |
| `DLC2EbonyWarriorNode` | `GetLevel >= 80` | `DLC2EbonyWarriorQuest` | `CLOC` | SMEN `CLOC` |

The 12 additions to the previously known DA14, Durak, and Ebony Warrior nodes are the Thieves Guild location node; the DA07, DA09, DA02, DA06, DA13, DA08, DA04, MS04, MS06, and FreeformRiften09 nodes; and Haknir's Deathbrand helper node. Children `DA09`, `DA02`, and `MS06` come from Update.esm overrides; the Story Manager nodes themselves are in Skyrim.esm. DA04's selected child is the `SeptimusSendForPlayer` helper, not the main `DA04` QUST. Haknir's selected child is an `IncreaseLevel` helper, not the treasure quest record.

## Source-grounded route leads

The local UESP snapshot corroborates several thresholds but remains secondary evidence. Its pages list Pieces of the Past at 20 (revision 3507117), Boethiah's Calling at 30 (3564723), The Cursed Tribe at 9 (3597866), The Break of Dawn at 12 (3539493), The Only Cure at 10 for the Afflicted Refugee and 12 for Kesh (3564205), The Whispering Door at 20 (3578672), Grimsever's Return at 14 (3633225), Deathbrand at 36 (3547873), and The Wolf Queen Awakened at 10 (3572499). The exact revision URLs and response hashes are in the capture manifest.

The DA04 page reports that Discerning the Transmundane may begin during Elder Knowledge or Scroll Scouting, while level 15 is needed to continue past giving Septimus the Lexicon; at lower level, a later courier letter resumes progression (revision 3564369). This is an alternate-start lead to examine in the next investigation, not proof of level-one execution. The node captured here selects only `DA04SeptimusSendForPlayerQuest`.

## Hypothesis result and limits

- **H1 falsified within the five official master SMEN/SMQN source-file scope:** the three known nodes do not account for all Story Manager `GetLevel` gates.
- **H2 supported within the same scope:** 12 additional function-80 nodes select distinct child QUST records.
- `CTDA` function 80 is `GetLevel`; the versioned TES5Edit schema maps type high nibble `0x60` to `>=` and low bit `0x04` to `Use global`. Global names and FLTV values were independently resolved from hash-verified plugin records.
- The native five-master xEdit query for `DA07StartNode` failed before process enumeration with `UtilBindVsockAnyPort:307: socket failed 1`. This is a tool blocker, not a record negative.
- No complete target load order, native xEdit winning fields, Dawnguard/other BSA script census, dynamic-start path census, or live level-one transition/control was available. No OBJ-2 causal edge is supported.
