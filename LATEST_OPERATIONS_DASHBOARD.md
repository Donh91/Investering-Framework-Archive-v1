# Operations Dashboard

Overall: **RED**
Generated: `2026-08-13T05:43:35.303131Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 31.741 |
| `openai_daily_director` | **RED** | STALE | 79.83 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.161 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.161 |
| `remediation_maturation` | **GREEN** | FRESH | 0.338 |

## AI and learning activity

- OpenAI receipts this month: **12**
- OpenAI cost this month: **$0.202256**
- Pending forecast candidates: **138**
- Experiment candidates: **61**
- Experiment dispatch requests: **164**
- Codex-ready remediation tasks: **4**
- Needs-more-evidence items: **13**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['continuity-learning-maintenance.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:LATEST_RUN_FAILED']
- **P0** `daily_capture` - STALE
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `1c5c4a5bd33f6dca99c088369d6dcb6854381d4d45f5120f0242d708e6933720`
