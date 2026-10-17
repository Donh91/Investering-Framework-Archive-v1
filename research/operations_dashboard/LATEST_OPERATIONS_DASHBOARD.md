# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-17T17:57:26.318087Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.441 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.29 |
| `weekly_output` | **GREEN** | FRESH | 131.483 |
| `automation_health` | **AMBER** | AMBER | 0.067 |
| `architecture_health` | **GREEN** | GREEN | 0.027 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.29 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.299 |
| `remediation_maturation` | **GREEN** | FRESH | 0.013 |

## AI and learning activity

- OpenAI receipts this month: **237**
- OpenAI estimated cost this month: **$11.951165 from receipts**
- Pending forecast candidates: **246**
- Experiment candidates: **555**
- Experiment dispatch requests: **31081**
- Codex-ready remediation tasks: **5**
- Needs-more-evidence items: **2**

## Incidents

Open incident references: **22**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `SHADOW_COMPASS_V2` | 38 | $2.337074 | 0 | 38 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 16 | $2.232892 | 0 | 16 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 68 | $0.690238 | 0 | 68 | 67 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 17 | $0.212319 | 0 | 11 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 17 | $0.113258 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 2 | $0.064436 | 0 | 2 | 0 |
| `EVIDENCE_GAP_AUDIT` | 15 | $0.050586 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `73af2d7dd90a9eacc72ee6dc1f4856f605cf92c388cf71a65385a200d89fadff`
