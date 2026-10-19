# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-19T20:53:38.774687Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.18 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 1.403 |
| `weekly_output` | **GREEN** | FRESH | 15.637 |
| `automation_health` | **AMBER** | AMBER | 0.232 |
| `architecture_health` | **GREEN** | GREEN | 0.168 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.402 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 14.6 |
| `remediation_maturation` | **GREEN** | FRESH | 0.152 |

## AI and learning activity

- OpenAI receipts this month: **260**
- OpenAI estimated cost this month: **$12.658069 from receipts**
- Pending forecast candidates: **249**
- Experiment candidates: **567**
- Experiment dispatch requests: **33118**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **1**

## Incidents

Open incident references: **22**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `SHADOW_COMPASS_V2` | 42 | $2.580200 | 0 | 42 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 76 | $0.777128 | 0 | 76 | 75 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 19 | $0.238964 | 0 | 13 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 19 | $0.126537 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.101492 | 0 | 3 | 0 |
| `UNCLASSIFIED` | 3 | $0.073760 | 0 | 3 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `3a1d31faeda001990be483269b02b9a2dff2736f65f9e7b1efc6c765978bbda0`
