# Protocol

## Goal

Resolve the record-level lead that a Drain Vitality-labelled Dawnguard shout can be associated with MFD words. Test whether its actual linked spells reference the MFD AV39 effect, while keeping acquisition, target, alias, and runtime claims separate.

## Inputs and boundaries

- Use installed official-master source records only. The retained `tools/xedit_bridge.py file-records` entrypoint is a direct read-only TES4 parser; it does not launch xEdit or resolve profile winners.
- Preserve each wrapper/raw record capture below ignored `.local/alignment/transactions/TX-20261016-0010/` and record hashes.
- Treat the private Apocrypha result as an untrusted lead; do not copy message text into tracked files.
- Use UESP page titles, revisions, and URLs as secondary context, not as proof of installed record links or runtime behavior.
- Do not launch the game, alter plugins, force acquisition, target, stage, or ActorValues, or treat an injected state as a vanilla reproduction.

## Steps

1. Capture the Drain Vitality-labelled Dawnguard SHOU records and read their word and spell FormIDs.
2. Capture each linked SPEL and enumerate its EFID MGEF FormIDs.
3. Capture each linked MGEF plus the candidate MFD AV39 MGEF `0010319D`; decode archetype and primary ActorValue using the established MGEF schema.
4. Compare the custom SPEL payload against the native Drain Vitality records and the base MFD records/list evidence in EV-0241/EV-0257.
5. State only the bounded record result. Keep the Script archetype, quest acquisition, target, profile winner, alias fill, raw AV39 delta, and armor XP outcome unresolved unless independently evidenced.

## Reproduction route

Use the retained dispatcher and exact installed-file forms recorded in EV-0273, for example:

```sh
python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature SHOU --plugin Dawnguard.esm --form-id 02018244
python3 scripts/python_env.py run tools/xedit_bridge.py file-records --signature SPEL --plugin Dawnguard.esm --form-id 02018243
```

Repeat for the other captured SHOU/SPEL/MGEF forms listed in EV-0273. A direct parser result must not be described as native xEdit output or a winning-record result.
