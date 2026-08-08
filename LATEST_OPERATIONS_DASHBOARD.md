# Operations Dashboard

Overall: **RED**
Generated: `2026-08-08T16:31:58.067849Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 18.671 |
| `openai_daily_director` | **RED** | STALE | 115.614 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **RED** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 13.509 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.509 |
| `remediation_maturation` | **GREEN** | FRESH | 0.511 |

## AI and learning activity

- OpenAI receipts this month: **7**
- OpenAI cost this month: **$0.101493**
- Pending forecast candidates: **46**
- Experiment candidates: **34**
- Experiment dispatch requests: **44**
- Codex-ready remediation tasks: **8**
- Needs-more-evidence items: **7**

## Incidents

Open incident references: **16**

## Required actions

- **P0** `architecture_health` - ['NO_WEEKLY_API_OUTPUT_YET', 'ETF_OWNER_STALE']
- **P0** `automation_health` - ['pdlt-discovery-once.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:SCHEDULE_STALE', 'weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED', 'weekly-api-calibration-shadow.yml:REPEATED_CONSECUTIVE_FAILURES', 'weekly-api-calibration-shadow.yml:SCHEDULE_STALE']
- **P0** `daily_capture` - STALE
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `0ae283f5b46e98fad8ec8dcae014ee1715e530b608f0f9f6f39c9776dc40d63b`
