# Results

Fixed and malleable wrappers share +0x128/+0x130/+0x188 targets; their +0x158 targets both release wrapper +0x18 data. The setup path stores a wrapper backlink at hkpConstraintInstance +0x58 and adjusts references, without direct +0x40/+0x48 callback writes. Two constructor families initialize those callback fields empty. Broad scans are capped and remain receiver ambiguous [EV-0366].
