# Automation Production Health
Status: **AMBER**
Generated: `2026-08-15T15:42:24.390273Z`
Workflows: 58 local / 63 registered
Scheduled: 24
Writers: 22
GREEN / AMBER / RED: 37 / 21 / 0

## Workflow matrix
| Workflow | Lifecycle | Schedule | Writer | Last conclusion | Last run | Status | Findings |
|---|---|---:|---:|---|---|---|---|
| `adaptive-decision-miss-validation.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `adaptive-evidence-gap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T14:20:05Z | **GREEN** | None |
| `adaptive-evidence-gap.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `adaptive-gap-validation-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T14:20:05Z | **GREEN** | None |
| `api-agent-gateway-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T14:20:05Z | **GREEN** | None |
| `automation-production-health-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T14:20:05Z | **GREEN** | None |
| `automation-production-health.yml` | `ACTIVE` | yes | yes | in_progress | 2026-08-15T15:42:16Z | **GREEN** | None |
| `backtest-engine-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-readiness-contracts.yml` | `ACTIVE` | no | no | success | 2026-07-30T18:08:16Z | **GREEN** | None |
| `backtest-wave1-2-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-wave1-3-authority-lineage.yml` | `ACTIVE` | no | no | success | 2026-07-28T16:15:15Z | **GREEN** | None |
| `backtest-wave1-4-prospective.yml` | `ACTIVE` | yes | no | success | 2026-08-14T16:26:56Z | **GREEN** | None |
| `binance-spot-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-08-01T19:31:36Z | **GREEN** | None |
| `binance-usdm-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `continuity-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T14:20:05Z | **GREEN** | None |
| `continuity-learning-maintenance.yml` | `ACTIVE` | yes | yes | success | 2026-08-14T21:58:09Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `daily-capture-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T13:54:53Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `daily-director-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-08-15T13:55:18Z | **GREEN** | None |
| `daily-raw-owner-capture.yml` | `ACTIVE` | yes | yes | success | 2026-08-15T13:46:21Z | **GREEN** | None |
| `daily-settled-etf-calibration.yml` | `ACTIVE` | yes | yes | success | 2026-08-15T06:53:53Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `daily-stablecoin-liquidity.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `data-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T14:20:05Z | **GREEN** | None |
| `data-terminal-shadow-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `dataset-registry-gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `evidence-closure-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T13:54:53Z | **GREEN** | None |
| `experiment-lifecycle-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T11:55:29Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `fetch_btc_d_cmc_free.yml` | `ACTIVE` | no | no | success | 2026-07-12T00:09:38Z | **GREEN** | None |
| `framework-learning-operations.yml` | `ACTIVE` | yes | yes | success | 2026-08-15T02:27:34Z | **GREEN** | None |
| `full-architecture-1to7-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T14:20:05Z | **GREEN** | None |
| `hourly-sequence-capture.yml` | `ACTIVE` | yes | yes | success | 2026-08-15T10:01:30Z | **GREEN** | None |
| `legacy-knowledge-bootstrap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `mar_wp04c4_gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T01:41:02Z | **GREEN** | None |
| `master-monday-preflight-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T11:55:29Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `master-monday-remaining-gaps.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T10:59:00Z | **AMBER** | SCHEDULE_STALE |
| `okx-swap-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `operations-dashboard-gate.yml` | `ACTIVE` | no | no | success | 2026-08-05T15:35:53Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `operations-dashboard.yml` | `ACTIVE` | yes | yes | success | 2026-08-15T04:35:41Z | **GREEN** | None |
| `owner-bound-daily-director-manual.yml` | `ACTIVE` | no | no | success | 2026-08-15T14:20:05Z | **GREEN** | None |
| `pdf-inspector-ingestion.yml` | `ACTIVE` | no | no | success | 2026-08-02T18:16:02Z | **GREEN** | None |
| `pdlt-bootstrap-once.yml` | `ACTIVE` | no | no | skipped | 2026-08-10T15:36:07Z | **GREEN** | None |
| `pdlt-daily-census.yml` | `ACTIVE` | yes | yes | success | 2026-08-14T22:08:09Z | **GREEN** | None |
| `pdlt-discovery-once.yml` | `EXPECTED_BLOCK` | no | no | failure | 2026-08-09T19:58:23Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-08-14T22:44:17Z | **GREEN** | None |
| `pdlt-runtime-gate.yml` | `ACTIVE` | yes | no | success | 2026-08-10T20:05:49Z | **AMBER** | SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `pdlt-v1-1.yml` | `ACTIVE` | no | no | success | 2026-08-10T15:36:09Z | **GREEN** | None |
| `remediation-maturation-gate.yml` | `ACTIVE` | no | no | success | 2026-08-10T20:05:49Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `remediation-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-08-15T04:14:08Z | **GREEN** | None |
| `research-execution-coordinator.yml` | `ACTIVE` | yes | yes | success | 2026-08-15T07:38:13Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `rich-breadth-checkpoint.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `sequential-research-queue.yml` | `ACTIVE` | yes | yes | success | 2026-08-15T07:02:47Z | **GREEN** | None |
| `specialist-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-01T05:33:29Z | **GREEN** | None |
| `storage-health-gate.yml` | `ACTIVE` | no | no | success | 2026-08-15T14:20:05Z | **GREEN** | None |
| `sunday-market-close-and-cfgi.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T02:23:55Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES, SCHEDULE_STALE |
| `top100-breadth-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-08-15T13:54:53Z | **GREEN** | None |
| `validate_m3_forward_ledger.yml` | `ACTIVE` | no | no | none | none | **GREEN** | None |
| `weekly-api-calibration-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T10:57:37Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES, SCHEDULE_STALE |
| `weekly-raw-calibration-bridge.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T02:39:34Z | **AMBER** | SCHEDULE_STALE |
| `weekly-sol-adversarial-review.yml` | `ACTIVE` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |

## Blockers
- None

## Warnings
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-full-profile-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-live-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:harness-redteam-p0-remediation-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:persistent-agent-runtime-readiness-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:t4-microstructure-live-readback.yml
- adaptive-decision-miss-validation.yml:NO_RUN_HISTORY
- adaptive-evidence-gap.yml:NO_RUN_HISTORY
- backtest-engine-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-wave1-2-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- continuity-learning-maintenance.yml:RECOVERING_AFTER_RECENT_FAILURES
- daily-capture-architecture-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- daily-settled-etf-calibration.yml:RECOVERING_AFTER_RECENT_FAILURES
- daily-stablecoin-liquidity.yml:NO_RUN_HISTORY
- experiment-lifecycle-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- master-monday-preflight-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- master-monday-remaining-gaps.yml:SCHEDULE_STALE
- operations-dashboard-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- pdlt-discovery-once.yml:EXPECTED_BLOCK
- pdlt-runtime-gate.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- remediation-maturation-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- research-execution-coordinator.yml:RECOVERING_AFTER_RECENT_FAILURES
- rich-breadth-checkpoint.yml:NO_RUN_HISTORY
- sunday-market-close-and-cfgi.yml:RECOVERING_AFTER_RECENT_FAILURES
- sunday-market-close-and-cfgi.yml:SCHEDULE_STALE
- weekly-api-calibration-shadow.yml:RECOVERING_AFTER_RECENT_FAILURES
- weekly-api-calibration-shadow.yml:SCHEDULE_STALE
- weekly-raw-calibration-bridge.yml:SCHEDULE_STALE
- weekly-sol-adversarial-review.yml:NO_RUN_HISTORY
