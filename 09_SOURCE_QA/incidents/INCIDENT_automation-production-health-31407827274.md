# Automation Production Health
Status: **RED**
Generated: `2026-08-10T16:13:54.634425Z`
Workflows: 49 local / 54 registered
Scheduled: 18
Writers: 16
GREEN / AMBER / RED: 38 / 10 / 1

## Workflow matrix
| Workflow | Schedule | Writer | Last conclusion | Last run | Status | Findings |
|---|---:|---:|---|---|---|---|
| `api-agent-gateway-gate.yml` | no | no | success | 2026-08-10T10:56:48Z | **GREEN** | None |
| `automation-production-health-gate.yml` | no | no | success | 2026-08-10T15:33:07Z | **GREEN** | None |
| `automation-production-health.yml` | yes | yes | in_progress | 2026-08-10T16:13:39Z | **GREEN** | None |
| `backtest-engine-foundation.yml` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-readiness-contracts.yml` | no | no | success | 2026-07-30T18:08:16Z | **GREEN** | None |
| `backtest-wave1-2-foundation.yml` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-wave1-3-authority-lineage.yml` | no | no | success | 2026-07-28T16:15:15Z | **GREEN** | None |
| `backtest-wave1-4-prospective.yml` | yes | no | success | 2026-08-09T17:31:51Z | **GREEN** | None |
| `binance-spot-owner-manual.yml` | no | no | success | 2026-08-01T19:31:36Z | **GREEN** | None |
| `binance-usdm-owner-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `continuity-learning-gate.yml` | no | no | success | 2026-08-10T10:56:48Z | **GREEN** | None |
| `continuity-learning-maintenance.yml` | yes | yes | success | 2026-08-09T22:03:37Z | **GREEN** | None |
| `daily-capture-architecture-gate.yml` | no | no | success | 2026-08-10T10:45:31Z | **GREEN** | None |
| `daily-director-shadow.yml` | yes | yes | success | 2026-08-09T21:53:27Z | **GREEN** | None |
| `daily-raw-owner-capture.yml` | yes | yes | success | 2026-08-10T14:33:12Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `daily-settled-etf-calibration.yml` | yes | yes | success | 2026-08-10T10:46:18Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `data-architecture-gate.yml` | no | no | success | 2026-08-10T15:41:47Z | **GREEN** | None |
| `data-terminal-shadow-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `dataset-registry-gate.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `experiment-lifecycle-gate.yml` | no | no | success | 2026-08-10T15:41:49Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `fetch_btc_d_cmc_free.yml` | no | no | success | 2026-07-12T00:09:38Z | **GREEN** | None |
| `framework-learning-operations.yml` | yes | yes | success | 2026-08-10T03:19:23Z | **GREEN** | None |
| `full-architecture-1to7-gate.yml` | no | no | success | 2026-08-10T15:33:07Z | **GREEN** | None |
| `hourly-sequence-capture.yml` | yes | yes | success | 2026-08-10T10:50:17Z | **GREEN** | None |
| `legacy-knowledge-bootstrap-gate.yml` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `mar_wp04c4_gate.yml` | no | no | success | 2026-07-31T01:41:02Z | **GREEN** | None |
| `master-monday-preflight-gate.yml` | no | no | success | 2026-08-10T10:56:48Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `master-monday-remaining-gaps.yml` | yes | yes | success | 2026-08-10T10:59:00Z | **GREEN** | None |
| `okx-swap-owner-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `operations-dashboard-gate.yml` | no | no | success | 2026-08-05T15:35:53Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `operations-dashboard.yml` | yes | yes | success | 2026-08-10T05:36:55Z | **GREEN** | None |
| `owner-bound-daily-director-manual.yml` | no | no | success | 2026-08-10T10:56:48Z | **GREEN** | None |
| `pdf-inspector-ingestion.yml` | no | no | success | 2026-08-02T18:16:02Z | **GREEN** | None |
| `pdlt-bootstrap-once.yml` | no | no | skipped | 2026-08-10T15:36:07Z | **GREEN** | None |
| `pdlt-daily-census.yml` | yes | yes | success | 2026-08-09T22:14:47Z | **GREEN** | None |
| `pdlt-discovery-once.yml` | no | no | failure | 2026-08-09T19:58:23Z | **RED** | REPEATED_CONSECUTIVE_FAILURES |
| `pdlt-maturation.yml` | yes | yes | success | 2026-08-09T22:54:20Z | **GREEN** | None |
| `pdlt-runtime-gate.yml` | yes | no | success | 2026-08-10T15:33:07Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES, SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `pdlt-v1-1.yml` | no | no | success | 2026-08-10T15:36:09Z | **GREEN** | None |
| `remediation-maturation-gate.yml` | no | no | success | 2026-08-05T17:54:58Z | **GREEN** | None |
| `remediation-maturation.yml` | yes | yes | success | 2026-08-10T05:10:24Z | **GREEN** | None |
| `sequential-research-queue.yml` | yes | yes | success | 2026-08-10T08:09:46Z | **GREEN** | None |
| `specialist-architecture-gate.yml` | no | no | success | 2026-08-01T05:33:29Z | **GREEN** | None |
| `storage-health-gate.yml` | no | no | success | 2026-08-10T15:41:47Z | **GREEN** | None |
| `sunday-market-close-and-cfgi.yml` | yes | yes | success | 2026-08-10T02:23:55Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `top100-breadth-owner-manual.yml` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `validate_m3_forward_ledger.yml` | no | no | none | none | **GREEN** | None |
| `weekly-api-calibration-shadow.yml` | yes | yes | success | 2026-08-10T10:57:37Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `weekly-raw-calibration-bridge.yml` | yes | yes | success | 2026-08-10T02:39:34Z | **GREEN** | None |

## Blockers
- pdlt-discovery-once.yml:REPEATED_CONSECUTIVE_FAILURES

## Warnings
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-full-profile-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-live-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:harness-redteam-p0-remediation-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:persistent-agent-runtime-readiness-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:t4-microstructure-live-readback.yml
- backtest-engine-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-wave1-2-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- daily-raw-owner-capture.yml:RECOVERING_AFTER_RECENT_FAILURES
- daily-settled-etf-calibration.yml:RECOVERING_AFTER_RECENT_FAILURES
- experiment-lifecycle-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- master-monday-preflight-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- operations-dashboard-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- pdlt-runtime-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- pdlt-runtime-gate.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- sunday-market-close-and-cfgi.yml:RECOVERING_AFTER_RECENT_FAILURES
- weekly-api-calibration-shadow.yml:RECOVERING_AFTER_RECENT_FAILURES
