# Operations Dashboard

Overall: **RED**
Generated: `2026-08-20T04:41:48.018081Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 7.917 |
| `openai_daily_director` | **RED** | STALE | 95.651 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.141 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.141 |
| `remediation_maturation` | **GREEN** | FRESH | 0.333 |

## AI and learning activity

- OpenAI receipts this month: **63**
- OpenAI cost this month: **$2.399193**
- Pending forecast candidates: **59**
- Experiment candidates: **99**
- Experiment dispatch requests: **831**
- Codex-ready remediation tasks: **9**
- Needs-more-evidence items: **10**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-capture-architecture-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `198a7aec260d2fbc48a9e955e3f939bd58d3017f145c4fa546df35d6d58a1ece`
