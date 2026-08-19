# Operations Dashboard

Overall: **RED**
Generated: `2026-08-19T04:41:01.308826Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 7.111 |
| `openai_daily_director` | **RED** | STALE | 71.638 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.12 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.12 |
| `remediation_maturation` | **GREEN** | FRESH | 0.313 |

## AI and learning activity

- OpenAI receipts this month: **54**
- OpenAI cost this month: **$2.037437**
- Pending forecast candidates: **54**
- Experiment candidates: **96**
- Experiment dispatch requests: **654**
- Codex-ready remediation tasks: **5**
- Needs-more-evidence items: **14**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `9ce24ccfdc2bf724aaf244827c9eb47fa7b9f10be4dcb30c594c755b2fea281d`
