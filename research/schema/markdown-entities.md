# Markdown research entity schemas

`scripts/validate_research.py` validates these compact durable record formats
using only Python's standard library. It checks required fields, unique IDs,
and every `EV-...` citation against `research/EVIDENCE.json`.

## Claims (`research/CLAIMS.md`)

Each claim is a five-cell row with a unique claim ID, concise statement, status,
one or more evidence IDs, and scope/open limit:

`ID | Claim | Status | Evidence IDs | Scope and open limit`

## Mechanisms and glitches

Each record starts with a unique `## M-...` or `## G-...` heading, followed by
a non-empty summary and one or more known evidence IDs. Historical findings
must keep their source-build and reproduction limits in the summary.

## Contradictions

Each unique `## C-LEG-...` section must state Model A, Model B, Source, and a
Discriminant. Source citations must resolve to the evidence register; no model
is promoted to fact by the format itself.

## Experiments

Every `experiments/EXP-*` directory contains `README.md`, `hypothesis.md`,
`protocol.md`, `expected-discriminants.md`, and `results.md`. The hypothesis
record names rival H1/H2 models. The bundle includes at least one registered
evidence ID, and all such citations resolve.
