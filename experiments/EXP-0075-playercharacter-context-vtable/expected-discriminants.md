# Expected discriminants

1. Identify the source/type of the TLS-selected object or nested `param_1+0x68` object's `+0x68` member.
2. Match the actual returned object's vtable at the `FUN_1408e6500` slot +0x150 callsite.
3. Identify the returned member's exact slot +0x8 finalizer.
4. Screen the resolved descendant path against Actor::UseSkill AV11/AV12.
