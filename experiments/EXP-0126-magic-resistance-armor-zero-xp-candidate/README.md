# EXP-0126 — Magical resistance armor and hit-XP route

- **Frontier:** Q-0077 (OBJ-2)
- **Question:** Can level-one-accessible positive-DNAM Light Armor reduce a verified magical hit while that hit supplies non-positive points to the Heavy/Light armor skill selector? Keep a bypassed selector distinct from suppressed XP on an eligible hit.
- **Candidate lead:** Skyrim.esm ARMO `0002AC61` (`DA05SaviorsHide`), whose source record has EITM `001097B7`; its full enchantment chain and source availability are still being checked. The item-page claim is secondary-source grounding only.
- **Starting evidence:** EV-0221–EV-0223 and EV-0261 map the GOG AE 1.6.1179.0 points guard, inline armor selector, and parts of HitData construction. EV-0398–EV-0402 map a separate resistance ActorValue path. EV-0260 preserves the exact Steam live discriminator and its current capability limits.
- **Scope:** Exact official-master ARMO/ENCH/MGEF and DA05 source path; read-only GOG 1.6.1179 call/dataflow from magical-hit producer through HitData and any AV11/AV12 award. Steam behavior, profile winners, level-one completion and actual damage remain separate.
- **Protocol and outcomes:** [protocol](protocol.md), [hypotheses](hypothesis.md), [discriminants](expected-discriminants.md), [results](results.md), [implications](implications.md), [schema notes](schema-notes.md).
