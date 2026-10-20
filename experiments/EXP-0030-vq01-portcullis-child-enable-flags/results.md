# Results

- Child REFR 02009742 XESP bytes are 72 77 01 02 00 D7 18 00. The parent is REFR 02017772; XESP Flags is zero, so neither opposite-parent nor Pop In is serialized.
- The child is based on ACTI 0003E726. Under the ACTI reference-flag variant, header bit 30 is Navmesh - Ground and bit 11 is Initially Disabled. Captured flags 0x40000000 set the former and not the latter.
- Parent REFR 02017772 is based on STAT 0000003B. Under the STAT variant, 0x400 is Persistent and 0x800 is Initially Disabled. Captured flags set Persistent only.
- Raw capture hashes, plugin identity, schema URL, version, and scope are recorded in EV-0282.

This supports ordinary serialized parent-state inheritance and rejects the specific inverted/Initially-Disabled model for these base records. It does not prove the loaded enable state, collision state, traversal, stage-trigger behavior, or level-one access.
