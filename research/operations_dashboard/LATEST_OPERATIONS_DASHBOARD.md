# Operations Dashboard

Overall: **RED**
Generated: `2026-08-10T16:53:02.013635Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **RED** | STALE | 19.149 |
| `openai_daily_director` | **AMBER** | DELAYED | 18.988 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **AMBER** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 13.557 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.557 |
| `remediation_maturation` | **GREEN** | FRESH | 0.388 |

## AI and learning activity

- OpenAI receipts this month: **9**
- OpenAI cost this month: **$0.135128**
- Pending forecast candidates: **90**
- Experiment candidates: **56**
- Experiment dispatch requests: **94**
- Codex-ready remediation tasks: **1**
- Needs-more-evidence items: **11**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['pdlt-discovery-once.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `daily_capture` - STALE
- **P1** `architecture_health` - ['ETF_OWNER_STALE']
- **P1** `openai_daily_director` - DELAYED
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `b50f20575ef4f17a603dd7e6f860fae95f77d75bc75da0ea85547e66f7856617`
