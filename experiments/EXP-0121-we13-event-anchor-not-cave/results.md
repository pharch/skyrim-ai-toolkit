# Results — Q70 bounded source map

The native fixed-five-master export of Skyrim.esm QUST 0009F32F (WE13) defines `TRIGGER` as a reference alias filled from Story Manager event data `R1` (`SCPT`), and `myHoldLocation` as a location alias filled from event data `L1`. `myAppropriateLocation` is constrained by `LocAliasIsLocation(myHoldLocation, ...)` conditions for Pale, Winterhold, and Hjaalmarch hold locations.

`TravelMarker1` and `TravelMarker2` are found as linked-reference children of `TRIGGER`; their conditions require `IsLinkedTo(TRIGGER)` and `HasRefType(WETravel)`. The QUST creates `EncSpriggan` and `EncTroll` at `TravelMarker1`; `Troll1` uses NPC_ 00023ABA and the Hard level setting. The QUST alias map contains no fixed named cave location, interior cell, entrance door, or placed cave troll. This supports an event-anchor-relative encounter model for this QUST record, not a global negative about every other source path.

The local UESP `Skyrim:Troll` revision 3526243 says trolls occur in wilderness and underground caves/Dwemer ruins; it uses “cave trolls” for generic cousins and does not define one unique Troll Cave. This is secondary wiki context, not evidence of a Skyrim AE route.

Q70-H2 and H3 are supported within the inspected record and cited page. Q70-H1 is falsified only for the QUST alias/spawn definition. EV-0387/EV-0321 still map the level-12 condition on the two Story Manager paths. No clean level-one event, WE13 state, alias fill, spawn, or physical traversal was observed; EV-0260 remains the runtime boundary.
