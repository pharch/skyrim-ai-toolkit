# Implications and next actions

EV-0314 resolves the GOG/source mapping: DA02, DA09, and DA06 `ENAM=LEVL` values reach the field tested by the GOG SetStage guard. A clear ready bit blocks this initial callback path; a set bit can pass the initial OR check, with later state guards still unknown. This narrows the static mechanism but does not establish a bypass.

The decisive gameplay test remains on verified Steam AE 1.6.1170.0 with a complete target order and clean level-one save. A read-only observer must capture the numeric level, exact quest event ID and ready bits before/after a naturally reachable source callback, SetStage reachability, EnsureQuestStarted outcome, running/stage state, Story Manager context, aliases, journal/dialogue, and functional access; compare with an ordinary no-callback control. No console forcing, script injection, or altered plugin can validate the candidate. Continue independent P0 work while that runtime lane remains unavailable.

No OBJ-2 edge is predicted; none is supported by current evidence. After the static field trace, continue with the highest-information ready OBJ-1 or OBJ-2 question while preserving the exact Steam observer prerequisite.
