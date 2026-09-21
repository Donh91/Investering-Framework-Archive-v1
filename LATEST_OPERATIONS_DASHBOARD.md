# Operations Dashboard

Overall: **RED**
Generated: `2026-09-21T20:16:27.625260Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.034 |
| `openai_daily_director` | **GREEN** | FRESH | 1.364 |
| `weekly_output` | **GREEN** | FRESH | 2.336 |
| `automation_health` | **RED** | RED | 0.208 |
| `architecture_health` | **AMBER** | AMBER | 0.172 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.364 |
| `experiment_receipt_sync` | **RED** | STALE | 157.887 |
| `remediation_maturation` | **GREEN** | FRESH | 0.157 |

## AI and learning activity

- OpenAI receipts this month: **168**
- OpenAI cost this month: **$12.204600**
- Pending forecast candidates: **197**
- Experiment candidates: **371**
- Experiment dispatch requests: **9872**
- Codex-ready remediation tasks: **23**
- Needs-more-evidence items: **20**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['adaptive-decision-miss-validation.yml:LATEST_RUN_FAILED', 'adaptive-decision-miss-validation.yml:REPEATED_CONSECUTIVE_FAILURES', 'daily-settled-etf-calibration.yml:LATEST_RUN_FAILED', 'daily-settled-etf-calibration.yml:REPEATED_CONSECUTIVE_FAILURES', 'framework-learning-operations.yml:LATEST_RUN_FAILED', 'framework-learning-operations.yml:REPEATED_CONSECUTIVE_FAILURES', 'operations-dashboard.yml:LATEST_RUN_FAILED', 'operations-dashboard.yml:REPEATED_CONSECUTIVE_FAILURES', 'situation-room-shadow-bridge.yml:LATEST_RUN_FAILED', 'situation-room-shadow-bridge.yml:REPEATED_CONSECUTIVE_FAILURES', 'unified-experimental-lifecycle-adjudication.yml:LATEST_RUN_FAILED']
- **P0** `experiment_receipt_sync` - STALE
- **P1** `architecture_health` - ['OWNER_POPULATION_EMPTY', 'ETF_OWNER_STALE', 'EXPERIMENT_RECEIPT_SYNC_STALE']

Dashboard SHA-256: `362bb61315c01f1aeb670bb2743017ff1258e0b0a9f246f45d853014a9e344ed`
