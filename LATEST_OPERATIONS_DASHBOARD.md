# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-29T11:22:54.092797Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.263 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 9.442 |
| `weekly_output` | **GREEN** | FRESH | 76.459 |
| `automation_health` | **AMBER** | AMBER | 0.39 |
| `architecture_health` | **GREEN** | GREEN | 0.335 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.731 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.758 |
| `remediation_maturation` | **GREEN** | FRESH | 0.24 |

## AI and learning activity

- OpenAI receipts this month: **355**
- OpenAI estimated cost this month: **$14.908264 from receipts**
- Pending forecast candidates: **269**
- Experiment candidates: **636**
- Experiment dispatch requests: **43036**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **4**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 62 | $3.819630 | 0 | 62 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `DAILY_DIRECTOR_SHADOW` | 113 | $1.207496 | 0 | 113 | 112 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 29 | $0.377993 | 0 | 23 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 29 | $0.193572 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 4 | $0.145990 | 0 | 4 | 0 |
| `UNCLASSIFIED` | 4 | $0.094826 | 0 | 4 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `8a6d34de24a3e82426030459c81d7c3ac4dda1f6e01ad80dfeb181240d04d659`
