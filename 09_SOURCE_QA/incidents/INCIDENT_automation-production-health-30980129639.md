# Automation Production Health
Status: **RED**
Generated: `2026-08-05T06:04:50.243163Z`
Workflows: 37 local / 40 registered
Scheduled: 11
Writers: 10
GREEN / AMBER / RED: 25 / 8 / 4

## Workflow matrix
| Workflow | Schedule | Writer | Last conclusion | Last run | Status | Findings |
|---|---:|---:|---|---|---|---|
| `api-agent-gateway-gate.yml` | no | no | success | 2026-08-04T16:16:37Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `automation-production-health-gate.yml` | no | no | success | 2026-08-04T16:16:38Z | **GREEN** | None |
| `automation-production-health.yml` | yes | yes | in_progress | 2026-08-05T06:04:34Z | **RED** | REPEATED_CONSECUTIVE_FAILURES |
| `backtest-engine-foundation.yml` | no | no | success | 2026-07-31T01:15:06Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-readiness-contracts.yml` | no | no | success | 2026-07-30T18:08:16Z | **GREEN** | None |
| `backtest-wave1-2-foundation.yml` | no | no | success | 2026-07-31T01:15:06Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-wave1-3-authority-lineage.yml` | no | no | success | 2026-07-28T16:15:15Z | **GREEN** | None |
| `backtest-wave1-4-prospective.yml` | yes | no | success | 2026-08-04T19:09:32Z | **AMBER** | ARTIFACT_RETENTION_UNBOUNDED, SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `binance-spot-owner-manual.yml` | no | no | success | 2026-08-01T19:31:36Z | **GREEN** | None |
| `binance-usdm-owner-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `continuity-learning-gate.yml` | no | no | success | 2026-08-04T16:16:37Z | **GREEN** | None |
| `continuity-learning-maintenance.yml` | yes | yes | success | 2026-08-04T22:43:32Z | **GREEN** | None |
| `daily-capture-architecture-gate.yml` | no | no | success | 2026-08-04T16:16:38Z | **GREEN** | None |
| `daily-director-shadow.yml` | yes | yes | failure | 2026-08-04T22:31:28Z | **RED** | LATEST_RUN_FAILED |
| `daily-raw-owner-capture.yml` | yes | yes | success | 2026-08-04T22:19:44Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `data-architecture-gate.yml` | no | no | success | 2026-08-04T19:08:37Z | **GREEN** | None |
| `data-terminal-shadow-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `dataset-registry-gate.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `fetch_btc_d_cmc_free.yml` | no | no | success | 2026-07-12T00:09:38Z | **GREEN** | None |
| `framework-learning-operations.yml` | yes | yes | success | 2026-08-05T04:31:34Z | **GREEN** | None |
| `full-architecture-1to7-gate.yml` | no | no | success | 2026-08-04T16:16:37Z | **GREEN** | None |
| `legacy-knowledge-bootstrap-gate.yml` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `mar_wp04c4_gate.yml` | no | no | success | 2026-07-31T01:41:02Z | **GREEN** | None |
| `master-monday-preflight-gate.yml` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `master-monday-remaining-gaps.yml` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `okx-swap-owner-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `operations-dashboard-gate.yml` | no | no | success | 2026-08-04T13:23:24Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `operations-dashboard.yml` | yes | yes | success | 2026-08-04T17:48:06Z | **GREEN** | None |
| `owner-bound-daily-director-manual.yml` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `pdf-inspector-ingestion.yml` | no | no | success | 2026-08-02T18:16:02Z | **GREEN** | None |
| `specialist-architecture-gate.yml` | no | no | success | 2026-08-01T05:33:29Z | **GREEN** | None |
| `storage-health-gate.yml` | no | no | success | 2026-08-04T19:08:36Z | **GREEN** | None |
| `sunday-market-close-and-cfgi.yml` | yes | yes | failure | 2026-08-03T03:41:11Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES, SCHEDULE_STALE |
| `top100-breadth-owner-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `validate_m3_forward_ledger.yml` | no | no | none | none | **GREEN** | None |
| `weekly-api-calibration-shadow.yml` | yes | yes | failure | 2026-08-04T15:59:06Z | **RED** | LATEST_RUN_FAILED, REPEATED_CONSECUTIVE_FAILURES |
| `weekly-raw-calibration-bridge.yml` | yes | yes | success | 2026-08-02T22:37:43Z | **AMBER** | SCHEDULE_STALE |

## Blockers
- automation-production-health.yml:REPEATED_CONSECUTIVE_FAILURES
- daily-director-shadow.yml:LATEST_RUN_FAILED
- sunday-market-close-and-cfgi.yml:LATEST_RUN_FAILED
- sunday-market-close-and-cfgi.yml:REPEATED_CONSECUTIVE_FAILURES
- sunday-market-close-and-cfgi.yml:SCHEDULE_STALE
- weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED
- weekly-api-calibration-shadow.yml:REPEATED_CONSECUTIVE_FAILURES

## Warnings
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-full-profile-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-live-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:t4-microstructure-live-readback.yml
- api-agent-gateway-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-engine-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-wave1-2-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-wave1-4-prospective.yml:ARTIFACT_RETENTION_UNBOUNDED
- backtest-wave1-4-prospective.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- daily-raw-owner-capture.yml:RECOVERING_AFTER_RECENT_FAILURES
- master-monday-remaining-gaps.yml:NO_RUN_HISTORY
- operations-dashboard-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- weekly-raw-calibration-bridge.yml:SCHEDULE_STALE
