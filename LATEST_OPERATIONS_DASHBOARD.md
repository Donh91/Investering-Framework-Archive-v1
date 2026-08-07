# Operations Dashboard

Overall: **RED**
Generated: `2026-08-07T05:43:48.945436Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.696 |
| `openai_daily_director` | **RED** | STALE | 80.812 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **RED** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.652 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 1.652 |
| `remediation_maturation` | **GREEN** | FRESH | 0.312 |

## AI and learning activity

- OpenAI receipts this month: **6**
- OpenAI cost this month: **$0.083987**
- Pending forecast candidates: **43**
- Experiment candidates: **26**
- Experiment dispatch requests: **30**
- Codex-ready remediation tasks: **9**
- Needs-more-evidence items: **9**

## Incidents

Open incident references: **14**

## Required actions

- **P0** `architecture_health` - ['NO_WEEKLY_API_OUTPUT_YET', 'ETF_OWNER_STALE']
- **P0** `automation_health` - ['backtest-wave1-4-prospective.yml:LATEST_RUN_FAILED', 'operations-dashboard.yml:LATEST_RUN_FAILED', 'remediation-maturation.yml:LATEST_RUN_FAILED', 'storage-health-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:SCHEDULE_STALE', 'weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED', 'weekly-api-calibration-shadow.yml:REPEATED_CONSECUTIVE_FAILURES', 'weekly-api-calibration-shadow.yml:SCHEDULE_STALE']
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `3b4b180a26006a9447ada6feb36d2f29d22fb48ea6f74cdfb18d0f960aa20cce`
