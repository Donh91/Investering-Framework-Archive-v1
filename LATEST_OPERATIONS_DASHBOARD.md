# Operations Dashboard

Overall: **RED**
Generated: `2026-08-18T04:39:57.991355Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 7.076 |
| `openai_daily_director` | **RED** | STALE | 47.62 |
| `weekly_output` | **UNKNOWN** | TIMESTAMP_UNAVAILABLE | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.15 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.151 |
| `remediation_maturation` | **GREEN** | FRESH | 0.323 |

## AI and learning activity

- OpenAI receipts this month: **44**
- OpenAI cost this month: **$1.548994**
- Pending forecast candidates: **45**
- Experiment candidates: **90**
- Experiment dispatch requests: **496**
- Codex-ready remediation tasks: **2**
- Needs-more-evidence items: **12**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['research-execution-coordinator.yml:LATEST_RUN_FAILED', 'research-execution-coordinator.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `openai_daily_director` - STALE
- **P1** `weekly_output` - TIMESTAMP_UNAVAILABLE

Dashboard SHA-256: `cad44cfa59d356868981254f267e32bb6d34cbd3de14e1681a11deee924c4c38`
