# Results

AnimatedCameraStartHandler entry 1 forwards its third argument into FUN_1408e6500 with flag 0 [EV-0344]. AnimatedCameraDeltaStartHandler entry 1 forwards its third argument into the same helper with flag 1. Their cleanup functions identify the base interface as IHandlerFunctor<Actor,BSFixedStringCI>, making a fixed-string argument interpretation consistent but not runtime-observed. The slot +0x150 receiver and returned member type remain unknown [EV-0345].
