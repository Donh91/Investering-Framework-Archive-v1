# Operations Dashboard

Overall: **RED**
Generated: `2026-09-23T09:11:54.467390Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.429 |
| `openai_daily_director` | **GREEN** | FRESH | 9.451 |
| `weekly_output` | **GREEN** | FRESH | 39.261 |
| `automation_health` | **RED** | RED | 0.478 |
| `architecture_health` | **AMBER** | AMBER | 0.449 |
| `experiment_lifecycle` | **GREEN** | FRESH | 9.451 |
| `experiment_receipt_sync` | **RED** | STALE | 194.812 |
| `remediation_maturation` | **GREEN** | FRESH | 0.352 |

## AI and learning activity

- OpenAI receipts this month: **174**
- OpenAI cost this month: **$12.287804**
- Pending forecast candidates: **201**
- Experiment candidates: **380**
- Experiment dispatch requests: **10693**
- Codex-ready remediation tasks: **22**
- Needs-more-evidence items: **15**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['adaptive-decision-miss-validation.yml:LATEST_RUN_FAILED', 'adaptive-decision-miss-validation.yml:REPEATED_CONSECUTIVE_FAILURES', 'daily-settled-etf-calibration.yml:LATEST_RUN_FAILED', 'daily-settled-etf-calibration.yml:REPEATED_CONSECUTIVE_FAILURES', 'framework-learning-operations.yml:LATEST_RUN_FAILED', 'framework-learning-operations.yml:REPEATED_CONSECUTIVE_FAILURES', 'situation-room-shadow-bridge.yml:LATEST_RUN_FAILED', 'situation-room-shadow-bridge.yml:REPEATED_CONSECUTIVE_FAILURES', 'unified-experimental-lifecycle-adjudication.yml:LATEST_RUN_FAILED']
- **P0** `experiment_receipt_sync` - STALE
- **P1** `architecture_health` - ['OWNER_COVERAGE_DEGRADED', 'ETF_OWNER_STALE', 'EXPERIMENT_RECEIPT_SYNC_STALE']

Dashboard SHA-256: `68f843d4e60b0ee4451c2b4f58cd09b1f7379750ea40c14b3597b04c34d84baf`
