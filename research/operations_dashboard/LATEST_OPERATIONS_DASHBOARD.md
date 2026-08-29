# Operations Dashboard

Overall: **RED**
Generated: `2026-08-29T19:13:30.323621Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.523 |
| `openai_daily_director` | **RED** | STALE | 51.784 |
| `weekly_output` | **GREEN** | FRESH | 137.047 |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **AMBER** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 11.265 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 11.265 |
| `remediation_maturation` | **GREEN** | FRESH | 0.386 |

## AI and learning activity

- OpenAI receipts this month: **147**
- OpenAI cost this month: **$6.865250**
- Pending forecast candidates: **138**
- Experiment candidates: **153**
- Experiment dispatch requests: **801**
- Codex-ready remediation tasks: **20**
- Needs-more-evidence items: **17**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-director-shadow.yml:LATEST_RUN_FAILED', 'daily-director-shadow.yml:SCHEDULE_STALE', 'daily-slow-cycle-shadow.yml:LATEST_RUN_FAILED', 'daily-slow-cycle-shadow.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `openai_daily_director` - STALE
- **P1** `architecture_health` - ['DAILY_DIRECTOR_STALE']

Dashboard SHA-256: `25a523c0cdc1b485051645a7ad7ec3571963f7dc4ec6bc65e648bbb4f2150e95`
