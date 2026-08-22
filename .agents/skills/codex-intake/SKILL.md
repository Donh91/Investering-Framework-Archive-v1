# Codex Intake Skill v1

Status: ACTIVE OPERATIONAL ROUTING
Scope: research-to-code remediation handoff only

## Trigger

Use this skill when a research thread, Deep Research review, audit, Claude/Grok review or user says any equivalent of:

- `sæt dette i Codex-køen`
- queue this for Codex
- this needs a bounded code fix
- hand this research finding to Codex

Do not use this skill for market calls, threshold changes, model weights, canonical authority, portfolio logic, API budget changes or new policy semantics.

## Mandatory read order

1. `LATEST_OPERATIONS_DASHBOARD.json`
2. `LATEST_HANDOFF.json`
3. `research/architecture_health/LATEST_AUTOMATION_HEALTH.json`
4. `research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json`
5. `LATEST_REMEDIATION_QUEUE.json`
6. `LATEST_CODEX_READY_TASKS.json`
7. `LATEST_CODEX_EXECUTION_STATE.json`
8. `00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md`
9. `07_PROMPTS_AND_AGENTS/codex/2026-08-22__codex-research-intake-and-execution-ledger-v1__operational.md`
10. exact source evidence, target code, workflow runs and tests

Conversation memory is not queue authority.

## Fast intake path

A research thread may submit evidence, but it may not self-declare `CODEX_READY`.

1. Prove the problem is code-remediable and bounded.
2. Search `LATEST_CODEX_READY_TASKS.json` for a duplicate.
3. If an active health signature already covers the same defect, set `linked_health_signature` to it and do not create parallel authority.
4. Create one candidate conforming to `research/codex/CODEX_RESEARCH_CANDIDATE.schema.json` at:
   `research/codex/intake/YYYY/MM/<candidate_id>.json`
5. Use an isolated `agent/task-*` branch and PR under archive governance.
6. Once the candidate lands on `main`, the non-writing `codex-intake-dispatch.yml` path listener immediately dispatches the guarded Remediation Maturation Controller. The main writer itself remains free of push triggers.
7. Only `LATEST_CODEX_READY_TASKS.json` may declare the candidate `CODEX_READY`.
8. For a standalone research task, Codex must run the task's `fresh_state_preflight_command` on its remediation branch before changing code.
9. Codex may only touch `allowed_change_scope`, must preserve `forbidden_changes`, must run positive and negative tests, and may never self-merge.
10. After merge and required verification, publish a completion receipt so the execution ledger can show `RESOLVED`.

## Candidate evidence minimum

A candidate must include:

- exact objective;
- exact allowed change paths;
- at least one durable evidence reference;
- deterministic or bounded reproduction instructions;
- positive acceptance test;
- negative acceptance test;
- `authority_boundary: CODE_REMEDIATION_ONLY`;
- `requires_framework_owner_authority: false`;
- all forbidden authority classes listed by the schema.

If evidence is incomplete, route to `NEEDS_MORE_EVIDENCE`. If authority is too broad, reject the Codex route and escalate to framework owner.

## Priority

`EXPEDITED` means queue ordering priority only. It does not bypass evidence, fresh-state binding, CI, review, PR or post-fix gates.

## Observability

Read:

- live queue: `LATEST_CODEX_READY_TASKS.json`
- latest lifecycle state: `LATEST_CODEX_EXECUTION_STATE.json`
- append-only event history: `research/codex/CODEX_EXECUTION_LEDGER.jsonl`
- intake status/errors: `research/codex/LATEST_CODEX_INTAKE_STATUS.json`
- health remediation history: `research/remediation/REMEDIATION_HISTORY.jsonl`
- transition receipts: `research/remediation/transitions/` for health tasks, `research/codex/transitions/` for research-intake tasks
- completion receipts: `research/codex/completions/`

The execution ledger is observability, not a second queue authority.

## No-write fallback

If the current thread cannot write GitHub, do not claim the task was queued. Produce a schema-complete candidate payload and state `CODEX_INTAKE_WRITE_UNAVAILABLE`. A later authorized writer may persist it.

## Kill / stop conditions

Stop intake and escalate if:

- the issue requires market-rule, threshold, weight, canonical-authority, portfolio, API-budget or policy changes;
- the candidate duplicates an existing current task and cannot be safely linked;
- evidence cannot reproduce the defect;
- requested paths are broader than needed;
- the candidate changed after task binding;
- the task is already fixed or superseded.
