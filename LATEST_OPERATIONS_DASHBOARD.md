# Operations Dashboard

Overall: **RED**
Generated: `2026-10-05T22:09:03.216055Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 1.425 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 0.822 |
| `weekly_output` | **GREEN** | FRESH | 15.967 |
| `automation_health` | **RED** | RED | 0.054 |
| `architecture_health` | **GREEN** | GREEN | 0.008 |
| `experiment_lifecycle` | **GREEN** | FRESH | 0.817 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 14.984 |
| `remediation_maturation` | **GREEN** | FRESH | 11.267 |

## AI and learning activity

- OpenAI receipts this month: **87**
- OpenAI cost this month: **$6.381415**
- Pending forecast candidates: **223**
- Experiment candidates: **466**
- Experiment dispatch requests: **19806**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **14**

## Incidents

Open incident references: **23**

## Required actions

- **P0** `automation_health` - ['cycle-navigator-precision-learning-supervisor.yml:LATEST_RUN_FAILED', 'framework-learning-supervisor.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `c38aa40107ee0efee5ed1c162c1bdfb399d1fba9ed9849b35ed382c0ad947686`
