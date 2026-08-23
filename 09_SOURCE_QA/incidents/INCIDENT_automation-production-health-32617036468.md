# Automation Production Health
Status: **RED**
Generated: `2026-08-23T04:06:36.041268Z`
Workflows: 101 local / 100 registered
Scheduled: 39
Writers: 44
GREEN / AMBER / RED: 71 / 26 / 4

## Workflow matrix
| Workflow | Lifecycle | Schedule | Writer | Last conclusion | Last run | Status | Findings |
|---|---|---:|---:|---|---|---|---|
| `adaptive-decision-miss-validation.yml` | `ACTIVE` | yes | yes | success | 2026-08-22T22:53:09Z | **GREEN** | None |
| `adaptive-evidence-gap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T14:20:05Z | **GREEN** | None |
| `adaptive-evidence-gap.yml` | `ACTIVE` | yes | yes | success | 2026-08-22T22:01:10Z | **GREEN** | None |
| `adaptive-gap-validation-gate.yml` | `ACTIVE` | no | no | success | 2026-08-16T10:26:31Z | **GREEN** | None |
| `adaptive-rotation-cadence.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T03:16:19Z | **GREEN** | None |
| `api-agent-gateway-gate.yml` | `ACTIVE` | no | no | success | 2026-08-16T10:26:31Z | **GREEN** | None |
| `automation-production-health-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T22:10:17Z | **GREEN** | None |
| `automation-production-health.yml` | `ACTIVE` | yes | yes | in_progress | 2026-08-23T04:06:27Z | **GREEN** | None |
| `autonomous-research-governance-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T22:10:17Z | **GREEN** | None |
| `autonomous-research-governance-loop.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `backtest-engine-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-readiness-contracts.yml` | `ACTIVE` | no | no | success | 2026-07-30T18:08:16Z | **GREEN** | None |
| `backtest-wave1-2-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-wave1-3-authority-lineage.yml` | `ACTIVE` | no | no | success | 2026-07-28T16:15:15Z | **GREEN** | None |
| `backtest-wave1-4-prospective.yml` | `ACTIVE` | yes | no | success | 2026-08-22T15:51:00Z | **GREEN** | None |
| `binance-spot-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-08-01T19:31:36Z | **GREEN** | None |
| `binance-usdm-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `cfgi-recovery-launch-once.yml` | `ACTIVE` | yes | no | success | 2026-08-23T03:37:16Z | **AMBER** | SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `cfgi-recovery-launch-trigger.yml` | `ACTIVE` | no | yes | skipped | 2026-08-22T22:10:31Z | **GREEN** | None |
| `cfgi-v3-launch-receipt-publish.yml` | `ACTIVE` | no | yes | success | 2026-08-23T03:37:31Z | **GREEN** | None |
| `codex-intake-dispatch.yml` | `ACTIVE` | no | no | none | none | **GREEN** | None |
| `continuity-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-08-20T08:26:34Z | **GREEN** | None |
| `continuity-learning-maintenance.yml` | `ACTIVE` | yes | yes | success | 2026-08-22T21:57:14Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-gate.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:00Z | **GREEN** | None |
| `cowork-historical-altseason-bundle-receipt.yml` | `ACTIVE` | no | yes | success | 2026-08-21T09:47:59Z | **GREEN** | None |
| `cowork-historical-altseason-bundle.yml` | `ACTIVE` | no | no | success | 2026-08-21T09:47:47Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:38:07Z | **GREEN** | None |
| `cycle-navigator-autonomous-calibration-loop.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `daily-capture-architecture-gate.yml` | `ACTIVE` | no | no | failure | 2026-08-19T12:46:58Z | **RED** | REPEATED_CONSECUTIVE_FAILURES |
| `daily-director-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-08-22T21:46:53Z | **GREEN** | None |
| `daily-raw-owner-capture.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T02:00:06Z | **GREEN** | None |
| `daily-settled-etf-calibration.yml` | `ACTIVE` | yes | yes | success | 2026-08-22T06:55:21Z | **GREEN** | None |
| `daily-stablecoin-liquidity.yml` | `ACTIVE` | yes | yes | success | 2026-08-22T05:48:22Z | **GREEN** | None |
| `data-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T22:10:17Z | **GREEN** | None |
| `data-terminal-shadow-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `dataset-registry-gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `entry-signal-ledger-gate.yml` | `ACTIVE` | no | no | success | 2026-08-20T13:44:05Z | **GREEN** | None |
| `entry-signal-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T03:37:19Z | **GREEN** | None |
| `ethbtc-persistence-lifecycle.yml` | `ACTIVE` | no | yes | success | 2026-08-22T21:47:47Z | **GREEN** | None |
| `evidence-closure-gate.yml` | `ACTIVE` | no | no | success | 2026-08-19T12:46:58Z | **GREEN** | None |
| `evidence-lifecycle-observability-gate.yml` | `ACTIVE` | no | no | success | 2026-08-16T11:33:59Z | **GREEN** | None |
| `evidence-lifecycle-store-health.yml` | `ACTIVE` | yes | no | success | 2026-08-23T04:01:58Z | **GREEN** | None |
| `experiment-lifecycle-gate.yml` | `ACTIVE` | no | no | success | 2026-08-20T08:26:34Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `fetch_btc_d_cmc_free.yml` | `ACTIVE` | no | no | success | 2026-07-12T00:09:38Z | **GREEN** | None |
| `framework-learning-operations.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T02:37:58Z | **GREEN** | None |
| `full-architecture-1to7-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T22:10:17Z | **GREEN** | None |
| `historical-altseason-cfgi-enrichment.yml` | `ACTIVE` | no | no | failure | 2026-08-23T02:49:36Z | **RED** | REPEATED_CONSECUTIVE_FAILURES |
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
| `hourly-sequence-capture.yml` | `ACTIVE` | yes | yes | success | 2026-08-22T22:13:46Z | **GREEN** | None |
| `intraday-execution-gate.yml` | `ACTIVE` | no | no | success | 2026-08-20T20:04:47Z | **GREEN** | None |
| `intraday-execution-research.yml` | `ACTIVE` | yes | yes | failure | 2026-08-23T03:42:47Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES, SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `legacy-knowledge-bootstrap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `mar_wp04c4_gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T01:41:02Z | **GREEN** | None |
| `master-monday-preflight-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T11:55:29Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `master-monday-remaining-gaps.yml` | `ACTIVE` | yes | yes | success | 2026-08-17T07:43:24Z | **AMBER** | SCHEDULE_STALE |
| `okx-swap-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `operations-dashboard-gate.yml` | `ACTIVE` | no | no | success | 2026-08-05T15:35:53Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `operations-dashboard.yml` | `ACTIVE` | yes | yes | success | 2026-08-22T16:22:16Z | **GREEN** | None |
| `owner-bound-daily-director-manual.yml` | `ACTIVE` | no | no | success | 2026-08-16T10:26:31Z | **GREEN** | None |
| `pdf-inspector-ingestion.yml` | `ACTIVE` | no | no | success | 2026-08-02T18:16:02Z | **GREEN** | None |
| `pdlt-bootstrap-once.yml` | `ACTIVE` | no | no | skipped | 2026-08-10T15:36:07Z | **GREEN** | None |
| `pdlt-daily-census.yml` | `ACTIVE` | yes | yes | success | 2026-08-22T22:02:35Z | **GREEN** | None |
| `pdlt-discovery-once.yml` | `EXPECTED_BLOCK` | no | no | failure | 2026-08-09T19:58:23Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-08-22T22:42:35Z | **GREEN** | None |
| `pdlt-runtime-gate.yml` | `ACTIVE` | yes | no | success | 2026-08-10T20:05:49Z | **AMBER** | SCHEDULE_STALE, SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `pdlt-v1-1.yml` | `ACTIVE` | no | no | success | 2026-08-10T15:36:09Z | **GREEN** | None |
| `pullback-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-08-20T14:17:33Z | **GREEN** | None |
| `pullback-learning-ledger.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T03:37:52Z | **GREEN** | None |
| `remediation-maturation-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T13:30:18Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `remediation-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-08-22T15:55:02Z | **GREEN** | None |
| `research-execution-coordinator.yml` | `ACTIVE` | yes | yes | failure | 2026-08-22T19:30:56Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES |
| `research-owner-breadth-daily.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `research-owner-btcd-daily.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `rich-breadth-checkpoint.yml` | `ACTIVE` | yes | yes | success | 2026-08-23T02:02:31Z | **GREEN** | None |
| `sequential-research-queue.yml` | `ACTIVE` | yes | yes | success | 2026-08-22T07:04:51Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:41:03Z | **GREEN** | None |
| `shadow-registry-autonomous-portfolio-loop.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `shadow-registry-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:41:03Z | **GREEN** | None |
| `shadow-registry-weekly.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `shared-row-prospective-evidence-loop.yml` | `ACTIVE` | yes | yes | success | 2026-08-22T23:00:28Z | **GREEN** | None |
| `shared-row-tournament-research-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:21:07Z | **GREEN** | None |
| `shared-row-tournament-weekly.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `source-provenance-recovery-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T19:50:51Z | **GREEN** | None |
| `source-provenance-recovery-loop.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `specialist-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-01T05:33:29Z | **GREEN** | None |
| `storage-health-gate.yml` | `ACTIVE` | no | no | success | 2026-08-22T22:10:17Z | **GREEN** | None |
| `sunday-market-close-and-cfgi.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `top100-breadth-owner-manual.yml` | `ACTIVE` | no | no | none | none | **AMBER** | WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `validate_m3_forward_ledger.yml` | `ACTIVE` | no | no | none | none | **AMBER** | WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `weekly-api-calibration-shadow.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `weekly-raw-calibration-bridge.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |
| `weekly-sol-adversarial-review.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY, WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE |

## Blockers
- daily-capture-architecture-gate.yml:REPEATED_CONSECUTIVE_FAILURES
- historical-altseason-cfgi-enrichment.yml:REPEATED_CONSECUTIVE_FAILURES
- intraday-execution-research.yml:LATEST_RUN_FAILED
- intraday-execution-research.yml:REPEATED_CONSECUTIVE_FAILURES
- intraday-execution-research.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- research-execution-coordinator.yml:LATEST_RUN_FAILED
- research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES

## Warnings
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-full-profile-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-live-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:harness-redteam-p0-remediation-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:historical-shadow-validation-stage1-manifest.yml
- REGISTERED_WITHOUT_LOCAL_FILE:persistent-agent-runtime-readiness-gate.yml
- autonomous-research-governance-loop.yml:NO_RUN_HISTORY
- backtest-engine-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-wave1-2-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- cfgi-recovery-launch-once.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- cycle-navigator-autonomous-calibration-loop.yml:NO_RUN_HISTORY
- experiment-lifecycle-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- historical-altseason-lab-gate.yml:ARTIFACT_RETENTION_UNBOUNDED
- historical-altseason-lab-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- historical-altseason-throughput-gate.yml:ARTIFACT_RETENTION_UNBOUNDED
- master-monday-preflight-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- master-monday-remaining-gaps.yml:SCHEDULE_STALE
- operations-dashboard-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- pdlt-discovery-once.yml:EXPECTED_BLOCK
- pdlt-runtime-gate.yml:SCHEDULE_STALE
- pdlt-runtime-gate.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- remediation-maturation-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- research-owner-breadth-daily.yml:NO_RUN_HISTORY
- research-owner-btcd-daily.yml:NO_RUN_HISTORY
- shadow-registry-autonomous-portfolio-loop.yml:NO_RUN_HISTORY
- shadow-registry-weekly.yml:NO_RUN_HISTORY
- shared-row-tournament-weekly.yml:NO_RUN_HISTORY
- source-provenance-recovery-loop.yml:NO_RUN_HISTORY
- sunday-market-close-and-cfgi.yml:NO_RUN_HISTORY
- sunday-market-close-and-cfgi.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- top100-breadth-owner-manual.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- validate_m3_forward_ledger.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- weekly-api-calibration-shadow.yml:NO_RUN_HISTORY
- weekly-api-calibration-shadow.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- weekly-raw-calibration-bridge.yml:NO_RUN_HISTORY
- weekly-raw-calibration-bridge.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
- weekly-sol-adversarial-review.yml:NO_RUN_HISTORY
- weekly-sol-adversarial-review.yml:WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE
