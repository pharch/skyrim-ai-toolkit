# Research transaction template

Create `experiments/EXP-####-slug/` for a material investigation. Keep raw
outputs immutable under `raw/`; never put a real save, private export, or game
binary in Git.

## Identity and state

- Frontier ID:
- Transaction ID:
- Status: `open | in_progress | awaiting_user_test | blocked_tool | blocked_environment | completed | falsified | superseded`
- Objective and falsifiable question:
- Exact next action:
- Started/updated UTC:

## Competing models and predictions

| Hypothesis ID | Causal model (unverified until evidenced) | Predicted observation | Discriminant |
|---|---|---|---|
| H1 | | | |
| H2 | | | |

## Target, environment, and permission

- Edition/runtime ProductVersion and executable SHA-256, or `unknown`:
- Active profile/load-order path and SHA-256, or `unknown`:
- Tool names/versions and instrumentation:
- Lane: `offline | diagnostic_intervention | vanilla_candidate | vanilla_reproduction | mechanism_inference`
- OS, dependencies, permission/consent, and target identity:
- Save/profile: disposable copy identity only, or `not applicable`:

## Procedure and controls

- Exact reproducible steps/commands:
- Positive control:
- Negative control:
- Baseline and measured variables:
- Expected outcomes under each hypothesis:
- Stop/rollback conditions:

## Evidence and interpretation

- Raw artifact paths and SHA-256:
- Coverage denominator, omissions, and liveness/identity checks:
- Direct observations (no interpretation):
- Inference and confidence:
- Decision/status rationale:
- Linked evidence IDs, claims, mechanisms, contradictions, and frontier items:
- Cross-domain implications (or why none are currently supported):

## Closure and continuation

- Successor frontier IDs and predicted discriminants:
- User-dependent follow-up protocol, if any:
- Exact next action:
- Interruption recovery note: what was incomplete and how to resume without
  treating partial output as a result.

Do not mark a terminal status without preserved evidence, a decision record,
cross-domain assessment, and at least one successor question. Preserve
falsified hypotheses and negative outcomes rather than deleting them.
