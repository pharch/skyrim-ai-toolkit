# Results — EXP-0026

- Local UESP `Skyrim:Dimhollow Crypt` revision 3586850 describes a gate/rubble boundary and a tower chain absent before Awakening. This is attributed wiki content and does not specify collision geometry or player-only clipping ([EV-0277]).
- REFR `02009742`, base ACTI `0003E726` (`NorPortcullisLarge01`), is parented by XESP to REFR `02017772` (`DLC1VQ01LeverGateEnableMarker`). The marker's base is Skyrim STAT `0000003B` (`XMarker`). The raw XESP flags and the child's raw header flags are not interpreted ([EV-0277]).
- The extracted `default2StateActivator` PEX was fully consumed. Its activation toggles open/close animation and enables/disables linked collision using its keyword property. No quest-stage call or explicit marker-enable call occurs in the recovered PEX ([EV-0277]).
- The declared five-master raw field screen found the child XESP as its only direct reference to the marker among scanned fields. Its exclusions do not rule out dynamic, alias-passed, native, profile or runtime writers ([EV-0277]).
- EV-0260 still lacks the exact selected order, clean candidate save and suitable read-only Story Manager/alias observer. No route, callback, quest start, alias fill, progression or level-one gameplay outcome was observed.
