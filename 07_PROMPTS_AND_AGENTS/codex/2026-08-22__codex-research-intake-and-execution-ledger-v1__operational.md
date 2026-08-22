# Codex Research Intake and Execution Ledger v1

Status: ACTIVE OPERATIONAL CONTRACT
Date: 2026-08-22
Authority: orchestration and code-remediation routing only

## Purpose

Make Codex work visible, source-agnostic and fast to queue from research without creating a parallel source of truth.

The same Codex queue may receive bounded code-remediation tasks from automation health or from durable research intake. Research cannot directly promote a task to `CODEX_READY`; the controller owns that transition.

## Machine authorities

- Queue authority: `LATEST_CODEX_READY_TASKS.json`
- Remediation authority: `LATEST_REMEDIATION_QUEUE.json`
- Execution observability: `LATEST_CODEX_EXECUTION_STATE.json`
- Append-only Codex lifecycle history: `research/codex/CODEX_EXECUTION_LEDGER.jsonl`
- Research intake status: `research/codex/LATEST_CODEX_INTAKE_STATUS.json`

`LATEST_CODEX_EXECUTION_STATE.json` is not allowed to override the queue or remediation state.

## Research-thread fast path

When a research thread concludes that a bounded code defect is reproducible and the user asks to queue it for Codex:

1. Read the current queue and execution state.
2. Deduplicate against an existing health/remediation signature.
3. Prepare one `CODEX_RESEARCH_CANDIDATE_v1` JSON document.
4. Persist it through isolated branch and PR at `research/codex/intake/YYYY/MM/<candidate_id>.json`.
5. Merge to `main` only after normal repository validation.
6. The path-restricted, non-writing `codex-intake-dispatch.yml` workflow receives the durable event and immediately dispatches `remediation-maturation.yml` on `main`. The guarded main writer itself remains free of push triggers.
7. The controller validates evidence and authority boundaries and routes the candidate as `CODEX_READY`, `NEEDS_MORE_EVIDENCE`, `DEDUPED_TO_HEALTH_TASK` or `REJECTED`.
8. Codex must perform the task-specific fresh-state binding before changing code.
9. Code changes use normal task branch, PR, CI and review discipline. No self-merge.
10. Post-merge verification is recorded with a completion receipt and reflected in the execution ledger.

The normal 05:45 and 17:45 Europe/Copenhagen maturation runs remain recovery/reconciliation passes, not the only intake opportunities.

## Candidate contract

Schema: `research/codex/CODEX_RESEARCH_CANDIDATE.schema.json`

Required intent fields include objective, bounded change scope, evidence, reproduction, positive and negative acceptance tests, code-only authority and explicit forbidden authority changes.

`requested_priority: EXPEDITED` only changes queue ordering. It never weakens evidence or safety gates.

## Deduplication

If research discovers the same defect already represented by an active health signature, it must set `linked_health_signature`. The research evidence is attached to the existing task and no second Codex authority is created.

If the linked signature is no longer current, the controller treats the research candidate independently only when its own evidence contract is complete.

## Authority boundary

Codex may repair implementation defects within the bounded task contract. Codex may not independently alter:

- market gates or thresholds;
- model weights;
- canonical authority or predecessor rules;
- portfolio logic or sizing;
- API budget;
- new policy semantics.

Those require framework-owner review and a separate governed proposal.

## Execution lifecycle

Observable states include:

`CODEX_READY -> IN_REMEDIATION -> POST_FIX_OBSERVATION -> RESOLVED`

and terminal/exception paths including:

`NEEDS_MORE_EVIDENCE`, `CLEARED_NO_CHANGE`, `REOPENED`, `REJECTED`, `DEDUPED_TO_HEALTH_TASK`.

Health-origin tasks retain their existing transition receipts in `research/remediation/transitions/`.
Research-origin standalone tasks use `research/codex/transitions/` and completion receipts in `research/codex/completions/`.

## History semantics

`research/codex/CODEX_EXECUTION_LEDGER.jsonl` is append-only and records state or contract changes from activation of this v1 contract forward. At activation it imports the currently visible remediation state as a baseline. Earlier Codex activity remains reconstructable from remediation history, transition receipts, issues, PRs and commits and is not falsely backfilled as if this ledger observed it live.

Each event includes signature, source type, workflow/finding or candidate ID, objective, task-contract hash, previous state, transition path and post-fix gate.

## Research thread instruction

Any repository-aware research thread should interpret `Sæt dette i Codex-køen` as a request to load `.agents/skills/codex-intake/SKILL.md` and follow this contract. If it lacks GitHub write capability, it must return a schema-complete candidate payload and explicitly say it was not persisted.

## Non-goals

This contract does not create an autonomous self-merging Codex bot, does not bypass repository review, does not give research threads code authority and does not change market or portfolio semantics.
