---
name: codex-intake
description: Route reproducible research or audit defects into the governed Codex intake. Use when asked to queue a bounded code fix or audit candidates before submission; preserve existing owners and never self-declare CODEX_READY.
---

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

## Cross-repository evidence rule

Read `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md` and `CROSS_REPO_AGENT_CONTEXT_MAP.json`. If reproduction requires restricted evidence, use an authorized immutable binding in `Donh91/secrets`. Never paste restricted values into a public candidate, issue, PR, fixture, test log or completion receipt. A public candidate carries commit/path/bytes/SHA-256/source-contract/time/schema/completeness metadata only. Credentials remain outside repository files. Return `PRIVATE_DATA_AUTHORITY_UNAVAILABLE` when the needed private authority cannot be read.

## Mandatory read order

1. `LATEST_OPERATIONS_DASHBOARD.json`
2. `LATEST_HANDOFF.json`
3. `research/architecture_health/LATEST_AUTOMATION_HEALTH.json`
4. `research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json`
5. `LATEST_REMEDIATION_QUEUE.json`
6. `LATEST_CODEX_READY_TASKS.json`
7. `LATEST_CODEX_EXECUTION_STATE.json`
8. `00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md`
9. `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`
10. `00_ARCHIVE_CONTROL/CROSS_REPO_AGENT_CONTEXT_MAP.json`
11. `07_PROMPTS_AND_AGENTS/codex/2026-08-22__codex-research-intake-and-execution-ledger-v1__operational.md`
12. exact source evidence, target code, workflow runs and tests

Conversation memory is not queue authority.

## Fast intake path

A research thread may submit evidence, but it may not self-declare `CODEX_READY`.

1. Prove the problem is code-remediable and bounded.
2. Search `LATEST_CODEX_READY_TASKS.json`, execution state, exact transition/completion receipts and current open PRs for an existing owner. Match signatures, objectives and changed paths, not titles alone. A missing PR pointer in generated state is not proof that no PR exists.
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

### Owner-aware, economical triage

- Reuse the existing owner/branch for the same defect. Return a read-only deduplication result when the new evidence adds no governed value. When durable new evidence does warrant persistence, submit it only through one schema-bound candidate on an isolated branch and link that candidate to the existing signature/owner; do not write directly to its PR branch, handoff or other ad hoc surface. Preserve the no-self-merge rule after material repair.
- Group investigation only when exact logs and reproduction establish a shared failing component. One bounded repair can serve multiple findings, but each signature retains its own receipt and post-fix gate. Similar workflow names alone do not justify merging independent defects or scopes.
- A correctly enforced budget, authority or evidence guard is not a code defect. Record the observed blocker without raising limits, weakening guards or changing failure semantics merely to make CI green. A distinct observability defect needs its own reproduction.
- Check the actual test runner, collected test count and exit status. Zero collected tests, skipped execution or unrelated green checks do not verify a fix.
- Compare suspected stale findings against fresh runs and owner contracts. Already-fixed or superseded findings need reconciliation evidence, not artificial code changes or manual deletion from generated queue files. A partial merge does not resolve a whole owner.
- Use deterministic inspection first. If a named causal or architectural question remains unresolved, prepare an advisory request with exact evidence and a bounded expected decision. Leave execution pending unless an existing authorized owner or the user explicitly authorizes the model route and its verified budget gate. Reuse evidence within its immutable binding; refresh changed heads, task contracts, runs and receipts before action. Do not repeat an unchanged audit or add another agent/controller merely to increase activity.

These are intake decisions, not new lifecycle states, model-budget authority or permission to execute a fix inside this skill. Use existing schema fields and the current handoff for evidence; do not create a parallel queue.

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

Do not invent new candidate schema fields merely to express a diagnosis. Use the existing objective, evidence, reproduction and acceptance-test surfaces to state what is known and what remains hypothesis.

If evidence is incomplete, route to `NEEDS_MORE_EVIDENCE`. If authority is too broad, reject the Codex route and escalate to framework owner.

## Root-cause discipline before readiness

A reproducible symptom is necessary but not always sufficient for a safe remediation candidate.

Before recommending readiness:

1. identify the smallest reproducible failure surface;
2. distinguish observed symptom from suspected root cause;
3. inspect recent relevant changes and a known-working comparison when available;
4. trace the failing data or control path far enough to identify the component boundary where behavior diverges;
5. record one primary causal hypothesis when the evidence supports one;
6. if root cause is not established, label it as unresolved and keep the proposed change bounded enough to test the hypothesis rather than presenting it as a proven fix.

Do not stack multiple speculative fixes into one candidate merely because they are nearby. When independent defects exist, split or link them instead of creating attribution ambiguity.

If repeated fix attempts expose different failures or shared-state coupling, stop treating the task as a simple bounded patch and escalate for architectural review rather than queueing another speculative fix.

## Completion verification discipline

A completion receipt is evidence of closure only when it contains fresh proof from the final merged state.

Required closure evidence, using existing receipt/test surfaces rather than inventing parallel authority:

- the original reproducible symptom or regression case no longer fails;
- positive acceptance tests pass;
- negative acceptance tests pass;
- the relevant bounded regression suite passes when available;
- the merged code and exact verified commit are the code that was tested;
- no forbidden change scope was touched;
- any unresolved assumptions remain explicit.

An agent report, changed diff, green unrelated test or earlier pre-merge run is not sufficient by itself to claim `RESOLVED`.

If fresh verification cannot be obtained, keep the lifecycle state non-final and record the missing evidence. Do not convert confidence into a completion claim.

## Priority

`EXPEDITED` means queue ordering priority only. It does not bypass evidence, fresh-state binding, root-cause discipline, CI, review, PR or post-fix gates.

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
- the task is already fixed or superseded;
- the proposed fix is presented as proven while the causal diagnosis remains unsupported;
- repeated failed fixes indicate the problem is architectural rather than a bounded code defect;
- fresh post-merge verification needed for closure is unavailable.
