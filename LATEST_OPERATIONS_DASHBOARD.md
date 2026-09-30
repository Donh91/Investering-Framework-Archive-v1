# Operations Dashboard

Overall: **RED**
Generated: `2026-09-30T20:14:47.464518Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.257 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.67 |
| `weekly_output` | **GREEN** | FRESH | 62.401 |
| `automation_health` | **RED** | RED | 0.068 |
| `architecture_health` | **AMBER** | AMBER | 0.022 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.67 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.43 |
| `remediation_maturation` | **GREEN** | FRESH | 10.226 |

## AI and learning activity

- OpenAI receipts this month: **216**
- OpenAI cost this month: **$14.349592**
- Pending forecast candidates: **215**
- Experiment candidates: **435**
- Experiment dispatch requests: **15670**
- Codex-ready remediation tasks: **7**
- Needs-more-evidence items: **42**

## Incidents

Open incident references: **26**

## Required actions

- **P0** `automation_health` - ['cycle-navigator-public-contract-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'situation-room-daily-static.yml:LATEST_RUN_FAILED', 'situation-room-daily-static.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P1** `architecture_health` - ['EXPERIMENT_RECEIPT_SYNC_UNAVAILABLE']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `4c00dc7384f39547e61ec3b15dadfcab0416e73f045cdb10386690e957d2d359`
