# Operations Dashboard

Overall: **RED**
Generated: `2026-09-30T20:34:34.976070Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.587 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 2.0 |
| `weekly_output` | **GREEN** | FRESH | 62.731 |
| `automation_health` | **RED** | RED | 0.398 |
| `architecture_health` | **AMBER** | AMBER | 0.352 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.0 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.76 |
| `remediation_maturation` | **GREEN** | FRESH | 0.276 |

## AI and learning activity

- OpenAI receipts this month: **216**
- OpenAI cost this month: **$14.349592**
- Pending forecast candidates: **215**
- Experiment candidates: **435**
- Experiment dispatch requests: **15670**
- Codex-ready remediation tasks: **7**
- Needs-more-evidence items: **33**

## Incidents

Open incident references: **26**

## Required actions

- **P0** `automation_health` - ['cycle-navigator-public-contract-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'situation-room-daily-static.yml:LATEST_RUN_FAILED', 'situation-room-daily-static.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P1** `architecture_health` - ['EXPERIMENT_RECEIPT_SYNC_UNAVAILABLE']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `bcf2f6a26e9f3c5bc6933d1f15eb5c4be010a9381568e9aa1607b1aa8fdb041d`
