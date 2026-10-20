# Protocol

## Static GOG/source trace

1. Validate the existing GOG project identity and route each query through `python3 scripts/python_env.py run` with the read-only adapter, `-noanalysis`, and no binary import/reanalysis.
2. Anchor `TESQuest+0xDC` in the constructor-installed TESQuest vtable and trace the exact QUST `DNAM` parser branch. Keep legacy `DATA`, `DNAM`, and `ENAM` writes distinct.
3. Decode `DNAM.General.Flags` against the versioned TES5Edit `dev-4.1.6` QUST schema, then retrieve exact DA02, DA04, DA06, and DA09 records through the direct TES4 parser. Preserve source identity; do not call them xEdit exports or profile winners.
4. Inspect scoped constructor/helper/mutator candidates and describe their machine behavior without assigning an undocumented semantic method name. Keep load-time copy separate from later mutation.
5. Capture raw outputs under ignored `.local/`, record build and artifact hashes, and register a durable evidence note before closing the bounded question.

## Runtime discriminator

To establish the field actually read by a natural callback, use verified Steam AE 1.6.1170.0, the complete exact target order, a disposable level-one save, and a read-only observer. Capture the source quest running state, numeric player level, stage, serialized and runtime event type, `+0xDC` bit state if safely exposed, Story Manager context, aliases, journal/dialogue, and functional access before/after a naturally reachable callback. Compare a no-callback control. Do not force stage, level, flags, event context, aliases, or plugin state.
