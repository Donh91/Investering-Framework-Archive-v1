# Operations Dashboard

Overall: **RED**
Generated: `2026-08-19T16:30:10.872620Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 18.93 |
| `openai_daily_director` | **RED** | STALE | 83.457 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.343 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.939 |
| `remediation_maturation` | **GREEN** | FRESH | 0.475 |

## AI and learning activity

- OpenAI receipts this month: **58**
- OpenAI cost this month: **$2.202762**
- Pending forecast candidates: **54**
- Experiment candidates: **98**
- Experiment dispatch requests: **786**
- Codex-ready remediation tasks: **9**
- Needs-more-evidence items: **10**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-capture-architecture-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `daily_capture` - STALE
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `30ffe0be890c78aa2de2949f97bfdb3820d415c93ae31bdb1e81afab195aeefd`
