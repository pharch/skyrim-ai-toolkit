# Results — EXP-0025

## Observed

- The VQ01 main QUST owns the `Book` alias. Its forced REFR is `0200D072`, whose base is BOOK `0200D070`, in Crypt02. The alias script's read callback requests stage 17; player receipt requests stage 17 only after stage 15.
- VQ01 stage 10 enables `VQ01EnableMarker`, which is the XESP parent of the forced book reference. The gate-side VQ00 helper starts VQ00 and advances VQ01's misc objective, whose fragment requests VQ01 stage 10.
- Three `defaultsetStageTrigSCRIPT` references were found in the bounded scan: Crypt01 stage 15 (optional prerequisite 10), Crypt02 stage 17 (no optional prerequisite property), and Crypt02 stage 18 (optional prerequisite 17).
- The tested extractor could not find `defaultsetStageTrigSCRIPT.psc` in the supported Misc-BSA stream; exact output and hash are in private EV-0276 captures. This is not evidence that the script is absent from other supported scopes or that its behavior is inert.
- The screened entrance/intercell door refs carry flag `0x400`, which EV-0250's TES5Edit schema maps to Persistent; they do not set `0x800` (Initially Disabled) and have no XESP parent. The UESP Dimhollow page separately describes a rubble gate before the quest starts. Neither source resolves collision geometry, trigger activation state, or a player-only route.

## Assessment

H2 is supported for static alias ownership and book placement/configuration; H1's pre-gate runtime claim is not demonstrated. The stage-17 reference is a separate candidate with unresolved script semantics and access. No profile-specific winning record, alias-fill observation, level-one route, or quest transition was captured. No causal edge to OBJ-2 armor/XP mechanisms is supported. See EV-0276, M-0028, C-OBJ1-VQ01-BOOK-ALIAS, C-OBJ1-VQ01-STAGE17-TRIGGER, and Q-0021.
