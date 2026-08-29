# Operations Dashboard

Overall: **RED**
Generated: `2026-08-29T10:56:11.454643Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.84 |
| `openai_daily_director` | **RED** | STALE | 43.496 |
| `weekly_output` | **GREEN** | FRESH | 128.758 |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **AMBER** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.977 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.977 |
| `remediation_maturation` | **GREEN** | FRESH | 0.492 |

## AI and learning activity

- OpenAI receipts this month: **147**
- OpenAI cost this month: **$6.865250**
- Pending forecast candidates: **138**
- Experiment candidates: **153**
- Experiment dispatch requests: **801**
- Codex-ready remediation tasks: **10**
- Needs-more-evidence items: **14**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-slow-cycle-shadow.yml:LATEST_RUN_FAILED', 'entry-signal-ledger.yml:LATEST_RUN_FAILED', 'entry-signal-ledger.yml:REPEATED_CONSECUTIVE_FAILURES', 'pullback-learning-ledger.yml:LATEST_RUN_FAILED', 'pullback-learning-ledger.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `openai_daily_director` - STALE
- **P1** `architecture_health` - ['DAILY_DIRECTOR_STALE']

Dashboard SHA-256: `707d39cccfe1a7c2fde1662d49b25f75d7ec71db9c2de66f206e1e9de4548bd1`
