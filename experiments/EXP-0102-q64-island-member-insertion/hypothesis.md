# Competing models

- H1: endpoint +0x130 is its hkpSimulationIsland pointer; island +0x60/+0x68 EntityPtrs stores endpoints, and endpoint +0x100/+0x108 stores constraint records.
- H2: matching offsets and serializer labels belong to different owner paths, so endpoint +0x130 does not identify the island used by EntityPtrs.

Exact attach read/assignment, typed initialization, serializer, insertion and merge discriminate H1/H2. Live ProcessTrapHit identity and AV11/AV12 remain separate.
