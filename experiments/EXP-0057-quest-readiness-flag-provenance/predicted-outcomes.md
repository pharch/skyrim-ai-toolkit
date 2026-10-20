# Predicted outcomes

- **H1:** the QUST parser's `DNAM` branch writes the first U16 to `+0xDC`; decoded bit 0 matches the exact source `DNAM.General.Flags` value. DA04 predicts bit 0 set; DA02, DA06, and DA09 predict it clear. EV-0316 observes this source-to-field mapping in GOG code.
- **H2:** the parser does not connect the serialized flag to `+0xDC.0`, and independent initialization would be needed to explain the source comparison. EV-0316 falsifies H2 for the inspected load-time path.
- **H3:** a virtual method clears bit 0 under a condition after the source value is copied. EV-0316 confirms that code exists at TESQuest slot 19; a callsite/order trace or read-only before/after observer is needed to establish timing.

The SetStage entry predicate, quest startup, callback reachability, running state, aliases, journal/dialogue, physical access, and numeric player level remain separate evidence requirements.
