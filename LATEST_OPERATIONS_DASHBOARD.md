# Operations Dashboard

Overall: **RED**
Generated: `2026-10-06T20:48:06.483996Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.469 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.727 |
| `weekly_output` | **GREEN** | FRESH | 38.618 |
| `automation_health` | **RED** | RED | 0.329 |
| `architecture_health` | **GREEN** | GREEN | 0.278 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.723 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 13.174 |
| `remediation_maturation` | **GREEN** | FRESH | 0.168 |

## AI and learning activity

- OpenAI receipts this month: **106**
- OpenAI cost this month: **$7.509793**
- Pending forecast candidates: **224**
- Experiment candidates: **470**
- Experiment dispatch requests: **20679**
- Codex-ready remediation tasks: **5**
- Needs-more-evidence items: **1**

## Incidents

Open incident references: **24**

## Required actions

- **P0** `automation_health` - ['framework-learning-operations.yml:LATEST_RUN_FAILED', 'framework-learning-operations.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `f904a25764badf65b0515f1cf59ef32a9dcbefff14723f046ef039d01d76a37c`
