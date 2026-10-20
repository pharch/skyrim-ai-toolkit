# Results

FreeCameraState slot+0x10 maps to FUN_1408e2480, with two direct calls and no indirect sites. Its FUN_140cd7210 helper only writes +0x120/+0x124 and itself has no calls. IronSightsState slot+0x10 maps to return-only FUN_140244650 with no calls. The shared array helper's descendants, other states, and teardown selection remain open [EV-0339].
