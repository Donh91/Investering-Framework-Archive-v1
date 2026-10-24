# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-24T18:36:20.238324Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.696 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.597 |
| `weekly_output` | **GREEN** | FRESH | 133.348 |
| `automation_health` | **AMBER** | AMBER | 0.336 |
| `architecture_health` | **GREEN** | GREEN | 0.324 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.597 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 12.615 |
| `remediation_maturation` | **GREEN** | FRESH | 0.249 |

## AI and learning activity

- OpenAI receipts this month: **311**
- OpenAI estimated cost this month: **$13.938417 from receipts**
- Pending forecast candidates: **259**
- Experiment candidates: **607**
- Experiment dispatch requests: **38415**
- Codex-ready remediation tasks: **5**
- Needs-more-evidence items: **2**

## Incidents

Open incident references: **23**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `SHADOW_COMPASS_V2` | 53 | $3.263398 | 0 | 53 | 0 |
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 96 | $1.007731 | 0 | 96 | 95 |
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

Dashboard SHA-256: `1630015f9e94c21ebd5b8fa71328bf1761f5a5001346201b9a3f430e36e5ad1a`
