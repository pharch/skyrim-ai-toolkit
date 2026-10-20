# Results

The legacy source reports the three Marked-for-Death spell forms in `WICastDragonBornShouts`, WICast event quests with actor/target aliases, a current-location `WIComplexInteractionToggle` predicate, and an unresolved actor/location selection rule. No ordinary cast or player AV39 delta was observed in that source experiment.

## Current official-master record review

- The installed Steam AE five-master screen found 1,633 MGEF records and 22 raw AV39 candidate rows (21 unique records after the Update.esm override). Skyrim.esm MGEF `0010319D` is `VoiceMarkedForDeathArmorEffect01`; Update.esm overrides the same form. All three Marked-for-Death spell forms (`0001861F`, `00018627`, `0001862B`) reference that MGEF. The record scan maps its primary ActorValue field to 39; the scan is a raw record read, not a live ActiveEffect observation ([EV-0224], [EV-0225], [EV-0226]).
- The WICast quests are linked from a `CAST` Story Manager node and use separate `CastingActor` (`R1`) and `SpellTarget` (`R2`) aliases. `WICastMagic03` also has a separate forced `Player` alias (`ALFR=00000014`); that does not prove its `SpellTarget` alias fills with the player. Update.esm overrides `WICastMagic03` with materially similar aliases. TES5Edit metadata explicitly leaves ALFD's stored event-data meaning unknown ([EV-0228], [EV-0229]).
- A five-master byte-reference screen found 41 raw candidate references and a bounded NPC_ scan found no direct spell/shout references to the MFD forms. These results do not prove absence of a script/native route or identify the actor selected by the event ([EV-0227]).
- The separate Haknir MGEF `02038053` modifies AV39 and is used through a scimitar enchantment on the Haknir actor; the traced encounter path has a level-36 Story Manager gate. It is not evidence for a level-one player-targeted writer ([EV-0225], [EV-0231], [EV-0232]).
- The indexed `OnStoryCastMagic` API lists parameters for casting actor and spell target, and its CK-Wiki-derived caveat says `akSpellTarget` always returns None. Cross-referenced with the WICast record aliases, this supports an inference that R1 is the player cast's source actor and R2 is only the nominal target field. The WICast QF fragments inspected contain no direct spell-application/retarget call; no natural event or PlayerRef AV39 delta is captured ([EV-0241], [EV-0244]).

**Lane:** `mechanism_inference` (current official-master record review plus legacy source review).

**Not performed:** native xEdit winner export, live event observation, or runtime hit test. Installed Steam AE 1.6.1170 identity is verified, but the full selected profile order, test save and loaded Observer are unavailable. A profile winner and player-targeted cast are not established.

## Next action

Capture a natural eligible event's source, target, spell, location, quest alias fills, and raw player AV39 if verified live observation becomes available. Until then, treat WICast as a player-cast response with unresolved target fill and continue screening independent negative AV39 writers; do not force the event or effect.
