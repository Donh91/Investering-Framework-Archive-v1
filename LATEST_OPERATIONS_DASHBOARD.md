# Operations Dashboard

Overall: **RED**
Generated: `2026-08-10T05:37:06.780257Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 7.884 |
| `openai_daily_director` | **GREEN** | FRESH | 7.722 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **RED** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.291 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.291 |
| `remediation_maturation` | **GREEN** | FRESH | 0.444 |

## AI and learning activity

- OpenAI receipts this month: **9**
- OpenAI cost this month: **$0.135128**
- Pending forecast candidates: **90**
- Experiment candidates: **56**
- Experiment dispatch requests: **94**
- Codex-ready remediation tasks: **5**
- Needs-more-evidence items: **8**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `architecture_health` - ['NO_WEEKLY_API_OUTPUT_YET', 'ETF_OWNER_STALE']
- **P0** `automation_health` - ['pdlt-discovery-once.yml:LATEST_RUN_FAILED', 'pdlt-discovery-once.yml:REPEATED_CONSECUTIVE_FAILURES', 'weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED', 'weekly-api-calibration-shadow.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `945682b4748b5fd3f5d6ef6a30164080715f917e26d148ab2f2ca14612c5e81a`
