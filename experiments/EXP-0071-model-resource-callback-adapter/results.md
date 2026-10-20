# Results

EV-0333 traces FUN_140216b40 from a generic resource handle to FUN_140d19980, whose two unresolved adapter slots are +0xB8 and +0xE8. Its caller passes the returned pointer into the EV-0329 candidate +0x9A0/+0x9A8 setter path. The recursive hierarchy test does not expose the selected root class. The final slot+0x8 target and AV11/AV12 descendants remain unknown. Q64-H1/H2 remain proposed [EV-0333], [EV-0329], [EV-0325].
