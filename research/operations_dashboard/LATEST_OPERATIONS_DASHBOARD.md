# Operations Dashboard

Overall: **RED**
Generated: `2026-08-25T04:43:14.171540Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.834 |
| `openai_daily_director` | **RED** | STALE | 215.674 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.146 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.147 |
| `remediation_maturation` | **GREEN** | FRESH | 0.311 |

## AI and learning activity

- OpenAI receipts this month: **119**
- OpenAI cost this month: **$5.317620**
- Pending forecast candidates: **118**
- Experiment candidates: **140**
- Experiment dispatch requests: **276**
- Codex-ready remediation tasks: **16**
- Needs-more-evidence items: **33**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['historical-altseason-cfgi-enrichment.yml:REPEATED_CONSECUTIVE_FAILURES', 'historical-altseason-lab-gate.yml:ARTIFACT_RETENTION_UNBOUNDED', 'historical-altseason-lab-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'shadow-admission-ai-decider.yml:LATEST_RUN_FAILED']
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `b8a5c92fab76306ad3ab4f908e647b8a9c7e1dcadf4af394a0c285cc697a5e9f`
