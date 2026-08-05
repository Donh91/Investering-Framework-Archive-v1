# Remediation Maturation Engine v1

Status: operational governance layer

## Purpose

This engine sits between Operations/Automation Health and code delivery. It prevents a single transient failure from becoming an immediate code change, while allowing critical reproducible faults to escalate without artificial delay.

## Flow

```text
Operations Dashboard and Automation Health
-> stable failure signature
-> evidence and persistence evaluation
-> OBSERVE / SELF-HEAL ALLOWLIST / CODEX PR / FRAMEWORK OWNER PROPOSAL
-> post-fix observation
-> RESOLVED or REOPENED
```

## States

`OBSERVED`, `SUSPECTED_TRANSIENT`, `PERSISTING`, `CONFIRMED`, `NEEDS_MORE_EVIDENCE`, `CODEX_READY`, `IN_REMEDIATION`, `POST_FIX_OBSERVATION`, `RESOLVED`, `REOPENED`.

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

`CODEX_READY` produces a bounded task package containing workflow, finding, run identity, evidence threshold, allowed paths, forbidden changes, acceptance evidence and post-fix gate. It does not invoke or merge Codex automatically.

### Framework-owner proposal

Model weights, market gates, canonical predecessor rules, authority boundaries, portfolio logic and API budget remain proposal-only.

## Post-fix acceptance

A merge does not resolve an incident. Scheduled workflows require three successful expected runs by default. Non-scheduled changes require CI plus one production-shape run. A returning signature becomes `REOPENED`.

## Outputs

- `LATEST_REMEDIATION_QUEUE.json`
- `LATEST_CODEX_READY_TASKS.json`
- `LATEST_NEEDS_MORE_EVIDENCE.json`
- `research/remediation/REMEDIATION_HISTORY.jsonl`

## Authority

The engine is operational routing only. It cannot create market truth, change framework state, modify model weights, issue portfolio action, write code automatically or merge pull requests.
