# Results

## Static observations

- REFR `00000EC8` is in CELL `0003D62B` (`DA14Interior`) and has a `defaultsetStageTrigSCRIPT` VMAD with `myQuest=DA14`, `stage=406`, `doOnce=true`, and `disableWhenDone=true` after schema-backed decoding.
- The bounded cell group scan found one XTEL-linked reference: interior portal REFR `0003DC3F` points to exterior REFR `0003DC45` in `Morvunskar01`.
- The exterior `SanguinesRealmDoorRef` carries record flags `0x00000C00`. TES5Edit schema maps door-reference bits 10 and 11 to Persistent and Initially Disabled. The reference has no XESP parent.
- Both checked DA14 QUST VMAD records map `QF_DA14 Fragment_53` to stage 135/log entry 0; stage 135 exists in both stage tables. The PEX fragment enables alias 36's initially-disabled XMarker REFR `0003DC43`.
- Marker `0003DC43` is the XESP parent of initially-disabled Morvunskar trigger REFR `0003DC42` (`dunda14PortalTriggerREF`). The trigger uses base ACTI `0003DC40`, whose `dunda14PortalScript` properties include `myDoor=0003DC45`, the initially-disabled exterior portal door. The PEX control flow is not known.
- `dunda14PortalScript` was not found by the supported Skyrim - Misc.bsa extractor (BSA v105, 17,713,449 bytes, SHA-256 `ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d`) or the exact loose `Scripts`/`Scripts/Source` checks. Other archives were not searched.
- The Skyrim.esm DA14 QUST and its Update.esm override list stages 0 through 200 and do not define 406. This is scoped direct-parser output, not a profile-specific winner or native xEdit export.

## Runtime result

Not run. No complete disposable profile/order, clean level-one test save, or loaded Observer is configured. No ordinary travel attempt, trigger callback, quest-running state, or stage transition was observed.

## Follow-up official-master reference screen

EV-0275 extends the direct-parser screen across all five installed official masters. It byte-scans every VMAD subrecord plus all subrecords on the enumerated writer-candidate signatures for the exact DA14, DA14Start, trigger, portal, and DA14Interior FormIDs. It found no new direct record candidate that places/moves the player into DA14Interior or starts/enables DA14 before the helper. This is a raw candidate screen with explicit signature and field limits, not native xEdit reverse references or an exhaustive code scan.

The Update.esm candidates are `Patch1_4_UpdateQuest` and REFR `0100080D`; their portal/DA14 properties match the separate cleanup route already traced in EV-0264. Its QF fragment checks `DA14.GetStageDone(200)` before disabling the portal door, FX, light, and enabler. The fragment contains no DA14 Start, SetStage, or MoveTo operation. Dragonborn's `DLC2DialogueRavenRock` DA14 alias remains unresolved as in EV-0264. A HearthFires `MISC/FULL` raw byte match for `00000EC8` was not a decoded reference and is not counted as a writer.

## Limits

`defaultSetStageTrigScript.pex` was not found by the tested Skyrim - Misc.bsa extractor or exact loose-file checks (EV-0250). The separate activation script `dunda14PortalScript.pex` was also not found by that supported extractor or its exact loose-file check (EV-0251, rechecked in EV-0275); this is not a global archive/source absence. Other scripted/native entry paths, profile overrides, portal-script behavior, and the effect of setting an undefined stage remain unknown. The exact level-one runtime discriminator still needs a complete disposable order/save and a read-only observer, absent in EV-0260. Raw captures and hashes are preserved under ignored `.local/` and registered in EV-0250/EV-0251/EV-0275.
