# Remediation Maturation Engine v1

Status: operational governance layer
Revision: 1.1 lifecycle and fresh-state hardening

## Purpose

This engine sits between Operations/Automation Health and code delivery. It prevents a single transient failure from becoming an immediate code change, prevents stale or intentionally blocked work from becoming speculative remediation, and requires post-fix evidence before resolution.

## Flow

```text
Operations Dashboard and Automation Health
-> stable actionable failure signature
-> evidence and persistence evaluation
-> OBSERVE / SELF-HEAL ALLOWLIST / CODEX PR / FRAMEWORK OWNER PROPOSAL
-> fresh-state remediation preflight
-> IN_REMEDIATION or CLEARED_NO_CHANGE
-> post-fix observation
-> RESOLVED or REOPENED
```

## States

`OBSERVED`, `SUSPECTED_TRANSIENT`, `PERSISTING`, `CONFIRMED`, `NEEDS_MORE_EVIDENCE`, `CODEX_READY`, `IN_REMEDIATION`, `POST_FIX_OBSERVATION`, `RESOLVED`, `REOPENED`, `CLEARED_NO_CHANGE`.

Lifecycle-only health findings such as `EXPECTED_BLOCK`, `PENDING_FIRST_EXPECTED_RUN` and retired-local visibility are not remediation work by themselves. Invalid lifecycle configuration remains actionable through its specific health finding.

## Timing principle

The engine measures expected runs rather than fixed calendar days.

- Security, data-loss, hash, false-PASS and canonical-corruption findings escalate immediately.
- High-frequency daily workflows normally require three observations or an equivalent failure streak.
- Ordinary scheduled workflows require two observations.
- Transient source, timeout, rate-limit and schedule-delay failures remain under observation until their evidence threshold is met.
- Weekly workflows may be reproduced manually rather than waiting a full additional week.

## Routes

### Allowlisted self-heal

Only reversible actions may be automated: rerun a failed job, regenerate a dashboard, rebuild a pointer from existing hash-verified output, or publish a missing failure receipt.

### Codex PR

`CODEX_READY` produces a bounded task package containing:

- workflow, finding, signature and latest run identity;
- concrete objective;
- fresh-state precondition;
- success evidence;
- clean-no-op condition;
- stop and escalation conditions;
- allowed paths and forbidden authority changes;
- required positive and negative tests;
- post-fix gate;
- source-health generation, task-contract hash and required transition-receipt path.

It does not invoke or merge Codex automatically.

Before changing code, the worker must revalidate the task and create the branch-bound transition receipt with:

```text
python scripts/remediation/write_transition_receipt.py --signature <signature> --branch <non-default-task-branch>
```

The helper reads current `LATEST_CODEX_READY_TASKS.json` and fresh Automation Production Health. It refuses a missing/non-unique task, refuses a task built from an older health generation, verifies the task-contract hash, refuses a task whose finding is no longer present, and refuses `main`, `master` or `backup/*` as remediation branches.

A valid receipt is stored under:

```text
research/remediation/transitions/<signature>.json
```

and binds the current task contract, source-health timestamp, latest run, branch, authority limits and acceptance conditions to `IN_REMEDIATION`. The receipt carries its own SHA-256 and is revalidated by the maturation engine. A receipt with a bad contract, state, signature/path relationship, unsafe branch, workflow/finding mismatch, missing task-contract hash or SHA mismatch is ignored and surfaced through `transition_receipt_errors`.

### Framework-owner proposal

Model weights, market gates, canonical predecessor rules, authority boundaries, portfolio logic and API budget remain proposal-only.

## Clean no-op semantics

If a prior `CODEX_READY` or `REOPENED` signature disappears before a newly valid remediation receipt binds it, the task becomes `CLEARED_NO_CHANGE` with terminal reason `FINDING_ABSENT_BEFORE_REMEDIATION_BINDING`.

This is not proof that a code fix occurred. It means the current evidence no longer justifies changing code. The task may re-enter normal maturation if the finding appears again later.

## Reopen semantics

A returning signature during or after post-fix observation becomes `REOPENED`. The prior transition receipt is historical evidence only and cannot silently reactivate remediation. A new hash-distinct transition receipt, created from current health and the current task contract, is required to return the finding to `IN_REMEDIATION`.

## Post-fix acceptance

A merge does not resolve an incident.

A bound remediation whose finding disappears enters `POST_FIX_OBSERVATION`. Scheduled workflows require three successful expected observations by default. Non-scheduled changes retain their declared `CI_PLUS_ONE_PRODUCTION_SHAPE_RUN` acceptance requirement for the code task; the remediation observer remains conservative and records successive healthy observations before terminal resolution.

`RESOLVED` requires the post-fix evidence gate and records terminal reason `POST_FIX_GATE_SATISFIED`.

## Outputs

- `LATEST_REMEDIATION_QUEUE.json`
- `LATEST_CODEX_READY_TASKS.json`
- `LATEST_NEEDS_MORE_EVIDENCE.json`
- `research/remediation/REMEDIATION_HISTORY.jsonl`
- branch-bound transition receipts under `research/remediation/transitions/`

## Authority

The engine is operational routing only. It cannot create market truth, change framework state, modify model weights, issue portfolio action, write code automatically or merge pull requests.
