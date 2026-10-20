# EXP-0049 — DA13 dialogue start gate and direct reference screen

## Question

Can a DA13-owned player-dialogue fragment start or advance main DA13 before its level-12 Story Manager path, and do other official records call into DA13 or its helper?

## Competing models

- **H1, dialogue bootstrap:** an INFO owned by stopped DA13 can be offered, and its unconditioned stage-21 `SetStage` starts the quest.
- **H2, running-owner gate:** DA13-owned INFOs are evaluated only while DA13 is running; the stage-21 fragment is downstream, while the Refugee-to-helper handoff remains level-gated.
- **H3, external writer:** a record/script outside the already-screened QUST/DIAL/INFO set independently references DA13 or `Da13Intro` and starts or stages it.

The discriminants are engine evidence for the dialogue owner gate, complete record-type coverage for direct FormID references in the five official masters, and an exact-target dialogue observation if static evidence cannot settle H1 versus H2.

## Scope

Static source screening only. The installed Steam runtime is 1.6.1170.0 (EV-0109); no active-profile order or live dialogue state is verified. The existing GOG 1.6.1179.0 project is separate and can provide mechanism predictions only. This experiment does not validate level-one access or a vanilla reproduction.

## Result

The source captures support a serialized level-10 WEJS14 Refugee/helper/scene chain that calls `Start()` on main DA13, below the ordinary level-12 Story Manager node. The source sweep also found an unconditioned main-owned stage-21 dialogue writer, but stopped-owner dialogue availability remains unresolved. See [results](results.md) and [implications](implications.md); evidence is EV-0307.
