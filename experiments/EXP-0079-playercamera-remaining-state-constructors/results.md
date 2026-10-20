# Results

State indices 2, 7, 10, and 12 resolve as VATSCameraState, TweenMenuCameraState, HorseCameraState, and DragonCameraState. Their slot+0x10 methods are respectively the previously observed no-op FUN_140244650, a field-copy FUN_1408eb830, and two wrappers that share FUN_1408e9990. The shared helper releases a +0xA0 member and may call its virtual +0x8 finalizer. No direct AV11/AV12 skill sink appears in the captured bodies [EV-0341].
