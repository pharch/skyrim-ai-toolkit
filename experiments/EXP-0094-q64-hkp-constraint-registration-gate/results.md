# Results

The factory-created hkpConstraintInstance uses an exact slot+0x30 target that returns zero. FUN_140b3a830 therefore skips its conditional FUN_140b3ac30 branch for this object. The path remains physics registration/reference handling; this does not classify other callers or the remaining ProcessTrapHit sites [EV-0356].
