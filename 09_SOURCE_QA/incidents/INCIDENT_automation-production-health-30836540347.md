# Automation Production Health
Status: **RED**
Generated: `2026-08-03T17:23:44.594695Z`
Workflows: 34 local / 37 registered
Scheduled: 10
Writers: 9
GREEN / AMBER / RED: 25 / 3 / 6

## Workflow matrix
| Workflow | Schedule | Writer | Last conclusion | Last run | Status | Findings |
|---|---:|---:|---|---|---|---|
| `api-agent-gateway-gate.yml` | no | no | success | 2026-08-03T12:21:36Z | **RED** | REPEATED_RECENT_FAILURES |
| `automation-production-health-gate.yml` | no | no | success | 2026-08-03T15:24:42Z | **GREEN** | None |
| `automation-production-health.yml` | yes | yes | in_progress | 2026-08-03T17:23:37Z | **GREEN** | None |
| `backtest-engine-foundation.yml` | no | no | success | 2026-07-31T01:15:06Z | **RED** | REPEATED_RECENT_FAILURES |
| `backtest-readiness-contracts.yml` | no | no | success | 2026-07-30T18:08:16Z | **GREEN** | None |
| `backtest-wave1-2-foundation.yml` | no | no | success | 2026-07-31T01:15:06Z | **RED** | REPEATED_RECENT_FAILURES |
| `backtest-wave1-3-authority-lineage.yml` | no | no | success | 2026-07-28T16:15:15Z | **GREEN** | None |
| `backtest-wave1-4-prospective.yml` | yes | no | success | 2026-08-02T18:32:17Z | **AMBER** | ARTIFACT_RETENTION_UNBOUNDED, SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `binance-spot-owner-manual.yml` | no | no | success | 2026-08-01T19:31:36Z | **GREEN** | None |
| `binance-usdm-owner-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `continuity-learning-gate.yml` | no | no | success | 2026-08-03T12:29:08Z | **GREEN** | None |
| `continuity-learning-maintenance.yml` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `daily-capture-architecture-gate.yml` | no | no | success | 2026-08-03T12:29:08Z | **GREEN** | None |
| `daily-director-shadow.yml` | yes | yes | success | 2026-08-02T22:13:54Z | **GREEN** | None |
| `daily-raw-owner-capture.yml` | yes | yes | failure | 2026-08-03T15:57:39Z | **RED** | LATEST_RUN_FAILED |
| `data-architecture-gate.yml` | no | no | success | 2026-08-03T15:24:42Z | **GREEN** | None |
| `data-terminal-shadow-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `dataset-registry-gate.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `fetch_btc_d_cmc_free.yml` | no | no | success | 2026-07-12T00:09:38Z | **GREEN** | None |
| `framework-learning-operations.yml` | yes | yes | success | 2026-08-03T04:51:00Z | **GREEN** | None |
| `full-architecture-1to7-gate.yml` | no | no | success | 2026-08-03T15:24:42Z | **GREEN** | None |
| `mar_wp04c4_gate.yml` | no | no | success | 2026-07-31T01:41:02Z | **GREEN** | None |
| `master-monday-preflight-gate.yml` | no | no | success | 2026-08-03T12:21:37Z | **GREEN** | None |
| `master-monday-remaining-gaps.yml` | yes | yes | none | none | **AMBER** | NO_RUN_HISTORY |
| `okx-swap-owner-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `owner-bound-daily-director-manual.yml` | no | no | success | 2026-08-03T12:29:08Z | **GREEN** | None |
| `pdf-inspector-ingestion.yml` | no | no | success | 2026-08-02T18:16:02Z | **GREEN** | None |
| `specialist-architecture-gate.yml` | no | no | success | 2026-08-01T05:33:29Z | **GREEN** | None |
| `storage-health-gate.yml` | no | no | success | 2026-08-03T15:24:42Z | **GREEN** | None |
| `sunday-market-close-and-cfgi.yml` | yes | yes | failure | 2026-08-03T03:41:11Z | **RED** | LATEST_RUN_FAILED, REPEATED_RECENT_FAILURES |
| `top100-breadth-owner-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `validate_m3_forward_ledger.yml` | no | no | none | none | **GREEN** | None |
| `weekly-api-calibration-shadow.yml` | yes | yes | failure | 2026-08-03T15:43:51Z | **RED** | LATEST_RUN_FAILED, REPEATED_RECENT_FAILURES |
| `weekly-raw-calibration-bridge.yml` | yes | yes | success | 2026-08-02T22:37:43Z | **GREEN** | None |

## Blockers
- api-agent-gateway-gate.yml:REPEATED_RECENT_FAILURES
- backtest-engine-foundation.yml:REPEATED_RECENT_FAILURES
- backtest-wave1-2-foundation.yml:REPEATED_RECENT_FAILURES
- daily-raw-owner-capture.yml:LATEST_RUN_FAILED
- sunday-market-close-and-cfgi.yml:LATEST_RUN_FAILED
- sunday-market-close-and-cfgi.yml:REPEATED_RECENT_FAILURES
- weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED
- weekly-api-calibration-shadow.yml:REPEATED_RECENT_FAILURES

## Warnings
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-full-profile-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-live-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:t4-microstructure-live-readback.yml
- backtest-wave1-4-prospective.yml:ARTIFACT_RETENTION_UNBOUNDED
- backtest-wave1-4-prospective.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- continuity-learning-maintenance.yml:NO_RUN_HISTORY
- master-monday-remaining-gaps.yml:NO_RUN_HISTORY
