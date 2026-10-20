# Implications

- **Candidate not yet established:** the exact ARMO record has a positive raw DNAM field and a linked EITM FormID, but the ENCH/MGEF semantics and the candidate's level-one acquisition remain under investigation.
- **No XP-suppression claim:** a magical attack that bypasses the AV11/AV12 selector is not a qualifying zero-XP armor hit. Preserve this distinction in source and any later live protocol.
- **Cross-domain status:** DA05's source-level level gate and the armor hit selector are currently separate paths. No causal edge to OBJ-1 is justified unless a shared native call, ActorValue, HitData field, or saved state is demonstrated.
- **Steam result remains open:** the exact clean level-one hit, effective protection, profile winner and raw AVSK comparison are unavailable under EV-0260. No vanilla reproduction is claimed.

## Evidence update — 2026-10-18

The official Skyrim.esm records now establish Savior's Hide as a positive-DNAM Light Armor source candidate with Resist Magic AV44 and Resist Poison AV40 enchantment effects [EV-0415], [EV-0416]. Its DA05 stage-100 reward path is source-backed, but the clean level-one acquisition remains untested. The fresh GOG captures do not connect the virtual `MagicTarget::CheckResistance` callsite to the AV11/AV12 selector, so H1/H2 remain open and zero XP from a pure magic-only hit would not by itself prove suppression [EV-0417]–[EV-0421]. The old DA05-to-armor-XP route remains unsupported: no shared call, ActorValue, HitData field, or serialization edge was found.
