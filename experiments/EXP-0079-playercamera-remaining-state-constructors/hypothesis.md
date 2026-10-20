# Competing models

- Q64-H1: the ProcessTrapHit-selected cleanup callbacks and relevant descendants do not dispatch AV11/AV12 skill progress.
- Q64-H2: a selected callback or finalizer can route an armor ActorValue into skill progress.

No callback selection is tied to the ProcessTrapHit chain yet. The shared Horse/Dragon helper contains an unresolved +0x8 finalizer.
