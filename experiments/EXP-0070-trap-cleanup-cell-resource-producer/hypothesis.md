# Competing models

- **Q64-H1:** cleanup descendants on the captured ProcessTrapHit route do not dispatch armor skill progress for AV11/AV12.
- **Q64-H2:** at least one teardown callback or descendant reaches skill progress with AV11/AV12.
- **Producer model A:** the type-0x11 cell-context branch returns a nested object whose finalizer can reach the skill sink.
- **Producer model B:** the metadata fallback returns an object whose finalizer does not reach the skill sink.

EV-0332 maps both producer shapes but does not identify which branch is live or either returned class. It therefore distinguishes neither Q64 model.
