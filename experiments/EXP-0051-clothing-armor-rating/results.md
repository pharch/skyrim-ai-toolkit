# Results

## Official record screen

The strict-dispatcher source screen parsed all 3,835 ARMO records from the five configured official masters. TES5Edit dev-4.1.6 defines BOD2's Armor Type values in order as Light Armor (0), Heavy Armor (1), and Clothing (2); ARMO DNAM is a signed armor-rating value divided by 100. The ARMO header flag bit index 2 is Non-Playable. Schema source: `https://raw.githubusercontent.com/TES5Edit/TES5Edit/dev-4.1.6/Core/wbDefinitionsTES5.pas`, lines 2143–2147, 2220–2241, 2235–2276, and 3879–3920.

The five files contain 40 source rows with BOD2 type 2 and positive DNAM, representing 36 unique official FormIDs because Update.esm has four overrides of Skyrim.esm records. Twenty-two unique records have the Non-Playable flag clear; this flag screen does not establish natural acquisition or gameplay protection. Source counts and hashes are in EV-0309.

The resolved ARMO armature graph contains 56 ARMA links across those 36 unique records, and every linked ARMA uses BODT/BOD2 Armor Type Clothing. It reveals no ARMO-versus-ARMA class mismatch in the screened set. A concrete low-rating candidate is Skyrim.esm ARMO `00013105 ClothesBeggarRobes`: BOD2 type 2, DNAM raw 100 (schema-scaled value 1.0), and linked ARMA `00013101 BeggarTorso01AA` also has Clothing type. `NPC_ 00013BA7 Brenuin` uses `OTFT 00028B61 BeggarWithHatOutfit`, which includes the robe; placed ACHR `0002C90F BrenuinBeggerRef` has XLCN `00018A56 WhiterunLocation`. This is a possible natural acquisition lead, not a confirmed player inventory or level-one route.

## Hit-skill and protection-side source comparison

GOG AE 1.6.1179.0 EV-0222 shows the unblocked player-receiver selector skipping worn ARMO subtype 2 and requiring positive base DNAM before choosing AV11/AV12. This creates a source-level route by which Clothing records could avoid that Heavy/Light eligibility scan.

Fresh matching-GOG Address Library and read-only Ghidra queries resolve `VTABLE::Actor` slot 0xE7 to a zero-returning stub and `VTABLE::PlayerCharacter` slot 0xE7 to a function that returns a float from `this+0x274`; when negative, it calls virtual slots 0xCA and 0xE6 before returning that field. EV-0261 shows the HitData builder uses the PlayerCharacter armor-factor result in its damage calculation. The getter does not inspect worn ARMO entries, and this query did not identify the field's writers or show whether type-2 Clothing DNAM contributes. The PlayerCharacter Ghidra query's identity, slot, disassembly, and decompilation checks passed; its overall `ok` is false only because a direct call xref is absent for the vtable target.

The record census confirms positive-rating Clothing items exist and the GOG XP selector skips their class. It does **not** distinguish whether the protection-side field includes their rating. No installed-Steam code mapping, numeric protection delta, AVSK change, or vanilla reproduction was observed. Do not call Clothing protective based on DNAM alone.

## Discriminating test and limits

On verified Steam AE 1.6.1170.0 with a complete exact active order and clean disposable level-one save, compare a naturally acquired positive-DNAM type-2 item (candidate `ClothesBeggarRobes`, if its acquisition is confirmed in that profile) against a no-armor control. Use the same nonmagical unblocked weapon attack, attacker, difficulty, and player state; verify qualifying hits and equal baselines, then capture numeric pre/post health, Heavy Armor AVSK, Light Armor AVSK, and player level across enough hits to detect delayed or rounded progress. A candidate passes only if incoming hits measurably reduce damage while both armor AVSK deltas remain exactly zero and the character stays level 1. No console/item injection, altered plugin, or forced state belongs in the vanilla sequence.

The current live lane lacks the selected disposable profile/full order, clean test save, deployed/loaded observer, and numeric skill-state capture prerequisites recorded by EV-0260. Static research therefore establishes a promising classification candidate and exact external discriminator, not a bounty result. No causal connection to OBJ-1 quest-start findings is supported.
