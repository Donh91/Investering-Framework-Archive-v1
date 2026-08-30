# Operations Dashboard

Overall: **RED**
Generated: `2026-08-30T19:03:28.204338Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.408 |
| `openai_daily_director` | **RED** | STALE | 75.617 |
| `weekly_output` | **GREEN** | FRESH | 160.879 |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **AMBER** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 12.223 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.223 |
| `remediation_maturation` | **GREEN** | FRESH | 0.256 |

## AI and learning activity

- OpenAI receipts this month: **150**
- OpenAI cost this month: **$6.994232**
- Pending forecast candidates: **138**
- Experiment candidates: **153**
- Experiment dispatch requests: **801**
- Codex-ready remediation tasks: **21**
- Needs-more-evidence items: **18**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-director-shadow.yml:LATEST_RUN_FAILED', 'daily-director-shadow.yml:SCHEDULE_STALE']
- **P0** `openai_daily_director` - STALE
- **P1** `architecture_health` - ['DAILY_DIRECTOR_STALE']

Dashboard SHA-256: `e23ea6f17f043d6f8d511a19034e12255c6a9cc6332f2ee7976f25a0b0253714`
