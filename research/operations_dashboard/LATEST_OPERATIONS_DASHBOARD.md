# Operations Dashboard

Overall: **RED**
Generated: `2026-08-05T17:30:11.092898Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 19.169 |
| `openai_daily_director` | **RED** | STALE | 44.584 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **RED** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 6.77 |
| `experiment_receipt_sync` | **AMBER** | NO_EXPERIMENT_RECEIPT_SYNC_YET | - |
| `remediation_maturation` | **GREEN** | FRESH | 0.361 |

## AI and learning activity

- OpenAI receipts this month: **4**
- OpenAI cost this month: **$0.051258**
- Pending forecast candidates: **16**
- Experiment candidates: **0**
- Experiment dispatch requests: **0**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **8**

## Incidents

Open incident references: **11**

## Required actions

- **P0** `architecture_health` - ['NO_WEEKLY_API_OUTPUT_YET', 'NO_REMEDIATION_QUEUE_YET']
- **P0** `automation_health` - ['automation-production-health.yml:REPEATED_CONSECUTIVE_FAILURES', 'daily-director-shadow.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:SCHEDULE_STALE', 'weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED', 'weekly-api-calibration-shadow.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `daily_capture` - STALE
- **P0** `openai_daily_director` - STALE
- **P1** `experiment_receipt_sync` - NO_EXPERIMENT_RECEIPT_SYNC_YET
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `6378c55967b07a0c45f6c6797e0d94ca28027128ca4ffb93ae3cef3ccb496173`
