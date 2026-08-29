# Operations Dashboard

Overall: **RED**
Generated: `2026-08-29T00:25:19.355155Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.136 |
| `openai_daily_director` | **RED** | STALE | 32.981 |
| `weekly_output` | **GREEN** | FRESH | 118.244 |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 11.385 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 11.385 |
| `remediation_maturation` | **GREEN** | FRESH | 0.325 |

## AI and learning activity

- OpenAI receipts this month: **144**
- OpenAI cost this month: **$6.740758**
- Pending forecast candidates: **138**
- Experiment candidates: **153**
- Experiment dispatch requests: **801**
- Codex-ready remediation tasks: **8**
- Needs-more-evidence items: **13**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-director-shadow.yml:LATEST_RUN_FAILED', 'daily-director-shadow.yml:REPEATED_CONSECUTIVE_FAILURES', 'daily-director-shadow.yml:SCHEDULE_STALE', 'daily-slow-cycle-shadow.yml:LATEST_RUN_FAILED']
- **P0** `openai_daily_director` - STALE

Dashboard SHA-256: `26be0da7a7f04fc5882b61e00b5bbcbfdbb0a09582a6797aa5ceaaca619c531f`
