# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-21T08:48:13.970745Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 3.98 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 8.733 |
| `weekly_output` | **GREEN** | FRESH | 51.547 |
| `automation_health` | **AMBER** | AMBER | 0.053 |
| `architecture_health` | **GREEN** | GREEN | 0.012 |
| `experiment_lifecycle` | **GREEN** | FRESH | 0.387 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 0.4 |
| `remediation_maturation` | **GREEN** | FRESH | 13.232 |

## AI and learning activity

- OpenAI receipts this month: **274**
- OpenAI estimated cost this month: **$12.953204 from receipts**
- Pending forecast candidates: **253**
- Experiment candidates: **577**
- Experiment dispatch requests: **34407**
- Codex-ready remediation tasks: **6**
- Needs-more-evidence items: **1**

## Incidents

Open incident references: **22**

### API spend by task (receipt estimates only)

| Task | Receipts | Known estimated USD | Unknown-cost receipts | Gateway PASS | Retries |
|---|---:|---:|---:|---:|---:|
| `DAILY_CONFLICT_REVIEW` | 32 | $2.936662 | 0 | 32 | 0 |
| `SHADOW_COMPASS_V2` | 45 | $2.772704 | 0 | 45 | 0 |
| `RESEARCH_LAB_SOL_ANALYSIS` | 18 | $2.476158 | 0 | 18 | 1 |
| `MONTHLY_LEARNING_ADVERSARIAL` | 4 | $1.036608 | 0 | 4 | 0 |
| `MONTHLY_LEARNING_ANALYST` | 4 | $1.026470 | 0 | 4 | 0 |
| `DAILY_DIRECTOR_SHADOW` | 81 | $0.833095 | 0 | 81 | 80 |
| `FMOS_AUTONOMOUS_MISSION_LOOP_AUDIT` | 3 | $0.718824 | 0 | 3 | 0 |
| `TEMP_SOL_PR_REVIEW` | 6 | $0.427192 | 0 | 6 | 2 |
| `DECISION_MISS_AUDIT` | 21 | $0.265729 | 0 | 15 | 0 |
| `EVIDENCE_GAP_VALIDATION` | 21 | $0.139819 | 0 | 0 | 0 |
| `WEEKLY_ADVERSARIAL_REVIEW` | 3 | $0.101492 | 0 | 3 | 0 |
| `UNCLASSIFIED` | 3 | $0.073760 | 0 | 3 | 0 |

A gateway PASS alone is not measured downstream value or investment edge.

## Required actions

- **P1** `automation_health` - SEMANTIC_STATUS_AMBER
- **P1** `openai_daily_director` - SEMANTIC_STATUS_DEGRADED

Dashboard SHA-256: `005cee1db00cb91ff5256ca3f491ea46420df8cabe19d5bda84ed21495f65a9a`
