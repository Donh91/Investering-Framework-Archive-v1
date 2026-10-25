# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-25T09:39:10.115675Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.94 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 10.074 |
| `weekly_output` | **GREEN** | FRESH | 148.396 |
| `automation_health` | **AMBER** | AMBER | 0.39 |
| `architecture_health` | **GREEN** | GREEN | 0.352 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.948 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 1.995 |
| `remediation_maturation` | **GREEN** | FRESH | 0.204 |

## AI and learning activity

- OpenAI receipts this month: **316**
- OpenAI estimated cost this month: **$14.034419 from receipts**
- Pending forecast candidates: **261**
- Experiment candidates: **609**
- Experiment dispatch requests: **38685**
- Codex-ready remediation tasks: **2**
- Needs-more-evidence items: **2**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 54 | $3.324154 | 0 | 54 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 97 | $1.019011 | 0 | 97 | 96 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 25 | $0.321016 | 0 | 19 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 25 | $0.166428 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.101492 | 0 | 3 | 0 |
| `EVIDENCE_GAP_AUDIT` | 23 | $0.077785 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `2981a255800108aa4cb68d56c6de6bb126eb762466c17769ed044a7ce85c242b`
