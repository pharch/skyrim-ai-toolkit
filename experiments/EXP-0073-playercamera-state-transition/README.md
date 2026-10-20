# EXP-0073 — PlayerCamera state transition

Trace PlayerCamera+0x28 from active-state replacement into the index-9 ThirdPersonState slot+0x10 callback. The callback has two direct helpers and one nested refcount release still to screen. EV-0335 narrows one teardown branch; Q-0064 remains open.
