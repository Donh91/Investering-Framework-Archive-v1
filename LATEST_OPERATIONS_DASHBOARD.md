# Operations Dashboard

Overall: **RED**
Generated: `2026-09-01T09:17:23.122246Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.127 |
| `openai_daily_director` | **RED** | STALE | 113.849 |
| `weekly_output` | **GREEN** | FRESH | 27.235 |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **AMBER** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.924 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.925 |
| `remediation_maturation` | **GREEN** | FRESH | 0.37 |

## AI and learning activity

- OpenAI receipts this month: **3**
- OpenAI cost this month: **$0.131483**
- Pending forecast candidates: **138**
- Experiment candidates: **153**
- Experiment dispatch requests: **801**
- Codex-ready remediation tasks: **25**
- Needs-more-evidence items: **18**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['buildwithclaude-shadow-round1.yml:REPEATED_CONSECUTIVE_FAILURES', 'cycle-navigator-weekly-publication.yml:LATEST_RUN_FAILED', 'daily-director-shadow.yml:LATEST_RUN_FAILED', 'daily-director-shadow.yml:SCHEDULE_STALE', 'pdlt-daily-census.yml:LATEST_RUN_FAILED']
- **P0** `openai_daily_director` - STALE
- **P1** `architecture_health` - ['DAILY_DIRECTOR_STALE']

Dashboard SHA-256: `23bdad2b35c11bb917ab6c3e79fbca8ed24f634f2c8fd675d2bbef2919863c2e`
