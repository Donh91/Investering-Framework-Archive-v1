# Operations Dashboard

Overall: **RED**
Generated: `2026-08-31T21:18:43.232492Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.186 |
| `openai_daily_director` | **RED** | STALE | 101.871 |
| `weekly_output` | **GREEN** | FRESH | 15.258 |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **AMBER** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 14.139 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 14.14 |
| `remediation_maturation` | **GREEN** | FRESH | 0.233 |

## AI and learning activity

- OpenAI receipts this month: **155**
- OpenAI cost this month: **$7.294758**
- Pending forecast candidates: **138**
- Experiment candidates: **153**
- Experiment dispatch requests: **801**
- Codex-ready remediation tasks: **24**
- Needs-more-evidence items: **18**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['buildwithclaude-shadow-round1.yml:REPEATED_CONSECUTIVE_FAILURES', 'cycle-navigator-weekly-publication.yml:LATEST_RUN_FAILED', 'daily-director-shadow.yml:LATEST_RUN_FAILED', 'daily-director-shadow.yml:SCHEDULE_STALE']
- **P0** `openai_daily_director` - STALE
- **P1** `architecture_health` - ['DAILY_DIRECTOR_STALE']

Dashboard SHA-256: `9a1d0dfb94a803ed0661bcecc3ff28127ba10c70083498499922fb85d7ee6e52`
