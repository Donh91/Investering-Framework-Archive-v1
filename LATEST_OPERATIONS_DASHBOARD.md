# Operations Dashboard

Overall: **RED**
Generated: `2026-10-06T20:32:41.224448Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.212 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.47 |
| `weekly_output` | **GREEN** | FRESH | 38.361 |
| `automation_health` | **RED** | RED | 0.072 |
| `architecture_health` | **GREEN** | GREEN | 0.021 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.466 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.917 |
| `remediation_maturation` | **GREEN** | FRESH | 9.713 |

## AI and learning activity

- OpenAI receipts this month: **105**
- OpenAI cost this month: **$7.495023**
- Pending forecast candidates: **224**
- Experiment candidates: **470**
- Experiment dispatch requests: **20679**
- Codex-ready remediation tasks: **5**
- Needs-more-evidence items: **5**

## Incidents

Open incident references: **24**

## Required actions

- **P0** `automation_health` - ['framework-learning-operations.yml:LATEST_RUN_FAILED', 'framework-learning-operations.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `ca96b6f0ba577f81d8b8e8ba32e0b36daab0da09a844aa03f95b0f68bf39231f`
