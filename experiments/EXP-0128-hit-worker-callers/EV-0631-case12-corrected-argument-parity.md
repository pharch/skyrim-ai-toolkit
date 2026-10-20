# EV-0631 — Correct tag-0x12 callsite and exact argument parity

## Scope and source identity

This is static GOG AE 1.6.1179.0 disassembly/decompilation from the existing read-only Ghidra project. The verified analysis binary SHA-256 is `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`; auto-analysis was disabled and no binary/project import or overwrite was attempted. These GOG RVAs are not transferred to Steam AE 1.6.1170.0.

## Competing models and discriminants

- H1: tag-0x12 deferred dispatch exactly matches the immediate AddRagdollHandler slot `+0x1a8` call, including argument five and a zero sixth argument. It predicts that the case-0x12 callsite stores zero at `[RSP+0x28]`, forms `[RSP+0x20]` from the payload dword, and sets `R8=1`, `R9=1`.
- H2: the deferred route inherits a different/nonzero sixth argument or takes argument values from the previously attributed callsite at RVA `0x65939c`. It predicts a nonzero byte at the actual case-0x12 call or a callsite that belongs to that case.

The exact discriminant is the dispatcher switch case paired with the instructions at the actual tag-0x12 virtual call, checked against the producer call and builder payload offsets.

## Direct evidence

- The caller-50 producer invokes `(*plVar6 + 0x1a8)(plVar6,lVar8,1,1,uVar13,0)` in the immediate route. Its deferred route calls `FUN_140657c30(...,lVar8,plVar6,uVar13)` [EV-0615], [EV-0616], raw `.local/ghidra/gog-query-20261019T191026Z.stdout.raw`.
- `FUN_140657c30` writes tag `0x12` at payload `+0`, its second parameter at `+8`, third at `+0x10`, and fourth dword at `+0x18` [EV-0618], raw `.local/ghidra/gog-query-20261019T191458Z.stdout.raw`.
- Dispatcher case `0x12` reads those payload fields and invokes the same vtable slot. The exact call is RVA `0x659c92`, not `0x65939c`. At `0x659c92`, instructions set `[RSP+0x28]=0`, load EAX from `[RDI+0x18]`, store it at `[RSP+0x20]`, set `R9B=1`, derive `R8D=1`, and set `RDX=R15`, `RCX=R14` [EV-0631], raw `.local/ghidra/gog-query-20261019T194800Z.stdout.raw`.
- The later address-only query confirms that the previously attributed `0x65939c` is a different virtual-call site in dispatcher case `0x4`; its byte-valued `R8` setup belongs to that case [EV-0631], raw `.local/ghidra/gog-query-20261019T195220Z.stdout.raw`. EV-0619's instruction reading was real, but its case attribution was wrong.
- The decompiler's case-0x12 sixth-argument expression masks off the low byte; the direct instruction query independently shows the sixth stack-argument byte is explicitly zero. The deferred call therefore does not use a nonzero inherited `param6` to skip `FUN_140e884d0`'s bit-1 eligibility check [EV-0630], [EV-0631].

## Result and limits

H1 is supported for the captured GOG call path; H2 is falsified for this callsite. The immediate producer and deferred case construct `(receiver, object, 1, 1, selector, 0)` in the same six argument positions. `FUN_14065b800` still forwards only the event pointer to the dispatcher, which reads the event fields and constructs the downstream call arguments. Thus the worker wrapper's limited call signature alone did not establish a mismatch.

This establishes static argument parity, not identical dynamic receiver state, callback execution, gameplay outcome, effective protection, armor-skill XP, Steam equivalence, or a vanilla exploit. No direct HitData/AV11/AV12/UseSkill edge is added. Caller 50 is bounded as a caller review; continue with caller 51/62.
