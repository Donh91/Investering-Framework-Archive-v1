# Operations Dashboard

Overall: **RED**
Generated: `2026-09-28T21:21:07.803229Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 1.685 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.103 |
| `weekly_output` | **GREEN** | FRESH | 15.507 |
| `automation_health` | **RED** | RED | 0.047 |
| `architecture_health` | **GREEN** | GREEN | 0.01 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.103 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 14.321 |
| `remediation_maturation` | **GREEN** | FRESH | 11.163 |

## AI and learning activity

- OpenAI receipts this month: **208**
- OpenAI cost this month: **$13.927907**
- Pending forecast candidates: **214**
- Experiment candidates: **426**
- Experiment dispatch requests: **14726**
- Codex-ready remediation tasks: **4**
- Needs-more-evidence items: **26**

## Incidents

Open incident references: **23**

## Required actions

- **P0** `automation_health` - ['framework-learning-supervisor.yml:LATEST_RUN_FAILED', 'situation-room-daily-static.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `e1d8f5c713033a3d3fa00504b246088d46bf9dc8534862425e239877644644c6`
