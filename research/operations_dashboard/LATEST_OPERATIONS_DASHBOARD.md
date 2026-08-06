# Operations Dashboard

Overall: **RED**
Generated: `2026-08-06T06:35:37.696557Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **AMBER** | DELAYED | 8.297 |
| `openai_daily_director` | **RED** | STALE | 57.675 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **RED** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.049 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.049 |
| `remediation_maturation` | **GREEN** | FRESH | 0.316 |

## AI and learning activity

- OpenAI receipts this month: **5**
- OpenAI cost this month: **$0.067911**
- Pending forecast candidates: **28**
- Experiment candidates: **17**
- Experiment dispatch requests: **17**
- Codex-ready remediation tasks: **9**
- Needs-more-evidence items: **4**

## Incidents

Open incident references: **13**

## Required actions

- **P0** `architecture_health` - ['NO_WEEKLY_API_OUTPUT_YET']
- **P0** `automation_health` - ['automation-production-health.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:SCHEDULE_STALE', 'weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED', 'weekly-api-calibration-shadow.yml:REPEATED_CONSECUTIVE_FAILURES', 'weekly-api-calibration-shadow.yml:SCHEDULE_STALE']
- **P0** `openai_daily_director` - STALE
- **P1** `daily_capture` - DELAYED
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `f527615e01e87c9cd3519bd7384de0b9f8db39d5cf14e76341dc940d6087593e`
