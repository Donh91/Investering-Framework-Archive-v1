# Operations Dashboard

Overall: **RED**
Generated: `2026-08-04T17:48:21.733253Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 19.544 |
| `openai_daily_director` | **AMBER** | DELAYED | 20.887 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **RED** | - | - |

## AI activity

- OpenAI receipts this month: **4**
- OpenAI cost this month: **$0.051258**
- Pending forecast candidates: **7**
- Codex attribution: **UNKNOWN**

## Incidents

Open incident references: **8**

## Required actions

- **P0** `architecture_health` - ['NO_WEEKLY_API_OUTPUT_YET']
- **P0** `automation_health` - ['automation-production-health.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:SCHEDULE_STALE', 'weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED', 'weekly-api-calibration-shadow.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `daily_capture` - STALE
- **P1** `openai_daily_director` - DELAYED
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `6f7200a4902e2b260e12d1cd31547caffa4f267725783f917b10552ca3302cf0`
