# Results

FirstPersonState slot+0x10 maps to FUN_1408e0e70, which clears +0x68 and calls the mapped array helper; its body has zero indirect sites. BleedoutCameraState slot+0x10 maps to FUN_1408e03d0, which final-releases +0x120 through an unresolved slot+0x8 and calls three playback/event helpers. No direct AV11/AV12 sink appears in the captured callback bodies or three direct Bleedout callees. Other descendants, the finalizer, and teardown state selection remain open [EV-0338].
