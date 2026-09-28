# Operations Dashboard

Overall: **RED**
Generated: `2026-09-28T21:38:04.397757Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 1.968 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.386 |
| `weekly_output` | **GREEN** | FRESH | 15.789 |
| `automation_health` | **RED** | RED | 0.329 |
| `architecture_health` | **GREEN** | GREEN | 0.292 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.386 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 14.603 |
| `remediation_maturation` | **GREEN** | FRESH | 0.258 |

## AI and learning activity

- OpenAI receipts this month: **208**
- OpenAI cost this month: **$13.927907**
- Pending forecast candidates: **214**
- Experiment candidates: **426**
- Experiment dispatch requests: **14726**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **23**

## Incidents

Open incident references: **23**

## Required actions

- **P0** `automation_health` - ['framework-learning-supervisor.yml:LATEST_RUN_FAILED', 'situation-room-daily-static.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `4de7228a7b1ea430c0b94897982deb5fc630e5302998e5cd3fe6afd53c97d164`
