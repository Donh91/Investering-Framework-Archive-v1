# Operations Dashboard

Overall: **RED**
Generated: `2026-09-22T09:11:30.411100Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.226 |
| `openai_daily_director` | **GREEN** | FRESH | 8.95 |
| `weekly_output` | **GREEN** | FRESH | 15.254 |
| `automation_health` | **RED** | RED | 0.508 |
| `architecture_health` | **AMBER** | AMBER | 0.467 |
| `experiment_lifecycle` | **GREEN** | FRESH | 8.95 |
| `experiment_receipt_sync` | **RED** | STALE | 170.805 |
| `remediation_maturation` | **GREEN** | FRESH | 0.371 |

## AI and learning activity

- OpenAI receipts this month: **169**
- OpenAI cost this month: **$12.213747**
- Pending forecast candidates: **199**
- Experiment candidates: **373**
- Experiment dispatch requests: **10034**
- Codex-ready remediation tasks: **21**
- Needs-more-evidence items: **22**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['adaptive-decision-miss-validation.yml:LATEST_RUN_FAILED', 'adaptive-decision-miss-validation.yml:REPEATED_CONSECUTIVE_FAILURES', 'daily-settled-etf-calibration.yml:LATEST_RUN_FAILED', 'daily-settled-etf-calibration.yml:REPEATED_CONSECUTIVE_FAILURES', 'framework-learning-operations.yml:LATEST_RUN_FAILED', 'framework-learning-operations.yml:REPEATED_CONSECUTIVE_FAILURES', 'situation-room-shadow-bridge.yml:LATEST_RUN_FAILED', 'situation-room-shadow-bridge.yml:REPEATED_CONSECUTIVE_FAILURES', 'unified-experimental-lifecycle-adjudication.yml:LATEST_RUN_FAILED']
- **P0** `experiment_receipt_sync` - STALE
- **P1** `architecture_health` - ['OWNER_POPULATION_EMPTY', 'ETF_OWNER_STALE', 'EXPERIMENT_RECEIPT_SYNC_STALE']

Dashboard SHA-256: `da4797579e85a61929679a08b8200f58340f990990256af4e0f013260ec85623`
