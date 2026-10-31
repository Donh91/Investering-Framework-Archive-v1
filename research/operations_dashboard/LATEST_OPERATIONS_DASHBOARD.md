# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-31T20:24:02.378997Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.691 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.638 |
| `weekly_output` | **GREEN** | FRESH | 133.478 |
| `automation_health` | **AMBER** | AMBER | 0.248 |
| `architecture_health` | **GREEN** | GREEN | 0.211 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.638 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 11.893 |
| `remediation_maturation` | **GREEN** | FRESH | 0.101 |

## AI and learning activity

- OpenAI receipts this month: **378**
- OpenAI estimated cost this month: **$15.409312 from receipts**
- Pending forecast candidates: **273**
- Experiment candidates: **658**
- Experiment dispatch requests: **46084**
- Codex-ready remediation tasks: **3**
- Needs-more-evidence items: **3**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 67 | $4.137496 | 0 | 67 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `DAILY_DIRECTOR_SHADOW` | 124 | $1.341563 | 0 | 124 | 123 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 31 | $0.406731 | 0 | 25 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 31 | $0.207032 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 4 | $0.145990 | 0 | 4 | 0 |
| `EVIDENCE_GAP_AUDIT` | 29 | $0.097717 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `0f118f4edc6e7a7b038a2c5b524220da0180c8e12c680831a37a2aa8c3cd4d2b`
