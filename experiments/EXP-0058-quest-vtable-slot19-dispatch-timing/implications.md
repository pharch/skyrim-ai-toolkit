# Implications and next actions

The immediate action is to inspect slot-19 function-pointer references and search for indirect call operands at vtable displacement `0x98`, then classify each candidate using TESQuest vtable provenance. A raw displacement hit is not sufficient to attribute a caller.

If call timing remains unresolved, the discriminating runtime capture is a verified Steam AE 1.6.1170.0 target with a complete order and a read-only observer of the affected quest's `+0xDC.0` before/after natural load and callback delivery. Do not force flags, event context, level, stage, or aliases. Keep the OBJ-2 positive-damage/protection/raw-AVSK experiment open independently.
