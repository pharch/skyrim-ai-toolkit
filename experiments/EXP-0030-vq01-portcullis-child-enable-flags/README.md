# EXP-0030 — VQ01 portcullis child enable flags

**Status:** Bounded static record/schema screen complete; loaded state and physical access remain unobserved.

**Objective:** Resolve whether the Dawnguard portcullis child's XESP and REFR header encode inverted parent semantics or an Initially Disabled state.

**Competing models:** H1 predicts ordinary parent-state inheritance with no child/parent Initially Disabled flag. H2 predicts an inverted XESP flag or explicit Initially Disabled state. The raw fields support H1 and falsify H2 for the inspected base records (EV-0282).

The captures are private under .local/alignment/transactions/TX-20261016-0018/; the installed Dawnguard.esm SHA-256 and exact record capture hashes are recorded in EV-0282. See [hypothesis](hypothesis.md), [protocol](protocol.md), [predicted outcomes](predicted-outcomes.md), [expected discriminants](expected-discriminants.md), [results](results.md), and [implications](implications.md).
