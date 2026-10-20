# EXP-0045 — ProcessTrapHit receiver indirection and armor skill credit

## Objective

Resolve the remaining indirect and virtual callsites in the GOG ProcessTrapHit receiver handler that could conceal an AV11/AV12 armor skill award.

## Scope

Static analysis uses only the existing GOG Skyrim AE 1.6.1179.0 Ghidra project and matching Address Library, read-only. Steam AE 1.6.1170.0 remains a separate runtime target. This dossier does not infer positive worn-armor protection, raw AVSK behavior, or a vanilla exploit from callgraph findings.

## Status

EV-0303 classifies all 28 enumerated sites into the visible AV15 call, mapped Actor/ActorMagicCaster branches, ActorValueOwner Health/Stamina operations, four TESObjectREFR source-reference accessors, and thirteen release-style cleanup calls. EV-0315 traces two temporary handles and the HitData sourceRef through generic handle helpers, but does not resolve concrete cleanup target classes. No mapped AV11/AV12 award is identified. Derived reference overrides, Steam gameplay, and effective protection remain unresolved.
