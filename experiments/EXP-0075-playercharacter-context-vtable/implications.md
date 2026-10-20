# Implications

The slot +0x378 getter is now mapped, but it conditionally returns a context-selected pointer. This narrows the source side of the ThirdPersonState+0xA0 path without establishing a shared scene-graph class or an AV11/AV12 result. Preserve the +0x730, +0x8F8, +0x9A0/+0x9A8, and +0xA0 paths separately until exact class evidence exists.
