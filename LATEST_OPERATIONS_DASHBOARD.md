# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-24T08:46:16.842519Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 4.138 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 8.811 |
| `weekly_output` | **GREEN** | FRESH | 123.514 |
| `automation_health` | **AMBER** | AMBER | 0.474 |
| `architecture_health` | **GREEN** | GREEN | 0.424 |
| `experiment_lifecycle` | **GREEN** | FRESH | 2.716 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 2.781 |
| `remediation_maturation` | **GREEN** | FRESH | 0.342 |

## AI and learning activity

- OpenAI receipts this month: **306**
- OpenAI estimated cost this month: **$13.784859 from receipts**
- Pending forecast candidates: **259**
- Experiment candidates: **601**
- Experiment dispatch requests: **37607**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **2**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 51 | $3.145460 | 0 | 51 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 93 | $0.972111 | 0 | 93 | 92 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 8 | $0.674266 | 0 | 8 | 4 |
| `DECISION_MISS_AUDIT` | 24 | $0.307146 | 0 | 18 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 24 | $0.159770 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.101492 | 0 | 3 | 0 |
| `EVIDENCE_GAP_AUDIT` | 22 | $0.074347 | 0 | 0 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `943aaa0f19178c276ee914a4701e150c632cf6f1fd9d0692e43a4cfc42a6009a`
