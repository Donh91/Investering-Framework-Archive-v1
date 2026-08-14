# Operations Dashboard

Overall: **RED**
Generated: `2026-08-14T05:40:48.397970Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 55.695 |
| `openai_daily_director` | **RED** | STALE | 103.784 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.155 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.155 |
| `remediation_maturation` | **GREEN** | FRESH | 0.345 |

## AI and learning activity

- OpenAI receipts this month: **13**
- OpenAI cost this month: **$0.235454**
- Pending forecast candidates: **138**
- Experiment candidates: **64**
- Experiment dispatch requests: **193**
- Codex-ready remediation tasks: **8**
- Needs-more-evidence items: **11**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['continuity-learning-maintenance.yml:LATEST_RUN_FAILED', 'continuity-learning-maintenance.yml:REPEATED_CONSECUTIVE_FAILURES', 'research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `daily_capture` - STALE
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `59f4835c270eb6c1d3db9fd5cf903559cc1012bf2fd89facf2dc6f1c7ee6e11b`
