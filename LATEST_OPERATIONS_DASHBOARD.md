# Operations Dashboard

Overall: **RED**
Generated: `2026-08-23T04:41:56.268105Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **AMBER** | DELAYED | 8.028 |
| `openai_daily_director` | **RED** | STALE | 167.653 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.996 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 1.996 |
| `remediation_maturation` | **GREEN** | FRESH | 0.312 |

## AI and learning activity

- OpenAI receipts this month: **96**
- OpenAI cost this month: **$4.055827**
- Pending forecast candidates: **97**
- Experiment candidates: **125**
- Experiment dispatch requests: **1550**
- Codex-ready remediation tasks: **9**
- Needs-more-evidence items: **29**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['daily-capture-architecture-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'historical-altseason-cfgi-enrichment.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:LATEST_RUN_FAILED', 'intraday-execution-research.yml:REPEATED_CONSECUTIVE_FAILURES', 'intraday-execution-research.yml:SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE', 'research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `openai_daily_director` - STALE
- **P1** `daily_capture` - DELAYED
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `d513a718626fedc47600a3a922ee04d66b3c40d20be525b4cf76028ac9b238f1`
