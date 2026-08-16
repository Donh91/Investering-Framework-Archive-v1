# Operations Dashboard

Overall: **RED**
Generated: `2026-08-16T16:23:54.518701Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 18.876 |
| `openai_daily_director` | **AMBER** | DELAYED | 26.47 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.464 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.792 |
| `remediation_maturation` | **GREEN** | FRESH | 0.474 |

## AI and learning activity

- OpenAI receipts this month: **27**
- OpenAI cost this month: **$0.785086**
- Pending forecast candidates: **19**
- Experiment candidates: **78**
- Experiment dispatch requests: **328**
- Codex-ready remediation tasks: **7**
- Needs-more-evidence items: **13**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `daily_capture` - STALE
- **P1** `openai_daily_director` - DELAYED
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `b15a6b737d34c34e32800fee313f9417a907dea338bbfbdce136a87b91b66c4e`
