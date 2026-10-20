# EXP-0017 — Blocked hit with worn armor: protection and skill routing

**Status:** protocol prepared; bounded GOG static path supports armor-factor calculation before blocked-hit routing; live measurement not run.

**Objective:** Q-0014 / OBJ-2. Determine whether an ordinary blocked hit can retain measurable effective armor protection while omitting Heavy/Light skill credit, and measure any Block skill cost separately.

**Static basis:** EV-0222 maps the blocked player receiver branch to AV9 and skips AV11/12. EV-0261 places AV39 plus the armor-base-factor calculation before blocked-hit bookkeeping. EV-0263 identifies the GOG PlayerCharacter slot `0xE7` getter used by that calculation; it returns a stored float but does not establish a positive value or numeric protection result. These are GOG 1.6.1179.0 static observations, not installed Steam runtime outcomes.

**Boundary:** no live test is scheduled until the exact Steam target, complete disposable profile order, clean save, and loaded read-only Observer are verified. EV-0260 records that these prerequisites are currently unavailable. No console forcing, injected effect, altered plugin, or live mutator is permitted for a vanilla reproduction claim.
