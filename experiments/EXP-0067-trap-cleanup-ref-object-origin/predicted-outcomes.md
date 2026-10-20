# Predicted outcomes

- **Supports Q64-H1:** resolve the stored object's finalizer and descendants; they do not reach Actor::UseSkill or the mapped skill-progress sink with AV11/AV12, with no relevant indirect target left open.
- **Supports Q64-H2:** a resolved finalizer descendant reaches the mapped skill-progress sink with AV11 or AV12.
- **Inconclusive:** the resource object's vtable or final slot +0x8 target remains dynamic, or an indirect descendant remains unresolved.
