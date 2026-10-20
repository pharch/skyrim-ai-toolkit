# Results

The earlier `hkpSimulationIslandAndEntity` label was a boundary error. FUN_1400d8fe0 passes the exact name `hkpSimulationIsland`; adjacent bytes are separate field labels. Its table includes an entity/constraint serializer and add/remove callback bridges, but the exact ProcessTrapHit instance is not proven to enter the island list. Whole-program +0x60/+0x68 scans counted 14,003/8,295 accesses but printed only the first 2,048 each, stopping before the 0x140b physics functions; no B-range writer conclusion follows [EV-0362], [EV-0363].
