# Operations Dashboard

Overall: **AMBER**
Generated: `2026-10-21T07:17:18.369571Z`

## Systems

| System | Status | Detail | Age hours |
|---|---:|---|---:|
| `daily_capture` | **GREEN** | FRESH | 2.464 |
| `openai_daily_director` | **AMBER** | SEMANTIC_STATUS_DEGRADED | 7.218 |
| `weekly_output` | **GREEN** | FRESH | 50.031 |
| `automation_health` | **AMBER** | AMBER | 0.053 |
| `architecture_health` | **GREEN** | GREEN | 0.01 |
| `experiment_lifecycle` | **GREEN** | FRESH | 1.177 |
| `experiment_receipt_sync` | **GREEN** | FRESH | 1.185 |
| `remediation_maturation` | **GREEN** | FRESH | 11.716 |

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

Dashboard SHA-256: `ab58745b00941ee1304a052a859a1736dbd6ecf535812ae4c45c261d287f8ec0`
