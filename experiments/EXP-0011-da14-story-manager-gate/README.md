# EXP-0011 — DA14 Story Manager gate and intro handoff

**Status:** Completed as a bounded static investigation; no gameplay result.

**Objective:** OBJ-1, locate a current Steam AE level gate and identify the record transition where it is evaluated. This experiment does not claim a level-one bypass.

**Current result:** The five official master files show one explicit `GetLevel` condition on the DA14 Story Manager start node, with a raw comparison value of 14.0 and a PlayerRef form reference. The node has one child, `DA14Start`. The screened quest and linked dialogue records contain no later `GetLevel` condition. EV-0264 maps the `DA14Start` fragment that calls `SetStage(5)` on DA14 and stops itself to stage 70; stages 30/50 start Sam's drinking scenes, which advance DA14Start at 40/60. This remains a static path result, not a level-one bypass. See [protocol](protocol.md), [results](results.md), and the linked evidence in `research/EVIDENCE.json`.

**Interpretation:** This supports a single explicit gate on the screened Story Manager path. It does not rule out another player-accessible start route or native/runtime conditions, prove a winning record for a user profile, or show that a level-one character can start DA14. Continue with Q-0002.

**Evidence:** EV-0108, EV-0212–EV-0216. The full active profile order is unavailable (EV-0110). The native xEdit attempt failed before launch through WSL PowerShell interop; raw direct-file parsing is kept distinct from a native xEdit export.
