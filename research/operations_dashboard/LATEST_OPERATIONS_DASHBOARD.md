# Operations Dashboard

Overall: **RED**
Generated: `2026-08-28T16:29:17.032234Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 5.081 |
| `openai_daily_director` | **AMBER** | DELAYED | 25.047 |
| `weekly_output` | **GREEN** | FRESH | 110.31 |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.451 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.451 |
| `remediation_maturation` | **GREEN** | FRESH | 0.799 |

## AI and learning activity

- OpenAI receipts this month: **144**
- OpenAI cost this month: **$6.740758**
- Pending forecast candidates: **138**
- Experiment candidates: **153**
- Experiment dispatch requests: **801**
- Codex-ready remediation tasks: **7**
- Needs-more-evidence items: **30**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-director-shadow.yml:LATEST_RUN_FAILED', 'daily-director-shadow.yml:REPEATED_CONSECUTIVE_FAILURES', 'daily-director-shadow.yml:SCHEDULE_STALE', 'entry-signal-ledger.yml:LATEST_RUN_FAILED', 'entry-signal-ledger.yml:SCHEDULE_STALE', 'pullback-learning-ledger.yml:LATEST_RUN_FAILED', 'pullback-learning-ledger.yml:SCHEDULE_STALE', 'situation-room-daily-static.yml:LATEST_RUN_FAILED', 'situation-room-daily-static.yml:SCHEDULE_STALE']
- **P1** `openai_daily_director` - DELAYED

Dashboard SHA-256: `81c23b578548d87a29b7addb95e58d262a49358c60d2544535575035f0b3efd7`
