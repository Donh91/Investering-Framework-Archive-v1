# Operations Dashboard

Overall: **RED**
Generated: `2026-08-08T05:02:00.767228Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 7.171 |
| `openai_daily_director` | **RED** | STALE | 104.115 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **RED** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.01 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.01 |
| `remediation_maturation` | **GREEN** | FRESH | 0.361 |

## AI and learning activity

- OpenAI receipts this month: **7**
- OpenAI cost this month: **$0.101493**
- Pending forecast candidates: **46**
- Experiment candidates: **34**
- Experiment dispatch requests: **44**
- Codex-ready remediation tasks: **8**
- Needs-more-evidence items: **8**

## Incidents

Open incident references: **16**

## Required actions

- **P0** `architecture_health` - ['NO_WEEKLY_API_OUTPUT_YET', 'ETF_OWNER_STALE']
- **P0** `automation_health` - ['pdlt-discovery-once.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:SCHEDULE_STALE', 'weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED', 'weekly-api-calibration-shadow.yml:REPEATED_CONSECUTIVE_FAILURES', 'weekly-api-calibration-shadow.yml:SCHEDULE_STALE']
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `12fbd20d38e7bb21f29fa413b4b4d0f6156a015a2b0078a36e6fb2a5b02a9b41`
