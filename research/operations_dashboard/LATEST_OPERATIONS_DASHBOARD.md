# Operations Dashboard

Overall: **RED**
Generated: `2026-09-22T19:34:48.831987Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.652 |
| `openai_daily_director` | **GREEN** | FRESH | 1.813 |
| `weekly_output` | **GREEN** | FRESH | 25.642 |
| `automation_health` | **RED** | RED | 0.566 |
| `architecture_health` | **AMBER** | AMBER | 0.53 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.813 |
| `experiment_receipt_sync` | **RED** | STALE | 181.193 |
| `remediation_maturation` | **GREEN** | FRESH | 0.44 |

## AI and learning activity

- OpenAI receipts this month: **172**
- OpenAI cost this month: **$12.241440**
- Pending forecast candidates: **199**
- Experiment candidates: **379**
- Experiment dispatch requests: **10528**
- Codex-ready remediation tasks: **23**
- Needs-more-evidence items: **24**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['adaptive-decision-miss-validation.yml:LATEST_RUN_FAILED', 'adaptive-decision-miss-validation.yml:REPEATED_CONSECUTIVE_FAILURES', 'daily-settled-etf-calibration.yml:LATEST_RUN_FAILED', 'daily-settled-etf-calibration.yml:REPEATED_CONSECUTIVE_FAILURES', 'framework-learning-operations.yml:LATEST_RUN_FAILED', 'framework-learning-operations.yml:REPEATED_CONSECUTIVE_FAILURES', 'situation-room-shadow-bridge.yml:LATEST_RUN_FAILED', 'situation-room-shadow-bridge.yml:REPEATED_CONSECUTIVE_FAILURES', 'unified-experimental-lifecycle-adjudication.yml:LATEST_RUN_FAILED']
- **P0** `experiment_receipt_sync` - STALE
- **P1** `architecture_health` - ['OWNER_POPULATION_EMPTY', 'ETF_OWNER_STALE', 'EXPERIMENT_RECEIPT_SYNC_STALE']

Dashboard SHA-256: `f5dd9d014c4bf2a0c69447029e304f3bcd532d7e5e5880811a6ac3f3286d55ff`
