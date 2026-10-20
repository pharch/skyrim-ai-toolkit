# EXP-0020 — DA07 exterior trigger and stage-7 start

**Status:** vanilla candidate supported by a bounded static trigger path; live transition unresolved.

**Question:** Q-0019 / OBJ-1. Can `DA07IntroTrigger` set DA07intro to stage 7 before the level-20 Story Manager helper, and does that produce a functional level-one initiation?

**Static lead:** REFR `000B1403` is in DawnstarExterior04, has no XESP enable parent in the direct record, and accepts Silus and Madena as its two required target actors. Its scripts call DA07intro `SetStage(7)` when both enter; the stage-7 fragment starts DA07IntroScene. EV-0266 preserves the records, script hashes, and API-source limit.

**Open:** ordinary co-entry timing, exact-build SetStage initialization, alias fill, scene functionality, and level-one state change remain unobserved. The next step is a clean natural-play discriminator after target/profile/save prerequisites are satisfied.

See [protocol](protocol.md) and [results](results.md). This is not a reproduced bypass.
