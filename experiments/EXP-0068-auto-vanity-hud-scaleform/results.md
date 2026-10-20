# Results — AutoVanity HUD dispatch

EV-0330 traces AutoVanity to queued message type 0x17 under the HUD Menu key, then through the registered HUDMenu vtable slot +0x20 to FUN_14091eed0. The exact case builds UI values and calls FUN_140fadb20 with Scaleform method `ShowElements`. For this call the optional native callback is zero. The captured native branch has no Actor skill-progress sink.

This bounds only one PlayerCamera callback branch. The Scaleform script and other teardown indirect targets are unresolved, so Q64-H1/H2 remain proposed [EV-0330], [EV-0329], [EV-0328], [EV-0327], [EV-0325], [EV-0319], [EV-0324].
