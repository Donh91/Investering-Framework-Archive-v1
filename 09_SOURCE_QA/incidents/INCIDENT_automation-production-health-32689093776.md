# Automation Production Health
Status: **RED**
Generated: `2026-08-24T04:11:56.513064Z`
Workflows: 110 local / 100 registered
Scheduled: 41
Writers: 47
GREEN / AMBER / RED: 78 / 29 / 3

## Workflow matrix
| Workflow | Lifecycle | Schedule | Writer | Last conclusion | Last run | Status | Findings |
|---|---|---:|---:|---|---|---|---|
| `adaptive-decision-miss-validation.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T22:53:06Z | **GREEN** | None |
| `adaptive-evidence-gap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T14:20:05Z | **GREEN** | None |
| `adaptive-evidence-gap.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T22:01:12Z | **GREEN** | None |
| `adaptive-gap-validation-gate.yml` | `ACTIVE` | no | no | success | 2026-08-16T10:26:31Z | **GREEN** | None |
| `adaptive-rotation-cadence.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T03:17:17Z | **GREEN** | None |
| `api-agent-gateway-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T21:14:25Z | **GREEN** | None |
| `automation-production-health-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T21:21:45Z | **GREEN** | None |
| `automation-production-health.yml` | `ACTIVE` | yes | yes | in_progress | 2026-08-24T04:11:44Z | **GREEN** | None |
| `autonomous-research-governance-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T11:29:50Z | **GREEN** | None |
| `autonomous-research-governance-loop.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T05:52:12Z | **GREEN** | None |
| `backtest-engine-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-readiness-contracts.yml` | `ACTIVE` | no | no | success | 2026-07-30T18:08:16Z | **GREEN** | None |
| `backtest-wave1-2-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-wave1-3-authority-lineage.yml` | `ACTIVE` | no | no | success | 2026-07-28T16:15:15Z | **GREEN** | None |
| `backtest-wave1-4-prospective.yml` | `ACTIVE` | yes | no | success | 2026-08-23T15:52:01Z | **GREEN** | None |
| `binance-spot-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-08-01T19:31:36Z | **GREEN** | None |
| `binance-usdm-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `buildwithclaude-shadow-evidence-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T23:51:52Z | **GREEN** | None |
| `buildwithclaude-shadow-prospective-observer.yml` | `ACTIVE` | no | no | success | 2026-08-23T15:24:40Z | **GREEN** | None |
| `buildwithclaude-shadow-round1.yml` | `ACTIVE` | no | no | success | 2026-08-23T20:47:41Z | **GREEN** | None |
| `cfgi-recovery-launch-once.yml` | `ACTIVE` | no | no | success | 2026-08-23T07:25:36Z | **GREEN** | None |
| `cfgi-recovery-launch-trigger.yml` | `ACTIVE` | no | yes | skipped | 2026-08-23T21:21:59Z | **GREEN** | None |
| `cfgi-v3-launch-receipt-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-23T07:24:14Z | **GREEN** | None |
| `codex-intake-dispatch.yml` | `ACTIVE` | no | no | success | 2026-08-23T08:18:32Z | **GREEN** | None |
| `continuity-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T21:21:45Z | **GREEN** | None |
| `continuity-learning-maintenance.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T21:56:50Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-gate.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:00Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-receipt.yml` | `ACTIVE` | no | yes | success | 2026-08-21T09:47:59Z | **GREEN** | None |
| `cowork-historical-altseason-bundle.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:47Z | **GREEN** | None |
| `cross-repo-agent-context-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T14:08:02Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:38:07Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-loop.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `daily-capture-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T21:21:45Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `daily-director-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T21:46:53Z | **GREEN** | None |
| `daily-raw-owner-capture.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T01:58:07Z | **GREEN** | None |
| `daily-settled-etf-calibration.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T06:56:32Z | **GREEN** | None |
| `daily-stablecoin-liquidity.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T05:50:16Z | **GREEN** | None |
| `data-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T21:21:45Z | **GREEN** | None |
| `data-terminal-shadow-manual.yml` | `ACTIVE` | no | no | failure | 2026-08-23T21:21:45Z | **GREEN** | None |
| `dataset-registry-gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `entry-signal-ledger-gate.yml` | `ACTIVE` | no | no | success | 2026-08-20T13:44:05Z | **GREEN** | None |
| `entry-signal-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T03:40:13Z | **GREEN** | None |
| `ethbtc-persistence-lifecycle.yml` | `ACTIVE` | no | yes | success | 2026-08-23T21:47:52Z | **GREEN** | None |
| `evidence-closure-gate.yml` | `ACTIVE` | no | no | success | 2026-08-19T12:46:58Z | **GREEN** | None |
| `evidence-lifecycle-observability-gate.yml` | `ACTIVE` | no | no | success | 2026-08-16T11:33:59Z | **GREEN** | None |
| `evidence-lifecycle-store-health.yml` | `ACTIVE` | yes | no | success | 2026-08-24T04:06:50Z | **GREEN** | None |
| `experiment-lifecycle-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T21:20:14Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `fetch_btc_d_cmc_free.yml` | `ACTIVE` | no | no | success | 2026-07-12T00:09:38Z | **GREEN** | None |
| `framework-learning-operations.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T02:38:27Z | **GREEN** | None |
| `full-architecture-1to7-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T21:21:45Z | **GREEN** | None |
| `historical-altseason-cfgi-enrichment.yml` | `ACTIVE` | no | no | failure | 2026-08-23T05:18:07Z | **RED** | REPEATED_CONSECUTIVE_FAILURES |
| `historical-altseason-cfgi-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-21T08:08:20Z | **GREEN** | None |
| `historical-altseason-cfgi-reservation.yml` | `ACTIVE` | no | yes | failure | 2026-08-22T06:54:11Z | **GREEN** | None |
| `historical-altseason-cfgi-run-audit.yml` | `ACTIVE` | no | yes | failure | 2026-08-22T06:36:46Z | **GREEN** | None |
| `historical-altseason-cfgi-terminal-finalize.yml` | `ACTIVE` | no | no | success | 2026-08-21T13:55:43Z | **GREEN** | None |
| `historical-altseason-cfgi-terminal-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-21T13:55:57Z | **GREEN** | None |
| `historical-altseason-free-bootstrap.yml` | `ACTIVE` | no | no | success | 2026-08-22T06:36:46Z | **GREEN** | None |
| `historical-altseason-free-publish-regression-gate.yml` | `ACTIVE` | no | no | success | 2026-08-21T13:54:37Z | **GREEN** | None |
| `historical-altseason-free-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-22T06:53:59Z | **GREEN** | None |
| `historical-altseason-lab-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T06:36:30Z | **AMBER** | ARTIFACT_RETENTION_UNBOUNDED, RECOVERING_AFTER_RECENT_FAILURES |
| `historical-altseason-throughput-gate.yml` | `ACTIVE` | no | no | success | 2026-08-21T13:55:43Z | **AMBER** | ARTIFACT_RETENTION_UNBOUNDED |
| `hourly-sequence-capture.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T01:56:19Z | **GREEN** | None |
| `intraday-execution-gate.yml` | `ACTIVE` | no | no | success | 2026-08-20T20:04:47Z | **GREEN** | None |
| `intraday-execution-research.yml` | `ACTIVE` | yes | yes | failure | 2026-08-24T03:46:21Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES, SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `legacy-knowledge-bootstrap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `mar_wp04c4_gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T01:41:02Z | **GREEN** | None |
| `master-monday-preflight-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T15:24:40Z | **GREEN** | None |
| `master-monday-remaining-gaps.yml` | `ACTIVE` | yes | yes | success | 2026-08-17T07:43:24Z | **AMBER** | SCHEDULE_STALE |
| `okx-swap-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `operations-dashboard-gate.yml` | `ACTIVE` | no | no | success | 2026-08-05T15:35:53Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `operations-dashboard.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T16:24:04Z | **GREEN** | None |
| `owner-bound-daily-director-manual.yml` | `ACTIVE` | no | no | success | 2026-08-23T15:24:40Z | **GREEN** | None |
| `pdf-inspector-ingestion.yml` | `ACTIVE` | no | no | success | 2026-08-02T18:16:02Z | **GREEN** | None |
| `pdlt-bootstrap-once.yml` | `ACTIVE` | no | no | skipped | 2026-08-10T15:36:07Z | **GREEN** | None |
| `pdlt-daily-census.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T22:02:33Z | **GREEN** | None |
| `pdlt-discovery-once.yml` | `EXPECTED_BLOCK` | no | no | failure | 2026-08-09T19:58:23Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T22:42:35Z | **GREEN** | None |
| `pdlt-runtime-gate.yml` | `ACTIVE` | yes | no | success | 2026-08-10T20:05:49Z | **AMBER** | SCHEDULE_STALE, SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `pdlt-v1-1.yml` | `ACTIVE` | no | no | success | 2026-08-10T15:36:09Z | **GREEN** | None |
| `phase4-no-hindsight-replay.yml` | `ACTIVE` | no | no | success | 2026-08-23T17:53:27Z | **GREEN** | None |
| `pullback-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-08-20T14:17:33Z | **GREEN** | None |
| `pullback-learning-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T03:40:37Z | **GREEN** | None |
| `remediation-maturation-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T13:30:18Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `remediation-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T15:56:06Z | **GREEN** | None |
| `research-execution-coordinator.yml` | `ACTIVE` | yes | yes | failure | 2026-08-23T19:30:43Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES |
| `research-owner-breadth-daily.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T05:46:07Z | **GREEN** | None |
| `research-owner-btcd-daily.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T05:58:36Z | **GREEN** | None |
| `rich-breadth-checkpoint.yml` | `ACTIVE` | yes | yes | success | 2026-08-24T02:00:32Z | **GREEN** | None |
| `round3-contract-freeze-gate.yml` | `ACTIVE` | no | no | success | 2026-08-23T14:08:02Z | **GREEN** | None |
| `round3-v2-materialization.yml` | `ACTIVE` | no | no | success | 2026-08-23T13:17:33Z | **GREEN** | None |
| `sequential-research-queue.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T07:07:03Z | **GREEN** | None |
| `shadow-admission-ai-decider.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T23:58:58Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:41:03Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-loop.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `shadow-registry-gate.yml` | `ACTIVE` | no | no | none | none | **AMBER** | WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `shadow-registry-weekly.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `shared-row-prospective-evidence-loop.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `shared-row-tournament-research-gate.yml` | `ACTIVE` | no | no | none | none | **AMBER** | WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `shared-row-tournament-weekly.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `source-provenance-recovery-gate.yml` | `ACTIVE` | no | no | none | none | **AMBER** | WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `source-provenance-recovery-loop.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `specialist-architecture-gate.yml` | `ACTIVE` | no | no | none | none | **AMBER** | WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `storage-health-gate.yml` | `ACTIVE` | no | no | none | none | **AMBER** | WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `sunday-market-close-and-cfgi.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `top100-breadth-owner-manual.yml` | `ACTIVE` | no | no | none | none | **AMBER** | WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `unified-experimental-lifecycle-adjudication.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `validate_m3_forward_ledger.yml` | `ACTIVE` | no | no | none | none | **AMBER** | WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `weekly-api-calibration-shadow.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `weekly-raw-calibration-bridge.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `weekly-sol-adversarial-review.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |

