# EXP-0138 — Pre-snapshot HitData entry-point screen

**Status:** Q91 completed as a bounded official-record and GOG call-order investigation. The armor objective remains open.

**Question:** Can an official PERK entry point running before the HitData `+0x54` snapshot zero the incoming-damage value used as armor-skill points, and does the resulting route meet OBJ-2's level-one, qualifying-hit, and functional-protection requirements?

**Result:** The complete five-official-master screen found 160 rows across the nine selectors called before the snapshot. Four rows have `EPFD = 0.0`. Deft Movement is the only Player-applicable `kModIncomingDamage` zero row: its native xEdit record has a zero multiplier, a `GetRandomPercent <= 10` entry condition, and conditions for fully worn Light Armor. The other rows are attached to a quest phantom, carriage actors/horses, or a companion safety effect. A successful Deft Movement entry-point application is statically predicted to make the later `+0x54` armor-skill points input zero; the PlayerCharacter UseSkill wrapper rejects non-positive points [EV-0699], [EV-0700], [EV-0701], [EV-0221].

**Interpretation:** This is an intermittent zero-damage candidate, not a solution to OBJ-2. It does not demonstrate a qualifying damage hit with armor-provided protection, repeatable all-hit XP suppression, or level-one access to the Light Armor perk. The pinned local UESP revision is secondary grounding only [EV-0702]. No gameplay or Steam result was collected; retain the exact hit/protection/raw-AVSK requirement in EV-0260.

**Evidence and raw provenance:** The five source-file hashes, enum source commit and file hash, parser outputs, accepted native xEdit result/TSV, and revision-pinned UESP raw page hash are enumerated in the private transaction manifest. Raw captures remain below ignored `.local/`.

See [hypotheses](hypothesis.md), [predicted discriminants](expected-discriminants.md), [protocol](protocol.md), and [results](results.md).
