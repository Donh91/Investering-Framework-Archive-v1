# Operations Dashboard

Overall: **RED**
Generated: `2026-08-30T09:50:33.708158Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.422 |
| `openai_daily_director` | **RED** | STALE | 66.402 |
| `weekly_output` | **GREEN** | FRESH | 151.664 |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **AMBER** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.007 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.008 |
| `remediation_maturation` | **GREEN** | FRESH | 0.364 |

## AI and learning activity

- OpenAI receipts this month: **150**
- OpenAI cost this month: **$6.994232**
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

Dashboard SHA-256: `12655d09ee37253c81788538b63361cb2fffb98c15a9359f6ee000c07688782f`
