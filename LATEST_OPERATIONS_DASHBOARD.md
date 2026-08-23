# Operations Dashboard

Overall: **RED**
Generated: `2026-08-23T16:24:14.052618Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 19.733 |
| `openai_daily_director` | **RED** | STALE | 179.358 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.436 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.701 |
| `remediation_maturation` | **GREEN** | FRESH | 0.466 |

## AI and learning activity

- OpenAI receipts this month: **102**
- OpenAI cost this month: **$4.406915**
- Pending forecast candidates: **97**
- Experiment candidates: **131**
- Experiment dispatch requests: **1775**
- Codex-ready remediation tasks: **17**
- Needs-more-evidence items: **28**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-capture-architecture-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'historical-altseason-cfgi-enrichment.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:LATEST_RUN_FAILED', 'intraday-execution-research.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE', 'research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `daily_capture` - STALE
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `228fb4ed16b7df74f834ab6dc84a7d9c84c3d8019793745bbab9e3cc9ba7d2e8`
