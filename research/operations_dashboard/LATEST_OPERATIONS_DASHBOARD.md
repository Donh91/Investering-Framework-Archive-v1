# Operations Dashboard

Overall: **RED**
Generated: `2026-08-22T16:22:24.847816Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 19.678 |
| `openai_daily_director` | **RED** | STALE | 155.327 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **AMBER** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.445 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.822 |
| `remediation_maturation` | **GREEN** | FRESH | 0.454 |

## AI and learning activity

- OpenAI receipts this month: **91**
- OpenAI cost this month: **$3.838264**
- Pending forecast candidates: **84**
- Experiment candidates: **123**
- Experiment dispatch requests: **1479**
- Codex-ready remediation tasks: **13**
- Needs-more-evidence items: **15**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-capture-architecture-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'historical-altseason-cfgi-enrichment.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:LATEST_RUN_FAILED', 'intraday-execution-research.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE', 'research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `daily_capture` - STALE
- **P0** `openai_daily_director` - STALE
- **P1** `architecture_health` - ['OUTCOME_CENSOR_RATE_HIGH']
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `5544c2fdd2eed24a03975f8da7461cf8a1517933fca64fc210e1d65ea1fcd2c1`
