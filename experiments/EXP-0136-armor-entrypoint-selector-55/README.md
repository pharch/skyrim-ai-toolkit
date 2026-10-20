# EXP-0136 — Selector 0x55 in the cached armor-factor path

**Status:** Q89 completed as a bounded GOG static code and official-record screen; Q90 continues the armor XP question.

**Result:** The cached PlayerCharacter armor-factor visitor sends each eligible non-clothing item contribution through Actor vtable slot 0x100 using selector 0x55 before accumulation. The five official masters contain zero-setting PERK rows, including Dragonhide and Earth Stone effects linked to zero-setting perks. This is a candidate cache adjustment, not proof of active protection or zero armor XP [EV-0696], [EV-0697].

**Build boundary:** GOG Skyrim AE 1.6.1179.0 for native analysis, separate from installed Steam AE 1.6.1170.0 [EV-0109].

**Open discriminant:** Does the unblocked HitData armor-skill path use a pre-mitigation physicalDamage field and independently require positive raw armor DNAM? Q-0090 traces the exact builder/resolver dataflow; EV-0260 remains the live Steam matched-hit, protection, and raw-AVSK protocol.

**Approved action surface:** Existing GOG Ghidra project and official five-master source files, read-only. No game launch, save, console, plugin, or profile winner claim.
