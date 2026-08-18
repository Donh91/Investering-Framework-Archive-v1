# Operations Dashboard

Overall: **RED**
Generated: `2026-08-18T16:30:25.141177Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 18.917 |
| `openai_daily_director` | **RED** | STALE | 59.461 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.34 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.991 |
| `remediation_maturation` | **GREEN** | FRESH | 0.485 |

## AI and learning activity

- OpenAI receipts this month: **49**
- OpenAI cost this month: **$1.812115**
- Pending forecast candidates: **45**
- Experiment candidates: **94**
- Experiment dispatch requests: **612**
- Codex-ready remediation tasks: **2**
- Needs-more-evidence items: **14**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `daily_capture` - STALE
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `106d949b1cf17becc1dac9a85bef8483188cc824ee52987a51229b9f62e80d80`
