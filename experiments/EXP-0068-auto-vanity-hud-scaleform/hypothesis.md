# Competing models

- **Q64-H1:** captured teardown callbacks and their relevant descendants do not dispatch AV11/AV12 skill progress.
- **Q64-H2:** at least one teardown callback or descendant reaches the mapped skill-progress sink with AV11 or AV12.
- **AutoVanity submodel A:** this callback is HUD-only native dispatch; the inspected case terminates at a Scaleform command.
- **AutoVanity submodel B:** the callback invokes a native skill-progress path on the inspected branch.

EV-0330 supports submodel A for the exact native case-0x17 branch. It does not select Q64-H1 because other indirect targets and the Scaleform script remain outside scope.
