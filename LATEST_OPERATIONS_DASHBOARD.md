# Operations Dashboard

Overall: **RED**
Generated: `2026-08-13T16:55:37.761250Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 42.942 |
| `openai_daily_director` | **RED** | STALE | 91.031 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 13.361 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.361 |
| `remediation_maturation` | **GREEN** | FRESH | 0.383 |

## AI and learning activity

- OpenAI receipts this month: **12**
- OpenAI cost this month: **$0.202256**
- Pending forecast candidates: **138**
- Experiment candidates: **61**
- Experiment dispatch requests: **164**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **12**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['continuity-learning-maintenance.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `daily_capture` - STALE
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `aa48f21c295b4337b30edee055b7680e740a24a176d7f4fa2924a854863fe0ff`
