# Operations Dashboard

Overall: **RED**
Generated: `2026-08-14T16:52:05.594615Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 66.883 |
| `openai_daily_director` | **RED** | STALE | 114.972 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 13.343 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.343 |
| `remediation_maturation` | **GREEN** | FRESH | 0.374 |

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

Dashboard SHA-256: `756aebd64cd89d1e1634dd102557f74618b37f2d15aefaddbd943bccb71fadf4`
