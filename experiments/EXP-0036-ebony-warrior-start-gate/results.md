# EXP-0036 results

## Direct observations

- `SMEN 0001320E` has event `CLOC`; Dragonborn.esm `SMQN 0202C49F` is its child node, with one QUST child `0202C49E`.
- The node's first CTDA is `GetLevel >= 80` on PlayerRef. Five OR-marked event-data conditions reference Whiterun, Windhelm, Riften, Markarth, and Solitude location records; another condition tests `DLC2SolstheimLocation` in the other location slot.
- QUST `0202C49E` is CLOC and its Start Game Enabled flag is clear. Its own four top-level CTDA function IDs are 74, 1, 1 and 72, not 80.
- The QF stage-10 fragment enables the Ebony Warrior alias, moves it to CityCenter, and gives the player the pickpocket modifier perk. The player alias script uses stage 100 during `OnLocationChange` to move the actor to Last Vigil; entering the Last Vigil location after the move starts combat. The alias `OnDeath` handler requests stage 200.
- Six DIAL records link to the quest. A scan of all 4,421 Dragonborn.esm INFO records found no CTDA function index 80. Three INFO records directly reference the quest in `GetStage` conditions; the direct parser does not include DIAL parent-group IDs, so no topic attribution is made.
- Three Ebony PACK records use quest-stage or location-alias conditions; none contains GetLevel.
- The local UESP revision 3580051 reports the same level-80 encounter premise.

## Inference

The serialized level requirement belongs to the initial CLOC Story Manager selection path, not only to downstream dialogue. The selected QUST and its stage-10 fragment provide the static handoff from selection to an enabled actor in a city. A later stage/location callback moves the actor to Last Vigil. The broad possibility of an independently callable pre-gate start path remains open.

## Negative scope and omissions

The `GetLevel` negative applies only to the captured Dragonborn.esm INFO records. No full ACHR/REFR base-reference scan, all-plugin script-caller inventory, active-profile winner check, or game test was completed. The event-data `Location 1`/`Location 2` fields are not assigned old/new meaning here.

Raw evidence is private under `.local/alignment/transactions/TX-20261016-0024/`; its manifest SHA-256 is `b4f2330731c95646749980b4b4f3d980356eeb0ef400a0e80978a3611e11a5c8` and its entries passed `sha256sum -c`. The private note is registered as EV-0288.
