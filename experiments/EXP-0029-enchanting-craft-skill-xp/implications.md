# Implications

The source trace narrows the ordinary Enchanting credit producer to the workbench's `usesSkill` field and one craft-confirmation `UseSkill` dispatch. It does not establish the amount or prove the UESP revision 3538992 statement that craft base XP is one per enchantment and unaffected by item value, selected enchantment, or soul level (EV-0124).

The same PlayerCharacter skill-progress sink handles the GOG armor/Block skill-use calls already traced in EV-0217–EV-0223. This supports a shared award-side primitive across Enchanting and incoming-hit XP, while the caller-specific points producers remain different. It adds a useful comparison point for future XP-suppression work, but it does not connect Enchanting to armor mitigation or level-gated quest start.

The highest-value next test is a raw AVSK before/after capture on a verified Steam 1.6.1170.0 disposable save, comparing one and two identical crafts and one-factor item-value/soul-size controls while holding perks and modifiers fixed. Current tools cannot supply that raw measurement; continue independent OBJ-1/OBJ-2 research under the live-lane gates recorded in EV-0260.
