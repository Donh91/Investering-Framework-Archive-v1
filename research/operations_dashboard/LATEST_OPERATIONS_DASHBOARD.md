# Operations Dashboard

Overall: **RED**
Generated: `2026-08-24T04:50:42.532571Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **AMBER** | DELAYED | 8.194 |
| `openai_daily_director` | **RED** | STALE | 191.799 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.123 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.123 |
| `remediation_maturation` | **GREEN** | FRESH | 0.34 |

## AI and learning activity

- OpenAI receipts this month: **109**
- OpenAI cost this month: **$4.783204**
- Pending forecast candidates: **109**
- Experiment candidates: **133**
- Experiment dispatch requests: **54**
- Codex-ready remediation tasks: **17**
- Needs-more-evidence items: **28**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['historical-altseason-cfgi-enrichment.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:LATEST_RUN_FAILED', 'intraday-execution-research.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE', 'research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `openai_daily_director` - STALE
- **P1** `daily_capture` - DELAYED
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `530d05af0f4e01fce1897a175a34f41a4721cf6e2da07cc9334aa19815fb14ca`
