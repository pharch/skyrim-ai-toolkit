# Competing models and update

- **H1 — gated main selection with downstream helper:** DA02's level-30 Story Manager node is the normal main-start selector; the event-driven WEDA02 helper is downstream of DA02 running, and fixed book references are unavailable below the level-30 global.
- **H2 — independent book or callback start:** a player-readable book or another ordinary callback starts or advances DA02 while its quest is stopped and independently of the level-30 node.

The source discriminant is a bounded path from SMQN child/global through DA02 QUST flags, aliases/stages, DIAL/INFO conditions, captured scripts, and all-signature official-master reference screens. EV-0310 supports H1 for the Story Manager and WEDA02 helper and the fixed book placements. H2 remains unresolved because `DA02BookScript.OnRead` requests stage 1 when DA02 is below stage 1; stopped-quest `SetStage` behavior and a naturally available level-one copy have not been tested. A source caller is not proof of natural reachability or stopped-event SetStage behavior.
