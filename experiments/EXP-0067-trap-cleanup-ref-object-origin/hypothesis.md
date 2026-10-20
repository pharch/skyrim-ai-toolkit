# Competing models

- **Q64-H1:** final-release callbacks on the captured ProcessTrapHit cleanup route do not dispatch AV11/AV12 armor-skill progress.
- **Q64-H2:** at least one such callback or descendant reaches the mapped skill-progress sink with AV11 or AV12.
- **Receiver model A:** FUN_140744180 and likely FUN_1407445d0 operate on the PlayerCharacter layout.
- **Receiver model B:** the setter's global receiver has another runtime type with coincident offsets.

The PlayerCharacter vtable accessors and teardown accesses support model A for the FUN_140738380 helper path. DAT_143188918 remains zero in the image, so the setter's runtime receiver is not directly typed. An unknown callback is inconclusive under Q64-H1/H2.
