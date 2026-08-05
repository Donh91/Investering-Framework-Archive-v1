# Operations Dashboard

Overall: **RED**
Generated: `2026-08-05T06:32:34.050165Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **AMBER** | DELAYED | 8.209 |
| `openai_daily_director` | **RED** | STALE | 33.624 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **RED** | - | - |

## AI activity

- OpenAI receipts this month: **4**
- OpenAI cost this month: **$0.051258**
- Pending forecast candidates: **16**
- Codex attribution: **UNKNOWN**

## Incidents

Open incident references: **11**

## Required actions

- **P0** `architecture_health` - ['NO_WEEKLY_API_OUTPUT_YET']
- **P0** `automation_health` - ['automation-production-health.yml:REPEATED_CONSECUTIVE_FAILURES', 'daily-director-shadow.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:SCHEDULE_STALE', 'weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED', 'weekly-api-calibration-shadow.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `openai_daily_director` - STALE
- **P1** `daily_capture` - DELAYED
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `2559559306e50a7cf1919a994e5ef16c1805acffd9181a15714142490d1f74a4`