## Blockers
- historical-altseason-cfgi-enrichment.yml:REPEATED_CONSECUTIVE_FAILURES
- intraday-execution-research.yml:LATEST_RUN_FAILED
- intraday-execution-research.yml:REPEATED_CONSECUTIVE_FAILURES
- intraday-execution-research.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- research-execution-coordinator.yml:LATEST_RUN_FAILED
- research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES

## Warnings
- REGISTERED_WITHOUT_LOCAL_FILE:agent-tool-shadow-round2.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-full-profile-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-live-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:harness-redteam-p0-remediation-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:historical-shadow-validation-stage1-manifest.yml
- REGISTERED_WITHOUT_LOCAL_FILE:persistent-agent-runtime-readiness-gate.yml
- backtest-engine-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-wave1-2-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- cycle-navigator-autonomous-calibration-loop.yml:NO_RUN_HISTORY
- daily-capture-architecture-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- experiment-lifecycle-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- historical-altseason-lab-gate.yml:ARTIFACT_RETENTION_UNBOUNDED
- historical-altseason-lab-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- historical-altseason-throughput-gate.yml:ARTIFACT_RETENTION_UNBOUNDED
- master-monday-remaining-gaps.yml:SCHEDULE_STALE
- operations-dashboard-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- pdlt-discovery-once.yml:EXPECTED_BLOCK
- pdlt-runtime-gate.yml:SCHEDULE_STALE
- pdlt-runtime-gate.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- remediation-maturation-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- shadow-registry-autonomous-portfolio-loop.yml:NO_RUN_HISTORY
- shadow-registry-gate.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- shadow-registry-weekly.yml:NO_RUN_HISTORY
- shadow-registry-weekly.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- shared-row-prospective-evidence-loop.yml:NO_RUN_HISTORY
- shared-row-prospective-evidence-loop.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- shared-row-tournament-research-gate.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- shared-row-tournament-weekly.yml:NO_RUN_HISTORY
- shared-row-tournament-weekly.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- source-provenance-recovery-gate.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- source-provenance-recovery-loop.yml:NO_RUN_HISTORY
- source-provenance-recovery-loop.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- specialist-architecture-gate.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- storage-health-gate.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- sunday-market-close-and-cfgi.yml:NO_RUN_HISTORY
- sunday-market-close-and-cfgi.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- top100-breadth-owner-manual.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- unified-experimental-lifecycle-adjudication.yml:NO_RUN_HISTORY
- unified-experimental-lifecycle-adjudication.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- validate_m3_forward_ledger.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- weekly-api-calibration-shadow.yml:NO_RUN_HISTORY
- weekly-api-calibration-shadow.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- weekly-raw-calibration-bridge.yml:NO_RUN_HISTORY
- weekly-raw-calibration-bridge.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- weekly-sol-adversarial-review.yml:NO_RUN_HISTORY
- weekly-sol-adversarial-review.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
