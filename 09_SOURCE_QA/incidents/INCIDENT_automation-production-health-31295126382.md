# Automation Production Health
Status: **RED**
Generated: `2026-08-09T04:42:14.333319Z`
Workflows: 48 local / 53 registered
Scheduled: 17
Writers: 16
GREEN / AMBER / RED: 37 / 8 / 3

## Workflow matrix
| Workflow | Schedule | Writer | Last conclusion | Last run | Status | Findings |
|---|---:|---:|---|---|---|---|
| `api-agent-gateway-gate.yml` | no | no | success | 2026-08-07T18:44:20Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `automation-production-health-gate.yml` | no | no | success | 2026-08-08T18:38:29Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `automation-production-health.yml` | yes | yes | in_progress | 2026-08-09T04:42:08Z | **GREEN** | None |
| `backtest-engine-foundation.yml` | no | no | success | 2026-07-31T01:15:06Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-readiness-contracts.yml` | no | no | success | 2026-07-30T18:08:16Z | **GREEN** | None |
| `backtest-wave1-2-foundation.yml` | no | no | success | 2026-07-31T01:15:06Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-wave1-3-authority-lineage.yml` | no | no | success | 2026-07-28T16:15:15Z | **GREEN** | None |
| `backtest-wave1-4-prospective.yml` | yes | no | success | 2026-08-08T15:58:48Z | **GREEN** | None |
| `binance-spot-owner-manual.yml` | no | no | success | 2026-08-01T19:31:36Z | **GREEN** | None |
| `binance-usdm-owner-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `continuity-learning-gate.yml` | no | no | success | 2026-08-08T18:38:29Z | **GREEN** | None |
| `continuity-learning-maintenance.yml` | yes | yes | success | 2026-08-08T22:01:39Z | **GREEN** | None |
| `daily-capture-architecture-gate.yml` | no | no | success | 2026-08-08T18:38:29Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `daily-director-shadow.yml` | yes | yes | success | 2026-08-08T21:50:23Z | **GREEN** | None |
| `daily-raw-owner-capture.yml` | yes | yes | success | 2026-08-08T21:40:50Z | **GREEN** | None |
| `data-architecture-gate.yml` | no | no | success | 2026-08-08T18:38:29Z | **GREEN** | None |
| `data-terminal-shadow-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `dataset-registry-gate.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `experiment-lifecycle-gate.yml` | no | no | success | 2026-08-07T19:30:47Z | **GREEN** | None |
| `fetch_btc_d_cmc_free.yml` | no | no | success | 2026-07-12T00:09:38Z | **GREEN** | None |
| `framework-learning-operations.yml` | yes | yes | success | 2026-08-09T03:09:23Z | **GREEN** | None |
| `full-architecture-1to7-gate.yml` | no | no | success | 2026-08-08T18:38:29Z | **GREEN** | None |
| `hourly-sequence-capture.yml` | yes | yes | success | 2026-08-08T22:13:14Z | **GREEN** | None |
| `legacy-knowledge-bootstrap-gate.yml` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `mar_wp04c4_gate.yml` | no | no | success | 2026-07-31T01:41:02Z | **GREEN** | None |
| `master-monday-preflight-gate.yml` | no | no | success | 2026-08-05T15:35:53Z | **GREEN** | None |
| `master-monday-remaining-gaps.yml` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `okx-swap-owner-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `operations-dashboard-gate.yml` | no | no | success | 2026-08-05T15:35:53Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `operations-dashboard.yml` | yes | yes | success | 2026-08-08T16:31:48Z | **GREEN** | None |
| `owner-bound-daily-director-manual.yml` | no | no | success | 2026-08-07T18:44:21Z | **GREEN** | None |
| `pdf-inspector-ingestion.yml` | no | no | success | 2026-08-02T18:16:02Z | **GREEN** | None |
| `pdlt-bootstrap-once.yml` | no | no | success | 2026-08-07T18:49:22Z | **GREEN** | None |
| `pdlt-daily-census.yml` | yes | yes | success | 2026-08-08T22:13:10Z | **GREEN** | None |
| `pdlt-discovery-once.yml` | yes | yes | failure | 2026-08-08T19:54:33Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES |
| `pdlt-maturation.yml` | yes | yes | success | 2026-08-08T22:51:27Z | **GREEN** | None |
| `pdlt-runtime-gate.yml` | no | no | success | 2026-08-07T19:30:48Z | **GREEN** | None |
| `pdlt-v1-1.yml` | no | no | success | 2026-08-07T18:49:22Z | **GREEN** | None |
| `remediation-maturation-gate.yml` | no | no | success | 2026-08-05T17:54:58Z | **GREEN** | None |
| `remediation-maturation.yml` | yes | yes | success | 2026-08-08T16:01:12Z | **GREEN** | None |
| `sequential-research-queue.yml` | yes | yes | success | 2026-08-08T07:23:39Z | **GREEN** | None |
| `specialist-architecture-gate.yml` | no | no | success | 2026-08-01T05:33:29Z | **GREEN** | None |
| `storage-health-gate.yml` | no | no | success | 2026-08-08T18:38:29Z | **GREEN** | None |
| `sunday-market-close-and-cfgi.yml` | yes | yes | failure | 2026-08-03T03:41:11Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES, SCHEDULE_STALE |
| `top100-breadth-owner-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `validate_m3_forward_ledger.yml` | no | no | none | none | **GREEN** | None |
| `weekly-api-calibration-shadow.yml` | yes | yes | failure | 2026-08-04T15:59:06Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES, SCHEDULE_STALE |
| `weekly-raw-calibration-bridge.yml` | yes | yes | success | 2026-08-02T22:37:43Z | **AMBER** | SCHEDULE_STALE |

## Blockers
- pdlt-discovery-once.yml:LATEST_RUN_FAILED
- pdlt-discovery-once.yml:REPEATED_CONSECUTIVE_FAILURES
- sunday-market-close-and-cfgi.yml:LATEST_RUN_FAILED
- sunday-market-close-and-cfgi.yml:REPEATED_CONSECUTIVE_FAILURES
- sunday-market-close-and-cfgi.yml:SCHEDULE_STALE
- weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED
- weekly-api-calibration-shadow.yml:REPEATED_CONSECUTIVE_FAILURES
- weekly-api-calibration-shadow.yml:SCHEDULE_STALE

## Warnings
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-full-profile-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-live-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:harness-redteam-p0-remediation-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:persistent-agent-runtime-readiness-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:t4-microstructure-live-readback.yml
- api-agent-gateway-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- automation-production-health-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-engine-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-wave1-2-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- daily-capture-architecture-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- master-monday-remaining-gaps.yml:NO_RUN_HISTORY
- operations-dashboard-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- weekly-raw-calibration-bridge.yml:SCHEDULE_STALE
