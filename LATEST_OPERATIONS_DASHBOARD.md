# Operations Dashboard

Overall: **RED**
Generated: `2026-10-05T22:19:57.791495Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 1.607 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.004 |
| `weekly_output` | **GREEN** | FRESH | 16.149 |
| `automation_health` | **RED** | RED | 0.236 |
| `architecture_health` | **GREEN** | GREEN | 0.19 |
| `experiment_lifecycle` | **GREEN** | FRESH | 0.999 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 15.165 |
| `remediation_maturation` | **GREEN** | FRESH | 0.153 |

## AI and learning activity

- OpenAI receipts this month: **88**
- OpenAI cost this month: **$6.381880**
- Pending forecast candidates: **223**
- Experiment candidates: **466**
- Experiment dispatch requests: **19806**
- Codex-ready remediation tasks: **5**
- Needs-more-evidence items: **6**

## Incidents

Open incident references: **23**

## Required actions

- **P0** `automation_health` - ['cycle-navigator-precision-learning-supervisor.yml:LATEST_RUN_FAILED', 'framework-learning-supervisor.yml:LATEST_RUN_FAILED']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `ef5d98c975d0ee6dfec7342c1afd713830a44c784c8e3e05dc3e440f029c868d`
