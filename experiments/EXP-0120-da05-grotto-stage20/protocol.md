# Protocol

1. Confirm the installed Steam executable identity and use only the fixed official five-master xEdit source view for native record semantics.
2. Export nested INFO `00095585` and parent DIAL `00095582` by exact FormID/EditorID; query helper QUST `000955CF` by EditorID. Keep raw parser outputs alongside the native exports.
3. Resolve the INFO's `GetIsAliasRef` parameter to helper alias 57 and its forced reference. Confirm the DIAL's QNAM owner and INFO child.
4. Map the main DA05 QF fragment that sets the helper quest's stage 10 to its native QUST stage. Compare that with the helper QUST's Start Game Enabled flag, stage-0 behavior, and exact five-master incoming reference candidates.
5. Resolve `TopicInfo.GetOwningQuest()` against the INFO's parent DIAL owner. Trace the TIF's helper-quest `SetStage(20)` through the helper QF stage fragment to the main DA05 `SetStage(60)` request, and keep the TIF's `PlayerTalkedToHunter` property write separate. Compare the main-quest request with the separately build-attested GOG `Quest.SetStage` path; do not transfer GOG RVAs or runtime outcomes to Steam AE 1.6.1170.0.
6. Preserve source identities, hashes, raw matches, and the failed bounded INFO-by-signature query. Treat direct references and PEX calls as candidates until their runtime conditions are observed.
7. Record an exact clean level-one test that separately observes helper quest state, alias fill, INFO availability, callback execution, main DA05 state, level preservation, and functional access.
