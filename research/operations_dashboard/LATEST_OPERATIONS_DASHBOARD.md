# Operations Dashboard

Overall: **RED**
Generated: `2026-08-21T16:33:24.633157Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 19.779 |
| `openai_daily_director` | **RED** | STALE | 131.511 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **AMBER** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.383 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.892 |
| `remediation_maturation` | **GREEN** | FRESH | 0.507 |

## AI and learning activity

- OpenAI receipts this month: **80**
- OpenAI cost this month: **$3.253941**
- Pending forecast candidates: **71**
- Experiment candidates: **116**
- Experiment dispatch requests: **1215**
- Codex-ready remediation tasks: **12**
- Needs-more-evidence items: **18**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-capture-architecture-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'historical-altseason-cfgi-enrichment.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:LATEST_RUN_FAILED', 'intraday-execution-research.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE', 'pdlt-daily-census.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `daily_capture` - STALE
- **P0** `openai_daily_director` - STALE
- **P1** `architecture_health` - ['OUTCOME_CENSOR_RATE_HIGH']
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `35719af380fa27bb6e60479cb18236c797692bad34fe4bac5cf64294fb959e54`
