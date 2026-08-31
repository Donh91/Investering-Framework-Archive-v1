# Operations Dashboard

Overall: **RED**
Generated: `2026-08-31T10:41:59.717344Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 5.099 |
| `openai_daily_director` | **RED** | STALE | 91.259 |
| `weekly_output` | **GREEN** | FRESH | 4.645 |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **AMBER** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.527 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.527 |
| `remediation_maturation` | **GREEN** | FRESH | 0.59 |

## AI and learning activity

- OpenAI receipts this month: **155**
- OpenAI cost this month: **$7.294758**
- Pending forecast candidates: **138**
- Experiment candidates: **153**
- Experiment dispatch requests: **801**
- Codex-ready remediation tasks: **25**
- Needs-more-evidence items: **18**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['buildwithclaude-shadow-round1.yml:REPEATED_CONSECUTIVE_FAILURES', 'daily-director-shadow.yml:LATEST_RUN_FAILED', 'daily-director-shadow.yml:SCHEDULE_STALE']
- **P0** `openai_daily_director` - STALE
- **P1** `architecture_health` - ['DAILY_DIRECTOR_STALE']

Dashboard SHA-256: `7e2e48b7be3c254c6c6e94a94b7a9c6722bb2dd604b4b6a0af6cb4bb1a43bf46`
