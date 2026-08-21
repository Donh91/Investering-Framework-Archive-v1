# Operations Dashboard

Overall: **RED**
Generated: `2026-08-21T04:42:37.915174Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 7.932 |
| `openai_daily_director` | **RED** | STALE | 119.664 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **AMBER** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.046 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.046 |
| `remediation_maturation` | **GREEN** | FRESH | 0.309 |

## AI and learning activity

- OpenAI receipts this month: **74**
- OpenAI cost this month: **$2.939093**
- Pending forecast candidates: **71**
- Experiment candidates: **108**
- Experiment dispatch requests: **1036**
- Codex-ready remediation tasks: **11**
- Needs-more-evidence items: **21**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-capture-architecture-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:LATEST_RUN_FAILED', 'intraday-execution-research.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE', 'operations-dashboard.yml:LATEST_RUN_FAILED', 'pdlt-daily-census.yml:LATEST_RUN_FAILED', 'remediation-maturation.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `openai_daily_director` - STALE
- **P1** `architecture_health` - ['OUTCOME_CENSOR_RATE_HIGH']
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `3b2dcec298bc2128cc3e4883f2097b00bf01357c4fa060fed1d5281928ea9233`
