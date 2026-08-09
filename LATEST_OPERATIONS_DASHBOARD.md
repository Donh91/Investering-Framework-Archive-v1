# Operations Dashboard

Overall: **RED**
Generated: `2026-08-09T16:34:20.042193Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 18.888 |
| `openai_daily_director` | **AMBER** | DELAYED | 18.728 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **RED** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 13.411 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.411 |
| `remediation_maturation` | **GREEN** | FRESH | 0.529 |

## AI and learning activity

- OpenAI receipts this month: **8**
- OpenAI cost this month: **$0.118514**
- Pending forecast candidates: **67**
- Experiment candidates: **40**
- Experiment dispatch requests: **65**
- Codex-ready remediation tasks: **10**
- Needs-more-evidence items: **6**

## Incidents

Open incident references: **19**

## Required actions

- **P0** `architecture_health` - ['NO_WEEKLY_API_OUTPUT_YET', 'ETF_OWNER_STALE']
- **P0** `automation_health` - ['daily-raw-owner-capture.yml:LATEST_RUN_FAILED', 'pdlt-discovery-once.yml:LATEST_RUN_FAILED', 'pdlt-discovery-once.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:SCHEDULE_STALE', 'weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED', 'weekly-api-calibration-shadow.yml:REPEATED_CONSECUTIVE_FAILURES', 'weekly-api-calibration-shadow.yml:SCHEDULE_STALE']
- **P0** `daily_capture` - STALE
- **P1** `openai_daily_director` - DELAYED
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `ed46b4819fe786fb70d67dfd31d77f750c545a97944399945034fb2bba0c8175`
