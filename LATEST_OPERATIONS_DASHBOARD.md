# Operations Dashboard

Overall: **RED**
Generated: `2026-08-17T16:26:35.382165Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 18.929 |
| `openai_daily_director` | **RED** | STALE | 35.397 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.36 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.845 |
| `remediation_maturation` | **GREEN** | FRESH | 0.49 |

## AI and learning activity

- OpenAI receipts this month: **39**
- OpenAI cost this month: **$1.355113**
- Pending forecast candidates: **32**
- Experiment candidates: **88**
- Experiment dispatch requests: **459**
- Codex-ready remediation tasks: **2**
- Needs-more-evidence items: **12**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `daily_capture` - STALE
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `5e9603f1886be431fdfe540722d036968a93c84ee073fd761a8d4fdafca4bed8`
