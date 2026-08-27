# Operations Dashboard

Overall: **RED**
Generated: `2026-08-27T15:04:31.125687Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 5.244 |
| `openai_daily_director` | **AMBER** | DELAYED | 14.098 |
| `weekly_output` | **RED** | TARGET_HASH_MISMATCH | - |
| `automation_health` | **RED** | - | - |
| `architecture_health` | **GREEN** | - | - |
| `experiment_lifecycle` | **GREEN** | FRESH | 3.708 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 3.708 |
| `remediation_maturation` | **GREEN** | FRESH | 0.279 |

## AI and learning activity

- OpenAI receipts this month: **140**
- OpenAI cost this month: **$6.539448**
- Pending forecast candidates: **138**
- Experiment candidates: **153**
- Experiment dispatch requests: **741**
- Codex-ready remediation tasks: **18**
- Needs-more-evidence items: **33**

## Incidents

Open incident references: **20**

## Required actions

- **P0** `automation_health` - ['historical-altseason-throughput-gate.yml:ARTIFACT_RETENTION_UNBOUNDED', 'historical-altseason-throughput-gate.yml:REPEATED_CONSECUTIVE_FAILURES']
- **P0** `weekly_output` - TARGET_HASH_MISMATCH
- **P1** `openai_daily_director` - DELAYED

Dashboard SHA-256: `4e8c760c873279b4a5f4f4c3dbc0213c06c61e12b2a9b0325b1b722a3b12c297`
