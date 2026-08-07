# Operations Dashboard

Overall: **RED**
Generated: `2026-08-07T16:54:13.584914Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **AMBER** | DELAYED | 15.87 |
| `openai_daily_director` | **RED** | STALE | 91.985 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **RED** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 12.825 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.825 |
| `remediation_maturation` | **GREEN** | FRESH | 0.37 |

## AI and learning activity

- OpenAI receipts this month: **6**
- OpenAI cost this month: **$0.083987**
- Pending forecast candidates: **43**
- Experiment candidates: **26**
- Experiment dispatch requests: **30**
- Codex-ready remediation tasks: **9**
- Needs-more-evidence items: **7**

## Incidents

Open incident references: **14**

## Required actions

- **P0** `architecture_health` - ['NO_WEEKLY_API_OUTPUT_YET', 'ETF_OWNER_STALE']
- **P0** `automation_health` - ['backtest-wave1-4-prospective.yml:LATEST_RUN_FAILED', 'storage-health-gate.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:LATEST_RUN_FAILED', 'sunday-market-close-and-cfgi.yml:REPEATED_CONSECUTIVE_FAILURES', 'sunday-market-close-and-cfgi.yml:SCHEDULE_STALE', 'weekly-api-calibration-shadow.yml:LATEST_RUN_FAILED', 'weekly-api-calibration-shadow.yml:REPEATED_CONSECUTIVE_FAILURES', 'weekly-api-calibration-shadow.yml:SCHEDULE_STALE']
- **P0** `openai_daily_director` - STALE
- **P1** `daily_capture` - DELAYED
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `ba55549fc5752d7773bd2f4fa07e77aee2e92b9c1dfb797b2fb7deb814cd8b53`
