# Expected discriminants

1. Resolve each wrapper vtable slot to an exact function.
2. Follow pointer setter, observer, reference operations and finalizer without conflating wrapper data with the hkp instance.
3. Distinguish direct +0x48 writes from vector copies beginning at +0x40.
4. Confirm whether exact hkp constructors initialize or populate callback entries.
5. Preserve unknown global writers and later finalizer paths.
