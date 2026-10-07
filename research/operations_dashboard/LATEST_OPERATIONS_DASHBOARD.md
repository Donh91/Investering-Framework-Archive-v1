# Operations Dashboard

Overall: **RED**
Generated: `2026-10-07T07:47:33.227084Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 1.773 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 6.824 |
| `weekly_output` | **GREEN** | FRESH | 49.608 |
| `automation_health` | **RED** | RED | 0.046 |
| `architecture_health` | **GREEN** | GREEN | 0.012 |
| `experiment_lifecycle` | **GREEN** | FRESH | 0.488 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 0.489 |
| `remediation_maturation` | **GREEN** | FRESH | 11.159 |

## AI and learning activity

- OpenAI receipts this month: **111**
- OpenAI cost this month: **$7.779104**
- Pending forecast candidates: **226**
- Experiment candidates: **472**
- Experiment dispatch requests: **20899**
- Codex-ready remediation tasks: **5**
- Needs-more-evidence items: **1**

## Incidents

Open incident references: **25**

## Required actions

- **P0** `automation_health` - ['adaptive-decision-miss-validation.yml:LATEST_RUN_FAILED', 'edge001-t2-registry.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `b2dedaeec33b15e4896444b6ce04f0e6f2b9ca5aa4ee75c5ae4b85824f94e823`
