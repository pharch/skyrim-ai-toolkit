# Evidence model

`research/EVIDENCE.json` is the machine-readable register for claims and
frontier evidence. An empty register means no results have yet been imported;
do not manufacture seed observations. Every evidence item must be immutable by
identity and independently inspectable.

Required evidence fields:

- `id`: stable ID (for example `EV-0001`); never recycle an ID.
- `kind`: `record`, `native`, `runtime`, `save`, `log`, `wiki`, `discord`,
  `tool`, or `legacy`.
- `source`: source name plus edition/build/record/revision/message identifier
  as applicable.
- `artifact`: repository-relative path to preserved raw output, or a clearly
  scoped `private-local:` reference for data that must not be committed.
- `sha256`: lowercase SHA-256 of the raw artifact; for a private artifact,
  compute and retain the hash locally without exposing its contents.
- `captured_utc`: ISO-8601 UTC timestamp.
- `edition`, `runtime`, `modified_state`, `lane`: use `AE`, verified version or
  explicit `unknown`, a boolean, and one of `offline`,
  `diagnostic_intervention`, `vanilla_candidate`, `vanilla_reproduction`, or
  `mechanism_inference`.
- `tools`: exact tool names and versions, including instrumentation.
- `coverage`: denominator, selection rule, omissions, and liveness/identity
  checks. Empty/partial output must state why it is incomplete.
- `result`: concise observation only; interpretations belong in a claim or
  experiment record.

Frontier items cite evidence IDs in `evidence`. Claims use the same IDs and
must distinguish direct observations from inference. Contradictions retain
both sides and point to competing evidence IDs. Preserve negative results and
raw outputs; never rewrite evidence to fit a hypothesis. Do not store saves,
co-saves, private exports, or game binaries in Git.
