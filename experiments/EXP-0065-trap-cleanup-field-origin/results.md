# Results — PlayerCharacter cleanup field and camera callback

EV-0327 resolves the PlayerCharacter teardown's global slot-0 callback through `PlayerCamera::vftable` to `FUN_1408e8b50` -> `FUN_1408e4070`. The camera cleanup body retains five indirect resource calls. The primary PlayerCharacter vtable query maps slot `0x98` (byte offset `+0x4C0`) to `FUN_1407373e0`; its cell/location transition path reads/clears `PlayerCharacter+0x730`, may call inner slot `+0x1C0`, and conditionally releases through slot `+0x8`.

The complete GOG `+0x730` displacement scan reports 67 operands, 13 writer functions, and complete direct/computed writer analysis. Attributed PlayerCharacter paths show null initialization and clearing; no non-null direct or computed writer was identified. Alias/copy writes and the field's dynamic type remain unknown. The same displacement occurs on unrelated structures.

Q-0064 H1/H2 remain unresolved. The inner target, five PlayerCamera indirect sites, and four other PlayerCharacter final-release fields remain open. No Steam runtime, positive-damage/protection result, or raw AVSK capture exists [EV-0327], [EV-0325], [EV-0319], [EV-0324], [EV-0261], [EV-0260].
