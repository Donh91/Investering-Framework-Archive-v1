# Operational Remediation Backlog v1

Source main: `ef92abe9e5fe80a2c66dfdb2cce1ec3e600dadc3`

Authority: **OPERATIONAL_ROUTING_ONLY**

This is the durable handoff for unresolved items from the complete 2026-08-24 health audit after the immediate PR #557 quick fixes. Current `main` remains authoritative. Every agent must revalidate its precondition before acting and exit as a clean no-op when the defect is already superseded or no longer reproduces.

## Execution lanes

- **Codex intake**: bounded code remediation only. Positive and negative tests, explicit allowed scope, rollback and post-fix production evidence are mandatory. No automatic merge.
- **OpenAI API analysis then Codex**: analysis-first. These packets are deliberately marked `QUEUED_NOT_AUTOWIRED` because the current market/cycle Deep Research queue is not an operational software-remediation runner. A future authorized operational API lane may consume them. Code work starts only after a reproducible bounded defect is found.
- **Observe only**: no code change. Verify merged repairs on expected production runs.
- **External dependency**: no code workaround. Access/governance evidence must unblock the task.

## P0 Codex candidates

### OPR-001 - Operations dashboard pointer truth

**Problem:** `build_latest_handoff.py` can discover the newest Daily Director and weekly artifacts, while the Operations Dashboard workflow currently builds directly from the existing `LATEST_HANDOFF.json`. If that handoff is old, the dashboard can report a producer as `STALE/RED` even though newer valid evidence exists.

**Required repair:** bind fresh handoff/discovery into dashboard generation or otherwise resolve fresh trusted producer evidence before final classification. Preserve pointer hashes, malformed-artifact rejection and the distinction between `FRESH + DEGRADED` and `STALE`.

Task: `research/codex/intake/2026/08/codex-operational-observability-pointer-truth-v1.json`

Post-fix gate: `2_CONSECUTIVE_OPERATIONS_DASHBOARD_RUNS_WITH_FRESH_POINTER_TRUTH_AND_NO_FALSE_STALE`

### OPR-002 - Historical CFGI terminal lifecycle

**Problem:** the old MARKET gapfill path can still fail with `CFGI_MARKET_GAPFILL_PROVIDER_RETURN_INVALID` when the provider returns zero MARKET rows. A newer terminal workflow already ratifies `TERMINAL_PROVIDER_NO_HISTORICAL_ROWS`, `NOT_TESTABLE_PROVIDER_UNAVAILABLE` and `no_additional_paid_retry_authorized=true` without paid calls. Treating the old failure as recoverable red is lifecycle drift.

**Required repair:** reconcile health/workflow lifecycle with that terminal state. Do **not** retry the provider, increase budget, fabricate MARKET data or reset billing history.

Task: `research/codex/intake/2026/08/codex-historical-cfgi-terminal-lifecycle-reconciliation-v1.json`

Linked historical health signature: `317201b09ae61bb7336b`

Post-fix gate: `ZERO_AUTOMATIC_PAID_RETRIES_AND_TERMINAL_STATE_NOT_REPORTED_AS_RECOVERABLE_RED`

## Analysis-first queue

### OPR-003 - Forecast censor attribution, P1

Audit snapshot showed 155 due, 80 matured, 79 censored and 159 adjudicated, approximately 49.7% censored. The rate is a research-health concern, not proof of a bug. The analysis must attribute censor causes to legitimate point-in-time absence, upstream unavailability, target-unit/schema quarantine, deadline/freshness miss, malformed candidate, owner/provider unavailable or unknown. Historical rows may not be rewritten.

Task: `research/remediation/openai_api/forecast-censor-attribution-v1.json`

### OPR-004 - Automation complexity review, P1

Audit scale was approximately 110 local workflows, 100 registered, 41 scheduled and 47 writers. Classify every workflow as `KEEP`, `MERGE_WITH_EXISTING`, `SCHEDULE_REMOVE`, `MANUAL_ONLY`, `ARCHIVE` or `UNKNOWN_NEEDS_EVIDENCE`. Identify duplicate owners, writer/concurrency overlap, terminalized/superseded workflows and action-runtime deprecation exposure. Analysis phase makes no schedule or deletion changes.

Task: `research/remediation/openai_api/automation-complexity-review-v1.json`

### OPR-005 - Draft PR hygiene, P2

PRs #49, #83, #96, #122 and #319 remain open drafts. Each must be compared against fresh main. Valid classifications are `ACTIVE_UNIQUE_WORK`, `SUPERSEDED_BY_MAIN`, `STALE_BUT_UNCLEAR`, `SAFE_TO_CLOSE` or `REBASE_OR_EXTRACT_SMALL_REMAINDER`. Age alone is never closure evidence. No automated close or branch delete is authorized.

Task: `research/remediation/openai_api/repository-pr-hygiene-review-v1.json`

## Observe-only queue

PR #557 is merged, so its intraday tuple crash and coordinator assertion drift are code-fixed but require expected production evidence. PR #542 and PR #544 are also merged and should not remain listed as open code defects. Verify Daily Capture six-anchor stability and Situation Room research-only authority on subsequent runs.

Task: `research/remediation/observe/post-merge-operational-verification-v1.json`

## External dependency

The intended external Vault backup boundary remains an access/verification matter. Do not work around missing repository authorization by copying restricted material into the public control plane or by pretending an internal branch is an independent external backup.

Task: `research/remediation/external/vault-backup-access-v1.json`

## Global guardrails

1. Fresh GitHub `main` is authoritative over this document.
2. Do not manually edit generated `LATEST_REMEDIATION_QUEUE.json` or `LATEST_CODEX_READY_TASKS.json`; the remediation controller owns those outputs.
3. No remediation changes market gates, model weights, portfolio logic, canonical market semantics or API budgets without separate governance.
4. No missing provider data may be fabricated or retrospectively inferred.
5. Restricted provider data stays in `Donh91/secrets`; credentials stay in GitHub Secrets.
6. Automatic code write and automatic merge remain false.
7. Non-reproducing or superseded findings terminate as clean no-op.
