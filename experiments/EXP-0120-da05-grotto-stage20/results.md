# Results

## Source identity and scope

The queried records are from the fixed official five-master SSEView scope. Steam `SkyrimSE.exe` ProductVersion 1.6.1170.0 is identified by EV-0109, but no live state or active profile winner was observed. The FormID census verified all five source plugin hashes and parsed 1,178,548 records. Its 142 exact-byte hits resolve to 70 candidate records; these are candidates for interpretation, not 142 semantic references.

## Direct record and script findings

1. Native xEdit maps INFO `00095585` as the only child of DIAL `00095582`, whose QNAM owner is helper QUST `000955CF`. The helper quest's Start Game Enabled flag is clear. Alias 57 is `Hunter00_JKier`, forced to `DA05JKierREF` (`ACHR 0002ABC6`) in `BloatedMansGrottoWorld`. The INFO has one condition: function 566, alias parameter 57, comparison value 1.0, Run On Subject. TES5Edit `dev-4.1.6` maps function 566 to `GetIsAliasRef` with an alias parameter [TES5Edit condition table](https://github.com/TES5Edit/TES5Edit/blob/dev-4.1.6/Core/wbDefinitionsTES5.pas#L3083-L3086).
2. The TIF class extends `TopicInfo`. Its `Fragment_0` calls `GetOwningQuest().SetStage(20)` and separately sets `DA05.PlayerTalkedToHunter=True`. The Papyrus API documentation describes `TopicInfo.GetOwningQuest()` as returning the quest that owns the TopicInfo [Papyrus API documentation](https://papyrus.bellcube.dev/skyrimse/script/topicinfo/function/getowningquest/). Since DIAL `00095582` is owned by helper QUST `000955CF`, the direct stage-20 receiver is the helper quest, not main DA05.
3. Helper QUST `000955CF` maps stage 20 to `QF_dunBloatedMansGrottoQST_000955CF.Fragment_2`. That fragment gets alias `Hunter00_JKier`, calls `Kill` on the reference, then requests `DA05.SetStage(60)`. Main DA05 stage 50 maps to `Fragment_7`, which requests helper `SetStage(10)`. The helper's stage 10 carries its Start Up Stage flag. This establishes the ordinary main-to-helper source route while leaving fresh-state execution unresolved.
4. The exact FormID census found 142 byte hits across 70 candidate records. Twenty-four records had a candidate VMAD; 18 were REFRs. All 18 REFR VMADs decode with zero errors across v4/object-format-1 and v5/object-format-2 layouts. Native xEdit cross-checks confirm both a v4 and a v5 object-property interpretation. The attached stage setters check their configured helper-stage prerequisites before calling `SetStage`; the source census does not cover loose files, every archive, native callers, or runtime indirection.

## Competing models

- H1 is supported for the mapped ordinary route: main DA05 stage 50 requests helper stage 10; the helper is not Start Game Enabled, and the INFO is attached to that helper and conditioned on its alias 57.
- H2 remains proposed: no independent helper start is identified in the bounded five-master reference/trigger screen, but dialogue availability and all possible runtime or unscanned start sources remain unresolved.
- H3 remains proposed: a request for main DA05 stage 60 does not establish that Steam AE starts or initializes the stopped quest, fills its aliases, or completes a useful transition.

The earlier interpretation that the TIF directly calls main DA05 stage 20 is corrected. The stage-20 receiver is the helper quest; the mapped helper fragment requests main DA05 stage 60. The old summary's `DA05` property reference identifies the separate `PlayerTalkedToHunter` write, not the stage-call receiver.

## Limits

This is static source research, not a vanilla reproduction. It does not establish INFO availability before normal DA05 progress, helper alias fill, the hunter's live state, fresh-state `SetStage` behavior on Steam AE 1.6.1170.0, player reachability, or any profile-specific winner. The GOG AE 1.6.1179.0 native trace remains a separate build. No OBJ-1/OBJ-2 causal edge is supported.
