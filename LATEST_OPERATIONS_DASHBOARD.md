# Operations Dashboard

Overall: **RED**
Generated: `2026-08-28T00:45:15.903289Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.514 |
| `openai_daily_director` | **UNKNOWN** | FRESH | 9.314 |
| `weekly_output` | **GREEN** | FRESH | 94.576 |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 9.314 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.387 |
| `remediation_maturation` | **GREEN** | FRESH | 0.157 |

## AI and learning activity

- OpenAI receipts this month: **141**
- OpenAI cost this month: **$6.612968**
- Pending forecast candidates: **138**
- Experiment candidates: **153**
- Experiment dispatch requests: **801**
- Codex-ready remediation tasks: **10**
- Needs-more-evidence items: **20**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-director-shadow.yml:LATEST_RUN_FAILED', 'daily-director-shadow.yml:REPEATED_CONSECUTIVE_FAILURES', 'situation-room-daily-static.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - FRESH

Dashboard SHA-256: `b825dbe55d6e928dbdc990b79c78e54609f63ba42bd50b50de6c5c58be80e1d4`
