# Operations Dashboard

Overall: **RED**
Generated: `2026-08-09T05:10:20.005642Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 7.488 |
| `openai_daily_director` | **GREEN** | FRESH | 7.328 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **RED** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.011 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.011 |
| `remediation_maturation` | **GREEN** | FRESH | 0.323 |

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
- **P0** `automation_health` - ['pdlt-discovery-once.yml:LATEST_RUN_FAILED', 'pdlt-discovery-once.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:SCHEDULE_STALE', 'weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED', 'weekly-api-calibration-shadow.yml:REPEATED_CONSECUTIVE_FAILURES', 'weekly-api-calibration-shadow.yml:SCHEDULE_STALE']
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `96ce653b255cfc0f5b256453c97c262066e97f7c95d5954d5a7ed971b514f2e6`
