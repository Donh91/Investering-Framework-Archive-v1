# Operations Dashboard

Overall: **RED**
Generated: `2026-08-22T04:37:35.962822Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 7.931 |
| `openai_daily_director` | **RED** | STALE | 143.581 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **AMBER** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.076 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.076 |
| `remediation_maturation` | **GREEN** | FRESH | 0.335 |

## AI and learning activity

- OpenAI receipts this month: **85**
- OpenAI cost this month: **$3.457142**
- Pending forecast candidates: **84**
- Experiment candidates: **117**
- Experiment dispatch requests: **1278**
- Codex-ready remediation tasks: **13**
- Needs-more-evidence items: **16**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-capture-architecture-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'historical-altseason-cfgi-enrichment.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:LATEST_RUN_FAILED', 'intraday-execution-research.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE', 'research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `openai_daily_director` - STALE
- **P1** `architecture_health` - ['OUTCOME_CENSOR_RATE_HIGH']
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `c2685dfa722ed85d35ce399da8fcb10f26ff519465e458f9d7b5ce693d9f2081`
