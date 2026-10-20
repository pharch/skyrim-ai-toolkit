# Protocol

## Build, profile, and lane

- Static lane: existing GOG AE 1.6.1179.0 Ghidra project, matching GOG Address Library, and local CommonLibSSE-NG commit `b93280e832f263dbef44e44cbe2936622a02f91a`.
- Record lane: installed official Skyrim.esm source file. Steam executable identity is separately verified as AE 1.6.1170.0 in EV-0109.
- Runtime lane: **not scheduled**. EV-0260 records no selected disposable profile/save or loaded Observer. The documented save reader only scans headers, strings, FormIDs, and byte patterns; it does not decode raw AVSK progress. The staged Observer does not capture native skill use, crafting transactions, or AVSK. Do not launch a game or claim a negative from this missing lane.
- No active-profile winner is inferred from the base Skyrim.esm record. No game, save, co-save, or plugin was modified.

## Static commands and captures

All commands use the strict Python dispatcher and read-only paths.

1. Resolve `VTABLE::PlayerCharacter`, then inspect vtable slot `0xF7` and its direct callee:

   `python3 scripts/python_env.py run tools/address_library_probe.py --symbol 'VTABLE::PlayerCharacter'`

   `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x18ACD70 --vtable-slot 0xF7 --follow-incoming-calls 16 --follow-direct-calls 4`

2. Resolve and inspect the EnchantMenuCraftCallback vtable slot 1:

   `python3 scripts/python_env.py run tools/address_library_probe.py --symbol 'VTABLE::CraftingSubMenus__EnchantConstructMenu__EnchantMenuCraftCallback'`

   `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x18F6900 --vtable-slot 1 --follow-direct-calls 8 --follow-incoming-calls 8`

3. Read the one official base workbench record using the configured Skyrim Data directory:

   `python3 scripts/python_env.py run tools/plugin_reader.py record <SKYRIM_DATA>/Skyrim.esm --signature FURN --form-id 000BAD0D --include-subrecords`

   The parser is direct TES4 parsing, not xEdit and not an active-order winner query. Interpret `WBDT` only against the hashed CommonLib `TESFurniture.h` and `ActorValues.h` sources recorded under EV-0281.

## Future raw-XP experiment — prerequisites

Do not execute until the target's Windows `ae_preflight.py` confirms the intended Steam executable and the complete selected plugin order; if MO2 manages that target, use that profile's explicit full `plugins.txt`. Also require a clean, duplicated disposable level-one save and a validated read-only instrument that reports the Enchanting raw progress field before and after each craft. No such AVSK reader or live Observer field is currently verified. Do not substitute the UI skill level or an unverified console/API method for raw progress.

Use two independent disposable baseline copies for the level-15 and level-20 cases. Record the save/runtime/load-order hashes, character level, Enchanting base level, exact raw progress and next-level threshold, available perks, station, inventory, selected item/effect/soul gem, and any skill-use modifiers. Keep modifiers and all unvaried inputs fixed. Do not use console, scripts, altered plugins, or injected state in the vanilla-candidate lane.

1. On matched copies, craft once using the same base item, effect, and soul-gem size; compare the raw Enchanting progress delta.
2. Repeat with only soul-gem size varied, then with only base-item value varied. Record the created item's actual effect and magnitude so the craft is useful, and record any character-level or Enchanting-level change.
3. On one copy, make two otherwise identical crafts and capture progress after each operation. This tests cumulative credit and threshold visibility.
4. A two-effect enchantment requires the Extra Effect perk and is not an ordinary level-15/20 control. If tested with a forced perk or other diagnostic intervention, label that lane `diagnostic_intervention`; do not treat it as vanilla validation.

## Controls, rollback, and interpretation

- Negative control: capture the same baseline without crafting and verify the instrument reports no raw progress change.
- Positive control: perform one ordinary, known successful craft on a separate copy to verify the observer's AVSK readout and item output.
- Rollback: discard only the disposable copies after preserving their raw captures; never overwrite the source save or co-save.
- H1 is supported if a one-factor change produces a reproducible raw-progress delta difference or step. H2 is supported if matched one-craft deltas are equal while repeated crafts accumulate progress before the displayed skill level crosses its threshold. Both may partially hold if the station award is fixed but downstream modifiers/rounding vary.
- Capture every before/after raw AVSK value, exact craft input and output, base level, threshold, character level, build/profile identity, tool version, and complete instrument output below ignored `.local/`.
