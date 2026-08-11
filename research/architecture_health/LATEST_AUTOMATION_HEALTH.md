# Automation Production Health
Status: **AMBER**
Generated: `2026-08-11T04:46:05.662991Z`
Workflows: 49 local / 54 registered
Scheduled: 18
Writers: 16
GREEN / AMBER / RED: 36 / 13 / 0

## Workflow matrix
| Workflow | Lifecycle | Schedule | Writer | Last conclusion | Last run | Status | Findings |
|---|---|---:|---:|---|---|---|---|
| `api-agent-gateway-gate.yml` | `ACTIVE` | no | no | success | 2026-08-10T10:56:48Z | **GREEN** | None |
| `automation-production-health-gate.yml` | `ACTIVE` | no | no | success | 2026-08-10T20:13:22Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `automation-production-health.yml` | `ACTIVE` | yes | yes | in_progress | 2026-08-11T04:45:59Z | **GREEN** | None |
| `backtest-engine-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-readiness-contracts.yml` | `ACTIVE` | no | no | success | 2026-07-30T18:08:16Z | **GREEN** | None |
| `backtest-wave1-2-foundation.yml` | `ACTIVE` | no | no | success | 2026-08-09T17:25:05Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `backtest-wave1-3-authority-lineage.yml` | `ACTIVE` | no | no | success | 2026-07-28T16:15:15Z | **GREEN** | None |
| `backtest-wave1-4-prospective.yml` | `ACTIVE` | yes | no | success | 2026-08-10T16:26:03Z | **GREEN** | None |
| `binance-spot-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-08-01T19:31:36Z | **GREEN** | None |
| `binance-usdm-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `continuity-learning-gate.yml` | `ACTIVE` | no | no | success | 2026-08-10T20:13:22Z | **GREEN** | None |
| `continuity-learning-maintenance.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T22:19:25Z | **GREEN** | None |
| `daily-capture-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-10T20:13:22Z | **GREEN** | None |
| `daily-director-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T22:01:50Z | **GREEN** | None |
| `daily-raw-owner-capture.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T21:53:34Z | **GREEN** | None |
| `daily-settled-etf-calibration.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T10:46:18Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `data-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-10T20:13:22Z | **GREEN** | None |
| `data-terminal-shadow-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `dataset-registry-gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `experiment-lifecycle-gate.yml` | `ACTIVE` | no | no | success | 2026-08-10T15:41:49Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `fetch_btc_d_cmc_free.yml` | `ACTIVE` | no | no | success | 2026-07-12T00:09:38Z | **GREEN** | None |
| `framework-learning-operations.yml` | `ACTIVE` | yes | yes | success | 2026-08-11T03:12:04Z | **GREEN** | None |
| `full-architecture-1to7-gate.yml` | `ACTIVE` | no | no | success | 2026-08-10T20:13:22Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `hourly-sequence-capture.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T22:22:25Z | **GREEN** | None |
| `legacy-knowledge-bootstrap-gate.yml` | `ACTIVE` | no | no | success | 2026-08-04T19:08:35Z | **GREEN** | None |
| `mar_wp04c4_gate.yml` | `ACTIVE` | no | no | success | 2026-07-31T01:41:02Z | **GREEN** | None |
| `master-monday-preflight-gate.yml` | `ACTIVE` | no | no | success | 2026-08-10T10:56:48Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `master-monday-remaining-gaps.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T10:59:00Z | **GREEN** | None |
| `okx-swap-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `operations-dashboard-gate.yml` | `ACTIVE` | no | no | success | 2026-08-05T15:35:53Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `operations-dashboard.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T16:52:54Z | **GREEN** | None |
| `owner-bound-daily-director-manual.yml` | `ACTIVE` | no | no | success | 2026-08-10T10:56:48Z | **GREEN** | None |
| `pdf-inspector-ingestion.yml` | `ACTIVE` | no | no | success | 2026-08-02T18:16:02Z | **GREEN** | None |
| `pdlt-bootstrap-once.yml` | `ACTIVE` | no | no | skipped | 2026-08-10T15:36:07Z | **GREEN** | None |
| `pdlt-daily-census.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T22:22:11Z | **GREEN** | None |
| `pdlt-discovery-once.yml` | `EXPECTED_BLOCK` | no | no | failure | 2026-08-09T19:58:23Z | **AMBER** | EXPECTED_BLOCK |
| `pdlt-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T23:00:06Z | **GREEN** | None |
| `pdlt-runtime-gate.yml` | `ACTIVE` | yes | no | success | 2026-08-10T20:05:49Z | **AMBER** | SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE |
| `pdlt-v1-1.yml` | `ACTIVE` | no | no | success | 2026-08-10T15:36:09Z | **GREEN** | None |
| `remediation-maturation-gate.yml` | `ACTIVE` | no | no | success | 2026-08-10T20:05:49Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `remediation-maturation.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T16:29:28Z | **GREEN** | None |
| `sequential-research-queue.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T08:09:46Z | **GREEN** | None |
| `specialist-architecture-gate.yml` | `ACTIVE` | no | no | success | 2026-08-01T05:33:29Z | **GREEN** | None |
| `storage-health-gate.yml` | `ACTIVE` | no | no | success | 2026-08-10T20:13:22Z | **GREEN** | None |
| `sunday-market-close-and-cfgi.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T02:23:55Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `top100-breadth-owner-manual.yml` | `ACTIVE` | no | no | success | 2026-07-31T20:51:59Z | **GREEN** | None |
| `validate_m3_forward_ledger.yml` | `ACTIVE` | no | no | none | none | **GREEN** | None |
| `weekly-api-calibration-shadow.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T10:57:37Z | **AMBER** | RECOVERING_AFTER_RECENT_FAILURES |
| `weekly-raw-calibration-bridge.yml` | `ACTIVE` | yes | yes | success | 2026-08-10T02:39:34Z | **GREEN** | None |

## Blockers
- None

## Warnings
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-full-profile-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:cfgi-live-smoke-temp.yml
- REGISTERED_WITHOUT_LOCAL_FILE:harness-redteam-p0-remediation-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:persistent-agent-runtime-readiness-gate.yml
- REGISTERED_WITHOUT_LOCAL_FILE:t4-microstructure-live-readback.yml
- automation-production-health-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-engine-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- backtest-wave1-2-foundation.yml:RECOVERING_AFTER_RECENT_FAILURES
- daily-settled-etf-calibration.yml:RECOVERING_AFTER_RECENT_FAILURES
- experiment-lifecycle-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- full-architecture-1to7-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- master-monday-preflight-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- operations-dashboard-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- pdlt-discovery-once.yml:EXPECTED_BLOCK
- pdlt-runtime-gate.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE
- remediation-maturation-gate.yml:RECOVERING_AFTER_RECENT_FAILURES
- sunday-market-close-and-cfgi.yml:RECOVERING_AFTER_RECENT_FAILURES
- weekly-api-calibration-shadow.yml:RECOVERING_AFTER_RECENT_FAILURES
