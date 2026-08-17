# Operations Dashboard

Overall: **RED**
Generated: `2026-08-17T04:48:15.955558Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 7.291 |
| `openai_daily_director` | **AMBER** | DELAYED | 23.758 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.206 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.206 |
| `remediation_maturation` | **GREEN** | FRESH | 0.365 |

## AI and learning activity

- OpenAI receipts this month: **33**
- OpenAI cost this month: **$1.032953**
- Pending forecast candidates: **32**
- Experiment candidates: **82**
- Experiment dispatch requests: **356**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **12**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P1** `openai_daily_director` - DELAYED
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `fcb9f4982c8b152988e51be54bdac94ace07af739bd4f2ace647b64dbd9ccb19`
