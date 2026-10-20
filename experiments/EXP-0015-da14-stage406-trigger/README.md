# EXP-0015 — DA14 stage-406 trigger access path

**Status:** Bounded static investigation; no gameplay result.

**Objective:** OBJ-1. Determine whether REFR `00000EC8` can start or advance DA14 before its level-14 Story Manager helper.

**Current assessment:** The trigger is in `DA14Interior`, its sole screened teleport link uses an initially-disabled Morvunskar door reference, and neither Skyrim.esm nor the Update.esm DA14 override defines stage 406. The expanded five-master raw FormID screen found no new direct record-level MoveTo/Enable/start candidate; the Update.esm branch it found is portal cleanup after DA14 stage 200 (EV-0275, with PEX detail in EV-0264). This supports a downstream trigger for the examined official-file routes. Dynamic/native paths, profile winners, and the undefined-stage runtime result remain open; no level-one gameplay result is claimed.

See [hypothesis](hypothesis.md), [protocol](protocol.md), [predicted outcomes](predicted-outcomes.md), [results](results.md), and [implications](implications.md). Evidence: EV-0109, EV-0111, EV-0112, EV-0212–EV-0216, EV-0250.
