# Codex Intake and Execution Ledger v1 - Implementation Receipt

Date: 2026-08-22
Status: MERGED_AND_CI_VERIFIED
Scope: orchestration, research-to-code intake, Codex queue observability and execution history

## Merge identity

- Pull request: `#493` - `Add event-driven research-to-Codex intake and execution ledger`
- PR head SHA: `97f19d811b713807e2011e6432d9c5b21888ce5e`
- merge commit SHA: `5cf5d2706800fe3f7a9566de6e2c8554a633d215`
- merged at UTC: `2026-08-22T13:31:01Z`
- base before merge: `1d54c9f1afb1e253d35297ce507cdfbccc5927d4`

## High-impact safepoint

Workflow changes were protected by:

- frozen source SHA: `bb2dba6f6f5abd5185485bbd168ecfd0c7b207af`
- safepoint branch: `backup-safepoint/2026-08-22-codex-intake-ledger`
- safepoint SHA: `bb2dba6f6f5abd5185485bbd168ecfd0c7b207af`
- receipt: `research/repository_safety/2026-08-22__codex-intake-ledger-safepoint-receipt.json`
- verification: `PASS_INTERNAL_SAFEPOINT_VERIFIED`

Main advanced by two unrelated market-learning commits while the task branch was open. A compare showed no path overlap with the Codex-intake change before merge.

## Activated authorities and discovery surfaces

Queue authority remains:

`LATEST_CODEX_READY_TASKS.json`

New observability and intake surfaces:

- `LATEST_CODEX_EXECUTION_STATE.json`
- `research/codex/LATEST_CODEX_EXECUTION_STATE.json`
- `research/codex/CODEX_EXECUTION_LEDGER.jsonl`
- `research/codex/LATEST_CODEX_INTAKE_STATUS.json`
- `research/codex/CODEX_RESEARCH_CANDIDATE.schema.json`
- `research/codex/README.md`
- `.agents/skills/codex-intake/SKILL.md`
- `07_PROMPTS_AND_AGENTS/codex/2026-08-22__codex-research-intake-and-execution-ledger-v1__operational.md`

`LATEST_CODEX_EXECUTION_STATE.json` and the ledger are observability only. They cannot promote a task or override the queue.

## Research-thread behavior

Repository-aware research threads now interpret requests equivalent to `sæt dette i Codex-køen` through `.agents/skills/codex-intake/SKILL.md`.

The governed fast path is:

```text
research finding
-> current queue deduplication
-> CODEX_RESEARCH_CANDIDATE_v1
-> isolated branch and PR
-> research/codex/intake/YYYY/MM/<candidate_id>.json on main
-> non-writing Codex Research Intake Dispatcher
-> workflow_dispatch of guarded Remediation Maturation Controller
-> CODEX_READY / NEEDS_MORE_EVIDENCE / DEDUPED_TO_HEALTH_TASK / REJECTED
-> fresh-state binding
-> bounded Codex PR
-> CI and review
-> merge
-> verification/completion receipt
-> execution ledger
```

The normal `05:45 / 17:45 Europe/Copenhagen` remediation schedule remains a reconciliation and recovery cadence, not a mandatory wait for durable research intake.

`requested_priority: EXPEDITED` affects ordering only and cannot bypass evidence, authority, fresh-state binding, CI, review or post-fix gates.

## Writer safety architecture

Event responsiveness was implemented without adding a push trigger to the main-writing remediation workflow.

- `.github/workflows/codex-intake-dispatch.yml` listens only to durable `main` changes under research intake, research transition and research completion paths.
- dispatcher permissions are `actions: write` and `contents: read`.
- dispatcher does not write repository content and does not run `git push`.
- dispatcher invokes `remediation-maturation.yml` through `workflow_dispatch`.
- `.github/workflows/remediation-maturation.yml` remains serialized through `framework-main-writer` and has no push trigger.

This preserves the pre-existing writer-trigger safety contract.

## CI verification

All pull-request gates associated with final head SHA `97f19d811b713807e2011e6432d9c5b21888ce5e` completed successfully:

- Data Architecture Gate, run `32575952219`: SUCCESS
- Full Architecture 1-7 Gate, run `32575952229`: SUCCESS
- Storage Health Gate, run `32575952230`: SUCCESS
- Remediation Maturation Gate, run `32575952221`: SUCCESS
- Automation Production Health Gate, run `32575952227`: SUCCESS

Automation Production Health Gate job `97038224632` additionally verified:

- Python compile of the new remediation scripts: SUCCESS
- main-writer trigger-safety validation: SUCCESS
- existing health tests plus `tests/health/test_codex_research_intake.py`: SUCCESS
- static automation repository inventory: SUCCESS

The intake tests cover:

- research candidate enters the same Codex queue while native health tasks are preserved;
- framework-owner authority candidates are rejected;
- research evidence deduplicates to an active health signature;
- native `NEEDS_MORE_EVIDENCE` schema is preserved;
- changed candidate hashes fail fresh-state binding;
- event dispatch remains non-writing and the main writer remains single-writer guarded.

## Authority boundary

No change in this delivery gives Codex or research threads authority over:

- market gates or thresholds;
- model weights;
- canonical authority or predecessor rules;
- portfolio logic or sizing;
- API budget;
- new policy semantics.

No self-merge path was added.

## History semantics

`research/codex/CODEX_EXECUTION_LEDGER.jsonl` begins with v1 activation and records observable state/contract changes going forward. The first remediation reconciliation after activation imports current remediation items as the baseline. Earlier Codex history remains reconstructable from `research/remediation/REMEDIATION_HISTORY.jsonl`, transition receipts, issues, PRs and commits and is deliberately not fabricated into the new ledger as if it had been observed live.

## Repository hygiene note

During pre-write branch verification, several empty `agent/task-20260822-codex-intake-ledger-*` branch refs were unintentionally created at the same frozen source SHA. They contain no task commits and never touched `main`. The connector available in the implementation session exposed no branch-delete action, so these refs remain non-authoritative hygiene residue only. They are not used by any workflow, queue, receipt or authority path.

## Final classification

```yaml
implementation: PASS
pull_request: 493
merge_commit: 5cf5d2706800fe3f7a9566de6e2c8554a633d215
ci_gates: 5_OF_5_SUCCESS
writer_safety: PASS
queue_authority_preserved: YES
research_fast_intake: ACTIVE
research_self_promotion: FORBIDDEN
codex_self_merge: FORBIDDEN
market_framework_authority_changed: NO
execution_ledger_history_scope: FORWARD_FROM_V1_ACTIVATION_PLUS_CURRENT_BASELINE
production_reconciliation: NEXT_EVENT_OR_SCHEDULED_MATURATION
```
